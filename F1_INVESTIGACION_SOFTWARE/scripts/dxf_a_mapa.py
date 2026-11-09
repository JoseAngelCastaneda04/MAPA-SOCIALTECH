#!/usr/bin/env python3
"""DXF -> mapa nav2 (PGM + YAML), pegamento mínimo entre ezdxf y map2sdf.

Por qué existe: ningún programa existente hace "capas de un DXF -> mapa nav2 con la escala del CAD".
Qué NO hace: no interpreta puertas, no dibuja muros a partir de líneas sueltas, no limpia el CAD.
Entradas : DXF, capa(s) de muros. Los muros deben ser contornos CERRADOS (LWPOLYLINE/POLYLINE/HATCH/SOLID),
           directamente o dentro de bloques (INSERT).
Unidades : se leen de $INSUNITS (mm, cm, m, in, ft...). Si falta, se aborta salvo --unidades.
Salida   : <out>.pgm (0 = ocupado, 254 = libre), <out>.yaml (convención nav2: fila 0 = Y máxima).
Origen   : por defecto el mínimo (x, y) de lo dibujado en las capas elegidas menos --margen; con
           --origen cad se conserva (0,0) del CAD (el YAML lleva el desplazamiento).
"""
import argparse
import sys

import cv2
import ezdxf
import numpy as np
from ezdxf import path as ezpath
from ezdxf import units

FACTOR = {u: units.conversion_factor(u, units.M) for u in (1, 2, 4, 5, 6)}  # in, ft, mm, cm, m


def poligonos(msp, capas):
    """Devuelve listas de vértices (en unidades del dibujo) de todo lo cerrado en las capas dadas."""
    pols = []
    for e in msp:
        if e.dxftype() == "INSERT":
            ents = [v for v in e.virtual_entities()]
        else:
            ents = [e]
        for v in ents:
            if v.dxf.layer not in capas and e.dxf.layer not in capas:
                continue
            t = v.dxftype()
            if t in ("LWPOLYLINE", "POLYLINE", "HATCH", "SOLID", "TRACE", "CIRCLE", "ELLIPSE"):
                try:
                    for p in ezpath.make_path(v).sub_paths():
                        pts = [(q.x, q.y) for q in p.flattening(1e-3 * 1000)]
                        if len(pts) >= 3 and (p.is_closed or t in ("SOLID", "TRACE", "HATCH", "CIRCLE")):
                            pols.append(pts)
                except Exception as exc:  # entidad no convertible: se avisa, no se ignora en silencio
                    print(f"AVISO: {t} no convertible: {exc}", file=sys.stderr)
    return pols


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("dxf"); ap.add_argument("--capas", nargs="+", required=True)
    ap.add_argument("--res", type=float, default=0.05, help="m/píxel (def. 0.05)")
    ap.add_argument("--out", required=True, help="prefijo de salida"); ap.add_argument("--margen", type=float, default=0.0)
    ap.add_argument("--unidades", type=int, help="código INSUNITS si el DXF no lo trae (4=mm, 5=cm, 6=m)")
    ap.add_argument("--origen", choices=["bbox", "cad"], default="bbox")
    ap.add_argument("--supersample", type=int, default=4)
    a = ap.parse_args()

    doc = ezdxf.readfile(a.dxf)
    code = a.unidades or doc.header.get("$INSUNITS", 0)
    if code not in FACTOR:
        sys.exit(f"Unidades no válidas o ausentes ($INSUNITS={code}); use --unidades")
    k = FACTOR[code]
    pols = poligonos(doc.modelspace(), set(a.capas))
    if not pols:
        sys.exit("No se encontró geometría cerrada en las capas dadas")
    todo = np.vstack(pols) * k
    xmin, ymin = (todo.min(0) - a.margen) if a.origen == "bbox" else (0.0, 0.0)
    if a.origen == "cad":
        xmin, ymin = min(0.0, todo[:, 0].min()), min(0.0, todo[:, 1].min())
    xmax, ymax = todo.max(0) + a.margen
    W, H = int(np.ceil((xmax - xmin) / a.res)), int(np.ceil((ymax - ymin) / a.res))
    S = a.supersample                       # se pinta a S veces la resolución y se promedia (celda ocupada si >=50 % cubierta)
    cob = np.zeros((H * S, W * S), np.uint8)
    for p in pols:
        q = np.array(p) * k
        px = np.round((q[:, 0] - xmin) / a.res * S * 16).astype(np.int32)         # subpíxel x16
        py = np.round((H * S) * 16 - (q[:, 1] - ymin) / a.res * S * 16).astype(np.int32)  # fila 0 = Y máx.
        cv2.fillPoly(cob, [np.stack([px, py], 1)], 255, lineType=cv2.LINE_8, shift=4)
    frac = cv2.resize(cob, (W, H), interpolation=cv2.INTER_AREA) / 255.0
    img = np.where(frac >= 0.49, 0, 254).astype(np.uint8)
    cv2.imwrite(a.out + ".pgm", img)
    with open(a.out + ".yaml", "w") as f:
        f.write(f"image: {a.out.split('/')[-1]}.pgm\nmode: trinary\nresolution: {a.res}\n"
                f"origin: [{xmin:.4f}, {ymin:.4f}, 0.0]\nnegate: 0\noccupied_thresh: 0.65\nfree_thresh: 0.196\n")
    print(f"unidades INSUNITS={code} (x{k} -> m) | {len(pols)} polígonos | {W}x{H} px | "
          f"extensión {xmax - xmin:.3f} x {ymax - ymin:.3f} m | origen [{xmin:.3f}, {ymin:.3f}]")


if __name__ == "__main__":
    main()

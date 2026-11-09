#!/usr/bin/env python3
"""Mide un mapa nav2 (YAML+PGM/PNG) contra la verdad-terreno de la vivienda de referencia, en METROS.

Uso: medir_mapa.py mapa.yaml [--dx m --dy m]   (dx,dy: desplazamiento si el mapa no usa el origen CAD)
Con --auto-origen se alinea por la esquina SO de lo ocupado (para rutas que pierden el origen CAD).
"""
import argparse
import json
import os

import cv2
import numpy as np
import yaml

AQUI = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pruebas", "vivienda_3formatos")
RES_GT = 0.01


def cargar(yml):
    y = yaml.safe_load(open(yml))
    img = cv2.imread(os.path.join(os.path.dirname(yml), y["image"]), cv2.IMREAD_GRAYSCALE)
    p = (255 - img) / 255.0 if y.get("negate", 0) == 0 else img / 255.0
    return y, p > y.get("occupied_thresh", 0.65)  # True = ocupado (fila 0 = Y máx.)


def a_rejilla_gt(occ, res, ox, oy, shape=(800, 1000)):
    """Remuestrea el mapa a la rejilla de 1 cm de la verdad-terreno (vecino más cercano)."""
    H, W = shape
    ys, xs = np.mgrid[0:H, 0:W]
    X = (xs + .5) * RES_GT; Y = (H - ys - .5) * RES_GT
    c = np.floor((X - ox) / res).astype(int); f = occ.shape[0] - 1 - np.floor((Y - oy) / res).astype(int)
    ok = (c >= 0) & (c < occ.shape[1]) & (f >= 0) & (f < occ.shape[0])
    out = np.zeros(shape, bool); out[ok] = occ[f[ok], c[ok]]
    return out


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("yaml")
    ap.add_argument("--dx", type=float, default=0.0); ap.add_argument("--dy", type=float, default=0.0)
    ap.add_argument("--auto-origen", action="store_true")
    ap.add_argument("--json", help="guardar resultado")
    a = ap.parse_args()
    y, occ = cargar(a.yaml)
    res = y["resolution"]; ox, oy = y["origin"][:2]
    gt = np.load(os.path.join(AQUI, "verdad_terreno_muros_1cm.npy")).astype(bool)
    ox += a.dx; oy += a.dy
    if a.auto_origen:  # esquina SO de lo ocupado del mapa := (0,0) del mundo
        r, c = np.where(occ)
        ox = -c.min() * res
        oy = -(occ.shape[0] - 1 - r.max()) * res
    m = a_rejilla_gt(occ, res, ox, oy)
    dm = cv2.distanceTransform((~m).astype(np.uint8), cv2.DIST_L2, 5) * RES_GT   # distancia al ocupado del mapa
    dg = cv2.distanceTransform((~gt).astype(np.uint8), cv2.DIST_L2, 5) * RES_GT
    # espesor medido en el mapa: muro sur a x=2 m (verdad 0,20 m); muro interior N-S a y=6,5 m (verdad 0,10 m)
    sur = m[:, int(2.0 / RES_GT)][-int(0.6 / RES_GT):].sum() * RES_GT          # franja sur, x=2 m
    nsint = m[int((8 - 6.5) / RES_GT), int(4.5 / RES_GT):int(5.5 / RES_GT)].sum() * RES_GT
    def libre(x, yy): return not m[int((8 - yy) / RES_GT), int(x / RES_GT)]
    def ocup(x, yy): return bool(m[int((8 - yy) / RES_GT), int(x / RES_GT)])
    # conectividad de espacio libre entre habitaciones (en la rejilla del propio mapa, sin tolerancia)
    libre_map = (~occ).astype(np.uint8)
    n, lab = cv2.connectedComponents(libre_map, connectivity=4)
    def etiqueta(x, yy):
        c = int(np.floor((x - ox) / res)); f = occ.shape[0] - 1 - int(np.floor((yy - oy) / res))
        return lab[f, c]
    hab = {"salon": (7.5, 2.5), "cocina": (2.5, 2.0), "dormitorio": (2.5, 6.0), "alcoba_E": (7.5, 6.8)}
    res_out = {
        "mapa": a.yaml, "resolucion_m_px": res, "origen_usado": [round(ox, 4), round(oy, 4)],
        "IoU_muros": round(float((m & gt).sum() / max(1, (m | gt).sum())), 4),
        "area_muros_m2": {"mapa": round(m.sum() * RES_GT ** 2, 3), "verdad": round(gt.sum() * RES_GT ** 2, 3)},
        "dist_mapa_a_verdad_m": {"media": round(float(dg[m].mean()), 4), "p95": round(float(np.percentile(dg[m], 95)), 4), "max": round(float(dg[m].max()), 4)},
        "dist_verdad_a_mapa_m": {"media": round(float(dm[gt].mean()), 4), "p95": round(float(np.percentile(dm[gt], 95)), 4), "max": round(float(dm[gt].max()), 4)},
        "obstaculos_espurios_m2(>12cm de un muro real)": round(float(((dg > 0.12) & m).sum() * RES_GT ** 2), 3),
        "muro_perdido_m2(>12cm de lo ocupado)": round(float(((dm > 0.12) & gt).sum() * RES_GT ** 2), 3),
        "espesor_muro_sur_m(verdad 0.20)": round(float(sur), 3), "espesor_muro_int_NS_m(verdad 0.10)": round(float(nsint), 3),
        "puertas_libres": {"P1_sur(5.0,0.1)": libre(5.0, 0.10), "P2_NS(5.0,2.45)": libre(5.0, 2.45), "P3_EO(2.45,4.0)": libre(2.45, 4.0)},
        "muros_ocupados": {"sur(2,0.1)": ocup(2, 0.1), "intNS(5,6.5)": ocup(5.0, 6.5), "intEO(1,4.0)": ocup(1.0, 4.0)},
        "mobiliario_en_mapa": {"mesa(7.5,6.0)": ocup(7.5, 6.0), "silla(7.5,5.2)": ocup(7.5, 5.2)},
        "componentes_libres_habitaciones": {k: int(etiqueta(*v)) for k, v in hab.items()},
    }
    print(json.dumps(res_out, indent=1, ensure_ascii=False))
    if a.json:
        json.dump(res_out, open(a.json, "w"), indent=1, ensure_ascii=False)


if __name__ == "__main__":
    main()

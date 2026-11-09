#!/usr/bin/env python3
"""F4: MAPA BASE (paredes validadas) + CAPA DE MOBILIARIO (sdf2map) = MAPA ACTUALIZADO.
Alineacion por coordenadas METRICAS (origen y resolucion de cada YAML), no por indices de pixel:
para cada celda del mapa base se toma el centro (x,y) y se mira la celda de la capa que lo contiene.
Combinacion = UNION de ocupados (no hay resta): una celda es ocupada si lo es en la base o en la capa.
Garantias: mismo tamano, resolucion y origen que la base; las celdas ocupadas de la base nunca se liberan.
Dos formas de dar la capa:
  --nube capa.pcd --z zmin zmax   (PREFERIDA) nube de puntos de sdf2map -> se rasteriza DIRECTAMENTE en la rejilla de la base (sin remuestreo, cada
                                  objeto cae en las mismas celdas aunque se muevan otros) con el mismo criterio que sdf2map (celda = floor((p-origen)/res),
                                  banda z, cierre morfologico 3x3 de radio 1).
  --capa capa.yaml                mapa de ocupacion ya generado por sdf2map: se REMUESTREA por coordenadas (puede desplazar +-1 celda segun
                                  el origen de su rejilla, que depende de los limites de la nube).
Uso: combinar_mapas.py --base base.yaml (--nube capa.pcd --z 0.05 1.8 | --capa capa.yaml) --salida mapa/piso_amueblado [--capa-alineada capa_alineada.pgm]"""
import argparse, os, sys, yaml, cv2, numpy as np

def cargar(yml):
    y = yaml.safe_load(open(yml)); p = os.path.join(os.path.dirname(os.path.abspath(yml)), y["image"])
    im = cv2.imread(p, cv2.IMREAD_UNCHANGED); assert im is not None, p
    occ = (255 - im.astype(float)) / 255.0 > y["occupied_thresh"] if y.get("negate", 0) == 0 else im / 255.0 > y["occupied_thresh"]
    return y, im, occ

def alinear(capa_occ, capa_y, base_shape, base_y):
    """Devuelve la capa remuestreada a la rejilla base (misma forma). Filas PGM: la 0 es la y maxima."""
    hb, wb = base_shape; hc, wc = capa_occ.shape
    rb, rc = base_y["resolution"], capa_y["resolution"]
    ox, oy = base_y["origin"][:2]; cx, cy = capa_y["origin"][:2]
    xs = ox + (np.arange(wb) + 0.5) * rb                  # centros de columna de la base (m)
    ys = oy + (hb - 1 - np.arange(hb) + 0.5) * rb          # centros de fila de la base (m)
    ic = np.floor((xs - cx) / rc).astype(int)              # columna de la capa
    jc = hc - 1 - np.floor((ys - cy) / rc).astype(int)     # fila de la capa
    vx = (ic >= 0) & (ic < wc); vy = (jc >= 0) & (jc < hc)
    out = np.zeros((hb, wb), bool)
    out[np.ix_(vy, vx)] = capa_occ[np.ix_(jc[vy], ic[vx])]
    # celdas de la capa que caen fuera de la base (mueble fuera del mapa) -> aviso
    fuera = capa_occ.sum() - out.sum()
    return out, int(fuera)

def leer_pcd(p):
    """PCD binario x y z float32 (formato de sdf2map) -> (N,3)."""
    with open(p, "rb") as f:
        n = 0
        while True:
            l = f.readline().decode()
            if l.startswith("POINTS"): n = int(l.split()[1])
            if l.startswith("DATA"): assert "binary" in l; break
        return np.fromfile(f, np.float32, 3 * n).reshape(n, 3).astype(np.float64)

def rasterizar_nube(pts, base_y, shape, zmin, zmax, cierre=1):
    h, w = shape; res = base_y["resolution"]; ox, oy = base_y["origin"][:2]
    m = (pts[:, 2] >= zmin) & (pts[:, 2] <= zmax); p = pts[m]
    cx = np.floor((p[:, 0] - ox) / res).astype(int); cy = np.floor((p[:, 1] - oy) / res).astype(int)
    ok = (cx >= 0) & (cx < w) & (cy >= 0) & (cy < h); fuera = int((~ok).sum())
    g = np.zeros((h, w), np.uint8); g[h - 1 - cy[ok], cx[ok]] = 1                    # fila 0 = y maxima
    if cierre > 0:
        k = np.ones((3, 3), np.uint8)
        g = cv2.erode(cv2.dilate(g, k, iterations=cierre), k, iterations=cierre)
    return g.astype(bool), fuera

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--base", required=True); ap.add_argument("--capa"); ap.add_argument("--nube"); ap.add_argument("--z", nargs=2, type=float, default=[0.05, 1.8])
    ap.add_argument("--salida", required=True); ap.add_argument("--capa-alineada")
    a = ap.parse_args()
    by, bim, bocc = cargar(a.base)
    if a.nube:
        capa, fuera = rasterizar_nube(leer_pcd(a.nube), by, bocc.shape, a.z[0], a.z[1]); cocc = capa
        if fuera: sys.exit(f"ERROR: {fuera} puntos de la nube quedan fuera del mapa base")
    else:
        cy, cim, cocc = cargar(a.capa); capa, fuera = alinear(cocc, cy, bocc.shape, by)
    if not a.nube and fuera > 0.02 * cocc.sum() + 5:  # tolerancia: pocos pixeles de borde por redondeo
        sys.exit(f"ERROR: {fuera} celdas de la capa quedan fuera del mapa base")
    nuevo = bocc | capa
    assert (nuevo | ~bocc).all(), "se liberaron celdas de la base"
    libre = 254 if (bim == 254).any() else 255
    pgm = np.where(nuevo, 0, libre).astype(np.uint8)
    cv2.imwrite(a.salida + ".pgm", pgm)
    y = dict(by); y["image"] = os.path.basename(a.salida) + ".pgm"
    with open(a.salida + ".yaml", "w") as f:
        f.write(f"image: {y['image']}\nmode: {y.get('mode','trinary')}\nresolution: {y['resolution']}\norigin: {list(y['origin'])}\nnegate: {y.get('negate',0)}\noccupied_thresh: {y['occupied_thresh']}\nfree_thresh: {y['free_thresh']}\n")
    if a.capa_alineada: cv2.imwrite(a.capa_alineada, np.where(capa, 0, libre).astype(np.uint8))
    print(f"base ocupadas={bocc.sum()}  capa ocupadas={cocc.sum()} (alineada={capa.sum()}, fuera={fuera})  union={nuevo.sum()}  solapan={int((bocc & capa).sum())}  nuevas={int((nuevo & ~bocc).sum())}")

#!/usr/bin/env python3
"""F5: comprueba si la HUELLA COMPLETA del TRACER (poligono real: proyeccion xy del casco de colision + ruedas, orientada) cabe en el mapa de F4.
Uso: huella_libre.py check x y yaw_deg     |     huella_libre.py buscar [xmin xmax ymin ymax]
Cuenta tambien el giro sobre si mismo: circulo circunscrito (radio al punto mas lejano de base_footprint)."""
import sys, os, json, numpy as np, re
from scipy import ndimage
from scipy.spatial import ConvexHull
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); MAPA = D + '/../F4_ESCENARIO_CON_MOBILIARIO/mapa/piso_amueblado'
def leer_pgm(p):
    b = open(p, 'rb').read(); m = re.match(rb'P5\s+(\d+)\s+(\d+)\s+(\d+)\s', b); w, h = int(m[1]), int(m[2]); return np.frombuffer(b[m.end():], dtype=np.uint8).reshape(h, w)
img = leer_pgm(MAPA + '.pgm'); RES, OX, OY = 0.01, 4.7299, -11.32
occ = img < 250          # PGM trinario de F4: 0 = ocupado, 254 = libre; cualquier otro valor (desconocido) cuenta como NO libre
H, W = occ.shape
# huella: casco de colision del chasis (xy) + ruedas (cilindros) -> poligono convexo (marco base_link; x,y iguales a base_footprint)
pts = []
for l in open(D + '/modelos/tracer_agv/meshes/chasis_colision.obj'):
    if l.startswith('v '): pts.append([float(t) for t in l.split()[1:3]])
for sx in (-1, 1):
    for ex in (-0.0605, 0.0605): pts += [[ex, sx * (0.17 + 0.0422)], [ex, sx * (0.17 - 0.0422)]]
pts = np.array(pts); HUL = pts[ConvexHull(pts).vertices]; R_CIRC = float(np.hypot(*HUL.T).max())
def poligono_mascara(x, y, yaw):
    c, s = np.cos(yaw), np.sin(yaw); P = HUL @ np.array([[c, s], [-s, c]]) + [x, y]
    from matplotlib.path import Path
    ii, jj = np.mgrid[0:H, 0:W]; X = OX + (jj + 0.5) * RES; Y = OY + (H - ii - 0.5) * RES
    # solo la ventana alrededor
    j0, j1 = int((P[:, 0].min() - OX) / RES) - 3, int((P[:, 0].max() - OX) / RES) + 3; i0, i1 = int(H - (P[:, 1].max() - OY) / RES) - 3, int(H - (P[:, 1].min() - OY) / RES) + 3
    sub = np.zeros((H, W), bool); xs = X[i0:i1, j0:j1]; ys = Y[i0:i1, j0:j1]
    sub[i0:i1, j0:j1] = Path(P).contains_points(np.c_[xs.ravel(), ys.ravel()]).reshape(xs.shape); return sub, P
def distancia_libre(x, y, radio_max=2.0):
    """distancia desde (x,y) al obstaculo mas cercano (m)"""
    j = int((x - OX) / RES); i = int(H - 1 - (y - OY) / RES); r = int(radio_max / RES)
    i0, i1, j0, j1 = max(0, i - r), min(H, i + r), max(0, j - r), min(W, j + r)
    d = ndimage.distance_transform_edt(~occ[i0:i1, j0:j1]); return float(d[i - i0, j - j0] * RES)
def check(x, y, yaw):
    m, P = poligono_mascara(x, y, yaw); sol = int((m & occ).sum()); dpoli = ndimage.distance_transform_edt(~occ)
    d_huella = float(dpoli[m].min() * RES) if m.any() else None
    return dict(x=x, y=y, yaw_deg=round(np.degrees(yaw), 2), celdas_huella=int(m.sum()), celdas_huella_ocupadas=sol, holgura_min_huella_m=d_huella,
                libre_giro_sobre_si_mismo=bool(distancia_libre(x, y) >= R_CIRC), dist_obstaculo_desde_centro_m=distancia_libre(x, y), radio_circunscrito_m=R_CIRC,
                ancho_huella_x_largo=[float(np.ptp(HUL[:, 1])), float(np.ptp(HUL[:, 0]))])
if __name__ == '__main__':
    if sys.argv[1] == 'check': print(json.dumps(check(float(sys.argv[2]), float(sys.argv[3]), np.radians(float(sys.argv[4]))), indent=1))
    else:
        a = [float(t) for t in sys.argv[2:]] or [5.0, 18.0, -11.0, 0.2]
        dist = ndimage.distance_transform_edt(~occ) * RES; best = []
        lab, _ = ndimage.label(~occ); interior = lab == lab[int(H - 1 - (-2.7 - OY) / RES), int((9.7 - OX) / RES)]   # solo el interior conectado con el salon
        for y in np.arange(a[2], a[3], 0.1):
            for x in np.arange(a[0], a[1], 0.1):
                j = int((x - OX) / RES); i = int(H - 1 - (y - OY) / RES)
                if interior[i, j] and dist[i, j] >= 0.9: best.append((dist[i, j], x, y))
        best.sort(reverse=True); print('mejores centros (holgura al obstaculo, x, y):'); [print('%.2f %.2f %.2f' % b) for b in best[:15]]

#!/usr/bin/env python3
"""F5: mide sobre los PIXELES que dibuja RViz2 (captura del display aislado, vista cenital a 110 px/m): (1) calibra pixel<->metros alineando los muros dibujados con el PGM de F4;
(2) los puntos rojos del LiDAR (marco laser -> TF -> map) deben caer sobre celdas ocupadas del mapa: distancia al obstaculo del mapa mas cercano, en m.
Esto valida la cadena completa robot->TF->RViz2 (pose del robot + montaje del lidar) sin fiarse de que 'se vea bien'. Uso: medir_rviz_pixeles.py <captura.png> <salida.json> [x_vista y_vista escala]"""
import sys, os, json, re, numpy as np
from PIL import Image
from scipy import ndimage
a = sys.argv; png, out = a[1], a[2]; X0, Y0, S = (float(a[3]), float(a[4]), float(a[5])) if len(a) > 5 else (9.6, -4.2, 110.0)
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
b = open(D + '/../F4_ESCENARIO_CON_MOBILIARIO/mapa/piso_amueblado.pgm', 'rb').read(); m = re.match(rb'P5\s+(\d+)\s+(\d+)\s+(\d+)\s', b); W, H = int(m[1]), int(m[2])
occ = np.frombuffer(b[m.end():], dtype=np.uint8).reshape(H, W) < 250; RES, OX, OY = 0.01, 4.7299, -11.32
img = np.array(Image.open(png).convert('RGB')).astype(int); h, w, _ = img.shape
u0, u1, v0, v1 = 492, w, 114, h          # zona 3D de RViz (fuera de paneles y borde gris del mapa)
negro = (img.sum(2) < 90)
def modelo(cu, cv, s):
    uu, vv = np.meshgrid(np.arange(u0, u1), np.arange(v0, v1)); x = X0 + (uu-cu)/s; y = Y0 - (vv-cv)/s
    j = ((x-OX)/RES).astype(int); i = (H-1-((y-OY)/RES)).astype(int); ok = (i >= 0) & (i < H) & (j >= 0) & (j < W); r = np.zeros(uu.shape, bool); r[ok] = occ[i[ok], j[ok]]; return r
tm = negro[v0:v1, u0:u1]; best = (0, None)
for s in (S,):
    for cu in range(930, 1040, 2):
        for cv in range(500, 600, 2):
            mm = modelo(cu, cv, s); iou = (mm & tm).sum()/max(1, (mm | tm).sum())
            if iou > best[0]: best = (iou, (cu, cv, s))
iou0, (cu, cv, s) = best
for cu2 in np.arange(cu-2, cu+2.01, 0.5):         # afinado a medio pixel
    for cv2 in np.arange(cv-2, cv+2.01, 0.5):
        mm = modelo(cu2, cv2, s); iou = (mm & tm).sum()/max(1, (mm | tm).sum())
        if iou > iou0: iou0, cu, cv = iou, cu2, cv2
rojo = (img[:, :, 0] > 220) & (img[:, :, 1] < 70) & (img[:, :, 2] < 70); rojo[:v0] = False; rojo[:, :u0] = False
lab, n = ndimage.label(rojo); cen = np.array(ndimage.center_of_mass(rojo, lab, range(1, n+1))) if n else np.zeros((0, 2))
dist = ndimage.distance_transform_edt(~occ)*RES; d = []
for (vv, uu) in cen:
    x = X0 + (uu-cu)/s; y = Y0 - (vv-cv)/s; j = int((x-OX)/RES); i = int(H-1-(y-OY)/RES)
    if 0 <= i < H and 0 <= j < W: d.append(dist[i, j])
d = np.array(d); res = dict(calibracion=dict(iou_muros_mapa_vs_pixeles=iou0, centro_px=[cu, cv], escala_px_m=s, resolucion_px_m=1/s),
    puntos_lidar_detectados=int(n), distancia_punto_a_celda_ocupada_m=dict(mediana=float(np.median(d)) if len(d) else None, p90=float(np.percentile(d, 90)) if len(d) else None, max=float(d.max()) if len(d) else None,
    fraccion_dentro_2cm=float((d <= 0.02).mean()) if len(d) else None, fraccion_dentro_5cm=float((d <= 0.05).mean()) if len(d) else None))
json.dump(res, open(out, 'w'), indent=1); print(json.dumps(res, indent=1))

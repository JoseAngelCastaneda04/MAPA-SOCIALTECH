#!/usr/bin/env python3
"""F2: mide en un mapa nav2 (YAML+PGM) el tramo libre continuo a lo largo de una línea que pasa por un punto
de una habitación y lo compara con la cota escrita en el plano. Unidades: metros, coordenadas del CAD.
Uso: medir_cotas.py mapa.yaml cotas.json  (cotas: [{"nombre","punto":[x,y],"eje":"x"|"y","cota_m"}])"""
import sys, json, os, yaml, cv2, numpy as np
y = yaml.safe_load(open(sys.argv[1])); res = y["resolution"]; ox, oy = y["origin"][:2]
img = cv2.imread(os.path.join(os.path.dirname(sys.argv[1]), y["image"]), 0); H, W = img.shape
libre = img > 127
def run(px, py, eje):
    c = int(np.floor((px - ox) / res)); r = H - 1 - int(np.floor((py - oy) / res))
    if not libre[r, c]: return None
    d = (0, 1) if eje == "x" else (1, 0); n = 0
    a = [r, c]; b = [r, c]
    while 0 <= a[0] - d[0] < H and 0 <= a[1] - d[1] < W and libre[a[0] - d[0], a[1] - d[1]]: a[0] -= d[0]; a[1] -= d[1]
    while 0 <= b[0] + d[0] < H and 0 <= b[1] + d[1] < W and libre[b[0] + d[0], b[1] + d[1]]: b[0] += d[0]; b[1] += d[1]
    return (abs(b[0] - a[0]) + abs(b[1] - a[1]) + 1) * res
out = []
for k in json.load(open(sys.argv[2])):
    m = run(*k["punto"], k["eje"]); e = None if m is None else round(m - k["cota_m"], 3)
    out.append({**k, "medido_m": None if m is None else round(m, 3), "error_m": e})
    print(f'{k["nombre"]:34s} cota {k["cota_m"]:5.2f}  medido {"—" if m is None else f"{m:5.2f}"}  error {"—" if e is None else f"{e:+.3f}"} m')
if len(sys.argv) > 3: json.dump(out, open(sys.argv[3], "w"), indent=1, ensure_ascii=False)

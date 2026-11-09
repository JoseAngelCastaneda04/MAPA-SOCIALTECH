#!/usr/bin/env python3
"""F4: mide en PIXELES RENDERIZADOS por RViz2 (config piso_amueblado_zoom: cenital ortogonal, 170 px/m, centro (8.9,-5.3)) las huellas del mobiliario
y las compara con la huella esperada en metros (referencia independiente, comprobar_mapa.referencia). Rejilla y ejes visibles se descartan por color (solo negro puro).
RViz2 corre en un display X aislado (Xephyr :5, scripts/rviz_aislado.sh): la captura NO puede incluir ventanas ni avisos del escritorio del usuario.
Uso: medir_rviz_mobiliario.py <salida_pantalla.png> <salida.json>"""
import json, os, subprocess, sys, yaml, cv2, numpy as np
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.join(D, "scripts"))
from comprobar_mapa import referencia, bbox, Rejilla
from combinar_mapas import cargar
recorte, jout = sys.argv[1], sys.argv[2]
subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-f", "x11grab", "-video_size", "1700x1100", "-i", ":5", "-frames:v", "1", recorte], check=True)   # pantalla completa de Xephyr
full = cv2.imread(recorte); vp = full[112:112 + 908, 464:464 + 1120]       # viewport 3D de RViz (xwininfo: 1120x908 en +364+62 dentro de la ventana en +100+50)
E, cx, cy = 170.0, vp.shape[1] / 2.0, vp.shape[0] / 2.0; X0, Y0 = 8.9, -5.3
negro = vp.max(2) < 40
cfg = yaml.safe_load(open(os.path.join(D, "config", "mobiliario.yaml"))); dims = json.load(open(os.path.join(D, "modelos", "dimensiones.json")))
by, _, bocc = cargar(os.path.join(D, cfg["mapa_base"])); rej = Rejilla(by, bocc.shape); out = []
for o in cfg["objetos"]:
    ref = referencia(o, dims, rej, *cfg["slice_z"]); b = bbox(ref, rej)       # xmin,ymin,xmax,ymax (m)
    px = lambda x: cx + (x - X0) * E; py = lambda y: cy - (y - Y0) * E
    x0, x1, y0, y1 = [int(round(v)) for v in (px(b[0]) - 1, px(b[2]) + 1, py(b[3]) - 1, py(b[1]) + 1)]
    win = negro[max(y0, 0):y1, max(x0, 0):x1]; ys, xs = np.nonzero(win)
    xs = xs + max(x0, 0); ys = ys + max(y0, 0)
    m = [X0 + (xs.min() - cx) / E, Y0 - (ys.max() + 1 - cy) / E, X0 + (xs.max() + 1 - cx) / E, Y0 - (ys.min() - cy) / E]
    out.append({"id": o["id"], "bbox_esperada_m": [round(v, 3) for v in b], "bbox_en_pixeles_RViz_m": [round(v, 3) for v in m], "error_max_m": round(max(abs(np.array(b) - np.array(m))), 3)})
    print(o["id"], "error max", out[-1]["error_max_m"], "m")
json.dump({"px_por_m": E, "objetos": out}, open(jout, "w"), indent=1, ensure_ascii=False)

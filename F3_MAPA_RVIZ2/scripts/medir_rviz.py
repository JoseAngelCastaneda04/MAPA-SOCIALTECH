#!/usr/bin/env python3
"""F3: mide EN PÍXELES RENDERIZADOS por RViz2 (vista cenital ortogonal, norte arriba, sin rejilla ni ejes).
Requiere map_server activo. Lanza rviz2 con una config temporal por vista, captura SOLO su ventana y analiza.
  vista completa (escala E px/m): calibra px/m con el rectángulo del mapa y mide la caja de muros respecto a su esquina
  vistas de puerta (escala 300 px/m, centradas en el punto de cada puerta): mide el hueco libre a lo largo del eje de la cota
Uso: medir_rviz.py <dir_salida>"""
import sys, os, json, subprocess, time, signal, cv2, numpy as np
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); OUT = sys.argv[1]; os.makedirs(OUT, exist_ok=True)
TPL = open(f"{D}/config/piso_1cm.rviz").read()
cot = json.load(open("/home/jose-angel/Desktop/MAPA SOCIALTECH/F2_PLANO_SIMPLE_GAZEBO/evidencias/cotas_verificadas.json"))[6:]
def cfg(x, y, esc, path):
    s = TPL.replace("Scale: 40", f"Scale: {esc}").replace("X: 11.4", f"X: {x}").replace("Y: -5.5", f"Y: {y}")
    s = s.replace("Name: Rejilla 1 m\n      Enabled: true", "Name: Rejilla 1 m\n      Enabled: false").replace("Name: Ejes del map\n      Enabled: true", "Name: Ejes del map\n      Enabled: false")
    open(path, "w").write(s)
def captura(x, y, esc, nombre):
    c = f"{OUT}/{nombre}.rviz"; cfg(x, y, esc, c)
    p = subprocess.Popen(["rviz2", "-d", c], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, preexec_fn=os.setsid); time.sleep(9)
    r = subprocess.run([f"{D}/scripts/captura_ventana.sh", str(p.pid), f"{OUT}/{nombre}.png"], capture_output=True, text=True)
    os.killpg(p.pid, signal.SIGTERM); p.wait(); print(nombre, r.stdout.strip() or r.stderr.strip())
    return cv2.imread(f"{OUT}/{nombre}.png")
res = {}
# ---- vista completa
E = 70; img = captura(11.4, -5.5, E, "vista_completa_70pxm"); g = img[63:969, 364:1484].astype(int)   # área 3D (de la captura 01)
bg = (np.abs(g - 48).max(2) <= 3); mapa = ~bg
ys, xs = np.where(mapa); x0, x1, y0, y1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
negro = g.max(2) < 60; yy, xx = np.where(negro & mapa)
res["vista_completa"] = {"px_por_m_teorico": E, "mapa_px": [int(x1 - x0), int(y1 - y0)], "mapa_m_medido": [round((x1 - x0) / E, 3), round((y1 - y0) / E, 3)], "mapa_m_esperado": [13.5, 11.79],
  "muros_caja_px": [int(xx.min() - x0), int(x1 - xx.max() - 1), int(yy.min() - y0), int(y1 - yy.max() - 1)],
  "muros_caja_tamano_m_medido": [round((xx.max() + 1 - xx.min()) / E, 3), round((yy.max() + 1 - yy.min()) / E, 3)], "muros_caja_tamano_m_CAD": [13.09, 11.39],
  "margen_izq_m": round((xx.min() - x0) / E, 3), "margen_inf_m": round((y1 - yy.max() - 1) / E, 3), "margen_esperado_m": 0.2,
  "colores_libre/ocupado": [g[mapa & ~negro][0].tolist(), g[negro & mapa][0].tolist()]}
# ---- puertas
ES = 300; W0, H0 = 1120, 906; cx, cy = W0 // 2, H0 // 2
res["puertas"] = []
for ct in cot:
    px, py = ct["punto"]; im = captura(px, py, ES, "puerta_" + ct["nombre"].split("(")[0].strip().replace(" ", "_").replace(".", "")); g = im[63:969, 364:1484].astype(int)
    libre = g.min(2) > 200
    if not libre[cy, cx]: res["puertas"].append({"nombre": ct["nombre"], "error": "el centro no es libre"}); continue
    v = libre[cy, :] if ct["eje"] == "x" else libre[:, cx]; c = cx if ct["eje"] == "x" else cy
    a = c
    while a > 0 and v[a - 1]: a -= 1
    z = c
    while z < len(v) - 1 and v[z + 1]: z += 1
    res["puertas"].append({"nombre": ct["nombre"], "eje": ct["eje"], "hueco_px": int(z - a + 1), "hueco_m": round((z - a + 1) / ES, 4), "toca_borde_vista": bool(a == 0 or z == len(v) - 1)})
json.dump(res, open(f"{OUT}/medidas_rviz.json", "w"), indent=1, ensure_ascii=False); print(json.dumps(res, indent=1, ensure_ascii=False))

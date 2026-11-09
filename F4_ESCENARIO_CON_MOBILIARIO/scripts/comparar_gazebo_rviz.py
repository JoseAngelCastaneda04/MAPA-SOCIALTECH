#!/usr/bin/env python3
"""F4: compara Gazebo EN MARCHA con el /map que recibe RViz2 (mismo topic), en metros.
 1) Poses de cada objeto: Gazebo (topic pose/info del mundo en ejecucion) frente a config/mobiliario.yaml.
 2) /map (nav2 map_server, QoS transient local) frente a mapa/piso_amueblado.pgm: celdas distintas.
 3) Huella de cada objeto en /map (bbox de celdas ocupadas) frente a la huella esperada calculada con la POSE DE GAZEBO.
Requiere demo en marcha (scripts/demo.sh).  Uso: comparar_gazebo_rviz.py [--mundo piso_amueblado] [--json salida.json]"""
import argparse, json, math, os, re, subprocess, sys, yaml, cv2, numpy as np
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, DurabilityPolicy, ReliabilityPolicy
from nav_msgs.msg import OccupancyGrid
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.join(D, "scripts"))
from comprobar_mapa import referencia, bbox, Rejilla
from combinar_mapas import cargar

def poses_gazebo(mundo):
    t = subprocess.run(["gz", "topic", "-e", "-n", "1", "-t", f"/world/{mundo}/pose/info"], capture_output=True, text=True, timeout=20).stdout
    res = {}
    for blk in re.findall(r"pose \{(.*?)\n\}", t, re.S):
        n = re.search(r'name: "([^"]+)"', blk).group(1)
        g = lambda s, k, d=0.0: float((re.search(rf"{k}: ([-\d.e]+)", s) or [0, d])[1]) if re.search(rf"{k}: ([-\d.e]+)", s) else d
        pos = re.search(r"position \{(.*?)\}", blk, re.S); ori = re.search(r"orientation \{(.*?)\}", blk, re.S)
        x, y, z = (g(pos.group(1), k) for k in "xyz") if pos else (0, 0, 0)
        qx, qy, qz, qw = (g(ori.group(1), k, 0.0) for k in ("x", "y", "z", "w")) if ori else (0, 0, 0, 1)
        res.setdefault(n, (x, y, z, math.degrees(math.atan2(2*(qw*qz+qx*qy), 1-2*(qy*qy+qz*qz)))))  # el primero = el modelo
    return res

def leer_map():
    rclpy.init(); n = Node("cmp_f4"); msg = []
    n.create_subscription(OccupancyGrid, "/map", lambda m: msg.append(m), QoSProfile(depth=1, durability=DurabilityPolicy.TRANSIENT_LOCAL, reliability=ReliabilityPolicy.RELIABLE))
    for _ in range(100):
        rclpy.spin_once(n, timeout_sec=0.1)
        if msg: break
    n.destroy_node(); rclpy.shutdown(); assert msg, "/map sin mensajes"
    return msg[0]

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--mundo", default="piso_amueblado"); ap.add_argument("--json"); a = ap.parse_args()
    cfg = yaml.safe_load(open(os.path.join(D, "config", "mobiliario.yaml"))); dims = json.load(open(os.path.join(D, "modelos", "dimensiones.json")))
    gz = poses_gazebo(a.mundo); out = {"poses": [], "map": {}}
    for o in cfg["objetos"]:
        x, y, z, yaw = gz[o["id"]]; dyaw = (yaw - o.get("yaw_deg", 0) + 180) % 360 - 180
        out["poses"].append({"id": o["id"], "gazebo_xy_yaw": [round(x, 4), round(y, 4), round(yaw, 3)], "yaml_xy_yaw": [o["x"], o["y"], o.get("yaml_yaw", o.get("yaw_deg", 0))],
                             "error_xy_m": round(math.hypot(x - o["x"], y - o["y"]), 5), "error_yaw_deg": round(abs(dyaw), 3)})
    m = leer_map(); h, w = m.info.height, m.info.width; g = np.array(m.data, np.int16).reshape(h, w)[::-1]      # fila 0 = y maxima, como el PGM
    mocc = g >= 65
    ay, _, aocc = cargar(os.path.join(D, "mapa", "piso_amueblado.yaml"))
    out["map"] = {"resolucion": m.info.resolution, "origen": [m.info.origin.position.x, m.info.origin.position.y], "tamano": [w, h], "frame": m.header.frame_id,
                  "celdas_distintas_vs_pgm": int((mocc != aocc).sum()) if mocc.shape == aocc.shape else "forma distinta", "celdas_ocupadas": int(mocc.sum())}
    by, _, bocc = cargar(os.path.join(D, cfg["mapa_base"])); rej = Rejilla({"resolution": m.info.resolution, "origin": [m.info.origin.position.x, m.info.origin.position.y]}, mocc.shape)
    out["map"]["paredes_base_liberadas_en_topic"] = int((bocc & ~mocc).sum()); zmin, zmax = cfg["slice_z"]; objs = []
    for o in cfg["objetos"]:
        x, y, z, yaw = gz[o["id"]]; og = dict(o, x=x, y=y, yaw_deg=yaw)
        ref = referencia(og, dims, rej, zmin, zmax); win = cv2.dilate(ref.astype(np.uint8), np.ones((7, 7), np.uint8)).astype(bool)
        got = mocc & win & ~bocc; br, bg = bbox(ref, rej), bbox(got, rej)
        cr = ((br[0]+br[2])/2, (br[1]+br[3])/2); cg = ((bg[0]+bg[2])/2, (bg[1]+bg[3])/2)
        objs.append({"id": o["id"], "bbox_esperada_gazebo_m": [round(v, 3) for v in br], "bbox_en_map_m": [round(v, 3) for v in bg],
                     "error_bbox_max_m": round(max(abs(np.array(br)-np.array(bg))), 3), "error_centro_bbox_m": round(math.hypot(cr[0]-cg[0], cr[1]-cg[1]), 4)})
    out["huellas"] = objs; s = json.dumps(out, indent=1, ensure_ascii=False); print(s)
    if a.json: open(a.json, "w").write(s)

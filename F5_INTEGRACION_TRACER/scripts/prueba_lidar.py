#!/usr/bin/env python3
"""F5: compara el /scan simulado con el MAPA de F4 (trazado de rayos sobre las celdas ocupadas) desde varias poses. Con sim en marcha (arrancar_sin_gui.sh). Uso: prueba_lidar.py <salida.json>
Mide por haz: rango del lidar frente a rango previsto por el mapa; y atribuye las diferencias a objetos del mobiliario (los que el lidar a 0,20 m NO ve: tableros, asientos, respaldos)."""
import sys, os, json, math, yaml, numpy as np, rclpy
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
_a = sys.argv; sys.argv = ['x']
import barrido_mapa as B
sys.argv = _a
from prueba_movimiento import T, yaw
from sensor_msgs.msg import LaserScan
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
objs = yaml.safe_load(open(D + '/../F4_ESCENARIO_CON_MOBILIARIO/config/mobiliario.yaml'))['objetos']
LX = 0.2125   # laser 0,2125 m delante de base_footprint
def raycast(ox, oy, ang, rmax=30.0, paso=0.005):
    dx, dy = math.cos(ang), math.sin(ang); r = 0.10
    while r < rmax:
        x, y = ox+dx*r, oy+dy*r; j = int((x-B.OX)/B.RES); i = B.H-1-int((y-B.OY)/B.RES)
        if not (0 <= i < B.H and 0 <= j < B.W): return None
        if B.occ[i, j]: return r
        r += paso
    return None
def objeto(x, y):
    d = [(math.hypot(x-o['x'], y-o['y']), o['id']) for o in objs]; d.sort(); return d[0][1] if d[0][0] < 1.3 else 'pared/otro'
class L(T):
    def __init__(s):
        super().__init__(); s.scan = None; s.create_subscription(LaserScan, '/scan', lambda m: setattr(s, 'scan', m), 5)
POSES = {'salon_libre': (9.7, -2.7, -90), 'frente_mesa_sillas': (8.9, -3.1, -90), 'junto_caja': (11.6, -6.3, 180), 'entre_mesa_papelera': (7.6, -7.6, 90), 'ante_puerta_dorm3': (12.3, -6.325, 0)}
if __name__ == '__main__':
    mundo = 'piso_amueblado'; rclpy.init(); n = L(); n.esperar_datos(); out = {}
    for nom, (x, y, th) in POSES.items():
        n.reponer(mundo, x, y, math.radians(th)); n.spin_until(n.now()+1.0, 0.0, 0.0); n.scan = None
        while n.scan is None: rclpy.spin_once(n, timeout_sec=0.1)
        n.spin_until(n.now()+0.3); s = n.scan; gx, gy, gth = n.gt[1], n.gt[2], n.gt[3]
        ox, oy = gx+LX*math.cos(gth), gy+LX*math.sin(gth)
        dif = []; vistos_no_mapa = []; mapa_no_vistos = {}; tot = 0; ok = 0
        for i, r in enumerate(s.ranges):
            ang = gth + s.angle_min + i*s.angle_increment; rm = raycast(ox, oy, ang); lv = r if math.isfinite(r) and r >= s.range_min else None; tot += 1
            if lv is not None and rm is not None:
                dif.append(lv-rm)
                if abs(lv-rm) < 0.03: ok += 1
                elif lv > rm+0.03:   # el lidar ve MAS LEJOS de lo que dice el mapa: el mapa tiene algo que el lidar no ve
                    o = objeto(ox+math.cos(ang)*rm, oy+math.sin(ang)*rm); mapa_no_vistos[o] = mapa_no_vistos.get(o, 0)+1
                else: vistos_no_mapa.append((round(lv, 3), round(rm, 3)))
            elif lv is None and rm is not None and rm < s.range_max:
                o = objeto(ox+math.cos(ang)*rm, oy+math.sin(ang)*rm); mapa_no_vistos[o+' (sin retorno)'] = mapa_no_vistos.get(o+' (sin retorno)', 0)+1
            elif lv is not None and rm is None: vistos_no_mapa.append((round(lv, 3), None))
        d = np.array(dif)
        out[nom] = dict(pose_gazebo=[gx, gy, math.degrees(gth)], frame=s.header.frame_id, haces=tot, finitos=int(sum(1 for r in s.ranges if math.isfinite(r))), comparables=len(d),
                        coinciden_3cm=ok, error_mediano_m=float(np.median(np.abs(d))) if len(d) else None, error_p95_m=float(np.percentile(np.abs(d), 95)) if len(d) else None,
                        error_medio_con_signo_m=float(d.mean()) if len(d) else None, mapa_ocupado_pero_lidar_no_ve_por_objeto=mapa_no_vistos, lidar_ve_mas_cerca_que_mapa=len(vistos_no_mapa))
        print(nom, json.dumps(out[nom]), flush=True)
    json.dump(out, open(sys.argv[1], 'w'), indent=1, default=float)

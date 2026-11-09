#!/usr/bin/env python3
"""F5: colisiones del TRACER contra el apartamento amueblado, EN SIMULACION y a 0,3 m/s. Para cada prueba: pose inicial (set_pose), orden v constante durante T s, parada y reposo.
Compara la distancia recorrida hasta parar con la prevista por el MAPA de F4 (barrido de la huella, scripts/barrido_mapa.py) y registra inclinacion/altura (¿trepa?), deriva lateral y giro.
Uso (via lanzar_pruebas.sh con SCRIPT=prueba_colision.py MUNDO=piso_amueblado): prueba_colision.py <mundo> <salida.json> [nombres...]"""
import sys, os, json, math, rclpy
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from prueba_movimiento import T, yaw, wrap
from nav_msgs.msg import Odometry
from sensor_msgs.msg import LaserScan
_a = sys.argv; sys.argv = ['x']
from barrido_mapa import barrido
sys.argv = _a

PRUEBAS = {   # nombre: (x, y, yaw_deg, largo_barrido, v, descripcion)
 'pared':        (9.70, -2.70,  90, 2.0, 0.3, 'pared norte del salon'),
 'mesa_1':       (8.20, -2.70, -90, 3.0, 0.3, 'borde norte de mesa_1 (carril x=8,2, entre silla_N y silla_W)'),
 'silla_N':      (8.90, -2.70, -90, 3.0, 0.3, 'silla_N de frente: respaldo (z>=0,43) y base estimada (z<=0,04)'),
 'silla_E_lateral': (10.05, -2.70, -90, 3.0, 0.3, 'silla_E por el costado (limitacion pendiente de F4)'),
 'caja':         (12.50, -6.30, 180, 3.0, 0.3, 'caja_1 desde el este'),
 'puerta_1.01':  (12.20, -6.325, 0,  3.0, 0.3, 'puerta dorm.3 (hueco 1,01 m): debe pasar'),
 'puerta_0.91':  (11.675, -8.00, 90, 2.4, 0.3, 'puerta dorm.1 (hueco 0,91 m): debe pasar'),
}

class C(T):
    def __init__(s):
        super().__init__(); s.full = []; s.scan = None
        s.create_subscription(LaserScan, '/scan', lambda m: setattr(s, 'scan', m), 5)
    def cb_gt(s, m):
        p = m.pose.pose.position; q = m.pose.pose.orientation
        roll = math.atan2(2*(q.w*q.x+q.y*q.z), 1-2*(q.x*q.x+q.y*q.y)); pitch = math.asin(max(-1, min(1, 2*(q.w*q.y-q.z*q.x))))
        t = m.header.stamp.sec+m.header.stamp.nanosec*1e-9; s.gt = (t, p.x, p.y, yaw(q)); s.full.append((t, p.x, p.y, p.z, roll, pitch, yaw(q), m.twist.twist.linear.x))

if __name__ == '__main__':
    mundo, salida = sys.argv[1], sys.argv[2]; sel = sys.argv[3:] or list(PRUEBAS)
    rclpy.init(); n = C(); n.esperar_datos(); out = {}
    for nombre in sel:
        x, y, th, largo, v, desc = PRUEBAS[nombre]; pred = barrido(x, y, th, largo)
        T_ord = ((pred['contacto_en_m'] if pred['contacto_en_m'] is not None else largo) + 0.6) / v
        n.reponer(mundo, x, y, math.radians(th)); n.full.clear(); i0 = 0
        r = n.mover(v, 0.0, T_ord, reposo=3.0)
        c, sn = math.cos(math.radians(th)), math.sin(math.radians(th))
        trk = [(t, (px-x)*c+(py-y)*sn, -(px-x)*sn+(py-y)*c, z, ro, pi, wrap(w-math.radians(th)), vx) for (t, px, py, z, ro, pi, w, vx) in n.full]
        fin = trk[-1]; recorrido = fin[1]
        res = dict(descripcion=desc, inicio=[x, y, th], v=v, orden_s=T_ord, prediccion_mapa=pred,
                   recorrido_real_m=recorrido, deriva_lateral_final_m=fin[2], giro_final_deg=math.degrees(fin[6]),
                   z_max_m=max(t[3] for t in trk), z_min_m=min(t[3] for t in trk), roll_max_deg=math.degrees(max(abs(t[4]) for t in trk)), pitch_max_deg=math.degrees(max(abs(t[5]) for t in trk)),
                   vel_gz_final_m_s=fin[7], odom_recorrido_m=math.hypot(r['od2'][1]-r['od0'][1], r['od2'][2]-r['od0'][2]),
                   lidar_min_m=(min((v_ for v_ in n.scan.ranges if v_ > n.scan.range_min and math.isfinite(v_)), default=None) if n.scan else None))
        if pred['contacto_en_m'] is not None:
            esp = pred['libre_hasta_m']; res['esperado_parada_m'] = esp; res['diferencia_vs_mapa_m'] = recorrido - esp   # >0: avanzo de mas (penetra / mapa conservador)
            res['bloqueado'] = bool(recorrido < pred['contacto_en_m'] + 0.05 and abs(fin[7]) < 0.02)
        else:
            res['esperado_recorrido_libre_m'] = v*r['dur_real']; res['paso_completo'] = bool(abs(recorrido - v*r['dur_real']) < 0.15)
        out[nombre] = res; print(nombre, json.dumps({k: (round(v_, 4) if isinstance(v_, float) else v_) for k, v_ in res.items() if k not in ('descripcion', 'inicio', 'prediccion_mapa')}), flush=True)
    json.dump(out, open(salida, 'w'), indent=1, default=float); n.destroy_node(); rclpy.shutdown()

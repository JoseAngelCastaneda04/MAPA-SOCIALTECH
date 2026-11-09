#!/usr/bin/env python3
"""F5: auditoria del arbol TF con la demo en marcha (use_sim_time). Mide: arbol y publicador de cada transformacion, duplicados, extrapolaciones, sellos de tiempo frente a /clock,
y la coincidencia map->base_footprint (la cadena que dibuja RViz2) con la pose REAL de Gazebo (/gz/odom_gt, requiere mundo *_gt y scripts/puente_verdad.sh) mientras el robot se mueve.
Uso: comprobar_tf.py <salida.json> [segundos=30]   (0-10 s avanza 0,1 m/s; 10-22 s gira 0,5 rad/s; ARRANCAR el sistema justo antes: odom debe nacer en la pose inicial y no haber chocado)"""
import sys, json, math, time, yaml, rclpy
from rclpy.node import Node
from rclpy.time import Time
from rclpy.duration import Duration
from tf2_ros import Buffer, TransformListener, TransformException
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from rosgraph_msgs.msg import Clock
from tf2_msgs.msg import TFMessage
def yaw(q): return math.atan2(2*(q.w*q.z+q.x*q.y), 1-2*(q.y*q.y+q.z*q.z))
class N(Node):
    def __init__(s):
        super().__init__('comprobar_tf', parameter_overrides=[rclpy.parameter.Parameter('use_sim_time', value=True)])
        s.buf = Buffer(); s.l = TransformListener(s.buf, s); s.pub = s.create_publisher(Twist, '/cmd_vel', 10)
        s.gt = None; s.gtd = {}; s.clock = 0.0; s.lag = []; s.pares = {}
        s.create_subscription(Odometry, '/gz/odom_gt', s.cb_gt, 50)
        s.create_subscription(Clock, '/clock', lambda m: setattr(s, 'clock', m.clock.sec+m.clock.nanosec*1e-9), 50)
        s.create_subscription(TFMessage, '/tf', s.cb_tf, 200)
    def cb_gt(s, m):
        t = m.header.stamp.sec+m.header.stamp.nanosec*1e-9; s.gt = (t, m.pose.pose.position.x, m.pose.pose.position.y, yaw(m.pose.pose.orientation)); s.gtd[round(t*1000)] = s.gt
        if len(s.gtd) > 400: s.gtd.pop(next(iter(s.gtd)))
    def cb_tf(s, m):
        for t in m.transforms:
            st = t.header.stamp.sec+t.header.stamp.nanosec*1e-9; s.lag.append(s.clock-st); s.pares.setdefault((t.header.frame_id, t.child_frame_id), 0); s.pares[(t.header.frame_id, t.child_frame_id)] += 1
if __name__ == '__main__':
    out, dur = sys.argv[1], float(sys.argv[2]) if len(sys.argv) > 2 else 30.0
    rclpy.init(); n = N()
    while n.clock == 0 or n.gt is None: rclpy.spin_once(n, timeout_sec=0.1)
    t0 = n.clock; ok = 0; fallos = []; err = []; k = 0
    while n.clock - t0 < dur:
        rclpy.spin_once(n, timeout_sec=0.01)
        tt = n.clock - t0   # 0-10 s: avanzar 0,1 m/s (1 m, libre); 10-22 s: girar 0,5 rad/s sobre si mismo (6 rad); luego parado
        if tt < 10: m = Twist(); m.linear.x = 0.1; n.pub.publish(m)
        elif tt < 22: m = Twist(); m.angular.z = 0.5; n.pub.publish(m)
        else: n.pub.publish(Twist())
        k += 1
        if k % 5 == 0 and n.clock - t0 > 3.0:   # tras 3 s de calentamiento; instante = marca de 20 ms (la rejilla del odom 50 Hz) con 60 ms de margen
            ms = int(n.clock*1000)//20*20 - 60; g = n.gtd.get(ms)
            try:
                tr = n.buf.lookup_transform('map', 'base_footprint', Time(nanoseconds=ms*1000000, clock_type=n.get_clock().clock_type), Duration(seconds=0.0)); ok += 1
                if g:
                    p = tr.transform.translation; dy = yaw(tr.transform.rotation)-g[3]
                    err.append((math.hypot(p.x-g[1], p.y-g[2]), abs(math.atan2(math.sin(dy), math.cos(dy)))))
                n.buf.lookup_transform('map', 'laser', Time(nanoseconds=ms*1000000, clock_type=n.get_clock().clock_type), Duration(seconds=0.0)); ok += 1
            except TransformException as e: fallos.append(str(e)[:160])
    for _ in range(50): rclpy.spin_once(n, timeout_sec=0.05)
    frames = yaml.safe_load(n.buf.all_frames_as_yaml())
    arbol = {c: dict(padre=v['parent'], publicador=v['broadcaster'], tasa_hz=v['rate'], mas_reciente_s=v['most_recent_transform'], ) for c, v in frames.items()}
    hijos = {}
    for (p, c), cnt in n.pares.items(): hijos.setdefault(c, []).append(p)
    lag = sorted(n.lag)
    res = dict(arbol=arbol, tf_dinamico_padres_por_hijo=hijos, hijos_con_varios_padres=[c for c, p in hijos.items() if len(set(p)) > 1],
               lookups_ok=ok, lookups_fallidos=len(fallos), primeros_fallos=fallos[:3],
               err_map_base_footprint_vs_gazebo_m=dict(n=len(err), media=sum(e[0] for e in err)/max(1, len(err)), max=max((e[0] for e in err), default=None)),
               err_yaw_deg=dict(media=math.degrees(sum(e[1] for e in err)/max(1, len(err))), max=math.degrees(max((e[1] for e in err), default=0))),
               retraso_sello_vs_clock_s=dict(mediana=lag[len(lag)//2] if lag else None, max=lag[-1] if lag else None, min=lag[0] if lag else None, n=len(lag)))
    json.dump(res, open(out, 'w'), indent=1, default=str); print(json.dumps({k: v for k, v in res.items() if k != 'arbol'}, indent=1, default=str)); print(yaml.dump(arbol))
    n.destroy_node(); rclpy.shutdown()

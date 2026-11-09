#!/usr/bin/env python3
"""F5: frecuencia de /odom /tf /joint_states /scan /clock en tiempo de SIMULACION y de pared durante N s (por defecto 10). Uso: medir_frecuencias.py [segundos] [salida.json]"""
import sys, time, json, rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry
from tf2_msgs.msg import TFMessage
from sensor_msgs.msg import JointState, LaserScan
from rosgraph_msgs.msg import Clock
class F(Node):
    def __init__(s):
        super().__init__('medir_frec'); s.n = {}; s.sim = {}
        for nom, tp in (('/odom', Odometry), ('/tf', TFMessage), ('/joint_states', JointState), ('/scan', LaserScan), ('/clock', Clock)):
            s.create_subscription(tp, nom, (lambda m, nom=nom: s.cb(nom, m)), 100); s.n[nom] = 0; s.sim[nom] = []
    def cb(s, nom, m):
        s.n[nom] += 1
        if nom == '/clock': s.sim[nom].append(m.clock.sec+m.clock.nanosec*1e-9)
        elif hasattr(m, 'header'): s.sim[nom].append(m.header.stamp.sec+m.header.stamp.nanosec*1e-9)
        elif nom == '/tf' and m.transforms: s.sim[nom].append(m.transforms[0].header.stamp.sec+m.transforms[0].header.stamp.nanosec*1e-9)
if __name__ == '__main__':
    d = float(sys.argv[1]) if len(sys.argv) > 1 else 10.0; rclpy.init(); n = F(); t0 = time.time()
    while time.time()-t0 < d: rclpy.spin_once(n, timeout_sec=0.05)
    w = time.time()-t0; out = {}
    for k in n.n:
        s = n.sim[k]; ds = (s[-1]-s[0]) if len(s) > 1 else None
        out[k] = dict(mensajes=n.n[k], hz_pared=n.n[k]/w, hz_sim=((len(s)-1)/ds if ds else None))
    print(json.dumps(out, indent=1)); 
    if len(sys.argv) > 2: json.dump(out, open(sys.argv[2], 'w'), indent=1)
    rclpy.shutdown()

#!/usr/bin/env python3
"""F5.2: compara /scan con un trazado de rayos sobre el mapa de F4 desde la pose REAL (/gz/odom_gt). Captura N escaneos separados por movimiento que ordenes tu (o por --esperar s).
Uso: comprobar_lidar.py [n_capturas=2] [segundos_entre_capturas=0] ; imprime por captura: pose real, mediana |scan - mapa| y fraccion de haces con |dif|<5 cm; y cuantos haces cambian entre capturas.
Limitacion conocida (F5): el LiDAR (0,20 m) no ve sillas/tableros que el mapa si marca -> parte de los haces 'ven mas lejos' que el mapa."""
import sys, math, time, numpy as np, yaml, rclpy
from PIL import Image
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from nav_msgs.msg import Odometry
M = '/home/jose-angel/Desktop/MAPA SOCIALTECH/F4_ESCENARIO_CON_MOBILIARIO/mapa/'
im = np.array(Image.open(M + 'piso_amueblado.pgm')); H, W = im.shape; ox, oy, res = 4.7299, -11.32, 0.01
def occ(x, y):
    c = int((x-ox)/res); r = H-1-int((y-oy)/res); return (not (0 <= c < W and 0 <= r < H)) or im[r, c] < 250
def ray(x, y, a, rmax=30.0):
    d = 0.1
    while d < rmax:
        if occ(x+d*math.cos(a), y+d*math.sin(a)): return d
        d += 0.01
    return rmax
def yaw_de(q): return math.atan2(2*(q.w*q.z+q.x*q.y), 1-2*(q.y*q.y+q.z*q.z))
rclpy.init(); n = Node('comprobar_lidar'); S = {}; G = {}
n.create_subscription(LaserScan, '/scan', lambda m: S.__setitem__('m', m), 5); n.create_subscription(Odometry, '/gz/odom_gt', lambda m: G.__setitem__('m', m), 5)
caps = int(sys.argv[1]) if len(sys.argv) > 1 else 2; gap = float(sys.argv[2]) if len(sys.argv) > 2 else 0; prev = None
for k in range(caps):
    S.clear(); G.clear()
    while not (S and G): rclpy.spin_once(n, timeout_sec=0.2)
    s = S['m']; g = G['m'].pose.pose; x, y, th = g.position.x, g.position.y, yaw_de(g.orientation)
    lx, ly = x + 0.2125*math.cos(th), y + 0.2125*math.sin(th)   # el LiDAR esta 0,2125 m por delante de base_footprint (laser_joint del URDF de F5)
    r = np.array(s.ranges); idx = np.arange(0, len(r), 6); ok = np.isfinite(r[idx])
    exp = np.array([ray(lx, ly, th + s.angle_min + i*s.angle_increment) for i in idx]); d = np.abs(r[idx][ok] - exp[ok])
    print('captura %d: pose real (%.2f, %.2f, %.0f deg) | haces %d (cada 6.o) | mediana |scan-mapa| %.3f m | dentro de 5 cm: %.0f %% | scan ve MAS lejos que el mapa (>20 cm): %.0f %%' % (k+1, x, y, math.degrees(th), len(d), np.median(d), 100*np.mean(d < .05), 100*np.mean(r[idx][ok] - exp[ok] > .2)))
    if prev is not None: print('   haces que cambian > 5 cm respecto a la captura anterior: %.0f %%' % (100*np.mean(np.abs(np.nan_to_num(r, posinf=30) - np.nan_to_num(prev, posinf=30)) > .05)))
    prev = r
    if k < caps-1:
        print('   -> mueve el robot (o espera %.0f s)...' % gap, flush=True); time.sleep(gap) if gap else input()

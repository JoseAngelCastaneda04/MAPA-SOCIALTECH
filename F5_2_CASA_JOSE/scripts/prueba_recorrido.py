#!/usr/bin/env python3
"""F5.2: recorrido automatico (lazo abierto, 0,2 m/s y 0,5 rad/s) por el salon oeste de la casa, validado ANTES sobre el mapa (huella r=0,42 m libre en todo el trayecto).
Ruta (desde la pose inicial 9,70/-2,70/-90): giro -90, 2,0 m, giro -90, 1,4 m, giro +90, 1,2 m, giro +90, 1,4 m, giro +90, 3,2 m, giro +90  (= 'S' y vuelta, termina cerca del inicio).
Modo --empuje: tras --vueltas, avanza contra una pared 5 s (las ruedas patinan: provoca deriva de la odometria a proposito).
Imprime t_ini/t_fin en tiempo de simulacion para filtrar el CSV del monitor. Solo publica /cmd_vel (pasa por el watchdog)."""
import sys, math, argparse, rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
ap = argparse.ArgumentParser(); ap.add_argument('--vueltas', type=int, default=1); ap.add_argument('--v', type=float, default=0.2); ap.add_argument('--w', type=float, default=0.5)
ap.add_argument('--empuje', type=float, default=0.0, help='segundos empujando hacia delante al final (con --pared-previa)'); ap.add_argument('--pausa', type=float, default=1.0); a = ap.parse_args()
R = [('t', -90), ('f', 2.0), ('t', -90), ('f', 1.4), ('t', 90), ('f', 1.2), ('t', 90), ('f', 1.4), ('t', 90), ('f', 3.2), ('t', 90)]
rclpy.init(); n = Node('prueba_recorrido', parameter_overrides=[rclpy.parameter.Parameter('use_sim_time', rclpy.Parameter.Type.BOOL, True)])
pub = n.create_publisher(Twist, '/cmd_vel', 10)
def ahora(): return n.get_clock().now().nanoseconds * 1e-9
def mover(vx, wz, dur):
    t0 = ahora(); m = Twist(); m.linear.x = vx; m.angular.z = wz
    while ahora() - t0 < dur and rclpy.ok(): pub.publish(m); rclpy.spin_once(n, timeout_sec=0.05)
while ahora() == 0.0: rclpy.spin_once(n, timeout_sec=0.1)
print('t_ini', round(ahora(), 2), flush=True)
for v in range(a.vueltas):
    for k, val in R:
        if k == 'f': mover(a.v, 0.0, val / a.v)
        else: mover(0.0, math.copysign(a.w, val), math.radians(abs(val)) / a.w)
        mover(0.0, 0.0, a.pausa)
if a.empuje > 0: mover(a.v, 0.0, a.empuje)
mover(0.0, 0.0, 1.5)
print('t_fin', round(ahora(), 2), flush=True)

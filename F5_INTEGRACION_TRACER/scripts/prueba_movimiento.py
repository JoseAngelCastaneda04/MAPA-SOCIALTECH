#!/usr/bin/env python3
"""F5: pruebas A-E de movimiento. Compara ORDEN (cmd_vel) -> ODOMETRIA (/odom) -> POSE REAL en Gazebo (verdad de terreno por /gz/odom_gt = OdometryPublisher del include del mundo, marca de tiempo de simulacion).
Requiere: Gazebo con el mundo, bridge (config/bridge.yaml) y el puente de verdad de terreno (ros2 run ros_gz_bridge parameter_bridge /gz/pose@... ; lo lanza scripts/lanzar_pruebas.sh).
Uso: prueba_movimiento.py <mundo> <salida.json> [A B C D E]   Todo en tiempo de simulacion (use_sim_time)."""
import sys, json, math, time, subprocess, rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry

def yaw(q): return math.atan2(2*(q.w*q.z+q.x*q.y), 1-2*(q.y*q.y+q.z*q.z))
def wrap(a): return (a+math.pi) % (2*math.pi)-math.pi

class T(Node):
    def __init__(s, modelo='tracer'):
        super().__init__('prueba_mov', parameter_overrides=[rclpy.parameter.Parameter('use_sim_time', value=True)])
        s.m = modelo; s.gt = None; s.od = None; s.trace = []
        s.pub = s.create_publisher(Twist, '/cmd_vel', 10)
        s.create_subscription(Odometry, '/gz/odom_gt', s.cb_gt, 50)
        s.create_subscription(Odometry, '/odom', s.cb_od, 50)
    def cb_gt(s, m):
        p = m.pose.pose.position; s.gt = (m.header.stamp.sec+m.header.stamp.nanosec*1e-9, p.x, p.y, yaw(m.pose.pose.orientation)); s.trace.append(s.gt)
    def cb_od(s, m):
        p = m.pose.pose.position; s.od = (m.header.stamp.sec+m.header.stamp.nanosec*1e-9, p.x, p.y, yaw(m.pose.pose.orientation),
                                          m.twist.twist.linear.x, m.twist.twist.angular.z)
    def now(s): return s.get_clock().now().nanoseconds*1e-9
    def spin_until(s, t_end, v=None, w=None, hz=20):
        nxt = 0
        while s.now() < t_end:
            rclpy.spin_once(s, timeout_sec=0.02)
            if v is not None and s.now() >= nxt:
                m = Twist(); m.linear.x = v; m.angular.z = w; s.pub.publish(m); nxt = s.now()+1.0/hz
    def esperar_datos(s):
        while s.gt is None or s.od is None or s.now() == 0: rclpy.spin_once(s, timeout_sec=0.1)
    def mover(s, v, w, dur, reposo=3.0):
        """Publica (v,w) durante dur s de simulacion; luego 0 durante `reposo` s. Devuelve poses: inicio, fin de orden, reposo."""
        s.spin_until(s.now()+0.3); g0, o0 = s.gt, s.od; t0 = s.now()
        s.spin_until(t0+dur, v, w); g1, o1 = s.gt, s.od; t1 = s.now()
        s.spin_until(t1+reposo, 0.0, 0.0); g2, o2 = s.gt, s.od
        return dict(v=v, w=w, dur_ordenada=dur, dur_real=t1-t0, gt0=g0, gt1=g1, gt2=g2, od0=o0, od1=o1, od2=o2)
    def reponer(s, mundo, x=0.0, y=0.0, th=0.0):
        qz, qw = math.sin(th/2), math.cos(th/2)
        subprocess.run(['gz', 'service', '-s', f'/world/{mundo}/set_pose', '--reqtype', 'gz.msgs.Pose', '--reptype', 'gz.msgs.Boolean', '--timeout', '3000',
                        '--req', f'name: "{s.m}" position {{x:{x} y:{y} z:0.002}} orientation {{z:{qz} w:{qw}}}'], capture_output=True)
        s.spin_until(s.now()+2.0, 0.0, 0.0)

def rel(g0, g1):  # desplazamiento en el marco del robot al inicio + giro
    dx, dy = g1[1]-g0[1], g1[2]-g0[2]; c, sn = math.cos(g0[3]), math.sin(g0[3])
    return dict(fwd=c*dx+sn*dy, lat=-sn*dx+c*dy, dist=math.hypot(dx, dy), dyaw=wrap(g1[3]-g0[3]))

def analizar(r):
    gt = rel(r['gt0'], r['gt1']); od = rel(r['od0'][:4], r['od1'][:4]); gtf = rel(r['gt0'], r['gt2']); odf = rel(r['od0'][:4], r['od2'][:4])
    d = r['dur_real']; v, w = r['v'], r['w']
    if abs(w) < 1e-9: esp = dict(fwd=v*d, lat=0.0, dyaw=0.0)
    elif abs(v) < 1e-9: esp = dict(fwd=0.0, lat=0.0, dyaw=w*d)
    else: R = v/w; esp = dict(fwd=R*math.sin(w*d), lat=R*(1-math.cos(w*d)), dyaw=w*d)
    return dict(orden=dict(v=v, w=w, dur_s=round(d, 4)), esperado=esp, gazebo_fin_orden=gt, odom_fin_orden=od, gazebo_tras_reposo=gtf, odom_tras_reposo=odf,
                err_gazebo_vs_esperado=dict(fwd=gt['fwd']-esp['fwd'], lat=gt['lat']-esp['lat'], dyaw=wrap(gt['dyaw']-esp['dyaw'])),
                err_odom_vs_gazebo=dict(fwd=od['fwd']-gt['fwd'], lat=od['lat']-gt['lat'], dyaw=wrap(od['dyaw']-gt['dyaw'])),
                vel_odom_final=dict(v=r['od1'][4], w=r['od1'][5]), deriva_tras_parar=dict(dist=math.hypot(gtf['fwd']-gt['fwd'], gtf['lat']-gt['lat']), dyaw=wrap(gtf['dyaw']-gt['dyaw'])))

if __name__ == '__main__':
    mundo, salida = sys.argv[1], sys.argv[2]; sel = sys.argv[3:] or list('ABCDE')
    rclpy.init(); n = T(); n.esperar_datos(); out = {}
    def un(nombre, v, w, dur):
        n.reponer(mundo); r = analizar(n.mover(v, w, dur)); out.setdefault(nombre, []).append(r)
        print(nombre, 'v=%.2f w=%.2f dur=%.2f | gz fwd %.4f lat %.4f dyaw %.2f° | esperado %.4f / %.2f° | odom-gz fwd %.4f dyaw %.3f°' % (v, w, r['orden']['dur_s'], r['gazebo_fin_orden']['fwd'], r['gazebo_fin_orden']['lat'], math.degrees(r['gazebo_fin_orden']['dyaw']), r['esperado']['fwd'], math.degrees(r['esperado']['dyaw']), r['err_odom_vs_gazebo']['fwd'], math.degrees(r['err_odom_vs_gazebo']['dyaw'])), flush=True)
    if 'A' in sel:
        for v in (0.1, 0.3, 0.6, 1.0, 1.5): un('A_avance', v, 0.0, 4.0 if v < 1 else 2.0)
        un('A_marcha_atras', -0.3, 0.0, 4.0)
    if 'B' in sel:
        for w in (0.2, 0.5, 1.0, 1.5): un('B_giro_izq', 0.0, w, (math.pi/2)/w)
        un('B_giro_der', 0.0, -0.5, (math.pi/2)/0.5)
    if 'C' in sel:
        for v in (0.3, 1.0): un('C_parada_tras_avance', v, 0.0, 3.0)
        un('C_parada_tras_giro', 0.0, 1.0, 2.0)
    if 'D' in sel:
        for v, w in ((0.3, 0.3), (0.5, -0.4), (0.8, 0.8), (-0.3, 0.3)): un('D_combinado', v, w, 5.0)
    if 'E' in sel:   # cuadrado de 1 m, 3 repeticiones, mismo comando; compara pose final
        n.reponer(mundo); reps = []
        for k in range(3):
            n.reponer(mundo); g0 = n.gt
            for _ in range(4):
                n.mover(0.25, 0.0, 4.0, 1.0); n.mover(0.0, 0.5, (math.pi/2)/0.5, 1.0)
            g1 = n.gt; reps.append(dict(rep=k+1, fin_vs_inicio=rel(g0, g1), fin_abs=g1[1:], odom=n.od))
            print('E rep', k+1, rel(g0, g1), flush=True)
        out['E_cuadrado'] = reps
    json.dump(out, open(salida, 'w'), indent=1, default=float); n.destroy_node(); rclpy.shutdown()

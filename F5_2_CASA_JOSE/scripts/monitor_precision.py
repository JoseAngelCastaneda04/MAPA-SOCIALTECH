#!/usr/bin/env python3
"""F5.2: compara TRES poses en el marco del mapa y las dibuja en RViz2 (no publica TF; no contamina el localizador).
  GT   : pose real en Gazebo (/gz/odom_gt, OdometryPublisher del mundo *_gt.sdf; mundo = mapa)              -> verde
  ODOM : SOLO odometria: pose inicial conocida (F5/config/inicio.yaml) compuesta con /odom                    -> amarillo
  AMCL : TF map->base_footprint (AMCL publica map->odom, Gazebo odom->base_footprint)                        -> cian
Publica: /f52/path_{gt,odom,amcl} (nav_msgs/Path), /f52/marcadores (flechas + texto de error + zonas prohibidas visuales).
Registra CSV (--csv) con t_sim, x/y/yaw de las tres y los errores (posicion m, yaw grados, con signo normalizado)."""
import math, sys, os, argparse, yaml
import rclpy
from rclpy.node import Node
from rclpy.duration import Duration
from rclpy.time import Time
from nav_msgs.msg import Odometry, Path
from geometry_msgs.msg import PoseStamped
from visualization_msgs.msg import Marker, MarkerArray
from tf2_ros import Buffer, TransformListener

def yaw_de(q): return math.atan2(2*(q.w*q.z+q.x*q.y), 1-2*(q.y*q.y+q.z*q.z))
def wrap(a): return (a+math.pi) % (2*math.pi)-math.pi
def quat(yaw): return (0.0, 0.0, math.sin(yaw/2), math.cos(yaw/2))

class Mon(Node):
    def __init__(s, a):
        super().__init__('monitor_precision', parameter_overrides=[rclpy.parameter.Parameter('use_sim_time', rclpy.Parameter.Type.BOOL, True)])
        D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        c = yaml.safe_load(open(D + '/../F5_INTEGRACION_TRACER/config/inicio.yaml')); s.p0 = (c['x'], c['y'], math.radians(c['yaw_deg']))
        s.zonas = yaml.safe_load(open(D + '/config/zonas_prohibidas.yaml')).get('zonas') or []
        s.gt = s.od = None; s.buf = Buffer(); s.tl = TransformListener(s.buf, s)
        s.create_subscription(Odometry, '/gz/odom_gt', lambda m: setattr(s, 'gt', (m.pose.pose.position.x, m.pose.pose.position.y, yaw_de(m.pose.pose.orientation))), 10)
        s.create_subscription(Odometry, '/odom', s.cb_odom, 10)
        s.pp = {k: s.create_publisher(Path, '/f52/path_' + k, 10) for k in ('gt', 'odom', 'amcl')}
        s.paths = {k: Path() for k in s.pp}; s.mk = s.create_publisher(MarkerArray, '/f52/marcadores', 10)
        s.csv = open(a.csv, 'w') if a.csv else None
        if s.csv: s.csv.write('t,gt_x,gt_y,gt_yaw,odom_x,odom_y,odom_yaw,amcl_x,amcl_y,amcl_yaw,err_odom_pos,err_odom_yaw_deg,err_amcl_pos,err_amcl_yaw_deg\n')
        s.n = 0; s.create_timer(0.1, s.tick); s.create_timer(1.0, s.zonas_pub)
    def cb_odom(s, m):
        x0, y0, t0 = s.p0; x, y, th = m.pose.pose.position.x, m.pose.pose.position.y, yaw_de(m.pose.pose.orientation)
        s.od = (x0 + math.cos(t0)*x - math.sin(t0)*y, y0 + math.sin(t0)*x + math.cos(t0)*y, wrap(t0 + th))
    def amcl(s):
        try:
            t = s.buf.lookup_transform('map', 'base_footprint', Time(), Duration(seconds=0.05)).transform   # ultima disponible
            return (t.translation.x, t.translation.y, yaw_de(t.rotation))
        except Exception: return None
    def ps(s, p, now):
        m = PoseStamped(); m.header.frame_id = 'map'; m.header.stamp = now
        m.pose.position.x, m.pose.position.y = p[0], p[1]; q = quat(p[2]); m.pose.orientation.z, m.pose.orientation.w = q[2], q[3]; return m
    def flecha(s, i, p, col, ns, now):
        m = Marker(); m.header.frame_id = 'map'; m.header.stamp = now; m.ns = ns; m.id = i; m.type = Marker.ARROW; m.action = Marker.ADD
        q = quat(p[2]); m.pose.position.x, m.pose.position.y, m.pose.position.z = p[0], p[1], 0.35; m.pose.orientation.z, m.pose.orientation.w = q[2], q[3]
        m.scale.x, m.scale.y, m.scale.z = 0.55, 0.09, 0.09; m.color.r, m.color.g, m.color.b = col; m.color.a = 1.0; return m
    def tick(s):
        a = s.amcl()
        if s.gt is None or s.od is None or a is None: return
        now = s.get_clock().now().to_msg()
        P = {'gt': s.gt, 'odom': s.od, 'amcl': a}; err = {}
        for k in ('odom', 'amcl'): err[k] = (math.hypot(P[k][0]-s.gt[0], P[k][1]-s.gt[1]), math.degrees(wrap(P[k][2]-s.gt[2])))
        for k, p in P.items():
            pa = s.paths[k]; pa.header.frame_id = 'map'; pa.header.stamp = now
            if not pa.poses or math.hypot(p[0]-pa.poses[-1].pose.position.x, p[1]-pa.poses[-1].pose.position.y) > 0.03: pa.poses.append(s.ps(p, now))
            s.pp[k].publish(pa)
        ma = MarkerArray()
        ma.markers += [s.flecha(1, s.gt, (0.1, 1.0, 0.1), 'gt', now), s.flecha(2, s.od, (1.0, 0.9, 0.1), 'odom', now), s.flecha(3, a, (0.1, 0.9, 1.0), 'amcl', now)]
        t = Marker(); t.header.frame_id = 'map'; t.header.stamp = now; t.ns = 'err'; t.id = 4; t.type = Marker.TEXT_VIEW_FACING; t.action = Marker.ADD
        t.pose.position.x, t.pose.position.y, t.pose.position.z = s.gt[0], s.gt[1], 1.0; t.scale.z = 0.22; t.color.r = t.color.g = t.color.b = t.color.a = 1.0
        t.text = 'err odom %.3f m %+.1f deg\nerr AMCL %.3f m %+.1f deg' % (err['odom'][0], err['odom'][1], err['amcl'][0], err['amcl'][1]); ma.markers.append(t)
        s.mk.publish(ma)
        if s.csv:
            s.csv.write('%.3f,' % (now.sec + now.nanosec*1e-9) + ','.join('%.5f' % v for k in ('gt', 'odom', 'amcl') for v in P[k]) + ',%.5f,%.4f,%.5f,%.4f\n' % (*err['odom'], *err['amcl'])); s.n += 1
            if s.n % 20 == 0: s.csv.flush()
    def zonas_pub(s):
        ma = MarkerArray(); now = s.get_clock().now().to_msg()
        for i, z in enumerate(s.zonas):
            x0, y0, x1, y1 = z['rect']; m = Marker(); m.header.frame_id = 'map'; m.header.stamp = now; m.ns = 'zonas'; m.id = 100 + i; m.type = Marker.CUBE; m.action = Marker.ADD
            m.pose.position.x, m.pose.position.y, m.pose.position.z = (x0+x1)/2, (y0+y1)/2, 0.02; m.pose.orientation.w = 1.0; m.scale.x, m.scale.y, m.scale.z = abs(x1-x0), abs(y1-y0), 0.02
            m.color.r, m.color.g, m.color.b, m.color.a = 1.0, 0.1, 0.1, 0.35; ma.markers.append(m)
            t = Marker(); t.header = m.header; t.ns = 'zonas_txt'; t.id = 200 + i; t.type = Marker.TEXT_VIEW_FACING; t.action = Marker.ADD; t.text = z['nombre'] + ' (solo visual)'
            t.pose.position.x, t.pose.position.y, t.pose.position.z = (x0+x1)/2, (y0+y1)/2, 0.3; t.scale.z = 0.18; t.color.r = 1.0; t.color.g = t.color.b = 0.4; t.color.a = 1.0; ma.markers.append(t)
        s.mk.publish(ma)

ap = argparse.ArgumentParser(); ap.add_argument('--csv', default=None); a = ap.parse_args(sys.argv[1:])
rclpy.init(); n = Mon(a)
try: rclpy.spin(n)
except KeyboardInterrupt: pass
if n.csv: n.csv.close()

#!/usr/bin/env python3
"""F5: watchdog de /cmd_vel. Gazebo Harmonic 8.15 (DiffDrive) NO tiene timeout: conserva la ultima orden. Este nodo es la UNICA entrada del DiffDrive:
   /cmd_vel (usuario) --> [watchdog] --> /cmd_vel_seguro (50 Hz, SIEMPRE publica) --> puente --> gz /cmd_vel_seguro --> DiffDrive
Si la ultima /cmd_vel recibida tiene mas de `timeout` s (TIEMPO DE SIMULACION), publica velocidad cero. Una orden vieja NUNCA se reenvia: tras caducar hay que enviar una orden nueva.
Los mensajes con valores no finitos se descartan. Sin dependencias; ~40 lineas."""
import math, rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist

class Watchdog(Node):
    def __init__(s):
        super().__init__('watchdog_cmd_vel')
        s.declare_parameter('timeout', 0.5); s.declare_parameter('rate', 50.0)
        s.declare_parameter('entrada', '/cmd_vel'); s.declare_parameter('salida', '/cmd_vel_seguro')
        s.to = s.get_parameter('timeout').value; s.ultima = None; s.t_ultima = None; s.caducada = True
        s.pub = s.create_publisher(Twist, s.get_parameter('salida').value, 10)
        s.create_subscription(Twist, s.get_parameter('entrada').value, s.cb, 10)
        s.create_timer(1.0/s.get_parameter('rate').value, s.tick)
    def cb(s, m):
        v = [m.linear.x, m.linear.y, m.linear.z, m.angular.x, m.angular.y, m.angular.z]
        if all(math.isfinite(x) for x in v): s.ultima = m; s.t_ultima = s.get_clock().now(); s.caducada = False
    def tick(s):
        out = Twist()
        if s.ultima is not None and (s.get_clock().now() - s.t_ultima).nanoseconds*1e-9 <= s.to: out = s.ultima
        elif not s.caducada:
            s.caducada = True; s.get_logger().info('orden caducada (> %.2f s sin /cmd_vel): parada' % s.to)
        s.pub.publish(out)

def main():
    rclpy.init(); n = Watchdog()
    try: rclpy.spin(n)
    except KeyboardInterrupt: pass
    finally:
        try: n.pub.publish(Twist())     # ultimo mensaje: parada
        except Exception: pass
        n.destroy_node()
        if rclpy.ok(): rclpy.shutdown()
if __name__ == '__main__': main()

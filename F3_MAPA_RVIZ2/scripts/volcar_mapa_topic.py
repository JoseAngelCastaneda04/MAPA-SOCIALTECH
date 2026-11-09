#!/usr/bin/env python3
"""F3: suscribe a /map (QoS transient_local, como RViz2) y guarda EXACTAMENTE lo recibido en un .npz.
Uso: volcar_mapa_topic.py salida.npz [topic]   (python del sistema + ROS 2 sourced)"""
import sys, time, numpy as np, rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, DurabilityPolicy, ReliabilityPolicy, HistoryPolicy
from nav_msgs.msg import OccupancyGrid
rclpy.init(); n = Node("volcar_mapa"); got = {}
q = QoSProfile(depth=1, durability=DurabilityPolicy.TRANSIENT_LOCAL, reliability=ReliabilityPolicy.RELIABLE, history=HistoryPolicy.KEEP_LAST)
t0 = time.time()
n.create_subscription(OccupancyGrid, sys.argv[2] if len(sys.argv) > 2 else "/map", lambda m: got.setdefault("m", (m, time.time() - t0)), q)
while "m" not in got and time.time() - t0 < 30: rclpy.spin_once(n, timeout_sec=0.2)
m, dt = got["m"]; i = m.info
np.savez(sys.argv[1], data=np.array(m.data, dtype=np.int8).reshape(i.height, i.width), res=i.resolution,
         origin=[i.origin.position.x, i.origin.position.y, i.origin.position.z],
         quat=[i.origin.orientation.x, i.origin.orientation.y, i.origin.orientation.z, i.origin.orientation.w], frame=m.header.frame_id)
print(f"recibido en {dt:.3f} s: {i.width}x{i.height} res {i.resolution} origen ({i.origin.position.x},{i.origin.position.y}) frame {m.header.frame_id}")

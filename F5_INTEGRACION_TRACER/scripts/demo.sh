#!/usr/bin/env bash
# F5: demostracion = Gazebo (piso amueblado + TRACER) + puente + TF + mapa + RViz2. Ctrl+C o scripts/parar_demo.sh cierra todo (por grupo de procesos, sin pkill).
# Uso: scripts/demo.sh [mundo_sin_extension]   (por defecto piso_amueblado_tracer)
source /opt/ros/jazzy/setup.bash
D="$(cd "$(dirname "$0")/.." && pwd)"; mkdir -p /tmp/f5_demo
if [ -f /tmp/f5_demo/gazebo.pid ] && kill -0 "$(cat /tmp/f5_demo/gazebo.pid)" 2>/dev/null; then echo "ERROR: la demo ya esta en marcha (scripts/parar_demo.sh para cerrarla)"; exit 2; fi
"$D/scripts/generar_mundo.py" > /dev/null
setsid "$D/scripts/demo_gazebo.sh" "${1:-piso_amueblado_tracer}" > /tmp/f5_demo/gazebo.log 2>&1 & echo $! > /tmp/f5_demo/gazebo.pid
setsid ros2 launch "$D/launch/tracer_piso.launch.py" rviz:="${RVIZ:-true}" > /tmp/f5_demo/ros.log 2>&1 & echo $! > /tmp/f5_demo/ros.pid
trap '"$D/scripts/parar_demo.sh"; exit 0' INT TERM
cat <<MSG
Demo F5 en marcha (Gazebo PID $(cat /tmp/f5_demo/gazebo.pid), ROS 2 launch PID $(cat /tmp/f5_demo/ros.pid)).
Mover el robot (parada automatica si no llegan ordenes en 0,5 s) desde OTRA terminal:   scripts/teleop.sh      (teclado)   o   ros2 topic pub -r 10 /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.2}}"
Cerrar: Ctrl+C aqui o scripts/parar_demo.sh
MSG
wait

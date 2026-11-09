#!/usr/bin/env bash
# F3: demostración completa = Gazebo (3D) + map_server + RViz2 (mapa). Ctrl+C cierra todo.  Uso: scripts/demo.sh [piso_1cm|piso_2cm]
source /opt/ros/jazzy/setup.bash
D="$(cd "$(dirname "$0")/.." && pwd)"; mkdir -p /tmp/f3_demo
setsid "$D/scripts/demo_gazebo.sh" > /tmp/f3_demo/gazebo.log 2>&1 & echo $! > /tmp/f3_demo/gazebo.pid
setsid ros2 launch "$D/launch/mapa_rviz.launch.py" mapa:="${1:-piso_1cm}" > /tmp/f3_demo/rviz.log 2>&1 & echo $! > /tmp/f3_demo/rviz.pid
trap '"$D/scripts/parar_demo.sh"; exit 0' INT TERM
echo "Demo en marcha (Gazebo PID $(cat /tmp/f3_demo/gazebo.pid), ROS 2 launch PID $(cat /tmp/f3_demo/rviz.pid)). Ctrl+C o scripts/parar_demo.sh para cerrar."
wait

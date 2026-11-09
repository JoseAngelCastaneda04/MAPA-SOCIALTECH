#!/usr/bin/env bash
# F4: demostracion = Gazebo (piso amueblado) + map_server (mapa actualizado) + TF identidad + RViz2. Ctrl+C cierra todo.
# Uso: scripts/demo.sh [mundo_sin_extension] [config_rviz]   (por defecto piso_amueblado piso_amueblado)
source /opt/ros/jazzy/setup.bash
D="$(cd "$(dirname "$0")/.." && pwd)"; mkdir -p /tmp/f4_demo
setsid "$D/scripts/demo_gazebo.sh" "${1:-piso_amueblado}" > /tmp/f4_demo/gazebo.log 2>&1 & echo $! > /tmp/f4_demo/gazebo.pid
setsid ros2 launch "$D/launch/mapa_rviz.launch.py" config:="${2:-piso_amueblado}" > /tmp/f4_demo/rviz.log 2>&1 & echo $! > /tmp/f4_demo/rviz.pid
trap '"$D/scripts/parar_demo.sh"; exit 0' INT TERM
echo "Demo F4 en marcha (Gazebo PID $(cat /tmp/f4_demo/gazebo.pid), ROS 2 launch PID $(cat /tmp/f4_demo/rviz.pid)). Ctrl+C o scripts/parar_demo.sh para cerrar."
wait

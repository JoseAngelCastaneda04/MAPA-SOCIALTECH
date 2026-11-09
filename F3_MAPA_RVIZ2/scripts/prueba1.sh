#!/usr/bin/env bash
# Prueba 1: map_server + lifecycle_manager (autostart) con el mapa de 1 cm
source /opt/ros/jazzy/setup.bash
D="$(cd "$(dirname "$0")/.." && pwd)"
ros2 run nav2_map_server map_server --ros-args -p yaml_filename:="$D/mapa/piso_1cm.yaml" &
ros2 run nav2_lifecycle_manager lifecycle_manager --ros-args -p autostart:=true -p node_names:="['map_server']" &
wait

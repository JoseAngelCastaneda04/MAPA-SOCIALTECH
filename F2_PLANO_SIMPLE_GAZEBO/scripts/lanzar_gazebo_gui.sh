#!/usr/bin/env bash
# F2: abre el mundo en la GUI de Gazebo Harmonic. Uso: lanzar_gazebo_gui.sh <mundo.sdf> <dir_modelos>
source /opt/ros/jazzy/setup.bash
export GZ_SIM_RESOURCE_PATH="$2" SDF_PATH="$2"
exec gz sim -r "$1"

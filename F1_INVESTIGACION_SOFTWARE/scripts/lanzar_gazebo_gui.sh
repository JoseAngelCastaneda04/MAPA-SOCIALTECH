#!/usr/bin/env bash
# Abre un mundo de prueba de F1 en la interfaz gráfica de Gazebo Harmonic.
# Uso: lanzar_gazebo_gui.sh <mundo.sdf> <dir_modelos_extra>
set -e
F1="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source /opt/ros/jazzy/setup.bash
export GZ_SIM_RESOURCE_PATH="$2:$F1/../F0_AUDITORIA_REPOSITORIOS/SocialTech-Gazebo/models"
export SDF_PATH="$GZ_SIM_RESOURCE_PATH"
exec gz sim -r "$1"

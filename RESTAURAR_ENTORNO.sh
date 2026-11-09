#!/usr/bin/env bash
# Reconstruye lo que NO se sube a GitHub (repos externos, venv, LibreDWG, ws de F1, mallas del TRACER).
# Requisitos: Ubuntu 24.04, ROS 2 Jazzy, Gazebo Harmonic, git, build-essential, python3-venv, xacro. Sin sudo.
set -euo pipefail
R="$(cd "$(dirname "$0")" && pwd)"; cd "$R"
clonar(){ # destino url commit
  if [ -d "$1/.git" ]; then echo "ya existe: $1"; return; fi
  mkdir -p "$(dirname "$1")"; git clone "$2" "$1"; git -C "$1" checkout "$3"
}
S=https://github.com/SocialTech-Challenge
clonar F0_AUDITORIA_REPOSITORIOS/SocialTech-Gazebo $S/SocialTech-Gazebo 138befa
clonar F0_AUDITORIA_REPOSITORIOS/SocialTech-NOVNC  $S/SocialTech-NOVNC  4fb87f7
clonar F0_AUDITORIA_REPOSITORIOS/SocialTech_ws     $S/SocialTech_ws     830ec8b
clonar F0_AUDITORIA_REPOSITORIOS/tracer_ros        $S/tracer_ros        774ba0f
clonar F0_AUDITORIA_REPOSITORIOS/ugv_sdk           $S/ugv_sdk           20d85ec
P=F1_INVESTIGACION_SOFTWARE/repos
clonar $P/dynamic_world_generator https://github.com/ali-pahlevani/Dynamic_World_Generator 76bdfc5
clonar $P/image2gazebo     https://github.com/salihmarangoz/image2gazebo 8f53ec2
clonar $P/linorobot2       https://github.com/linorobot/linorobot2 f6b0bd0
clonar $P/map2sdf          https://github.com/atinfinity/map2sdf fde43ff
clonar $P/rmf_traffic_editor https://github.com/open-rmf/rmf_traffic_editor 9cb2a6b
clonar $P/scenery_builder  https://github.com/secorolab/scenery_builder b0e7abe
clonar $P/sdf2map          https://github.com/atinfinity/sdf2map 66feb61
# ws de F1 (enlaces a los repos)
mkdir -p F1_INVESTIGACION_SOFTWARE/ws/src
ln -sfn ../../repos/linorobot2/linorobot2_gazebo F1_INVESTIGACION_SOFTWARE/ws/src/linorobot2_gazebo
ln -sfn ../../repos/map2sdf F1_INVESTIGACION_SOFTWARE/ws/src/map2sdf
ln -sfn ../../repos/sdf2map F1_INVESTIGACION_SOFTWARE/ws/src/sdf2map
# venv de Python (ezdxf, opencv...)
python3 -m venv F1_INVESTIGACION_SOFTWARE/herramientas/venv
F1_INVESTIGACION_SOFTWARE/herramientas/venv/bin/pip install -r requirements_f1.txt
# LibreDWG 0.14 (DWG->DXF), verifica firma GPG
F1_INVESTIGACION_SOFTWARE/scripts/compilar_libredwg.sh
# mallas del TRACER (enlaces a tracer_ros; no redistribuibles)
M=F5_INTEGRACION_TRACER/modelos/tracer_agv/meshes
for f in castor castor_joint tracer_base_link_no_wheel tracer_wheel; do
  ln -sfn ../../../../F0_AUDITORIA_REPOSITORIOS/tracer_ros/tracer_description/meshes/$f.dae $M/$f.dae
done
# ws de F1: compilar map2sdf/sdf2map
( source /opt/ros/jazzy/setup.bash && cd F1_INVESTIGACION_SOFTWARE/ws && colcon build )
echo "Entorno restaurado. Demo: F5_INTEGRACION_TRACER/scripts/demo.sh"

#!/usr/bin/env bash
# F5: genera desde urdf/tracer_agv.urdf.xacro (1) el URDF para robot_state_publisher/RViz2 (mallas por file://) y (2) el SDF del modelo de Gazebo (mallas por model://).
set -e
source /opt/ros/jazzy/setup.bash
D="$(cd "$(dirname "$0")/.." && pwd)"; M="$D/modelos/tracer_agv"
ENC="$(python3 -c 'import sys,urllib.parse;print(urllib.parse.quote(sys.argv[1]))' "$M/meshes")"
xacro "$D/urdf/tracer_agv.urdf.xacro" mesh_prefix:="model://tracer_agv/meshes" -o "$M/tracer_agv_gz.urdf" "$@"
xacro "$D/urdf/tracer_agv.urdf.xacro" mesh_prefix:="file://$ENC" gz_extras:=false -o "$D/urdf/tracer_agv_rviz.urdf" "$@"
gz sdf -p "$M/tracer_agv_gz.urdf" > "$M/model.sdf"
cat > "$M/model.config" <<CFG
<?xml version="1.0"?>
<model><name>tracer_agv</name><version>1.0</version><sdf version="1.9">model.sdf</sdf>
<description>AgileX TRACER AGV (original) para Gazebo Harmonic. Generado por scripts/generar_robot.sh</description></model>
CFG
gz sdf -k "$M/model.sdf"

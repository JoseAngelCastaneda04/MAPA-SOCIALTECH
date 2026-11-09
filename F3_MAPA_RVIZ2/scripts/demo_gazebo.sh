#!/usr/bin/env bash
# F3: abre el mundo definitivo de F2 (0,01 m/celda) en Gazebo Harmonic, SIN modificar F2 (solo lo lee), y pone la cámara cenital (norte arriba).
source /opt/ros/jazzy/setup.bash
F2="$(cd "$(dirname "$0")/../../F2_PLANO_SIMPLE_GAZEBO" && pwd)"
export GZ_SIM_RESOURCE_PATH="$F2/mundo/modelos" SDF_PATH="$F2/mundo/modelos"
gz sim -r "$F2/mundo/piso_designscad_1cm.sdf" &
GP=$!; trap 'kill $GP 2>/dev/null' INT TERM
for i in $(seq 1 30); do sleep 1; gz service -s /gui/move_to/pose --reqtype gz.msgs.GUICamera --reptype gz.msgs.Boolean --timeout 1000 \
  --req 'pose: {position: {x: 11.0, y: -5.4, z: 15.0}, orientation: {x: -0.5, y: 0.5, z: 0.5, w: 0.5}}' 2>/dev/null | grep -q true && break; done
wait $GP

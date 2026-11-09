#!/usr/bin/env bash
# F4: abre el mundo amueblado (mundo/piso_amueblado.sdf) en Gazebo Harmonic y pone la camara cenital (norte arriba). Solo LEE F2 (modelo del piso).
source /opt/ros/jazzy/setup.bash
D="$(cd "$(dirname "$0")/.." && pwd)"; F2M="$D/../F2_PLANO_SIMPLE_GAZEBO/mundo/modelos"
export GZ_SIM_RESOURCE_PATH="$D/modelos:$F2M" SDF_PATH="$D/modelos:$F2M"
gz sim -r "$D/mundo/${1:-piso_amueblado}.sdf" &
GP=$!; trap 'kill $GP 2>/dev/null' INT TERM
for i in $(seq 1 30); do sleep 1; gz service -s /gui/move_to/pose --reqtype gz.msgs.GUICamera --reptype gz.msgs.Boolean --timeout 1000 \
  --req 'pose: {position: {x: 11.0, y: -5.4, z: 15.0}, orientation: {x: -0.5, y: 0.5, z: 0.5, w: 0.5}}' 2>/dev/null | grep -q true && break; done
wait $GP

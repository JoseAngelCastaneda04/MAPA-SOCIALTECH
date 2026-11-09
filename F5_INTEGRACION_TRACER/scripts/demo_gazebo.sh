#!/usr/bin/env bash
# F5: abre el mundo amueblado + TRACER en Gazebo Harmonic (GUI) con camara cenital. Solo LEE F2/F4 (modelos).
source /opt/ros/jazzy/setup.bash
D="$(cd "$(dirname "$0")/.." && pwd)"
export GZ_SIM_RESOURCE_PATH="$D/modelos:$D/../F4_ESCENARIO_CON_MOBILIARIO/modelos:$D/../F2_PLANO_SIMPLE_GAZEBO/mundo/modelos" SDF_PATH="$GZ_SIM_RESOURCE_PATH"
gz sim -r "$D/mundo/${1:-piso_amueblado_tracer}.sdf" &
GP=$!; trap 'kill $GP 2>/dev/null' INT TERM
for i in $(seq 1 30); do sleep 1; gz service -s /gui/move_to/pose --reqtype gz.msgs.GUICamera --reptype gz.msgs.Boolean --timeout 1000 \
  --req 'pose: {position: {x: 11.0, y: -5.4, z: 15.0}, orientation: {x: -0.5, y: 0.5, z: 0.5, w: 0.5}}' 2>/dev/null | grep -q true && break; done
wait $GP

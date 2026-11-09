#!/usr/bin/env bash
# F5: arranca Gazebo (servidor sin GUI, mundo con verdad de terreno) + lado ROS 2 sin RViz + puente de verdad. Se cierra con parar_demo.sh. Para auditorias/medidas.
source /opt/ros/jazzy/setup.bash; D="$(cd "$(dirname "$0")/.." && pwd)"; mkdir -p /tmp/f5_demo
if [ -f /tmp/f5_demo/gazebo.pid ] && kill -0 "$(cat /tmp/f5_demo/gazebo.pid)" 2>/dev/null; then echo "ERROR: ya en marcha"; exit 2; fi
"$D/scripts/generar_mundo.py" --gt > /dev/null
export GZ_SIM_RESOURCE_PATH="$D/modelos:$D/../F4_ESCENARIO_CON_MOBILIARIO/modelos:$D/../F2_PLANO_SIMPLE_GAZEBO/mundo/modelos" SDF_PATH="$GZ_SIM_RESOURCE_PATH"
setsid gz sim -s -r "$D/mundo/piso_amueblado_tracer_gt.sdf" > /tmp/f5_demo/gazebo.log 2>&1 < /dev/null & echo $! > /tmp/f5_demo/gazebo.pid
setsid ros2 launch "$D/launch/tracer_piso.launch.py" rviz:=false > /tmp/f5_demo/ros.log 2>&1 < /dev/null & echo $! > /tmp/f5_demo/ros.pid
setsid "$D/scripts/puente_verdad.sh" > /tmp/f5_demo/gt.log 2>&1 < /dev/null & echo $! > /tmp/f5_demo/gt.pid
sleep "${1:-10}"; echo arrancado

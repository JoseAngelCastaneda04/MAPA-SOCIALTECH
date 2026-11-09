#!/usr/bin/env bash
# F5: capturas SIN tocar el escritorio del usuario. Gazebo GUI y RViz2 se abren cada uno en su propio servidor X anidado (Xephyr :6 / :5) y se captura SOLO ese display.
# Uso: captura_aislada.sh abrir | gazebo <png> | rviz <png> | cerrar     (requiere scripts/arrancar_sin_gui.sh en marcha)
source /opt/ros/jazzy/setup.bash; D="$(cd "$(dirname "$0")/.." && pwd)"; mkdir -p /tmp/f5_demo
export GZ_SIM_RESOURCE_PATH="$D/modelos:$D/../F4_ESCENARIO_CON_MOBILIARIO/modelos:$D/../F2_PLANO_SIMPLE_GAZEBO/mundo/modelos" SDF_PATH="$GZ_SIM_RESOURCE_PATH"
case "$1" in
abrir)
  setsid Xephyr :6 -screen 1400x900 -ac -title F5_Xephyr_gazebo > /tmp/f5_demo/xeph6.log 2>&1 < /dev/null & echo $! > /tmp/f5_demo/xeph6.pid
  setsid Xephyr :5 -screen 1500x950 -ac -title F5_Xephyr_rviz > /tmp/f5_demo/xeph5.log 2>&1 < /dev/null & echo $! > /tmp/f5_demo/xeph5.pid; sleep 2
  DISPLAY=:6 setsid gz sim -g > /tmp/f5_demo/gui6.log 2>&1 < /dev/null & echo $! > /tmp/f5_demo/gui6.pid
  DISPLAY=:5 setsid rviz2 -d "$D/rviz/tracer_piso.rviz" --ros-args -p use_sim_time:=true > /tmp/f5_demo/rviz5.log 2>&1 < /dev/null & echo $! > /tmp/f5_demo/rviz5.pid
  sleep 12
  for i in $(seq 1 20); do DISPLAY=:6 gz service -s /gui/move_to/pose --reqtype gz.msgs.GUICamera --reptype gz.msgs.Boolean --timeout 1000 --req 'pose: {position: {x: 11.0, y: -5.4, z: 15.0}, orientation: {x: -0.5, y: 0.5, z: 0.5, w: 0.5}}' 2>/dev/null | grep -q true && break; sleep 1; done; echo abierto;;
gazebo) ffmpeg -loglevel error -y -f x11grab -video_size 1400x900 -i :6 -frames:v 1 "$2" && echo "ok $2";;
rviz)   ffmpeg -loglevel error -y -f x11grab -video_size 1500x950 -i :5 -frames:v 1 "$2" && echo "ok $2";;
cerrar) for n in gui6 rviz5 xeph6 xeph5; do f=/tmp/f5_demo/$n.pid; [ -f $f ] && { kill -INT -- -$(cat $f) 2>/dev/null; }; done; sleep 3; for n in gui6 rviz5 xeph6 xeph5; do f=/tmp/f5_demo/$n.pid; [ -f $f ] && { kill -TERM -- -$(cat $f) 2>/dev/null; rm -f $f; }; done; echo cerrado;;
esac

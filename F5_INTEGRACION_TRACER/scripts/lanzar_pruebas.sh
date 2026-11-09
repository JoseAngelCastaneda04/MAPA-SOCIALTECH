#!/usr/bin/env bash
# F5: arranca un servidor Gazebo SIN GUI + bridge + verdad de terreno y ejecuta las pruebas. Uso: lanzar_pruebas.sh <mundo> <salida.json> [A B C D E]
source /opt/ros/jazzy/setup.bash
D="$(cd "$(dirname "$0")/.." && pwd)"; M="$1"; O="$2"; shift 2; mkdir -p /tmp/f5; SCRIPT="${SCRIPT:-prueba_movimiento.py}"; MUNDO="${MUNDO:-$M}"
export GZ_SIM_RESOURCE_PATH="$D/modelos:$D/../F4_ESCENARIO_CON_MOBILIARIO/modelos:$D/../F2_PLANO_SIMPLE_GAZEBO/mundo/modelos" SDF_PATH="$GZ_SIM_RESOURCE_PATH"
if timeout 3 gz topic -l 2>/dev/null | grep -q '^/clock$'; then echo "ERROR: ya hay una simulacion Gazebo activa; cierrala antes (evita pruebas mezcladas)"; exit 2; fi
setsid gz sim -s -r "$D/mundo/$M.sdf" > /tmp/f5/p_srv.log 2>&1 & echo $! > /tmp/f5/p_srv.pid
setsid ros2 run ros_gz_bridge parameter_bridge --ros-args -p config_file:="$D/config/bridge.yaml" -p use_sim_time:=true > /tmp/f5/p_br.log 2>&1 & echo $! > /tmp/f5/p_br.pid
setsid "$D/scripts/watchdog_cmd_vel.py" --ros-args -p use_sim_time:=true > /tmp/f5/p_wd.log 2>&1 & echo $! > /tmp/f5/p_wd.pid
setsid "$D/scripts/puente_verdad.sh" > /tmp/f5/p_gt.log 2>&1 & echo $! > /tmp/f5/p_gt.pid
sleep 8
python3 "$D/scripts/$SCRIPT" "$MUNDO" "$O" "$@"; R=$?
for n in wd gt br srv; do kill -INT -- -$(cat /tmp/f5/p_$n.pid) 2>/dev/null; done; sleep 2; for n in wd gt br srv; do kill -TERM -- -$(cat /tmp/f5/p_$n.pid) 2>/dev/null; done
exit $R

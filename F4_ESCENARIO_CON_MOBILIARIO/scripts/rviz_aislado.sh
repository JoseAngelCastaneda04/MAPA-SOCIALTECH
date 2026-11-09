#!/usr/bin/env bash
# F4: arranca (o cierra con 'parar') un RViz2 en un display X anidado (Xephyr :5) para capturas/mediciones SIN tocar el escritorio del usuario.
# Requiere el map_server de la demo (scripts/demo.sh) ya activo.  Uso: rviz_aislado.sh [config_rviz=piso_amueblado_zoom] | parar
source /opt/ros/jazzy/setup.bash; D="$(cd "$(dirname "$0")/.." && pwd)"; mkdir -p /tmp/f4_demo
if [ "${1:-}" = "parar" ]; then for n in rviz_xeph xephyr; do f=/tmp/f4_demo/$n.pid; [ -f "$f" ] && { kill -TERM -- -"$(cat $f)" 2>/dev/null; rm -f "$f"; }; done; echo "aislado cerrado"; exit 0; fi
setsid Xephyr :5 -screen 1700x1100 -ac -title "F4_Xephyr_aislado" > /tmp/f4_demo/xephyr.log 2>&1 & echo $! > /tmp/f4_demo/xephyr.pid; sleep 2
DISPLAY=:5 setsid rviz2 -d "$D/config/${1:-piso_amueblado_zoom}.rviz" > /tmp/f4_demo/rviz_xeph.log 2>&1 & echo $! > /tmp/f4_demo/rviz_xeph.pid
echo "RViz2 aislado en Xephyr :5 (espera ~8 s)"

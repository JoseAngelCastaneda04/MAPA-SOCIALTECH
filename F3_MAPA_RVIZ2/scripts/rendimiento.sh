#!/usr/bin/env bash
# F3: rendimiento del servidor de mapas y de RViz2 para un mapa. Uso: rendimiento.sh <mapa.yaml> <segundos_muestreo> <salida.txt>
# Mide: tiempo de configure (carga del PGM) y activate, RSS del servidor, CPU/RSS de rviz2, estabilidad (muestras), 20 ciclos de lifecycle.
source /opt/ros/jazzy/setup.bash
D="$(cd "$(dirname "$0")/.." && pwd)"; Y="$1"; T="$2"; O="$3"; exec > "$O" 2>&1
ms() { echo $(( ($(date +%s%N) - $1) / 1000000 )); }
echo "== mapa: $Y  muestreo: ${T}s  $(date -Is)"
ros2 run nav2_map_server map_server --ros-args -p yaml_filename:="$Y" & SP=$!; sleep 3
SRV=$(pgrep -f "lib/nav2_map_server/map_server" | head -1); echo "RSS servidor sin cargar: $(awk '/VmRSS/{print $2}' /proc/$SRV/status) kB"
t=$(date +%s%N); ros2 lifecycle set /map_server configure >/dev/null; echo "configure (carga PGM+YAML): $(ms $t) ms (incluye ~0,5 s de arranque de la CLI ros2)"
echo "RSS tras configure: $(awk '/VmRSS/{print $2}' /proc/$SRV/status) kB"
t=$(date +%s%N); ros2 lifecycle set /map_server activate >/dev/null; echo "activate: $(ms $t) ms"
echo "estado: $(ros2 lifecycle get /map_server)"
python3 "$D/scripts/volcar_mapa_topic.py" /tmp/_m.npz | sed 's/^/suscriptor tardío (transient_local): /'
(setsid rviz2 -d "$D/config/piso_1cm.rviz" > /tmp/_rviz_perf.log 2>&1 &); sleep 10; RV=$(pgrep -x rviz2)
echo "RSS rviz2 a los 10 s: $(awk '/VmRSS/{print $2}' /proc/$RV/status) kB"
echo "muestras (t_s, CPU_rviz_%, CPU_srv_%, RSS_rviz_kB, RSS_srv_kB):"
for i in $(seq 1 $((T/5))); do sleep 5; echo "$((i*5)) $(ps -o %cpu= -p $RV) $(ps -o %cpu= -p $SRV) $(awk '/VmRSS/{print $2}' /proc/$RV/status) $(awk '/VmRSS/{print $2}' /proc/$SRV/status)"; done
"$D/scripts/captura_ventana.sh" "$RV" "${O%.txt}_rviz.png"
echo "errores/avisos de rviz2 (excluye el de GLSL, ya documentado):"; grep -E "ERROR|WARN" /tmp/_rviz_perf.log | grep -v -E "glsl120|indexed_8bit" || echo "  ninguno"
echo "GLSL: $(grep -c glsl120 /tmp/_rviz_perf.log) mención(es)"
kill $RV; sleep 1
echo "-- 20 ciclos deactivate/cleanup/configure/activate"
t=$(date +%s%N); for i in $(seq 1 20); do for tr in deactivate cleanup configure activate; do ros2 lifecycle set /map_server $tr >/dev/null || echo "FALLO ciclo $i $tr"; done; done
echo "20 ciclos en $(ms $t) ms; estado final: $(ros2 lifecycle get /map_server); RSS final: $(awk '/VmRSS/{print $2}' /proc/$SRV/status) kB"
python3 "$D/scripts/volcar_mapa_topic.py" /tmp/_m.npz | sed 's/^/tras ciclos: /'
kill $SP; sleep 1; pkill -f "lib/nav2_map_server/map_server"
echo "fin $(date -Is)"

#!/usr/bin/env bash
# F4 (copia de F2): captura SOLO la región de la ventana de Gazebo de ESTA sesión (PID dado), tras comprobar que tiene el foco.
# Nunca usa scrot -u. Uso: captura_ventana.sh <pid_gz_gui> <salida.png>
PID="$1"; OUT="$2"
WID=$(for w in $(xdotool search --name "Gazebo Sim"); do [ "$(xdotool getwindowpid $w)" = "$PID" ] && echo $w; done | head -1)
[ -z "$WID" ] && { echo "ventana no encontrada para PID $PID"; exit 1; }
xdotool windowactivate --sync "$WID"; sleep 1
ACT=$(xdotool getactivewindow); [ "$ACT" = "$WID" ] || { echo "ABORTO: la ventana activa ($ACT) no es la de Gazebo ($WID)"; exit 2; }
# Posición/tamaño reales con xwininfo (xdotool da un desplazamiento por la decoración de la ventana)
X=$(xwininfo -id "$WID" | awk '/Absolute upper-left X/{print $4}'); Y=$(xwininfo -id "$WID" | awk '/Absolute upper-left Y/{print $4}')
WIDTH=$(xwininfo -id "$WID" | awk '/Width:/{print $2}'); HEIGHT=$(xwininfo -id "$WID" | awk '/Height:/{print $2}')
/usr/bin/ffmpeg -loglevel error -y -f x11grab -video_size ${WIDTH}x${HEIGHT} -i ${DISPLAY}+${X},${Y} -frames:v 1 "$OUT" && echo "ok $OUT (${WIDTH}x${HEIGHT}+${X}+${Y}, ventana $WID)"

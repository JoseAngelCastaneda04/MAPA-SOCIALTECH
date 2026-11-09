#!/usr/bin/env bash
# F4 (copia de F3): captura SOLO la ventana de RViz2 de ESTA sesión (PID dado), tras comprobar foco. Nunca scrot -u.
# Uso: captura_ventana.sh <pid_rviz> <salida.png>
PID="$1"; OUT="$2"
WID=$(for w in $(xdotool search --name " - RViz"); do [ "$(xdotool getwindowpid $w)" = "$PID" ] && echo $w; done | head -1)
[ -z "$WID" ] && { echo "ventana no encontrada para PID $PID"; exit 1; }
xdotool windowactivate --sync "$WID"; sleep 1
[ "$(xdotool getactivewindow)" = "$WID" ] || { echo "ABORTO: ventana activa distinta"; exit 2; }
I=$(xwininfo -id "$WID")
X=$(echo "$I" | awk '/Absolute upper-left X/{print $4}'); Y=$(echo "$I" | awk '/Absolute upper-left Y/{print $4}')
W=$(echo "$I" | awk '/Width:/{print $2}'); H=$(echo "$I" | awk '/Height:/{print $2}')
/usr/bin/ffmpeg -loglevel error -y -f x11grab -video_size ${W}x${H} -i ${DISPLAY}+${X},${Y} -frames:v 1 "$OUT" && echo "ok $OUT (${W}x${H}+${X}+${Y}, ventana $WID)"

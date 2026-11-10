#!/usr/bin/env bash
# F5.2: demostracion de percepcion + localizacion: Gazebo (mundo con verdad de terreno) + puente + AMCL + monitor de precision + RViz2.
# Uso: scripts/demo_f52.sh            Pose inicial de AMCL desplazada de PRUEBA:  F52_ERR_X=0.3 F52_ERR_Y=-0.2 F52_ERR_YAW_DEG=10 scripts/demo_f52.sh
# Cierra con Ctrl+C o scripts/parar_f52.sh (por grupos de proceso, sin pkill). Solo LEE F0-F5.
source /opt/ros/jazzy/setup.bash
D="$(cd "$(dirname "$0")/.." && pwd)"; F5="$D/../F5_INTEGRACION_TRACER"; T=/tmp/f52_demo; mkdir -p "$T" "$D/logs"
if [ -f $T/gazebo.pid ] && kill -0 "$(cat $T/gazebo.pid)" 2>/dev/null; then echo "ERROR: ya esta en marcha (scripts/parar_f52.sh)"; exit 2; fi
# NO se ejecuta generar_mundo.py de F5 (reescribiria archivos de F5): se usa el mundo *_gt.sdf ya generado.
setsid "$F5/scripts/demo_gazebo.sh" piso_amueblado_tracer_gt > $T/gazebo.log 2>&1 & echo $! > $T/gazebo.pid
setsid ros2 launch "$D/launch/f52_percepcion.launch.py" rviz:="${RVIZ:-true}" > $T/ros.log 2>&1 & echo $! > $T/ros.pid
setsid "$D/scripts/monitor_precision.py" --csv "${CSV:-$D/logs/ultima_sesion.csv}" > $T/monitor.log 2>&1 & echo $! > $T/monitor.pid
trap '"$D/scripts/parar_f52.sh"; exit 0' INT TERM
cat <<MSG
F5.2 en marcha. Conducir desde OTRA terminal:  $F5/scripts/teleop.sh   (i , j l; k parar; mantén la tecla: sin ordenes 0,5 s = parada)
RViz2: verde = REAL (Gazebo), amarillo = SOLO odometria, cian = AMCL; magenta = LiDAR; rojo = zonas prohibidas (visuales). Error en texto sobre el robot.
Si AMCL arranca mal: herramienta '2D Pose Estimate' de RViz2.  Registro CSV: ${CSV:-$D/logs/ultima_sesion.csv}
MSG
wait

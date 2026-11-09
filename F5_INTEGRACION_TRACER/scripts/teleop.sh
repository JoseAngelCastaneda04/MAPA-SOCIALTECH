#!/usr/bin/env bash
# F5: teleoperacion por teclado (teleop_twist_keyboard) con velocidades prudentes (0,2 m/s y 0,5 rad/s: rango donde el error medido es <1 %). Teclas: i/, avanzar/retroceder, j/l girar, k parar.
# La orden pasa por el watchdog: si dejas de pulsar mas de 0,5 s el robot se para solo (mantén la tecla pulsada para avanzar).
source /opt/ros/jazzy/setup.bash
exec ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args -p speed:=0.2 -p turn:=0.5 -p use_sim_time:=true

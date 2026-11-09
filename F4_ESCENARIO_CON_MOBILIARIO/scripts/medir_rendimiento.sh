#!/usr/bin/env bash
# F4: muestrea RAM (RSS) y CPU de los procesos de Gazebo (servidor, GUI) durante N segundos y lee el factor de tiempo real del topic stats.
# Uso: medir_rendimiento.sh <mundo> [segundos=30]  (con el mundo YA abierto por scripts/demo*.sh o gz sim)
source /opt/ros/jazzy/setup.bash
W="$1"; N="${2:-30}"
for i in $(seq 1 $N); do ps -eo rss,pcpu,args | grep -E "gz sim (server|gui)" | grep -v grep | awk '{n=($3=="gz"&&$5=="server")?"server":"gui"; print n, $1, $2}'; sleep 1; done | awk '{r[$1]+=$2; c[$1]+=$3; k[$1]++; if($2>m[$1])m[$1]=$2} END{for(n in r) printf "%s: RAM media %.0f MB (max %.0f MB), CPU media %.1f %%\n", n, r[n]/k[n]/1024, m[n]/1024, c[n]/k[n]}'
timeout 10 gz topic -e -n 3 -t /world/$W/stats | grep -E "real_time_factor|iterations" | tail -2

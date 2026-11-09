#!/usr/bin/env bash
# F4: cierra SOLO lo lanzado por demo.sh (grupos de proceso guardados en /tmp/f4_demo/*.pid). No usa pkill por nombre.
for n in rviz gazebo; do f=/tmp/f4_demo/$n.pid; [ -f "$f" ] && { p=$(cat "$f"); kill -INT -- -"$p" 2>/dev/null; }; done
sleep 4
for n in rviz gazebo; do f=/tmp/f4_demo/$n.pid; [ -f "$f" ] && { p=$(cat "$f"); kill -TERM -- -"$p" 2>/dev/null; rm -f "$f"; }; done
echo "demo cerrada"

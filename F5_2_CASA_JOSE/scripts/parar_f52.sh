#!/usr/bin/env bash
# F5.2: cierra SOLO lo lanzado por demo_f52.sh (grupos de proceso; sin pkill por nombre).
T=/tmp/f52_demo
for n in monitor ros gazebo; do f=$T/$n.pid; [ -f "$f" ] && kill -INT -- -"$(cat $f)" 2>/dev/null; done
sleep 4
for n in monitor ros gazebo; do f=$T/$n.pid; [ -f "$f" ] && { kill -TERM -- -"$(cat $f)" 2>/dev/null; rm -f "$f"; }; done
echo "F5.2 cerrada"

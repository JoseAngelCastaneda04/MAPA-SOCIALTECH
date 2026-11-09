#!/usr/bin/env bash
# F5: RAM/CPU del SERVIDOR Gazebo solo (sin ROS) para un mundo, tras 12 s y durante 15 s. Uso: medir_servidor.sh <ruta_mundo.sdf> <etiqueta>
source /opt/ros/jazzy/setup.bash; D="$(cd "$(dirname "$0")/.." && pwd)"
export GZ_SIM_RESOURCE_PATH="$D/modelos:$D/../F4_ESCENARIO_CON_MOBILIARIO/modelos:$D/../F2_PLANO_SIMPLE_GAZEBO/mundo/modelos" SDF_PATH="$GZ_SIM_RESOURCE_PATH"
T0=$(date +%s.%N); setsid gz sim -s -r "$1" > /tmp/f5/srv_$2.log 2>&1 < /dev/null & G=$!
until gz topic -l 2>/dev/null | grep -q "^/clock$"; do sleep 0.2; done; T1=$(date +%s.%N)
sleep 12
python3 - "$G" "$2" "$T0" "$T1" <<'PY'
import psutil, sys, time, os
g=int(sys.argv[1]); ps=[p for p in psutil.process_iter() if p.pid==g or (lambda q: q==g)(os.getpgid(p.pid))]
[p.cpu_percent(None) for p in ps]; time.sleep(15)
print(sys.argv[2], 'carga_s=%.2f'%(float(sys.argv[4])-float(sys.argv[3])), 'RAM_MB=%d'%sum(p.memory_info().rss for p in ps if p.is_running())/1e6 if False else '', end=' ')
print('RAM_MB=%d CPU_pct=%.0f'%(sum(p.memory_info().rss for p in ps)/1e6, sum(p.cpu_percent(None) for p in ps)))
PY
kill -INT -- -$G 2>/dev/null; sleep 3; kill -TERM -- -$G 2>/dev/null

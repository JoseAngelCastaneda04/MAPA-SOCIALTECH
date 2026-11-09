#!/usr/bin/env python3
"""F5: CPU y RAM de los procesos del proyecto (por grupos de procesos de /tmp/f5_demo/*.pid) + RTF de Gazebo, en reposo y con el robot moviendose. Uso: medir_rendimiento.py <salida.json> [segundos_por_fase=20]"""
import sys, os, time, json, subprocess, psutil, re
dur = float(sys.argv[2]) if len(sys.argv) > 2 else 20.0
def grupo(pidfile):
    try: pg = int(open(pidfile).read())
    except Exception: return []
    r = []
    for p in psutil.process_iter(['pid', 'name']):
        try:
            if os.getpgid(p.pid) == pg or p.pid == pg: r.append(p)
        except Exception: pass
    return r
def sesion():   # todos los procesos de los grupos de la demo, etiquetados
    g = {}
    for n in ('gazebo', 'ros', 'gt', 'gui6', 'rviz5', 'xeph6', 'xeph5'):
        for p in grupo('/tmp/f5_demo/%s.pid' % n): g[p.pid] = (n, p)
    return g
def rtf():
    o = subprocess.run(['gz', 'topic', '-e', '-t', '/world/piso_amueblado/stats', '-n', '2'], capture_output=True, text=True, timeout=10).stdout
    m = re.findall(r'real_time_factor: ([\d.e-]+)', o); return float(m[-1]) if m else None
def fase(nombre, mover):
    g = sesion(); [p.cpu_percent(None) for _, p in g.values()]; t0 = time.time(); ram = {}
    if mover:
        pub = subprocess.Popen(['ros2', 'topic', 'pub', '-r', '10', '/cmd_vel', 'geometry_msgs/msg/Twist', '{linear: {x: 0.0}, angular: {z: 0.5}}'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
    time.sleep(dur)
    cpu = {}; 
    for pid, (n, p) in g.items():
        try:
            nm = p.name(); cpu[nm] = cpu.get(nm, 0) + p.cpu_percent(None); ram[nm] = ram.get(nm, 0) + p.memory_info().rss/1e6
        except Exception: pass
    r = rtf()
    if mover: os.killpg(pub.pid, 15)
    return dict(fase=nombre, cpu_pct_por_proceso={k: round(v, 1) for k, v in cpu.items()}, ram_MB_por_proceso={k: round(v) for k, v in ram.items()}, rtf=r, cpu_total_pct=round(sum(cpu.values()), 1), ram_total_MB=round(sum(ram.values())))
out = [fase('reposo', False), fase('robot girando (cmd_vel 10 Hz)', True)]
json.dump(out, open(sys.argv[1], 'w'), indent=1); print(json.dumps(out, indent=1))

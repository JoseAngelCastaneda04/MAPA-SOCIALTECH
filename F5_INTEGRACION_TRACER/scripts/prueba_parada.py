#!/usr/bin/env python3
"""F5: pruebas A-E de PARADA AUTOMATICA (watchdog de /cmd_vel). Requiere el sistema en marcha (arrancar_sin_gui.sh: mundo _gt + watchdog + puente de verdad). Uso: prueba_parada.py <salida.json> [A B1 B2 C D E]
Mide en TIEMPO DE SIMULACION: t_ultima_orden (ultimo /cmd_vel recibido), t_watchdog (primer cero en /cmd_vel_seguro = lo que ve el DiffDrive), t_parada (|v| real < 0,01 m/s sostenido 0,3 s), desplazamiento real desde la ultima orden."""
import sys, os, json, math, time, pty, signal, subprocess, rclpy
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from prueba_movimiento import T, yaw, wrap
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MUNDO = 'piso_amueblado'; INICIO = (12.0, -6.325, 0.0)     # carril libre de 3,6 m hacia +X (puerta dorm.3)

class P(T):
    def __init__(s):
        super().__init__(); s.rx = []; s.seg = []; s.vgt = []; s.od = []
        s.create_subscription(Twist, '/cmd_vel', lambda m: s.rx.append((s.now(), m.linear.x, m.angular.z)), 50)
        s.create_subscription(Twist, '/cmd_vel_seguro', lambda m: s.seg.append((s.now(), m.linear.x, m.angular.z)), 200)
    def cb_gt(s, m):
        super().cb_gt(m); t = m.header.stamp.sec+m.header.stamp.nanosec*1e-9; v = m.twist.twist.linear
        s.vgt.append((t, math.hypot(v.x, v.y), m.pose.pose.position.x, m.pose.pose.position.y))
    def limpiar(s): s.rx.clear(); s.seg.clear(); s.vgt.clear()
    def esperar(s, seg): s.spin_until(s.now()+seg)    # no publica nada

def analizar(n, nombre, cmd, t_fin_esp):
    rx = n.rx; t_last = rx[-1][0] if rx else None
    out = dict(prueba=nombre, comando=cmd, n_ordenes_recibidas=len(rx), t_ultima_orden_s=t_last)
    if t_last is None: out['resultado'] = 'SIN ORDENES'; return out
    seg_post = [x for x in n.seg if x[0] > t_last]; cero = next((x for x in seg_post if x[1] == 0.0 and x[2] == 0.0), None)
    v_ult = next((x for x in reversed(n.vgt) if x[0] <= t_last), n.vgt[-1]); out['vel_real_en_ultima_orden_m_s'] = v_ult[1]
    out['t_watchdog_cero_s'] = (cero[0]-t_last) if cero else None
    # parada: primer instante tras t_last en que |v|<0,01 y se mantiene 0,3 s
    t_stop = None
    for i, (t, v, x, y) in enumerate(n.vgt):
        if t >= t_last and v < 0.01 and all(w[1] < 0.01 for w in n.vgt[i:] if w[0] <= t+0.3): t_stop = t; break
    out['t_hasta_parada_s'] = (t_stop-t_last) if t_stop else None
    p0 = (v_ult[2], v_ult[3]); p1 = (n.vgt[-1][2], n.vgt[-1][3]); ps = next(((x, y) for (t, v, x, y) in n.vgt if t_stop and t >= t_stop), p1)
    out['desplazamiento_desde_ultima_orden_hasta_parada_m'] = math.hypot(ps[0]-p0[0], ps[1]-p0[1]); out['desplazamiento_posterior_a_la_parada_m'] = math.hypot(p1[0]-ps[0], p1[1]-ps[1])
    out['vel_real_final_m_s'] = n.vgt[-1][1]; out['ultima_orden_en_seguro'] = list(seg_post[-1][1:]) if seg_post else None
    out['watchdog_publicando_hasta_el_final'] = bool(n.seg and n.seg[-1][0] > n.now()-0.2)
    out['resultado'] = 'PARA AUTOMATICAMENTE' if (out['t_hasta_parada_s'] is not None and out['t_hasta_parada_s'] < 1.0 and out['vel_real_final_m_s'] < 0.01 and out['desplazamiento_posterior_a_la_parada_m'] < 0.001) else 'FALLO'
    return out

def teleop_pty(n, tecla=b'i', seg=2.0, hz=20, como='kill9'):
    pid, fd = pty.fork()
    if pid == 0:
        os.execvp('ros2', ['ros2', 'run', 'teleop_twist_keyboard', 'teleop_twist_keyboard', '--ros-args', '-p', 'speed:=0.3', '-p', 'turn:=0.5', '-p', 'use_sim_time:=true'])
    os.set_blocking(fd, False); t0 = time.time()
    while time.time()-t0 < 4.0:
        try: os.read(fd, 65536)
        except Exception: pass
        n.spin_until(n.now()+0.05) if False else rclpy.spin_once(n, timeout_sec=0.05)
    n.limpiar(); ts = n.now(); nxt = 0
    while n.now()-ts < seg:
        rclpy.spin_once(n, timeout_sec=0.01)
        if n.now() >= nxt:
            try: os.write(fd, tecla); os.read(fd, 65536)
            except Exception: pass
            nxt = n.now()+1.0/hz
    if como == 'kill9': os.killpg(os.getpgid(pid), signal.SIGKILL)
    else: os.write(fd, b'\x03')       # Ctrl+C en el terminal del teleop (SIGINT al grupo en primer plano)
    time.sleep(0.2)
    try: os.waitpid(pid, os.WNOHANG)
    except Exception: pass
    return pid

if __name__ == '__main__':
    salida = sys.argv[1]; sel = sys.argv[2:] or ['A', 'B1', 'B2', 'C', 'E', 'D']; rclpy.init(); n = P(); n.esperar_datos(); out = {}
    def preparar(): n.reponer(MUNDO, *[INICIO[0], INICIO[1], math.radians(INICIO[2])]); n.esperar(2.0); n.limpiar()
    for k in sel:
        if k == 'A':
            preparar(); teleop_pty(n, como='kill9'); n.esperar(3.0); out['A'] = analizar(n, 'A: teleop_twist_keyboard real, tecla i 2 s a 20 Hz, proceso muerto con SIGKILL sin pulsar k', 'v=0,3 m/s (tecla i)', 0)
        elif k == 'B1':
            preparar(); teleop_pty(n, como='ctrlc'); n.esperar(3.0); out['B1'] = analizar(n, 'B1: teleop_twist_keyboard real + Ctrl+C durante el movimiento (sin k)', 'v=0,3 m/s (tecla i)', 0)
        elif k == 'B2':
            preparar(); p = subprocess.Popen(['ros2', 'topic', 'pub', '-r', '10', '/cmd_vel', 'geometry_msgs/msg/Twist', '{linear: {x: 0.3}}'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
            n.esperar(4.0); n.limpiar(); n.esperar(2.0); os.killpg(p.pid, signal.SIGINT); p.wait(timeout=10); n.esperar(3.0)
            out['B2'] = analizar(n, 'B2: ros2 topic pub -r 10 + Ctrl+C (SIGINT) durante el movimiento', 'v=0,3 m/s a 10 Hz', 0)
        elif k == 'C':
            preparar(); ts = n.now(); nxt = 0
            while n.now()-ts < 2.0:
                rclpy.spin_once(n, timeout_sec=0.01)
                if n.now() >= nxt: m = Twist(); m.linear.x = 0.3; n.pub.publish(m); nxt = n.now()+0.1
            n.esperar(3.0); out['C'] = analizar(n, 'C: v=0,3 m/s 10 Hz durante 2 s y se deja de publicar (silencio, sin cero)', 'v=0,3 m/s', 0)
        elif k == 'E':
            preparar(); n.esperar(1.0)     # el watchdog ya esta en estado 'caducada'
            r = n.mover(0.3, 0.0, 4.0, reposo=2.0); g0, g1 = r['gt0'], r['gt1']; fwd = math.hypot(g1[1]-g0[1], g1[2]-g0[2])
            out['E'] = dict(prueba='E: orden valida tras una caducidad: v=0,3 m/s 4 s', recorrido_real_m=fwd, esperado_m=0.3*r['dur_real'], diferencia_mm=(fwd-0.3*r['dur_real'])*1e3,
                            referencia_sin_watchdog_mm=-8.4, vel_odom_final=r['od1'][4], resultado='REANUDA' if fwd > 1.0 else 'NO REANUDA')
        elif k == 'D':
            x, y, th = 12.5, -6.3, 180.0; n.reponer(MUNDO, x, y, math.radians(th)); n.esperar(2.0); n.limpiar(); ts = n.now(); nxt = 0
            while n.now()-ts < 8.0:                      # 0,3 m/s hacia la caja: contacto a ~5,8 s; seguimos ordenando 2 s MAS contra ella
                rclpy.spin_once(n, timeout_sec=0.01)
                if n.now() >= nxt: m = Twist(); m.linear.x = 0.3; n.pub.publish(m); nxt = n.now()+0.1
            bloqueado = n.vgt[-1][1] < 0.01; pb = (n.vgt[-1][2], n.vgt[-1][3])
            n.esperar(2.5)                               # silencio: watchdog caduca; el robot sigue empujando? no: debe estar parado
            pa = (n.vgt[-1][2], n.vgt[-1][3])
            subprocess.run(['gz', 'service', '-s', f'/world/{MUNDO}/remove', '--reqtype', 'gz.msgs.Entity', '--reptype', 'gz.msgs.Boolean', '--timeout', '3000', '--req', 'name: "caja_1" type: MODEL'], capture_output=True)
            t_rm = n.now(); n.esperar(5.0); pf = (n.vgt[-1][2], n.vgt[-1][3])
            tras = [v for (t, v, x_, y_) in n.vgt if t > t_rm]
            out['D'] = analizar(n, 'D: bloqueado 2 s contra caja_1, se deja de publicar, se RETIRA la caja (gz remove) y se espera 5 s', 'v=0,3 m/s hacia la caja', 0)
            out['D'].update(bloqueado_antes_de_dejar_de_publicar=bool(bloqueado), velocidad_max_tras_retirar_caja_m_s=max(tras) if tras else None,
                            desplazamiento_tras_retirar_caja_m=math.hypot(pf[0]-pa[0], pf[1]-pa[1]), caja_retirada=True, resultado='NO REANUDA' if math.hypot(pf[0]-pa[0], pf[1]-pa[1]) < 0.001 else 'REANUDA (FALLO)')
        if k in out:
            print(k, json.dumps(out[k], default=float), flush=True)
    json.dump(out, open(salida, 'w'), indent=1, default=float); n.destroy_node(); rclpy.shutdown()

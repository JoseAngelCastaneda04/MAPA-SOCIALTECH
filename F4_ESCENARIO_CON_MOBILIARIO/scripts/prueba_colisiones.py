#!/usr/bin/env python3
"""F4: prueba fisica controlada (sin robot). Anade bolas DINAMICAS (r=0.05 m) al mundo amueblado, las suelta desde z=1.2 m sobre cada objeto
y mide en que altura quedan; ademas lanza una bola lateralmente contra la silla_E y otra contra la pared.
Resultado esperado: z_final = altura_superficie + 0.05 (hay colision); sin colision la bola caeria al suelo (z=0.05).
Uso: prueba_colisiones.py [--malla] [--segundos 6]   -> evidencias/logs/prueba_colisiones[_malla].json   Cierra SOLO el gz sim que lanza."""
import argparse, json, os, re, signal, subprocess, sys, time, yaml
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def bola(n, x, y, z, vx=0.0, vy=0.0):
    # solo las bolas laterales llevan VelocityControl (impone la velocidad en cada paso, anula la caida); las de caida son libres
    plg = f'<plugin filename="gz-sim-velocity-control-system" name="gz::sim::systems::VelocityControl"><initial_linear>{vx} {vy} 0</initial_linear></plugin>' if (vx or vy) else ""
    return f'''    <model name="{n}"><pose>{x} {y} {z} 0 0 0</pose>
      {plg}
      <link name="l"><inertial><mass>0.2</mass><inertia><ixx>0.0002</ixx><iyy>0.0002</iyy><izz>0.0002</izz></inertia></inertial>
      <collision name="c"><geometry><sphere><radius>0.05</radius></sphere></geometry><surface><friction><ode><mu>0</mu><mu2>0</mu2></ode></friction></surface></collision>
      <visual name="v"><geometry><sphere><radius>0.05</radius></sphere></geometry><material><ambient>1 0 0 1</ambient><diffuse>1 0 0 1</diffuse></material></visual></link></model>
'''
if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--malla", action="store_true"); ap.add_argument("--segundos", type=float, default=6); a = ap.parse_args()
    sfx = "_malla" if a.malla else ""; mundo = f"piso_amueblado{sfx}"
    cfg = yaml.safe_load(open(os.path.join(D, "config", "mobiliario.yaml"))); O = {o["id"]: o for o in cfg["objetos"]}
    # (nombre bola, x, y, z_ini, vx, esperado_z, descripcion)
    sx, sy = O["silla_N"]["x"], O["silla_N"]["y"] - 0.0385       # centro del asiento (yaw 0)
    T = [("b_mesa1", O["mesa_1"]["x"], O["mesa_1"]["y"], 1.2, 0, 0.7962 + 0.05, "tablero mesa_1 (h=0.7962)"),
         ("b_mesa2", O["mesa_2"]["x"], O["mesa_2"]["y"], 1.2, 0, 0.7395 + 0.05, "tablero mesa_2 (h=0.7395)"),
         ("b_caja", O["caja_1"]["x"], O["caja_1"]["y"], 1.2, 0, 0.50 + 0.05, "caja (h=0.50)"),
         ("b_papelera", O["papelera_1"]["x"], O["papelera_1"]["y"], 1.2, 0, 0.60 + 0.05, "papelera (h=0.60)"),
         ("b_asiento", sx, sy, 1.2, 0, None, "asiento silla_N (altura segun colision)"),
         ("b_suelo", 9.6, -3.4, 1.2, 0, 0.05, "control: suelo libre (z=0.05)")]
    mw = open(os.path.join(D, "mundo", mundo + ".sdf")).read()
    extra = "".join(bola(n, x, y, z) for n, x, y, z, vx, e, d in T)
    extra += bola("l_caja", 10.9, O["caja_1"]["y"], 0.05, vx=-2.0)      # contra la caja (cara este en x=10.40)
    extra += bola("l_pared", 8.0, -6.6, 0.05, vx=0.0, vy=-2.0)            # contra la pared sur (y~-6.86)
    tmp = os.path.join(D, "mundo", f"_prueba_colisiones{sfx}.sdf"); open(tmp, "w").write(mw.replace("</world>", extra + "  </world>"))
    env = dict(os.environ); F2M = os.path.join(D, "..", "F2_PLANO_SIMPLE_GAZEBO", "mundo", "modelos")
    env["GZ_SIM_RESOURCE_PATH"] = env["SDF_PATH"] = os.path.join(D, "modelos") + ":" + F2M
    p = subprocess.Popen(["gz", "sim", "-s", "-r", "-v", "1", tmp], env=env, start_new_session=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        t0 = time.time()
        while time.time() - t0 < 60:               # esperar a que el TIEMPO DE SIMULACION (no el reloj) llegue a N s
            st = subprocess.run(["gz", "topic", "-e", "-n", "1", "-t", "/world/piso_amueblado/stats"], capture_output=True, text=True, env=env, timeout=20).stdout
            m = re.search(r"sim_time \{\s*sec: (\d+)", st)
            if m and int(m.group(1)) >= a.segundos: break
            time.sleep(0.5)
        t = subprocess.run(["gz", "topic", "-e", "-n", "1", "-t", f"/world/piso_amueblado/dynamic_pose/info"], capture_output=True, text=True, env=env, timeout=20).stdout
    finally:
        os.killpg(p.pid, signal.SIGINT); time.sleep(2)
        try: os.killpg(p.pid, signal.SIGTERM)
        except ProcessLookupError: pass
        os.remove(tmp)
    pos = {}
    for blk in re.findall(r"pose \{(.*?)\n\}", t, re.S):
        n = re.search(r'name: "([^"]+)"', blk).group(1)
        if n in ("l",): continue
        g = lambda k: float(re.search(rf"\b{k}: ([-\d.e]+)", re.search(r"position \{(.*?)\}", blk, re.S).group(1)).group(1)) if re.search(rf"\b{k}: ", re.search(r"position \{(.*?)\}", blk, re.S).group(1)) else 0.0
        pos.setdefault(n, (g("x"), g("y"), g("z")))
    res = []
    for n, x, y, z, vx, e, d in T:
        f = pos.get(n); ok = None if (f is None or e is None) else abs(f[2] - e) < 0.01
        res.append({"bola": n, "prueba": d, "xy_ini": [x, y], "z_final": None if f is None else round(f[2], 4), "z_esperado": e, "ok": ok})
    for n, d, cond in (("l_caja", "bola a -2 m/s contra la caja (para en la cara: x_final = 10.45 +-0.02)", lambda f: abs(f[0] - 10.45) < 0.02),
                       ("l_pared", "bola lanzada a -2 m/s contra pared sur (no debe atravesar: y_final > -6.90)", lambda f: f[1] > -6.90)):
        f = pos.get(n); res.append({"bola": n, "prueba": d, "final_xyz": None if f is None else [round(v, 3) for v in f], "ok": None if f is None else bool(cond(f))})
    s = json.dumps(res, indent=1, ensure_ascii=False); print(s); open(os.path.join(D, "evidencias", "logs", f"prueba_colisiones{sfx}.json"), "w").write(s)

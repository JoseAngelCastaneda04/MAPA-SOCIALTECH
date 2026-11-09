#!/usr/bin/env python3
"""F4 prueba de automatizacion: mueve UNA silla en config/mobiliario.yaml, regenera mundo+mapa y comprueba (en metros):
 1 posicion inicial, 2 nueva posicion en zona libre, 3 mundo Gazebo regenerado (se carga headless y se lee pose/info),
 4 la silla aparece en el mapa nuevo, 5 su ocupacion desaparece de la posicion antigua, 6 paredes sin cambios, 7 puertas abiertas,
 y que NO cambia ninguna otra celda. Al final RESTAURA el YAML original (guarda copia en evidencias/logs).
Uso: prueba_mover_silla.py [--id silla_W] [--x 9.9] [--y -3.3] [--yaw 135]"""
import argparse, json, os, re, shutil, signal, subprocess, sys, time, yaml, cv2, numpy as np
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.join(D, "scripts"))
from combinar_mapas import cargar
from comprobar_mapa import referencia, Rejilla, run_libre
CFG = os.path.join(D, "config", "mobiliario.yaml")
def regen(): return subprocess.run([os.path.join(D, "scripts", "regenerar.sh")], capture_output=True, text=True)
def mapa(): return cargar(os.path.join(D, "mapa", "piso_amueblado.yaml"))
if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--id", default="silla_W"); ap.add_argument("--x", type=float, default=9.9); ap.add_argument("--y", type=float, default=-3.3); ap.add_argument("--yaw", type=float, default=135)
    a = ap.parse_args(); orig_txt = open(CFG).read(); shutil.copy(CFG, os.path.join(D, "evidencias", "logs", "mobiliario_antes_prueba.yaml"))
    cfg = yaml.safe_load(orig_txt); dims = json.load(open(os.path.join(D, "modelos", "dimensiones.json"))); res = {}
    try:
        r = regen(); assert r.returncode == 0, r.stderr[-500:]
        y0, im0, occ0 = mapa(); by, _, bocc = cargar(os.path.join(D, cfg["mapa_base"])); rej = Rejilla(y0, occ0.shape)
        o0 = next(o for o in cfg["objetos"] if o["id"] == a.id); zmin, zmax = cfg["slice_z"]
        ref0 = referencia(o0, dims, rej, zmin, zmax)
        res["1_posicion_inicial"] = {k: o0[k] for k in ("x", "y", "yaw_deg")}
        res["2_posicion_nueva"] = {"x": a.x, "y": a.y, "yaw_deg": a.yaw}
        o1 = dict(o0, x=a.x, y=a.y, yaw_deg=a.yaw); ref1 = referencia(o1, dims, rej, zmin, zmax)
        res["2_zona_libre"] = {"solapa_pared_base": bool((ref1 & bocc).any()), "solapa_otro_objeto": any((ref1 & referencia(o, dims, rej, zmin, zmax)).any() for o in cfg["objetos"] if o["id"] != a.id),
                               "distancia_min_a_pared_m": round(float((cv2.distanceTransform((~bocc).astype(np.uint8), cv2.DIST_L2, 5) * rej.res)[ref1].min()), 3)}
        # editar SOLO esa entrada del YAML (texto, conservando comentarios)
        nuevo = re.sub(rf"(- \{{id: {a.id},.*?x: )[-\d.]+(,\s*y: )[-\d.]+(,\s*z: [-\d.]+,\s*yaw_deg: )[-\d.]+", rf"\g<1>{a.x}\g<2>{a.y}\g<3>{a.yaw}", orig_txt)
        assert nuevo != orig_txt, "no se pudo editar el YAML"; open(CFG, "w").write(nuevo)
        r = regen(); assert r.returncode == 0, r.stderr[-500:]
        y1, im1, occ1 = mapa()
        # 3) mundo regenerado cargado en Gazebo (headless)
        env = dict(os.environ); F2M = os.path.join(D, "..", "F2_PLANO_SIMPLE_GAZEBO", "mundo", "modelos"); env["GZ_SIM_RESOURCE_PATH"] = env["SDF_PATH"] = os.path.join(D, "modelos") + ":" + F2M
        p = subprocess.Popen(["gz", "sim", "-s", "-r", "-v", "1", os.path.join(D, "mundo", "piso_amueblado.sdf")], env=env, start_new_session=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        try:
            time.sleep(6); t = subprocess.run(["gz", "topic", "-e", "-n", "1", "-t", "/world/piso_amueblado/pose/info"], capture_output=True, text=True, env=env, timeout=20).stdout
        finally:
            os.killpg(p.pid, signal.SIGINT); time.sleep(2)
            try: os.killpg(p.pid, signal.SIGTERM)
            except ProcessLookupError: pass
        blk = [b for b in re.findall(r"pose \{(.*?)\n\}", t, re.S) if f'name: "{a.id}"' in b][0]
        gx = float(re.search(r"x: ([-\d.e]+)", blk).group(1)); gy = float(re.search(r"y: ([-\d.e]+)", blk).group(1))
        qz = float((re.search(r"z: ([-\d.e]+)", blk[blk.index("orientation"):]) or [0, 0])[1]); qw = float(re.search(r"w: ([-\d.e]+)", blk[blk.index("orientation"):]).group(1))
        gyaw = np.degrees(2 * np.arctan2(qz, qw))
        res["3_gazebo_pose"] = {"x": gx, "y": gy, "yaw_deg": round(float(gyaw), 3), "error_xy_m": round(float(np.hypot(gx - a.x, gy - a.y)), 5), "error_yaw_deg": round(float(abs((gyaw - a.yaw + 180) % 360 - 180)), 3)}
        # 4-5) mapa
        ocupa_nueva = (occ1 & ref1).sum() / ref1.sum()                                   # fraccion de la huella nueva ocupada en el mapa nuevo
        ref0_libre = ref0 & ~ref1                                                         # huella antigua que no se solapa con la nueva
        otros = np.zeros_like(occ1)
        for o in cfg["objetos"]:
            if o["id"] != a.id: otros |= cv2.dilate(referencia(o, dims, rej, zmin, zmax).astype(np.uint8), np.ones((5, 5), np.uint8)).astype(bool)
        interior_viejo = cv2.erode(ref0_libre.astype(np.uint8), np.ones((5, 5), np.uint8)).astype(bool) & ~otros                # nucleo de la huella antigua, sin vecinos
        res["4_silla_en_mapa_nuevo"] = {"fraccion_huella_nueva_ocupada": round(float(ocupa_nueva), 4), "fraccion_huella_nueva_ocupada_en_mapa_antiguo": round(float((occ0 & ref1).sum() / ref1.sum()), 4)}
        res["5_ocupacion_antigua_desaparece"] = {"celdas_nucleo_antiguo": int(interior_viejo.sum()), "ocupadas_en_mapa_antiguo": int((occ0 & interior_viejo).sum()), "ocupadas_en_mapa_nuevo": int((occ1 & interior_viejo).sum())}
        # 6) paredes, resto
        dif = occ0 ^ occ1; permitido = cv2.dilate((ref0 | ref1).astype(np.uint8), np.ones((9, 9), np.uint8)).astype(bool)   # +-4 cm alrededor de huella antigua y nueva
        res["6_paredes"] = {"celdas_pared_base_liberadas_antes": int((bocc & ~occ0).sum()), "celdas_pared_base_liberadas_despues": int((bocc & ~occ1).sum()),
                            "celdas_cambiadas_total": int(dif.sum()), "celdas_cambiadas_fuera_de_las_dos_huellas": int((dif & ~permitido).sum()), "celdas_cambiadas_sobre_pared_base": int((dif & bocc).sum())}
        pu = json.load(open(os.path.join(D, "..", "F2_PLANO_SIMPLE_GAZEBO", "evidencias", "cotas_verificadas.json")))[6:]
        res["7_puertas_m"] = [{"puerta": q["nombre"], "antes": run_libre(occ0, rej.res, rej.ox, rej.oy, rej.h, q["punto"], q["eje"]), "despues": run_libre(occ1, rej.res, rej.ox, rej.oy, rej.h, q["punto"], q["eje"])} for q in pu]
        res["APROBADO"] = bool(res["2_gazebo_ok"] if False else (res["3_gazebo_pose"]["error_xy_m"] < 1e-3 and res["3_gazebo_pose"]["error_yaw_deg"] < 0.1 and ocupa_nueva > 0.95
                          and res["5_ocupacion_antigua_desaparece"]["ocupadas_en_mapa_nuevo"] == 0 and res["5_ocupacion_antigua_desaparece"]["ocupadas_en_mapa_antiguo"] > 0
                          and res["6_paredes"]["celdas_cambiadas_fuera_de_las_dos_huellas"] == 0 and res["6_paredes"]["celdas_pared_base_liberadas_despues"] == 0
                          and all(q["antes"] == q["despues"] and q["despues"] > 0.8 for q in res["7_puertas_m"]) and not res["2_zona_libre"]["solapa_pared_base"] and not res["2_zona_libre"]["solapa_otro_objeto"]))
        shutil.copy(os.path.join(D, "mapa", "piso_amueblado.pgm"), os.path.join(D, "evidencias", "logs", "mapa_tras_mover_silla.pgm"))
    finally:
        open(CFG, "w").write(orig_txt); r = regen()                                          # restaurar y regenerar
        res["restaurado"] = (r.returncode == 0)
    s = json.dumps(res, indent=1, ensure_ascii=False); print(s); open(os.path.join(D, "evidencias", "logs", "prueba_mover_silla.json"), "w").write(s)

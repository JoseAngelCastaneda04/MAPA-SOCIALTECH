#!/usr/bin/env python3
"""F4: config/mobiliario.yaml -> mundo/piso_amueblado.sdf (apartamento de F2 + <include> de cada objeto con su pose)
y mundo/solo_mobiliario.sdf (solo los objetos, para que sdf2map produzca la capa de mobiliario).
No toca el modelo del piso ni el mundo de F2.   Uso: generar_mundo.py [--config ...] [--malla]   (--malla: sillas con colision de malla original)"""
import argparse, math, os, yaml
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAB = '''<?xml version="1.0"?>
<!-- GENERADO por scripts/generar_mundo.py desde config/mobiliario.yaml. No editar a mano: editar el YAML y regenerar. -->
<sdf version="1.9">
  <world name="{nombre}">
    <physics name="1ms" type="ignored"><max_step_size>0.001</max_step_size><real_time_factor>1.0</real_time_factor></physics>
    <plugin filename="gz-sim-physics-system" name="gz::sim::systems::Physics"/>
    <plugin filename="gz-sim-scene-broadcaster-system" name="gz::sim::systems::SceneBroadcaster"/>
    <plugin filename="gz-sim-user-commands-system" name="gz::sim::systems::UserCommands"/>
    <light type="directional" name="sun"><pose>0 0 10 0 0 0</pose><direction>-0.5 0.1 -0.9</direction><diffuse>1 1 1 1</diffuse></light>
'''
SUELO = '''    <model name="suelo"><static>true</static><pose>11.5 -5.4 0 0 0 0</pose><link name="l">
      <collision name="c"><geometry><plane><normal>0 0 1</normal><size>26 22</size></plane></geometry></collision>
      <visual name="v"><geometry><plane><normal>0 0 1</normal><size>26 22</size></plane></geometry>
        <material><ambient>0.55 0.55 0.58 1</ambient><diffuse>0.55 0.55 0.58 1</diffuse></material></visual></link></model>
    <include><name>piso</name><uri>model://piso_designscad_1cm</uri></include>
'''
def inc(o, malla):
    m = o["modelo"]
    if malla and m == "silla": m = "silla_malla"
    return (f'    <include><name>{o["id"]}</name><uri>model://{m}</uri>'
            f'<pose>{o["x"]} {o["y"]} {o.get("z",0)} 0 0 {math.radians(o.get("yaw_deg",0)):.6f}</pose></include>\n')
if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--config", default=os.path.join(D, "config", "mobiliario.yaml"))
    ap.add_argument("--malla", action="store_true"); ap.add_argument("--salida", default=os.path.join(D, "mundo"))
    a = ap.parse_args(); cfg = yaml.safe_load(open(a.config)); os.makedirs(a.salida, exist_ok=True)
    ids = [o["id"] for o in cfg["objetos"]]; assert len(ids) == len(set(ids)), "ids repetidos"
    for o in cfg["objetos"]: assert os.path.isdir(os.path.join(D, "modelos", o["modelo"])), f"modelo desconocido: {o['modelo']}"
    sfx = "_malla" if a.malla else ""
    with open(os.path.join(a.salida, f"piso_amueblado{sfx}.sdf"), "w") as f:
        f.write(CAB.format(nombre="piso_amueblado") + SUELO + "".join(inc(o, a.malla) for o in cfg["objetos"]) + "  </world>\n</sdf>\n")
    with open(os.path.join(a.salida, f"solo_mobiliario{sfx}.sdf"), "w") as f:
        f.write(CAB.format(nombre="solo_mobiliario") + "".join(inc(o, a.malla) for o in cfg["objetos"]) + "  </world>\n</sdf>\n")
    print(f"{len(ids)} objetos -> {a.salida}/piso_amueblado{sfx}.sdf")

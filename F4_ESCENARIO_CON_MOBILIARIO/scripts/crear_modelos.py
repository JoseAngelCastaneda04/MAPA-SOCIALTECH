#!/usr/bin/env python3
"""F4: crea modelos/ a partir de los modelos ORIGINALES de SocialTech 2025 (F0/SocialTech-Gazebo/models, que NO se tocan).
Cada modelo nuevo es una COPIA con dos cambios documentados:
  1) el origen pasa al CENTRO de la huella (el original de mesa1/mesa2 lo tiene en una ESQUINA) y z=0 = suelo;
  2) un unico giro Rx(90 grados) (Y-arriba del OBJ -> Z-arriba), sin el giro duplicado del <model><pose> original (que <include><pose> ignora).
Dimensiones: se MIDEN de la malla (no se inventan) y se guardan en modelos/dimensiones.json.
Colision: tabla/silla: 'malla' (como 2025) o 'simple' (cajas/cilindro; la silla original tiene 155 001 triangulos).
Uso: crear_modelos.py"""
import json, os, shutil, sys
import numpy as np
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ORIG = os.path.join(D, "..", "F0_AUDITORIA_REPOSITORIOS", "SocialTech-Gazebo", "models")
OUT = os.path.join(D, "modelos")

def bbox_obj(p):
    v = np.array([[float(x) for x in l.split()[1:4]] for l in open(p) if l.startswith("v ")])
    w = np.c_[v[:, 0], -v[:, 2], v[:, 1]]          # Rx(90): (x,y,z)->(x,-z,y)
    return w.min(0), w.max(0)

def tri(p):
    return sum(len(l.split()) - 3 for l in open(p) if l.startswith("f "))

def mesh_model(nombre, orig, malla, colision, cajas=None):
    mn, mx = bbox_obj(os.path.join(ORIG, orig, "meshes", malla))
    c = (mn + mx) / 2.0
    t = (-c[0], -c[1], -mn[2])                    # centro de la huella al origen, base en z=0
    dst = os.path.join(OUT, nombre)
    if os.path.isdir(dst): shutil.rmtree(dst)
    shutil.copytree(os.path.join(ORIG, orig, "meshes"), os.path.join(dst, "meshes"))
    pose = f"{t[0]:.5f} {t[1]:.5f} {t[2]:.5f} 1.570796 0 0"
    uri = f"meshes/{malla}"
    if colision == "malla":
        col = f'<collision name="col"><pose>{pose}</pose><geometry><mesh><uri>{uri}</uri></mesh></geometry></collision>'
    else:
        col = "\n      ".join(cajas)
    sdf = f'''<?xml version="1.0"?>
<!-- F4: copia de SocialTech-Gazebo/models/{orig} (original sin modificar). Origen = centro de la huella, z=0 = suelo.
     Dimensiones medidas de la malla: {(mx-mn)[0]:.4f} x {(mx-mn)[1]:.4f} x {(mx-mn)[2]:.4f} m (X x Y x Z a yaw 0). Colision: {colision}. -->
<sdf version="1.9">
  <model name="{nombre}">
    <static>true</static>
    <link name="link">
      <visual name="vis"><pose>{pose}</pose><geometry><mesh><uri>{uri}</uri></mesh></geometry></visual>
      {col}
    </link>
  </model>
</sdf>
'''
    open(os.path.join(dst, "model.sdf"), "w").write(sdf)
    open(os.path.join(dst, "model.config"), "w").write(f'<?xml version="1.0"?>\n<model><name>{nombre}</name><version>1.0</version><sdf version="1.9">model.sdf</sdf><description>F4: copia de SocialTech 2025 {orig} (origen centrado)</description></model>\n')
    return {"origen": f"SocialTech-Gazebo/models/{orig}/meshes/{malla}", "triangulos": tri(os.path.join(ORIG, orig, "meshes", malla)),
            "dimensiones_xyz_m": [round(float(x), 4) for x in (mx - mn)], "huella_original_min_xy": [round(float(mn[0]), 4), round(float(mn[1]), 4)],
            "desplazamiento_aplicado_xyz": [round(float(x), 5) for x in t], "colision": colision}

def primitivo(nombre, geom_vis, geom_col, alto, rgb, desc):
    dst = os.path.join(OUT, nombre); os.makedirs(dst, exist_ok=True)
    sdf = f'''<?xml version="1.0"?>
<!-- F4: obstaculo sencillo de prueba (propio de F4, no existe en SocialTech 2025). {desc} Origen = centro de la base, z=0 = suelo. -->
<sdf version="1.9"><model name="{nombre}"><static>true</static><link name="link"><pose>0 0 {alto/2}  0 0 0</pose>
  <visual name="vis"><geometry>{geom_vis}</geometry><material><ambient>{rgb} 1</ambient><diffuse>{rgb} 1</diffuse></material></visual>
  <collision name="col"><geometry>{geom_col}</geometry></collision></link></model></sdf>
'''
    open(os.path.join(dst, "model.sdf"), "w").write(sdf)
    open(os.path.join(dst, "model.config"), "w").write(f'<?xml version="1.0"?>\n<model><name>{nombre}</name><version>1.0</version><sdf version="1.9">model.sdf</sdf><description>F4 obstaculo de prueba</description></model>\n')

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    dims = {}
    dims["mesa1"] = mesh_model("mesa1", "table1", "mesa1.obj", "malla")
    dims["mesa2"] = mesh_model("mesa2", "table2", "mesa2.obj", "malla")
    dims["silla_malla"] = mesh_model("silla_malla", "chair", "silla.obj", "malla")
    # silla con colision simple: asiento y respaldo MEDIDOS de la malla (franjas de altura, ver DETALLE F4):
    #   asiento z 0.35-0.43, x +-0.223, y -0.258..0.181 ; respaldo z 0.43-0.84, x +-0.194, y 0.168..0.265.
    #   La base de ruedas es una ESTIMACION (cilindro r=0.25, h=0.04): la malla solo tiene una huella plana (z<0.009) y triangulos largos sueltos; no hay datos de altura de la base.
    sillacajas = [
        '<collision name="base_estimada"><pose>0 0 0.02 0 0 0</pose><geometry><cylinder><radius>0.25</radius><length>0.04</length></cylinder></geometry></collision>',
        '<collision name="asiento"><pose>0 -0.0385 0.39 0 0 0</pose><geometry><box><size>0.446 0.439 0.08</size></box></geometry></collision>',
        '<collision name="respaldo"><pose>0 0.2165 0.635 0 0 0</pose><geometry><box><size>0.388 0.097 0.41</size></box></geometry></collision>']
    dims["silla"] = mesh_model("silla", "chair", "silla.obj", "simple", sillacajas)
    primitivo("caja", "<box><size>0.40 0.40 0.50</size></box>", "<box><size>0.40 0.40 0.50</size></box>", 0.50, "0.8 0.35 0.1", "Caja 0.40 x 0.40 x 0.50 m.")
    primitivo("papelera", "<cylinder><radius>0.20</radius><length>0.60</length></cylinder>", "<cylinder><radius>0.20</radius><length>0.60</length></cylinder>", 0.60, "0.2 0.5 0.3", "Cilindro r=0.20 m, h=0.60 m.")
    dims["caja"] = {"origen": "propio de F4", "dimensiones_xyz_m": [0.4, 0.4, 0.5]}
    dims["papelera"] = {"origen": "propio de F4", "dimensiones_xyz_m": [0.4, 0.4, 0.6]}
    json.dump(dims, open(os.path.join(OUT, "dimensiones.json"), "w"), indent=1, ensure_ascii=False)
    print(json.dumps(dims, indent=1, ensure_ascii=False))

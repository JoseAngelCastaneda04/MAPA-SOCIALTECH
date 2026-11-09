#!/usr/bin/env python3
"""F4: comprobaciones INDEPENDIENTES del mapa actualizado (no usan sdf2map para la referencia):
 A) paredes: toda celda ocupada de la base sigue ocupada; lo nuevo coincide con la capa de mobiliario.
 B) 6 puertas: hueco libre medido a lo largo del eje, en base y en mapa actualizado (de F2/cotas_verificadas.json).
 C) holgura mueble-pared: distancia minima de cada objeto a las paredes (distance transform).
 D) huella: referencia dibujada desde las MALLAS originales (mesas, proyeccion de triangulos) o las primitivas de colision/analiticas
    (silla simple, caja, papelera), colocada con la pose del YAML, frente a la capa -> IoU y error de bbox por objeto.
Uso: comprobar_mapa.py [--mapa mapa/piso_amueblado] [--config config/mobiliario.yaml] [--json salida.json]"""
import argparse, json, math, os, sys, yaml, cv2, numpy as np
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(D, "scripts"))
from combinar_mapas import cargar

def rot(yaw): c, s = math.cos(yaw), math.sin(yaw); return np.array([[c, -s], [s, c]])

def run_libre(occ, res, ox, oy, h, punto, eje):
    """Hueco libre (m) que contiene 'punto' a lo largo de 'eje' (x|y); 0 si el punto esta ocupado."""
    col = int((punto[0] - ox) / res); row = h - 1 - int((punto[1] - oy) / res)
    if occ[row, col]: return 0.0
    line = occ[row, :] if eje == "x" else occ[:, col]; i = col if eje == "x" else row
    a = i
    while a > 0 and not line[a - 1]: a -= 1
    b = i
    while b < len(line) - 1 and not line[b + 1]: b += 1
    return (b - a + 1) * res

class Rejilla:
    def __init__(s, y, shape): s.res = y["resolution"]; s.ox, s.oy = y["origin"][:2]; s.h, s.w = shape
    def px(s, xy):  # (N,2) metros -> (N,2) pixeles (col,row), float
        xy = np.asarray(xy, float); return np.c_[(xy[:, 0] - s.ox) / s.res, s.h - (xy[:, 1] - s.oy) / s.res]

def tri_obj(path, dz):
    v = []; f = []
    for l in open(path):
        if l.startswith("v "): v.append([float(x) for x in l.split()[1:4]])
        elif l.startswith("f "):
            ii = [int(t.split("/")[0]) - 1 for t in l.split()[1:]]
            for k in range(1, len(ii) - 1): f.append((ii[0], ii[k], ii[k + 1]))
    v = np.array(v); w = np.c_[v[:, 0], -v[:, 2], v[:, 1]] + np.array(dz)   # Rx90 + desplazamiento del modelo F4
    return w, np.array(f)

def referencia(obj, dims, rej, zmin, zmax):
    """Mascara bool de la huella esperada del objeto (en la rejilla base)."""
    m = np.zeros((rej.h, rej.w), np.uint8); yaw = math.radians(obj.get("yaw_deg", 0)); R = rot(yaw); p0 = np.array([obj["x"], obj["y"]])
    def poly(pts, val=1): cv2.fillPoly(m, [np.round(rej.px(pts)).astype(np.int32)], val)
    def rect(c, sx, sy): return np.array([[-sx/2, -sy/2], [sx/2, -sy/2], [sx/2, sy/2], [-sx/2, sy/2]]) + np.array(c)
    mod = obj["modelo"]
    if mod in ("mesa1", "mesa2"):
        d = dims[mod]; orig = {"mesa1": "table1/meshes/mesa1.obj", "mesa2": "table2/meshes/mesa2.obj"}[mod]
        w, f = tri_obj(os.path.join(D, "..", "F0_AUDITORIA_REPOSITORIOS", "SocialTech-Gazebo", "models", orig), d["desplazamiento_aplicado_xyz"])
        for t in f:
            z = w[t, 2]
            if z.max() >= zmin and z.min() <= zmax: poly((w[t, :2] @ R.T) + p0)
    elif mod == "silla":
        poly((rect((0, -0.0385), 0.446, 0.439) @ R.T) + p0); poly((rect((0, 0.2165), 0.388, 0.097) @ R.T) + p0)   # asiento y respaldo (la base queda bajo la banda z)
    elif mod == "caja": poly((rect((0, 0), 0.4, 0.4) @ R.T) + p0)
    elif mod == "papelera":
        ang = np.linspace(0, 2*np.pi, 90, endpoint=False); poly(np.c_[0.2*np.cos(ang), 0.2*np.sin(ang)] + p0)
    return m.astype(bool)

def bbox(mask, rej):
    ys, xs = np.nonzero(mask)
    if len(xs) == 0: return None
    return [rej.ox + xs.min()*rej.res, rej.oy + (rej.h - 1 - ys.max())*rej.res, rej.ox + (xs.max()+1)*rej.res, rej.oy + (rej.h - ys.min())*rej.res]  # xmin,ymin,xmax,ymax (m)

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--mapa", default=os.path.join(D, "mapa", "piso_amueblado"))
    ap.add_argument("--config", default=os.path.join(D, "config", "mobiliario.yaml")); ap.add_argument("--json")
    a = ap.parse_args(); cfg = yaml.safe_load(open(a.config)); dims = json.load(open(os.path.join(D, "modelos", "dimensiones.json")))
    by, bim, bocc = cargar(os.path.normpath(os.path.join(D, cfg["mapa_base"])))
    ny, nim, nocc = cargar(a.mapa + ".yaml"); rej = Rejilla(by, bocc.shape); out = {}
    # A) paredes
    capa_al = cv2.imread(os.path.join(D, "mapa", "capa_alineada.pgm"), -1) < 128
    out["A_paredes"] = {"mismo_tamano": bocc.shape == nocc.shape, "misma_resolucion": by["resolution"] == ny["resolution"], "mismo_origen": list(by["origin"]) == list(ny["origin"]),
                        "celdas_base_liberadas": int((bocc & ~nocc).sum()), "celdas_nuevas": int((nocc & ~bocc).sum()), "nuevas_distintas_de_capa": int(((nocc & ~bocc) ^ (capa_al & ~bocc)).sum()),
                        "celdas_pared_base": int(bocc.sum())}
    # B) puertas
    pu = json.load(open(os.path.join(D, "..", "F2_PLANO_SIMPLE_GAZEBO", "evidencias", "cotas_verificadas.json")))[6:]
    out["B_puertas"] = [{"nombre": p["nombre"], "hueco_base_m": round(run_libre(bocc, rej.res, rej.ox, rej.oy, rej.h, p["punto"], p["eje"]), 3),
                         "hueco_actualizado_m": round(run_libre(nocc, rej.res, rej.ox, rej.oy, rej.h, p["punto"], p["eje"]), 3)} for p in pu]
    # C) holgura a paredes + D) huella
    dist = cv2.distanceTransform((~bocc).astype(np.uint8), cv2.DIST_L2, 5) * rej.res
    zmin, zmax = cfg["slice_z"]; objs = []
    for o in cfg["objetos"]:
        ref = referencia(o, dims, rej, zmin, zmax); win = cv2.dilate(ref.astype(np.uint8), np.ones((7, 7), np.uint8)).astype(bool)   # +-3 cm
        got = capa_al & win; inter = (ref & capa_al).sum(); uni = (ref | got).sum()
        bref, bgot = bbox(ref, rej), bbox(got, rej)
        objs.append({"id": o["id"], "modelo": o["modelo"], "x": o["x"], "y": o["y"], "yaw_deg": o.get("yaw_deg", 0),
                     "distancia_min_a_pared_m": round(float(dist[ref].min()), 3), "solapa_pared": bool((ref & bocc).any()),
                     "IoU_ref_vs_capa": round(float(inter / max(uni, 1)), 4), "bbox_ref_m": [round(x, 3) for x in bref], "bbox_capa_m": [round(x, 3) for x in bgot],
                     "error_bbox_max_m": round(float(max(abs(np.array(bref) - np.array(bgot)))), 3)})
    out["CD_objetos"] = objs
    out["D_global"] = {"celdas_capa": int(capa_al.sum())}
    s = json.dumps(out, indent=1, ensure_ascii=False); print(s)
    if a.json: open(a.json, "w").write(s)

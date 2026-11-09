#!/usr/bin/env python3
"""F3: compara numéricamente (metros, coordenadas CAD) tres representaciones del MISMO piso:
  CAD  = polígonos de muro de F2/derivados/plano_piso_muros.dxf (verdad, analítica o a 2,5 mm)
  MAPA = OccupancyGrid recibida por /map (lo que dibuja RViz2), volcada por volcar_mapa_topic.py
  GZ   = STL del modelo de Gazebo + pose de su model.sdf (lo que carga gz sim)
Solo lee F2/F1. Uso (venv de F1, -I): comparar_geometria.py <map.npz> <salida.json>"""
import sys, os, json, re, struct, importlib.util, numpy as np, cv2
sys.dont_write_bytecode = True
import ezdxf
ROOT = "/home/jose-angel/Desktop/MAPA SOCIALTECH"
F2 = f"{ROOT}/F2_PLANO_SIMPLE_GAZEBO"
DXF = f"{F2}/derivados/plano_piso_muros.dxf"; COTAS = f"{F2}/evidencias/cotas_verificadas.json"
MOD = f"{F2}/mundo/modelos/piso_designscad_1cm"
CAPAS = {"ESTRUTURA - ARQ-STA - BLOCOS_ESTRUTURAIS", "F2_LAZOS_ALVENARIA"}
spec = importlib.util.spec_from_file_location("d2m", f"{ROOT}/F1_INVESTIGACION_SOFTWARE/scripts/dxf_a_mapa.py"); d2m = importlib.util.module_from_spec(spec); spec.loader.exec_module(d2m)
out = {}
# ---------- datos
M = np.load(sys.argv[1]); grid = M["data"]; res = float(M["res"]); ox, oy = map(float, M["origin"][:2]); H, W = grid.shape
assert list(M["quat"]) == [0, 0, 0, 1], "orientación no identidad"
occ = grid[::-1] >= 65                                   # OccupancyGrid: fila 0 = y MÍNIMA (origen); se voltea para fila 0 = y máxima como el PGM
pols = [np.array(p) for p in d2m.poligonos(ezdxf.readfile(DXF).modelspace(), CAPAS)]
sdf = open(f"{MOD}/model.sdf").read(); pose = [float(v) for v in re.search(r"<pose>([^<]+)</pose>", sdf).group(1).split()]
b = open(f"{MOD}/piso_designscad_1cm_walls.stl", "rb").read(); n = struct.unpack("<I", b[80:84])[0]
T = np.frombuffer(b[84:], dtype=np.dtype([("n", "<3f4"), ("v", "<9f4"), ("a", "<u2")]), count=n)
tri = T["v"].reshape(-1, 3, 3).astype(float) + np.array(pose[:3]); nrm = T["n"].astype(float)   # triángulos en coords. de mundo (sin rotación: pose[3:]=0)
assert pose[3:] == [0, 0, 0]
# ---------- 1-5: dimensiones, escala, origen, orientación
allv = np.vstack(pols); cad_min, cad_max = allv.min(0), allv.max(0)
stl_min, stl_max = tri.reshape(-1, 3).min(0), tri.reshape(-1, 3).max(0)
rr, cc = np.where(occ); map_min = np.array([ox + cc.min() * res, oy + (H - 1 - rr.max()) * res]); map_max = np.array([ox + (cc.max() + 1) * res, oy + (H - rr.min()) * res])
f = lambda a: [round(float(x), 4) for x in a]
out["dimensiones"] = {
 "CAD_bbox_min": f(cad_min), "CAD_bbox_max": f(cad_max), "CAD_tamano": f(cad_max - cad_min),
 "STL_bbox_min_xy": f(stl_min[:2]), "STL_bbox_max_xy": f(stl_max[:2]), "STL_tamano_xy": f(stl_max[:2] - stl_min[:2]), "STL_altura": round(float(stl_max[2] - stl_min[2]), 4),
 "MAPA_ocupado_min": f(map_min), "MAPA_ocupado_max": f(map_max), "MAPA_ocupado_tamano": f(map_max - map_min),
 "MAPA_extension_total": f([W * res, H * res]), "MAPA_origen": [ox, oy], "MODELO_pose": pose,
 "margen_libre_mapa_(min x,y | max x,y)": f(np.r_[cad_min - [ox, oy], [ox + W * res, oy + H * res] - cad_max]),
 "error_MAPA-CAD_bbox_min": f(map_min - cad_min), "error_MAPA-CAD_bbox_max": f(map_max - cad_max),
 "error_STL-CAD_bbox_min": f(stl_min[:2] - cad_min), "error_STL-CAD_bbox_max": f(stl_max[:2] - cad_max),
 "error_MAPA-STL_bbox_min": f(map_min - stl_min[:2]), "error_MAPA-STL_bbox_max": f(map_max - stl_max[:2]),
 "escala_celda_m": res, "escala_STL/CAD_x": round(float((stl_max[0] - stl_min[0]) / (cad_max[0] - cad_min[0])), 5)}
# ---------- rejilla común de 2,5 mm sobre la extensión del mapa
S = 4; r2 = res / S; W2, H2 = W * S, H * S
def raster(polys, SS=4):
    """Mismo criterio que dxf_a_mapa.py de F1: se pinta a SS veces la rejilla de 2,5 mm y se promedia (ocupada si >=49 % cubierta);
    así no se infla el borde (fillPoly marca como ocupado todo píxel que toca el borde)."""
    img = np.zeros((H2 * SS, W2 * SS), np.uint8); rs = r2 / SS
    for q in polys:
        px = np.round((q[:, 0] - ox) / rs * 16).astype(np.int32); py = np.round((H2 * SS - (q[:, 1] - oy) / rs) * 16).astype(np.int32)
        cv2.fillPoly(img, [np.stack([px, py], 1)], 255, lineType=cv2.LINE_8, shift=4)
    return cv2.resize(img, (W2, H2), interpolation=cv2.INTER_AREA) / 255.0 >= 0.49
cad2 = raster(pols)
cap = [t[:, :2] for t, nz in zip(tri, nrm[:, 2]) if nz > 0.9 and abs(t[0, 2] - stl_max[2]) < 1e-6]
stl2 = raster(cap)
map2 = np.kron(occ, np.ones((S, S), bool))
iou = lambda a, b: float((a & b).sum() / (a | b).sum())
area = lambda a: float(a.sum() * r2 * r2)
out["areas_m2"] = {"CAD": round(area(cad2), 4), "MAPA": round(area(map2), 4), "STL_tapa": round(area(stl2), 4)}
out["IoU_2.5mm"] = {"MAPA_vs_CAD": round(iou(map2, cad2), 5), "STL_vs_CAD": round(iou(stl2, cad2), 5), "MAPA_vs_STL": round(iou(map2, stl2), 5)}
# orientación: el mapa solo debe coincidir con el CAD en su orientación real
tr = {"identidad (correcta)": map2, "espejo vertical (y invertida)": map2[::-1], "espejo horizontal (x invertida)": map2[:, ::-1], "giro 180°": map2[::-1, ::-1]}
out["orientacion_IoU_MAPA_vs_CAD"] = {k: round(iou(v, cad2), 4) for k, v in tr.items()}
# desviación de bordes (distancia de cada borde de A al borde más cercano de B), en m
def borde(a):
    a8 = a.astype(np.uint8); return (a8 - cv2.erode(a8, np.ones((3, 3), np.uint8))).astype(bool)
def dist_a_borde(b):  # distancia (m) de cada píxel al borde de b
    return cv2.distanceTransform((~borde(b)).astype(np.uint8), cv2.DIST_L2, 5) * r2
def desv(a, b):
    d = dist_a_borde(b)[borde(a)]; return {"media_m": round(float(d.mean()), 4), "p99_m": round(float(np.percentile(d, 99)), 4), "max_m": round(float(d.max()), 4)}
out["desviacion_bordes"] = {"MAPA→CAD": desv(map2, cad2), "CAD→MAPA": desv(cad2, map2), "STL→CAD": desv(stl2, cad2), "CAD→STL": desv(cad2, stl2), "MAPA→STL": desv(map2, stl2), "STL→MAPA": desv(stl2, map2)}
# ---------- 7: habitaciones (espacio libre con radio de erosión 0,46 m > semihueco 0,45 m: los huecos de 0,90 m quedan sellados)
def habitaciones(solid):
    dist = cv2.distanceTransform((~solid).astype(np.uint8), cv2.DIST_L2, 5) * r2
    core = (dist > 0.46).astype(np.uint8); nlab, lab, st, cen = cv2.connectedComponentsWithStats(core, connectivity=4)
    # área de la habitación = píxeles libres más cerca de cada núcleo (dilatación acotada)
    res_ = []
    for i in range(1, nlab):
        if st[i, cv2.CC_STAT_AREA] * r2 * r2 < 1.0: continue
        m = (lab == i); d = cv2.dilate(m.astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * int(0.46 / r2) + 1,) * 2)).astype(bool) & ~solid
        yy, xx = np.where(m); res_.append({"centro_xy": [round(ox + xx.mean() * r2, 3), round(oy + (H2 - yy.mean()) * r2, 3)], "area_nucleo_m2": round(float(m.sum() * r2 * r2), 3)})
    return sorted(res_, key=lambda r: (r["centro_xy"][0], r["centro_xy"][1]))
hab = {"CAD": habitaciones(cad2), "MAPA": habitaciones(map2), "STL": habitaciones(stl2)}
out["habitaciones_nucleos_libres"] = hab
dif = []
for a, bb in zip(hab["MAPA"], hab["CAD"]):
    dif.append(round(float(np.hypot(a["centro_xy"][0] - bb["centro_xy"][0], a["centro_xy"][1] - bb["centro_xy"][1])), 4))
out["habitaciones_n"] = {k: len(v) for k, v in hab.items()}
out["habitaciones_dist_centros_MAPA-CAD_m"] = dif if len(hab["MAPA"]) == len(hab["CAD"]) else "distinto número de habitaciones"
# ---------- 8: cotas y 6 puertas, medidas con cortes analíticos
def corte_intervalos_poly(q, eje, v):  # intervalos ocupados de un polígono sobre la recta eje=v (eje 'x': recta y=v)
    k = 1 if eje == "x" else 0; j = 1 - k; xs = []
    for p0, p1 in zip(q, np.roll(q, -1, 0)):
        if (p0[k] - v) * (p1[k] - v) < 0 or (p0[k] == v) != (p1[k] == v) and min(p0[k], p1[k]) < v <= max(p0[k], p1[k]):
            t = (v - p0[k]) / (p1[k] - p0[k]); xs.append(p0[j] + t * (p1[j] - p0[j]))
    xs.sort(); return [(xs[i], xs[i + 1]) for i in range(0, len(xs) - 1, 2)]
def union(iv):
    iv = sorted(iv); o = []
    for a, bq in iv:
        if o and a <= o[-1][1] + 1e-9: o[-1][1] = max(o[-1][1], bq)
        else: o.append([a, bq])
    return o
def libre(iv, p):
    iv = union(iv); lo, hi = -1e9, 1e9
    for a, bq in iv:
        if a <= p <= bq: return None
        if bq < p: lo = max(lo, bq)
        if a > p: hi = min(hi, a)
    return lo, hi
def corte_stl_z(h, eje, v):  # cruces con caras verticales a la altura h -> intervalos ocupados por paridad
    k = 1 if eje == "x" else 0; j = 1 - k; xs = []
    for t, nz in zip(tri, nrm[:, 2]):
        if abs(nz) > 1e-6 or t[:, 2].min() > h or t[:, 2].max() < h: continue
        for p0, p1 in ((t[0], t[1]), (t[1], t[2]), (t[2], t[0])):
            if (p0[2] - h) * (p1[2] - h) < 0:
                s = (h - p0[2]) / (p1[2] - p0[2]); q0 = p0 + s * (p1 - p0)
                xs.append(q0)
        # una cara vertical (rectángulo en 2 triángulos) corta el plano en un segmento
    return xs
def stl_libre_z(h, eje, v, p):  # segmentos del STL a altura h -> cruces con la recta -> intervalo libre alrededor de p
    k = 1 if eje == "x" else 0; j = 1 - k; segs = {}
    pts = []
    for t, nz in zip(tri, nrm[:, 2]):
        if abs(nz) > 1e-6: continue
        c = []
        for p0, p1 in ((t[0], t[1]), (t[1], t[2]), (t[2], t[0])):
            if (p0[2] - h) * (p1[2] - h) < 0:
                s = (h - p0[2]) / (p1[2] - p0[2]); c.append((p0 + s * (p1 - p0))[:2])
        if len(c) == 2: pts.append((c[0], c[1]))
    xs = []
    for a, bq in pts:
        if abs(a[k] - bq[k]) < 1e-9: continue                      # segmento paralelo a la recta
        if min(a[k], bq[k]) <= v < max(a[k], bq[k]):
            s = (v - a[k]) / (bq[k] - a[k]); xs.append(a[j] + s * (bq[j] - a[j]))
    xs = sorted(xs); lo = max([x for x in xs if x < p], default=None); hi = min([x for x in xs if x > p], default=None)
    return (lo, hi, sum(1 for x in xs if x < p) % 2 == 0)
def stl_libre_cap(eje, v, p):
    k = 1 if eje == "x" else 0; j = 1 - k; iv = []
    for t in cap:
        xs = []
        for p0, p1 in ((t[0], t[1]), (t[1], t[2]), (t[2], t[0])):
            if (p0[k] - v) * (p1[k] - v) < 0 or (p0[k] != p1[k] and min(p0[k], p1[k]) <= v < max(p0[k], p1[k])):
                s = (v - p0[k]) / (p1[k] - p0[k]); xs.append(p0[j] + s * (p1[j] - p0[j]))
        if len(xs) >= 2: iv.append((min(xs), max(xs)))
    return libre(iv, p)
def mapa_libre(eje, v, p):
    k = 1 if eje == "x" else 0
    if eje == "x":
        r = H - 1 - int(np.floor((v - oy) / res)); fila = occ[r, :]; c = int(np.floor((p - ox) / res))
        if fila[c]: return None
        a = c
        while a > 0 and not fila[a - 1]: a -= 1
        z = c
        while z < W - 1 and not fila[z + 1]: z += 1
        return ox + a * res, ox + (z + 1) * res
    c = int(np.floor((v - ox) / res)); col = occ[:, c]; r = H - 1 - int(np.floor((p - oy) / res))
    if col[r]: return None
    a = r
    while a > 0 and not col[a - 1]: a -= 1
    z = r
    while z < H - 1 and not col[z + 1]: z += 1
    return oy + (H - 1 - z) * res, oy + (H - a) * res
cotas = json.load(open(COTAS)); filas = []
for ct in cotas:
    px, py = ct["punto"]; eje = ct["eje"]; v, p = (py, px) if eje == "x" else (px, py)
    cad = libre(sum((corte_intervalos_poly(q, eje, v) for q in pols), []), p)
    cap_ = stl_libre_cap(eje, v, p); mp = mapa_libre(eje, v, p)
    zs = {h: stl_libre_z(h, eje, v, p) for h in (0.05, 1.25, 2.45)}
    g = lambda r: None if r is None else [round(float(r[0]), 4), round(float(r[1]), 4)]
    w = lambda r: None if r is None else round(float(r[1] - r[0]), 4)
    fila = {"nombre": ct["nombre"], "eje": eje, "cota_escrita_m": ct["cota_m"], "CAD": g(cad), "MAPA": g(mp), "STL_tapa": g(cap_),
            **{f"STL_z{h}": g(r[:2]) if r[2] else None for h, r in zs.items()},
            "ancho_CAD": w(cad), "ancho_MAPA": w(mp), "ancho_STL": w(cap_),
            "err_ancho_MAPA-CAD": None if cad is None or mp is None else round(w(mp) - w(cad), 4),
            "err_ancho_STL-CAD": None if cad is None or cap_ is None else round(w(cap_) - w(cad), 4),
            "err_extremos_MAPA-CAD": None if cad is None or mp is None else [round(mp[0] - cad[0], 4), round(mp[1] - cad[1], 4)],
            "err_extremos_STL-CAD": None if cad is None or cap_ is None else [round(cap_[0] - cad[0], 4), round(cap_[1] - cad[1], 4)],
            "err_extremos_MAPA-STL": None if cap_ is None or mp is None else [round(mp[0] - cap_[0], 4), round(mp[1] - cap_[1], 4)]}
    filas.append(fila)
out["cotas_y_puertas"] = filas

# figura: diferencias a 2,5 mm (gris = coinciden; rojo = solo MAPA; azul = solo CAD; verde = STL fuera de MAPA)
fig = np.full((H2, W2, 3), 255, np.uint8); fig[map2 & cad2] = (90, 90, 90); fig[map2 & ~cad2] = (0, 0, 220); fig[~map2 & cad2] = (220, 60, 0); fig[stl2 & ~map2] = (0, 160, 0)
cv2.imwrite(os.path.splitext(sys.argv[2])[0] + "_diferencias.png", cv2.resize(fig, (W2 // 2, H2 // 2), interpolation=cv2.INTER_AREA))
json.dump(out, open(sys.argv[2], "w"), indent=1, ensure_ascii=False)
print(json.dumps({k: out[k] for k in out if k != "cotas_y_puertas"}, indent=1, ensure_ascii=False))
for fl in filas: print(f'{fl["nombre"]:34s} CAD {fl["ancho_CAD"]}  MAPA {fl["ancho_MAPA"]}  STL {fl["ancho_STL"]} | errW M-C {fl["err_ancho_MAPA-CAD"]} S-C {fl["err_ancho_STL-CAD"]} | ext M-C {fl["err_extremos_MAPA-CAD"]} S-C {fl["err_extremos_STL-CAD"]} | z1.25 {fl["STL_z1.25"]}')

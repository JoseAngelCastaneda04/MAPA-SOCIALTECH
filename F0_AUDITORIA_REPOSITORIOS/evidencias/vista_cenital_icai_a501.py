#!/usr/bin/env python3
"""F0 - Evidencia: vista cenital del mundo ICAI_A501 (solo lectura).

Propósito: reconstruir la relación mundo -> modelo -> malla -> pose a partir de
los archivos originales de SocialTech-Gazebo, SIN modificarlos.
- Lee worlds/ICAI_A501.world (poses de <include>).
- Lee las mallas OBJ de cada modelo y aplica la pose del <visual> (Rx 90º) y la
  pose del <include> del mundo.
- Dibuja: vértices de aula_501 en franjas de altura, huellas (bbox orientada)
  de mesas/sillas/puerta, checkpoints y la pose de spawn del robot de prueba1.launch.

Uso: python3 -I vista_cenital_icai_a501.py <ruta SocialTech-Gazebo> <salida.png>
"""
import sys, math, xml.etree.ElementTree as ET
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

repo, out = sys.argv[1], sys.argv[2]

def load_obj_vertices(path):
    vs = []
    with open(path, errors="replace") as fh:
        for line in fh:
            if line.startswith("v "):
                vs.append([float(x) for x in line.split()[1:4]])
    return np.array(vs)

def rx(a):
    c, s = math.cos(a), math.sin(a)
    return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])

def rz(a):
    c, s = math.cos(a), math.sin(a)
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])

# Pose del <visual> en los model.sdf usados (verificado en F0): 0 0 0 1.5708 0 0
VIS = rx(math.pi / 2)
MESH = {
    "aula_501": "models/aula_501/meshes/aula_501.obj",
    "table1": "models/table1/meshes/mesa1.obj",
    "table2": "models/table2/meshes/mesa2.obj",
    "chair": "models/chair/meshes/silla.obj",
    "door": "models/door/meshes/door.obj",
}
local = {k: (VIS @ load_obj_vertices(f"{repo}/{p}").T).T for k, p in MESH.items()}

world = ET.parse(f"{repo}/worlds/ICAI_A501.world").getroot().find("world")
fig, ax = plt.subplots(figsize=(10, 11))

def load_obj_faces(path):
    """Índices de caras (triangulación en abanico), base 0."""
    F = []
    with open(path, errors="replace") as fh:
        for line in fh:
            if line.startswith("f "):
                idx = [int(t.split("/")[0]) - 1 for t in line.split()[1:]]
                for i in range(1, len(idx) - 1):
                    F.append([idx[0], idx[i], idx[i + 1]])
    return np.array(F)

def section(V, F, z):
    """Segmentos de la intersección de la malla con el plano horizontal z."""
    T = V[F]
    d = T[:, :, 2] - z
    segs = []
    for tri, dd in zip(T, d):
        if (dd > 0).all() or (dd < 0).all():
            continue
        pts = []
        for a, b in ((0, 1), (1, 2), (2, 0)):
            if dd[a] * dd[b] < 0:
                t = dd[a] / (dd[a] - dd[b])
                pts.append(tri[a] + t * (tri[b] - tri[a]))
        if len(pts) == 2:
            segs.append([pts[0][:2], pts[1][:2]])
    return segs

# Aula: cortes horizontales de la malla (z en metros tras la rotación)
from matplotlib.collections import LineCollection
A = local["aula_501"]
FA = load_obj_faces(f"{repo}/{MESH['aula_501']}")
for z, col, lw in [(1.5, "#9ecae1", 0.8), (0.5, "#1f77b4", 0.8)]:
    segs = section(A, FA, z)
    ax.add_collection(LineCollection(segs, colors=col, linewidths=lw, zorder=1,
                                     label=f"aula_501 corte z={z} m ({len(segs)} seg.)"))
    print(f"corte aula_501 z={z}: {len(segs)} segmentos")

colors = {"table1": "#d62728", "table2": "#ff7f0e", "chair": "#2ca02c", "door": "#8c564b"}
for inc in world.findall("include"):
    uri = inc.findtext("uri").replace("model://", "")
    name = inc.findtext("name") or uri
    pose = [float(x) for x in (inc.findtext("pose") or "0 0 0 0 0 0").split()]
    x, y, yaw = pose[0], pose[1], pose[5]
    if uri == "checkpoint":
        ax.add_patch(plt.Circle((x, y), 0.125, color="#08306b", zorder=4))
        ax.annotate(name, (x, y), xytext=(4, 4), textcoords="offset points", fontsize=7, color="#08306b")
        continue
    if uri not in local or uri == "aula_501":
        continue
    V = local[uri]
    mn, mx = V.min(0), V.max(0)
    corners = np.array([[mn[0], mn[1], 0], [mx[0], mn[1], 0], [mx[0], mx[1], 0], [mn[0], mx[1], 0], [mn[0], mn[1], 0]])
    W = (rz(yaw) @ corners.T).T + [x, y, 0]
    ax.plot(W[:, 0], W[:, 1], color=colors[uri], lw=1.4, zorder=3)
    ax.plot(x, y, "x", color=colors[uri], ms=4, zorder=3)
    ax.annotate(name, (W[:4, 0].mean(), W[:4, 1].mean()), fontsize=6, ha="center", zorder=5)

# Spawn del robot en launch/prueba1.launch: x=-1.0 y=2.0 yaw=1.570796
sx, sy, syaw = -1.0, 2.0, 1.570796
ax.arrow(sx, sy, 0.5 * math.cos(syaw), 0.5 * math.sin(syaw), width=0.04, color="magenta", zorder=6)
ax.annotate("spawn tracer2 (prueba1.launch)", (sx, sy), xytext=(6, -10), textcoords="offset points", fontsize=7, color="magenta")
ax.plot(0, 0, "k+", ms=14, mew=2, zorder=6)
ax.annotate("origen mundo (0,0)", (0, 0), xytext=(6, -12), textcoords="offset points", fontsize=7)

ax.set_aspect("equal")
ax.grid(True, lw=0.3)
ax.set_xlabel("x [m] (marco mundo Gazebo)")
ax.set_ylabel("y [m]")
ax.set_title("ICAI_A501.world @138befa — vista cenital reconstruida desde los archivos")
ax.legend(loc="upper right", fontsize=7)
ax.autoscale_view()
fig.tight_layout()
fig.savefig(out, dpi=150)

# Resumen numérico para el informe
print("aula_501 bbox tras Rx90:", A.min(0).round(3), A.max(0).round(3))
for k in ("table1", "table2", "chair", "door"):
    V = local[k]
    print(f"{k} bbox local tras Rx90: min={V.min(0).round(3)} max={V.max(0).round(3)}")

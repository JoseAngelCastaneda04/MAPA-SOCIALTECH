#!/usr/bin/env python3
"""F5: colision del chasis = envolvente convexa SIMPLIFICADA de la malla OFICIAL tracer_base_link_no_wheel.dae (rotada Rx(+90 deg) como en el URDF del fabricante).
Los vertices son los extremos de la malla en N direcciones; el error (distancia de cada vertice original al casco simplificado) se mide y se guarda en logs/colision_chasis.json."""
import numpy as np, json, os, sys
from scipy.spatial import ConvexHull, Delaunay
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ns = {}; exec(open(D + '/scripts/medir_malla.py').read().split("for p in sys.argv")[0], ns)
v, u = ns['dae'](D + '/modelos/tracer_agv/meshes/tracer_base_link_no_wheel.dae')
v = np.c_[v[:, 0], -v[:, 2], v[:, 1]]                 # Rx(+90): (x,y,z)->(x,-z,y)
N = int(sys.argv[1]) if len(sys.argv) > 1 else 400
i = np.arange(N) + 0.5; phi = np.arccos(1 - 2 * i / N); th = np.pi * (1 + 5 ** 0.5) * i
dirs = np.c_[np.cos(th) * np.sin(phi), np.sin(th) * np.sin(phi), np.cos(phi)]
dirs = np.vstack([dirs, np.eye(3), -np.eye(3)])
sel = np.unique((v @ dirs.T).argmax(0)); P = v[sel]
h = ConvexHull(P); hv = h.vertices; Q = P[hv]
remap = {o: n for n, o in enumerate(hv)}
# distancia de los vertices originales fuera del casco simplificado (0 = dentro)
eq = h.equations; d = (v @ eq[:, :3].T + eq[:, 3]).max(1); out = np.clip(d, 0, None)
rep = dict(n_vertices_original=len(v), n_vertices_casco=int(len(Q)), n_caras=int(len(h.simplices)),
           vol_casco_m3=h.volume, vol_casco_original_m3=ConvexHull(v).volume,
           max_vertice_fuera_m=float(out.max()), p99_vertice_fuera_m=float(np.percentile(out, 99)),
           bbox_min=Q.min(0).tolist(), bbox_max=Q.max(0).tolist())
with open(D + '/modelos/tracer_agv/meshes/chasis_colision.obj', 'w') as f:
    f.write('# F5: casco convexo simplificado de tracer_base_link_no_wheel.dae (AgileX), marco base_link, metros\n')
    for p in Q: f.write('v %.5f %.5f %.5f\n' % tuple(p))
    for k, (s, e) in enumerate(zip(h.simplices, h.equations)):   # dartsim exige normales: una por cara
        f.write('vn %.5f %.5f %.5f\n' % tuple(e[:3]))
    for k, (s, e) in enumerate(zip(h.simplices, h.equations)):
        a, b, c = [remap[q] + 1 for q in s]
        n = np.cross(Q[remap[s[1]]] - Q[remap[s[0]]], Q[remap[s[2]]] - Q[remap[s[0]]])
        if n @ e[:3] < 0: b, c = c, b
        f.write('f %d//%d %d//%d %d//%d\n' % (a, k + 1, b, k + 1, c, k + 1))
os.makedirs(D + '/logs', exist_ok=True); json.dump(rep, open(D + '/logs/colision_chasis.json', 'w'), indent=1)
print(json.dumps(rep, indent=1))

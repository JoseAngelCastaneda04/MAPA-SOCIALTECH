#!/usr/bin/env python3
"""Paso MANUAL de F2: las capas de mampostería del CAD dibujan los muros como LINEs sueltas. Con
ezdxf.edgeminer se buscan los lazos que esas líneas YA cierran (tolerancia 1 mm) y se escriben como
LWPOLYLINE cerradas en una capa nueva. No se une nada que el CAD no una; las líneas abiertas se listan.
Uso: cerrar_lazos.py in.dxf out.dxf "capa1|capa2" """
import sys, ezdxf
from ezdxf import edgeminer as em
src, dst, capas = sys.argv[1], sys.argv[2], sys.argv[3].split("|")
doc = ezdxf.readfile(src); ms = doc.modelspace(); NUEVA = "F2_LAZOS_ALVENARIA"
doc.layers.add(NUEVA)
for capa in capas:
    lines = [e for e in ms if e.dxf.layer == capa and e.dxftype() == "LINE"]
    edges = [em.make_edge(e.dxf.start, e.dxf.end) for e in lines]
    loops = em.find_all_loops(em.Deposit(edges, gap_tol=1e-3), timeout=60)
    usadas = {id(ed) for lp in loops for ed in lp}
    print(f"{capa.split(' - ')[-1]}: {len(lines)} líneas -> {len(loops)} lazos cerrados")
    for lp in loops:
        pts = [(ed.start.x, ed.start.y) for ed in lp]
        xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
        print(f"   {len(lp)} aristas  x {min(xs):.2f}..{max(xs):.2f}  y {min(ys):.2f}..{max(ys):.2f}")
        ms.add_lwpolyline(pts, close=True, dxfattribs={"layer": NUEVA})
doc.saveas(dst)

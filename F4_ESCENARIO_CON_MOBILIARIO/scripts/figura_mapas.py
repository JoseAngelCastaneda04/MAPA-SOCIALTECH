#!/usr/bin/env python3
"""F4: figura de evidencia: base (F3) | mapa actualizado | tras mover la silla (verde=nueva, rojo=antigua), recorte del salon, ejes en metros del CAD."""
import os, sys, yaml, cv2, numpy as np, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.join(D, "scripts"))
from combinar_mapas import cargar
by, _, base = cargar(os.path.join(D, "..", "F3_MAPA_RVIZ2", "mapa", "piso_1cm.yaml")); _, _, act = cargar(os.path.join(D, "mapa", "piso_amueblado.yaml"))
mov = cv2.imread(os.path.join(D, "evidencias", "logs", "mapa_tras_mover_silla.pgm"), -1) < 128
ox, oy, r = by["origin"][0], by["origin"][1], by["resolution"]; h = base.shape[0]
x0, x1, y0, y1 = 6.8, 11.0, -7.1, -2.7
c0, c1 = int((x0 - ox) / r), int((x1 - ox) / r); r0, r1 = int(h - (y1 - oy) / r), int(h - (y0 - oy) / r); ext = [x0, x1, y0, y1]
def rgb(a, b=None):
    im = np.ones(a.shape + (3,)); im[a] = 0.15
    return im
fig, ax = plt.subplots(1, 3, figsize=(18, 5.2))
ax[0].imshow(rgb(base)[r0:r1, c0:c1], extent=ext); ax[0].set_title("Mapa base F3 (paredes)")
ax[1].imshow(rgb(act)[r0:r1, c0:c1], extent=ext); ax[1].set_title("Mapa actualizado = base + mobiliario (sdf2map)")
im = rgb(act); im[(act & ~mov)] = [1, 0.2, 0.2]; im[(mov & ~act)] = [0.2, 0.75, 0.2]
ax[2].imshow(im[r0:r1, c0:c1], extent=ext); ax[2].set_title("Tras mover silla_W: rojo = ocupacion que desaparece, verde = nueva")
for a in ax: a.set_xlabel("x (m, CAD)"); a.set_ylabel("y (m, CAD)"); a.grid(alpha=.3)
plt.tight_layout(); plt.savefig(os.path.join(D, "evidencias", "figuras", "mapas_base_actualizado_movimiento.png"), dpi=110)

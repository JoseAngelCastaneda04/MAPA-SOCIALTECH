"""Plano sintético de prueba: vivienda 10 x 8 m, resolución 0.05 m/px, muros de 0.15 m, 3 huecos de puerta de ~0.9 m.
Genera plano_test.png (negro=muro, blanco=libre) y plano_test.yaml (formato nav2)."""
import os
import numpy as np
import cv2

d = os.path.dirname(os.path.abspath(__file__))
res = 0.05
W, H = int(10 / res), int(8 / res)
img = np.full((H, W), 254, np.uint8)


def fill(x0, y0, x1, y1, v):
    img[int(y0 / res):int(y1 / res), int(x0 / res):int(x1 / res)] = v


for r in [(0, 0, 10, .15), (0, 7.85, 10, 8), (0, 0, .15, 8), (9.85, 0, 10, 8), (5, 0, 5.15, 8), (0, 4, 5, 4.15)]:
    fill(*r, 0)
for r in [(5, 2, 5.15, 2.9), (2, 4, 2.9, 4.15), (4.5, 7.85, 5.4, 8)]:  # huecos de puerta
    fill(*r, 254)

cv2.imwrite(f"{d}/plano_test.png", img)
with open(f"{d}/plano_test.yaml", "w") as f:
    f.write("image: plano_test.png\nmode: trinary\nresolution: 0.05\norigin: [0.0, 0.0, 0.0]\n"
            "negate: 0\noccupied_thresh: 0.65\nfree_thresh: 0.196\n")

"""FIXTURE (no es una foto real): simula la fotografía de la hoja A3 impresa con el plano.
Entrada : PNG de la hoja a 200 dpi.  Salida: JPG 4000x3000 con perspectiva, iluminación desigual, desenfoque, ruido, JPEG q75.
Dos niveles: leve (hoja inclinada ~12º en perspectiva) y fuerte (giro ~9º + perspectiva marcada + sombra)."""
import sys

import cv2
import numpy as np

src = cv2.imread(sys.argv[1])             # hoja completa (blanco = papel)
h, w = src.shape[:2]
NIVELES = {
    "leve":   dict(dst=[(520, 330), (3560, 520), (3820, 2650), (330, 2480)], grad=(0.80, 1.05), sombra=False),
    "fuerte": dict(dst=[(900, 260), (3500, 700), (3750, 2800), (250, 2300)], grad=(0.55, 1.05), sombra=True),
}
for nombre, p in NIVELES.items():
    rng = np.random.default_rng(7)
    M = cv2.getPerspectiveTransform(np.float32([[0, 0], [w, 0], [w, h], [0, h]]), np.float32(p["dst"]))
    lienzo = np.zeros((3000, 4000, 3), np.uint8)
    yy, xx = np.mgrid[0:3000, 0:4000]
    lienzo[:] = (np.array([40, 70, 110]) * (0.7 + 0.3 * np.sin(xx / 90.0)[..., None])).astype(np.uint8)   # mesa de madera
    mask = cv2.warpPerspective(np.full((h, w), 255, np.uint8), M, (4000, 3000))
    foto = cv2.warpPerspective(src, M, (4000, 3000), flags=cv2.INTER_LINEAR, borderValue=(0, 0, 0))
    lienzo = np.where(mask[..., None] > 0, foto, lienzo).astype(np.float32)
    g = np.linspace(p["grad"][0], p["grad"][1], 4000)[None, :, None] * np.linspace(1.0, 0.85, 3000)[:, None, None]
    lienzo *= g
    if p["sombra"]:
        sombra = cv2.GaussianBlur(((xx + yy * 0.3 > 2600) & (xx + yy * 0.3 < 3400)).astype(np.float32), (301, 301), 0)
        lienzo *= (1 - 0.35 * sombra)[..., None]
    lienzo = cv2.GaussianBlur(lienzo, (0, 0), 1.4) + rng.normal(0, 6, lienzo.shape)
    cv2.imwrite(f"pruebas/E_jpg/foto_simulada_{nombre}.jpg", np.clip(lienzo, 0, 255).astype(np.uint8), [cv2.IMWRITE_JPEG_QUALITY, 75])
    print(nombre, "esquinas reales de la hoja:", p["dst"])

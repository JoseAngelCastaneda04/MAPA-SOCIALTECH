#!/usr/bin/env python3
"""Rectifica la foto de una hoja de plano con OpenCV estándar (sin reconocimiento arquitectónico).

Cadena: umbral del papel -> mayor contorno -> approxPolyDP (4 vértices) -> getPerspectiveTransform -> warpPerspective.
Alternativa manual: --esquinas "x,y x,y x,y x,y" (4 clics sobre las esquinas de la hoja).
La escala sale de datos conocidos de la hoja: --papel 420x297 (mm), --escala 100 (1:100) y --px-por-mm.
Escribe <out>.png y imprime los m/px para raster_a_mapa.py --m-por-px.
"""
import argparse
import sys

import cv2
import numpy as np


def ordenar(p):
    p = np.array(p, np.float32).reshape(4, 2)
    s, d = p.sum(1), np.diff(p, axis=1).ravel()
    return np.float32([p[np.argmin(s)], p[np.argmin(d)], p[np.argmax(s)], p[np.argmax(d)]])   # TL, TR, BR, BL


def esquinas_auto(im):
    g = cv2.GaussianBlur(cv2.cvtColor(im, cv2.COLOR_BGR2GRAY), (9, 9), 0)
    _, th = cv2.threshold(g, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    th = cv2.morphologyEx(th, cv2.MORPH_CLOSE, np.ones((25, 25), np.uint8))   # tapa el dibujo dentro de la hoja
    cs, _ = cv2.findContours(th, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    c = max(cs, key=cv2.contourArea)
    for eps in (0.01, 0.02, 0.03, 0.05):
        ap = cv2.approxPolyDP(c, eps * cv2.arcLength(c, True), True)
        if len(ap) == 4:
            return ordenar(ap), f"approxPolyDP eps={eps}"
    return ordenar(cv2.boxPoints(cv2.minAreaRect(c))), "minAreaRect (aprox. NO proyectiva)"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("foto"); ap.add_argument("--out", required=True)
    ap.add_argument("--papel", default="420x297", help="ancho x alto de la hoja en mm (def. A3 apaisado)")
    ap.add_argument("--escala", type=float, default=100.0, help="denominador de la escala de impresión (def. 100)")
    ap.add_argument("--px-por-mm", type=float, default=8.0); ap.add_argument("--esquinas")
    a = ap.parse_args()
    im = cv2.imread(a.foto)
    if im is None:
        sys.exit("no se pudo leer la foto")
    if a.esquinas:
        q, how = ordenar([tuple(map(float, t.split(","))) for t in a.esquinas.split()]), "manual"
    else:
        q, how = esquinas_auto(im)
    pw, ph = map(float, a.papel.split("x")); W, H = int(pw * a.px_por_mm), int(ph * a.px_por_mm)
    M = cv2.getPerspectiveTransform(q, np.float32([[0, 0], [W, 0], [W, H], [0, H]]))
    cv2.imwrite(a.out + ".png", cv2.warpPerspective(im, M, (W, H), flags=cv2.INTER_CUBIC))
    print("esquinas", q.round(1).tolist(), "| método:", how)
    print(f"m_por_px {1.0 / a.px_por_mm * a.escala / 1000:.6f}  (hoja {pw:.0f}x{ph:.0f} mm, 1:{a.escala:.0f}, {a.px_por_mm} px/mm)")


if __name__ == "__main__":
    main()

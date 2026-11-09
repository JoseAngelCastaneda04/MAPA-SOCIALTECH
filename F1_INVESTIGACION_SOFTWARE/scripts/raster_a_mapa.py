#!/usr/bin/env python3
"""PNG de un plano (rasterizado desde PDF/LibreCAD o escaneado) -> mapa nav2 (PGM + YAML).

Por qué existe: pdftoppm/LibreCAD dan una imagen, pero no un mapa nav2 con escala, muros rellenos y sin textos.
Pasos (todos parámetros, nada específico de un plano):
  1. Máscara de "tinta de muro": píxeles oscuros y poco saturados (color de la capa de muros en CAD, o negro en escaneos).
  2. --quitar-texto N: elimina componentes conexas de menos de N px (números, cotas, símbolos sueltos).
  3. --rellenar: los muros dibujados como CONTORNO se rellenan (lo cerrado que no se alcanza desde el borde sin cruzar tinta).
  4. Escala: --m-por-px (si se conoce) o --calibrar "x1,y1,x2,y2,metros" (dos puntos sobre una cota conocida).
  5. Remuestreo a --res m/celda (celda ocupada si >=50 % de tinta). Origen: esquina inferior izquierda de la tinta -> (0,0).
No detecta puertas ni corrige trazos rotos: un contorno abierto no se rellena y se avisa.
"""
import argparse
import math
import sys

import cv2
import numpy as np


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("png"); ap.add_argument("--out", required=True)
    ap.add_argument("--m-por-px", type=float); ap.add_argument("--calibrar", help="x1,y1,x2,y2,metros")
    ap.add_argument("--res", type=float, default=0.05)
    ap.add_argument("--umbral", type=int, default=90, help="gris máximo para ser tinta (def. 90)")
    ap.add_argument("--sat-max", type=int, default=60, help="saturación máx. HSV para ser tinta de muro")
    ap.add_argument("--quitar-texto", type=int, default=0); ap.add_argument("--rellenar", action="store_true")
    ap.add_argument("--cerrar", type=int, default=0, help="cierre morfológico (px) para tapar roturas de trazo")
    ap.add_argument("--recorte", help="x0,y0,x1,y1 (px) para ignorar marcos/membretes")
    ap.add_argument("--abrir", type=int, default=0, help="apertura morfológica (px): borra líneas más finas que N px (símbolos, cotas, arcos)")
    ap.add_argument("--ancho-conocido", type=float, help="anchura REAL (m) de la tinta de muros ya limpia: calibra la escala (equivale a 1 clic sobre una cota)")
    ap.add_argument("--normalizar", action="store_true", help="quita sombras/iluminación desigual (gris / fondo desenfocado) antes del umbral")
    ap.add_argument("--enderezar", action="store_true", help="corrige el giro del escaneo (minAreaRect de la tinta mayor)")
    a = ap.parse_args()

    im = cv2.imread(a.png, cv2.IMREAD_COLOR)
    if im is None:
        sys.exit("no se pudo leer la imagen")
    if a.recorte:
        x0, y0, x1, y1 = map(int, a.recorte.split(",")); mask_roi = np.zeros(im.shape[:2], bool); mask_roi[y0:y1, x0:x1] = True
    else:
        mask_roi = np.ones(im.shape[:2], bool)
    if a.normalizar:
        k = max(31, (min(im.shape[:2]) // 8) | 1)
        fondo = cv2.GaussianBlur(cv2.morphologyEx(im, cv2.MORPH_CLOSE, np.ones((15, 15), np.uint8)), (k, k), 0).astype(np.float32)
        im = np.clip(im.astype(np.float32) / np.maximum(fondo, 1) * 255, 0, 255).astype(np.uint8)
    hsv = cv2.cvtColor(im, cv2.COLOR_BGR2HSV); gris = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    tinta = ((gris <= a.umbral) & (hsv[..., 1] <= a.sat_max) & mask_roi).astype(np.uint8)
    if a.abrir:
        tinta = cv2.morphologyEx(tinta, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_RECT, (a.abrir, a.abrir)))
    if a.enderezar:
        n, lab, st, _ = cv2.connectedComponentsWithStats(tinta, connectivity=8)
        big = (lab == 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))).astype(np.uint8)
        (cx, cy), (w, h), ang = cv2.minAreaRect(cv2.findNonZero(big))
        ang = ang - 90 if ang > 45 else ang
        print(f"giro detectado: {ang:.3f}º")
        M = cv2.getRotationMatrix2D((cx, cy), ang, 1.0)
        tinta = cv2.warpAffine(tinta, M, (tinta.shape[1], tinta.shape[0]), flags=cv2.INTER_NEAREST)
    if a.cerrar:
        tinta = cv2.morphologyEx(tinta, cv2.MORPH_CLOSE, np.ones((a.cerrar, a.cerrar), np.uint8))
    if a.quitar_texto:
        n, lab, st, _ = cv2.connectedComponentsWithStats(tinta, connectivity=8)
        keep = np.zeros(n, bool); keep[1:] = st[1:, cv2.CC_STAT_AREA] >= a.quitar_texto
        print(f"componentes: {n - 1}, eliminadas por pequeñas: {int((~keep[1:]).sum())}")
        tinta = keep[lab].astype(np.uint8)
    if a.rellenar:
        pad = cv2.copyMakeBorder(tinta, 1, 1, 1, 1, cv2.BORDER_CONSTANT, value=0)
        ff = (pad * 255).astype(np.uint8)
        cv2.floodFill(ff, np.zeros((pad.shape[0] + 2, pad.shape[1] + 2), np.uint8), (0, 0), 128)
        tinta = ((ff != 128)[1:-1, 1:-1]).astype(np.uint8)

    ys0, xs0 = np.where(tinta > 0)
    if a.ancho_conocido and xs0.size:
        a.m_por_px = a.ancho_conocido / (xs0.max() - xs0.min() + 1)
    if a.calibrar:
        x1, y1, x2, y2, m = map(float, a.calibrar.split(",")); mpp = m / math.hypot(x2 - x1, y2 - y1)
    elif a.m_por_px:
        mpp = a.m_por_px
    else:
        sys.exit("falta --m-por-px o --calibrar")
    ys, xs = np.where(tinta > 0)
    if xs.size == 0:
        sys.exit("no hay tinta de muro con esos umbrales")
    tinta = tinta[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    Wm, Hm = tinta.shape[1] * mpp, tinta.shape[0] * mpp
    W, H = int(math.ceil(Wm / a.res)), int(math.ceil(Hm / a.res))
    frac = cv2.resize(tinta.astype(np.float32), (W, H), interpolation=cv2.INTER_AREA)
    img = np.where(frac >= 0.49, 0, 254).astype(np.uint8)
    cv2.imwrite(a.out + ".pgm", img)
    with open(a.out + ".yaml", "w") as f:
        f.write(f"image: {a.out.split('/')[-1]}.pgm\nmode: trinary\nresolution: {a.res}\norigin: [0.0, 0.0, 0.0]\n"
                "negate: 0\noccupied_thresh: 0.65\nfree_thresh: 0.196\n")
    print(f"escala {mpp:.5f} m/px | tinta {tinta.shape[1]}x{tinta.shape[0]} px = {Wm:.3f} x {Hm:.3f} m | mapa {W}x{H} @ {a.res} m")


if __name__ == "__main__":
    main()

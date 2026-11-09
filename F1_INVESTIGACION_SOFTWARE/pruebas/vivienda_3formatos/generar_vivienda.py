"""Vivienda de referencia F1 (sintética). UNA sola geometría -> DXF (de aquí salen el PDF y el DWG) + verdad-terreno.

Convenciones (las de un plano CAD típico, no las de un mapa nav2):
  - Unidades: milímetros ($INSUNITS = 4). Origen CAD (0,0) = esquina SO exterior. Y hacia ARRIBA (norte).
  - Capas: A-MUROS (contornos cerrados), A-PUERTAS (hoja + arco), A-COTAS (dimensiones), A-TEXTO,
           A-MOBILIARIO (bloques MESA y SILLA), A-EJES (línea de eje, no es pared).
Dimensiones (m): exterior 10,0 x 8,0; muro exterior 0,20; muros interiores 0,10; 3 puertas de 0,90.
"""
import json
import os

import ezdxf
import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
MM = 1000.0

# (x0, y0, x1, y1) en metros
MUROS = [
    (0.00, 0.00, 4.55, 0.20), (5.45, 0.00, 10.0, 0.20),   # sur, hueco puerta 1: x 4.55-5.45
    (0.00, 7.80, 10.0, 8.00),                              # norte
    (0.00, 0.20, 0.20, 7.80), (9.80, 0.20, 10.0, 7.80),    # oeste, este
    (4.95, 0.20, 5.05, 2.00), (4.95, 2.90, 5.05, 7.80),    # interior N-S, hueco puerta 2: y 2.0-2.9
    (0.20, 3.95, 2.00, 4.05), (2.90, 3.95, 4.95, 4.05),    # interior E-O, hueco puerta 3: x 2.0-2.9
]
# puertas: (bisagra x, y, ancho, ángulo_hoja_abierta_deg, sentido)  -> hoja abierta 90º dentro del hueco
PUERTAS = [("P1", (4.55, 0.10), 0.90, 0, 90), ("P2", (5.00, 2.00), 0.90, 90, 90), ("P3", (2.00, 4.00), 0.90, 0, 90)]
MESA = (7.50, 6.00, 1.20, 0.60)    # centro x, y, largo, ancho  (m)
SILLA = (7.50, 5.20, 0.45, 0.45)


def rect(msp, r, layer):
    x0, y0, x1, y1 = [v * MM for v in r]
    msp.add_lwpolyline([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], close=True, dxfattribs={"layer": layer})


def main():
    doc = ezdxf.new("R2010", setup=True)
    doc.header["$INSUNITS"] = 4          # milímetros
    doc.header["$MEASUREMENT"] = 1       # métrico
    for nombre, color in [("A-MUROS", 7), ("A-PUERTAS", 3), ("A-COTAS", 1), ("A-TEXTO", 5), ("A-MOBILIARIO", 6), ("A-EJES", 8)]:
        doc.layers.add(nombre, color=color)
    msp = doc.modelspace()

    for m in MUROS:
        rect(msp, m, "A-MUROS")

    for nombre, (hx, hy), ancho, ang, giro in PUERTAS:
        a = np.radians(ang)
        hoja_fin = (hx + ancho * np.cos(a + np.radians(giro)), hy + ancho * np.sin(a + np.radians(giro)))
        msp.add_line((hx * MM, hy * MM), (hoja_fin[0] * MM, hoja_fin[1] * MM), dxfattribs={"layer": "A-PUERTAS"})
        msp.add_arc((hx * MM, hy * MM), ancho * MM, ang, ang + giro, dxfattribs={"layer": "A-PUERTAS"})

    # bloques de mobiliario (definidos con origen en su centro)
    for nombre, (_, _, l, w) in [("MESA", MESA), ("SILLA", SILLA)]:
        blk = doc.blocks.new(nombre)
        blk.add_lwpolyline([(-l / 2 * MM, -w / 2 * MM), (l / 2 * MM, -w / 2 * MM), (l / 2 * MM, w / 2 * MM), (-l / 2 * MM, w / 2 * MM)],
                           close=True, dxfattribs={"layer": "A-MOBILIARIO"})
    msp.add_blockref("MESA", (MESA[0] * MM, MESA[1] * MM), dxfattribs={"layer": "A-MOBILIARIO"})
    msp.add_blockref("SILLA", (SILLA[0] * MM, SILLA[1] * MM), dxfattribs={"layer": "A-MOBILIARIO"})

    # cotas, textos y eje: NO son paredes
    dim = msp.add_linear_dim(base=(5000, -1200), p1=(0, 0), p2=(10000, 0), dimstyle="EZDXF", dxfattribs={"layer": "A-COTAS"})
    dim.render()
    dim = msp.add_linear_dim(base=(-1200, 4000), p1=(0, 0), p2=(0, 8000), angle=90, dimstyle="EZDXF", dxfattribs={"layer": "A-COTAS"})
    dim.render()
    for txt, pos in [("SALON", (7500, 2500)), ("DORMITORIO 1", (2500, 6000)), ("COCINA", (2500, 2000)), ("Plano de prueba 1:100", (0, -2200))]:
        msp.add_text(txt, height=250, dxfattribs={"layer": "A-TEXTO", "insert": pos})
    msp.add_line((5000, -500), (5000, 8500), dxfattribs={"layer": "A-EJES", "linetype": "CONTINUOUS"})

    doc.saveas(os.path.join(AQUI, "vivienda.dxf"))

    # verdad-terreno en metros
    gt = {"unidades_dxf": "mm", "exterior_m": [10.0, 8.0], "interior_libre_m": [9.6, 7.6], "espesor_ext_m": 0.20,
          "espesor_int_m": 0.10, "puertas": [{"id": p[0], "ancho_m": p[2], "bisagra_m": list(p[1])} for p in PUERTAS],
          "muros_m": MUROS, "mesa_m": MESA, "silla_m": SILLA, "origen": "esquina SO exterior, Y arriba"}
    json.dump(gt, open(os.path.join(AQUI, "verdad_terreno.json"), "w"), indent=1)

    # máscara de verdad-terreno de MUROS a 1 cm/px (fila 0 = Y máx.), para medir errores en metros
    res = 0.01
    W, H = int(10.0 / res), int(8.0 / res)
    m = np.zeros((H, W), np.uint8)
    for x0, y0, x1, y1 in MUROS:
        m[H - int(round(y1 / res)):H - int(round(y0 / res)), int(round(x0 / res)):int(round(x1 / res))] = 1
    np.save(os.path.join(AQUI, "verdad_terreno_muros_1cm.npy"), m)
    print("OK", os.path.join(AQUI, "vivienda.dxf"), "muros m2:", round(m.sum() * res * res, 3))


if __name__ == "__main__":
    main()

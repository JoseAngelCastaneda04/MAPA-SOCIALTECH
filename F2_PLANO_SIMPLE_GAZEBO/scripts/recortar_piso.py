#!/usr/bin/env python3
"""Paso MANUAL de F2: aísla el piso del DXF. Copia a un DXF nuevo (con INSUNITS=6, metros) las entidades cuyo centro de caja
envolvente cae dentro de la ventana (x0 x1 y0 y1, metros) y, opcionalmente, solo las de las capas pedidas (separadas por |).
Solo ezdxf; no interpreta ni modifica geometría. Imprime lo conservado y lo descartado."""
import sys, collections, ezdxf
from ezdxf import bbox
from ezdxf.addons.importer import Importer
src, dst, x0, x1, y0, y1 = sys.argv[1], sys.argv[2], *map(float, sys.argv[3:7])
mantener = set(sys.argv[7].split("|")) if len(sys.argv) > 7 else None
doc = ezdxf.readfile(src); ms = doc.modelspace()
borr = collections.Counter(); queda = collections.Counter(); sel = []
for e in ms:
    b = bbox.extents([e])
    c = b.center if b.has_data else None
    dentro = c is not None and x0 <= c.x <= x1 and y0 <= c.y <= y1
    if dentro and (mantener is None or e.dxf.layer in mantener):
        queda[e.dxf.layer] += 1; sel.append(e)
    else:
        borr[e.dxf.layer] += 1
nuevo = ezdxf.new("R2010", units=6)          # unidades DECLARADAS = metros (corrección manual documentada)
imp = Importer(doc, nuevo); imp.import_entities(sel); imp.finalize()
nuevo.saveas(dst)
print("conservadas:", sum(queda.values()), dict(queda)); print("borradas:", sum(borr.values()))

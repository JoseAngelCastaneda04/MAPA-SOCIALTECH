#!/usr/bin/env python3
"""Paso auxiliar de la ruta PDF: escala un DXF de metros a milímetros (x1000) y declara INSUNITS=4, porque el CLI de
LibreCAD (dxf2pdf -p) solo acepta el tamaño de hoja en las unidades del dibujo. Solo ezdxf. Uso: dxf_m_a_mm.py in out"""
import sys, ezdxf
from ezdxf.math import Matrix44
doc = ezdxf.readfile(sys.argv[1]); m = Matrix44.scale(1000, 1000, 1000)
for e in doc.modelspace(): e.transform(m)
doc.header["$INSUNITS"] = 4; doc.saveas(sys.argv[2]); print("escalado x1000, INSUNITS=4")

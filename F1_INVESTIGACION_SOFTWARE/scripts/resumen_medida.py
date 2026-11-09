#!/usr/bin/env python3
"""Imprime en una línea el JSON de medir_mapa.py (para comparar rutas)."""
import json
import sys

for f in sys.argv[1:]:
    d = json.load(open(f))
    print(f"{f.split('pruebas/')[-1]:55s} IoU={d['IoU_muros']:.3f} área={d['area_muros_m2']['mapa']:.2f}/{d['area_muros_m2']['verdad']:.2f} "
          f"espurio={d['obstaculos_espurios_m2(>12cm de un muro real)']:.2f} perdido={d['muro_perdido_m2(>12cm de lo ocupado)']:.2f} "
          f"m→v máx={d['dist_mapa_a_verdad_m']['max']:.3f} v→m máx={d['dist_verdad_a_mapa_m']['max']:.3f} "
          f"puertas={sum(d['puertas_libres'].values())}/3 habitaciones_conectadas={len(set(d['componentes_libres_habitaciones'].values())) == 1}")

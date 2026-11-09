#!/usr/bin/env python3
"""F5: barre la huella del TRACER por el mapa de F4 a lo largo de una recta y da la distancia hasta el primer contacto con celdas ocupadas (prediccion por MAPA, independiente de Gazebo).
Uso: barrido_mapa.py x y yaw_deg largo_m [direccion=adelante|atras]"""
import sys, os, numpy as np
sys.argv_backup = sys.argv; sys.argv = sys.argv[:1]
_src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'huella_libre.py')).read()
__file__ = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'huella_libre.py')
exec(_src[:_src.index("if __name__ ==")])
def barrido(x, y, yaw_deg, largo, paso=0.01):
    yaw = np.radians(yaw_deg); dx, dy = np.cos(yaw), np.sin(yaw)
    for k in range(int(largo / paso) + 1):
        s = k * paso; m, _ = poligono_mascara(x + dx * s, y + dy * s, yaw)
        if (m & occ).any(): return dict(contacto_en_m=s, centro_en_contacto=[x + dx * s, y + dy * s], libre_hasta_m=max(0, s - paso))
    return dict(contacto_en_m=None, libre_hasta_m=largo)
if __name__ == '__main__':
    a = sys.argv_backup[1:]; print(barrido(float(a[0]), float(a[1]), float(a[2]), float(a[3])))

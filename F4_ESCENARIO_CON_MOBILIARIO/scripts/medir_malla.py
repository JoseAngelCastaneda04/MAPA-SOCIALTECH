#!/usr/bin/env python3
"""F4: mide una malla OBJ (solo numpy): vértices, caras, bbox en el marco de la malla y tras aplicar los giros del SDF original.
Uso: medir_malla.py malla.obj"""
import sys, numpy as np
def cargar(p):
    v=[];f=0
    with open(p) as fh:
        for l in fh:
            if l.startswith('v '): v.append([float(x) for x in l.split()[1:4]])
            elif l.startswith('f '):
                n=len(l.split())-3; f+=n  # triangulos equivalentes
    return np.array(v),f
def rx(a):
    c,s=np.cos(a),np.sin(a); return np.array([[1,0,0],[0,c,-s],[0,s,c]])
if __name__=='__main__':
    v,f=cargar(sys.argv[1]); print(f"{sys.argv[1]}: vértices={len(v)} triángulos={f}")
    def bb(x,t): print(f"  {t}: min={x.min(0).round(4)} max={x.max(0).round(4)} tamaño={(x.max(0)-x.min(0)).round(4)}")
    bb(v,'malla (marco OBJ)')
    bb(v@rx(np.pi/2).T,'Rx(90°) [una vez: solo visual/collision]')
    bb(v@rx(np.pi).T,'Rx(180°) [lo que hace table1/2 y chair: model pose + visual pose]')

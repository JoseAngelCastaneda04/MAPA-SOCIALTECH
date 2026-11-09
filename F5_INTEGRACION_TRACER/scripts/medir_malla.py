#!/usr/bin/env python3
"""F5: bbox de mallas STL (binario/ASCII) y DAE (COLLADA, aplica <unit> y up_axis; ignora transformaciones de nodo salvo que se indique). Uso: medir_malla.py archivo..."""
import sys, struct, re, numpy as np, xml.etree.ElementTree as ET
def stl(p):
    b = open(p,'rb').read()
    if b[:5]==b'solid' and b'facet' in b[:300]:
        v = np.array(re.findall(rb'vertex\s+(\S+)\s+(\S+)\s+(\S+)', b), dtype=float)
    else:
        n = struct.unpack('<I', b[80:84])[0]
        a = np.frombuffer(b[84:84+n*50], dtype=np.dtype([('n','<3f4'),('v','<9f4'),('a','<u2')]))
        v = a['v'].reshape(-1,3).astype(float)
    return v, 1.0
def dae(p):
    r = ET.parse(p).getroot(); ns = r.tag.split('}')[0]+'}'
    u = r.find(f'.//{ns}unit'); unit = float(u.get('meter')) if u is not None else 1.0
    ax = r.find(f'.//{ns}up_axis'); 
    vs=[]
    for g in r.iter(f'{ns}geometry'):
        srcs={x.get('id'):x for x in g.iter(f'{ns}source')}
        for vt in g.iter(f'{ns}vertices'):
            for i in vt.iter(f'{ns}input'):
                if i.get('semantic')=='POSITION':
                    fa=srcs[i.get('source')[1:]].find(f'{ns}float_array')
                    vs.append(np.array(fa.text.split(), dtype=float).reshape(-1,3))
    return np.vstack(vs), unit
for p in sys.argv[1:]:
    v, unit = (dae if p.lower().endswith('.dae') else stl)(p); v = v*unit
    mn, mx = v.min(0), v.max(0)
    print(f"{p}\n  unit={unit} n={len(v)} min={np.round(mn,4)} max={np.round(mx,4)} size={np.round(mx-mn,4)}")

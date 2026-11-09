#!/usr/bin/env python3
"""F4: edicion minima de config/mobiliario.yaml (texto; conserva comentarios). Despues ejecutar scripts/regenerar.sh.
  mobiliario.py anadir <id> <modelo> <x> <y> [yaw_deg]     (modelos: mesa1 mesa2 silla caja papelera)
  mobiliario.py mover  <id> <x> <y> [yaw_deg]
  mobiliario.py quitar <id>
  mobiliario.py listar"""
import os, re, sys, yaml
CFG = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config", "mobiliario.yaml")
t = open(CFG).read(); a = sys.argv[1:]
ids = [o["id"] for o in yaml.safe_load(t)["objetos"]]
if not a or a[0] == "listar":
    for o in yaml.safe_load(t)["objetos"]: print(o)
elif a[0] == "anadir":
    i, m, x, y = a[1:5]; yaw = a[5] if len(a) > 5 else "0"; assert i not in ids, "id ya existe"
    t = t.rstrip("\n") + f"\n  - {{id: {i}, modelo: {m}, x: {x}, y: {y}, z: 0, yaw_deg: {yaw}}}\n"; open(CFG, "w").write(t)
elif a[0] == "mover":
    i, x, y = a[1:4]; assert i in ids, "id desconocido"
    pat = rf"(- \{{id: {i},.*?x: )[-\d.]+(,\s*y: )[-\d.]+(,\s*z: [-\d.]+,\s*yaw_deg: )([-\d.]+)"
    yaw = a[4] if len(a) > 4 else re.search(pat, t).group(4); open(CFG, "w").write(re.sub(pat, rf"\g<1>{x}\g<2>{y}\g<3>{yaw}", t))
elif a[0] == "quitar":
    assert a[1] in ids, "id desconocido"; open(CFG, "w").write("".join(l for l in t.splitlines(True) if not re.match(rf"\s*- \{{id: {a[1]},", l)))
else: sys.exit(__doc__)

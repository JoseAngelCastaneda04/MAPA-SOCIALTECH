#!/usr/bin/env python3
"""F5.2: estadisticas de error (posicion m, yaw grados) de ODOM y AMCL frente a la pose real de Gazebo, a partir del CSV del monitor. Uso: analizar_csv.py CSV [t_ini t_fin]"""
import sys, csv, math
f = sys.argv[1]; t0 = float(sys.argv[2]) if len(sys.argv) > 2 else -1e9; t1 = float(sys.argv[3]) if len(sys.argv) > 3 else 1e12
R = [r for r in csv.DictReader(open(f)) if t0 <= float(r['t']) <= t1]
def est(v): v = sorted(v); n = len(v); return 'media %.4f  mediana %.4f  p95 %.4f  max %.4f' % (sum(v)/n, v[n//2], v[int(n*.95)-1], v[-1])
print('muestras:', len(R), ' duracion: %.1f s' % (float(R[-1]['t']) - float(R[0]['t'])))
# recorrido real acumulado
d = sum(math.hypot(float(R[i]['gt_x'])-float(R[i-1]['gt_x']), float(R[i]['gt_y'])-float(R[i-1]['gt_y'])) for i in range(1, len(R))); print('distancia real recorrida: %.2f m' % d)
for k in ('odom', 'amcl'):
    print('ERROR %-4s posicion (m):' % k.upper(), est([float(r['err_%s_pos' % k]) for r in R])); print('ERROR %-4s yaw (grados, |.|):' % k.upper(), est([abs(float(r['err_%s_yaw_deg' % k])) for r in R]))
    print('        final: %.4f m, %+.2f deg' % (float(R[-1]['err_%s_pos' % k]), float(R[-1]['err_%s_yaw_deg' % k])))

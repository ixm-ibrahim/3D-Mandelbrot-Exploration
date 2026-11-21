"""Round 20 check: two screens that take seconds and would have stopped m_w3 before the panel.
  ear   : the rabbit's two ears, thickness round the x-axis over width in the flat plane (a ball of the one-plane rule: 1.15, 1.19)
  settle: the basilica nudged by 0.03, 0.058 (and c = -0.9 nudged by 0.01) in 19 directions: does the orbit of 0 come to rest on a cycle?
python out/r20/check/screens.py <rule> [<rule> ...]"""
import os, sys, json
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, 'out', 'r16', 'bench'))
import bench as B
import rules as R
RAB = (-0.122561, 0.744862, 0.0); z = complex(RAB[0], RAB[1]); z2 = z * z + z


def ear(F, cen, c=RAB, steps=80):
    x0, y0 = cen; rho = abs(y0); t = np.linspace(0, 0.9, 18001)
    def first(ins):
        o = np.flatnonzero(~ins); return float(t[o[0]]) if o.size else float(t[-1])
    w = []
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        ins, _ = B.inside(F, x0 + dx * t, y0 + dy * t, 0 * t, c=c, steps=steps); w.append(first(ins))
    a = t / rho; th = []
    for s in (1.0, -1.0):
        ins, _ = B.inside(F, np.full_like(t, x0), y0 * np.cos(s * a), abs(y0) * np.sin(s * a), c=c, steps=steps); th.append(first(ins))
    return 0.5 * (th[0] + th[1]) / min(0.5 * (w[0] + w[1]), 0.5 * (w[2] + w[3]))


def settles(F, c, n=3000):
    x = np.zeros(1); y = np.zeros(1); zz = np.zeros(1); R2 = B.resc(c) ** 2; tr = []
    for k in range(n):
        x, y, zz = F(x, y, zz); x = x + c[0]; y = y + c[1]; zz = zz + c[2]
        if not np.isfinite(x[0]) or x[0] ** 2 + y[0] ** 2 + zz[0] ** 2 > R2:
            return 'L'
        if k >= n - 300:
            tr.append((x[0], y[0], zz[0]))
    tr = np.array(tr)
    for p in (1, 2, 3, 4, 6, 8, 12, 16):
        if np.abs(tr[p:] - tr[:-p]).max() < 1e-6:
            return str(p) if p < 10 else 'c'
    return '~'


out = {}
for rule in sys.argv[1:]:
    try:
        F = R.get(rule)
    except Exception as e:
        print(rule, 'not registered'); continue
    e1 = ear(F, (z.real, z.imag)); e2 = ear(F, (z2.real, z2.imag))
    rows = {}
    for nm, cx, size in (('basilica 0.030', -1.0, 0.03), ('basilica 0.058', -1.0, 0.058), ('c=-0.9   0.010', -0.9, 0.01)):
        rows[nm] = [settles(F, (cx, size * np.cos(np.radians(d)), size * np.sin(np.radians(d)))) for d in range(0, 91, 5)]
    calm = sum(r == '2' for v in rows.values() for r in v); tot = sum(len(v) for v in rows.values())
    out[rule] = dict(ear_c=e1, ear_c2=e2, settle=rows, calm=calm, of=tot)
    print('%-10s ears: thickness / width %.2f and %.2f (needs about 1) | orbit of 0 rests on the 2-cycle in %d of %d nudged cases' % (rule, e1, e2, calm, tot))
    for nm, v in rows.items():
        print('            %s, direction 0..90 by 5: %s' % (nm, ' '.join(v)), flush=True)
json.dump(out, open(os.path.join(HERE, 'screens.json'), 'w'), indent=1)

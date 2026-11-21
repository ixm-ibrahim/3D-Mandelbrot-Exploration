"""Hunter task 2 (claim C1): for a given c, is there any flat plane other than z = 0 that the map v -> F(v) + c keeps?
Direct test: put points on a candidate plane {n . v = d}, apply the map once, measure how far the answers stand
off the plane (RMS, in units of length). An invariant plane gives 0. All planes are scanned (normal every ~2.5
degrees, offset d from -0.9 to 0.9), the best ones are polished.   Also: where do bounded orbits end up?
    python out/r17/hunter/c1.py   -> c1.json, c1.txt
"""
import os, sys, json
import numpy as np
from scipy.optimize import minimize
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import core as K
import rules as R

RABBIT = np.array([-0.122561, 0.744862, 0.0])
CASES = [('rabbit', RABBIT), ('basilica (control)', np.array([-1.0, 0, 0])), ('c = (-0.6, 0.3, 0)', np.array([-0.6, 0.3, 0.0]))]
names = ['oneplane', 'lathe', 'along', 'twoplane', 'away']
rng = np.random.default_rng(3)
DISC = rng.uniform(-1, 1, (4000, 2)); DISC = DISC[(DISC ** 2).sum(1) <= 1][:500] * 1.3      # points on the plane, radius 1.3


def frame(n):
    a = np.array([1.0, 0, 0]) if abs(n[0]) < 0.9 else np.array([0, 1.0, 0])
    e1 = np.cross(n, a); e1 /= np.linalg.norm(e1); e2 = np.cross(n, e1)
    return e1, e2


def resid(F, c, n, d):
    n = n / np.linalg.norm(n); e1, e2 = frame(n)
    v = d * n + DISC[:, :1] * e1 + DISC[:, 1:] * e2
    w = K.apply(F, v) + c
    return float(np.sqrt((((w @ n) - d) ** 2).mean()))


def scan(F, c):
    # normals over a half sphere
    out = []
    for el in np.radians(np.arange(0, 90.1, 2.5)):
        k = max(1, int(round(144 * np.cos(el))))
        for az in np.arange(k) * 2 * np.pi / k:
            n = np.array([np.cos(el) * np.cos(az), np.cos(el) * np.sin(az), np.sin(el)])
            e1, e2 = frame(n)
            for d in np.linspace(-0.9, 0.9, 37):
                v = d * n + DISC[:, :1] * e1 + DISC[:, 1:] * e2
                w = K.apply(F, v) + c
                out.append((float(np.sqrt((((w @ n) - d) ** 2).mean())), n[0], n[1], n[2], d))
    return np.array(out)


def polish(F, c, n, d):
    def f(p):
        n_ = np.array([np.cos(p[1]) * np.cos(p[0]), np.cos(p[1]) * np.sin(p[0]), np.sin(p[1])])
        return resid(F, c, n_, p[2])
    p0 = [np.arctan2(n[1], n[0]), np.arcsin(np.clip(n[2], -1, 1)), d]
    r = minimize(f, p0, method='Nelder-Mead', options=dict(xatol=1e-10, fatol=1e-14, maxiter=4000))
    p = r.x; n_ = np.array([np.cos(p[1]) * np.cos(p[0]), np.cos(p[1]) * np.sin(p[0]), np.sin(p[1])])
    return float(r.fun), n_, float(p[2])


def orbits(F, c, n=40000, steps=600):
    v = rng.uniform(-1.6, 1.6, (n, 3)); idx = np.arange(n)
    for k in range(steps):
        v = K.apply(F, v) + c
        keep = (v * v).sum(1) <= 9.0
        idx, v = idx[keep], v[keep]
    if idx.size == 0:
        return dict(bounded=0)
    ref = v.copy(); per = np.full(idx.size, -1); zmax = np.abs(v[:, 2]).copy(); ymax = np.abs(v[:, 1]).copy()
    for p in range(1, 49):
        v = K.apply(F, v) + c
        zmax = np.maximum(zmax, np.abs(v[:, 2])); ymax = np.maximum(ymax, np.abs(v[:, 1]))
        hit = (per < 0) & (np.abs(v - ref).max(1) < 1e-7); per[hit] = p
    vals, cnt = np.unique(per, return_counts=True)
    return dict(bounded=int(idx.size), share_bounded=float(idx.size / n), periods={int(a): int(b) for a, b in zip(vals, cnt)},
                share_ending_in_flat_plane=float((zmax < 1e-6).mean()), share_ending_in_plane_y0=float((ymax < 1e-6).mean()),
                largest_height_reached=float(zmax.max()))


res = {}; lines = []
for cname, c in CASES:
    for nm in names:
        F = R.get(nm)
        T = scan(F, c)
        order = np.argsort(T[:, 0])
        found = []
        for i in order[:4000]:
            r0, nx, ny, nz, d = T[i]
            n = np.array([nx, ny, nz])
            if any(abs(abs(n @ f[1]) - 1) < 0.02 and abs(d - f[2] * np.sign(n @ f[1])) < 0.08 for f in found):
                continue
            rr, n2, d2 = polish(F, c, n, d)
            if n2[2] < 0 or (n2[2] == 0 and n2[1] < 0):
                n2, d2 = -n2, -d2
            if any(abs(abs(n2 @ f[1]) - 1) < 1e-3 and abs(d2 - f[2] * np.sign(n2 @ f[1])) < 1e-3 for f in found):
                continue
            found.append((rr, n2, d2))
            if len(found) >= 5:
                break
        found.sort(key=lambda f: f[0])
        ob = orbits(F, c)
        res['%s | %s' % (cname, nm)] = dict(planes=[dict(off_plane_rms=f[0], normal=[float(x) for x in f[1]], offset=f[2]) for f in found],
                                             typical_rms=float(np.median(T[:, 0])), orbits=ob)
        lines.append('%-20s %-9s median over all planes %.3f. Best planes: ' % (cname, nm, np.median(T[:, 0])) +
                     ' | '.join('rms %.1e normal (%+.2f %+.2f %+.2f) d %+.3f' % (f[0], *f[1], f[2]) for f in found[:4]))
        lines.append('%-20s %-9s bounded orbits: %s' % ('', '', json.dumps(ob)))
        print(lines[-2]); print(lines[-1], flush=True)
json.dump(res, open(os.path.join(HERE, 'c1.json'), 'w'), indent=1)
open(os.path.join(HERE, 'c1.txt'), 'w').write('\n'.join(lines) + '\n')

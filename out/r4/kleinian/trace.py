import sys, os, json
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import model as M
km = M.km
presets = json.load(open('data/klein-presets.json', encoding='utf-8'))
k = presets[int(sys.argv[1]) if len(sys.argv) > 1 else 8]['k']
rule = sys.argv[2] if len(sys.argv) > 2 else 'leys'
mu = np.array([k['mx'], k['my'], k['mz']]); L = k['L']; three = k['three']; a = mu[1]
pts, true, res, (C, Rr) = M.study(k, n=20000)
est = res['exact %s+balls' % rule][0]
out = true > 2e-3
ratio = np.where(out, est / np.maximum(true, 1e-9), 0)
bad = np.argsort(-ratio)[:400]
bad = bad[::40]
def sphere_vec(c, r):   # ball centre c radius r as a vector of R^(4,1): inside when <v, X> > 0 (see klein_model)
    w = 1.0 / r
    x = c * w
    s = 0.5 * ((c * c).sum() - r * r) * w
    return np.array([x[0], x[1], x[2], s - 0.5 * w, s + 0.5 * w])
def neg(v):   # q -> -q
    o = v.copy(); o[:3] = -o[:3]; return o
fs = np.sign(-mu[0]); sx, sz = mu[0] / a, mu[2] / a
wrap = lambda x, per, s: (x - s) - per * np.floor((x - s) / per) + s
for i in bad:
    z = pts[i].copy()
    d = np.sqrt(((C - z) ** 2).sum(1)) - Rr
    j = int(np.argmin(d))
    print("\npoint %s true %.4f est %.4f ratio %.1f | nearest pearl r %.4f at %s" % (np.round(z, 3), true[i], est[i], ratio[i], Rr[j], np.round(C[j], 3)))
    v = sphere_vec(C[j], Rr[j])
    for step in range(14):
        x0 = z[0]; z[0] -= sx * z[1]; z[0] = wrap(z[0], 2.0, -1.0); z[0] += sx * z[1]; sh = np.array([z[0] - x0, 0, 0])
        if three:
            z0 = z[2]; z[2] -= sz * z[1]; z[2] = wrap(z[2], 2 * L, -L); z[2] += sz * z[1]; sh[2] = z[2] - z0
        v = km.tr(v, sh)
        xs = z[0] - 0.5 * mu[0]
        if rule == 'leys':
            line = a * 0.5 + fs * (2.0 * a - 1.95) / 4.0 * np.sign(xs) * (1.0 - np.exp(-(7.2 - (1.95 - a) * 15.0) * abs(xs)))
            up = z[1] >= line
        else:
            up = ((z - mu) ** 2).sum() < (z * z).sum()
        if up:
            z = mu - z; v = km.tr(neg(v), mu)
        w = v[4] - v[3]
        cc, rr = (v[:3] / w, 1 / w) if abs(w) > 1e-9 else (None, None)
        dq = (np.linalg.norm(z - cc) - rr) if cc is not None else None
        print("  step %2d %s q=%s |q|=%.3f  pearl c=%s r=%s gap=%s" % (step, 'flip' if up else '    ', np.round(z, 3), np.linalg.norm(z), None if cc is None else np.round(cc, 3), None if rr is None else round(float(rr), 4), None if dq is None else round(float(dq), 4)))
        z = mu + z * np.array([1, -1, -1]) / (z * z).sum()
        v = km.tr(km.J(v), mu)
        w = v[4] - v[3]
        if abs(w) < 1e-7: print("  -> pearl became a wall at step", step); break

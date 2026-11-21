# where does the reference lose accuracy near a seam? (for the entry engineer's check against it)
import sys, os, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', '..', 'me', 'r15'))
import fastpil as Fp, pillow_ref as P
rng = np.random.default_rng(3)
lay = Fp.get_lay(Fp.REF)
for scale in (1e-2, 1e-3, 1e-4, 1e-5, 1e-6):
    u = rng.uniform(-0.5, 0.5, 50000); eps = rng.normal(size=50000) * scale
    r2 = u * u + eps * eps
    d = np.stack([2 * u / (1 + r2), 2 * eps / (1 + r2), (1 - r2) / (1 + r2) * rng.choice([-1, 1], 50000)], 1)
    s, t = P.pil(d); back = P.dirn(s, t); er = np.abs(back - d).max(axis=1)
    s2, t2 = lay.pil(d[:, 0], d[:, 1], d[:, 2]); b2 = np.stack(lay.dirn(s2, t2), 1); ef = np.abs(b2 - d).max(axis=1)
    fa = P.F(d.copy()); fb = np.stack(Fp.F(d[:, 0].copy(), d[:, 1].copy(), d[:, 2].copy(), lay), 1); df = np.abs(fa - fb).max(axis=1)
    i = int(np.argmax(er))
    print('distance from the seam ~%g: reference round trip worst %.1e (share above 1e-9: %.4f), fast %.1e; F reference against fast worst %.1e (share above 1e-9: %.4f); worst point p = (%.6f, %.2e), reference beta %.3e, fast beta %.3e' % (
        scale, er.max(), (er > 1e-9).mean(), ef.max(), df.max(), (df > 1e-9).mean(), u[i], eps[i], P.solve_beta(u[i:i+1], eps[i:i+1])[0], Fp.solve_beta(u[i:i+1], eps[i:i+1])[0]))
v = rng.normal(size=(20000, 3)); v /= np.linalg.norm(v, axis=1)[:, None]
for k in range(5):
    v = rng.normal(size=(20000, 3)); v *= (rng.uniform(0.2, 1.5, 20000) / np.linalg.norm(v, axis=1))[:, None]
    fa = P.F(v.copy()); fb = np.stack(Fp.F(v[:, 0].copy(), v[:, 1].copy(), v[:, 2].copy(), lay), 1); df = np.abs(fa - fb).max(axis=1)
    print('20,000 random points, draw %d: worst %.1e, points above 1e-9: %d' % (k, df.max(), (df > 1e-9).sum()))

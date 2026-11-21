import sys, os, time, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', '..', 'me', 'r15'))
import fastpil as Fp, pillow_ref as P
rng = np.random.default_rng(3)
v = rng.normal(size=(1000000, 3)); v /= np.linalg.norm(v, axis=1)[:, None]
lay = Fp.get_lay(Fp.REF)
x, y, z = v[:, 0].copy(), v[:, 1].copy(), v[:, 2].copy()
t0 = time.time(); Fp.F(x, y, z, lay); print('F 1M', time.time() - t0)
den = 1 + np.abs(z); px, py = x / den, y / den
t0 = time.time(); b = Fp.solve_beta(px, py); print('solve 1M', time.time() - t0)
t0 = time.time(); s, t = lay.pil(x, y, z); print('pil', time.time() - t0)
t0 = time.time(); lay.dirn(s, t); print('dirn', time.time() - t0)
# who is right near the seam: round trips
u = rng.uniform(-0.5, 0.5, 50000); eps = rng.normal(size=50000) * 1e-4
r2 = u * u + eps * eps
d = np.stack([2 * u / (1 + r2), 2 * eps / (1 + r2), (1 - r2) / (1 + r2) * rng.choice([-1, 1], 50000)], 1)
s, t = P.pil(d); back = P.dirn(s, t); print('near the seam: reference round trip worst %.2e' % np.abs(back - d).max())
s, t = lay.pil(d[:, 0], d[:, 1], d[:, 2]); bx, by, bz = lay.dirn(s, t); print('near the seam: fast round trip worst %.2e' % np.abs(np.stack([bx, by, bz], 1) - d).max())
# the single worst random point
v = rng.normal(size=(200000, 3)); v /= np.linalg.norm(v, axis=1)[:, None]
s, t = P.pil(v); back = P.dirn(s, t); print('random: reference round trip worst %.2e' % np.abs(back - v).max())
s, t = lay.pil(v[:, 0], v[:, 1], v[:, 2]); bx, by, bz = lay.dirn(s, t); print('random: fast round trip worst %.2e' % np.abs(np.stack([bx, by, bz], 1) - v).max())

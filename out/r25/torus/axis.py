"""Section 'torus': small measurements behind NOTES.md.
1. ring3, c = 0: which heights on the upright axis stay (the discus and the bowls).
2. ring3 and ring3b: how the 'inside' share shrinks with the number of steps (is there a real body?).
3. hopf: what the flat cut and an upright half-plane hold (how far from the flat picture).
"""
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import torus as T
M = T.M

r3 = T.RULES['ring3']()
h = np.linspace(0.0005, 6.0, 12000); n = M.stay(r3, 1e-7 + 0 * h, 0 * h, h, 0.0, 0.0, 0.0, 200) >= 200
edges = np.flatnonzero(np.diff(n.astype(int)) != 0)
print('ring3, c = 0, upright axis: inside from 0 up to h = %.4f (predicted tan 15 deg = %.4f)' % (h[edges[0]], np.tan(np.radians(15))))
big = [(h[a], h[b]) for a, b in zip(edges[:-1], edges[1:]) if n[a + 1] and h[b] - h[a] > 0.05]
print('   further inside stretches wider than 0.05:', ['%.3f..%.3f' % t for t in big], '(predicted bowl 1.000..%.3f)' % (1 / np.tan(np.radians(15))))
print('   number of separate inside stretches between h = 0 and 6: %d' % (len(edges) // 2 + 1))

rng = np.random.default_rng(7); q = rng.uniform(-1, 1, size=(3, 150000)) * np.array([[1.8], [1.4], [1.4]])
for key in ('oneplane', 'ring3', 'ring3b'):
    r = T.RULES[key]()
    for nm, c in [('c = -1', (-1.0, 0.0, 0.0)), ('rabbit', M.RABBIT)]:
        s = [float((M.stay(r, q[0], q[1], q[2], *c, k) >= k).mean()) for k in (30, 60, 120, 240)]
        print('%-9s %-7s share of the box still inside after 30 / 60 / 120 / 240 steps: %.4f %.4f %.4f %.4f' % (key, nm, *s))

# hopf: the flat cut against the flat picture, and an upright half-plane against the flat picture
hp = T.RULES['hopf'](); n = 40000; zr, zi = rng.uniform(-1.8, 1.8, n), rng.uniform(-1.3, 1.3, n)
for nm, c in [('c = -1', (-1.0, 0.0)), ('rabbit', M.RABBIT[:2])]:
    flat = M.flat_stay(zr, zi, c[0], c[1], 60) >= 60
    cut = M.stay(hp, zr, zi, 0 * zr, c[0], c[1], 0.0, 60) >= 60
    # the same flat point read in the half-plane y = 0, x > 0 through the disc coordinate d = z/2 (ring point in the middle)
    d = (zr + 1j * zi) / 2.0; zeta = (1 + d) / (1 - d); ok = zeta.real > 0
    up = M.stay(hp, zeta.real, 0 * zr, zeta.imag, c[0], c[1], 0.0, 60) >= 60
    Zh = T.hopf_value(zeta.real, 0 * zr, zeta.imag); stretch = np.abs(Zh) / np.maximum(np.abs(zr + 1j * zi), 1e-12)
    print('hopf %-7s flat cut differs from the flat picture at %d of %d points; an upright half-plane (read through d = z/2) differs at %d of %d; there the radius is stretched by %.2f .. %.2f'
          % (nm, int((flat != cut).sum()), n, int((flat[ok] != up[ok]).sum()), int(ok.sum()), stretch[flat].min(), stretch[flat].max()))

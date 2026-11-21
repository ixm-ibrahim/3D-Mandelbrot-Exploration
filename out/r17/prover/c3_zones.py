"""Prover: how close does the skin of a Julia set come to the origin? (the main body of the Mandelbrot solid is decided
by the rule inside radius 1/2: the flat resting point has size at most 1/2).  Flat picture, and the 3D basilica of the
known rules oneplane and twoplane.      python out/r17/prover/c3_zones.py"""
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, 'out', 'me', 'r16')); sys.path.insert(0, os.path.join(ROOT, 'out', 'r14', 'turns'))
import scout as S

def flat_min(c, n=1601, L=0.8, steps=400):
    a = np.linspace(-L, L, n); X, Y = np.meshgrid(a, a); z = X + 1j * Y; alive = np.ones(z.shape, bool)
    for _ in range(steps):
        z[alive] = z[alive] ** 2 + c; alive &= np.abs(z) <= 4
    r = np.hypot(X, Y); return r[~alive].min()

for nm, c in (('basilica c = -1', -1 + 0j), ('rabbit', -0.122561 + 0.744862j), ('c = -0.5 (inside the main body)', -0.5 + 0j), ('c = 0.2775+0.2980i (sheet, middle picture)', 0.2775 + 0.2980j), ('c = i (a tree: the set passes through 0)', 1j)):
    print('flat %-45s nearest point outside the filled set: %.3f from the origin' % (nm, flat_min(c)))

rng = np.random.default_rng(2)
for nm, F in (('oneplane', S.oneplane), ('twoplane', S.twoplane)):
    u = rng.normal(size=(3, 200000)); u /= np.linalg.norm(u, axis=0)
    rmin = 9.0
    for rad in np.arange(0.40, 0.70, 0.005):
        v = u * rad; alive = np.ones(v.shape[1], bool)
        for _ in range(80):
            X, Y, Z = F(v[0, alive], v[1, alive], v[2, alive]); w = np.stack([X - 1.0, Y, Z]); v[:, alive] = w
            alive[alive] = (w * w).sum(0) <= 36
        if (~alive).any(): rmin = rad; break
    print('3D basilica of %-9s: the whole ball of radius %.3f round the origin is inside the set; first outside point at radius %.3f' % (nm, rmin - 0.005, rmin))

"""Round 23, section "cone": the best rule of the hinge-free door ("welded cones"). Depends only on out/r21/lib/mem.py.

    import sys; sys.path.insert(0, 'out/r23/cone'); import best; r = best.rule()      # the fixed rule (bench-style M.Rule)
    best.rule('c')                    # the same with the cones turned to follow c (looks at c; has a seam, see NOTES.md)
    best.rule(theta=0.0)              # any other turn of the cones (0 and pi are the y-mirror-symmetric ones)
    python out/r23/cone/best.py       # flat check, lift test, 30 against 80 and 200 steps

The square of v = (x, y, z), r = |v|:
    mu = atanh(z / r)  (Mercator latitude),  lam = atan2(y, x)
    E  = the unit vector at Mercator latitude 2|mu|, longitude 2 lam                (the one-plane rule's direction, w^2)
    C  = the unit vector at Mercator latitude MU60 - |mu|, longitude theta - lam    (the turn-over rho e^(i theta) / w)
         MU60 = ln(2 + sqrt 3) = 1.31696 is the Mercator latitude of 60 degrees
    chi = S((|mu| - MUA) / (MUB - MUA)) clamped to 0..1,  S(q) = q^3 (10 - 15 q + 6 q^2)
         MUA = 0.2 (below it the rule IS the one-plane rule), MUB = MUA + (MU60/3 - MUA) / 0.59087 = 0.60447
         (0.59087 is where S = 2/3: at |mu| = MU60/3 the mix must be exactly 2/3, or the rule folds)
    G  = ((1 - chi) E + chi C) made a unit vector again, its z given the sign of z
    square = r^2 G
theta = 90 degrees for the fixed rule; theta = 1.5 * atan2(cy, cx) for the 'c' variant.
"""
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, 'out', 'r21', 'lib'))
import mem as M

MU60 = float(np.log(2.0 + np.sqrt(3.0))); MUA = 0.2; MUB = MUA + (MU60 / 3 - MUA) / 0.59087


def direction(x, y, z, theta):
    r = np.sqrt(x * x + y * y + z * z); rs = np.where(r > 0, r, 1.0)
    mu = np.arctanh(np.clip(z / rs, -1 + 1e-15, 1 - 1e-15)); lam = np.arctan2(y, x); am = np.abs(mu); sg = np.where(z < 0, -1.0, 1.0)
    q = np.clip((am - MUA) / (MUB - MUA), 0.0, 1.0); chi = q * q * q * (10 - 15 * q + 6 * q * q)
    a = np.minimum(2 * am, 60.0); b = np.clip(MU60 - am, -60.0, 60.0)
    X = (1 - chi) * np.cos(2 * lam) / np.cosh(a) + chi * np.cos(theta - lam) / np.cosh(b)
    Y = (1 - chi) * np.sin(2 * lam) / np.cosh(a) + chi * np.sin(theta - lam) / np.cosh(b)
    Z = (1 - chi) * np.tanh(a) + chi * np.tanh(b)
    n = np.sqrt(X * X + Y * Y + Z * Z); n = np.where(n > 0, n, 1.0)
    return X / n, Y / n, sg * Z / n


def rule(kind='fixed', theta=np.pi / 2):
    def step(x, y, z, st, k, cx, cy, cz):
        th = (1.5 * np.arctan2(cy, cx) + 0 * x) if kind == 'c' else theta
        r2 = x * x + y * y + z * z; X, Y, Z = direction(x, y, z, th); ok = r2 > 0
        return np.where(ok, r2 * X, 0.0), np.where(ok, r2 * Y, 0.0), np.where(ok, r2 * Z, 0.0), st
    if kind == 'c':
        return M.Rule('cones-c', 'welded cones, turned to follow c', step, init=lambda n: ())
    return M.Rule('cones', 'welded cones, theta = %.0f degrees' % np.degrees(theta), step, init=lambda n: ())


if __name__ == '__main__':
    for kind in ('fixed', 'c'):
        r = rule(kind); print('==', r.name, '|', r.label)
        rng = np.random.default_rng(2); p = rng.normal(size=(3, 5000)) * rng.uniform(1e-9, 2, 5000); p[2, :50] = 0; p[0, 50:60] = 0; p[1, 50:60] = 0
        o = r.step(p[0], p[1], p[2], (), 0, np.full(5000, -0.12), np.full(5000, 0.74), np.zeros(5000))
        print('   finite on a test batch (flat points and points on the upright axis among them):', bool(all(np.isfinite(t).all() for t in o[:3])),
              '| length squared, largest error %.1e' % np.abs(np.sqrt(o[0] ** 2 + o[1] ** 2 + o[2] ** 2) - (p * p).sum(0)).max())
        print('   flat check:', M.flat_check(r, n=20000, steps=60))
        zr, zi = rng.uniform(-1.8, 1.8, 6000), rng.uniform(-1.3, 1.3, 6000)
        for nm, c in (('c = -1', (-1.0, 0.0, 0.0)), ('c = -0.75', (-0.75, 0.0, 0.0)), ('rabbit', M.RABBIT), ('Siegel disc', M.SIEGEL)):
            ins = M.flat_stay(zr, zi, c[0], c[1], 300) >= 300
            lost = [int((M.stay(r, zr[ins], zi[ins], np.full(ins.sum(), e), c[0], c[1], 0.0, 150) < 150).sum()) for e in (1e-6, 1e-3, 1e-2)]
            v = rng.uniform([-1.8, -1.4, -1.4], [1.8, 1.4, 1.4], size=(150000, 3)); n = M.stay(r, v[:, 0], v[:, 1], v[:, 2], c[0], c[1], c[2], 200)
            print('   %-11s lifted by 1e-6 / 1e-3 / 1e-2: %d / %d / %d lost of %d | share of a box inside after 30, 80, 200 steps: %.4f %.4f %.4f'
                  % (nm, lost[0], lost[1], lost[2], int(ins.sum()), (n >= 30).mean(), (n >= 80).mean(), (n >= 200).mean())); sys.stdout.flush()

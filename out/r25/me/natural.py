"""Round 25 scout: rules that follow from "sphere inversions" and "quaternions" with nothing chosen.

1. 'fit'   The fitted-inversion square. At every point z0 of the flat plane there is exactly one chain of circle
           inversions (a Moebius map) that agrees with z -> z^2 at z0 in place, in speed and in bend. Circles become
           spheres with the same centre and radius (the paper's "inflation"), and the point at height t above z0 is
           moved by that chain. Worked out with quaternions (v = z0 + t j, r = |z0|):
               square(z0, t) = ( z0^2 (4 r^2 - 3 t^2) / (4 r^2 + t^2) ,  height 8 t r^3 / (4 r^2 + t^2) )
           (the Ahlfors-Weill extension of z^2). Nothing is chosen. It is exact on the flat plane, shape-keeping
           beside it, and treats every direction round the upright axis alike.

2. 'mid s' Between the sphere-inversion square P (one plane) and the quaternion square Q (the Lathe). Both have the
           length |v|^2 and both are z^2 on the flat plane, so they differ only by a turn: the turn that takes P(v)
           to Q(v). Do the share s of that turn (a quaternion "slerp"). s = 0 is one plane, s = 1 the Lathe.

3. 'alt'   P and Q in turn (P on even steps, Q on odd ones): the plainest other way to use both.

    python out/r25/me/natural.py check | cuts | solids a|top
"""
import os, sys, time
import numpy as np
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, 'out', 'r21', 'lib'))
import mem as M


def P(x, y, z):
    r2 = x * x + y * y + z * z; r = np.sqrt(r2); d = r2 + z * z; f = np.where(d > 0, r2 / np.where(d > 0, d, 1.0), 0.0)
    return f * (x * x - y * y), f * 2 * x * y, f * 2 * r * z


def Q(x, y, z):
    return x * x - y * y - z * z, 2 * x * y, 2 * x * z


def fit(x, y, z):
    r2 = x * x + y * y; r = np.sqrt(r2); t2 = z * z; den = 4 * r2 + t2; ok = den > 0; dn = np.where(ok, den, 1.0)
    k = (4 * r2 - 3 * t2) / dn
    return np.where(ok, k * (x * x - y * y), 0.0), np.where(ok, k * 2 * x * y, 0.0), np.where(ok, 8 * z * r * r2 / dn, 0.0)


def mid(s):
    def F(x, y, z):
        px, py, pz = P(x, y, z); qx, qy, qz = Q(x, y, z)
        L = x * x + y * y + z * z; Ls = np.where(L > 0, L, 1.0)
        dot = np.clip((px * qx + py * qy + pz * qz) / (Ls * Ls), -1.0, 1.0); om = np.arccos(dot); so = np.sin(om)
        small = so < 1e-9
        a = np.where(small, 1 - s, np.sin((1 - s) * om) / np.where(small, 1.0, so)); b = np.where(small, s, np.sin(s * om) / np.where(small, 1.0, so))
        return a * px + b * qx, a * py + b * qy, a * pz + b * qz
    return F


RULES = {
    'fit': lambda: M.fixed(fit, 'fit', 'a sphere inversion fitted to the flat rule at every point (nothing chosen)'),
    'mid25': lambda: M.fixed(mid(0.25), 'mid 0.25', 'a quarter of the way from the sphere-inversion square to the quaternion square'),
    'mid50': lambda: M.fixed(mid(0.5), 'mid 0.50', 'half way between the sphere-inversion square and the quaternion square'),
    'mid75': lambda: M.fixed(mid(0.75), 'mid 0.75', 'three quarters of the way to the quaternion square'),
    'lathe': lambda: M.fixed(Q, 'lathe', 'the quaternion square'),
}

SETS = [('c = -1', (-1.0, 0.0, 0.0)), ('rabbit', M.RABBIT), ('c = -0.75', (-0.75, 0.0, 0.0)), ('Siegel disc', M.SIEGEL)]


def alt_stay(x, y, z, c, steps):
    """P on even steps, Q on odd ones; returns the number of steps stayed (NaN or far = gone)."""
    x = np.array(x, float); y = np.array(y, float); z = np.array(z, float); n = np.zeros(x.shape, int); alive = np.ones(x.shape, bool)
    for k in range(steps):
        fx, fy, fz = (P if k % 2 == 0 else Q)(x, y, z)
        x = np.where(alive, fx + c[0], x); y = np.where(alive, fy + c[1], y); z = np.where(alive, fz + c[2], z)
        r2 = x * x + y * y + z * z; alive = alive & np.isfinite(r2) & (r2 < 1e6); n += alive
    return n


def check():
    for key in ('fit', 'mid25', 'mid50', 'mid75'):
        r = RULES[key](); print('\n==', r.name, '|', r.label)
        print('   flat check', M.flat_check(r, n=20000, steps=60))
        rng = np.random.default_rng(4); p = rng.normal(size=(3, 20000)); X, Y, Z, _ = r.step(p[0], p[1], p[2], (), 0, 0, 0, 0)
        L = (p * p).sum(0); R = np.sqrt(X * X + Y * Y + Z * Z)
        print('   length of the square over length squared: %.3f .. %.3f; all finite: %s' % ((R / L).min(), (R / L).max(), bool(np.isfinite(X + Y + Z).all())))
        for nm, c in SETS:
            n = 200000; q = rng.uniform(-1, 1, size=(3, n)) * np.array([[1.8], [1.4], [1.4]])
            a30 = (M.stay(r, q[0], q[1], q[2], c, 30) >= 30).mean(); a120 = (M.stay(r, q[0], q[1], q[2], c, 120) >= 120).mean()
            o = M.bench('oneplane'); o30 = (M.stay(o, q[0], q[1], q[2], c, 30) >= 30).mean()
            print('   %-12s share of the box inside after 30 / 120 steps: %.4f / %.4f   (one plane %.4f)' % (nm, a30, a120, o30))


def cuts():
    rules = [M.bench('oneplane'), RULES['fit'](), RULES['mid25'](), RULES['mid50'](), RULES['mid75'](), RULES['lathe']()]
    w, h, steps, pad = 300, 220, 60, 8; f = M.font(15)
    cols = [('flat cut', 0.0), ('upright cut through the x-axis', 90.0)]
    W = pad + len(SETS) * len(cols) * (w + pad); H = 30 + len(rules) * (h + 26)
    im = Image.new('RGB', (W, H), (12, 14, 20)); d = ImageDraw.Draw(im); t0 = time.time()
    for i, r in enumerate(rules):
        y = 30 + i * (h + 26); d.text((pad, y - 20), r.name + ': ' + r.label, fill=(235, 220, 170), font=f)
        for j, (sn, c) in enumerate(SETS):
            for k, (cn, ang) in enumerate(cols):
                x = pad + (j * len(cols) + k) * (w + pad)
                im.paste(Image.fromarray(M.shade(M.cut_axis(r, ang, w, h, steps, c=c), steps)), (x, y)); d.text((x + 4, y + 2), sn + ', ' + cn, fill=(150, 160, 175), font=M.font(12))
        print('cuts', r.name, '%.0f s' % (time.time() - t0)); sys.stdout.flush()
    im.save(os.path.join(HERE, 'natural-cuts.png')); print('wrote natural-cuts.png', im.size)


def solids(tag):
    cam = {'a': (0.45, 0.5, 1.0), 'top': (0.2, 1.0, 0.35)}[tag]
    rules = [M.bench('oneplane'), RULES['fit'](), RULES['mid25'](), RULES['mid50'](), RULES['mid75'](), RULES['lathe']()]
    M.julia_sheet(rules, os.path.join(HERE, 'natural-solids-%s.png' % tag), sets=[SETS[0], SETS[1]], w=420, h=315, nd=230, steps=30, cam=cam,
                  title='Rough solids, eye at %s' % (cam,))
    print('sheet', tag, 'done')


if __name__ == '__main__':
    a = sys.argv[1] if len(sys.argv) > 1 else 'check'
    if a == 'check':
        check()
    elif a == 'cuts':
        cuts()
    else:
        solids(sys.argv[2] if len(sys.argv) > 2 else 'a')

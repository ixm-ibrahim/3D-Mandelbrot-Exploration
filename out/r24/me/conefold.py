"""Round 24 scout, part 5: "two planes" with its second plane bent into a cone.

"Sphere inversions, two planes" folds space across the two slanted planes through the x-axis and then squares about
the flat plane; its second, upright plane shows a copy of the flat picture, but only when c lies on the x-axis.
Here the fold is across a CONE round the upright axis instead: a point's height angle (latitude) L is kept up to
L0 and folded back above it, so that the cone at Lc is laid onto the flat plane and the upright axis onto itself,
pointing the other way. Then the one-plane rule. Nothing in it looks at the x-axis, so the copy on the cone is there
for every c (round 23's mathematics section built the case L0 = 30 as a counterexample and nobody drew it).

    fold(L) = L                                  for |L| <= L0
            = L0 - (|L| - L0) (90 + L0)/(90 - L0)    above, with the sign of L        (L0 = 30: 90 - 2|L|)

Variants: L0 = 20, 30, 40;  'soft': the corner of the fold rounded over +-w degrees.

    python out/r24/me/conefold.py check
    python out/r24/me/conefold.py cuts
    python out/r24/me/conefold.py solids a|top
"""
import os, sys, time
import numpy as np
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, 'out', 'r21', 'lib'))
import mem as M


def P(x, y, z):
    """The one-plane rule."""
    r2 = x * x + y * y + z * z; r = np.sqrt(r2); d = r2 + z * z; f = np.where(d > 0, r2 / np.where(d > 0, d, 1.0), 0.0)
    return f * (x * x - y * y), f * 2 * x * y, f * 2 * r * z


def tent(a, L0, soft=0.0):
    """Folded latitude for a = |L| in radians."""
    k = (np.pi / 2 + L0) / (np.pi / 2 - L0)
    if soft <= 0:
        return np.where(a <= L0, a, L0 - (a - L0) * k)
    # rounded corner: slope goes from 1 to -k over [L0 - soft, L0 + soft] (a parabola), value matched at both ends
    lo, hi = L0 - soft, L0 + soft; t = np.clip((a - lo) / (2 * soft), 0, 1)
    mid = lo + 2 * soft * (t - (1 + k) * t * t / 2)            # integral of the slope 1 - (1 + k) t
    top = lo + 2 * soft * (1 - (1 + k) / 2)
    return np.where(a <= lo, a, np.where(a >= hi, top - (a - hi) * k, mid))


def fold_rule(L0deg=30.0, soft=0.0, name=None, label=None):
    L0 = np.radians(L0deg); sf = np.radians(soft)
    if soft > 0:                                             # rescale so that the pole still goes to the opposite pole
        end = float(tent(np.array([np.pi / 2]), L0, sf)[0])

    def F(x, y, z):
        r = np.sqrt(x * x + y * y + z * z); rs = np.where(r > 0, r, 1.0)
        L = np.arcsin(np.clip(z / rs, -1, 1)); a = np.abs(L)
        g = tent(a, L0, sf)
        if soft > 0:
            neg = g < 0; g = np.where(neg, g * (-(np.pi / 2) / end), g)
        L2 = np.sign(L) * g
        rho = np.hypot(x, y); ok = rho > 0; cx = np.where(ok, x / np.where(ok, rho, 1.0), 1.0); cy = np.where(ok, y / np.where(ok, rho, 1.0), 0.0)
        return P(r * np.cos(L2) * cx, r * np.cos(L2) * cy, r * np.sin(L2))
    return M.fixed(F, name or 'conefold %g' % L0deg, label or ('two planes with the second plane bent into a cone (fold at %g degrees%s)' % (L0deg, ', rounded' if soft > 0 else '')))


def cone_lat(L0deg):
    L0 = np.radians(L0deg); k = (np.pi / 2 + L0) / (np.pi / 2 - L0)
    return np.degrees(L0 + L0 / k)


VARIANTS = [(20.0, 0.0), (30.0, 0.0), (40.0, 0.0), (30.0, 8.0)]
SETS = [('c = -1', (-1.0, 0.0, 0.0)), ('rabbit', M.RABBIT), ('c = -0.75', (-0.75, 0.0, 0.0)), ('Siegel disc', M.SIEGEL)]


def check():
    for L0, sf in VARIANTS:
        r = fold_rule(L0, sf); print('\n==', r.name, '| the cone that is laid on the flat plane stands at latitude %.1f' % cone_lat(L0))
        print('   flat check', M.flat_check(r, n=20000, steps=60))
        rng = np.random.default_rng(2); p = rng.normal(size=(3, 20000)); X, Y, Z, _ = r.step(p[0], p[1], p[2], (), 0, 0, 0, 0)
        print('   length squared: largest error %.1e; finite: %s' % (np.abs(np.sqrt(X * X + Y * Y + Z * Z) - (p * p).sum(0)).max(), bool(np.isfinite(X + Y + Z).all())))
        for nm, c in SETS:
            n = 200000; q = rng.uniform(-1, 1, size=(3, n)) * np.array([[1.8], [1.4], [1.4]])
            a30 = (M.stay(r, q[0], q[1], q[2], c, 30) >= 30).mean(); a120 = (M.stay(r, q[0], q[1], q[2], c, 120) >= 120).mean()
            o = M.bench('oneplane'); o30 = (M.stay(o, q[0], q[1], q[2], c, 30) >= 30).mean(); o120 = (M.stay(o, q[0], q[1], q[2], c, 120) >= 120).mean()
            print('   %-12s share of the box inside after 30 / 120 steps: %.4f / %.4f   (one plane %.4f / %.4f)' % (nm, a30, a120, o30, o120))


def cuts():
    rules = [M.bench('oneplane'), M.bench('twoplane')] + [fold_rule(L0, sf) for L0, sf in VARIANTS]
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
    im.save(os.path.join(HERE, 'conefold-cuts.png')); print('wrote conefold-cuts.png', im.size)


def solids(tag):
    cam = {'a': (0.45, 0.5, 1.0), 'top': (0.2, 1.0, 0.35)}[tag]
    rules = [M.bench('twoplane'), fold_rule(30.0), fold_rule(30.0, 8.0), fold_rule(20.0), fold_rule(40.0)]
    M.julia_sheet(rules, os.path.join(HERE, 'conefold-solids-%s.png' % tag), sets=[SETS[0], SETS[1]], w=420, h=315, nd=230, steps=30, cam=cam,
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

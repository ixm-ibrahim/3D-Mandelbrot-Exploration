"""Round 25, section klein, part 3: the only repair there is of the paper's rule, built and measured.

The paper's rule (its first construction; bench name 'kleinian'):  v -> |v|^2 H(v / |v|) + c, where H works on
directions: inside each of three caps round the flat circle, a sphere inversion and a mirror; elsewhere the mirror.
On the flat circle H is the map h of paper2d.py, a cousin of angle doubling, so the flat cut is not the flat picture.

The repair: h and doubling are the same road map with the stops at different places. Let phi move every stop of h to
the stop of doubling with the same road (phi(h(a)) = 2 phi(a)). Re-space the directions round the upright axis with
phi before and after H:

    kfix:  direction (angle round the axis a, height above the flat plane b)  ->  ( phi(a'), b' ),
           where (a', b') = H( phi^-1(a), b );   length squared as always.

On the flat circle this is angle doubling exactly. Nothing else is touched.

    python out/r25/klein/repair.py check
    python out/r25/klein/repair.py cuts            repair-cuts.png
"""
import os, sys, time
import numpy as np
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, 'out', 'r21', 'lib')); sys.path.insert(0, HERE)
import mem as M
import paper2d as P2

_TAB = {}


def table(n=1 << 21):
    """phi on an even grid of h-angles (turns), cached on disk. KFIX_FAST=1 in the environment: every 8th entry only
    (for rough solids: the table then fits the processor's fast memory; angles good to 1e-5 instead of 1e-6)."""
    if 't' not in _TAB:
        f = os.path.join(HERE, 'phi-table.npy')
        if os.environ.get('KFIX_FAST') and os.path.exists(f):
            p = np.load(f)[::8]; _TAB['t'] = np.arange(p.size) / (p.size - 1); _TAB['p'] = p; return _TAB['t'], _TAB['p']
        if os.path.exists(f):
            p = np.load(f)
        else:
            t = np.arange(n + 1) / n; p = np.empty(n + 1)
            for a in range(0, n + 1, 1 << 18):
                p[a:a + (1 << 18)] = P2.phi(t[a:a + (1 << 18)], n=44)
            p[0] = 0.0; p[-1] = 1.0; p = np.maximum.accumulate(p); np.save(f, p)
        _TAB['t'] = np.arange(p.size) / (p.size - 1); _TAB['p'] = p
    return _TAB['t'], _TAB['p']


def K1dir(dx, dy, dz):
    """The paper's map of directions (the same as out/r14/turns/turns.py K1, without the length)."""
    ox, oy, oz = dx, dy, dz
    for ax, ay in ((0.5, np.sqrt(3) / 2), (-1.0, 0.0), (0.5, -np.sqrt(3) / 2)):
        m = (dx * ax + dy * ay) > 0.5; sx, sy = 2 * ax, 2 * ay; ux, uy, uz = dx - sx, dy - sy, dz; k = 3.0 / (ux * ux + uy * uy + uz * uz)
        ox = np.where(m, sx + k * ux, ox); oy = np.where(m, sy + k * uy, oy); oz = np.where(m, k * uz, oz)
    return ox, -oy, oz


def kfix(x, y, z):
    t, p = table()
    r2 = x * x + y * y + z * z; r = np.sqrt(r2); ok = r > 0; rs = np.where(ok, r, 1.0)
    rho = np.hypot(x, y); a = np.mod(np.arctan2(y, x) / (2 * np.pi), 1.0)
    ah = np.interp(a, p, t) * 2 * np.pi                                       # the true angle -> the paper's angle
    hx, hy, hz = K1dir(rho / rs * np.cos(ah), rho / rs * np.sin(ah), z / rs)
    a2 = np.interp(np.mod(np.arctan2(hy, hx) / (2 * np.pi), 1.0), t, p) * 2 * np.pi   # and back
    q = np.hypot(hx, hy)
    X, Y, Z = r2 * q * np.cos(a2), r2 * q * np.sin(a2), r2 * hz
    flat = z == 0                                                             # on the flat plane the rule IS z^2; say so exactly (the table is good to 1e-6 only)
    return np.where(flat, x * x - y * y, X), np.where(flat, 2 * x * y, Y), np.where(flat, 0.0, Z)


def kfix_table_only(x, y, z):
    """The same without the exact line for the flat plane (to show what the table alone gives)."""
    e = 1e-300
    return kfix(x, y, np.where(z == 0, e, z))


RULES = {
    'paper': lambda: M.bench('kleinian'),
    'kfix': lambda: M.fixed(kfix, 'paper rule, re-spaced', 'the paper\'s rule with the directions re-spaced so that the flat cut is exact'),
}
SETS = [('c = -1', (-1.0, 0.0, 0.0)), ('rabbit', M.RABBIT), ('c = -0.75', (-0.75, 0.0, 0.0)), ('Siegel disc', M.SIEGEL)]


def check():
    t, p = table(); print('table', p.size, 'steps of phi: largest %.2e' % np.diff(p).max())
    r = RULES['kfix'](); print('flat check, kfix          :', M.flat_check(r, n=20000, steps=60))
    print('flat check, table only    :', M.flat_check(M.fixed(kfix_table_only, 'kfix-table'), n=20000, steps=60))
    rng = np.random.default_rng(4); q = rng.normal(size=(3, 20000)); X, Y, Z = kfix(q[0], q[1], q[2])
    print('all finite:', bool(np.isfinite(X + Y + Z).all()), ' length kept: %.2e' % np.abs(np.sqrt(X * X + Y * Y + Z * Z) / (q * q).sum(0) - 1).max())
    # is the rule the same just off the flat plane as on it? (a jump there would be a tear)
    a = rng.uniform(0, 2 * np.pi, 20000); x, y = np.cos(a), np.sin(a)
    for h in (1e-2, 1e-4, 1e-6):
        X, Y, Z = kfix(x, y, np.full_like(x, h)); print('   height %.0e above the flat circle: the square is at most %.2e from the flat square' % (h, np.sqrt((X - (x * x - y * y)) ** 2 + (Y - 2 * x * y) ** 2).max()))
    # how unevenly the re-spacing squeezes: neighbouring directions on the flat circle, before and after
    for n in (1 << 8, 1 << 12, 1 << 16, 1 << 20):
        L = np.diff(np.interp(np.arange(n + 1) / n, p, t)); print('   the circle cut into %7d equal arcs: re-spaced, the longest is %.0f times the shortest' % (n, L.max() / max(L.min(), 1e-300)))
    for nm, c in SETS:
        n = 200000; q = rng.uniform(-1, 1, size=(3, n)) * np.array([[1.8], [1.4], [1.4]])
        print('   %-12s share of the box inside after 30 steps: kfix %.4f, paper %.4f, one plane %.4f' % (
            nm, (M.stay(r, q[0], q[1], q[2], *c, 30) >= 30).mean(), (M.stay(RULES['paper'](), q[0], q[1], q[2], *c, 30) >= 30).mean(), (M.stay(M.bench('oneplane'), q[0], q[1], q[2], *c, 30) >= 30).mean()))


def cuts():
    rules = [M.bench('oneplane'), RULES['paper'](), RULES['kfix']()]
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
    im.save(os.path.join(HERE, 'repair-cuts.png')); print('wrote repair-cuts.png', im.size)


if __name__ == '__main__':
    {'check': check, 'cuts': cuts}[sys.argv[1] if len(sys.argv) > 1 else 'check']()

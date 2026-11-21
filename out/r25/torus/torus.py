"""Round 25, section 'torus': rules built on the doughnut picture of space.

Space (with the point at infinity) is the sphere of unit quaternions w1 + w2 j seen through one sphere inversion:
    w1 = 2 (x + i y) / (1 + |v|^2),   w2 = ((1 - |v|^2) + 2 i z) / (1 + |v|^2).
Two linked circles: the RING (the flat unit circle, w2 = 0) and the AXIS (the upright axis with infinity, w1 = 0).
Every upright half-plane through the axis is a disc with the ring's point in its middle:
    zeta = rho + i z (rho = distance from the axis),   d = (zeta - 1) / (zeta + 1),   d = r e^(i sigma).
    d = 0 the ring, |d| = 1 the axis, d = -1 the origin, d = +1 infinity, d real = the flat plane.
    sigma = the angle ROUND THE RING (sigma const = a sphere through the unit circle: a 'page of the book').
    r const = a doughnut round the ring (r = tan(eta/2), eta = the angle from the ring on the quaternion sphere;
    r = tan(22.5 deg) is the Clifford torus).  D = 2 artanh r = the distance from the ring in the half-plane's own
    (hyperbolic) geometry.  phi = the longitude round the axis.
The flat rule z -> z^2 in these words:  phi -> 2 phi,  D -> 2 D  (r -> 2 r / (1 + r^2)),  sigma stays 0 or 180.

Rules (each returns the 'square' without c):
    book    phi -> 2 phi, D -> 2 D, sigma kept: z^2 done on every sphere through the unit circle (page by page).
    ring2   phi -> 2 phi, D -> 2 D, sigma -> 2 sigma: the angle round the ring doubled too.
    clif    the Clifford doubling (w1, w2) -> (w1^2, w2^2) / length: both angles doubled, the Clifford torus stays.
    tor3    phi -> 2 phi, D -> 2 D, sigma -> 3 sigma (the smallest winding round the ring that keeps both sides of
            the flat circle on their own side).
    ring3   wind 3 times round the ring (D and phi kept), THEN the one-plane square.   ring3b: the other order.
    hopf    not a rule v -> F(v) + c but the honest quaternion object: the unit quaternion w1 + w2 j is sent to
            (w1^2, w2^2 + c w1^2) / length.  Its bodies are all points whose number w2 / w1 stays under z^2 + c
            (every point of the flat picture becomes a whole circle; c = 0 gives the Clifford doughnut).

    python out/r25/torus/torus.py check | cuts | solids a|top [rules...] | zero
"""
import os, sys, time
import numpy as np
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, 'out', 'r21', 'lib'))
import mem as M

np.seterr(all='ignore')


# ---------------------------------------------------------------- coordinates
def to_tor(x, y, z):
    rho = np.hypot(x, y); ok = rho > 0; rs = np.where(ok, rho, 1.0)
    c1 = np.where(ok, x / rs, 1.0); s1 = np.where(ok, y / rs, 0.0)
    den = (rho + 1) ** 2 + z * z
    return (rho * rho + z * z - 1) / den, 2 * z / den, c1, s1          # d = dr + i di, cos phi, sin phi


def from_tor(dr, di, c1, s1):
    den = (1 - dr) ** 2 + di * di                                       # 0 at infinity: inf / nan = escaped
    rho = np.maximum((1 - dr * dr - di * di) / den, 0.0); z = 2 * di / den
    return rho * c1, rho * s1, z


def unit(dr, di):
    r = np.hypot(dr, di); ok = r > 0; rs = np.where(ok, r, 1.0)
    return r, np.where(ok, dr / rs, 1.0), np.where(ok, di / rs, 0.0)


def P(x, y, z):
    """The one-plane square (longitude doubled, Mercator latitude doubled, length squared)."""
    r2 = x * x + y * y + z * z; r = np.sqrt(r2); d = r2 + z * z; f = np.where(d > 0, r2 / np.where(d > 0, d, 1.0), 0.0)
    return f * (x * x - y * y), f * 2 * x * y, f * 2 * r * z


def snap(F):
    """Take rounding out of the flat plane: where z == 0 exactly, use the plain complex square."""
    def G(x, y, z):
        X, Y, Z = F(x, y, z); fl = z == 0
        return np.where(fl, x * x - y * y, X), np.where(fl, 2 * x * y, Y), np.where(fl, 0.0, Z)
    return G


# ---------------------------------------------------------------- the rules
def book(x, y, z):
    dr, di, c1, s1 = to_tor(x, y, z); s = 2.0 / (1.0 + dr * dr + di * di)
    return from_tor(s * dr, s * di, c1 * c1 - s1 * s1, 2 * c1 * s1)


def ringk(k):
    """phi -> 2 phi, D -> 2 D, sigma -> k sigma."""
    def F(x, y, z):
        dr, di, c1, s1 = to_tor(x, y, z); r, ur, ui = unit(dr, di); R = 2 * r / (1 + r * r)
        w = (ur + 1j * ui) ** k
        return from_tor(R * w.real, R * w.imag, c1 * c1 - s1 * s1, 2 * c1 * s1)
    return F


def clif(x, y, z):
    """(w1, w2) -> (w1^2, w2^2) / length: tan(eta) squared, both angles doubled."""
    dr, di, c1, s1 = to_tor(x, y, z); r, ur, ui = unit(dr, di)
    T = 2 * r / np.maximum(1 - r * r, 1e-300); T2 = T * T
    R = np.where(T2 > 1e-12, (np.sqrt(1 + T2 * T2) - 1) / np.where(T2 > 1e-12, T2, 1.0), T2 / 2)
    return from_tor(R * (ur * ur - ui * ui), R * 2 * ur * ui, c1 * c1 - s1 * s1, 2 * c1 * s1)


def wind(k):
    """Wind k times round the ring; the distance from the ring and the longitude are kept."""
    def W(x, y, z):
        dr, di, c1, s1 = to_tor(x, y, z); r, ur, ui = unit(dr, di); w = (ur + 1j * ui) ** k
        return from_tor(r * w.real, r * w.imag, c1, s1)
    return W


W3 = wind(3)


def ring3(x, y, z):
    return P(*W3(x, y, z))


def ring3b(x, y, z):
    return W3(*P(x, y, z))


def hopf_value(x, y, z):
    """The number w2 / w1 of the unit quaternion behind the point (infinite on the upright axis)."""
    return ((1 - x * x - y * y - z * z) + 2j * z) / (2 * (x + 1j * y))


def _hopf_step(x, y, z, st, k, cx, cy, cz):
    if k == 0:
        Z = hopf_value(x, y, z); Z2 = Z * Z
        return Z2.real, Z2.imag, 0.0 * x, st
    return x * x - y * y, 2 * x * y, 0.0 * x, st


RULES = {
    'oneplane': lambda: M.fixed(P, 'one plane', 'the baseline (for comparison)'),
    'book': lambda: M.fixed(snap(book), 'book', 'z^2 done on every sphere through the unit circle (angle round the ring kept)'),
    'ring2': lambda: M.fixed(ringk(2), 'ring2', 'the angle round the ring doubled as well'),
    'clif': lambda: M.fixed(clif, 'clif', 'the Clifford doubling: both angles doubled, the Clifford doughnut stays'),
    'tor3': lambda: M.fixed(snap(ringk(3)), 'tor3', 'longitude doubled, the angle round the ring tripled'),
    'ring3': lambda: M.fixed(snap(ring3), 'ring3', 'wound three times round the flat circle, then one plane'),
    'ring3b': lambda: M.fixed(snap(ring3b), 'ring3b', 'one plane, then wound three times round the flat circle'),
    'hopf': lambda: M.Rule('hopf', 'the quaternion (Hopf) doughnut: every flat point becomes a circle', _hopf_step, init=lambda n: ()),
}
RAW = {'book': book, 'tor3': ringk(3), 'ring3': ring3, 'ring3b': ring3b}
SETS = [('c = -1', (-1.0, 0.0, 0.0)), ('rabbit', M.RABBIT), ('c = -0.75', (-0.75, 0.0, 0.0)), ('Siegel disc', M.SIEGEL)]
HALF = {'hopf': 3.9}                                                    # the hopf bodies reach out to 3.6


# ---------------------------------------------------------------- numbers
def check():
    rng = np.random.default_rng(4)
    print('-- obstacle 2 (book): a far point is only pushed to the top of its own sphere through the unit circle')
    for R in (10.0, 100.0, 1000.0):
        e = np.radians(rng.uniform(5, 85, 4000)); a = rng.uniform(0, 2 * np.pi, 4000)
        x, y, z = R * np.cos(e) * np.cos(a), R * np.cos(e) * np.sin(a), R * np.sin(e)
        X, Y, Z = book(x, y, z); L = np.sqrt(X * X + Y * Y + Z * Z)
        q = L * np.sin(e) / R
        print('   |v| = %6g: |book(v)| * sin(elevation) / |v| = %.4f .. %.4f (1 = linear growth; z^2 would give %g); distance from the axis after: max %.2e'
              % (R, q.min(), q.max(), R, np.hypot(X, Y).max()))
    print('-- book: height above the 2-cycle of c = -1 after one round (start (0.02, 0.01, h))')
    for h in (1e-4, 1e-3, 1e-2):
        x, y, z = np.array([0.02]), np.array([0.01]), np.array([h])
        for _ in range(2):
            x, y, z = book(x, y, z); x = x - 1.0
        print('   h = %g -> %.6g (times %.3f)' % (h, z[0], z[0] / h))
    for key in ('book', 'ring2', 'clif', 'tor3', 'ring3', 'ring3b', 'hopf'):
        r = RULES[key](); print('\n==', r.name, '|', r.label)
        f = M.flat_check(r, n=20000, steps=60); print('   flat check', f)
        if key in RAW:
            f2 = M.flat_check(M.fixed(RAW[key], key), n=20000, steps=60); print('   flat check without the rounding guard', f2)
        if key != 'hopf':
            p = rng.normal(size=(3, 20000)); X, Y, Z, _ = r.step(p[0], p[1], p[2], (), 0, 0, 0, 0)
            L = (p * p).sum(0); Rr = np.sqrt(X * X + Y * Y + Z * Z); fin = np.isfinite(X + Y + Z)
            print('   finite: %.4f of a test batch; length of the square over length squared: %.3g .. %.3g' % (fin.mean(), np.nanmin(Rr / L), np.nanmax(Rr / L)))
        hw = HALF.get(key, 1.8)
        for nm, c in [('c = 0', (0.0, 0.0, 0.0))] + SETS[:2]:
            n = 200000; q = rng.uniform(-1, 1, size=(3, n)) * np.array([[hw], [hw * 0.78], [hw * 0.78]])
            a30 = (M.stay(r, q[0], q[1], q[2], *c, 30) >= 30).mean(); a120 = (M.stay(r, q[0], q[1], q[2], *c, 120) >= 120).mean()
            o30 = (M.stay(RULES['oneplane'](), q[0], q[1], q[2], *c, 30) >= 30).mean()
            print('   %-8s share of the box inside after 30 / 120 steps: %.4f / %.4f   (one plane %.4f)' % (nm, a30, a120, o30))
        sys.stdout.flush()


# ---------------------------------------------------------------- pictures
def cuts(keys=None, name='cuts.png'):
    keys = keys or ['oneplane', 'book', 'tor3', 'ring3', 'ring3b', 'clif', 'hopf']
    sets = [('c = 0', (0.0, 0.0, 0.0))] + SETS[:2]
    w, h, steps, pad = 300, 220, 60, 8; f = M.font(15)
    cols = [('flat cut', 0.0), ('upright cut through the x-axis', 90.0)]
    W = pad + len(sets) * len(cols) * (w + pad); H = 30 + len(keys) * (h + 26)
    im = Image.new('RGB', (W, H), (12, 14, 20)); d = ImageDraw.Draw(im); t0 = time.time()
    for i, key in enumerate(keys):
        r = RULES[key](); y = 30 + i * (h + 26); d.text((pad, y - 20), r.name + ': ' + r.label, fill=(235, 220, 170), font=f)
        hw = HALF.get(key, 1.8) if key != 'ring3' else 1.8
        box = (-hw, hw, -hw * h / w, hw * h / w)
        for j, (sn, c) in enumerate(sets):
            for k, (cn, ang) in enumerate(cols):
                x = pad + (j * len(cols) + k) * (w + pad)
                im.paste(Image.fromarray(M.shade(M.cut_axis(r, ang, w, h, steps, c=c, box=box), steps)), (x, y))
                d.text((x + 4, y + 2), '%s, %s (half width %.1f)' % (sn, cn, hw), fill=(150, 160, 175), font=M.font(12))
        print('cuts', r.name, '%.0f s' % (time.time() - t0)); sys.stdout.flush()
    im.save(os.path.join(HERE, name)); print('wrote', name, im.size)


def solids(tag, keys, sets, name, w=340, h=255, nd=170, steps=28):
    cam = {'a': (0.45, 0.5, 1.0), 'top': (0.2, 1.0, 0.35)}[tag]; pad = 10; t0 = time.time()
    W = pad + len(sets) * (w + pad); H = 56 + len(keys) * (h + 36)
    im = Image.new('RGB', (W, H), (12, 14, 20)); d = ImageDraw.Draw(im)
    d.text((pad, 10), 'Rough solids, eye %s (%d blocks deep, %d steps)' % ('in front' if tag == 'a' else 'above', nd, steps), fill=(240, 240, 245), font=M.font(22))
    for i, key in enumerate(keys):
        r = RULES[key](); y = 56 + i * (h + 36); d.text((pad, y), '%s: %s' % (r.name, r.label), fill=(235, 220, 170), font=M.font(17))
        for j, (sn, c) in enumerate(sets):
            dep, px = M.solid(r, c, w, h, nd, steps, half_w=HALF.get(key, 1.75), cam=cam); x = pad + j * (w + pad)
            im.paste(Image.fromarray(M.shade_solid(dep, px)), (x, y + 26)); d.text((x + 6, y + 30), sn, fill=(150, 160, 175), font=M.font(13))
            print('solid', tag, r.name, sn, '%.0f s' % (time.time() - t0), 'blocks hit: %d' % int(np.isfinite(dep).sum())); sys.stdout.flush()
    im.save(os.path.join(HERE, name)); print('wrote', name, im.size)


def row(tag, key, steps=60, w=340, h=255, nd=170):
    """One rule, three sets (c = 0, c = -1, rabbit), one eye: saved as a strip to be stacked by 'sheet'."""
    cam = {'a': (0.45, 0.5, 1.0), 'top': (0.2, 1.0, 0.35)}[tag]; pad = 10; t0 = time.time()
    sets = [('c = 0', (0.0, 0.0, 0.0))] + SETS[:2]; r = RULES[key]()
    im = Image.new('RGB', (pad + len(sets) * (w + pad), h + 36), (12, 14, 20)); d = ImageDraw.Draw(im)
    d.text((pad, 0), '%s: %s' % (r.name, r.label), fill=(235, 220, 170), font=M.font(17))
    for j, (sn, c) in enumerate(sets):
        hw = HALF.get(key, 1.75)
        dep, px = M.solid(r, c, w, h, nd, steps, half_w=hw, cam=cam); x = pad + j * (w + pad)
        im.paste(Image.fromarray(M.shade_solid(dep, px)), (x, 26)); d.text((x + 6, 30), '%s (picture is %.1f wide)' % (sn, 2 * hw), fill=(150, 160, 175), font=M.font(13))
        print('solid', tag, r.name, sn, '%.0f s' % (time.time() - t0), 'pixels hit: %d of %d' % (int(np.isfinite(dep).sum()), dep.size)); sys.stdout.flush()
    im.save(os.path.join(HERE, 'row-%s-%s.png' % (tag, key)))


def sheet(tag, keys, name, steps=60):
    rows = [Image.open(os.path.join(HERE, 'row-%s-%s.png' % (tag, k))) for k in keys]
    W = max(r.size[0] for r in rows); H = 50 + sum(r.size[1] for r in rows)
    im = Image.new('RGB', (W, H), (12, 14, 20)); d = ImageDraw.Draw(im)
    d.text((10, 10), 'Rough solids, eye %s (170 blocks deep, %d steps)' % ('in front' if tag == 'a' else 'above', steps), fill=(240, 240, 245), font=M.font(22))
    y = 50
    for r in rows:
        im.paste(r, (0, y)); y += r.size[1]
    im.save(os.path.join(HERE, name)); print('wrote', name, im.size)


if __name__ == '__main__':
    a = sys.argv[1] if len(sys.argv) > 1 else 'check'
    if a == 'check':
        check()
    elif a == 'cuts':
        cuts()
    elif a == 'row':
        row(sys.argv[2], sys.argv[3])
    elif a == 'sheet':
        sheet(sys.argv[2], sys.argv[3].split(','), sys.argv[4])

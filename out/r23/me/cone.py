"""Scout for round 23: the "cone rule" (mine).

Idea. A rule |v|^2 * G(direction) + c keeps shapes (stretches by the same 2|v| in all three directions) at a place only
if G stretches the sphere of directions by exactly 2 there. On the flat plane that means: longitude doubled. On the
cone 60 degrees above the flat plane, where a circle of longitude is HALF as long as the equator (cos 60 = 1/2), it
means: longitude kept once round, and the cone laid onto the flat plane. That cone is the flat picture rolled up so
that z and -z touch. So: a direction map that is w^2 beside the equator and lays the two 60-degree cones onto the
equator once round. As a formula in the stereographic coordinate w (|w| = 1 the equator, north = infinity):

    R_t(w) = (w^3 + t) / (w (1 + t w^3)),   t = tan 15 degrees = 2 - sqrt 3      (t = 0 is w^2, the one-plane rule)

R_t is angle-true on the whole sphere, covers it 4 times, never folds, sends north pole <-> south pole, and near
|w| = 1/t = tan 75 (latitude 60) it is 1/(t w): stretch (t + 1/t)/2 = 2. It is NOT exact doubling on the equator,
so beside the equator it is blended into w^2:  W = w^2 * ((1 + t w^-3)/(1 + t w^3))^chi(mu),  chi = 0 with slope 0 at
mu = 0 (mu = Mercator latitude), chi = 1 from |mu| = mu1 on.

    python out/r23/me/cone.py check            numbers about the direction map and the flat-plane check
    python out/r23/me/cone.py cuts             cuts of the Julia sets (fast)
    python out/r23/me/cone.py solids [sets]    rough solids beside one plane and along
"""
import os, sys, time
import numpy as np
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, 'out', 'r21', 'lib'))
import mem as M

T15 = 2.0 - np.sqrt(3.0)


def cone_dir(x, y, z, t=T15, mu1=0.4, blend=True):
    """The direction map on unit vectors given as (x, y, z) with any length r > 0. Returns the unit vector G."""
    r = np.sqrt(x * x + y * y + z * z); rs = np.where(r > 0, r, 1.0)
    Zs = np.clip(z / rs, -1 + 1e-15, 1 - 1e-15); mu = np.arctanh(Zs)
    north = z > 0
    # the small one of w and 1/w, so nothing overflows: south w = (x + iy)/(r - z), north u = 1/w = (x - iy)/(r + z)
    den = np.where(north, rs + z, rs - z); den = np.where(den > 0, den, 1.0)
    s = (x + 1j * np.where(north, -y, y)) / den                       # |s| <= 1
    s3 = s * s * s
    N = np.where(north, s * (1 + t * s3), s3 + t)                     # R_t = N / D
    D = np.where(north, s3 + t, s * (1 + t * s3))
    if blend:
        inb = np.abs(mu) < mu1
        if inb.any():
            sa = np.where(inb, s, 1.0); w = np.where(north, 1.0 / np.where(np.abs(sa) > 0, sa, 1.0), sa)
            q = np.clip(np.abs(mu) / mu1, 0, 1); chi = q * q * (3 - 2 * q)
            w3 = w * w * w
            W = w * w * np.exp(chi * (np.log(1 + t / w3) - np.log(1 + t * w3)))
            N = np.where(inb, W, N); D = np.where(inb, 1.0 + 0j, D)
    n2, d2 = np.abs(N) ** 2, np.abs(D) ** 2; tot = n2 + d2; tot = np.where(tot > 0, tot, 1.0)
    xy = 2 * N * np.conj(D) / tot
    return xy.real, xy.imag, (n2 - d2) / tot


def cone_rule(t=T15, mu1=0.4, blend=True, name=None, label=None):
    def F(x, y, z):
        r2 = x * x + y * y + z * z
        X, Y, Z = cone_dir(x, y, z, t, mu1, blend)
        ok = r2 > 0
        return np.where(ok, r2 * X, 0.0), np.where(ok, r2 * Y, 0.0), np.where(ok, r2 * Z, 0.0)
    return M.fixed(F, name or 'cone', label or 'cone rule, t = %.4f' % t)


RULES = {
    'conep': lambda: cone_rule(T15, name='cone+', label='cone rule: the rolled-up copy opens toward +x'),
    'conem': lambda: cone_rule(-T15, name='cone-', label='cone rule: the rolled-up copy opens toward -x'),
    'coneraw': lambda: cone_rule(T15, blend=False, name='cone raw', label='the angle-true map R_t alone (flat plane NOT exact)'),
}


def sphere_numbers(t, blend=True, mu1=0.4, n=1400):
    """Degree, folded share, stretches of the direction map."""
    lat = (np.arange(n) + 0.5) / n * np.pi - np.pi / 2; lon = (np.arange(2 * n) + 0.5) / (2 * n) * 2 * np.pi
    LA, LO = np.meshgrid(lat, lon, indexing='ij'); h = 1e-5

    def G(la, lo):
        return np.stack(cone_dir(np.cos(la) * np.cos(lo), np.cos(la) * np.sin(lo), np.sin(la), t, mu1, blend), -1)
    g = G(LA, LO); a = (G(LA + h, LO) - G(LA - h, LO)) / (2 * h); b = (G(LA, LO + h) - G(LA, LO - h)) / (2 * h) / np.cos(LA)[..., None]
    det = (np.cross(a, b) * g).sum(-1); dA = np.cos(LA) * (np.pi / n) * (np.pi / n)
    aa, bb, ab = (a * a).sum(-1), (b * b).sum(-1), (a * b).sum(-1)
    tr, dd = aa + bb, np.sqrt(np.maximum((aa - bb) ** 2 + 4 * ab * ab, 0)); s1, s2 = np.sqrt((tr + dd) / 2), np.sqrt(np.maximum((tr - dd) / 2, 0))
    out = {'covers (signed)': float((det * dA).sum() / (4 * np.pi)), 'covers (unsigned)': float((np.abs(det) * dA).sum() / (4 * np.pi)),
           'folded share of directions': float((dA * (det < 0)).sum() / dA.sum())}
    rows = []
    for deg in (0, 5, 10, 15, 20, 25, 30, 40, 50, 60, 70, 80, 88):
        i = int(np.argmin(np.abs(np.degrees(lat) - deg)))
        rows.append((deg, float(s1[i].min()), float(s1[i].max()), float(s2[i].min()), float(s2[i].max()), float(np.degrees(np.arcsin(np.clip(g[i, :, 2], -1, 1))).min()), float(np.degrees(np.arcsin(np.clip(g[i, :, 2], -1, 1))).max())))
    # where the northern hemisphere is laid onto the equator: sign changes of the image height along each meridian
    zimg = g[..., 2]; nh = lat > np.radians(3.0); found = []
    for j in range(0, 2 * n, max(1, n // 36)):
        col = zimg[nh, j]; la = lat[nh]; k = np.nonzero(np.sign(col[1:]) != np.sign(col[:-1]))[0]
        for kk in k:
            f = col[kk] / (col[kk] - col[kk + 1]); la0 = la[kk] + f * (la[kk + 1] - la[kk]); ii = np.nonzero(nh)[0][kk]
            found.append((float(np.degrees(lon[j])), float(np.degrees(la0)), float(s1[ii, j]), float(s2[ii, j]), float(np.degrees(np.arctan2(g[ii, j, 1], g[ii, j, 0])))))
    return out, rows, found


def check():
    for nm, t, bl in (('one plane (t = 0)', 0.0, True), ('cone+ blended', T15, True), ('cone- blended', -T15, True), ('R_t alone', T15, False)):
        out, rows, found = sphere_numbers(t, bl)
        print('\n== %s' % nm); print('  ', out)
        print('   latitude: larger stretch min..max | smaller stretch min..max | image latitude min..max')
        for r in rows:
            print('   %4d: %6.3f..%6.3f | %6.3f..%6.3f | %7.2f..%7.2f' % r)
        if found:
            la = np.array([f[1] for f in found]); s1 = np.array([f[2] for f in found]); s2 = np.array([f[3] for f in found])
            print('   northern directions laid onto the equator: %d crossings on %d meridians; latitude %.2f..%.2f; stretches there %.3f..%.3f and %.3f..%.3f'
                  % (len(found), len(set(f[0] for f in found)), la.min(), la.max(), s2.min(), s2.max(), s1.min(), s1.max()))
            print('   (longitude -> image longitude) samples:', ', '.join('%.0f->%.0f' % (f[0], f[4]) for f in found[:12]))
    for key in ('conep', 'conem'):
        r = RULES[key](); print('\nflat check', r.name, M.flat_check(r, n=20000, steps=60))
    # length squared?
    rng = np.random.default_rng(1); p = rng.normal(size=(3, 5000)); r = RULES['conep']()
    X, Y, Z, _ = r.step(p[0], p[1], p[2], (), 0, 0, 0, 0); print('length squared: largest error %.2e' % np.abs(np.sqrt(X * X + Y * Y + Z * Z) - (p * p).sum(0)).max())


def cuts():
    rules = [M.bench('oneplane'), M.bench('along'), RULES['conep'](), RULES['conem']()]
    sets = [('basilica', (-1.0, 0.0, 0.0)), ('rabbit', M.RABBIT), ('San Marco', (-0.75, 0.0, 0.0))]
    w, h, steps, pad = 360, 260, 60, 8; f = M.font(15)
    cols = [('flat cut', 0.0), ('upright cut (through the x-axis)', 90.0)]
    W = pad + len(sets) * len(cols) * (w + pad); H = 30 + len(rules) * (h + 26)
    im = Image.new('RGB', (W, H), (12, 14, 20)); d = ImageDraw.Draw(im); t0 = time.time()
    for i, r in enumerate(rules):
        y = 30 + i * (h + 26); d.text((pad, y - 20 if i == 0 else y - 20), r.name + ': ' + r.label, fill=(235, 220, 170), font=f)
        for j, (sn, c) in enumerate(sets):
            for k, (cn, ang) in enumerate(cols):
                x = pad + (j * len(cols) + k) * (w + pad)
                im.paste(Image.fromarray(M.shade(M.cut_axis(r, ang, w, h, steps, c=c), steps)), (x, y)); d.text((x + 4, y + 2), sn + ', ' + cn, fill=(150, 160, 175), font=M.font(12))
        print('cuts', r.name, '%.0f s' % (time.time() - t0)); sys.stdout.flush()
    im.save(os.path.join(HERE, 'cone-cuts.png')); print('wrote cone-cuts.png', im.size)


def solids(which):
    rules = [M.bench('oneplane'), M.bench('along'), RULES['conep'](), RULES['conem']()]
    allsets = {'basilica': ('basilica, c = -1', (-1.0, 0.0, 0.0)), 'rabbit': ('rabbit', M.RABBIT), 'sanmarco': ('San Marco, c = -0.75', (-0.75, 0.0, 0.0)),
               'siegel': ('Siegel disc', M.SIEGEL), 'dendrite': ('dendrite, c = i', (0.0, 1.0, 0.0))}
    sets = [allsets[s] for s in (which or ['basilica', 'rabbit'])]
    for cam, tag in (((0.45, 0.5, 1.0), 'a'), ((0.2, 1.0, 0.35), 'top')):
        M.julia_sheet(rules, os.path.join(HERE, 'cone-solids-%s-%s.png' % ('-'.join(which or ['basilica', 'rabbit']), tag)), sets=sets, w=420, h=315, nd=260, steps=30, cam=cam,
                      title='Rough solids, eye at %s' % (cam,))
        print('sheet', tag, 'done'); sys.stdout.flush()


if __name__ == '__main__':
    a = sys.argv[1] if len(sys.argv) > 1 else 'check'
    {'check': check, 'cuts': cuts}.get(a, lambda: solids(sys.argv[2:]))()

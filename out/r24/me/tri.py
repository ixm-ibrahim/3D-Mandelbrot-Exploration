"""Round 24 scout, part 2: the whole range of the "second new try", from one plane to the even-spacing end.

The second new try is the direction map R_t(w) = (w^3 + t) / (w (1 + t w^3)) with t = -0.268, blended into plain
doubling beside the flat plane. t = 0 is the one-plane rule. t = -1/2 is the direction map that pulls neighbouring
directions apart by exactly 2 everywhere (multiplication by 2 on a pillow made of two flat triangles; measured in
dirs.py). Rules here:

    cone(t)      R_t blended into doubling beside the flat plane (the scout of round 23, any t)
    tri          the t = -1/2 end done exactly: directions <-> two flat triangles ("kite" layout, below), flat
                 position doubled, back. Exact doubling on the flat plane with no blend.

Kite layout. The flat triangle has corners V0, V1, V2 (side 1); they are the directions at longitude 0, 120, 240 on
the flat plane's circle, the triangle is the upper half of the sphere, its mirror image the lower half. Each corner
owns the part of the triangle nearest to it (a kite) and the part of the half sphere within 60 degrees of longitude.
In the kite: flat polar coordinates (rho, beta) about the corner, beta = 0..60 degrees measured from the edge; on the
sphere polar coordinates (sigma, phi) about the corner's direction, phi = 0..180 measured from the flat circle.
    phi = 3 beta,   sigma / sigma_max(phi) = rho / rho_max(beta)
so the 60-degree corner is opened like a fan to 180 degrees, an edge is laid on the flat circle at constant speed,
and beside the edge heights are 3 times flat distances, the same all along (so the rule is plain doubling there).

    python out/r24/me/tri.py check
    python out/r24/me/tri.py cuts
    python out/r24/me/tri.py solids [a|top]
"""
import os, sys, time
import numpy as np
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, 'out', 'r21', 'lib')); sys.path.insert(0, os.path.join(ROOT, 'out', 'r23', 'me'))
import mem as M
import cone as C

S3 = np.sqrt(3.0); T3 = 2 * np.pi / 3; E2 = np.exp(1j * np.pi / 3)
VERT = np.array([0.0 + 0j, 1.0 + 0j, E2])


def _smax(phi):
    return np.arctan2(S3, np.abs(np.cos(phi)))


def _rmax(beta):
    return 0.5 / np.cos(np.minimum(beta, np.pi / 3 - beta))


def to_flat(x, y, z):
    """Unit direction -> position u in the reference triangle (0, 1, e^(i 60)) and the flag 'lower half'."""
    south = z < 0; za = np.abs(z)
    lon = np.arctan2(y, x); k = np.round(lon / T3); l = lon - k * T3; k = np.mod(k, 3).astype(int)
    rxy = np.sqrt(x * x + y * y); dx = rxy * np.cos(l); dy = rxy * np.sin(l)
    sig = np.arccos(np.clip(dx, -1.0, 1.0)); phi = np.arctan2(za, dy); beta = phi / 3
    rho = _rmax(beta) * sig / _smax(phi)
    return VERT[k] + rho * np.exp(1j * (T3 * k + beta)), south


def from_flat(u, south):
    """Position in the reference triangle and the flag -> unit direction."""
    b2 = u.imag / (S3 / 2); b1 = u.real - b2 / 2; b0 = 1 - b1 - b2
    k = np.argmax(np.stack([b0, b1, b2]), axis=0)
    d = u - VERT[k]; rho = np.abs(d)
    ang = np.mod(np.angle(d) - T3 * k + np.pi, 2 * np.pi) - np.pi
    beta = np.clip(ang, 0.0, np.pi / 3); phi = 3 * beta
    sig = _smax(phi) * rho / _rmax(beta)
    dx = np.cos(sig); dy = np.sin(sig) * np.cos(phi); dz = np.sin(sig) * np.sin(phi)
    a = T3 * k; ca, sa = np.cos(a), np.sin(a)
    return dx * ca - dy * sa, dx * sa + dy * ca, np.where(south, -dz, dz)


def mult(u, south, n=2):
    """Multiply the flat position by n and bring it back to (reference triangle, flag)."""
    U = n * np.where(south, np.conj(u), u)
    b = U.imag / (S3 / 2); a = U.real - b / 2
    i = np.floor(a); j = np.floor(b); fa = a - i; fb = b - j
    up = (fa + fb) < 1
    k0 = np.mod(i - j, 3).astype(int)
    wa = np.where(up, 1 - fa - fb, fa + fb - 1)       # weight of the corner of class k0
    wb = np.where(up, fa, 1 - fb)                     # class k0 + 1
    wc = np.where(up, fb, 1 - fa)                     # class k0 + 2
    st = np.stack([wa, wb, wc])
    w1 = np.take_along_axis(st, np.mod(1 - k0, 3)[None], 0)[0]
    w2 = np.take_along_axis(st, np.mod(2 - k0, 3)[None], 0)[0]
    return w1 + w2 * E2, ~up


def tri_dir(x, y, z, n=2):
    r = np.sqrt(x * x + y * y + z * z); rs = np.where(r > 0, r, 1.0)
    u, s = to_flat(x / rs, y / rs, z / rs)
    u2, s2 = mult(u, s, n)
    return from_flat(u2, s2)


def tri_rule(n=2, name=None, label=None):
    def F(x, y, z):
        r2 = x * x + y * y + z * z
        X, Y, Z = tri_dir(x, y, z, n)
        ok = r2 > 0; rn = r2 ** (n / 2.0)
        return np.where(ok, rn * X, 0.0), np.where(ok, rn * Y, 0.0), np.where(ok, rn * Z, 0.0)
    return M.fixed(F, name or 'tri', label or 'even spacing (two flat triangles, kite layout)')


def cone(t, mu1=0.4):
    return C.cone_rule(t, mu1=mu1, name='cone %+.2f' % t, label='second new try with the dial at %.2f' % t)


SWEEP = [-0.10, -0.20, -0.268, -0.35, -0.45]


def check():
    rng = np.random.default_rng(5); p = rng.normal(size=(3, 200000)); p /= np.sqrt((p * p).sum(0))
    u, s = to_flat(*p); q = np.stack(from_flat(u, s)); print('round trip direction -> flat -> direction: largest error %.2e' % np.abs(q - p).max())
    # doubling on the flat circle
    th = rng.uniform(0, 2 * np.pi, 100000); X, Y, Z = tri_dir(np.cos(th), np.sin(th), 0 * th)
    e = np.angle(np.exp(1j * (np.arctan2(Y, X) - 2 * th))); print('flat circle: largest error of the doubled angle %.2e, largest |z| %.2e' % (np.abs(e).max(), np.abs(Z).max()))
    # continuity: neighbours stay neighbours
    h = 1e-6; t = rng.normal(size=(3, 200000)); t -= (t * p).sum(0) * p; t /= np.sqrt((t * t).sum(0))
    p2 = p + h * t; p2 /= np.sqrt((p2 * p2).sum(0))
    g1 = np.stack(tri_dir(*p)); g2 = np.stack(tri_dir(*p2)); st = np.sqrt(((g2 - g1) ** 2).sum(0)) / h
    print('stretch of directions over 200000 random pairs: median %.3f, 5..95 %% %.3f..%.3f, largest %.1f (a jump would show as about 1e6)' % (np.median(st), np.percentile(st, 5), np.percentile(st, 95), st.max()))
    # how many directions are sent to one direction: area count
    n = 1200; lat = (np.arange(n) + 0.5) / n * np.pi - np.pi / 2; lon = (np.arange(2 * n) + 0.5) / (2 * n) * 2 * np.pi
    LA, LO = np.meshgrid(lat, lon, indexing='ij'); hh = 1e-5

    def G(la, lo):
        return np.stack(tri_dir(np.cos(la) * np.cos(lo), np.cos(la) * np.sin(lo), np.sin(la)), -1)
    g = G(LA, LO); a = (G(LA + hh, LO) - G(LA - hh, LO)) / (2 * hh); b = (G(LA, LO + hh) - G(LA, LO - hh)) / (2 * hh) / np.cos(LA)[..., None]
    det = (np.cross(a, b) * g).sum(-1); dA = np.cos(LA) * (np.pi / n) * (np.pi / n)
    aa, bb, ab = (a * a).sum(-1), (b * b).sum(-1), (a * b).sum(-1); tr, dd = aa + bb, np.sqrt(np.maximum((aa - bb) ** 2 + 4 * ab * ab, 0))
    s1, s2 = np.sqrt((tr + dd) / 2), np.sqrt(np.maximum((tr - dd) / 2, 0)); ok = np.isfinite(det) & (np.abs(det) < 1e3)
    print('covers the sphere %.3f times; folded share %.4f; squeeze (larger / smaller stretch): median %.2f, 90 %% below %.2f, 99 %% below %.2f'
          % ((det * dA)[ok].sum() / (4 * np.pi), (dA * (det < 0))[ok].sum() / dA[ok].sum(), np.nanmedian((s1 / s2)[ok]), np.nanpercentile((s1 / s2)[ok], 90), np.nanpercentile((s1 / s2)[ok], 99)))
    for deg in (0.5, 2, 5, 10, 20, 40, 60, 80):
        i = int(np.argmin(np.abs(np.degrees(lat) - deg)))
        print('   latitude %4.1f: larger stretch %.2f..%.2f, smaller %.2f..%.2f' % (deg, s1[i].min(), s1[i].max(), s2[i].min(), s2[i].max()))
    r = tri_rule(); print('flat check', M.flat_check(r, n=20000, steps=60))
    pp = rng.normal(size=(3, 5000)); X, Y, Z, _ = r.step(pp[0], pp[1], pp[2], (), 0, 0, 0, 0)
    print('length squared: largest error %.2e; all finite: %s' % (np.abs(np.sqrt(X * X + Y * Y + Z * Z) - (pp * pp).sum(0)).max(), bool(np.isfinite(X).all() and np.isfinite(Y).all() and np.isfinite(Z).all())))


SETS = [('c = -1', (-1.0, 0.0, 0.0)), ('rabbit', M.RABBIT), ('c = -0.75', (-0.75, 0.0, 0.0)), ('Siegel disc', M.SIEGEL)]


def cuts():
    rules = [M.bench('oneplane')] + [cone(t) for t in SWEEP] + [tri_rule()]
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
    im.save(os.path.join(HERE, 'sweep-cuts.png')); print('wrote sweep-cuts.png', im.size)


def solids(tag):
    cam = {'a': (0.45, 0.5, 1.0), 'top': (0.2, 1.0, 0.35)}[tag]
    rules = [M.bench('oneplane')] + [cone(t) for t in (-0.10, -0.268, -0.45)] + [tri_rule()]
    M.julia_sheet(rules, os.path.join(HERE, 'sweep-solids-%s.png' % tag), sets=[SETS[0], SETS[1]], w=420, h=315, nd=230, steps=30, cam=cam,
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

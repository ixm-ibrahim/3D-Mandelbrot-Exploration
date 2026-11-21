"""Round 27, respace, step 1: the point-to-point match of the two flat pictures (c = -1), checked and drawn.

    python flatmatch.py check      -> flatmatch-check.log (printed)
    python flatmatch.py picture    -> match.png
"""
import sys, time, colorsys
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage
import carry as C
M = C.M
BOX = (-1.8, 1.8, -1.3, 1.3)


def circle(pts):
    """The round disc that a cloud of points fills: a circle fitted to the corners of its hull."""
    from scipy.spatial import ConvexHull
    q = np.c_[pts.real, pts.imag]; hv = q[ConvexHull(q).vertices]
    A = np.c_[2 * hv, np.ones(len(hv))]; sol = np.linalg.lstsq(A, (hv ** 2).sum(1), rcond=None)[0]
    cen = sol[0] + 1j * sol[1]
    return cen, float(np.sqrt(sol[2] + abs(cen) ** 2))


def check():
    t0 = time.time(); rng = np.random.default_rng(27); n = 20000
    u, s = rng.uniform(BOX[0], BOX[1], n), rng.uniform(BOX[2], BOX[3], n); z = u + 1j * s
    tru = M.flat_stay(u, s, -1.0, 0.0, 600) >= 600
    P, kind = C.Hflat(z, nmax=300)
    car = np.zeros(n, bool); fin = np.isfinite(P.real) & np.isfinite(P.imag)
    car[fin] = C.flat_tree_inside(P[fin])
    raw = C.flat_tree_inside(z)
    print('20000 random points of the box %s' % (BOX,))
    print('  truly inside: %d;  the object\'s flat cut as it stands: wrong verdict at %d points (%.1f%% of the true area)'
          % (tru.sum(), (raw != tru).sum(), 100.0 * (raw != tru).sum() / tru.sum()))
    print('  carried over (object asked at the matched point): true verdict at %d of %d; wrong at %d' % ((car == tru).sum(), n, (car != tru).sum()))
    print('     of the wrong ones: truly inside %d, truly outside %d' % ((tru & ~car).sum(), (~tru & car).sum()))
    print('  kinds: matched inside a body %d, outside %d, not settled in 300 steps %d' % ((kind == 1).sum(), (kind == 0).sum(), (kind == -1).sum()))
    print('  inside points matched inside a body: %d of %d; outside points sent outside: %d of %d'
          % ((tru & (kind == 1)).sum(), tru.sum(), (~tru & (kind == 0)).sum(), (~tru).sum()))
    # body to body: every true body lands in one disc of the object, different bodies in different discs
    w, h = 900, 650
    gu, gs = np.meshgrid(np.linspace(BOX[0], BOX[1], w), np.linspace(BOX[3], BOX[2], h)); zz = (gu + 1j * gs).ravel()
    nn, zn, d, _ = C.enter(C.BASILICA, zz, 90); nn = nn.reshape(h, w)
    Pg = np.zeros(zz.size, complex); kg = np.zeros(zz.size, int)
    for i in range(0, zz.size, 60000):
        Pg[i:i + 60000], kg[i:i + 60000] = C.Hflat(zz[i:i + 60000], nmax=90)
    Pg = Pg.reshape(h, w); kg = kg.reshape(h, w); bodies = []
    for k in range(0, 12):
        lab, cnt = ndimage.label((nn == k) & (kg == 1))
        for j in range(1, cnt + 1):
            m = lab == j
            if m.sum() >= 60:
                pts = Pg[m]; cen, r = circle(pts)
                bodies.append((k, int(m.sum()), cen, r, (gu[m] + 1j * gs[m]).mean()))
    print('  body to body: %d true bodies of at least 60 grid points (grid %d x %d)' % (len(bodies), w, h))
    worst = 0.0; bad = 0
    for i in range(len(bodies)):
        for j in range(i + 1, len(bodies)):
            ov = bodies[i][3] + bodies[j][3] - abs(bodies[i][2] - bodies[j][2])
            worst = max(worst, ov / min(bodies[i][3], bodies[j][3])); bad += ov > 0.02 * min(bodies[i][3], bodies[j][3])
    print('     their images: pairs that overlap by more than 2%% of the smaller radius: %d; worst overlap %.3f of the smaller radius' % (bad, worst))
    fill = []
    for k, cnt, cen, r, zc in bodies:
        a = np.linspace(0, 2 * np.pi, 400, endpoint=False); rr = r * np.sqrt(np.random.default_rng(1).uniform(0, 0.98 ** 2, 400))
        fill.append(C.flat_tree_inside(cen + rr * np.exp(1j * a)).mean())
    print('     the round disc spanned by each image: share of it that the object calls inside: least %.3f, mean %.3f' % (min(fill), np.mean(fill)))
    big = sorted(bodies, key=lambda b: -b[1])[:9]
    for k, cnt, cen, r, zc in big:
        print('     true body at %+.3f%+.3fi (first entry %d, %5d points) -> disc of the object at %+.3f%+.3fi, radius %.3f' % (zc.real, zc.imag, k, cnt, cen.real, cen.imag, r))
    # rim to rim: halvings land on fractions
    B = C.BASILICA; th = np.array([1 / 4, 1 / 8, 3 / 8, 1 / 16, 3 / 16, 5 / 16, 7 / 16]); fr = ['1/1', '1/2', '2/1', '1/3', '2/3', '3/2', '3/1']
    zr = B.unbott(0.9995 * np.exp(-2j * np.pi * th)); Pr, kr = C.Hflat(zr, nmax=300); wr = C.model_of(Pr)
    for a, f, zq, wq in zip(th, fr, zr, wr):
        print('     rim of the middle body at the halving %-5s (true point %+.3f%+.3fi) -> the object\'s rim coordinate %.4f (fraction %s)' % ('%g' % a, zq.real, zq.imag, wq.real, f))
    print('%.0f s' % (time.time() - t0))


def colour(nn, b):
    """A pattern in the body's natural coordinate: 16 spokes at the halvings, three rings."""
    ang = (-np.angle(b) / (2 * np.pi)) % 1.0; r = np.abs(b)
    sec = np.floor(ang * 16).astype(int); ring = (r > 0.45).astype(int) + (r > 0.75) + (r > 0.92)
    out = np.zeros(b.shape + (3,), np.uint8)
    for s in range(16):
        for q in range(4):
            rgb = colorsys.hsv_to_rgb(s / 16.0, 0.35 + 0.18 * q, 1.0 - 0.17 * q - (0.12 if s % 2 else 0.0))
            out[(sec == s) & (ring == q)] = [int(255 * v) for v in rgb]
    return out


def picture():
    t0 = time.time(); w, h, ss = 800, 578, 2
    W, H = w * ss, h * ss
    gu, gs = np.meshgrid(np.linspace(BOX[0], BOX[1], W), np.linspace(BOX[3], BOX[2], H)); zz = (gu + 1j * gs).ravel()
    left = np.zeros((H * W, 3), np.uint8); left[:] = (16, 20, 34)
    right = np.zeros((h, w, 3), np.uint8); right[:] = (16, 20, 34)
    tg = np.meshgrid(np.linspace(BOX[0], BOX[1], w), np.linspace(BOX[3], BOX[2], h))
    tin = C.flat_tree_inside((tg[0] + 1j * tg[1]).ravel()).reshape(h, w); right[tin] = (70, 74, 86)
    for i in range(0, zz.size, 80000):
        z = zz[i:i + 80000]
        n, zn, d, _ = C.enter(C.BASILICA, z, 80); ok = n >= 0
        if not ok.any():
            continue
        b, _db = C.BASILICA.bott(zn[ok]); col = colour(n[ok], b)
        left[i + np.flatnonzero(ok)] = col
        P, kind = C.Hflat(z[ok], nmax=80); good = kind == 1
        px = np.round((P.real[good] - BOX[0]) / (BOX[1] - BOX[0]) * (w - 1)).astype(int); py = np.round((BOX[3] - P.imag[good]) / (BOX[3] - BOX[2]) * (h - 1)).astype(int)
        m = (px >= 0) & (px < w) & (py >= 0) & (py < h); right[py[m], px[m]] = col[good][m]
        print('  %d / %d  %.0f s' % (i, zz.size, time.time() - t0)); sys.stdout.flush()
    left = np.asarray(Image.fromarray(left.reshape(H, W, 3)).resize((w, h), Image.LANCZOS))
    pad = 10; im = Image.new('RGB', (2 * w + 3 * pad, h + 64), (12, 14, 20)); d = ImageDraw.Draw(im)
    d.text((pad, 8), 'The match, body by body. Same colour = same point.', fill=(240, 240, 245), font=M.font(20))
    d.text((pad, 36), 'Left: the true flat picture of c = -1, 16 spokes at the halvings in every body.', fill=(170, 178, 192), font=M.font(14))
    d.text((w + 2 * pad, 36), 'Right: where the match puts them in the flat cut of the balls object (grey = not reached at this grid).', fill=(170, 178, 192), font=M.font(14))
    im.paste(Image.fromarray(left), (pad, 60)); im.paste(Image.fromarray(right), (w + 2 * pad, 60))
    im.save('match.png'); print('wrote match.png %.0f s' % (time.time() - t0))


if __name__ == '__main__':
    (check if (len(sys.argv) < 2 or sys.argv[1] == 'check') else picture)()

"""Round 25, section klein, part 1: the paper's own flat rule, measured.

The paper (Kucera) replaces z -> z^2 on the unit circle by the map h made of three pieces of circle inversions:
    arc   0..120 degrees: g2      = mirror(y -> -y) after the inversion in the circle of centre 2 e^(+i 60), radius sqrt 3
    arc 120..240 degrees: g1      = mirror after the inversion in the circle of centre -2, radius sqrt 3
    arc 240..360 degrees: g2^(-1) = mirror after the inversion in the circle of centre 2 e^(-i 60), radius sqrt 3
and extends it "by simple radial scaling": z -> |z|^2 h(z / |z|) + c.

    python out/r25/klein/paper2d.py numbers      what h is, how far it is from doubling, how far the flat cut is
    python out/r25/klein/paper2d.py picture      flatcut.png: the true flat pictures, the paper's, the difference
"""
import os, sys
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, 'out', 'r21', 'lib'))
import mem as M

S3 = np.sqrt(3.0)
CENT = [2 * np.exp(1j * np.pi / 3), -2 + 0j, 2 * np.exp(-1j * np.pi / 3)]


def h_unit(w):
    """The paper's map on unit complex numbers w."""
    th = np.nan_to_num(np.mod(np.angle(w), 2 * np.pi)); k = np.clip((th / (2 * np.pi / 3)).astype(int), 0, 2)
    a = np.array(CENT)[k]; u = w - a
    return np.conj(a + 3.0 * u / (u.real ** 2 + u.imag ** 2))


def h_angle(t):
    """h as a map of the angle, in turns (0..1)."""
    return np.mod(np.angle(h_unit(np.exp(2j * np.pi * t))) / (2 * np.pi), 1.0)


def phi(t, n=48):
    """The matching phi between h and doubling: phi(h(t)) = 2 phi(t). Read from which third of the circle the orbit
    of t under h visits (the same thirds are a road map for doubling)."""
    t = np.mod(np.asarray(t, float), 1.0); its = []
    for _ in range(n):
        its.append(np.minimum((t * 3).astype(int), 2)); t = h_angle(t)
    x = (its[-1] + 0.5) / 3.0
    for k in reversed(its[:-1]):
        # the point of third k whose double is x:  third 0 = [0, 1/3] -> [0, 2/3];  third 1 -> [2/3, 4/3];  third 2 -> [4/3, 2]
        x = np.where(k == 0, x / 2, np.where(k == 2, (x + 1) / 2, np.where(x < 0.5, (x + 1) / 2, x / 2)))
    return x


def paper_stay(zr, zi, c, steps, r2=36.0):
    z = np.array(zr, float) + 1j * np.array(zi, float); n = np.zeros(z.shape, np.int32); alive = np.ones(z.shape, bool)
    for _ in range(steps):
        z = np.where(alive, z, 1.0); r = np.abs(z); w = np.where(r > 0, z / np.where(r > 0, r, 1.0), 1.0)
        z = r * r * h_unit(w) + complex(c[0], c[1])
        alive &= (z.real ** 2 + z.imag ** 2) < r2; n += alive
    return n


SETS = [('c = -1', (-1.0, 0.0)), ('rabbit', M.RABBIT[:2]), ('c = -0.75', (-0.75, 0.0)), ('Siegel disc', M.SIEGEL[:2])]
BOX = (-1.8, 1.8, -1.35, 1.35)


def grids(w=960, steps=300):
    hh = int(w * (BOX[3] - BOX[2]) / (BOX[1] - BOX[0])); u, s = np.meshgrid(np.linspace(BOX[0], BOX[1], w), np.linspace(BOX[3], BOX[2], hh))
    out = []
    for nm, c in SETS:
        out.append((nm, M.flat_stay(u, s, c[0], c[1], steps) >= steps, paper_stay(u, s, c, steps) >= steps))
    return out, (BOX[1] - BOX[0]) / (w - 1)


def haus(a, b, px):
    if not a.any() or not b.any():
        return float('nan')
    da = ndimage.distance_transform_edt(~a) * px; db = ndimage.distance_transform_edt(~b) * px
    return float(max(da[b].max(), db[a].max()))


def numbers():
    t = (np.arange(200000) + 0.5) / 200000
    # 1. what h is
    e = 1e-6
    print('h at 0, 1/3, 2/3 (turns):', h_angle(np.array([0.0, 1 / 3 + 1e-12, 2 / 3 + 1e-12])), ' (doubling: 0, 2/3, 1/3)')
    print('speed of h at angle 0: %.6f (doubling: 2)   speed of h after h at 1/3: %.6f (doubling: 4)' %
          ((h_angle(np.array([e]))[0]) / e, np.mod(h_angle(h_angle(np.array([1 / 3 + e])))[0] - 1 / 3, 1) / e))
    d = np.abs(np.mod(h_angle(t) - 2 * t + 0.5, 1.0) - 0.5)
    print('largest gap between h and doubling, one step: %.2f degrees (at %.1f degrees)' % (360 * d.max(), 360 * t[d.argmax()]))
    sp = np.mod(h_angle(t + 1e-7) - h_angle(t), 1.0) / 1e-7
    print('speed of h: from %.3f to %.3f (doubling: 2 everywhere)' % (sp.min(), sp.max()))
    # 2. the matching phi
    p = phi(t); g = np.abs(p - t)
    print('phi (h-angle -> true angle): largest shift %.2f degrees, mean %.2f degrees' % (360 * g.max(), 360 * g.mean()))
    for lev in (4, 8, 12, 16):
        # the arcs that doubling cuts the circle into after lev steps (true length 1 / (3 * 2^lev)); their length for h
        q = np.arange(3 * 2 ** lev + 1) / (3 * 2 ** lev); tt = np.interp(q, np.concatenate([[0], p, [1]]), np.concatenate([[0], t, [1]]))
        L = np.diff(tt); print('   after %2d steps the %d equal arcs of doubling are, for h, from %.2e to %.2e long: ratio %.0f' % (lev, L.size, L.min(), L.max(), L.max() / L.min()))
    # 3. the flat cut
    gs, px = grids()
    for nm, tr, pa in gs:
        print('%-12s true area %.4f, paper area %.4f; wrong verdicts %.1f%% of the true area; furthest apart %.3f (the set is about 3.2 wide)'
              % (nm, tr.sum() * px * px, pa.sum() * px * px, 100.0 * (tr != pa).sum() / max(tr.sum(), 1), haus(tr, pa, px)))
    # 4. the library's own check of the same rule in 3D (bench "kleinian" = the paper's first construction)
    print('library flat check of the paper rule:', M.flat_check(M.bench('kleinian'), n=20000, steps=60))


def picture():
    gs, px = grids(w=520, steps=300); pad = 8; h, w = gs[0][1].shape
    W = pad + len(gs) * (w + pad); H = 34 + 3 * (h + 24)
    im = Image.new('RGB', (W, H), (12, 14, 20)); d = ImageDraw.Draw(im)
    d.text((pad, 6), 'Flat cut: the true flat picture (top), the paper\'s rule (middle), where they differ (bottom, red = only true, blue = only paper)', fill=(240, 240, 245), font=M.font(16))
    for j, (nm, tr, pa) in enumerate(gs):
        x = pad + j * (w + pad)
        for i, a in enumerate((tr, pa)):
            img = np.zeros((h, w, 3), np.uint8); img[...] = (20, 26, 40); img[a] = (238, 228, 200)
            im.paste(Image.fromarray(img), (x, 34 + i * (h + 24))); d.text((x + 4, 36 + i * (h + 24)), nm + (', true' if i == 0 else ', the paper\'s rule'), fill=(150, 160, 175), font=M.font(13))
        img = np.zeros((h, w, 3), np.uint8); img[...] = (20, 26, 40); img[tr & pa] = (90, 90, 90); img[tr & ~pa] = (230, 80, 70); img[~tr & pa] = (80, 140, 240)
        im.paste(Image.fromarray(img), (x, 34 + 2 * (h + 24)))
    im.save(os.path.join(HERE, 'flatcut.png')); print('wrote flatcut.png', im.size)


if __name__ == '__main__':
    {'numbers': numbers, 'picture': picture}[sys.argv[1] if len(sys.argv) > 1 else 'numbers']()

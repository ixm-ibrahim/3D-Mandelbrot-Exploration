"""Round 24 scout, part 6: the second new try with its extra copy laid round MORE than once.

    R(w) = (w^m + t) / (w^(m-2) (1 + t w^m))          m = 3: the new try of round 23 (copy once round, lopsided)
                                                      m = 4: copy twice round, like the flat picture itself
                                                      m = 6: four times round
On the flat circle it is doubling for every m (m - (m - 2) = 2). R(-w) = R(w) exactly when m is even, so for even m
the solid keeps the flat picture's half-turn sameness and cannot be lopsided. Covers the sphere 2 + 2 (m - 2) times.
Blended into plain doubling beside the flat plane exactly as in out/r23/me/cone.py.
With t < 0 the push is strong at longitudes 0, 360/m, 2*360/m, ... and weak half way between.

    python out/r24/me/mfold.py check | cuts | solids a|top
"""
import os, sys, time
import numpy as np
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, 'out', 'r21', 'lib'))
import mem as M


def mdir(x, y, z, m=4, t=-0.268, mu1=0.4, blend=True):
    r = np.sqrt(x * x + y * y + z * z); rs = np.where(r > 0, r, 1.0)
    Zs = np.clip(z / rs, -1 + 1e-15, 1 - 1e-15); mu = np.arctanh(Zs)
    north = z > 0
    den = np.where(north, rs + z, rs - z); den = np.where(den > 0, den, 1.0)
    s = (x + 1j * np.where(north, -y, y)) / den                       # |s| <= 1: w in the south, 1/w in the north
    sm = s ** m; sm2 = s ** (m - 2)
    N = np.where(north, sm2 * (1 + t * sm), sm + t)
    D = np.where(north, sm + t, sm2 * (1 + t * sm))
    if blend:
        inb = np.abs(mu) < mu1
        if inb.any():
            sa = np.where(inb, s, 1.0); w = np.where(north, 1.0 / np.where(np.abs(sa) > 0, sa, 1.0), sa)
            q = np.clip(np.abs(mu) / mu1, 0, 1); chi = q * q * (3 - 2 * q)
            wm = w ** m
            W = w * w * np.exp(chi * (np.log(1 + t / wm) - np.log(1 + t * wm)))
            N = np.where(inb, W, N); D = np.where(inb, 1.0 + 0j, D)
    n2, d2 = np.abs(N) ** 2, np.abs(D) ** 2; tot = n2 + d2; tot = np.where(tot > 0, tot, 1.0)
    xy = 2 * N * np.conj(D) / tot
    return xy.real, xy.imag, (n2 - d2) / tot


def rule(m=4, t=-0.268, mu1=0.4, blend=True):
    def F(x, y, z):
        r2 = x * x + y * y + z * z
        X, Y, Z = mdir(x, y, z, m, t, mu1, blend)
        ok = r2 > 0
        return np.where(ok, r2 * X, 0.0), np.where(ok, r2 * Y, 0.0), np.where(ok, r2 * Z, 0.0)
    return M.fixed(F, 'm%d %+.2f' % (m, t), 'extra copy laid %d times round, dial %.2f' % (m - 2, t))


SETS = [('c = -1', (-1.0, 0.0, 0.0)), ('rabbit', M.RABBIT), ('c = -0.75', (-0.75, 0.0, 0.0)), ('Siegel disc', M.SIEGEL)]
LIST = [(3, -0.268), (4, -0.10), (4, -0.20), (4, -0.30), (4, -0.45), (6, -0.10), (6, -0.20)]


def push_line(m, t, lift=15.0):
    lon = np.radians(np.arange(0, 360, 15.0)); la = np.radians(lift)
    X, Y, Z = mdir(np.cos(la) * np.cos(lon), np.cos(la) * np.sin(lon), np.sin(la) + 0 * lon, m, t)
    return np.arcsin(np.clip(Z, -1, 1)) / la


def check():
    for m, t in LIST:
        r = rule(m, t); print('\n==', r.name, r.label)
        print('   flat check', M.flat_check(r, n=20000, steps=60))
        p = push_line(m, t); print('   push at a lift of 15 degrees, longitudes 0, 15, ..., 345:\n      ' + ' '.join('%.2f' % v for v in p))
        for nm, lo, rr in (('c = -1 meeting points (180)', 180.0, 0.618), ('rabbit meeting point (120)', 119.94, 0.5536)):
            for lift in (8.0, 15.0, 25.0):
                la = np.radians(lift); lon = np.radians(np.array([lo]))
                X, Y, Z = mdir(np.cos(la) * np.cos(lon), np.cos(la) * np.sin(lon), np.sin(la) + 0 * lon, m, t)
                print('   %-30s lift %4.0f: push times distance %.2f' % (nm, lift, float(np.arcsin(Z[0]) / la * rr)))
        # the copy: where is the northern half laid onto the flat circle, and how much is it stretched there
        n = 2000; lat = np.radians(np.linspace(25, 89.5, n)); lo0 = np.radians(17.0)
        X, Y, Z = mdir(np.cos(lat) * np.cos(lo0), np.cos(lat) * np.sin(lo0), np.sin(lat), m, t)
        k = np.nonzero(np.sign(Z[1:]) != np.sign(Z[:-1]))[0]
        print('   the copy stands at latitude', ', '.join('%.1f' % np.degrees(lat[i]) for i in k), '(2 / cos of it = %s; 2 keeps shapes)' % ', '.join('%.2f' % (2 / np.cos(lat[i])) for i in k))


def cuts():
    rules = [M.bench('oneplane')] + [rule(m, t) for m, t in LIST]
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
    im.save(os.path.join(HERE, 'mfold-cuts.png')); print('wrote mfold-cuts.png', im.size)


def solids(tag, which):
    cam = {'a': (0.45, 0.5, 1.0), 'top': (0.2, 1.0, 0.35)}[tag]
    rules = [M.bench('oneplane')] + [rule(m, t) for m, t in which]
    M.julia_sheet(rules, os.path.join(HERE, 'mfold-solids-%s.png' % tag), sets=[SETS[0], SETS[1]], w=420, h=315, nd=230, steps=30, cam=cam,
                  title='Rough solids, eye at %s' % (cam,))
    print('sheet', tag, 'done')


if __name__ == '__main__':
    a = sys.argv[1] if len(sys.argv) > 1 else 'check'
    if a == 'check':
        check()
    elif a == 'cuts':
        cuts()
    else:
        solids(sys.argv[2] if len(sys.argv) > 2 else 'a', [(4, -0.20), (4, -0.30), (6, -0.10), (6, -0.20)])

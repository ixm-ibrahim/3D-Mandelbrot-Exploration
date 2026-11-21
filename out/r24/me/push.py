"""Round 24 scout, part 4: how hard does each rule push a lifted point away, all round the flat circle?

For a direction on the flat circle at longitude lon, lift it by a small latitude eps and look at the latitude of
its square: push(lon) = image latitude / eps. Plain doubling gives 2 at every longitude. A rule's push at the
longitude of a meeting point, times the meeting point's distance from 0, says whether a point lifted above the
meeting point runs away (bodies stay apart) or is held (bodies grow together).

Also: the push at several heights, because the blended rules are exact AT the plane and change above it.

    python out/r24/me/push.py        -> push.png, numbers on the screen
"""
import os, sys
import numpy as np
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, 'out', 'r21', 'lib')); sys.path.insert(0, os.path.join(ROOT, 'out', 'r23', 'me')); sys.path.insert(0, HERE)
import mem as M
import cone as C
import tri as T


def push_of(dirfun, lon, lat):
    x, y, z = np.cos(lat) * np.cos(lon), np.cos(lat) * np.sin(lon), np.sin(lat) + 0 * lon
    X, Y, Z = dirfun(x, y, z)
    return np.arcsin(np.clip(Z, -1, 1)) / lat


def oneplane_dir(x, y, z):
    w = (x + 1j * y) / (1 - z); W = w * w; n2 = np.abs(W) ** 2
    return 2 * W.real / (1 + n2), 2 * W.imag / (1 + n2), (n2 - 1) / (n2 + 1)


RULES = [('one plane', oneplane_dir, (150, 200, 255)),
         ('first version (dial +0.27)', lambda x, y, z: C.cone_dir(x, y, z, C.T15), (255, 140, 120)),
         ('second version (dial -0.27)', lambda x, y, z: C.cone_dir(x, y, z, -C.T15), (140, 230, 150)),
         ('even-spacing end', lambda x, y, z: T.tri_dir(x, y, z), (240, 220, 130))]

MEET = [('c = -1 meeting points', 180.0, 0.618), ('rabbit meeting point', 119.94, 0.5536), ('c = -0.75', 180.0, 0.5), ('Siegel disc (no meeting point; its centre)', 137.5 / 2 % 360, 0.5)]


def main():
    lon = np.radians(np.arange(0, 360, 1.0))
    for lat_deg in (1.0, 8.0, 15.0, 25.0):
        print('\nlift = %.0f degrees of latitude: push at longitude 0, 60, 120, 180, 240, 300 (plain doubling near the plane = 2)' % lat_deg)
        for nm, f, _ in RULES:
            p = push_of(f, lon, np.radians(lat_deg))
            print('   %-28s %s   min %.2f max %.2f' % (nm, ' '.join('%6.2f' % p[i] for i in (0, 60, 120, 180, 240, 300)), p.min(), p.max()))
    print('\nAt the meeting points (push times distance from 0; above 1 = a lifted point runs away, below 1 = it is held):')
    for nm, lo, r in MEET[:3]:
        for lat_deg in (1.0, 8.0, 15.0, 25.0):
            row = []
            for rn, f, _ in RULES:
                p = float(push_of(f, np.radians(np.array([lo])), np.radians(lat_deg))[0]); row.append('%s %.2f' % (rn.split(' (')[0], abs(p) * r))
            print('   %-24s lift %4.0f deg: %s' % (nm, lat_deg, ' | '.join(row)))
    # picture: push round the circle at a lift of 15 degrees
    W, H, pad = 980, 420, 60; im = Image.new('RGB', (W, H), (12, 14, 20)); d = ImageDraw.Draw(im); f = M.font(14)
    d.text((pad, 10), 'How hard a lifted point is pushed away from the flat picture, all round (lift: 15 degrees)', fill=(235, 235, 235), font=M.font(16))
    ymax = 5.0

    def XY(lo, v):
        return pad + lo / 360.0 * (W - 2 * pad), H - 50 - np.clip(v, -1, ymax) / ymax * (H - 110)
    for v in (0, 1, 2, 3, 4, 5):
        y = XY(0, v)[1]; d.line([(pad, y), (W - pad, y)], fill=(40, 46, 60)); d.text((pad - 22, y - 8), '%d' % v, fill=(150, 160, 175), font=f)
    for lo in (0, 60, 120, 180, 240, 300, 360):
        x = XY(lo, 0)[0]; d.line([(x, H - 50), (x, 50)], fill=(30, 35, 48)); d.text((x - 10, H - 44), '%d' % lo, fill=(150, 160, 175), font=f)
    for i, (nm, fn, col) in enumerate(RULES):
        p = np.abs(push_of(fn, lon, np.radians(15.0))); pts = [XY(np.degrees(l), v) for l, v in zip(lon, p)]
        d.line(pts, fill=col, width=3); d.text((pad + 10 + i * 230, H - 22), nm, fill=col, font=f)
    im.save(os.path.join(HERE, 'push.png')); print('\nwrote push.png')


if __name__ == '__main__':
    main()

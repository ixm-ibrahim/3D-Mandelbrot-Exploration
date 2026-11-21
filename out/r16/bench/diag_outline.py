"""Working aid: draw the outline r(angle) of the middle body's cut at x = 0 for a few rules (to check the rib measure)."""
import os, sys, numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import bench as B, rules as R

names = sys.argv[1:] or ['twoplane', 'away', 'along', 'oneplane']
W, H = 1440, 260
im = Image.new('RGB', (W, H * len(names)), (12, 14, 20)); dr = ImageDraw.Draw(im)
for row, n in enumerate(names):
    F = R.get(n); nray = 1440
    th = np.linspace(0, 2 * np.pi, nray, endpoint=False)
    t = np.linspace(0, 1.0, 301)[1:]
    Y = t[None, :] * np.cos(th)[:, None]; Z = t[None, :] * np.sin(th)[:, None]
    ins, _ = B.inside(F, 0 * Y, Y, Z, trap=0.05)
    k = np.argmax(~ins, axis=1); lo = np.where(k > 0, t[np.maximum(k - 1, 0)], 0.0); hi = t[k]
    for it in range(18):
        mid = 0.5 * (lo + hi); mi, _ = B.inside(F, 0 * mid, mid * np.cos(th), mid * np.sin(th), trap=0.05)
        lo = np.where(mi, mid, lo); hi = np.where(mi, hi, mid)
    r = lo; slow = ndimage.median_filter(r, size=81, mode='wrap')
    print(n, 'r min %.4f max %.4f' % (r.min(), r.max()), 'median |dev| %.5f' % np.median(np.abs(r - slow)), 'share of rays with |dev| > 0.002: %.2f' % (np.abs(r - slow) > 0.002).mean())
    y0 = row * H
    f = lambda v: y0 + H - 10 - (v - 0.40) / 0.45 * (H - 20)
    dr.line([(i, f(slow[i])) for i in range(nray)], fill=(90, 140, 220))
    dr.line([(i, f(min(r[i], 0.85))) for i in range(nray)], fill=(235, 225, 200))
    dr.text((6, y0 + 4), n + ': outline radius of the cut x = 0 against the angle round the x-axis (0 to 360 degrees); blue = slow shape', fill=(220, 220, 220))
im.save(os.path.join(HERE, 'logs', 'diag-outline.png'))

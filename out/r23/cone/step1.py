"""Step 1: where do the shells of the scout's cone+ come from?  python out/r23/cone/step1.py"""
import os, sys
import numpy as np
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import conelib as L
M = L.M

# --- R_t by hand: critical directions and where they go, for a few t
print('R_t alone: t | cone latitude (1/t = tan(45 + L/2)) | stretch on the cone (t + 1/t)/2 | critical latitude | sent to latitude')
for t in (0.05, 0.1, 0.15, 0.2, L.T15, 0.35, 0.45):
    u = ((1 - 2 * t * t) + np.sqrt((1 - 2 * t * t) ** 2 - t * t)) / t; w = u ** (1 / 3.0); R = (u + t) / (w * (1 + t * u))
    print('  %.4f | %6.2f | %5.2f | %6.2f | %6.2f' % (t, 2 * np.degrees(np.arctan(1 / t)) - 90, (t + 1 / t) / 2, 2 * np.degrees(np.arctan(w)) - 90, 2 * np.degrees(np.arctan(abs(R))) - 90))

out, (lat, lon, g, s1, s2, det) = L.numbers(L.DIRS['scout+'])
crit = out['critical (lat, lon -> lat, lon, stretch)']

# --- shell points of the upright cut, c = -1
r = L.rule('scout+'); c = (-1.0, 0.0, 0.0); w, h, steps = 720, 520, 60
u, s = np.meshgrid(np.linspace(-1.8, 1.8, w), np.linspace(1.3, -1.3, h))
n = M.stay(r, u, 0 * u, s, *c, steps); ins = n >= steps
rad = np.hypot(u, s); shell = ins & (rad > 0.95) & (u > 0.2)
print('upright cut, c = -1: inside %d points; shell region (radius > 0.95, x > 0.2): %d' % (ins.sum(), shell.sum()))
x0, z0 = u[shell], s[shell]; y0 = 0 * x0
la0 = np.degrees(np.arctan2(z0, np.abs(x0)))
X, Y, Z, _ = r.step(x0, y0, z0, (), 0, 0, 0, 0)
R1 = np.sqrt(X * X + Y * Y + Z * Z); la1 = np.degrees(np.arcsin(Z / R1)); lo1 = np.degrees(np.arctan2(Y, X))
print('start: latitude of the shell points (percentiles 5 25 50 75 95):', np.round(np.percentile(np.abs(la0), [5, 25, 50, 75, 95]), 1))
print('one squaring: latitude of the square  :', np.round(np.percentile(np.abs(la1), [5, 25, 50, 75, 95]), 1))
print('one squaring: longitude of the square :', np.round(np.percentile(lo1, [5, 25, 50, 75, 95]), 1))
print('squares within 6 degrees of the critical value (lat +-15.8, lon 0): %.1f %%' % (100 * np.mean((np.abs(np.abs(la1) - 15.8) < 6) & (np.abs(lo1) < 6))))
print('start directions span %.0f degrees of latitude; their squares span %.0f degrees' % (np.ptp(np.abs(la0)), np.ptp(np.abs(la1))))
x1, y1, z1 = X + c[0], Y, Z
print('after the step: x %.2f..%.2f, |z| median %.3f, max %.3f' % (x1.min(), x1.max(), np.median(np.abs(z1)), np.abs(z1).max()))
# later: do they come down to the flat plane?
x, y, z = x1, y1, z1
for k in range(1, 40):
    if k in (1, 2, 3, 5, 10, 20, 39):
        print('   step %2d: median |z| %.4f, 95th %.4f; median distance to the nearer of 0 and -1: %.3f' % (k, np.median(np.abs(z)), np.percentile(np.abs(z), 95), np.median(np.minimum(np.sqrt(x * x + y * y + z * z), np.sqrt((x + 1) ** 2 + y * y + z * z)))))
    X, Y, Z, _ = r.step(x, y, z, (), k, 0, 0, 0); x, y, z = X + c[0], Y, Z

# --- picture: the cut with the critical directions, and where one squaring puts the shell points
img = M.shade(n, steps); im = Image.new('RGB', (2 * w + 30, h + 40), (12, 14, 20)); d = ImageDraw.Draw(im); f = M.font(15)
im.paste(Image.fromarray(img), (10, 34))


def px(xx, zz, ox):
    return ox + (xx + 1.8) / 3.6 * (w - 1), 34 + (1.3 - zz) / 2.6 * (h - 1)


for (cl, clon, vl, vlon, st) in crit:
    if abs(clon) < 2 or abs(clon - 360) < 2 or abs(clon - 180) < 2:
        sg = 1 if (abs(clon) < 2 or abs(clon - 360) < 2) else -1
        for zs in (1, -1):
            d.line([px(0, 0, 10), px(1.9 * sg * np.cos(np.radians(cl)), zs * 1.9 * np.sin(np.radians(cl)), 10)], fill=(255, 90, 80), width=2)
for zs in (1, -1):
    for sg in (1, -1):
        d.line([px(0, 0, 10), px(sg * 1.9 * 0.5, zs * 1.9 * 0.866, 10)], fill=(90, 220, 120), width=1)
d.text((10, 8), 'scout cone+, c = -1, upright cut. Red: the directions the rule stops stretching at. Green: the 60-degree cone.', fill=(235, 220, 170), font=f)
# right: the same cut again, shell points in orange, and where one step sends them in white, the ray c + s*e in red
img2 = img.copy(); im.paste(Image.fromarray(img2), (w + 20, 34))
sel = np.random.default_rng(1).choice(x0.size, min(4000, x0.size), replace=False)
for i in sel:
    a, b = px(x0[i], z0[i], w + 20); d.point((a, b), fill=(255, 160, 40))
for i in sel:
    if abs(y1[i]) < 0.05:
        a, b = px(x1[i], z1[i], w + 20); d.point((a, b), fill=(60, 255, 255))
for zs in (1, -1):
    d.line([px(-1, 0, w + 20), px(-1 + 2.6 * np.cos(np.radians(15.8)), zs * 2.6 * np.sin(np.radians(15.8)), w + 20)], fill=(255, 90, 80), width=1)
d.text((w + 20, 8), 'Orange: shell points. Blue-green: the same points one step later. Red: the line they are all sent along.', fill=(235, 220, 170), font=f)
im.save(os.path.join(HERE, 'step1-shells.png')); print('wrote step1-shells.png')

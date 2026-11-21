"""Round 20 check: the rabbit, the dendrite and the Siegel disc of m_w3, point by point, between its planes.
python out/r20/check/rabbit.py <set> [rule]   set = rabbit | dendrite | siegel | basilica ...   -> between-<rule>-<set>.png + numbers
Row 1: half-planes through the x-axis at 0, 10, 20, 30, 40, 50, 60 degrees from the flat plane (80 steps).
Row 2: cuts across the x-axis at five x. Row 3: the 30 degree half-plane at 40, 80, 160, 320 steps, and zooms.
"""
import os, sys, json, time
import numpy as np
from scipy import ndimage
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, 'out', 'r16', 'bench')); sys.path.insert(0, os.path.join(ROOT, 'out', 'me', 'r16'))
import bench as B
import rules as R
import truth as T

C = dict(rabbit=(-0.122561, 0.744862, 0.0), dendrite=(0.0, 1.0, 0.0), siegel=(-0.390541, -0.586788, 0.0), basilica=(-1.0, 0.0, 0.0),
         sanmarco=(-0.75, 0.0, 0.0), rab_up=(-0.122561, 0.744862, 0.015), bas_yz=(-1.0, 0.05, 0.03), bas_zy=(-1.0, 0.03, 0.05), sm_yz=(-0.75, 0.01, 0.02),
         airplane=(-1.754878, 0.0, 0.0), cauliflower=(0.25, 0.0, 0.0))
HALF = dict(rabbit=1.3, dendrite=1.4, siegel=1.3, basilica=1.7, sanmarco=1.6, rab_up=1.3, bas_yz=1.7, bas_zy=1.7, sm_yz=1.6, airplane=1.9, cauliflower=1.15)
XS = dict(rabbit=(-0.66, -0.4, -0.12, 0.0, 0.3), dendrite=(-0.6, -0.3, 0.0, 0.3, 0.6), siegel=(-0.6, -0.39, 0.0, 0.3, 0.6), basilica=(-1.0, -0.618, -0.3, 0.0, 0.3))
n = 440


def img_of(ins, death, steps):
    im = np.zeros(ins.shape + (3,), np.uint8); t = np.clip(death / 14.0, 0, 1)
    for ch, (lo, hi) in enumerate(((22, 60), (26, 90), (44, 160))):
        im[..., ch] = (lo + (hi - lo) * t).astype(np.uint8)
    im[ins] = (238, 228, 200)
    return im


def half_plane(F, c, ang, half, steps, n=n, x0=0.0, s0=None, hw=None):
    """Full plane through the x-axis: across = x, up = signed distance from the axis (upper half = the half-plane at `ang`)."""
    a = np.radians(ang)
    if hw is None:
        u = np.linspace(x0 - half, x0 + half, n); s = np.linspace(half, -half, n)
    else:
        u = np.linspace(x0 - hw, x0 + hw, n); s = np.linspace(s0 + hw, s0 - hw, n)
    U, Sg = np.meshgrid(u, s)
    return B.inside(F, U, Sg * np.cos(a), Sg * np.sin(a), c=c, steps=steps)


def cross(F, c, x0, half, steps, n=n):
    y = np.linspace(-half, half, n); z = np.linspace(half, -half, n); Y, Z = np.meshgrid(y, z)
    return B.inside(F, np.full_like(Y, x0), Y, Z, c=c, steps=steps)


if __name__ == '__main__':
    tag = sys.argv[1]; rule = sys.argv[2] if len(sys.argv) > 2 else 'm_w3'
    F = R.get(rule); c = C[tag]; half = HALF[tag]; steps = 80 if tag != 'dendrite' else 14
    angs = (0, 10, 20, 30, 40, 50, 60); xs = XS.get(tag, (-0.6, -0.3, 0.0, 0.3, 0.6))
    cols = 7; W = cols * (n + 8) + 8; Hh = 3 * (n + 28) + 44
    im = Image.new('RGB', (W, Hh), (12, 13, 18)); dr = ImageDraw.Draw(im); f = T.font(15); fb = T.font(18)
    dr.text((8, 8), '%s, rule %s (%s). Worked point by point, cream = inside. Upper half of each top tile = the half-plane named.' % (tag, rule, R.RULES[rule][1]), fill=(230, 230, 230), font=fb)
    num = dict(rule=rule, tag=tag, planes={}, cross={}, steps30={})
    for i, ang in enumerate(angs):
        ins, death = half_plane(F, c, ang, half, steps)
        up = ins[: n // 2]                       # the half-plane itself
        lab, k = ndimage.label(up); sz = np.bincount(lab.ravel())[1:] if k else np.array([0])
        px = (2 * half / (n - 1)) ** 2
        num['planes'][str(ang)] = dict(area=float(up.sum() * px), pieces=int(k), biggest_share=float(sz.max() / max(up.sum(), 1)), small_pieces=int((sz < 30).sum()))
        im.paste(Image.fromarray(img_of(ins, death, steps)), (8 + i * (n + 8), 62)); dr.text((8 + i * (n + 8), 42), 'through the x-axis, %d degrees from the flat plane, %d steps' % (ang, steps), fill=(210, 210, 210), font=f)
    for i, x0 in enumerate(xs):
        ins, death = cross(F, c, x0, 0.92 * half, steps)
        lab, k = ndimage.label(ins); sz = np.bincount(lab.ravel())[1:] if k else np.array([0])
        num['cross'][str(x0)] = dict(pieces=int(k), biggest_share=float(sz.max() / max(ins.sum(), 1)))
        y0 = 62 + n + 28
        im.paste(Image.fromarray(img_of(ins, death, steps)), (8 + i * (n + 8), y0)); dr.text((8 + i * (n + 8), y0 - 20), 'cut ACROSS the x-axis at x = %.2f (flat plane = the level line)' % x0, fill=(210, 210, 210), font=f)
    # the 30 degree half-plane at several step counts, zoomed on the upper half
    y0 = 62 + 2 * (n + 28)
    for i, st in enumerate((20, 40, 80, 160, 320) if tag != 'dendrite' else (8, 10, 12, 14, 18)):
        ins, death = half_plane(F, c, 30, half, st, x0=c[0] * 0.0, s0=0.5 * half, hw=0.5 * half)
        px = (half / (n - 1)) ** 2
        num['steps30'][str(st)] = dict(area=float(ins.sum() * px))
        j = 5 + i if i < 2 else i - 2
        if i < 2:
            continue
        im.paste(Image.fromarray(img_of(ins, death, st)), (8 + j * (n + 8), y0)); dr.text((8 + j * (n + 8), y0 - 20), 'the 30 degree half-plane, upper half only, %d steps' % st, fill=(210, 210, 210), font=f)
    # zooms at 30 degrees on whatever stands clear of the biggest piece
    ins, death = half_plane(F, c, 30, half, steps, n=880)
    up = ins[:440]; lab, k = ndimage.label(up)
    zi = 3
    if k > 1:
        sz = np.bincount(lab.ravel()); sz[0] = 0; order = np.argsort(sz)[::-1][1:4]
        u = np.linspace(-half, half, 880); s = np.linspace(half, -half, 880)
        for q in order:
            if sz[q] < 3 or zi >= 7:
                continue
            ys, xs_ = np.nonzero(lab == q); cy, cx = ys.mean(), xs_.mean(); ext = max(np.ptp(ys), np.ptp(xs_), 6) * (2 * half / 879)
            hw = max(0.8 * ext, 0.02)
            zin, zd = half_plane(F, c, 30, half, steps, x0=float(u[int(cx)]), s0=float(s[int(cy)]), hw=hw)
            im.paste(Image.fromarray(img_of(zin, zd, steps)), (8 + zi * (n + 8), y0)); dr.text((8 + zi * (n + 8), y0 - 20), '30 degrees, zoom: %.3f wide at x = %.2f, %.2f from the axis' % (2 * hw, u[int(cx)], s[int(cy)]), fill=(210, 210, 210), font=f)
            zi += 1
    num['loose_at_30_deg'] = int(k - 1)
    p = os.path.join(HERE, 'between-%s-%s.png' % (rule, tag)); im.save(p)
    json.dump(num, open(os.path.join(HERE, 'between-%s-%s.json' % (rule, tag)), 'w'), indent=1)
    print(json.dumps(num)); print('wrote', p)

"""Round 28, skeptic of Track B: my own pictures of my own block solids, from eyes the explorer did not use.

    PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1 python -W ignore out/r28/skeptic/sk_look.py <out.png> <h> <what> [<what> ...]

One column per solid, one row per eye:
    row 1  the eye stands near the LEFT end of the row and BELOW the flat plane
    row 2  the eye looks ALONG the row from its right end; only the middle body's stretch of the row is kept
    row 3  the same from the left end
(The explorer's eyes were: above the flat picture, in the flat plane from the front, and in front a little above.)
"""
import os, sys, time
sys.dont_write_bytecode = True
import numpy as np
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE))); sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, 'out', 'r21', 'lib'))
import mem as M
import sk_vox


def frame(cam, up):
    p = np.array(cam, float); p /= np.linalg.norm(p); e1 = np.cross(np.array(up, float), p); e1 /= np.linalg.norm(e1)
    return e1, np.cross(p, e1), -p                                        # screen right, screen up, depth (away from the eye)


def depth_map(ins, xs, ys, zs, cam, up, w, hgt, half_w, centre=(0.0, 0.0, 0.0), sub=0.6):
    e1, e2, e3 = frame(cam, up); h = xs[1] - xs[0]; lo = np.array([xs[0], ys[0], zs[0]]) - 0.5 * h; n = ins.shape
    us = np.linspace(-half_w, half_w, w); vs = np.linspace(half_w * hgt / w, -half_w * hgt / w, hgt); U, V = np.meshgrid(us, vs)
    P0 = [centre[i] + U * e1[i] + V * e2[i] for i in range(3)]; depth = np.full((hgt, w), np.inf); live = np.ones((hgt, w), bool)
    ii = np.argwhere(ins); cor = (lo + (ii.min(0)) * h, lo + (ii.max(0) + 1) * h)
    ds = [np.dot(np.array([cor[a][0], cor[b][1], cor[c][2]]) - np.array(centre), e3) for a in (0, 1) for b in (0, 1) for c in (0, 1)]
    for dk in np.arange(min(ds) - h, max(ds) + h, h * sub):
        idx = [np.floor((P0[i][live] + dk * e3[i] - lo[i]) / h).astype(np.int64) for i in range(3)]
        ok = (idx[0] >= 0) & (idx[0] < n[0]) & (idx[1] >= 0) & (idx[1] < n[1]) & (idx[2] >= 0) & (idx[2] < n[2])
        hit = np.zeros(ok.shape, bool); hit[ok] = ins[idx[0][ok], idx[1][ok], idx[2][ok]]
        if hit.any():
            li = np.flatnonzero(live); depth.ravel()[li[hit]] = dk; live.ravel()[li[hit]] = False
    return depth, us[1] - us[0]


EYES = [('eye near the left end of the row, below the flat plane', (-1.0, -0.55, -0.6), (0, 0, 1), None),
        ('eye on the row at its right end, looking along it; only the middle body kept', (1.0, 0.0, 0.0), (0, 0, 1), 'mid'),
        ('eye on the row at its left end, looking along it; only the middle body kept', (-1.0, 0.0, 0.0), (0, 0, 1), 'mid')]
NAMES = {'A-m1': 'the rule, first build, c = -1', 'B-m1': 'the rule, second build, c = -1', 'balls': 'Balls on balls (square grid), the yardstick', 'A-rab': 'the rule, first build, the rabbit', 'plain-m1': 'the rule, plain build, c = -1'}

if __name__ == '__main__':
    out = sys.argv[1]; h = float(sys.argv[2]); whats = sys.argv[3:]; w, hgt, pad = 640, 520, 8; t0 = time.time()
    im = Image.new('RGB', (pad + len(whats) * (w + pad), 40 + len(EYES) * (hgt + pad)), (12, 14, 20)); d = ImageDraw.Draw(im)
    d.text((pad, 8), 'The skeptic\'s own solids (blocks of side %g, every block computed, no mirror used), from eyes the explorer did not use' % h, fill=(240, 240, 245), font=M.font(18))
    for ci, what in enumerate(whats):
        ins, xs, ys, zs = sk_vox.load(what, h); Rm = 0.5 if what == 'balls' else 0.587
        for ri, (nm, cam, up, clip) in enumerate(EYES):
            if clip:
                g = ins & (np.abs(xs) < Rm)[:, None, None]; hw = 0.95
            else:
                g = ins; hw = 1.75
            dep, px = depth_map(g, xs, ys, zs, cam, up, w, hgt, hw); x = pad + ci * (w + pad); y = 36 + ri * (hgt + pad)
            im.paste(Image.fromarray(M.shade_solid(dep, px)), (x, y)); d.text((x + 6, y + 4), '%s: %s' % (NAMES.get(what, what), nm), fill=(170, 180, 195), font=M.font(13))
            print(what, nm, '%.0f s' % (time.time() - t0)); sys.stdout.flush()
    im.save(os.path.join(HERE, out)); print('wrote', out, im.size)

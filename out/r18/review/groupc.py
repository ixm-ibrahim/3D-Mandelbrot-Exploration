"""Reviewer check 1: is the bench's `along` the lab's rule for c out of the flat plane, and are the group-C solids
really empty / wisps?  python out/r18/review/groupc.py   (writes only into out/r18/review/)"""
import os, sys, json
import numpy as np
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, 'out', 'r16', 'bench'))
import bench as B
import rules as R

C30 = (-0.122561, 0.645069, 0.372431)
C90 = (-0.122561, 0.0, 0.744862)
RAB = (-0.122561, 0.744862, 0.0)


def run(F, x, y, z, c, steps, bail):
    """own loop (not the bench's): returns inside mask and the step at which each point left (0 = never)."""
    sh = x.shape; x, y, z = (np.ravel(a).astype(float) for a in (x, y, z))
    n = x.size; death = np.zeros(n, np.int16); alive = np.arange(n); R2 = bail * bail
    for k in range(steps):
        if alive.size == 0:
            break
        X, Y, Z = F(x, y, z); X = X + c[0]; Y = Y + c[1]; Z = Z + c[2]
        keep = X * X + Y * Y + Z * Z <= R2
        death[alive[~keep]] = k + 1
        alive = alive[keep]; x, y, z = X[keep], Y[keep], Z[keep]
    ins = np.zeros(n, bool); ins[alive] = True
    return ins.reshape(sh), death.reshape(sh)


out = {}
# ---- (a) the lab's flat pictures of `along` against the bench's `along`, same window, pixel for pixel
for tag, c in (('rabbit30', C30), ('rabbit90', C90), ('rabbit', RAB)):
    im = np.asarray(Image.open(os.path.join(ROOT, 'out', 'me', 'panel', tag + '-flat.png')).convert('RGB')).astype(int)
    H, W = im.shape[:2]
    cream = (np.abs(im - np.array([233, 224, 200])).sum(-1) < 45)
    px = 3.6 / H
    xs = (np.arange(W) + 0.5 - W / 2) * px; ys = (H / 2 - np.arange(H) - 0.5) * px
    X, Y = np.meshgrid(xs, ys)
    rec = dict(lab_cream_area=float(cream.sum() * px * px), lab_cream_pct_of_frame=float(100 * cream.mean()), rows=[])
    best = None
    for bail in (B.resc(c), 64.0):
        for steps in (10, 14, 20, 30, 40, 60):
            ins, _ = run(R.get('along'), X, Y, 0 * X, c, steps, bail)
            iou = float((ins & cream).sum() / max((ins | cream).sum(), 1))
            rec['rows'].append(dict(bail=round(float(bail), 3), steps=steps, area=float(ins.sum() * px * px), iou_with_lab=iou))
            print(tag, 'bail %.2f steps %d: inside area %.3f (lab cream %.3f), overlap/union with the lab picture %.2f' % (bail, steps, ins.sum() * px * px, rec['lab_cream_area'], iou), flush=True)
            if bail == 64.0 and steps == 40:
                best = ins
    side = np.zeros((H, 2 * W + 6, 3), np.uint8); side[:, :W] = im.astype(np.uint8)
    mine = np.zeros((H, W, 3), np.uint8) + np.array([30, 40, 90], np.uint8); mine[best] = (238, 228, 200)
    side[:, W + 6:] = mine
    Image.fromarray(side).save(os.path.join(HERE, 'lab-vs-bench-%s.png' % tag))
    out[tag] = rec

# ---- (b) the solids of group C on a coarse grid, own loop, several step counts
N = 129; L = 1.4; a = np.linspace(-L, L, N); X, Y, Z = np.meshgrid(a, a, a, indexing='ij'); h3 = (2 * L / (N - 1)) ** 3
out['solids'] = []
for rule in ('oneplane', 'twoplane', 'along', 'lathe'):
    for tag, c in (('rabbit', RAB), ('rabbit90', C90), ('rabbit30', C30)):
        ins, death = run(R.get(rule), X, Y, Z, c, 60, B.resc(c))
        row = dict(rule=rule, set=tag, last_step_any_point_left=int(death.max()))
        for s in (6, 10, 14, 20, 30, 40, 60):
            row['inside_at_%d' % s] = int(((death == 0) | (death > s)).sum())
        row['volume_at_40'] = float(row['inside_at_40'] * h3)
        out['solids'].append(row); print(row, flush=True)
json.dump(out, open(os.path.join(HERE, 'groupc.json'), 'w'), indent=1)

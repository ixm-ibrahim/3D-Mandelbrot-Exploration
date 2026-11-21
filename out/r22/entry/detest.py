"""Round 22, entry: the three distance estimates of the lab against the set worked point by point (the library).

  python out/r22/entry/run.py js out/r22/entry/detest.js detest.log
  python out/r22/entry/detest.py [log.json] [out.txt]      -> detest.txt, detest.png
A stop is FALSE when no point of the set lies within 0.03 of it (300 random points in that ball, the library's rule,
the lab's number of steps). A line of sight is MISSED when the library finds the set on it (one test every 0.004) and
the lab does not stop."""
import json, os, sys
import numpy as np
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, 'out', 'r21', 'lib')); sys.path.insert(0, os.path.join(ROOT, 'out', 'r21', 'judge'))
import mem as M
import myrules as J
LIB = {'alongonce': J.get('alongmem.c_wake1'), 'pulledplane': J.get('sheet.evc005e70k16'), 'mercator': M.bench('oneplane'), 'turnalong': M.bench('along')}
src = sys.argv[1] if len(sys.argv) > 1 else 'detest.log.json'; dst = sys.argv[2] if len(sys.argv) > 2 else 'detest'
o = json.load(open(os.path.join(HERE, src), encoding='utf-8'))
rep = ['The three settings of "Distance estimate" (cap lifted in the page), 48 x 36 lines of sight per picture.',
       'false = a stop with no point of the set within 0.03; missed = the set is on the line and the lab does not stop.', '']
rng = np.random.default_rng(1); off = rng.normal(size=(300, 3)); off /= np.linalg.norm(off, axis=1)[:, None]; off *= rng.uniform(0, 0.03, (300, 1))
cache = {}; tiles = []
def inside(rule, d, Q):
    if d['mode'] == 'j':
        return M.stay(rule, Q[..., 0], Q[..., 1], Q[..., 2], *d['c'], d['iter'], r2=4096.0) >= d['iter']
    return M.stay(rule, Q[..., 0], Q[..., 1], Q[..., 2], Q[..., 0], Q[..., 1], Q[..., 2], d['iter'] - 1, r2=4096.0) >= d['iter'] - 1
for key, d in o.items():
    id_, tag, de = key.split(' '); rule = LIB[id_]
    w, h, PX, PY, fov = d['w'], d['h'], d['PX'], d['PY'], d['fov']
    ro = np.array(d['pos']); R, U, F = np.array(d['right']), np.array(d['up']), np.array(d['f'])
    hit = np.array([p is not None for p in d['picks']]).reshape(PY, PX)
    P = np.array([p if p is not None else [0, 0, 0] for p in d['picks']], float).reshape(PY, PX, 3)
    if (id_, tag) not in cache:
        jj, ii = np.meshgrid(np.arange(PY), np.arange(PX), indexing='ij')
        ux = (2 * (w * (ii + 0.5) / PX) - w) / h * fov; uy = (h - 2 * (h * (jj + 0.5) / PY)) / h * fov
        rd = ux[..., None] * R + uy[..., None] * U + F; rd /= np.linalg.norm(rd, axis=-1, keepdims=True)
        b = (rd * ro).sum(-1); disc = b * b - (ro * ro).sum() + 2.6 ** 2
        ok = disc > 0; sq = np.sqrt(np.where(ok, disc, 0)); t0 = np.where(ok, -b - sq, 0); t1 = np.where(ok, -b + sq, 0)
        ts = np.arange(0, 5.2, 0.004); lh = np.zeros((PY, PX), bool)
        for r0 in range(0, PY, 6):
            sl = slice(r0, r0 + 6); T = t0[sl, :, None] + ts[None, None, :]
            lh[sl] = (inside(rule, d, ro + T[..., None] * rd[sl, :, None, :]) & (T < t1[sl, :, None])).any(-1)
        cache[(id_, tag)] = lh
    lh = cache[(id_, tag)]
    near = np.zeros((PY, PX), bool); near[hit] = inside(rule, d, P[hit][:, None, :] + off[None]).any(1)
    false = hit & ~near; missed = lh & ~hit
    rep.append('%-11s %-3s %s: stops %4d, false %4d (%4.1f %%); library has the set on %4d lines, missed %3d (%4.1f %%); %5d ms to draw' % (
        id_, tag, {'0': 'Rough        ', '1': 'One neighbour', '3': 'Exact        '}[de], hit.sum(), false.sum(), 100 * false.sum() / max(1, hit.sum()), lh.sum(), missed.sum(), 100 * missed.sum() / max(1, lh.sum()), d['ms']))
    print(rep[-1]); sys.stdout.flush()
    m = np.zeros((PY, PX, 3), np.uint8); m[...] = (20, 24, 34); m[hit] = (238, 228, 200); m[false] = (255, 60, 60); m[missed] = (90, 160, 255)
    tiles.append((key, np.kron(m, np.ones((5, 5, 1), np.uint8))))
cols = 3; th, tw = tiles[0][1].shape[:2]
im = Image.new('RGB', (10 + cols * (tw + 10), 40 + ((len(tiles) + cols - 1) // cols) * (th + 28)), (12, 14, 20)); dr = ImageDraw.Draw(im)
dr.text((10, 8), 'columns: Rough | One neighbour | Exact.  cream = a true stop, red = a false stop, blue = missed', fill=(240, 240, 245), font=M.font(15))
for i, (key, m) in enumerate(tiles):
    x = 10 + (i % cols) * (tw + 10); y = 40 + (i // cols) * (th + 28)
    dr.text((x, y), key, fill=(200, 205, 215), font=M.font(13)); im.paste(Image.fromarray(m), (x, y + 18))
im.save(os.path.join(HERE, dst + '.png'))
open(os.path.join(HERE, dst + '.txt'), 'w', encoding='utf-8', newline='\n').write('\n'.join(rep) + '\n')

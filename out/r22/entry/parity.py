"""Round 22, entry: the lab's two entries against the library's rules (out/r21/lib/mem.py, out/r21/judge/myrules.py).

  python out/r22/entry/run.py js out/r22/entry/parity.js parity.log     (the page; writes parity.log.json)
  python out/r22/entry/parity.py                                        -> parity.txt, parity-slices-*.png, parity-rays.png
A: the rule in JavaScript, orbit by orbit.  B: the shader on level slices, point by point.  C: the 3D picture, ray by ray.
"""
import json, os, sys
import numpy as np
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, 'out', 'r21', 'lib')); sys.path.insert(0, os.path.join(ROOT, 'out', 'r21', 'judge'))
import mem as M
import myrules as J

LIB = {'alongonce': J.get('alongmem.c_wake1'), 'pulledplane': J.get('sheet.evc005e70k16'), 'mercator': M.bench('oneplane'), 'turnalong': M.bench('along')}
RAB = (-0.122561, 0.744862, 0.0); BAS = (-1.0, 0.0, 0.0)
rep = []
def say(*a):
    t = ' '.join(str(x) for x in a); rep.append(t); print(t); sys.stdout.flush()

o = json.load(open(os.path.join(HERE, 'parity.log.json'), encoding='utf-8'))

# ---------------------------------------------------------------- A
say('A. The rule in JavaScript (CARRY in 10-approaches.js) against the library, 20,000 orbits each, 40 steps, leaving = |v| >= 6.')
say('   "verdict" = stays all 40 steps or not; "count" = the number of steps it stays.')
k = np.arange(1, 20001, dtype=float); frac = lambda x: x - np.floor(x)
X = 3.6 * frac(k * 0.8191725133961645) - 1.8; Y = 2.6 * frac(k * 0.6710436067037893) - 1.3; Z = 2.6 * frac(k * 0.5497004779019703) - 1.3
for id_ in ('alongonce', 'pulledplane'):
    r = LIB[id_]
    for tag, c in (('bas', BAS), ('rab', RAB), ('man', None)):
        lib = M.stay(r, X, Y, Z, *(c if c else (X, Y, Z)), 40)
        js = np.array(o['A'][id_][tag])
        line = '   %-11s %s: inside %5d (library) %5d (lab); verdicts that differ %d; counts that differ %d' % (id_, {'bas': 'Julia c = -1    ', 'rab': 'Julia rabbit    ', 'man': 'Mandelbrot      '}[tag],
                (lib >= 40).sum(), (js >= 40).sum(), ((lib >= 40) != (js >= 40)).sum(), (lib != js).sum())
        if tag == 'man':
            js0 = np.array(o['A'][id_]['man0'])
            line += '; started at 0 instead of at c (as the lab does): counts that differ from the lab\'s own start at c: %d' % (js0 != js).sum()
        say(line)

# ---------------------------------------------------------------- B
say('')
say('B. The shader, point by point: level slices z = const, 200 x 200 points (sampleSlice: the picture\'s own program, with three')
say('   neighbouring orbits beside every point). Library: the same points, the same number of squarings, leaving = |v| >= 64 as in the lab.')
say('   "edge" = a differing point that has a neighbour of the other kind in the library\'s picture (within one grid step).')
def grid(box, N):
    cx, cy, side = box; t = (np.arange(N) + 0.5) / N - 0.5
    return np.meshgrid(cx + side * t, cy + side * t)          # rows from the lowest y upward
def edge_of(m):
    e = np.zeros_like(m)
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            e |= np.roll(np.roll(m, dy, 0), dx, 1) != m
    return e
tiles = {}
for key, d in o['B'].items():
    id_, tag, zt = key.split(' '); N = d['N']; z = d['z']
    lab = np.frombuffer(d['mask'].encode(), np.uint8).reshape(N, N) - 48
    gx, gy = grid(d['box'], N); gz = np.full_like(gx, z)
    if d['mode'] == 'j':
        lib = M.stay(LIB[id_], gx, gy, gz, *d['c'], d['iter'], r2=4096.0) >= d['iter']
    else:
        lib = M.stay(LIB[id_], gx, gy, gz, gx, gy, gz, d['iter'] - 1, r2=4096.0) >= d['iter'] - 1
    labin = lab == 1; amb = (lab >= 2)
    diff = (labin != lib) & ~amb; ed = edge_of(lib)
    line = '   %-11s %-3s z = %-4g: inside %5d (library) %5d (lab); differ %4d of %d, of them on an edge %4d; lab reads exactly 0: %d' % (
        id_, tag, z, lib.sum(), labin.sum(), diff.sum(), N * N, (diff & ed).sum(), amb.sum())
    if z == 0:
        if d['mode'] == 'j':
            flat = M.flat_stay(gx, gy, d['c'][0], d['c'][1], d['iter'], r2=4096.0) >= d['iter']
        else:
            flat = M.flat_stay(gx, gy, gx, gy, d['iter'] - 1, r2=4096.0) >= d['iter'] - 1
        fd = (labin != flat) & ~amb
        line += ' | against the flat (complex) picture: lab differs %d (on an edge %d), library differs %d' % (fd.sum(), (fd & edge_of(flat)).sum(), (lib != flat).sum())
    say(line)
    img = np.zeros((N, 3 * N + 20, 3), np.uint8); img[...] = (14, 17, 26)
    for j, m in enumerate((labin, lib)):
        img[:, j * (N + 10):j * (N + 10) + N][m[::-1]] = (238, 228, 200)
    dd = np.zeros((N, N, 3), np.uint8); dd[...] = (30, 34, 46); dd[lib[::-1]] = (70, 76, 92); dd[(diff & ~ed)[::-1]] = (255, 60, 60); dd[(diff & ed)[::-1]] = (255, 200, 60); dd[amb[::-1]] = (90, 160, 255)
    img[:, 2 * (N + 10):] = dd
    tiles.setdefault(id_, []).append((key, img))
for id_, ts in tiles.items():
    N = ts[0][1].shape[0]; W = ts[0][1].shape[1]
    im = Image.new('RGB', (W + 20, 40 + len(ts) * (N + 26)), (12, 14, 20)); dr = ImageDraw.Draw(im)
    dr.text((10, 8), '%s: the lab\'s shader | the library | where they differ (red: away from an edge, yellow: on an edge, blue: lab reads exactly 0)' % id_, fill=(240, 240, 245), font=M.font(15))
    for i, (key, img) in enumerate(ts):
        y = 40 + i * (N + 26); dr.text((10, y), key, fill=(200, 205, 215), font=M.font(14)); im.paste(Image.fromarray(img), (10, y + 20))
    im.save(os.path.join(HERE, 'parity-slices-%s.png' % id_))

# ---------------------------------------------------------------- C
say('')
say('C. The 3D picture (Rough estimate, no neighbouring orbits), 48 x 36 probes from one camera. Library: the same lines of sight,')
say('   one test every 0.004 along each. "depth": lab stop minus the first library point inside, along the line (median, 95 %), in pixels of the page.')
sil = []
for key, d in o['C'].items():
    id_, tag = key.split(' ')
    w, h, PX, PY, fov = d['w'], d['h'], d['PX'], d['PY'], d['fov']
    ro = np.array(d['pos']); R, U, F = np.array(d['right']), np.array(d['up']), np.array(d['f'])
    jj, ii = np.meshgrid(np.arange(PY), np.arange(PX), indexing='ij')
    px = w * (ii + 0.5) / PX; py = h * (jj + 0.5) / PY
    ux = (2 * px - w) / h * fov; uy = (h - 2 * py) / h * fov
    rd = ux[..., None] * R + uy[..., None] * U + F; rd /= np.linalg.norm(rd, axis=-1, keepdims=True)
    hit = np.array([p is not None for p in d['picks']]).reshape(PY, PX)
    P = np.array([p if p is not None else [0, 0, 0] for p in d['picks']], float).reshape(PY, PX, 3)
    tl = ((P - ro) * rd).sum(-1)
    off = np.linalg.norm(P - (ro + tl[..., None] * rd), axis=-1)             # how far the lab's stop lies from my line of sight
    b = (rd * ro).sum(-1); disc = b * b - (ro * ro).sum() + 2.6 ** 2
    ok = disc > 0; sq = np.sqrt(np.where(ok, disc, 0)); t0 = np.where(ok, -b - sq, 0); t1 = np.where(ok, -b + sq, 0)
    ts = np.arange(0, 5.2, 0.004)
    tlib = np.full((PY, PX), np.inf)
    for r0 in range(0, PY, 6):
        sl = slice(r0, r0 + 6)
        T = t0[sl, :, None] + ts[None, None, :]; inside_span = T < t1[sl, :, None]
        Q = ro + T[..., None] * rd[sl, :, None, :]
        if d['mode'] == 'j':
            n = M.stay(LIB[id_], Q[..., 0], Q[..., 1], Q[..., 2], *d['c'], d['iter'], r2=4096.0) >= d['iter']
        else:
            n = M.stay(LIB[id_], Q[..., 0], Q[..., 1], Q[..., 2], Q[..., 0], Q[..., 1], Q[..., 2], d['iter'] - 1, r2=4096.0) >= d['iter'] - 1
        n &= inside_span
        first = np.where(n.any(-1), np.take_along_axis(T, np.argmax(n, -1)[..., None], -1)[..., 0], np.inf)
        tlib[sl] = first
    lh = np.isfinite(tlib); both = hit & lh
    pix = 2 * fov / h * np.where(both, tl, 1)
    dp = np.where(both, (tl - tlib) / pix, 0)[both]
    say('   %-11s %-3s: lab hits %4d, library hits %4d, both %4d, lab only %3d, library only %3d of %d; depth %+.1f px median, |depth| 95 %%: %.1f px; lab stops lie %.1e off my lines at most'
        % (id_, tag, hit.sum(), lh.sum(), both.sum(), (hit & ~lh).sum(), (lh & ~hit).sum(), PX * PY, np.median(dp) if dp.size else 0, np.quantile(np.abs(dp), 0.95) if dp.size else 0, off[hit].max() if hit.any() else 0))
    m = np.zeros((PY, PX, 3), np.uint8); m[...] = (20, 24, 34); m[both] = (238, 228, 200); m[hit & ~lh] = (255, 60, 60); m[lh & ~hit] = (90, 160, 255)
    sil.append((key, np.kron(m, np.ones((6, 6, 1), np.uint8))))
cols = 3; th, tw = sil[0][1].shape[:2]
im = Image.new('RGB', (10 + cols * (tw + 10), 40 + ((len(sil) + cols - 1) // cols) * (th + 30)), (12, 14, 20)); dr = ImageDraw.Draw(im)
dr.text((10, 8), 'Lines of sight: cream = lab and library both stop, red = only the lab stops, blue = only the library has a point of the set', fill=(240, 240, 245), font=M.font(15))
for i, (key, m) in enumerate(sil):
    x = 10 + (i % cols) * (tw + 10); y = 40 + (i // cols) * (th + 30)
    dr.text((x, y), key, fill=(200, 205, 215), font=M.font(14)); im.paste(Image.fromarray(m), (x, y + 20))
im.save(os.path.join(HERE, 'parity-rays.png'))
open(os.path.join(HERE, 'parity.txt'), 'w', encoding='utf-8', newline='\n').write('\n'.join(rep) + '\n')

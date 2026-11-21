"""Round 22, entrycheck second pass: the lab's two entries against the LIBRARY's rules (alongmem.c_wake1,
sheet.evc005e70k16), from what e2_parity_page.py took off the page (parity.log.json).
  python out/r22/entrycheck2/e2_parity.py   -> parity.txt, parity-slices.png, parity-rays.png
"""
import json, os, sys
import numpy as np
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, 'out', 'r21', 'lib')); sys.path.insert(0, os.path.join(ROOT, 'out', 'r21', 'judge'))
import mem as M
import myrules as J

LIB = {'alongonce': J.get('alongmem.c_wake1'), 'pulledplane': J.get('sheet.evc005e70k16')}
CSET = {'bas': (-1.0, 0.0, 0.0), 'rab': (-0.122561, 0.744862, 0.0), 'smk': (-0.75, 0.0, 0.0), 'air': (-1.754878, 0.0, 0.0), 'off': (-0.3, 0.4, -0.25)}
rep = []
def say(*a):
    t = ' '.join(str(x) for x in a); rep.append(t); print(t); sys.stdout.flush()

def flat_stay(zr, zi, cr, ci, steps, r2):
    """my own flat (complex) iteration"""
    z = np.array(zr, float) + 1j * np.array(zi, float); c = np.broadcast_to(np.asarray(cr, float) + 1j * np.asarray(ci, float), z.shape)
    n = np.zeros(z.shape, np.int32); alive = np.ones(z.shape, bool)
    with np.errstate(all='ignore'):
        for _ in range(steps):
            z = z * z + c
            alive &= (z.real ** 2 + z.imag ** 2) < r2; n += alive
            z = np.where(alive, z, 0)
    return n

o = json.load(open(os.path.join(HERE, 'parity.log.json'), encoding='utf-8'))

say('A. The rule in JavaScript (L.CARRY) against the library. 10,000 orbits each, 50 steps, leaving = |v| >= 6.')
k = np.arange(1, 10001, dtype=float); frac = lambda x: x - np.floor(x)
X = 3.2 * frac(k * 0.6180339887498949) - 1.6; Y = 2.4 * frac(k * 0.32471795724474603) - 1.2; Z = 2.4 * frac(k * 0.7548776662466927) - 1.2
tot = 0
for key in ('alongonce', 'pulledplane'):
    for tag in ('bas', 'rab', 'smk', 'off', 'man'):
        c = CSET.get(tag, (X, Y, Z))
        lib = M.stay(LIB[key], X, Y, Z, *c, 50)
        js = np.array(o['A'][key][tag]); tot += js.size
        say('   %-12s %-3s: stay all 50: lab %5d, library %5d | verdicts that differ %d, stay counts that differ %d' % (key, tag, (js >= 50).sum(), (lib >= 50).sum(), ((js >= 50) != (lib >= 50)).sum(), (js != lib).sum()))
say('   (%d orbits in all)' % tot)

say('')
say('B. The shader point by point (sampleSlice, three neighbour orbits beside each point), level slices of 144 x 144.')
say('   Same number of squarings as the page (Julia: Iterations; Mandelbrot: started at c, Iterations - 1), leaving = |v| >= 64.')
def grid(box, N):
    cx, cy, side = box; t = (np.arange(N) + 0.5) / N - 0.5
    return np.meshgrid(cx + side * t, cy + side * t)
def edge_of(m):
    e = np.zeros_like(m)
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            e |= np.roll(np.roll(m, dy, 0), dx, 1) != m
    return e
tiles = []; totB = 0; diffB = 0
for key, d in o['B'].items():
    name, tag, zt = key.split(' '); N = d['N']; z = d['z']
    lab = np.frombuffer(d['mask'].encode(), np.uint8).reshape(N, N) - 48
    gx, gy = grid(d['box'], N); gz = np.full_like(gx, z)
    if d['mode'] == 'j':
        a = (gx, gy, gz, *d['c'], d['iter'])
    else:
        a = (gx, gy, gz, gx, gy, gz, d['iter'] - 1)
    lib = M.stay(LIB[name], *a, r2=4096.0) >= a[-1]
    labin = lab == 1; amb = lab >= 2
    diff = (labin != lib) & ~amb; ed = edge_of(lib); totB += N * N; diffB += int(diff.sum())
    line = '   %-12s %-3s z = %-5g: inside lab %5d, library %5d; differ %4d (on an edge %4d); lab reads 0 or NaN: %d' % (name, tag, z, labin.sum(), lib.sum(), diff.sum(), (diff & ed).sum(), amb.sum())
    if z == 0 and d['c'][2] == 0:
        st = d['iter'] if d['mode'] == 'j' else d['iter'] - 1
        flat = (flat_stay(gx, gy, d['c'][0], d['c'][1], st, 4096.0) if d['mode'] == 'j' else flat_stay(gx, gy, gx, gy, st, 4096.0)) >= st
        line += ' | the flat (complex) picture: lab differs %d' % ((labin != flat) & ~amb).sum()
    say(line)
    img = np.zeros((N, 3 * N + 20, 3), np.uint8); img[...] = (14, 17, 26)
    for j, m in enumerate((labin, lib)):
        img[:, j * (N + 10):j * (N + 10) + N][m[::-1]] = (238, 228, 200)
    dd = np.zeros((N, N, 3), np.uint8); dd[...] = (30, 34, 46); dd[lib[::-1]] = (70, 76, 92); dd[(diff & ~ed)[::-1]] = (255, 60, 60); dd[(diff & ed)[::-1]] = (255, 200, 60); dd[amb[::-1]] = (90, 160, 255)
    img[:, 2 * (N + 10):] = dd
    tiles.append((key, img))
say('   (%d points in all, %d differ)' % (totB, diffB))
N = tiles[0][1].shape[0]; W = tiles[0][1].shape[1]; cols = 3; rows = (len(tiles) + cols - 1) // cols
im = Image.new('RGB', (10 + cols * (W + 14), 40 + rows * (N + 26)), (12, 14, 20)); dr = ImageDraw.Draw(im)
dr.text((10, 8), 'each tile: the lab\'s shader | the library | where they differ (red; yellow = on an edge; blue = lab reads 0)', fill=(240, 240, 245), font=M.font(15))
for i, (key, img) in enumerate(tiles):
    x = 10 + (i % cols) * (W + 14); y = 40 + (i // cols) * (N + 26)
    dr.text((x, y), key, fill=(200, 205, 215), font=M.font(13)); im.paste(Image.fromarray(img), (x, y + 18))
im.save(os.path.join(HERE, 'parity-slices.png'))

say('')
say('C. The 3D picture (the page caps these entries at Rough), 36 x 27 probes per camera, against the library along the same lines of sight (a test every 0.004).')
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
    off = np.linalg.norm(P - (ro + tl[..., None] * rd), axis=-1)
    b = (rd * ro).sum(-1); disc = b * b - (ro * ro).sum() + 2.6 ** 2
    ok = disc > 0; sq = np.sqrt(np.where(ok, disc, 0)); t0 = np.where(ok, -b - sq, 0); t1 = np.where(ok, -b + sq, 0)
    ts = np.arange(0, 5.2, 0.004)
    tlib = np.full((PY, PX), np.inf)
    jul = d['mode'] == 'j'; steps = d['iter'] if jul else d['iter'] - 1
    for r0 in range(0, PY, 3):
        sl = slice(r0, r0 + 3)
        T = t0[sl, :, None] + ts[None, None, :]; span = T < t1[sl, :, None]
        Q = ro + T[..., None] * rd[sl, :, None, :]
        cc = d['c'] if jul else (Q[..., 0], Q[..., 1], Q[..., 2])
        n = (M.stay(LIB[id_], Q[..., 0], Q[..., 1], Q[..., 2], *cc, steps, r2=4096.0) >= steps) & span
        tlib[sl] = np.where(n.any(-1), np.take_along_axis(T, np.argmax(n, -1)[..., None], -1)[..., 0], np.inf)
    lh = np.isfinite(tlib); both = hit & lh
    pix = 2 * fov / h * np.where(both, tl, 1)
    dp = np.where(both, (tl - tlib) / pix, 0)[both]
    only = hit & ~lh
    say('   %-11s %-4s: lab stops %4d, library %4d, both %4d, lab only %3d, library only %3d of %d; lab stops %+.1f px (median) from the library\'s first point, |.| 95 %%: %.1f px; stops off the lines of sight: %.1e at most'
        % (id_, tag, hit.sum(), lh.sum(), both.sum(), only.sum(), (lh & ~hit).sum(), PX * PY, np.median(dp) if dp.size else 0, np.quantile(np.abs(dp), 0.95) if dp.size else 0, off[hit].max() if hit.any() else 0))
    m = np.zeros((PY, PX, 3), np.uint8); m[...] = (20, 24, 34); m[both] = (238, 228, 200); m[only] = (255, 60, 60); m[lh & ~hit] = (90, 160, 255)
    sil.append((key, np.kron(m, np.ones((7, 7, 1), np.uint8))))
cols = 3; th, tw = sil[0][1].shape[:2]
im = Image.new('RGB', (10 + cols * (tw + 10), 40 + ((len(sil) + cols - 1) // cols) * (th + 30)), (12, 14, 20)); dr = ImageDraw.Draw(im)
dr.text((10, 8), 'Lines of sight: cream = lab and library both have the set, red = only the lab stops, blue = only the library', fill=(240, 240, 245), font=M.font(15))
for i, (key, m) in enumerate(sil):
    x = 10 + (i % cols) * (tw + 10); y = 40 + (i // cols) * (th + 30)
    dr.text((x, y), key, fill=(200, 205, 215), font=M.font(14)); im.paste(Image.fromarray(m), (x, y + 20))
im.save(os.path.join(HERE, 'parity-rays.png'))
open(os.path.join(HERE, 'parity.txt'), 'w', encoding='utf-8', newline='\n').write('\n'.join(rep) + '\n')

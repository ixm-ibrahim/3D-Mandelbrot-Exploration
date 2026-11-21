"""Round 22, entrycheck: the lab's two entries against (1) the library's rules and (2) my own writing-out of the
briefing (ec_rules.py).
  python out/r22/entrycheck/drive.py js out/r22/entrycheck/ec_parity.js parity.log     (the page -> parity.log.json)
  python out/r22/entrycheck/ec_parity.py       -> parity.txt, parity-slices.png, parity-rays.png, lab-only.json
"""
import json, os, sys
import numpy as np
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, 'out', 'r21', 'lib')); sys.path.insert(0, os.path.join(ROOT, 'out', 'r21', 'judge')); sys.path.insert(0, HERE)
import mem as M
import myrules as J
import ec_rules as E

SHEET = sys.modules['rules_sheet']
LIB = {'alongonce': J.get('alongmem.c_wake1'), 'pulledplane': J.get('sheet.evc005e70k16'), 'mercator': M.bench('oneplane')}
st_m, ini_m = SHEET.evc(0.2, ease_c=0.4, ease=0.4, kc=5.0)
LIB['pulledplane moved'] = M.Rule('moved', 'evc 0.2 / 0.4 / 5', st_m, ini_m)
MINE = {'alongonce': 'alongonce', 'pulledplane': ('pulledplane', 0.05, 0.7, 16.0), 'pulledplane moved': ('pulledplane', 0.2, 0.4, 5.0), 'mercator': 'oneplane'}
CS = {'bas': (-1.0, 0.0, 0.0), 'sie': (-0.390541, -0.586788, 0.0), 'off': (-0.6, 0.2, 0.15)}
rep = []
def say(*a):
    t = ' '.join(str(x) for x in a); rep.append(t); print(t); sys.stdout.flush()

o = json.load(open(os.path.join(HERE, 'parity.log.json'), encoding='utf-8'))

# ---------------------------------------------------------------- A
say('A. The rule in JavaScript (L.CARRY) against the library and against my own writing-out of the briefing.')
say('   12,000 orbits each, 60 steps, leaving = |v| >= 6. "verdict" = stays all 60 steps; "count" = steps it stays.')
k = np.arange(1, 12001, dtype=float); frac = lambda x: x - np.floor(x)
X = 3.4 * frac(k * 0.41421356237309515) - 1.7; Y = 2.6 * frac(k * 0.7320508075688772) - 1.3; Z = 2.6 * frac(k * 0.2360679774997898) - 1.3
for key in ('alongonce', 'pulledplane', 'pulledplane moved'):
    for tag in ('bas', 'sie', 'off', 'man'):
        c = CS.get(tag, (X, Y, Z))
        lib = M.stay(LIB[key], X, Y, Z, *c, 60)
        mine = E.stay(MINE[key], X, Y, Z, *c, 60)
        js = np.array(o['A'][key][tag])
        say('   %-18s %-3s: inside lab %5d, library %5d, mine %5d | lab vs library: verdicts %d, counts %d | lab vs mine: verdicts %d, counts %d | library vs mine: verdicts %d' % (
            key, tag, (js >= 60).sum(), (lib >= 60).sum(), (mine >= 60).sum(), ((js >= 60) != (lib >= 60)).sum(), (js != lib).sum(),
            ((js >= 60) != (mine >= 60)).sum(), (js != mine).sum(), ((lib >= 60) != (mine >= 60)).sum()))

# ---------------------------------------------------------------- B
say('')
say('B. The shader point by point (sampleSlice, three neighbouring orbits beside each point), level slices of 160 x 160 points.')
say('   Same number of squarings, leaving = |v| >= 64. "edge": a differing point with a neighbour of the other kind in the library\'s slice.')
def grid(box, N):
    cx, cy, side = box; t = (np.arange(N) + 0.5) / N - 0.5
    return np.meshgrid(cx + side * t, cy + side * t)
def edge_of(m):
    e = np.zeros_like(m)
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            e |= np.roll(np.roll(m, dy, 0), dx, 1) != m
    return e
tiles = []
for key, d in o['B'].items():
    name, tag, zt = key.split(' '); N = d['N']; z = d['z']
    rk = 'pulledplane moved' if name == 'pulledplane-moved' else name
    lab = np.frombuffer(d['mask'].encode(), np.uint8).reshape(N, N) - 48
    gx, gy = grid(d['box'], N); gz = np.full_like(gx, z)
    if d['mode'] == 'j':
        a = (gx, gy, gz, *d['c'], d['iter'])
    else:
        a = (gx, gy, gz, gx, gy, gz, d['iter'] - 1)
    lib = M.stay(LIB[rk], *a, r2=4096.0) >= a[-1]
    mine = E.stay(MINE[rk], *a, r2=4096.0) >= a[-1]
    labin = lab == 1; amb = lab >= 2
    diff = (labin != lib) & ~amb; dm = (labin != mine) & ~amb; ed = edge_of(lib)
    line = '   %-17s %-3s z = %-5g: inside lab %5d, library %5d, mine %5d; lab vs library differ %4d (on an edge %4d); lab vs mine differ %4d; lab reads 0 or NaN: %d' % (
        name, tag, z, labin.sum(), lib.sum(), mine.sum(), diff.sum(), (diff & ed).sum(), dm.sum(), amb.sum())
    if z == 0 and abs(d['c'][2]) == 0:
        if d['mode'] == 'j':
            flat = E.flat_stay(gx, gy, d['c'][0], d['c'][1], d['iter'], r2=4096.0) >= d['iter']
        else:
            flat = E.flat_stay(gx, gy, gx, gy, d['iter'] - 1, r2=4096.0) >= d['iter'] - 1
        line += ' | flat (complex) picture: lab differs %d' % ((labin != flat) & ~amb).sum()
    say(line)
    img = np.zeros((N, 3 * N + 20, 3), np.uint8); img[...] = (14, 17, 26)
    for j, m in enumerate((labin, lib)):
        img[:, j * (N + 10):j * (N + 10) + N][m[::-1]] = (238, 228, 200)
    dd = np.zeros((N, N, 3), np.uint8); dd[...] = (30, 34, 46); dd[lib[::-1]] = (70, 76, 92); dd[(diff & ~ed)[::-1]] = (255, 60, 60); dd[(diff & ed)[::-1]] = (255, 200, 60); dd[amb[::-1]] = (90, 160, 255)
    img[:, 2 * (N + 10):] = dd
    tiles.append((key, img))
say('')
say('B2. The shader against the page\'s own JavaScript rule where the library has none (Julia sets, 160 x 160 points, a slice off the flat plane).')
for key, d in o['BJ'].items():
    N = d['N']
    lab = np.frombuffer(d['lab'].encode(), np.uint8).reshape(N, N) - 48; js = (np.frombuffer(d['js'].encode(), np.uint8).reshape(N, N) - 48) == 1
    labin = lab == 1; amb = lab >= 2; diff = (labin != js) & ~amb
    say('   %-28s c = %s, z = %g: inside shader %5d, JavaScript %5d; differ %4d (on an edge %4d); shader reads 0 or NaN: %d' % (key, d['c'], d['z'], labin.sum(), js.sum(), diff.sum(), (diff & edge_of(js)).sum(), amb.sum()))
    img = np.zeros((N, 3 * N + 20, 3), np.uint8); img[...] = (14, 17, 26)
    for j, m in enumerate((labin, js)):
        img[:, j * (N + 10):j * (N + 10) + N][m[::-1]] = (238, 228, 200)
    dd = np.zeros((N, N, 3), np.uint8); dd[...] = (30, 34, 46); dd[js[::-1]] = (70, 76, 92); dd[diff[::-1]] = (255, 60, 60); dd[amb[::-1]] = (90, 160, 255)
    img[:, 2 * (N + 10):] = dd
    tiles.append((key, img))
N = tiles[0][1].shape[0]; W = tiles[0][1].shape[1]; cols = 3; rows = (len(tiles) + cols - 1) // cols
im = Image.new('RGB', (10 + cols * (W + 14), 40 + rows * (N + 26)), (12, 14, 20)); dr = ImageDraw.Draw(im)
dr.text((10, 8), 'each tile: the lab\'s shader | the library (or the page\'s JavaScript rule) | where they differ (red; yellow = on an edge; blue = lab reads 0)', fill=(240, 240, 245), font=M.font(15))
for i, (key, img) in enumerate(tiles):
    x = 10 + (i % cols) * (W + 14); y = 40 + (i // cols) * (N + 26)
    dr.text((x, y), key, fill=(200, 205, 215), font=M.font(13)); im.paste(Image.fromarray(img), (x, y + 18))
im.save(os.path.join(HERE, 'parity-slices.png'))

# ---------------------------------------------------------------- C
say('')
say('C. The 3D picture (Rough), 40 x 30 probes per camera. My rule along the same lines of sight, a test every 0.003.')
say('   "near": of the lab-only stops, how many have a point of the set (mine, 400 random points) within 0.02 of the stop.')
sil = []; lab_only = {}
rng = np.random.default_rng(7)
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
    ts = np.arange(0, 5.2, 0.003)
    tlib = np.full((PY, PX), np.inf)
    jul = d['mode'] == 'j'; steps = d['iter'] if jul else d['iter'] - 1
    for r0 in range(0, PY, 5):
        sl = slice(r0, r0 + 5)
        T = t0[sl, :, None] + ts[None, None, :]; span = T < t1[sl, :, None]
        Q = ro + T[..., None] * rd[sl, :, None, :]
        cc = d['c'] if jul else (Q[..., 0], Q[..., 1], Q[..., 2])
        n = (E.stay(MINE[id_], Q[..., 0], Q[..., 1], Q[..., 2], *cc, steps, r2=4096.0) >= steps) & span
        tlib[sl] = np.where(n.any(-1), np.take_along_axis(T, np.argmax(n, -1)[..., None], -1)[..., 0], np.inf)
    lh = np.isfinite(tlib); both = hit & lh
    pix = 2 * fov / h * np.where(both, tl, 1)
    dp = np.where(both, (tl - tlib) / pix, 0)[both]
    only = hit & ~lh; near = 0; pts = P[only]
    for p in pts:
        q = p + 0.02 * rng.normal(size=(400, 3)) / 1.7
        cc = d['c'] if jul else (q[:, 0], q[:, 1], q[:, 2])
        near += bool((E.stay(MINE[id_], q[:, 0], q[:, 1], q[:, 2], *cc, steps, r2=4096.0) >= steps).any())
    lab_only[key] = dict(pos=d['pos'], pts=pts.tolist(), rd=rd[only].tolist(), iter=d['iter'], mode=d['mode'], c=d['c'])
    say('   %-11s %-4s: lab stops %4d, mine %4d, both %4d, lab only %3d (near the set: %d), mine only %3d of %d; depth %+.1f px median, |depth| 95 %%: %.1f px; stops off my lines: %.1e at most'
        % (id_, tag, hit.sum(), lh.sum(), both.sum(), only.sum(), near, (lh & ~hit).sum(), PX * PY, np.median(dp) if dp.size else 0, np.quantile(np.abs(dp), 0.95) if dp.size else 0, off[hit].max() if hit.any() else 0))
    m = np.zeros((PY, PX, 3), np.uint8); m[...] = (20, 24, 34); m[both] = (238, 228, 200); m[only] = (255, 60, 60); m[lh & ~hit] = (90, 160, 255)
    sil.append((key, np.kron(m, np.ones((6, 6, 1), np.uint8))))
cols = 5; th, tw = sil[0][1].shape[:2]
im = Image.new('RGB', (10 + cols * (tw + 10), 40 + ((len(sil) + cols - 1) // cols) * (th + 30)), (12, 14, 20)); dr = ImageDraw.Draw(im)
dr.text((10, 8), 'Lines of sight: cream = lab and my rule both have the set, red = only the lab stops, blue = only my rule has a point of the set', fill=(240, 240, 245), font=M.font(15))
for i, (key, m) in enumerate(sil):
    x = 10 + (i % cols) * (tw + 10); y = 40 + (i // cols) * (th + 30)
    dr.text((x, y), key, fill=(200, 205, 215), font=M.font(14)); im.paste(Image.fromarray(m), (x, y + 20))
im.save(os.path.join(HERE, 'parity-rays.png'))
json.dump(lab_only, open(os.path.join(HERE, 'lab-only.json'), 'w'))
open(os.path.join(HERE, 'parity.txt'), 'w', encoding='utf-8', newline='\n').write('\n'.join(rep) + '\n')

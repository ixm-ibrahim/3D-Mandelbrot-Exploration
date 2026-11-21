"""The judge's numbers, one json file per rule in out/r21/judge/num/.   python out/r21/judge/jnum.py [rule names]

For each rule:
  flat      M.flat_check (40,000 points, 60 steps)
  spun      M.spun_check (40,000 pairs, 40 steps)
  vol       inside points on a 120 x 120 x 120 grid (x -1.8..1.8, y and z -1.5..1.5; no grid point lies on z = 0),
            basilica and rabbit, counted at 30, 80 and 200 steps
  pieces    connected pieces of the 80-step grid (touching by face, edge or corner): how many of 50 cells or more
            ("bodies"), how many smaller ("specks"), the share of the volume in specks, the share in the biggest piece
  eroded    the same grid with one layer of cells peeled off (a point stays if its six neighbours are inside): how many
            pieces of 30 cells or more. Separate bodies that meet in a point come apart; a lump stays one piece.
  pinch     share of a small ball round the rabbit's pinch point (-0.276, 0.480, 0) that is inside at 80 steps, for
            radius 0.12 and 0.06, not counting the slab within a quarter radius of the flat page
  lift      flat-inside points (300 steps of the complex orbit) lifted 1e-6 and 1e-3 off the page: how many are lost
            at 300 steps (Mandelbrot set: c lifted; basilica, rabbit, Siegel disc: the start point lifted)
  arcs      on circles round the x-axis at x = 0 (the basilica's middle body) and x = -1 (its side body), 2,880 places,
            80 steps: number of separate inside arcs and the share of the circle inside. 1 arc and 100 % = a ring.
"""
import os, sys, json, time
import numpy as np
from scipy import ndimage
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import myrules as J
M = J.M
OUT = os.path.join(J.HERE, 'num'); os.makedirs(OUT, exist_ok=True)
BAS = (-1.0, 0.0, 0.0)
N = 120


def grid():
    xs = np.linspace(-1.8, 1.8, N); ys = np.linspace(-1.5, 1.5, N)
    return np.meshgrid(xs, ys, ys, indexing='ij')


def pieces(mask):
    lab, n = ndimage.label(mask, structure=np.ones((3, 3, 3)))
    if n == 0:
        return {'bodies': 0, 'specks': 0, 'speck_share': 0.0, 'biggest_share': 0.0, 'sizes': []}
    sz = np.sort(np.bincount(lab.ravel())[1:])[::-1]; tot = int(sz.sum())
    return {'bodies': int((sz >= 50).sum()), 'specks': int((sz < 50).sum()), 'speck_share': float(sz[sz < 50].sum() / tot),
            'biggest_share': float(sz[0] / tot), 'sizes': [int(s) for s in sz[:8]]}


def eroded(mask):
    e = ndimage.binary_erosion(mask); lab, n = ndimage.label(e, structure=np.ones((3, 3, 3)))
    if n == 0:
        return {'left': 0, 'pieces30': 0, 'sizes': []}
    sz = np.sort(np.bincount(lab.ravel())[1:])[::-1]
    return {'left': int(e.sum()), 'pieces30': int((sz >= 30).sum()), 'sizes': [int(s) for s in sz[:8]]}


def volumes(r):
    X, Y, Z = grid(); out = {}
    for nm, c in (('basilica', BAS), ('rabbit', M.RABBIT)):
        n = M.stay(r, X, Y, Z, c[0], c[1], c[2], 200)
        out[nm] = {'n30': int((n >= 30).sum()), 'n80': int((n >= 80).sum()), 'n200': int((n >= 200).sum()), 'of': int(n.size),
                   'pieces80': pieces(n >= 80), 'eroded80': eroded(n >= 80), 'pieces200': pieces(n >= 200)}
    return out


def pinch(r, seed=11, n=60000):
    rng = np.random.default_rng(seed); out = {}
    p0 = (-0.276, 0.480, 0.0)
    for rad in (0.12, 0.06):
        v = rng.normal(size=(n, 3)); v /= np.linalg.norm(v, axis=1)[:, None]; v *= rad * rng.uniform(0, 1, n)[:, None] ** (1 / 3)
        v = v[np.abs(v[:, 2]) > 0.25 * rad]
        s = M.stay(r, p0[0] + v[:, 0], p0[1] + v[:, 1], v[:, 2], *M.RABBIT, 80) >= 80
        out['r%.2f' % rad] = float(s.mean())
    return out


def lift(r, seed=7, n=20000, steps=300):
    rng = np.random.default_rng(seed); out = {}
    cr, ci = rng.uniform(-2.1, 0.7, n), rng.uniform(-1.3, 1.3, n); ins = M.flat_stay(cr, ci, cr, ci, steps) >= steps
    cr, ci = cr[ins], ci[ins]; d = {'inside': int(ins.sum())}
    for h in (1e-6, 1e-3):
        d['lost_%g' % h] = int((M.mandel(r, cr, ci, np.full(cr.size, h), steps) < steps).sum())
    out['mandelbrot'] = d
    zr, zi = rng.uniform(-1.8, 1.8, n), rng.uniform(-1.3, 1.3, n)
    for nm, c in (('basilica', BAS), ('rabbit', M.RABBIT), ('siegel', M.SIEGEL)):
        ins = M.flat_stay(zr, zi, c[0], c[1], steps) >= steps; a, b = zr[ins], zi[ins]; d = {'inside': int(ins.sum())}
        for h in (1e-6, 1e-3):
            d['lost_%g' % h] = int((M.stay(r, a, b, np.full(a.size, h), c[0], c[1], c[2], steps) < steps).sum())
        out[nm] = d
    return out


def arcs(r, x0, radii, n=2880, steps=80):
    t = np.arange(n) * 2 * np.pi / n; out = []
    for rad in radii:
        s = M.stay(r, np.full(n, x0), rad * np.cos(t), rad * np.sin(t), *BAS, steps) >= steps
        k = int((s & ~np.roll(s, 1)).sum()); k = 1 if (k == 0 and s.all()) else k
        runs = []
        if 0 < s.sum() < n:
            i0 = int(np.argmax(~s)); q = np.roll(s, -i0); edges = np.flatnonzero(np.diff(np.concatenate([[0], q.astype(int), [0]])))
            runs = sorted(((edges[1::2] - edges[0::2]) * 360.0 / n).tolist(), reverse=True)
        out.append({'radius': float(rad), 'arcs': k, 'share': float(s.mean()), 'widest_deg': [round(a, 1) for a in runs[:8]]})
    return out


def one(r):
    t0 = time.time(); d = {'name': r.name, 'label': r.label}
    d['flat'] = M.flat_check(r); d['spun'] = M.spun_check(r)
    print('  flat', d['flat'], '\n  spun', d['spun']); sys.stdout.flush()
    d['vol'] = volumes(r); d['pinch'] = pinch(r); d['lift'] = lift(r)
    d['arcs_x0'] = arcs(r, 0.0, np.arange(0.50, 0.801, 0.02)); d['arcs_xm1'] = arcs(r, -1.0, np.arange(0.20, 0.501, 0.02))
    d['seconds'] = time.time() - t0
    json.dump(d, open(os.path.join(OUT, r.name + '.json'), 'w'), indent=1)
    v = d['vol']
    print('  %s done in %.0f s; basilica %d/%d/%d, rabbit %d/%d/%d' % (r.name, d['seconds'], v['basilica']['n30'], v['basilica']['n80'], v['basilica']['n200'],
                                                                     v['rabbit']['n30'], v['rabbit']['n80'], v['rabbit']['n200'])); sys.stdout.flush()


if __name__ == '__main__':
    names = sys.argv[1:] or [r.name for r in J.RULES]
    for nm in names:
        print(nm); one(J.get(nm))

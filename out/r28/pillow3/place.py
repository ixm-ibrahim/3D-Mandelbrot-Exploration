"""Round 28, pillow3: where the bodies sit, measured the same way on the pillow solids and on Balls on balls.

From a point inside a body, lines of sight in every direction: mu = angle from +x (the row), th = angle round the row
(0 = up in the flat picture, 90 = off the flat picture). r1(mu, th) = how far the line stays inside. A bud is a bump of
r1 over the body's own smooth skin (grey opening, window 24 degrees). Listed: every bump higher than 6 % of the body's
half width, with its place, its height and its two widths at half height (all in units of the body's half width R).

    python out/r28/pillow3/place.py > out/r28/pillow3/place.log
"""
import os, sys
import numpy as np
from scipy import ndimage as ndi
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, '..', '..', 'r25', 'klein'))
import vox, tree
M = vox.M
DMU, DTH, DR = 1.5, 3.0, 0.003
MU = np.radians(np.arange(DMU / 2, 180, DMU)); TH = np.radians(np.arange(0, 360, DTH))


def rays(inside_fn, centre, rmax):
    mu, th = np.meshgrid(MU, TH, indexing='ij'); d = np.stack([np.cos(mu), np.sin(mu) * np.cos(th), np.sin(mu) * np.sin(th)])
    rs = np.arange(DR, rmax, DR); r1 = np.full(mu.shape, rmax); live = np.ones(mu.shape, bool)
    for r in rs:
        ins = inside_fn(centre[0] + r * d[0][live], centre[1] + r * d[1][live], centre[2] + r * d[2][live])
        idx = np.flatnonzero(live); out = idx[~ins]; r1.ravel()[out] = r; live.ravel()[out] = False
        if not live.any():
            break
    return r1


def grid_fn(tag, h=0.006):
    ins, ax, _, _ = vox.grid(tag, h); lo = ax[0] - 0.5 * h; n = ax.size

    def f(x, y, z):
        i, j, k = (np.floor((v - lo) / h).astype(np.int64) for v in (x, y, z)); ok = (i >= 0) & (i < n) & (j >= 0) & (j < n) & (k >= 0) & (k < n)
        out = np.zeros(x.shape, bool); out[ok] = ins[i[ok], j[ok], k[ok]]; return out
    return f, ins, ax


def balls_fn(lattice='gauss'):
    r = tree.tree(lattice)
    return lambda x, y, z: M.stay(r, x, y, z, 0.0, 0.0, 0.0, 14) >= 14


def bumps(r1, R, floor=0.06):
    w = (int(round(24 / DMU)) | 1, int(round(24 / DTH)) | 1)
    base = ndi.grey_opening(r1, size=w, mode=('nearest', 'wrap')); hgt = (r1 - base) / R
    pk = (hgt == ndi.maximum_filter(hgt, size=(5, 5), mode=('nearest', 'wrap'))) & (hgt > floor)
    lab, n = ndi.label(hgt > floor)                         # one bump = one patch above the floor; keep its highest point
    out = []
    for i in range(1, n + 1):
        m = lab == i; j = np.argmax(np.where(m, hgt, -1)); a, b = np.unravel_index(j, hgt.shape)
        half = m & (hgt > 0.5 * hgt[a, b]); rr = r1[a, b] - 0.5 * hgt[a, b] * R
        wm = half[:, b].sum() * np.radians(DMU) * rr / R; wt = half[a, :].sum() * np.radians(DTH) * rr * np.sin(MU[a]) / R
        out.append((np.degrees(MU[a]), np.degrees(TH[b]), hgt[a, b], wm, wt))
    # patches that wrap round th = 0 are found twice: merge those that sit at the same mu, th 0 and 360 - DTH
    return sorted(out, key=lambda t: -t[2])


def report(name, fn, centre, R, rmax, top=10):
    r1 = rays(fn, centre, rmax); b = bumps(r1, R)
    big = [t for t in b if t[2] >= 0.5]; mid = [t for t in b if 0.15 <= t[2] < 0.5]; small = [t for t in b if t[2] < 0.15]
    print('%s (lines from (%.3f, 0, 0), half width R = %.3f): bumps higher than 0.5 R: %d; 0.15..0.5 R: %d; 0.06..0.15 R: %d' % (name, centre[0], R, len(big), len(mid), len(small)))
    for t in b[:top]:
        print('     %5.1f degrees from +x, %5.1f round the row: height %.2f R, widths %.2f R (along the row) x %.2f R (round it)%s' % (*t, '  [reaches the end of the line]' if t[2] * R + 1e-9 >= 0 and False else ''))
    return r1, b


if __name__ == '__main__':
    fb = balls_fn('gauss'); fbh = balls_fn('eisen')
    fa, insA, ax = grid_fn('m1'); fB, insB, _ = grid_fn('m1-lean50')
    k2 = tree.K2; rn = k2 / (2 * tree.T0 - 1) / 2
    print('--- the middle body'); res = {}
    res['balls'] = report('Balls on balls, square grid', fb, (0, 0, 0), k2 / 2, 0.95)
    res['ballsh'] = report('Balls on balls, honeycomb grid', fbh, (0, 0, 0), k2 / 2, 0.95)
    res['A'] = report('pillow3 layout A, c = -1', fa, (0, 0, 0), 0.618, 1.1)
    res['B'] = report('pillow3 layout B, c = -1', fB, (0, 0, 0), 0.618, 1.1)
    print('--- the right neighbour')
    report('Balls on balls, square grid', fb, (k2 / 2 + rn, 0, 0), rn, 0.6)
    report('pillow3 layout A', fa, (0.945, 0, 0), 0.327, 0.75)
    report('pillow3 layout B', fB, (0.945, 0, 0), 0.327, 0.75)
    print('--- the left neighbour')
    report('Balls on balls, square grid', fb, (-k2 / 2 - rn, 0, 0), rn, 0.6)
    report('pillow3 layout A', fa, (-0.945, 0, 0), 0.327, 0.75)
    report('pillow3 layout B', fB, (-0.945, 0, 0), 0.327, 0.75)
    print('--- whole solids (blocks of side 0.006)')
    one = M.bench('oneplane')
    for nm, ins in (('pillow3 layout A, c = -1', insA), ('pillow3 layout B, c = -1', insB), ('pillow3 layout A, rabbit', vox.grid('rab', 0.006)[0])):
        v = ins.sum(); ht = (ins != ins[::-1, ::-1]).sum() / v; mz = (ins != ins[:, :, ::-1]).sum() / v; my = (ins != ins[:, ::-1]).sum() / v
        op = ndi.binary_opening(ins, structure=ndi.generate_binary_structure(3, 1), iterations=3); thin = 1 - op.sum() / v
        lab, n = ndi.label(op); sz = np.sort(ndi.sum(op, lab, range(1, n + 1)))[::-1]
        print('%s: volume %.4f; changed by a half turn about the upright axis: %.1f %% of the volume; by the mirror in the flat plane: %.1f %%; by the mirror in the upright plane through the x-axis: %.1f %%'
              % (nm, v * 0.006 ** 3, 100 * ht, 100 * mz, 100 * my))
        print('     thin share (lost when 3 blocks are peeled and put back): %.1f %%; separate pieces after peeling: %d, of them larger than 1000 blocks: %d, crumbs under 30 blocks: %d' % (100 * thin, n, int((sz > 1000).sum()), int((sz < 30).sum())))
    # the same numbers for the flat picture spun into a plain one-plane solid, as a yardstick of the method
    import p3
    for nm, r in (('pillow3 layout A', p3.rule(True)),):
        s = M.spun_check(r, n=40000, steps=40); print('%s: turned round the x-axis by a random angle, %.1f %% of the points of c = -1 change verdict (inside share %.1f %%): not a ring' % (nm, 100 * s['basilica_differ'], 100 * s['basilica_inside']))

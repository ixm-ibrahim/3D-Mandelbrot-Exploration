"""A HAND-BUILT solid, not the solid of any squaring rule: the 'necklace' arrangement (NOTES.md, part 4, D2 and D6).

    python out/r21/prover/t6_necklace.py  ->  out/r21/prover/t6_necklace.png, t6_necklace.txt

It answers one question only: is there ANY solid whose cut along the flat page is exactly the flat Mandelbrot set,
with round buds all round the main body, no rings, and no one count of planes?  Yes, as a SET.  The recipe:
  1. Every body of the flat set that sits ON the x-axis (the main body, the period-2 disc, the period-4 disc, ...) is
     spun round the x-axis: these become one smooth body, balls and so on.  Spinning them makes no ring.
  2. Every limb that hangs OFF the x-axis (a bud that touches one of those bodies, with everything that grows on it)
     would become a ring if spun.  Instead it is 'puffed' in its own sheet (each disc of the flat set becomes a ball:
     thickness sqrt(d (2 r - d)), d = distance to the edge of the disc, r = the disc's inner radius) and that puffed
     limb is repeated N times round the x-axis, N = as many as fit side by side:  N = the even number nearest to
     pi * (height of the bud above the x-axis) / (1.3 * radius of the bud), at least 2.  One copy sits on the flat
     page.  N is different for every limb, so no two necklaces share their planes except the flat page itself.
  3. On the flat page itself the orbit is the true flat orbit, so the flat cut is exact by construction.
The 'rule' that the library draws is a look-up in a table made from the flat set: it only parks an inside point at 0.
"""
import os, sys, time
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, 'out', 'r21', 'lib')); sys.path.insert(0, HERE)
import mem as M

X0, X1, R1, HH = -2.1, 0.7, 1.3, 0.002
KAPPA = 1.3
out = []


def say(t=''):
    print(t); sys.stdout.flush(); out.append(t)


def build():
    """The table: for every pixel of the upper half of the flat picture: axis body? which limb? puff thickness; and N per limb."""
    xs = np.arange(X0, X1 + HH / 2, HH); rs = np.arange(0.0, R1 + HH / 2, HH)
    a, b = np.meshgrid(xs, rs); c = (a + 1j * b).ravel(); z = c.copy(); idx = np.arange(c.size)
    for _ in range(2500):
        z = z * z + c[idx]; keep = (z.real ** 2 + z.imag ** 2) < 36.0; idx, z = idx[keep], z[keep]
    inset = np.zeros(c.size, bool); inset[idx] = True
    per = np.zeros(c.size, np.int32); z0 = z.copy(); zz = z.copy(); todo = np.ones(idx.size, bool)
    for p in range(1, 97):                                                             # the period of the cycle the orbit has settled on
        zz = zz * zz + c[idx]; hit = todo & (np.abs(zz - z0) < 1e-5); per[idx[hit]] = p; todo &= ~hit
    per = per.reshape(a.shape); inset = inset.reshape(a.shape)
    lab = np.zeros(a.shape, np.int32); nlab = 0
    for p in np.unique(per[per > 0]):                                                  # a body = a connected patch of one period
        l, n = ndimage.label(per == p, structure=np.ones((3, 3)))
        size = ndimage.sum(np.ones_like(l), l, index=np.arange(n + 1)); l = np.where(size[l] >= 12, l, 0)
        lab[l > 0] = l[l > 0] + nlab; nlab += n
    # the rim of every body settles too slowly to get a period: give each such pixel the body nearest to it (within 12 pixels)
    dist, (ii, jj) = ndimage.distance_transform_edt(lab == 0, return_indices=True)
    lab = np.where((lab == 0) & inset & (dist <= 12), lab[ii, jj], lab)
    edge = np.zeros(a.shape, bool)
    for sh, ax in ((1, 0), (-1, 0), (1, 1), (-1, 1)):
        edge |= lab != np.roll(lab, sh, axis=ax)
    edge[0] = False                                                                    # the x-axis is not an edge: the lower half mirrors the upper
    edt = ndimage.distance_transform_edt(~edge) * HH                                   # distance to the edge of the pixel's own body
    rad = ndimage.maximum(edt, lab, index=np.arange(nlab + 1)); rad[0] = 0.0
    pos = ndimage.maximum_position(edt, lab, index=np.arange(nlab + 1))
    axis_labels = np.unique(lab[:3][lab[:3] > 0])
    axis = np.isin(lab, axis_labels)
    # limbs: start from the buds that touch an axis body, then grow through everything of the flat set that hangs on them
    to_axis = ndimage.distance_transform_edt(~axis) * HH
    prim = np.array([p for p in range(1, nlab + 1) if p not in set(axis_labels.tolist()) and rad[p] >= 4 * HH and to_axis[pos[p]] <= 1.5 * rad[p] + 3 * HH], np.int32)
    limb = np.where(np.isin(lab, prim), lab, 0)
    rest = inset & ~axis
    for _ in range(900):
        grown = ndimage.maximum_filter(limb, size=3); new = (limb == 0) & rest & (grown > 0)
        if not new.any():
            break
        limb[new] = grown[new]
    nn = np.zeros(nlab + 1, np.int32)
    for p in prim:
        rho = pos[p][0] * HH; nn[p] = max(2, 2 * int(round(np.pi * rho / (2 * KAPPA * rad[p]))))
    g = np.sqrt(np.clip(edt * (2 * rad[lab] - edt), 0, None))                          # the puff: a disc becomes a ball
    big = sorted(prim, key=lambda p: -rad[p])[:10]
    say('table: %d x %d pixels of %.3f; %d bodies, %d of them on the x-axis; %d limbs off the x-axis' % (a.shape[1], a.shape[0], HH, nlab, len(axis_labels), len(prim)))
    say('the ten biggest limbs: (x, height above the x-axis) radius -> copies round the x-axis')
    for p in big:
        say('   period %3d  (%.3f, %.3f)  radius %.3f  ->  N = %d' % (per[pos[p]], X0 + pos[p][1] * HH, pos[p][0] * HH, rad[p], nn[p]))
    return dict(axis=axis, limb=limb, g=g, nn=nn, shape=a.shape)


def make_rule(T):
    def inside(cx, cy, cz):
        rho = np.hypot(cy, cz); th = np.arctan2(cz, cy)
        i = np.rint(rho / HH).astype(np.int64); j = np.rint((cx - X0) / HH).astype(np.int64)
        ok = (i < T['shape'][0]) & (j >= 0) & (j < T['shape'][1]); i, j = np.where(ok, i, 0), np.where(ok, j, 0)
        ax = T['axis'][i, j] & ok; lb = np.where(ok, T['limb'][i, j], 0); n = np.maximum(T['nn'][lb], 1)
        pitch = 2 * np.pi / n; dth = th - pitch * np.rint(th / pitch)
        return ax | ((lb > 0) & (T['nn'][lb] > 0) & (rho * np.abs(np.sin(dth)) <= T['g'][i, j]))

    def step(x, y, z, st, k, cx, cy, cz):
        flag = st[0]
        if k == 0:
            page = (cz == 0) & (z == 0)
            flag = np.where(page, 1.0, np.where(inside(cx, cy, cz), 2.0, 0.0))
        X = np.where(flag == 1, x * x - y * y, np.where(flag == 2, -cx, 50.0))
        Y = np.where(flag == 1, 2 * x * y, np.where(flag == 2, -cy, 0.0))
        Z = np.where(flag == 1, 0.0, np.where(flag == 2, -cz, 0.0))
        return X, Y, Z, (flag,)
    return M.Rule('necklace', 'HAND-BUILT (no squaring rule): bodies on the x-axis spun, every limb off it puffed and repeated as often as fits', step, lambda n: (np.zeros(n),))


def main():
    np.seterr(all='ignore')
    t0 = time.time(); T = build(); say('(table %.0f s)' % (time.time() - t0))
    r = make_rule(T)
    f = M.flat_check(r, n=20000); say('flat page: verdicts that differ from the flat orbit: Mandelbrot %d of %d' % (f['mandelbrot'], f['of']))
    s = M.spun_check(r, n=20000, steps=3); say('turned by a random angle round the x-axis: %.2f%% of verdicts change (inside: %.2f%% of the box)' % (100 * s['mandel_differ'], 100 * s['mandel_inside']))
    w, h, nd = 620, 470, 400; tiles = []
    for cam, nm in (((0.45, 0.5, 1.0), 'the whole solid, eye at (0.45, 0.5, 1)'), ((1.0, 0.25, 0.25), 'seen almost along the x-axis, eye at (1, 0.25, 0.25)')):
        dep, px = M.solid(r, None, w, h, nd, 3, cam=cam); tiles.append((nm, M.shade_solid(dep, px))); say('solid %s (%.0f s)' % (nm, time.time() - t0))
    dep, px = M.solid(r, None, w, h, nd, 3, centre=(-0.12, 0.62, 0.0), half_w=0.45, cam=(0.3, 1.0, 0.5)); tiles.append(('close-up of the period-3 necklace', M.shade_solid(dep, px)))
    cuts = [('cut along the flat page', M.shade(np.where(M.cut_axis(r, 0.0, 440, 410, 60) >= 60, 3, 0), 3)),
            ('cut along the sheet turned 11.25', M.shade(np.where(M.cut_axis(r, 11.25, 440, 410, 3) >= 3, 3, 0), 3)),
            ('cut across the x-axis at x = -0.12', M.shade(np.where(M.cut_across(r, -0.12, 410, 3) >= 3, 3, 0), 3))]
    pad = 8; W = pad + 3 * (w + pad); H = 60 + h + 36 + 410 + 16
    im = Image.new('RGB', (W, H), (12, 14, 20)); d = ImageDraw.Draw(im)
    d.text((pad, 6), 'HAND-BUILT, not from any squaring rule: the "necklace" arrangement', fill=(240, 240, 245), font=M.font(20))
    d.text((pad, 34), 'bodies on the x-axis are spun; every limb off the x-axis is puffed into balls and repeated round the x-axis as often as fits (a different count for every limb)', fill=(170, 175, 190), font=M.font(13))
    for i, (nm, img) in enumerate(tiles):
        x = pad + i * (w + pad); d.text((x, 58), nm, fill=(235, 220, 170), font=M.font(14)); im.paste(Image.fromarray(img), (x, 80))
    x = pad
    for nm, img in cuts:
        d.text((x, 80 + h + 8), nm, fill=(235, 220, 170), font=M.font(14)); im.paste(Image.fromarray(img), (x, 80 + h + 30)); x += img.shape[1] + pad
    im.save(os.path.join(HERE, 't6_necklace.png')); say('(%.0f s)' % (time.time() - t0))
    open(os.path.join(HERE, 't6_necklace.txt'), 'w', encoding='utf-8').write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()

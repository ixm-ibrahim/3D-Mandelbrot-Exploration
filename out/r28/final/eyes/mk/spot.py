"""The eyes: one spot of a 3D view in detail. For the sampled rays in a box of the picture: the colour painted, where
pick() stopped, and what my own walk finds on that ray (first solid stretch of 2 px or more; first solid point).
  python out/r28/final/eyes/mk/spot.py <tag> <view> x0 y0 x1 y1"""
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import recipe, walk
tag, name = sys.argv[1:3]; x0, y0, x1, y1 = map(int, sys.argv[3:7])
m, dep, met, img = walk.load(tag, name)
top = 2 * m['k']['bt']; rho = m['k']['brho']; grid = m['k']['bgrid']; rounds = m['k']['bit']
ro = np.array(m['ro']); pix = m['pix']; bound = m['bound']
ii, jj, rd = walk.rays_of(m)
ST = m['STEP']
sel = np.nonzero((ii * ST >= x0) & (ii * ST <= x1) & (jj * ST >= y0) & (jj * ST <= y1))[0]
print('view %s: p %.2f rho %.4f grid %d depth %d; eye %s; pixel = %.5f x distance' % (name, 100 / (top - 1), rho, grid, rounds, np.round(ro, 4), pix))
for k in sel:
    b = rd[k] @ ro; hh = b * b - ro @ ro + bound * bound
    s_out = -b + np.sqrt(hh) if hh > 0 else 0
    s_in = max(-b - np.sqrt(max(hh, 0)), 1e-4)
    n = int(np.log(max(s_out / s_in, 1.0001)) / np.log(1 + 0.25 * pix)) + 1
    s = s_in * (1 + 0.25 * pix) ** np.arange(n)
    P = ro + rd[k] * s[:, None]
    v = recipe.verdict(P, top, rho, grid, rounds)
    v300 = None
    so = v != 0
    first = s[so.argmax()] if so.any() else None
    # the first stretch
    txt = 'no solid point on the ray'
    if first is not None:
        a = so.argmax(); e = a
        while e < n and so[e]:
            e += 1
        kind = 'reaches a wall' if (v[a:e] == 1).any() else 'undecided only'
        txt = 'first solid at %.5f, for %.1f px (%s)' % (first, (e - a) * 0.25, kind)
    d = dep[k]
    col = tuple(int(c) for c in img[int(jj[k] * ST), int(ii[k] * ST)])
    stop = ''
    if d > 0:
        Ps = ro + rd[k] * d
        vs = int(recipe.verdict(Ps[None, :], top, rho, grid, rounds)[0]); v3 = int(recipe.verdict(Ps[None, :], top, rho, grid, 300)[0])
        stop = '; pick stops at %.5f (%s px before my first solid), there my verdict %d at the page depth, %d at 300 rounds; page met %.2f px' % (d, '%.1f' % ((first - d) / (pix * d)) if first else '-', vs, v3, met[k])
    else:
        stop = '; pick stops nowhere'
    print('  pixel (%d, %d) colour %s: %s%s' % (ii[k] * ST, jj[k] * ST, col, txt, stop))

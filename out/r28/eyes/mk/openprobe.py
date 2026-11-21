"""The eyes: the stops of a 3D view that mk/walk.py calls IN THE OPEN (nothing solid at the stop, at 78 probes
within 2.5 px, at 3000 random probes within 3 px), looked at harder: 400000 more random probes within 1.5 px of
each, at the page's depth and with 3000 rounds. A ball much smaller than a pixel slips through 3000 probes; the
page's own measure (the distance to the nearest ball its search meets) is printed beside it.
  python out/r28/eyes/mk/openprobe.py <tag> <view> [view ...]   -> logs/openprobe-<tag>.txt (appended)"""
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import recipe, walk
tag = sys.argv[1]; out = []
for name in sys.argv[2:]:
    m, dep, met, img = walk.load(tag, name)
    top = 2 * m['k']['bt']; rho = m['k']['brho']; grid = m['k']['bgrid']; rounds = m['k']['bit']
    ro = np.array(m['ro']); pix = m['pix']; ST = m['STEP']
    ii, jj, rd = walk.rays_of(m)
    sol = lambda P: recipe.solid(P, top, rho, grid, rounds)
    hidx = np.nonzero(dep > 0)[0]
    Pst = ro + rd[hidx] * dep[hidx, None]; one = pix * dep[hidx]
    dirs = np.array([[a, b, c] for a in (-1, 0, 1) for b in (-1, 0, 1) for c in (-1, 0, 1) if a or b or c], dtype=float); dirs /= np.linalg.norm(dirs, axis=1)[:, None]
    nearb = sol(Pst).copy()
    for kk in (0.8, 1.6, 2.5):
        left = np.nonzero(~nearb)[0]
        if left.size == 0:
            break
        nearb[left] = sol((Pst[left][:, None, :] + kk * one[left][:, None, None] * dirs[None]).reshape(-1, 3)).reshape(left.size, -1).any(axis=1)
    left = np.nonzero(~nearb)[0]
    rng = np.random.default_rng(28); still = []
    for a in left:
        v = rng.normal(size=(3000, 3)); v /= np.linalg.norm(v, axis=1)[:, None]; v *= (rng.random(3000) ** (1 / 3))[:, None] * 3.0
        if not sol(Pst[a] + one[a] * v).any():
            still.append(a)
    out.append('%s (size %.2f, second sphere %.2f %%, grid %d, depth %d): %d stops; nothing solid at 78 probes: %d; nothing at 3000 more: %d' % (name, 100 / (top - 1), 100 * rho, grid, rounds, hidx.size, left.size, len(still)))
    for a in still:
        found = 0; nearest = None; n = 0
        for _ in range(8):
            v = rng.normal(size=(50000, 3)); v /= np.linalg.norm(v, axis=1)[:, None]; r = (rng.random(50000) ** (1 / 3)) * 1.5; v *= r[:, None]
            s = sol(Pst[a] + one[a] * v); n += 50000
            if s.any():
                found += int(s.sum()); d = float(r[s].min()); nearest = d if nearest is None else min(nearest, d)
        k = hidx[a]
        out.append('   pixel (%d, %d): of %d probes within 1.5 px, solid at %d%s; the page\'s own measure %.2f px; painted %s'
                   % (ii[k] * ST, jj[k] * ST, n, found, ', the nearest %.2f px from the stop' % nearest if found else ' -> NOTHING: A STOP IN THE OPEN', met[k], tuple(int(c) for c in img[int(jj[k] * ST), int(ii[k] * ST)])))
text = '\n'.join(out) + '\n'
open(os.path.join(walk.EYES, 'logs', 'openprobe-%s.txt' % tag), 'a', encoding='utf-8', newline='\n').write(text)
print(text)

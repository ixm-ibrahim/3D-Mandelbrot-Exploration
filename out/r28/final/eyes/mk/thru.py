"""The eyes: the rays of a 3D view that the page stops BEHIND a solid stretch, one by one. Each sampled ray that
stops is walked again in quarter-pixel steps from the eye to its stop (my recipe at the page's depth and with 300
rounds). Listed: every ray whose walk meets a solid stretch of 2 px or more that ends more than 2 px before the stop.
  python out/r28/final/eyes/mk/thru.py <tag> <view> [view ...]   -> logs/thru-<tag>.txt (appended)"""
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import recipe, walk
tag = sys.argv[1]
out = []
for name in sys.argv[2:]:
    m, dep, met, img = walk.load(tag, name)
    top = 2 * m['k']['bt']; rho = m['k']['brho']; grid = m['k']['bgrid']; rounds = m['k']['bit']
    ro = np.array(m['ro']); pix = m['pix']; bound = m['bound']; ST = m['STEP']
    ii, jj, rd = walk.rays_of(m)
    hits = np.nonzero(dep > 0)[0]
    # a first pass at half-pixel steps over all stopping rays, 3000 rays at a time, from 60 % of the stop's distance or the entry into the Drawing radius
    b = rd @ ro; hh = b * b - ro @ ro + bound * bound
    s_in = np.maximum(-b - np.sqrt(np.maximum(hh, 0)), 1e-4)
    found = []
    q = 1 + 0.5 * pix
    for a0 in range(0, hits.size, 2000):
        part = hits[a0:a0 + 2000]
        n = int(np.ceil(np.log(np.maximum(dep[part] / s_in[part], 1.0001)).max() / np.log(q))) + 1
        n = min(n, 30000)
        sv = dep[part, None] / q ** np.arange(n)[None, ::-1]            # ends exactly at the stop
        ok = sv >= s_in[part, None]
        P = ro[None, None, :] + rd[part][:, None, :] * sv[:, :, None]
        so = np.zeros(sv.shape, dtype=bool)
        so[ok] = recipe.solid(P[ok], top, rho, grid, rounds)
        for r in range(part.size):
            row = so[r]
            if not row.any():
                continue
            # stretches of solid, as (start index, length)
            dz = np.diff(np.concatenate([[0], row.astype(np.int8), [0]]))
            st = np.nonzero(dz == 1)[0]; en = np.nonzero(dz == -1)[0]
            for s0, e0 in zip(st, en):
                length = (e0 - s0) * 0.5
                behind = (n - e0) * 0.5              # pixels between the end of the stretch and the stop
                if length >= 2 and behind > 2:
                    seg = P[r, s0:e0]
                    v300 = recipe.verdict(seg, top, rho, grid, 300)
                    found.append((int(ii[part[r]] * ST), int(jj[part[r]] * ST), length, behind, int((v300 == 1).sum()), int((v300 == 2).sum()), int((v300 == 0).sum()), float(dep[part[r]]), float(met[part[r]]),
                                  tuple(int(c) for c in img[int(jj[part[r]] * ST), int(ii[part[r]] * ST)])))
    out.append('%s (size %.2f, second sphere %.2f %%, grid %d, depth %d): %d of %d stopping rays pass a solid stretch of 2 px or more and stop more than 2 px behind it' % (name, 100 / (top - 1), 100 * rho, grid, rounds, len(set((f[0], f[1]) for f in found)), hits.size))
    for f in found[:60]:
        out.append('   pixel (%d, %d): solid for %.1f px, the stop %.1f px behind its end; of the stretch at 300 rounds: %d points reach a wall, %d still undecided, %d OUTSIDE; stop at %.4f from the eye, the page\'s own measure there %.2f px; painted %s'
                   % f)
text = '\n'.join(out) + '\n'
with open(os.path.join(walk.EYES, 'logs', 'thru-%s.txt' % tag), 'a', encoding='utf-8', newline='\n') as f:
    f.write(text)
print(text)

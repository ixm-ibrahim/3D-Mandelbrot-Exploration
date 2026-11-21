"""The eyes: is a dark pixel of a 3D picture the BACKGROUND (a ray that stopped nowhere) or a dark place of the solid?
The background of a picture is one colour to within 1 (measured on pixels where no ray stops all round). For every
sampled pixel well inside the stops (pick() stops on it and on its 8 sampled neighbours) the picture's colour is
compared with it: within 1 = painted exactly as background.
Also counted over ALL pixels of the picture: pixels within 1 of the background that lie well inside the stops' area
(grown from the sampled grid), as connected patches, with the largest patches.
  python out/r28/fix/eyes/mk/bgexact.py <tag> <view> [view ...]"""
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import walk
tag = sys.argv[1]
for name in sys.argv[2:]:
    m, dep, met, img = walk.load(tag, name)
    nx, ny, ST = m['nx'], m['ny'], m['STEP']
    H, W = img.shape[:2]
    hit = (dep > 0).reshape(ny, nx)
    def eroded(g, n=1):
        for _ in range(n):
            e = g.copy()
            e[1:, :] &= g[:-1, :]; e[:-1, :] &= g[1:, :]; e[:, 1:] &= g[:, :-1]; e[:, :-1] &= g[:, 1:]
            e[1:, 1:] &= g[:-1, :-1]; e[:-1, :-1] &= g[1:, 1:]; e[1:, :-1] &= g[:-1, 1:]; e[:-1, 1:] &= g[1:, :-1]
            e[0, :] = False; e[-1, :] = False; e[:, 0] = False; e[:, -1] = False
            g = e
        return g
    dh, dm = eroded(hit), eroded(~hit)
    col = img[np.minimum(np.arange(ny) * ST, H - 1)][:, np.minimum(np.arange(nx) * ST, W - 1)]
    if dm.sum() > 20:
        bg = np.median(col[dm], axis=0); spread = int(np.abs(col[dm] - bg).max())
    else:
        bg = np.array([8, 13, 18]); spread = -1
    d = np.abs(col - bg).max(axis=2)
    # all pixels: the area well inside the stops, at full resolution (each sample stands for its 4 x 4 block)
    full = np.kron(eroded(hit, 2), np.ones((ST, ST), dtype=bool))[:H, :W]
    fd = np.abs(img - bg).max(axis=2)
    exact = (fd <= 1) & full[:fd.shape[0], :fd.shape[1]]
    # connected patches of exact-background pixels (4-neighbours), by a simple flood
    seen = np.zeros_like(exact); sizes = []
    ys, xs = np.nonzero(exact)
    for y0, x0 in zip(ys, xs):
        if seen[y0, x0]:
            continue
        stack = [(y0, x0)]; seen[y0, x0] = True; n = 0; sy = sx = 0
        while stack:
            y, x = stack.pop(); n += 1; sy += y; sx += x
            for yy, xx in ((y + 1, x), (y - 1, x), (y, x + 1), (y, x - 1)):
                if 0 <= yy < H and 0 <= xx < W and exact[yy, xx] and not seen[yy, xx]:
                    seen[yy, xx] = True; stack.append((yy, xx))
        sizes.append((n, sx // n, sy // n))
    sizes.sort(reverse=True)
    print('%-26s background %s (spread %d over %d samples) | sampled pixels well inside the stops: %d; within 6 of the background %d, within 1 of it %d, pure black (0, 0, 0) %d | all pixels well inside the stops: %d, within 1 of the background: %d in %d patches; patches of 9 pixels or more: %d; largest (pixels at x, y): %s'
          % (name, [int(x) for x in bg], spread, int(dm.sum()), int(dh.sum()), int((dh & (d <= 6)).sum()), int((dh & (d <= 1)).sum()), int((dh & (col.sum(axis=2) == 0)).sum()),
             int(full.sum()), int(exact.sum()), len(sizes), sum(1 for s in sizes if s[0] >= 9), ', '.join('%d at (%d, %d)' % s for s in sizes[:5])))

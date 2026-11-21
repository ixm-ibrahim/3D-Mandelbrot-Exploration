"""The eyes: the saved picture against pick() for one 3D view, in detail: where a pixel well inside the stops is
painted like the background, and where a pixel well outside them is not, with colours and the pick's depth.
  python out/r28/fix/eyes/mk/picdiff.py <tag> <view>"""
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import walk
tag, name = sys.argv[1:3]
m, dep, met, img = walk.load(tag, name)
nx, ny, ST = m['nx'], m['ny'], m['STEP']
hit = (dep > 0).reshape(ny, nx)
col = img[np.minimum(np.arange(ny) * ST, img.shape[0] - 1)][:, np.minimum(np.arange(nx) * ST, img.shape[1] - 1)]
def eroded(g):
    e = g.copy()
    e[1:, :] &= g[:-1, :]; e[:-1, :] &= g[1:, :]; e[:, 1:] &= g[:, :-1]; e[:, :-1] &= g[:, 1:]
    e[1:, 1:] &= g[:-1, :-1]; e[:-1, :-1] &= g[1:, 1:]; e[1:, :-1] &= g[:-1, 1:]; e[:-1, 1:] &= g[1:, :-1]
    e[0, :] = False; e[-1, :] = False; e[:, 0] = False; e[:, -1] = False
    return e
dh, dm = eroded(hit), eroded(~hit)
bg = np.median(col[dm], axis=0)
d = np.abs(col - bg).max(axis=2)
print('background', bg)
print('well inside the stops, painted within 6 of the background:')
for y, x in np.argwhere(dh & (d <= 6))[:40]:
    # the darkest and brightest of the 9 x 9 picture pixels round it
    blk = img[max(0, y * ST - 4):y * ST + 5, max(0, x * ST - 4):x * ST + 5].reshape(-1, 3)
    print('   pixel (%d, %d) colour %s, depth %.3f, met %.2f px; the 9 x 9 pixels round it: %d of %d within 6 of the background, brightest %s' % (x * ST, y * ST, tuple(col[y, x]), dep.reshape(ny, nx)[y, x], met.reshape(ny, nx)[y, x], int((np.abs(blk - bg).max(axis=1) <= 6).sum()), len(blk), tuple(blk[blk.sum(axis=1).argmax()])))
print('well outside the stops, painted more than 24 from the background:')
for y, x in np.argwhere(dm & (d > 24))[:40]:
    print('   pixel (%d, %d) colour %s' % (x * ST, y * ST, tuple(col[y, x])))

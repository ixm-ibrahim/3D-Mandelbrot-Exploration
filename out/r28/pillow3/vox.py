"""Round 28, pillow3: a solid as a grid of small blocks, computed once per set, then looked at from any eye.

    python out/r28/pillow3/vox.py make <tag> <h> [steps]     tag: m1 (c = -1), rab (rabbit), rabm (its mirror image c -> conj c),
                                                             m075, sie; add '-plain' for the plain re-timing, '-lean' for lean.py's layout
    grid(tag) -> (inside [nx, ny, nz] bool, x, y, z centres)   (the mirror halves are filled in)

A block is inside when the orbit of its centre never leaves the ball of radius 6 in `steps` steps (M.stay).
Uses what is measured in checks.py: every solid with c in the flat plane is its own mirror image in the flat plane;
for c on the x-axis also in the upright plane through the x-axis. Only one half (quarter) is computed.
"""
import os, sys, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import p3
M = p3.M
CACHE = os.path.join(HERE, 'cache')
CS = {'m1': (-1.0, 0.0), 'rab': M.RABBIT[:2], 'rabm': (M.RABBIT[0], -M.RABBIT[1]), 'm075': (-0.75, 0.0), 'sie': M.SIEGEL[:2]}


def the_rule(tag):
    if tag.endswith('-plain'):
        return p3.rule(False)
    if '-lean' in tag:
        import lean
        return lean.rule(float(tag.split('-lean')[1] or 1.0))
    return p3.rule(True)


def make(tag, h, steps=40, full=False):
    c = CS[tag.split('-')[0]]; r = the_rule(tag)
    R = 0.5 * (1 + np.sqrt(1 + 4 * np.hypot(*c))) + 2 * h          # nothing outside this ball stays
    n = int(np.ceil(R / h)); ax = (np.arange(-n, n) + 0.5) * h
    quarter = (c[1] == 0.0) and not full
    ys = ax[n:] if quarter else ax; zs = ax if full else ax[n:]
    ins = np.zeros((ax.size, ys.size, zs.size), bool); t0 = time.time()
    for i, x in enumerate(ax):
        Y, Z = np.meshgrid(ys, zs, indexing='ij'); ok = (x * x + Y * Y + Z * Z) < R * R
        if ok.any():
            v = np.zeros(Y.shape, bool)
            v[ok] = M.stay(r, np.full(ok.sum(), x), Y[ok], Z[ok], c[0], c[1], 0.0, steps) >= steps
            ins[i] = v
        if i % 50 == 0:
            print('  slab %d of %d, %.0f s' % (i, ax.size, time.time() - t0)); sys.stdout.flush()
    os.makedirs(CACHE, exist_ok=True)
    np.savez_compressed(os.path.join(CACHE, '%s-%g.npz' % (tag, h)), ins=np.packbits(ins), shape=ins.shape, h=h, n=n, quarter=quarter, full=full, steps=steps, c=c)
    print('%s: h %g, %d steps, grid %s, inside %d blocks, volume %.4f, %.0f s' % (tag, h, steps, ins.shape, ins.sum(), ins.sum() * h ** 3 * (4 if quarter else (1 if full else 2)), time.time() - t0))


def grid(tag, h):
    d = np.load(os.path.join(CACHE, '%s-%g.npz' % (tag, h)))
    sh = tuple(d['shape']); ins = np.unpackbits(d['ins'])[:np.prod(sh)].reshape(sh).astype(bool); n = int(d['n']); hh = float(d['h'])
    if not bool(d['full']):
        ins = np.concatenate([ins[:, :, ::-1], ins], 2)
    if bool(d['quarter']):
        ins = np.concatenate([ins[:, ::-1], ins], 1)
    ax = (np.arange(-n, n) + 0.5) * hh
    return ins, ax, ax, ax


def frame2(cam, up):
    """Screen right, screen up, depth for an eye at cam with the given direction kept upright on the screen."""
    p = np.array(cam, float); p /= np.linalg.norm(p)
    e1 = np.cross(np.array(up, float), p); e1 /= np.linalg.norm(e1)
    return e1, np.cross(p, e1), -p


def depth_map(ins, ax, cam, w=900, hgt=680, half_w=1.75, centre=(0.0, 0.0, 0.0), sub=0.5, up=(0.0, 1.0, 0.0)):
    """First block met on each line of sight (orthographic, eye at cam, as M.solid). Returns (depth, pixel size)."""
    e1, e2, e3 = frame2(cam, up); h = ax[1] - ax[0]; n = ax.size; lo = ax[0] - 0.5 * h
    us = np.linspace(-half_w, half_w, w); vs = np.linspace(half_w * hgt / w, -half_w * hgt / w, hgt)
    U, V = np.meshgrid(us, vs); depth = np.full((hgt, w), np.inf); live = np.ones((hgt, w), bool)
    P0 = [centre[i] + U * e1[i] + V * e2[i] for i in range(3)]
    Rb = np.abs(ax).max() * 1.75
    for dk in np.arange(-Rb, Rb, h * sub):
        idx = [np.floor((P0[i][live] + dk * e3[i] - lo) / h).astype(np.int64) for i in range(3)]
        ok = (idx[0] >= 0) & (idx[0] < n) & (idx[1] >= 0) & (idx[1] < n) & (idx[2] >= 0) & (idx[2] < n)
        hit = np.zeros(ok.shape, bool); hit[ok] = ins[idx[0][ok], idx[1][ok], idx[2][ok]]
        if hit.any():
            li = np.flatnonzero(live); depth.ravel()[li[hit]] = dk; live.ravel()[li[hit]] = False
    return depth, us[1] - us[0]


def picture(ins, ax, cam, **kw):
    d, px = depth_map(ins, ax, cam, **kw)
    return M.shade_solid(d, px)


if __name__ == '__main__':
    if sys.argv[1] == 'make':
        make(sys.argv[2], float(sys.argv[3]), int(sys.argv[4]) if len(sys.argv) > 4 else 40, full=(len(sys.argv) > 5 and sys.argv[5] == 'full'))

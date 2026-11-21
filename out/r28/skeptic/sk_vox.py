"""Round 28, skeptic of Track B: my own solids as blocks, computed WITHOUT using any mirror (the whole box, every block).

    PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1 python -W ignore out/r28/skeptic/sk_vox.py make <what> <h> [steps]
        what: A-m1, B-m1, plain-m1, A-rab, balls        (m1: c = -1; rab: the rabbit; balls: Balls on balls, square grid, t = 1.40)
    load(what, h) -> (inside [nx, ny, nz] bool, xs, ys, zs block centres)

A block is inside when the orbit of its centre never leaves the ball of radius 6 in `steps` steps (my own loop).
"""
import os, sys, time
sys.dont_write_bytecode = True
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, 'out', 'r28', 'pillow3'))
CACHE = os.path.join(HERE, 'cache')
RABBIT = (-0.122561, 0.744862)
CSET = {'m1': (-1.0, 0.0), 'rab': RABBIT}


def step_fn(layout):
    import p3
    if layout == 'A':
        r = p3.rule(True)
    elif layout == 'plain':
        r = p3.rule(False)
    else:
        import lean; r = lean.rule(50.0)
    return lambda x, y, z: r.step(x, y, z, (), 0, 0.0, 0.0, 0.0)[:3]


def inside_pts(F, x, y, z, c, steps, r2=36.0):
    """True where the orbit of the point never leaves the ball of radius 6 in `steps` steps."""
    sh = np.shape(x); x, y, z = (np.array(v, float).ravel() for v in (x, y, z)); n = x.size; idx = np.arange(n)
    for _ in range(steps):
        X, Y, Z = F(x, y, z); x, y, z = X + c[0], Y + c[1], Z
        keep = (x * x + y * y + z * z) < r2                       # a NaN drops out here; sk_checks.py looks for NaN on its own
        idx, x, y, z = idx[keep], x[keep], y[keep], z[keep]
        if idx.size == 0:
            break
    out = np.zeros(n, bool); out[idx] = True
    return out.reshape(sh)


def balls_inside(x, y, z, rounds=24, t=1.40, k2=1.05):
    """Balls on balls, written from the recipe in docs/ROUND28.md section 1.1 (square grid, two equal spheres), my own
    numpy; the frame is one sphere inversion about (0, 0, 1) of the object's own space, k^2 = 1.05 (out/r25/klein/tree.py)."""
    top = 2 * t
    ux, uy, uz = y, z, x - k2 / 2; d = ux * ux + uy * uy + uz * uz; d = np.where(d > 0, d, 1e-300)
    mx, my, mz = k2 * ux / d, k2 * uy / d, 1 + k2 * uz / d
    inside = np.zeros(mx.shape, bool); live = np.ones(mx.shape, bool)
    for _ in range(rounds):
        hit = live & ((mz < 0) | (mz > top)); inside |= hit; live &= ~hit
        mx = mx - np.round(mx); my = my - np.round(my)
        rb = mx * mx + my * my + mz * mz; rt = mx * mx + my * my + (mz - top) ** 2
        inb = live & (rb < 1); itp = live & ~inb & (rt < 1); live &= (inb | itp)
        sb = 1 / np.where(rb > 0, rb, 1.0); st = 1 / np.where(rt > 0, rt, 1.0)
        mx, my, mz = np.where(inb, mx * sb, np.where(itp, mx * st, mx)), np.where(inb, my * sb, np.where(itp, my * st, my)), np.where(inb, mz * sb, np.where(itp, top + (mz - top) * st, mz))
        if not live.any():
            break
    return inside


def make(what, h, steps=40):
    t0 = time.time(); os.makedirs(CACHE, exist_ok=True)
    if what == 'balls':
        xs = (np.arange(-int(np.ceil(1.32 / h)), int(np.ceil(1.32 / h))) + 0.5) * h; ys = (np.arange(-int(np.ceil(0.9 / h)), int(np.ceil(0.9 / h))) + 0.5) * h; zs = ys
        ins = np.zeros((xs.size, ys.size, zs.size), bool)
        for i, x in enumerate(xs):
            Y, Z = np.meshgrid(ys, zs, indexing='ij'); ins[i] = balls_inside(np.full(Y.shape, x), Y, Z)
    else:
        layout, cs = what.split('-'); c = CSET[cs]; F = step_fn(layout)
        R = 0.5 * (1 + np.sqrt(1 + 4 * np.hypot(*c))) + 2 * h; n = int(np.ceil(R / h)); xs = (np.arange(-n, n) + 0.5) * h; ys = xs; zs = xs
        ins = np.zeros((xs.size, ys.size, zs.size), bool); Y, Z = np.meshgrid(ys, zs, indexing='ij')
        for i, x in enumerate(xs):
            ok = (x * x + Y * Y + Z * Z) < R * R
            if ok.any():
                px, py, pz = np.full(int(ok.sum()), x), Y[ok], Z[ok]; idx = np.arange(px.size)
                for _ in range(steps):
                    X, Yv, Zv = F(px, py, pz); px, py, pz = X + c[0], Yv + c[1], Zv
                    keep = (px * px + py * py + pz * pz) < 36.0; idx, px, py, pz = idx[keep], px[keep], py[keep], pz[keep]
                    if idx.size == 0:
                        break
                v = np.zeros(int(ok.sum()), bool); v[idx] = True; sl = np.zeros(Y.shape, bool); sl[ok] = v; ins[i] = sl
            if i % 40 == 0:
                print('  slab %d of %d, %.0f s' % (i, xs.size, time.time() - t0)); sys.stdout.flush()
    np.savez_compressed(os.path.join(CACHE, '%s-%g.npz' % (what, h)), ins=np.packbits(ins), shape=ins.shape, xs=xs, ys=ys, zs=zs, h=h, steps=steps)
    print('%s: h %g, %d steps, grid %s, inside %d blocks, volume %.4f, %.0f s' % (what, h, steps, ins.shape, int(ins.sum()), ins.sum() * h ** 3, time.time() - t0))


def load(what, h):
    d = np.load(os.path.join(CACHE, '%s-%g.npz' % (what, h))); sh = tuple(d['shape'])
    return np.unpackbits(d['ins'])[:int(np.prod(sh))].reshape(sh).astype(bool), d['xs'], d['ys'], d['zs']


if __name__ == '__main__':
    if sys.argv[1] == 'make':
        make(sys.argv[2], float(sys.argv[3]), int(sys.argv[4]) if len(sys.argv) > 4 else 40)

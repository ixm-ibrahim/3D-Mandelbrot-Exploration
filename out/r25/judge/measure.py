"""Judge, round 25: one solid, many numbers. My own script; the sections' rules are only loaded.

    python out/r25/judge/measure.py job [job ...]        job = rule:set[:tilt]   e.g.  skew:c1   twin_tri:rabbit:3

For one rule and one c (optionally lifted out of the flat plane by `tilt` degrees) it makes a grid of blocks
(side 0.015, box x -1.8..1.8, y and z -1.5..1.5, 50 steps) and prints:
  size      share of the box inside; the same with 30 / 60 / 150 steps on random points (does it leak?)
  lop       share of the solid that has NO partner under: up-down mirror, half turn about the upright axis,
            left-right mirror y -> -y (0 = perfectly even; a flat Julia set of z^2 + c keeps the half turn, and the
            y mirror when c is on the x-axis)
  pieces    separate pieces (blocks joined by faces): how many, share of the solid in the biggest, crumbs
            (pieces under 20 blocks): how many and their share
  skin      how fast the skin grows when the blocks are halved (2.0 = smooth; more = rough at every size)
  extra     share of the solid that lies OUTSIDE the one-plane solid of the same c (material off the flat picture's
            own bodies), and the share of the one-plane solid that is missing
  eggs      the extra material cut into bodies (one block shaved off to cut the necks): for each body of at least
            150 blocks the longest over the shortest axis (1.0 = a ball)
The grid is kept in out/r25/judge/cache/.
"""
import os, sys, time
import numpy as np
from scipy import ndimage as ndi
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import jl
M = jl.M
CACHE = os.path.join(HERE, 'cache'); os.makedirs(CACHE, exist_ok=True)
H = 0.015; BOX = (-1.8, 1.8, -1.5, 1.5, -1.5, 1.5); STEPS = 50
BASE = {'cube': 'oneplane3', 'tri3': 'oneplane3', 'pearl': 'pearl-line', 'pearl-eisen': 'pearl-line'}


def get(name):
    if name == 'oneplane3':
        return jl.section('wall').PL.rule_oneplane(3)
    if name in ('tri3', 'tri2'):                 # the judge's one probe: round 24's two flat triangles with the power 3 (tri2 = as built in round 24)
        for p in (('out', 'r24', 'me'), ('out', 'r23', 'me')):
            sys.path.insert(0, os.path.join(jl.ROOT, *p))
        import tri as T
        return T.tri_rule(int(name[3]), name=name, label='even spacing on two flat triangles, power %s' % name[3])
    if name == 'zip1fix':                        # the zip rule with points on the upright axis nudged off it (the rule returns NaN there)
        r0 = jl.get('zip1')
        def step(x, y, z, st, k, cx, cy, cz):
            ax = (np.abs(x) + np.abs(y)) < 1e-150
            return r0.step(np.where(ax, 1e-150, x), y, z, st, k, cx, cy, cz)
        return M.Rule('zip1fix', 'zip, upright axis nudged', step, init=r0.init)
    if name == 'pearl-line':
        return jl.section('klein').rule('line')
    if name == 'alongonce':
        a = jl.get('along'); p = jl.get('oneplane')
        return M.Rule('alongonce', 'along at the first squaring, one plane after', lambda x, y, z, st, k, cx, cy, cz: (a if k == 0 else p).step(x, y, z, st, k, cx, cy, cz), init=lambda n: ())
    return jl.get(name)


def cval(setname, tilt):
    if setname == 'none':
        return (0.0, 0.0, 0.0)
    return jl.tilt(jl.SETS[setname], tilt)


def grid(name, setname, tilt=0.0, steps=None):
    steps = steps or (14 if name.startswith('pearl') else STEPS)
    f = os.path.join(CACHE, 'g-%s-%s-%g.npz' % (name, setname, tilt))
    xs = np.arange(BOX[0] + H / 2, BOX[1], H); ys = np.arange(BOX[2] + H / 2, BOX[3], H); zs = np.arange(BOX[4] + H / 2, BOX[5], H)
    if os.path.exists(f):
        d = np.load(f); return np.unpackbits(d['bits'])[:xs.size * ys.size * zs.size].reshape(xs.size, ys.size, zs.size).astype(bool), xs, ys, zs
    r = get(name); c = cval(setname, tilt); ins = np.zeros((xs.size, ys.size, zs.size), bool)
    for i0 in range(0, xs.size, 16):
        X, Y, Z = np.meshgrid(xs[i0:i0 + 16], ys, zs, indexing='ij')
        ins[i0:i0 + 16] = M.stay(r, X, Y, Z, c[0], c[1], c[2], steps) >= steps
    np.savez_compressed(f, bits=np.packbits(ins.ravel()))
    return ins, xs, ys, zs


def skin(ins):
    p = np.pad(ins, 1); c = p[1:-1, 1:-1, 1:-1]
    nb = p[:-2, 1:-1, 1:-1] & p[2:, 1:-1, 1:-1] & p[1:-1, :-2, 1:-1] & p[1:-1, 2:, 1:-1] & p[1:-1, 1:-1, :-2] & p[1:-1, 1:-1, 2:]
    return int((c & ~nb).sum())


def axes_ratio(idx):
    """longest over shortest axis of a cloud of block indices (from its spread in the three main directions)."""
    q = idx - idx.mean(0); w = np.linalg.eigvalsh(q.T @ q / len(q) + np.eye(3) / 12.0)
    return float(np.sqrt(w[2] / w[0]))


def job(spec):
    parts = spec.split(':'); name, setname = parts[0], parts[1]; tilt = float(parts[2]) if len(parts) > 2 else 0.0
    t0 = time.time(); r = get(name); c = cval(setname, tilt); steps = 14 if name.startswith('pearl') else STEPS
    ins, xs, ys, zs = grid(name, setname, tilt); V = int(ins.sum()); tot = ins.size
    out = ['%s  c = %s  (%s%s)' % (name, '(%.4f, %.4f, %.4f)' % c, setname, ', lifted %g degrees' % tilt if tilt else '')]
    # size and leak
    rng = np.random.default_rng(77); n = 300000; v = rng.uniform([BOX[0], BOX[2], BOX[4]], [BOX[1], BOX[3], BOX[5]], size=(n, 3))
    if name.startswith('pearl'):
        cnt = M.stay(r, v[:, 0], v[:, 1], v[:, 2], 0.0, 0.0, 0.0, 40); leak = [(cnt >= s).mean() for s in (8, 14, 40)]; lab = '8 / 14 / 40'
    else:
        cnt = M.stay(r, v[:, 0], v[:, 1], v[:, 2], c[0], c[1], c[2], 150); leak = [(cnt >= s).mean() for s in (30, 60, 150)]; lab = '30 / 60 / 150'
    out.append('  size    share of the box inside %.4f (grid, %d steps); random points at %s steps: %.4f / %.4f / %.4f' % (V / tot, steps, lab, *leak))
    if V == 0:
        out.append('  EMPTY'); print('\n'.join(out)); sys.stdout.flush(); return
    # lopsidedness (the grid is its own mirror image in all three directions)
    ud = (ins & ~ins[:, :, ::-1]).sum() / V; ht = (ins & ~ins[::-1, ::-1, :]).sum() / V; my = (ins & ~ins[:, ::-1, :]).sum() / V; mx = (ins & ~ins[::-1, :, :]).sum() / V
    up = ins[:, :, zs > 0].sum() / max(1, ins[:, :, zs < 0].sum())
    out.append('  lop     no partner under: up-down mirror %.3f | half turn about the upright axis %.3f | mirror y -> -y %.3f | mirror x -> -x %.3f | volume above / below %.3f' % (ud, ht, my, mx, up))
    if name in ('cube', 'oneplane3', 'tri3'):
        a = 2 * np.pi / 3; co, si = np.cos(a), np.sin(a); ii = cnt >= 60
        p = M.stay(r, co * v[ii, 0] - si * v[ii, 1], si * v[ii, 0] + co * v[ii, 1], v[ii, 2], c[0], c[1], c[2], 60) >= 60
        out.append('          (cube) no partner under a third of a turn about the upright axis: %.3f' % (1 - p.mean()))
    # pieces
    lab_, k = ndi.label(ins); sz = np.bincount(lab_.ravel())[1:]; big = sz.max() / V; cr = sz < 20
    out.append('  pieces  %d pieces; biggest holds %.3f of the solid; second %.3f; crumbs (under 20 blocks) %d holding %.4f' % (
        k, big, (np.sort(sz)[-2] / V if k > 1 else 0.0), int(cr.sum()), sz[cr].sum() / V))
    # skin growth
    s1 = skin(ins); s2 = skin(ins[::2, ::2, ::2]); s4 = skin(ins[::4, ::4, ::4])
    out.append('  skin    skin blocks %d (side h), %d (2h), %d (4h): growth exponent %.2f (h against 2h), %.2f (2h against 4h)' % (s1, s2, s4, np.log2(s1 / max(s2, 1)), np.log2(s2 / max(s4, 1))))
    # against the one-plane solid of the same c
    bname = BASE.get(name, 'oneplane')
    if name not in ('oneplane', 'oneplane3', 'pearl-line'):
        base, _, _, _ = grid(bname, setname, tilt); Vb = int(base.sum())
        ext = ins & ~base; out.append('  extra   outside the %s solid: %.3f of this solid; of the %s solid %.3f is missing here; size against %s %.2f' % (
            bname, ext.sum() / V, bname, (base & ~ins).sum() / max(Vb, 1), bname, V / max(Vb, 1)))
        er = ndi.binary_erosion(ext, iterations=1); lab2, k2 = ndi.label(er); sz2 = np.bincount(lab2.ravel())[1:]
        good = np.nonzero(sz2 >= 150)[0]; ratios = []; sizes = []
        for g in good[np.argsort(-sz2[good])][:40]:
            idx = np.argwhere(lab2 == g + 1).astype(float); ratios.append(axes_ratio(idx)); sizes.append(int(sz2[g]))
        if ratios:
            rr = np.array(ratios)
            out.append('  eggs    %d extra bodies of 150 blocks or more (after shaving one block); longest / shortest axis: median %.2f, quartiles %.2f .. %.2f, biggest five: %s (blocks %s)' % (
                len(rr), np.median(rr), np.percentile(rr, 25), np.percentile(rr, 75), ' '.join('%.2f' % t for t in rr[:5]), ' '.join(str(t) for t in sizes[:5])))
        else:
            out.append('  eggs    no extra body of 150 blocks or more')
        out.append('          extra pieces of every size after shaving: %d; of them under 20 blocks: %d' % (k2, int((sz2 < 20).sum())))
    out.append('  (%.0f s)' % (time.time() - t0))
    print('\n'.join(out)); sys.stdout.flush()


if __name__ == '__main__':
    for spec in sys.argv[1:]:
        try:
            job(spec)
        except Exception as e:
            import traceback; traceback.print_exc(); print(spec, 'FAILED', e); sys.stdout.flush()

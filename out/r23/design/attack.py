"""Round 23, design: trying to make 'cones1' fail on the rabbit (and the same numbers for 'alongonce' and 'oneplane').

    python out/r23/design/attack.py [rule,rule,...]      -> prints; attack.log is the saved output

1. Finer blocks. Side 0.01, box x -1.1..1.1, y -1.2..1.2, z 0.005..1.0 (the upper half only: every rule here is the
   same above and below), 120 steps. Bodies off the flat picture: lumps left after peeling 3 blocks (0.03) that lie
   wholly above z = 0.05. For each: is it joined to the big piece when blocks must share a FACE (the strict way),
   and its long : thick ratio. Also the share of the volume that is loose (not in the biggest piece, strict way).
2. Slow leak: share of a random box inside after 30, 80, 200, 400 steps.
3. c moved a little: the rabbit's c times 1.01 and 0.99, and turned 1 degree out of the flat plane: volume at 80 steps.
"""
import os, sys, time
import numpy as np
from scipy import ndimage as ndi
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import rules as R
M = R.M
S6 = ndi.generate_binary_structure(3, 1)


def widths(idx, h):
    p = np.array(idx, float).T * h; cov = np.cov(p.T) if p.shape[0] > 3 else np.eye(3) * 1e-9
    ev = np.sort(np.clip(np.linalg.eigvalsh(cov), 0, None))[::-1]
    return 2 * np.sqrt(5 * ev) + 4 * h


def fine(name, c, h=0.01, steps=120):
    r = R.get(name); xs = np.arange(-1.1 + h / 2, 1.1, h); ys = np.arange(-1.2 + h / 2, 1.2, h); zs = np.arange(h / 2, 1.0, h)
    ins = np.zeros((xs.size, ys.size, zs.size), bool)
    for i0 in range(0, xs.size, 20):
        X, Y, Z = np.meshgrid(xs[i0:i0 + 20], ys, zs, indexing='ij')
        ins[i0:i0 + 20] = M.stay(r, X, Y, Z, c[0], c[1], c[2], steps) >= steps
    lab, k = ndi.label(ins, structure=S6); size = np.bincount(lab.ravel())[1:]; main = int(np.argmax(size)) + 1
    lab26, k26 = ndi.label(ins, structure=np.ones((3, 3, 3), bool)); size26 = np.bincount(lab26.ravel())[1:]; main26 = int(np.argmax(size26)) + 1
    core = ndi.binary_erosion(ins, structure=S6, iterations=3); clab, ck = ndi.label(core, structure=S6); csize = np.bincount(clab.ravel())[1:]
    objs = ndi.find_objects(clab); off = []
    for b in range(1, ck + 1):
        if csize[b - 1] < 20:
            continue
        sl = objs[b - 1]; sub = clab[sl] == b; idx = np.nonzero(sub); zlo = zs[sl[2].start + idx[2].min()] - 3 * h
        if zlo > 0.05:
            wd = widths(idx, h); off.append((float(wd[0] / wd[2]), int(lab[sl][sub][0]) == main, float(csize[b - 1] * h ** 3), int(lab26[sl][sub][0]) == main26))
    return {'vol': float(ins.sum() * h ** 3), 'loose': float(1 - size.max() / max(ins.sum(), 1)), 'pieces20': int((size >= 20).sum()),
            'off': len(off), 'off_joined': sum(o[1] for o in off), 'ratios': sorted(round(o[0], 2) for o in off),
            'off_joined26': sum(o[3] for o in off), 'loose26': float(1 - size26.max() / max(ins.sum(), 1))}


if __name__ == '__main__':
    names = sys.argv[1].split(',') if len(sys.argv) > 1 else ['oneplane', 'alongonce', 'cones1']
    c0 = np.array(M.RABBIT); t0 = time.time(); rng = np.random.default_rng(5)
    v = rng.uniform([-1.8, -1.4, -1.4], [1.8, 1.4, 1.4], size=(200000, 3)); a = np.radians(1.0)
    for nm in names:
        r = R.get(nm)
        f = fine(nm, M.RABBIT)
        print('%-9s corner contact counted too: loose share %.4f, bodies off the flat picture joined %d' % (nm, f['loose26'], f['off_joined26']))
        print('%-9s fine blocks (upper half): volume %.4f, loose share (faces only) %.4f, pieces of 20+ blocks %d | bodies off the flat picture %d, joined %d, long : thick %s  [%.0f s]'
              % (nm, f['vol'], f['loose'], f['pieces20'], f['off'], f['off_joined'], f['ratios'], time.time() - t0)); sys.stdout.flush()
        n = M.stay(r, v[:, 0], v[:, 1], v[:, 2], c0[0], c0[1], c0[2], 400)
        print('          share of a box inside after 30 / 80 / 200 / 400 steps: %.5f %.5f %.5f %.5f' % tuple((n >= s).mean() for s in (30, 80, 200, 400)))
        row = []
        for tag, c in (('c x 1.01', c0 * 1.01), ('c x 0.99', c0 * 0.99), ('c turned 1 degree out', (c0[0], c0[1] * np.cos(a), c0[1] * np.sin(a)))):
            row.append('%s: %.5f' % (tag, (M.stay(r, v[:, 0], v[:, 1], v[:, 2], c[0], c[1], c[2], 80) >= 80).mean()))
        print('          share inside at 80 steps with ' + ' | '.join(row) + '  [%.0f s]' % (time.time() - t0)); sys.stdout.flush()

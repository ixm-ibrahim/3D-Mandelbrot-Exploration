"""Working numbers: a few orbits written out step by step.  python out/r22/lump/trails1.py [cset]"""
import sys
import numpy as np
import lumplib as L

cs = sys.argv[1] if len(sys.argv) > 1 else 'rabbit'; c = L.CSETS[cs]
STARTS = [(-0.276, 0.480, 0.25), (-0.276, 0.480, 0.05), (0.0, 0.0, 0.6), (0.04, -0.30, 0.65), (0.3, 0.3, 0.5), (-0.5, 0.2, 0.45), (0.1, 0.5, 0.3)]
P = np.array(STARTS).T


def trail(r, p, n):
    x, y, z = (p[i].copy() for i in range(3)); m = x.size; cx, cy, cz = (np.full(m, t) for t in c); st = tuple(r.init(m)); out = [np.stack([x, y, z])]
    for k in range(n):
        o = r.step(x, y, z, st, k, cx, cy, cz); st = tuple(o[3]); x, y, z = o[0] + cx, o[1] + cy, o[2] + cz; out.append(np.stack([x, y, z]))
    return np.stack(out)                                       # (n + 1, 3, m)


if __name__ == '__main__':
    for rn in ['along', 'oneplane', 'alongmem.c_wake1', 'lathe']:
        r = L.rule(rn); T = trail(r, P, 16)
        print('==', rn)
        for j, s in enumerate(STARTS):
            line = []
            for k in range(17):
                x, y, z = T[k, :, j]; rr = np.sqrt(x * x + y * y + z * z)
                if rr > 6 or not np.isfinite(rr):
                    line.append('OUT'); break
                line.append('(%.2f %.2f %.3f)' % (x, y, z))
            print('  start', s, '\n     ', ' '.join(line))

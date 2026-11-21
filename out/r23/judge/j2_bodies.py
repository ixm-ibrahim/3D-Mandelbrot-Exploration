"""Round 23, judge, check 2: the bodies off the flat picture, on fine blocks. My loop, my grid, my measures.

    python out/r23/judge/j2_bodies.py <rabbit|basilica> [rule,rule,...]

Blocks of side 0.008, the UPPER half only (z from 0 to 1; j3 checks that above and below are alike), 100 steps.
  volume        of the upper half
  thin          share of the volume that goes when everything thinner than about 0.05 is removed (peel 3 blocks, grow back 3)
  not holding   share of the volume in pieces that do not reach the flat plane: (a) blocks must share a face, (b) a corner is enough
  bodies off the flat picture: lumps left after peeling 4 blocks (0.032) that lie wholly above z = 0.05, at least 3e-5 in volume.
     for each: volume, long : thick (from the lump's own three widths, after growing it back to full size inside the
     shape), where its middle is, and how it holds on to the bodies of the flat picture ("grounded" = every piece
     that reaches the flat plane):
        joined   = it is in a grounded piece when blocks must share a FACE
        touching = only when a shared corner or edge is enough (the contact is no wider than a block, 0.008)
        floating = neither; then the GAP is the smallest distance from it to any grounded-by-corners piece
"""
import os, sys, time
import numpy as np
from scipy import ndimage as ndi
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import jl as L
S6 = ndi.generate_binary_structure(3, 1); S26 = np.ones((3, 3, 3), bool)
H = 0.008; PEEL = 4


def measure(name, c, box, steps=100):
    r = L.get(name); ins, xs, ys, zs = L.blocks(r, c, H, box, steps)
    cell = H ** 3; tot = int(ins.sum()); out = {'vol': tot * cell}
    if tot == 0:
        return out
    opened = ndi.binary_dilation(ndi.binary_erosion(ins, structure=S6, iterations=3), structure=S6, iterations=3) & ins
    out['thin'] = 1 - opened.sum() / tot
    lab6, k6 = ndi.label(ins, structure=S6); s6 = np.bincount(lab6.ravel())[1:]; main6 = int(np.argmax(s6)) + 1
    lab26, k26 = ndi.label(ins, structure=S26); s26 = np.bincount(lab26.ravel())[1:]; main26 = int(np.argmax(s26)) + 1
    out['loose6'] = 1 - s6.max() / tot; out['loose26'] = 1 - s26.max() / tot
    out['pieces'] = int((s26 * cell >= 3e-5).sum())
    core = ndi.binary_erosion(ins, structure=S6, iterations=PEEL); clab, ck = ndi.label(core, structure=S6); cs = np.bincount(clab.ravel())[1:]
    objs = ndi.find_objects(clab)
    g6 = np.zeros(k6 + 1, bool); g6[np.unique(lab6[:, :, 0])] = True; g6[0] = False            # pieces that reach the flat plane
    g26 = np.zeros(k26 + 1, bool); g26[np.unique(lab26[:, :, 0])] = True; g26[0] = False
    out['ungrounded6'] = float((ins & ~g6[lab6]).sum() / tot); out['ungrounded26'] = float((ins & ~g26[lab26]).sum() / tot)
    dist = ndi.distance_transform_edt(~g26[lab26]) * H                                         # distance to the grounded shape
    off = []
    for b in range(1, ck + 1):
        sl = objs[b - 1]; sub = clab[sl] == b; idx = np.nonzero(sub)
        zlo = zs[sl[2].start + idx[2].min()] - PEEL * H
        if zlo <= 0.05:
            continue
        # grow the lump back to its full size inside the shape (not past it)
        pad = tuple(slice(max(s.start - PEEL - 1, 0), s.stop + PEEL + 1) for s in sl)
        seed = clab[pad] == b; full = ndi.binary_dilation(seed, structure=S6, iterations=PEEL, mask=ins[pad])
        vol = float(full.sum() * cell)
        if vol < 3e-5:
            continue
        p = np.array(np.nonzero(full), float).T * H; ev = np.sort(np.clip(np.linalg.eigvalsh(np.cov(p.T)), 0, None))[::-1]
        wd = 2 * np.sqrt(5 * ev)
        gi = np.nonzero(full); cen = (xs[pad[0].start + int(np.mean(gi[0]))], ys[pad[1].start + int(np.mean(gi[1]))], zs[pad[2].start + int(np.mean(gi[2]))])
        off.append({'vol': vol, 'ratio': float(wd[0] / max(wd[2], 1e-9)), 'cen': cen, 'j6': bool(g6[lab6[pad][full]].any()),
                    'j26': bool(g26[lab26[pad][full]].any()), 'gap': float(dist[pad][full].min())})
    off.sort(key=lambda o: -o['vol']); out['off'] = off
    return out


if __name__ == '__main__':
    which = sys.argv[1]
    names = sys.argv[2].split(',') if len(sys.argv) > 2 else ['oneplane', 'alongonce', 'cones1', 'cones2', 'cones', 'along', 'twoplane']
    SHAPES = {'rabbit': (L.RABBIT, (-1.1, 1.1, -1.2, 1.2, 0.0, 1.0)), 'basilica': (L.BAS, (-1.75, 1.75, -1.0, 1.0, 0.0, 1.0)),
              'four': ((0.282271, 0.530061, 0.0), (-1.2, 1.2, -1.2, 1.2, 0.0, 1.0)),          # middle of the bud with four bodies round each meeting point
              'five': ((-0.504340, 0.562766, 0.0), (-1.3, 1.3, -1.2, 1.2, 0.0, 1.0)),         # middle of a bud with five
              'siegel': (L.SIEGEL, (-1.3, 1.3, -1.2, 1.2, 0.0, 1.0))}
    c, box = SHAPES[which]
    t0 = time.time()
    for nm in names:
        m = measure(nm, c, box)
        if 'off' not in m:
            print('%-10s %s: empty' % (nm, which)); continue
        o = m['off']
        print('%-10s %s, upper half: volume %.4f | thin %.1f %% | share of the volume NOT holding on to the bodies of the flat picture: by faces %.1f %%, by corners %.1f %% | pieces %d | bodies off the flat picture: %d  [%.0f s]'
              % (nm, which, m['vol'], 100 * m['thin'], 100 * m['ungrounded6'], 100 * m['ungrounded26'], m['pieces'], len(o), time.time() - t0))
        for q in o[:14]:
            print('             volume %.5f, long : thick %.2f, middle at (%.2f, %.2f, %.2f), %s'
                  % (q['vol'], q['ratio'], q['cen'][0], q['cen'][1], q['cen'][2], 'JOINED' if q['j6'] else ('TOUCHING at a point' if q['j26'] else 'FLOATING, gap %.3f' % q['gap'])))
        if o:
            big = [q for q in o if q['vol'] >= 1e-3]; rr = [q['ratio'] for q in o]; rb = [q['ratio'] for q in big] or [0.0]
            cnt = lambda qs: (sum(q['j6'] for q in qs), sum((not q['j6']) and q['j26'] for q in qs), sum(not q['j26'] for q in qs))
            print('             summary, all %d: joined %d, touching %d, floating %d; long : thick median %.2f, largest %.2f | the %d of volume over 0.001: joined %d, touching %d, floating %d; long : thick largest %.2f'
                  % ((len(o),) + cnt(o) + (float(np.median(rr)), max(rr), len(big)) + cnt(big) + (max(rb),)))
        sys.stdout.flush()

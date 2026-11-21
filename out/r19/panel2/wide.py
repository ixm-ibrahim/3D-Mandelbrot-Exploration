"""Round 19, panel2: the WIDE close cut. Point by point, 80 steps, the skin of one rule on one set looked at in
8 half-planes through the x-axis x 5 skin points x 3 widths = 120 tiles. Only the tiles are made and kept here
(wide/<rule>-<set>.npz); the number is worked out from the kept tiles by hairnum.py, so the measure can be changed
without cutting anything again.

    python out/r19/panel2/wide.py <rule>:<set> [<rule>:<set> ...]        rule 'flat' = the flat set itself
    python out/r19/panel2/wide.py <rule>:<set>:<extra angle>,<extra angle>  adds the rule's own mid angles

'flat' is the one-plane rule cut at 0 degrees (the flat plane, which is the flat set exactly), 15 skin points.
"""
import os, sys, json, time
import numpy as np
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, 'out', 'r16', 'bench'))
import bench as B
import rules as R

CW, CH, CSTEPS = 420, 294, 80
ANGLES = (11.25, 22.5, 33.75, 45.0, 56.25, 67.5, 78.75, 90.0)      # degrees from the flat plane; 22.5 and 11.25 were the old panel's
OFFS = (-0.5, 0.35, -0.8, -0.2, 0.7)                               # skin points (the old panel's two first)
FLAT_OFFS = tuple(np.round(np.linspace(-0.9, 0.9, 15), 3))
WID = (0.1, 0.02, 0.004)
RAB = (-0.122561, 0.744862, 0.0)
# tag -> (c, half box, thickest place of the flat set it is scaled by)
SETS = dict(
    basilica=((-1.0, 0.0, 0.0), 1.7, 0.4714), sanmarco=((-0.75, 0.0, 0.0), 1.6, None), airplane=((-1.754878, 0.0, 0.0), 0.42, None),
    cauliflower=((0.25, 0.0, 0.0), 1.15, None), rabbit=(RAB, 1.4, None), siegel=((-0.390541, -0.586788, 0.0), 1.45, None),
    bas_yz=((-1.0, 0.05, 0.03), 1.7, 'basilica'), bas_zy=((-1.0, 0.03, 0.05), 1.7, 'basilica'),
    sm_yz=((-0.75, 0.01, 0.02), 1.6, 'sanmarco'), rab_up=((-0.122561, 0.744862, 0.015), 1.4, 'rabbit'))


def thick_of(tag):
    c, L, t = SETS[tag]
    base = t if isinstance(t, str) else tag
    r = json.load(open(os.path.join(HERE, 'results', 'oneplane.json')))['sets'][base]['flat']['thickest']
    return float(r)


def go(rule, tag, extra=()):
    flat = rule == 'flat'
    F = R.get('oneplane' if flat else rule); c, L, _ = SETS[tag]
    scale = thick_of(tag) / 0.47
    angles = (0.0,) if flat else tuple(ANGLES) + tuple(a for a in extra if a not in ANGLES)
    offs = FLAT_OFFS if flat else OFFS
    masks = []; meta = []
    for ang in angles:
        a = np.radians(ang); ca, sa = np.cos(a), np.sin(a)
        xs = np.linspace(-L, L, 401); ss = np.linspace(0.0, L, 201)[1:]
        X, Sg = np.meshgrid(xs, ss, indexing='ij')
        ins, _ = B.inside(F, X, Sg * ca, Sg * sa, c=c, steps=CSTEPS)
        lab, k = ndimage.label(ins)
        if k == 0 or np.bincount(lab.ravel())[1:].max() < 40:
            meta.append(dict(angle=ang, note='nothing of the solid in this half-plane')); continue
        big = lab == (1 + int(np.argmax(np.bincount(lab.ravel())[1:])))
        d = ndimage.distance_transform_edt(np.pad(big, ((1, 1), (0, 1)))[1:-1, :-1]); i, j = np.unravel_index(int(np.argmax(d)), d.shape)
        dmax = float(d[i, j] * (xs[1] - xs[0])); s0 = float(ss[j])
        for off in offs:
            x0 = float(xs[i] + off * dmax)
            s = np.linspace(s0, 1.3 * L, 20001)
            i1, _ = B.inside(F, np.full_like(s, x0), s * ca, s * sa, c=c, steps=CSTEPS)
            o = np.flatnonzero(~i1)
            if not o.size or o[0] == 0:
                meta.append(dict(angle=ang, off=float(off), note='no skin found')); continue
            e = float(s[o[0]])
            for q, hw0 in enumerate(WID):
                hw = hw0 * scale
                x, sg = np.meshgrid(np.linspace(x0 - hw, x0 + hw, CW), np.linspace(e + 0.7 * hw, e - 0.7 * hw, CH))
                it, _dt = B.inside(F, x, sg * ca, sg * sa, c=c, steps=CSTEPS)
                meta.append(dict(angle=ang, off=float(off), q=q, width=2 * hw, x0=x0, e=e, k=len(masks)))
                masks.append(np.packbits(it, axis=1))
    os.makedirs(os.path.join(HERE, 'wide'), exist_ok=True)
    np.savez_compressed(os.path.join(HERE, 'wide', '%s-%s.npz' % (rule, tag)), masks=np.array(masks, np.uint8), meta=json.dumps(meta))
    return len(masks)


if __name__ == '__main__':
    for arg in sys.argv[1:]:
        t0 = time.time(); parts = arg.split(':'); extra = tuple(float(x) for x in parts[2].split(',')) if len(parts) > 2 else ()
        p = os.path.join(HERE, 'wide', '%s-%s.npz' % (parts[0], parts[1]))
        if os.path.exists(p):
            print('have', arg, flush=True); continue
        n = go(parts[0], parts[1], extra); print('%s: %d tiles (%.0f s)' % (arg, n, time.time() - t0), flush=True)

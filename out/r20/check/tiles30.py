"""Round 20 check: panel2's close-cut tiles at the rule's OWN angles, which panel2's eight half-planes do not hold:
30 degrees (half way between its planes; panel2 has 90, which is the same place only when c is in the flat plane),
60 degrees (a copy plane: must be as clean as the flat set) and 150 degrees (for the nudged sets).
Same code path as out/r19/panel2/wide.py (its go() with other angles), kept in out/r20/check/wide30/ so that panel2's
own folder is not touched. Scored with panel2's hair number.
python out/r20/check/tiles30.py <rule> <set> [<set> ...]
"""
import os, sys, json, time
import numpy as np
from scipy import ndimage
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, 'out', 'r19', 'panel2'))
import wide as Wd
import hairnum as H
B = Wd.B; R = Wd.R
ANG = (30.0, 60.0, 150.0)


def go(rule, tag):
    F = R.get(rule); c, L, _ = Wd.SETS[tag]; scale = Wd.thick_of(tag) / 0.47
    masks = []; meta = []
    for ang in ANG:
        a = np.radians(ang); ca, sa = np.cos(a), np.sin(a)
        xs = np.linspace(-L, L, 401); ss = np.linspace(0.0, L, 201)[1:]
        X, Sg = np.meshgrid(xs, ss, indexing='ij')
        ins, _ = B.inside(F, X, Sg * ca, Sg * sa, c=c, steps=Wd.CSTEPS)
        lab, k = ndimage.label(ins)
        if k == 0 or np.bincount(lab.ravel())[1:].max() < 40:
            meta.append(dict(angle=ang, note='nothing of the solid in this half-plane')); continue
        big = lab == (1 + int(np.argmax(np.bincount(lab.ravel())[1:])))
        d = ndimage.distance_transform_edt(np.pad(big, ((1, 1), (0, 1)))[1:-1, :-1]); i, j = np.unravel_index(int(np.argmax(d)), d.shape)
        dmax = float(d[i, j] * (xs[1] - xs[0])); s0 = float(ss[j])
        for off in Wd.OFFS:
            x0 = float(xs[i] + off * dmax)
            s = np.linspace(s0, 1.3 * L, 20001)
            i1, _ = B.inside(F, np.full_like(s, x0), s * ca, s * sa, c=c, steps=Wd.CSTEPS)
            o = np.flatnonzero(~i1)
            if not o.size or o[0] == 0:
                meta.append(dict(angle=ang, off=float(off), note='no skin found')); continue
            e = float(s[o[0]])
            for q, hw0 in enumerate(Wd.WID):
                hw = hw0 * scale
                x, sg = np.meshgrid(np.linspace(x0 - hw, x0 + hw, Wd.CW), np.linspace(e + 0.7 * hw, e - 0.7 * hw, Wd.CH))
                it, _dt = B.inside(F, x, sg * ca, sg * sa, c=c, steps=Wd.CSTEPS)
                sc = H.score(it)
                meta.append(dict(angle=ang, off=float(off), q=q, width=2 * hw, x0=x0, e=e, k=len(masks), fins=sc['fins'], film_pct=sc['film_pct'], old=sc['old']))
                masks.append(np.packbits(it, axis=1))
    os.makedirs(os.path.join(HERE, 'wide30'), exist_ok=True)
    np.savez_compressed(os.path.join(HERE, 'wide30', '%s-%s.npz' % (rule, tag)), masks=np.array(masks, np.uint8), meta=json.dumps(meta))
    return meta


if __name__ == '__main__':
    rule = sys.argv[1]
    p = os.path.join(HERE, 'wide30', 'scores-%s.json' % rule); os.makedirs(os.path.join(HERE, 'wide30'), exist_ok=True)
    allr = json.load(open(p)) if os.path.exists(p) else {}
    for tag in sys.argv[2:]:
        t0 = time.time(); meta = go(rule, tag); rows = [m for m in meta if 'k' in m and m['fins'] is not None]
        res = {}
        for ang in ANG:
            rr = [m for m in rows if m['angle'] == ang]
            if rr:
                res[str(ang)] = dict(tiles=len(rr), thin_worst=max(m['fins'] for m in rr), film_worst=max(m['film_pct'] for m in rr), old_worst=max(m['old'] for m in rr),
                                     over=sum(1 for m in rr if m['fins'] > H.T_FINS or m['film_pct'] > H.T_FILM))
        allr[tag] = res; json.dump(allr, open(p, 'w'), indent=1)
        print('%s %s (%.0f s): ' % (rule, tag, time.time() - t0) + ' | '.join('%s deg: thin %.2f film %.1f %% old %.2f, %d of %d tiles over' % (a, v['thin_worst'], v['film_worst'], v['old_worst'], v['over'], v['tiles']) for a, v in res.items()), flush=True)

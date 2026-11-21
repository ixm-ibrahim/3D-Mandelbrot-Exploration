"""Second, sturdier check of task 1: instead of stepping 0.03 off the calculated skin along its normal (which goes
wrong where the skin is folded or the body is thin), push the RESTING POINT 6 % (and 15 %) beyond the place where it
stops attracting, take the c that belongs to it, and ask the solid what happens there.  python outray.py"""
import os, sys, json
import numpy as np
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import core as K
import rules as R
out = {}
for name in sys.argv[1:] or ['lathe', 'oneplane', 'along', 'twoplane']:
    F = R.get(name)
    th = (np.arange(181) + 0.5) * np.pi / 181; ph = np.arange(0, 91) * np.pi / 180
    S = K.skin(F, th=th, ph=ph); kind, ang = S['kind'], S['ang']; good = ~S['bad']
    w = np.sin(th)[:, None] * np.ones(kind.shape)
    r = {}
    for tag, fr in (('in_0.94', 0.94), ('out_1.06', 1.06), ('out_1.15', 1.15)):
        v = S['u'] * (fr / S['rho'])[..., None]; c = v - K.apply(F, v)
        per = K.periods(F, c, steps=2500)
        def dist(m):
            ww = w[m & good]; p = per[m & good]; tot = max(ww.sum(), 1e-30)
            return {k: round(float(ww[sel(p)].sum() / tot), 4) for k, sel in (('flies', lambda p: p == 0), ('p1', lambda p: p == 1), ('p2', lambda p: p == 2), ('p3', lambda p: p == 3), ('p4', lambda p: p == 4), ('p5plus', lambda p: p >= 5), ('never_repeats', lambda p: p == -1))}
        r[tag] = {'pair': dist(kind == 0), 'minus1': dist(kind == -1), 'plus1': dist(kind == 1)}
        if fr > 1:
            q = {}
            for pp, lev in ((3, 1 / 3), (4, 0.25), (5, 0.2)):
                m = (per == pp) & (kind == 0) & good; near = (kind == 0) & good & (np.abs(ang - lev) < 0.01)
                q['p%d' % pp] = {'cells': int(m.sum()), 'angle_10_50_90': [round(float(x), 3) for x in np.percentile(ang[m], [10, 50, 90])] if m.any() else None,
                                 'share_of_line_with_this_period_beyond': round(float((per[near] == pp).mean()), 3) if near.any() else None,
                                 'share_of_these_cells_within_0.02_turn_of_line': round(float((np.abs(ang[m] - lev) < 0.02).mean()), 3) if m.any() else None}
            m2 = (per == 2) & good
            q['p2'] = {'share_of_blue_patch_with_p2_beyond': round(float((per[(kind == -1) & good] == 2).mean()), 3) if ((kind == -1) & good).any() else None,
                       'share_of_p2_cells_on_blue_patch': round(float((kind[m2] == -1).mean()), 3) if m2.any() else None}
            r['match_' + tag] = q
            half = np.concatenate([per, per[:, -2::-1]], 1); full = np.concatenate([half, half[:, -2:0:-1]], 1)
            Image.fromarray(K.colour_of(full)).resize((540, 271), Image.NEAREST).save(os.path.join(HERE, 'tiles', '%s-ray-%s.png' % (name, tag)))
    out[name] = r; print(name, json.dumps(r), flush=True)
    json.dump(out, open(os.path.join(HERE, 'outray.json'), 'w'), indent=1)

"""Round 20 check: what the nudged sets do over a long time. For each nudged c and rule: the orbit of 0 (does it settle
on a cycle?), and of 20,000 points taken inside the solid's biggest body, the share still inside after 80 ... 3000 steps."""
import os, sys, json
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, 'out', 'r16', 'bench'))
import bench as B
import rules as R
SETS = dict(basilica=(-1.0, 0.0, 0.0), bas_yz=(-1.0, 0.05, 0.03), bas_zy=(-1.0, 0.03, 0.05), bas_small=(-1.0, 0.01, 0.006), bas_y=(-1.0, 0.058, 0.0), bas_30=(-1.0, 0.0505, 0.0292),
            sanmarco=(-0.75, 0.0, 0.0), sm_yz=(-0.75, 0.01, 0.02), rabbit=(-0.122561, 0.744862, 0.0), rab_up=(-0.122561, 0.744862, 0.015))
out = {}
rng = np.random.default_rng(11)
for rule in sys.argv[1:] or ['m_w3', 'oneplane', 'along', 'twoplane']:
    F = R.get(rule)
    for tag, c in SETS.items():
        # orbit of 0
        x = np.zeros(1); y = np.zeros(1); z = np.zeros(1); R2 = B.resc(c) ** 2; tr = []; left = None
        for k in range(6000):
            x, y, z = F(x, y, z); x = x + c[0]; y = y + c[1]; z = z + c[2]
            if x[0] ** 2 + y[0] ** 2 + z[0] ** 2 > R2:
                left = k + 1; break
            if k >= 5000:
                tr.append((x[0], y[0], z[0]))
        if left is None:
            tr = np.array(tr); per = None
            for p in (1, 2, 3, 4, 6, 8, 12):
                if np.abs(tr[p:] - tr[:-p]).max() < 1e-6:
                    per = p; break
            spread = float(np.ptp(tr, axis=0).max()); orb = 'settles on a cycle of %d' % per if per else 'never settles (wanders in a region %.3f across)' % spread
        else:
            orb = 'leaves at step %d' % left
        # a cloud of points inside the solid: start in a ball of radius 0.3 round the origin, keep those inside at 40 steps
        v = rng.normal(size=(3, 60000)); v *= 0.3 * rng.uniform(0, 1, 60000) ** (1 / 3) / np.sqrt((v * v).sum(0))
        ins, death = B.inside(F, v[0], v[1], v[2], c=c, steps=3000)
        base = ins | (death > 40)
        sh = {n: float((ins | (death > n))[base].mean()) for n in (80, 160, 320, 1000, 3000)}
        out['%s|%s' % (rule, tag)] = dict(orbit=orb, share=sh, n=int(base.sum()))
        print('%-8s %-9s orbit of 0 %s; of %d points inside at 40 steps, still inside at 80/160/320/1000/3000: %s' % (rule, tag, orb, base.sum(), ' '.join('%.3f' % sh[n] for n in (80, 160, 320, 1000, 3000))), flush=True)
        json.dump(out, open(os.path.join(HERE, 'nudge-%s.json' % '-'.join(sys.argv[1:] or ['all'])), 'w'), indent=1)

"""Hunter task 3 (claim C2): the turning count round the negative x-axis, and how much of the sphere of directions
lands mirror-reversed.   python out/r17/hunter/c2.py     -> c2.json, c2.txt
"""
import os, sys, json
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import core as K
import rules as R

names = ['lathe', 'oneplane', 'twoplane', 'wind2', 'away', 'along'] + sorted(k for k in R.RULES if k[:2] in ('p_', 'b_'))
if len(sys.argv) > 1:
    names = sys.argv[1:]


def turning(F, xs, eps, n=40001):
    phi = np.linspace(0, 2 * np.pi, n)
    X, Y, Z = F(np.full(n, xs), eps * np.cos(phi), eps * np.sin(phi))
    a = np.arctan2(Z, Y)
    d = np.diff(a); d = (d + np.pi) % (2 * np.pi) - np.pi
    side = np.hypot(Y, Z)
    return float(d.sum() / (2 * np.pi)), float(np.abs(d).max()), float(side.min() / eps), float(side.max() / eps)


out = {}
lines = ['%-11s %-32s %-32s %9s %9s %9s %9s %8s' % ('rule', 'turns round -x (eps 1e-3, .05, .3)', 'turns round +x', 'reversed', 'degree', 'covered', 'stretch', 'tear')]
for nm in names:
    F = R.get(nm)
    try:
        neg = [turning(F, -1.0, e) for e in (1e-3, 0.05, 0.3)]
        pos = [turning(F, 1.0, e) for e in (1e-3, 0.05, 0.3)]
        S = K.skin(F, 361, 720)
        sw = np.sin(S['th'])[:, None] * np.ones(S['det'].shape); sw[S['bad']] = 0; sw /= sw.sum()
        det = np.where(S['bad'], 0.0, S['det'])
        rev = float(sw[det < 0].sum()); deg = float((sw * det).sum() / 2); cov = float((sw * np.abs(det)).sum() / 2)
        st = float(np.nanmax(np.where(S['bad'], np.nan, S['sv'][..., 0]))); st99 = float(np.nanpercentile(np.where(S['bad'], np.nan, S['sv'][..., 0]), 99))
        out[nm] = dict(label=R.RULES[nm][1], turns_neg=[t[0] for t in neg], maxstep_neg=[t[1] for t in neg], side_minmax_neg=[t[2:] for t in neg],
                       turns_pos=[t[0] for t in pos], reversed_share=rev, degree=deg, covered=cov, max_stretch=st, stretch_99pct=st99,
                       tear=bool(max(t[1] for t in neg + pos) > 1.0))
        lines.append('%-11s %-32s %-32s %8.1f%% %9.2f %9.2f %9.2f %8s' % (nm, ' '.join('%+.2f' % t[0] for t in neg), ' '.join('%+.2f' % t[0] for t in pos),
                                                                    100 * rev, deg, cov, st, 'jump' if out[nm]['tear'] else '-'))
    except Exception as e:
        lines.append('%-11s failed: %r' % (nm, e))
    print(lines[-1], flush=True)
json.dump(out, open(os.path.join(HERE, 'c2.json'), 'w'), indent=1)
open(os.path.join(HERE, 'c2.txt'), 'w').write('\n'.join(lines) + '\n')

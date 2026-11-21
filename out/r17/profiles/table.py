"""Collect every number of this section into one markdown table (out/r17/profiles/table.md)."""
import os, sys, json
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, HERE); import screen as S
sys.path.insert(0, os.path.join(ROOT, 'out', 'r16', 'bench')); import bench as B
R = S.R
cover = json.load(open(os.path.join(HERE, 'cover.json')))
known_hair = {'along': 3.12, 'away': 17.0, 'twoplane': 0.04, 'oneplane': 0.00, 'wind2': 10.6}
order = ['oneplane', 'lathe', 'along', 'away', 'p_lin', 'p_ss', 'p_cot', 'p_half', 'p_n4', 'p_n8', 'p_n8c', 'p_h4', 'p_h16', 'p_tt1', 'p_tt4', 'p_tt16', 'p_tt64', 'p_tt128', 'p_tt256', 'p_tt1024',
         'p_aw_n8', 'p_aw_h4', 'p_aw_tt4', 'p_aw_tt16', 'p_aw_tt64', 'p_aw_tt256', 'p_aw_tt1024', 'twoplane']
def cliff(F, g=1e-3, n=200000):
    rng = np.random.default_rng(11); th = np.arccos(rng.uniform(-1, 1, n)); x = np.cos(th); rho = np.sin(th)
    d = np.minimum(g / 2 / np.maximum(rho, 1e-12), 0.7)
    a = np.stack(F(x, rho * np.cos(np.pi / 4 - d), rho * np.sin(np.pi / 4 - d)), 1); b = np.stack(F(x, rho * np.cos(np.pi / 4 + d), rho * np.sin(np.pi / 4 + d)), 1)
    return float(np.linalg.norm(a - b, axis=1).max())
rows = ['| rule | what it is | close cut: worst hair (limit 0.3) | bench, eight tests | cliff at gap 0.001 | net wraps / inside out | turned inside out | stretch, largest (flat rule = 1) |', '|---|---|---|---|---|---|---|---|']
for nm in order:
    F = R.get(nm); p = os.path.join(HERE, 'cc', nm + '.json'); j = json.load(open(p)) if os.path.exists(p) else None
    hair = j['hair_worst'] if j else known_hair.get(nm)
    res = B.load(nm); ver = B.verdicts(res) if res else None
    fails = [k for k, v in ver.items() if not v[0]] if ver else None
    bl = 'not run' if ver is None else ('passes all eight' if not fails else 'fails ' + ', '.join(fails))
    cv = cover.get(nm, {}); d = S.directions(F, n=60000)
    rows.append('| `%s` | %s | %s | %s | %.3g | %s | %s | %.1f |' % (nm, R.RULES[nm][1], 'n/a' if hair is None else '%.2f' % hair, bl, cliff(F),
                '%.0f / %.2f' % (round(cv['net']), cv['inside_out']) if cv else '', '%.1f %%' % cv['reversed_pct'] if cv else '', d['stretch_max']))
open(os.path.join(HERE, 'table.md'), 'w', encoding='utf-8').write('\n'.join(rows) + '\n'); print('\n'.join(rows))

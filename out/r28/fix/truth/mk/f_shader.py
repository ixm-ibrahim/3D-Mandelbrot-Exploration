"""Round 28, truth checker: the few grid points where the shader's number and the twin's ballsEstimate are more than
1 % apart, or where the shader's number is longer than the true distance by more than my first allowance. From the
kept answers of the page (logs/raw/bc_<key>.json.gz): no browser.

  python out/r28/fix/truth/mk/f_shader.py      -> out/r28/fix/truth/logs/f_shader.txt

The question: is it single precision, or something else? The shader's numbers have 7 digits. The frame carries a
picture point P to m = (0, 0, 1) + k^2 u / |u|^2 (u = P less the frame's centre), so a far point of the picture lands
close to (0, 0, 1), where one unit of the last digit of a single-precision number is 1.2e-7; carried back to the
picture that is 1.2e-7 |u|^2 / k^2. "ulps" below = the difference, in the picture, measured in that unit.
"""
import gzip, json, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); TRUTH = os.path.dirname(HERE); sys.path.insert(0, HERE)
import tkit as T
import bc_page as B

lines = []
def say(s):
    print(s, flush=True); lines.append(s)

def grid_points(s):
    n = s['n']; idx = (np.arange(n) + 0.5) / n - 0.5
    X = (s['cx'] + s['side'] * idx[None, :] + np.zeros((n, 1))).ravel(); Y = (s['cy'] + s['side'] * idx[:, None] + np.zeros((1, n))).ravel()
    return np.column_stack([X, Y, np.full(n * n, s['z'])])

tot = [0, 0, 0]
for key in (B.SETS if __name__ == "__main__" else []):
    fn = os.path.join(TRUTH, 'logs', 'raw', 'bc_%s.json.gz' % key)
    if not os.path.exists(fn):
        continue
    raw = json.load(gzip.open(fn, 'rt', encoding='utf-8')); job, page = raw['job'], raw['page']
    words, rho, t, gname, depth = B.SETS[key]; top = 2 * float(t)
    P = np.concatenate([grid_points(s) for s in job['slices']])
    d = np.concatenate([np.array([np.nan if v is None else v for v in g['d']], float) for g in page['slices']]); e = np.concatenate([np.array(g['e'], float) for g in page['slices']])
    u2 = P[:, 1] ** 2 + P[:, 2] ** 2 + (P[:, 0] - T.K2 / 2) ** 2
    ulp = 1.2e-7 * np.maximum(u2 / T.K2, np.sqrt((P * P).sum(1)) + 1)          # one last digit, in the picture: of m near (0, 0, 1), or of P itself
    both = (d > 0) & (e > 0); rel = np.abs(d - e) / np.maximum(e, 1e-300)
    far = both & (rel > 0.01)
    sign = (d > 0) != (e > 0)
    say('%s (%s): %d grid points; one says inside and the other outside at %d (largest of the two numbers there %.1e); both outside at %d, more than 1 %% apart at %d'
        % (key, words, len(P), int(sign.sum()), float(np.max(np.maximum(np.abs(d[sign]), np.abs(e[sign])))) if sign.any() else 0.0, int(both.sum()), int(far.sum())))
    tot[0] += int(sign.sum()); tot[1] += int(far.sum())
    for k in np.nonzero(far)[0]:
        say('      at (%.5f, %.5f, %.5f): shader %.6g, twin %.6g, apart by %.2g = %.1f %% = %.1f ulps (the shader is the %s one)' % (*P[k], d[k], e[k], abs(d[k] - e[k]), 100 * rel[k], abs(d[k] - e[k]) / ulp[k], 'longer' if d[k] > e[k] else 'shorter'))
    # the largest difference in ulps over all points where both say outside
    k = int(np.argmax(np.where(both, np.abs(d - e) / ulp, -1)))
    say('      the largest difference of all, in ulps: %.1f (at (%.4f, %.4f, %.4f): shader %.6g, twin %.6g)' % (abs(d[k] - e[k]) / ulp[k], *P[k], d[k], e[k]))
    tot[2] = max(tot[2], abs(d[k] - e[k]) / ulp[k])
if __name__ == '__main__':            # (f_shader_L.py borrows grid_points from this file: nothing runs and nothing is written then)
    say('ALL: verdicts apart at %d points; distances more than 1 %% apart at %d; the largest difference between the shader\'s number and the twin\'s anywhere: %.1f ulps' % tuple(tot))
    open(os.path.join(TRUTH, 'logs', 'f_shader.txt'), 'w', encoding='utf-8', newline='\n').write('\n'.join(lines) + '\n')

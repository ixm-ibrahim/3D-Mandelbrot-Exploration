"""Round 20, entry: how the rule stretches space, from its derivative (numbers for the entry's texts).
python out/r20/entry/stretch.py  -> stretch.txt.  Points of length 1; stretches are given as a share of what the
flat plane does there (n at power n), so 1 = as the flat plane, 0 = crushed."""
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import rule

out = []
def say(s=''):
    print(s); out.append(s)

def jac(F, P, h=1e-6):
    J = np.zeros((len(P), 3, 3))
    for j in range(3):
        e = np.zeros(3); e[j] = h
        a = np.stack(F(*(P + e).T), 1); b = np.stack(F(*(P - e).T), 1)
        J[:, :, j] = (a - b) / (2 * h)
    return J

def at(x, a_deg, t_deg=90.0):
    """direction at the angle t from the +x axis, in the half-plane at a_deg round the x-axis"""
    t = np.radians(t_deg); a = np.radians(a_deg)
    return np.array([np.cos(t), np.sin(t) * np.cos(a), np.sin(t) * np.sin(a)])

rng = np.random.default_rng(20)
for n in (2, 3, 4, 5):
    k = rule.kof(n); F = rule.wn(n)
    say('===== power %d, wound k = %d times' % (n, k))
    # 1. the directions sent to -x for power 2 (bud directions): at right angles to the x-axis, in the 2k half-planes
    bud_t = 180.0 / n   # the flat direction at 180/n degrees from +x is sent to -x by z^n
    P = np.array([at(0, j * 180.0 / k, bud_t) for j in range(2 * k)])
    W = np.stack(F(*P.T), 1); s = np.linalg.svd(jac(F, P), compute_uv=False) / n
    say('directions %g degrees from +x in the %d half-planes: sent to %s; stretches (1 = as the flat plane): smallest %.6f, largest %.6f' % (
        bud_t, 2 * k, np.round(W[0], 6).tolist(), s.min(), s.max()))
    # 2. half way between: the crushed directions (at right angles to the x-axis, half way between the half-planes)
    P = np.array([at(0, (j + 0.5) * 180.0 / k) for j in range(2 * k)])
    W = np.stack(F(*P.T), 1); s = np.linalg.svd(jac(F, P, 1e-7), compute_uv=False) / n
    say('directions at right angles to the x-axis half way between them (%s degrees ...): sent to %s; stretches: %s' % (
        ', '.join('%g' % ((j + 0.5) * 180.0 / k) for j in range(3)), np.round(W[0], 6).tolist(), np.round(s[0], 5).tolist()))
    for off in (10.0, 3.0, 1.0, 0.3):
        P = np.array([at(0, 0.5 * 180.0 / k, 90 - off)]); s = np.linalg.svd(jac(F, P, 1e-7), compute_uv=False) / n
        say('   %g degrees away from such a direction (toward +x): stretches %s' % (off, np.round(s[0], 5).tolist()))
    # 3. everywhere: 400,000 random directions
    d = rng.normal(size=(400000, 3)); d /= np.linalg.norm(d, axis=1)[:, None]
    J = jac(F, d); s = np.linalg.svd(J, compute_uv=False) / n; det = np.linalg.det(J)
    a = np.degrees(np.arctan2(d[:, 2], d[:, 1])); t = np.degrees(np.arccos(d[:, 0]))
    i = s[:, 0].argmax()
    say('400,000 random directions: largest stretch %.3f (at %.1f degrees from +x, %.1f degrees round the axis); mirror-reversed (det < 0): %d' % (s[i, 0], t[i], a[i], int((det < 0).sum())))
    ratio = s[:, 0] / np.maximum(s[:, 2], 1e-300)
    say('   largest / smallest stretch: median %.2f; under 1.25 for %.1f %% of directions, under 2 for %.1f %%, over 5 for %.1f %%, over 20 for %.1f %%' % (
        np.median(ratio), 100 * (ratio < 1.25).mean(), 100 * (ratio < 2).mean(), 100 * (ratio > 5).mean(), 100 * (ratio > 20).mean()))
    # 4. within 5 degrees of a copy plane and within 5 degrees of half way, how round
    da = np.abs(((a + 90 / k) % (180 / k)) - 90 / k)      # degrees from the nearest carrying half-plane
    for lo, hi, nm in ((0, 2, 'within 2 degrees of a carrying half-plane'), (0, 5, 'within 5 degrees'), (5, 15, '5 to 15 degrees from one'), (90 / k - 5, 90 / k + 1e-9, 'within 5 degrees of half way')):
        m = (da >= lo) & (da < hi) & (t > 20) & (t < 160)
        say('   %s (20 to 160 degrees from +x): largest / smallest stretch median %.2f, 90 %% under %.2f' % (nm, np.median(ratio[m]), np.quantile(ratio[m], 0.9)))
    say('   slope of the winding g: 1 at the carrying half-planes, %d half way between them, %d on average' % (2 * k - 1, k))
    say()
open(os.path.join(HERE, 'stretch.txt'), 'w', encoding='utf-8', newline='\n').write('\n'.join(out) + '\n')

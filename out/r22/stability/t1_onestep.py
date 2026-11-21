"""t1: one step of each rule under the magnifying glass. python out/r22/stability/t1_onestep.py > t1_onestep.txt
- checks of the tool against closed forms (one-plane keeps shapes; lathe: longest / shortest = r / |x|, inside out for x < 0)
- share of space by kind (keeps shapes / squeezes / squeezes hard / inside out), for the cube -1.5..1.5 and by turn round the x-axis
- near the x-axis: how the turn round the axis is passed on (the 'winding') at x < 0 and x > 0"""
import numpy as np
import stab as T

rng = np.random.default_rng(7); N = 400000
P = rng.uniform(-1.5, 1.5, size=(N, 3)); x, y, z = P.T
print('== tool check')
s, det = T.stretch(T.jac(T.rule('oneplane'), x, y, z))
print('oneplane: longest/shortest stretch max %.6f, inside out %d of %d, middle stretch / 2r max err %.2e' % (T.ratio(s).max(), (det < 0).sum(), N, np.abs(s[:, 1] / (2 * np.linalg.norm(P, axis=1)) - 1).max()))
s, det = T.stretch(T.jac(T.rule('lathe'), x, y, z)); r = np.linalg.norm(P, axis=1)
print('lathe: ratio against r/|x| max rel err %.2e; det sign equals sign(x): %d mismatches' % (np.abs(T.ratio(s) * np.abs(x) / r - 1).max(), (det != np.sign(x)).sum()))

print('\n== share of the cube -1.5..1.5 by kind (ratio = longest / shortest stretch of a tiny ball; keeps < 1.25 <= squeezes < 3 <= hard)')
phi = np.degrees(np.arctan2(z, y)) % 90.0; phi = np.minimum(phi, 90 - phi)          # 0 = flat or upright page, 45 = diagonal page
for nm in T.NAMES:
    s, det = T.stretch(T.jac(T.rule(nm), x, y, z)); cat = T.category(s, det); q = T.ratio(s)
    print('%-9s keeps %5.1f %%  squeezes %5.1f %%  hard %5.1f %%  inside out %5.1f %% | median ratio %.2f, 90th pct %.2f | length: |F| / r^2 err %.1e'
          % (nm, *(100 * (cat == k).mean() for k in range(4)), np.median(q), np.percentile(q, 90),
             np.abs(np.linalg.norm(np.stack(T.rule(nm)(x, y, z)), axis=0) / r ** 2 - 1).max()))
    for half, sel in (('x > 0', x > 0), ('x < 0', x < 0)):
        row = []
        for a0 in range(0, 45, 5):
            m = sel & (phi >= a0) & (phi < a0 + 5)
            row.append('%2d-%2d: %3.0f/%3.0f/%3.0f' % (a0, a0 + 5, 100 * (cat[m] == 0).mean(), 100 * ((cat[m] == 1) | (cat[m] == 2)).mean(), 100 * (cat[m] == 3).mean()))
        print('    %s, by turn from the flat or upright page (keeps/squeezes/inside out %%): ' % half + ' | '.join(row))

print('\n== near the x-axis (0.001 off it): where a point at turn phi is sent (turn of the image), and the stretch along the circle against the stretch outward')
for nm in T.NAMES:
    F = T.rule(nm)
    for x0 in (-0.6, 0.6):
        ph = np.radians(np.arange(0, 91, 7.5)); rho = 1e-3
        X, Y, Z = F(np.full_like(ph, x0), rho * np.cos(ph), rho * np.sin(ph))
        out = np.degrees(np.arctan2(Z, Y)) % 360
        s, det = T.stretch(T.jac(F, np.full_like(ph, x0), rho * np.cos(ph), rho * np.sin(ph), h=1e-7))
        print('%-9s x = %+.1f  phi -> image turn: ' % (nm, x0) + ' '.join('%g->%.1f' % (np.degrees(a), b) for a, b in zip(ph, out)))
        print('%-9s            ratio: ' % '' + ' '.join('%.2f%s' % (q, '-' if d < 0 else '+') for q, d in zip(T.ratio(s), det)))

print('\n== along and away: where exactly is the border between keeping the handedness and turning inside out? (turn from the flat page at which det changes sign)')
for nm in ('along', 'away'):
    F = T.rule(nm)
    for x0 in (-1.2, -0.8, -0.4, -0.1, 0.0, 0.1, 0.4, 0.8, 1.2):
        for rho in (0.05, 0.3, 0.62, 1.0):
            ph = np.radians(np.linspace(0.01, 89.99, 3600))
            s, det = T.stretch(T.jac(F, np.full_like(ph, x0), rho * np.cos(ph), rho * np.sin(ph), h=1e-7))
            ch = np.degrees(ph[1:][det[1:] != det[:-1]])
            print('%-6s x %+.1f rho %.2f: sign at 0+ %+d, changes at %s' % (nm, x0, rho, det[0], ' '.join('%.1f' % a for a in ch) or 'none'))

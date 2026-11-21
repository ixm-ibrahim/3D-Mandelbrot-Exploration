"""Round 29, Track A, builder, decision 5: do the numbers of Frame it for a smaller second sphere still hold for a
second sphere between 1/2 and 1 of the first, the two spheres apart? (numpy alone, no page)

  python -B out/r29/free/mk/tall29.py   -> out/r29/free/logs/tall.txt

For each pair: the recipe on a fine grid of the flat cut and of the cut across the chain (200 rounds).
  reach: the largest |x| that is inside, against the formula k^2 / end + k^2 / 2 (end from the two fixed points);
  tall:  the largest distance from the middle line that is inside, against max(neighbour's radius,
         k^2 / 2 + k^2 / (2 top - 1)), the number Frame it uses.
"""
import os, sys
import numpy as np
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import kit29 as K


def numbers(p, rho):
    t = K.t_of(p); top = 2 * t
    gap = max(top - 1 - rho, 0); D = gap * (top - 1 + rho) / top; sq = np.sqrt(D * (D + 4)); end = 0.5 * (D + sq)
    reach = K.K2 / end + K.K2 / 2 if end > 0 else np.inf
    tall = max(K.K2 * p / 200, K.K2 / 2 + K.K2 / (2 * top - 1))
    HB = 1 / (1 + end)                        # the hull of the bud on the waist (what the page uses for rho > 1/2)
    hull = max(K.K2 * p / 200, K.K2 / 2 + K.K2 * HB / (2 - HB))
    return t, reach, tall, hull


if __name__ == '__main__':
    lines = []
    sets = [(80, 75, 0), (60, 60, 1), (100, 90, 0), (55.56, 99, 0), (120, 51, 2), (30, 75, 0), (40, 60, 0), (90, 99, 0), (70, 85, 1), (110, 80, 0), (20, 95, 2), (125, 70, 0), (50, 55, 1)]
    for (p, rs, grid) in sets:
        rho = rs / 100.0
        t, reach, tall, hull = numbers(p, rho)
        if not np.isfinite(reach) or reach > 60:
            lines.append('size %6.2f second %5.1f grid %d: the chain is longer than 60, not measured' % (p, rs, grid)); continue
        # the far end: a strip along the chain, fine
        hw = reach * 1.15 + 0.2; n = 6000
        xs = np.linspace(-hw, hw, n); best_x = 0.0; best_r = 0.0
        for plane in ('flat', 'up', 'diag'):
            hh = tall * 1.3 + 0.2; ny = int(n * hh / hw / 4) * 2 + 1
            ys = np.linspace(-hh, hh, ny)
            X, Y = np.meshgrid(xs[::4], ys)
            if plane == 'flat':
                P = np.stack([X.ravel(), Y.ravel(), 0 * X.ravel()], 1)
            elif plane == 'up':
                P = np.stack([X.ravel(), 0 * X.ravel(), Y.ravel()], 1)
            else:
                P = np.stack([X.ravel(), Y.ravel() * np.sqrt(0.5), Y.ravel() * np.sqrt(0.5)], 1)
            ins = K.recipe(P, t, rho, grid, 200)
            if ins.any():
                best_x = max(best_x, np.abs(P[ins, 0]).max()); best_r = max(best_r, np.sqrt(P[ins, 1] ** 2 + P[ins, 2] ** 2).max())
        # the far end along the middle line itself, very fine
        P = np.stack([xs, 0 * xs, 0 * xs], 1); ins = K.recipe(P, t, rho, grid, 200)
        line_x = np.abs(xs[ins]).max() if ins.any() else 0.0
        lines.append('size %6.2f second %5.1f grid %d: reach by the formula %.4f, largest |x| inside: on the middle line %.4f, anywhere in three cuts %.4f (%s) | tall: largest distance from the middle line inside %.4f; the number of Version 21 %.4f (%s); with the hull of the bud on the waist %.4f (%s)'
                     % (p, rs, grid, reach, line_x, best_x, 'holds' if best_x <= reach * 1.002 + 2 * hw / n * 4 else 'DOES NOT HOLD', best_r, tall, 'holds' if best_r <= tall * 1.002 + 0.004 else 'DOES NOT HOLD', hull, 'holds' if best_r <= hull * 1.002 + 0.004 else 'DOES NOT HOLD'))
        print(lines[-1], flush=True)
    open(os.path.join(os.path.dirname(HERE), 'logs', 'tall.txt'), 'w', encoding='utf-8', newline='\n').write('\n'.join(lines) + '\n')

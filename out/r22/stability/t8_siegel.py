"""t8: the Siegel disc: is a point above the flat page pulled down to it, and how fast? python out/r22/stability/t8_siegel.py > t8_siegel.txt
30,000 random starts in the box; the height |z| of the orbits still inside after 100, 400, 1600, 6400 steps (median, 10th and 90th pct).
A pull 'by a fixed share each step' would shrink the height by a fixed factor from column to column; a pull that
weakens as the point gets close shows as: four times the steps, half the height."""
import numpy as np
import stab as T

rng = np.random.default_rng(21); V = rng.uniform([-1.8, -1.3, -1.3], [1.8, 1.3, 1.3], size=(30000, 3))
for label, c in (('Siegel', T.SIEGEL), ('San Marco', T.MARCO)):
    for nm in ('oneplane', 'along', 'lathe'):
        F = T.rule(nm); x, y, z = V[:, 0].copy(), V[:, 1].copy(), V[:, 2].copy(); n = 0; row = []
        for stop in (100, 400, 1600, 6400):
            while n < stop:
                X, Y, Z = F(x, y, z); x, y, z = X + c[0], Y + c[1], Z + c[2]; n += 1
                keep = x * x + y * y + z * z < 36.0
                if not keep.all():
                    x, y, z = x[keep], y[keep], z[keep]
            h = np.abs(z) if label == 'Siegel' else np.hypot(y, z)
            row.append('%d steps: %d inside, %s median %.2e (%.1e..%.1e)' % (stop, x.size, 'height' if label == 'Siegel' else 'distance from the x-axis', np.median(h), np.percentile(h, 10), np.percentile(h, 90)))
        print('%-9s %-9s %s' % (label, nm, ' | '.join(row)))

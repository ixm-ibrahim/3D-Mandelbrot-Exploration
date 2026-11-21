"""Judge, check 1b: are the bodies exact balls? For four bodies (centre and radius from the recipe's own arithmetic)
ask the recipe on a shell just inside and just outside the ball, 200000 random directions each."""
import numpy as np
import jlib as J

rng = np.random.default_rng(2702); n = 200000; k2 = 1.05; t = 1.4
d = rng.normal(size=(n, 3)); d /= np.linalg.norm(d, axis=1)[:, None]
wn = k2 / (2 * t - 1); wb = k2 / (2 * t * 2 - 1)          # neighbour; bud at the fraction 1/1 (p^2 + q^2 = 2)
bodies = [('middle ball', (0, 0, 0), k2 / 2), ('right neighbour', (k2 / 2 + wn / 2, 0, 0), wn / 2),
          ('bud on top, in the flat plane', (0, k2 / 2 + wb / 2, 0), wb / 2), ('bulb straight toward the eye', (0, 0, k2 / 2 + wb / 2), wb / 2)]
for nm, c, r in bodies:
    c = np.array(c, float); row = []
    for eps in (1e-3, 1e-5, 1e-7):
        Pi = c + r * (1 - eps) * d; Po = c + r * (1 + eps) * d
        vi = J.balls(Pi[:, 0], Pi[:, 1], Pi[:, 2], rounds=60); vo = J.balls(Po[:, 0], Po[:, 1], Po[:, 2], rounds=60)
        row.append('%.0e: inside shell not inside %d, outside shell in a bud %d, undecided %d' % (eps, int((vi != 1).sum()), int((vo == 1).sum()), int((vo == 0).sum())))
    print('%-30s radius %.5f | shells at 1 -/+ ' % (nm, r) + ' | '.join(row))
print('(points of the outside shell that are inside lie in buds that kiss the ball. Their share stays the same at every shell distance:')
print(' the buds come at every size, so a fixed share of the skin, here about 11 of 100 parts, has a bud standing over it at any height.)')

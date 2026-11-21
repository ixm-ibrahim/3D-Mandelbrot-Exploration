"""Small checks behind the notes.

1. Which seam turns give a rule without a jump? (largest jump of the direction map over close pairs, per rho)
2. The plain doubling z -> 2 z on the pillow turns the belt the WRONG way round (minus doubling).
3. Sideways push beside the flat plane, longitude by longitude: the pillows of this section and round 24's triangle.
4. Where the first extra bodies of the middle body of c = -1 sit (directions sent to +x that are not on the flat plane).
"""
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import pil as P
import best as B
sys.path.insert(0, os.path.join(P.ROOT, 'out', 'r24', 'me'))
import tri as T
TWO_PI = 2 * np.pi
rng = np.random.default_rng(2)

print('1. largest jump of the direction map between 300,000 pairs of directions 1e-6 apart (no jump = about 1e-5 or less)')
d = rng.normal(size=(3, 300000)); d /= np.sqrt((d * d).sum(0)); e = d + 1e-6 * rng.normal(size=d.shape); e /= np.sqrt((e * e).sum(0))
for rho in (0.0, 0.125, 0.2, 0.25, 1 / 3, 0.4, 0.5, 0.6, 0.75, 0.9):
    pl = P.Pillow(rho, 1.0, 'J'); j = np.sqrt(((np.stack(pl.G(*d)) - np.stack(pl.G(*e))) ** 2).sum(0))
    print('   rho %.3f: largest %.1e, share of pairs that jump by more than 0.01: %.4f' % (rho, j.max(), (j > 0.01).mean()))

print('2. plain doubling z -> 2 z on the square pillow, belt y = H/3: where does the belt point at longitude s go?')
pl = P.Pillow(0.0, 1.0, 'J'); s = np.array([0.05, 0.1, 0.2, 0.3]); x, y = s, np.full_like(s, pl.y0)
X2, Y2 = 2 * x, 2 * y                                   # = (2 s, 2H/3), folded back by z ~ -z + tau: (-2 s, H/3)
xf, yf = -X2, pl.H - Y2
print('   s =', s, '-> y =', yf, ', longitude', np.mod(xf, 1), '= -2 s: the mirror image of doubling')

print('3. sideways push beside the flat plane (2 = the same as along the flat plane), by longitude')
th = np.radians(np.arange(0, 360, 15.0)); eps = 1e-5
up = (np.cos(th) * np.cos(eps), np.sin(th) * np.cos(eps), np.full_like(th, np.sin(eps)))
dn = (up[0], up[1], -up[2])
for nm, G in (('square JA', B.rule('square').step), ('tetra JA', B.rule('tetra').step), ('skew JA', B.rule('skew').step), ('skew, plain layout', B.rule('skew', 'J').step), ('triangle (round 24)', None)):
    if G is None:
        gu = T.tri_dir(*up); gd = T.tri_dir(*dn)
    else:
        gu = G(*up, (), 0, 0, 0, 0)[:3]; gd = G(*dn, (), 0, 0, 0, 0)[:3]
    su = np.abs(np.arcsin(np.clip(gu[2], -1, 1))) / eps; sd = np.abs(np.arcsin(np.clip(gd[2], -1, 1))) / eps
    print('   %-20s upward: %s' % (nm, ' '.join('%.2f' % v for v in su)))
    print('   %-20s downward: %s' % ('', ' '.join('%.2f' % v for v in sd)))
print('   longitudes:', ' '.join('%d' % v for v in np.degrees(th)))

print('4. directions sent to +x (the middle body of c = -1 carries a body the size of its neighbours in each)')
for nm in ('square', 'tetra', 'skew', 'skew-mirror'):
    r = B.rule(nm); rho, H, _ = B.KINDS[nm]; pl = P.pillow(rho, H, 'JA')
    for k in (0, 1):
        s = 1.5 * rho + 0.5 * k; v = pl.from_flat(np.array([s - rho]), np.array([H / 6]))
        g = pl.G(*v)
        print('   %-12s longitude %5.1f, latitude %5.1f  (sent to %.3f %.3f %.3f)' % (nm, np.degrees(np.arctan2(v[1][0], v[0][0])) % 360, np.degrees(np.arcsin(v[2][0])), g[0][0], g[1][0], g[2][0]))

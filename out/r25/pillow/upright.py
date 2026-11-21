"""Is the upright plane through the x-axis kept by the direction map, and how much of its circle is covered?"""
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import pil as P
import best as B

t = (np.arange(200000) + 0.5) / 200000 * 2 * np.pi; X, Y, Z = np.cos(t), 0 * t, np.sin(t)
for nm in ('square', 'tetra', 'skew'):
    rho, H, _ = B.KINDS[nm]; pl = P.pillow(rho, H, 'JA'); g = pl.G(X, Y, Z)
    ang = np.degrees(np.arctan2(g[2], g[0])); hist = np.histogram(ang, bins=360, range=(-180, 180))[0]
    print('%-7s upright plane y = 0: largest |y| of the image %.2e; share of the image within 1e-6 of the plane %.3f; degrees of the circle that are hit: %d of 360'
          % (nm, np.abs(g[1]).max(), (np.abs(g[1]) < 1e-6).mean(), int((hist > 0).sum()) if np.abs(g[1]).max() < 1e-6 else -1))

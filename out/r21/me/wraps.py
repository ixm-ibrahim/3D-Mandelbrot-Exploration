"""How many times does a rule wrap the sphere of directions round itself? (python out/r21/me/wraps.py)

A rule F(v) = |v|^2 D(v/|v|) sends directions to directions. The NET number of wraps (wraps the right way round
minus wraps turned inside out) cannot change while a rule is changed gradually, so two rules with different
numbers cannot be joined by a gradual change. Also printed: the share of the sphere that is turned inside out,
and how many directions land on one given direction (counted for a few targets).
"""
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, 'out', 'r16', 'bench'))
import rules as R


def dirs(F, th, ph):
    x, y, z = np.sin(th) * np.cos(ph), np.sin(th) * np.sin(ph), np.cos(th)
    X, Y, Z = F(x, y, z); L = np.sqrt(X * X + Y * Y + Z * Z)
    return np.stack([X / L, Y / L, Z / L], -1)


def wraps(F, n=1400):
    h = np.pi / n
    th = (np.arange(n) + 0.5) * h; ph = (np.arange(2 * n) + 0.5) * h
    TH, PH = np.meshgrid(th, ph, indexing='ij'); e = h * 0.25
    D = dirs(F, TH, PH)
    Dt = (dirs(F, TH + e, PH) - dirs(F, TH - e, PH)) / (2 * e)
    Dp = (dirs(F, TH, PH + e) - dirs(F, TH, PH - e)) / (2 * e)
    dens = (D * np.cross(Dt, Dp)).sum(-1) * h * h          # signed area of the image of one cell
    area = np.sin(TH) * h * h
    ok = np.isfinite(dens) & (np.abs(dens) < 50 * area.max())   # drop the few cells that straddle a seam of atan2
    return dens[ok].sum() / (4 * np.pi), np.abs(dens[ok]).sum() / (4 * np.pi), area[ok & (dens < 0)].sum() / (4 * np.pi)


for name in ['lathe', 'oneplane', 'away', 'along', 'm_w3', 'm_w5']:
    net, total, back = wraps(R.get(name))
    print('%-9s net wraps %+6.2f | wraps counted both ways %6.2f | share of the sphere turned inside out %5.1f%%' % (name, net, total, 100 * back))

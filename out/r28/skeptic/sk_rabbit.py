"""Round 28, skeptic of Track B: the rabbit by the first build. Two things the explorer only SAW.

    PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1 python -W ignore out/r28/skeptic/sk_rabbit.py > out/r28/skeptic/rabbit.log

1. Do three bodies meet in ONE point? Small balls round the meeting point of the flat rabbit (the point that the flat
   rule holds still), at four sizes: the share of each ball's skin that is inside the solid, and into how many
   separate patches the inside part of the skin falls (three bodies that meet in a point: three patches at every size;
   bodies grown together: one patch, and the share goes up as the ball shrinks).
2. The same for c = -1 at its meeting point on the row (two bodies), as the yardstick.
3. How ragged: from my own blocks (side 0.009, every block computed), the thin share by my recipe, beside c = -1.
"""
import os, sys
sys.dont_write_bytecode = True
import numpy as np
from scipy import ndimage as ndi
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import sk_vox
FA = sk_vox.step_fn('A'); FB = sk_vox.step_fn('B')


def say(*a):
    print(*a); sys.stdout.flush()


def skin(F, c, centre, rad, n=240, steps=80):
    """A net of the ball's skin (n x 2n), True where inside the solid; the count of separate inside patches (the net
    closes round the ball; a patch must hold at least 0.2 % of the skin to count)."""
    lat = (np.arange(n) + 0.5) / n * np.pi - np.pi / 2; lon = (np.arange(2 * n) + 0.5) / (2 * n) * 2 * np.pi; LA, LO = np.meshgrid(lat, lon, indexing='ij')
    x = centre[0] + rad * np.cos(LA) * np.cos(LO); y = centre[1] + rad * np.cos(LA) * np.sin(LO); z = centre[2] + rad * np.sin(LA)
    ins = sk_vox.inside_pts(F, x, y, z, c, steps); w = np.cos(LA); share = (ins * w).sum() / w.sum()
    lab, k = ndi.label(ins, structure=np.ones((3, 3), bool)); parent = list(range(k + 1))

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]; a = parent[a]
        return a

    def join(a, b):
        if a and b:
            parent[find(a)] = find(b)
    for i in range(n):                                                     # the net closes round the ball: join across the seam
        for di in (-1, 0, 1):
            if 0 <= i + di < n:
                join(lab[i, 0], lab[i + di, -1])
    for row in (0, n - 1):                                                 # and over each pole
        ls = np.unique(lab[row]); ls = ls[ls > 0]
        for l in ls[1:]:
            join(ls[0], l)
    root = np.array([find(a) for a in range(k + 1)]); area = np.bincount(root[lab].ravel(), weights=w.ravel(), minlength=k + 1) / w.sum(); area[0] = 0
    big = sorted([a for a in area if a > 0.002], reverse=True)
    return share, big


RAB = sk_vox.RABBIT; cc = complex(*RAB); al = (1 - np.sqrt(1 - 4 * cc)) / 2
say('the flat rabbit\'s meeting point of three bodies: (%.6f, %.6f); it is held still by the flat rule to %.1e' % (al.real, al.imag, abs(al * al + cc - al)))
for nm, F in (('first build', FA), ('second build', FB)):
    for rad in (0.08, 0.02, 0.005, 0.00125):
        if nm == 'second build' and rad < 0.005:
            continue
        sh, big = skin(F, RAB, (al.real, al.imag, 0.0), rad, n=240 if nm == 'first build' else 120)
        say('1. rabbit, %s, ball of radius %.5f round the meeting point: %.1f %% of its skin is inside; separate inside patches over 0.2 %% of the skin: %d (%s)' % (nm, rad, 100 * sh, len(big), ', '.join('%.1f %%' % (100 * a) for a in big[:8])))
a1 = 0.5 * (1 - np.sqrt(5))
for nm, F in (('first build', FA), ('second build', FB)):
    for rad in (0.08, 0.02, 0.005, 0.00125):
        if nm == 'second build' and rad < 0.005:
            continue
        sh, big = skin(F, (-1.0, 0.0), (a1, 0.0, 0.0), rad, n=240 if nm == 'first build' else 120)
        say('2. c = -1, %s, ball of radius %.5f round the left meeting point on the row: %.1f %% of its skin is inside; separate inside patches over 0.2 %% of the skin: %d (%s)' % (nm, rad, 100 * sh, len(big), ', '.join('%.1f %%' % (100 * a) for a in big[:8])))

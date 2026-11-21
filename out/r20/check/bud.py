"""Round 20 check: ONE BUD, point by point. Three cuts at right angles through the middle of one bud (or one ear):
in the flat plane, across the x-axis, and the third way (the plane that touches the circle round the x-axis there),
for the four rules. A ball shows as three discs. -> out/r20/check/bud.png"""
import os, sys
import numpy as np
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, 'out', 'r16', 'bench')); sys.path.insert(0, os.path.join(ROOT, 'out', 'me', 'r16'))
import bench as B
import rules as R
import truth as T
RAB = (-0.122561, 0.744862, 0.0); z = complex(RAB[0], RAB[1]); z2 = z * z + z
SPOTS = [('Basilica: the bud on top of the middle body', (-1.0, 0, 0), (0.0, 0.62), 0.16),
         ('Basilica: a bud on that bud (second level)', (-1.0, 0, 0), (0.0791, 0.6631), 0.03),
         ('Rabbit: the ear round c', RAB, (z.real, z.imag), 0.32),
         ('Rabbit: the ear round c^2 + c', RAB, (z2.real, z2.imag), 0.36),
         ('Basilica nudged, c = (-1, 0.05, 0.03): the bud on top of the middle body', (-1.0, 0.05, 0.03), (0.0, 0.64), 0.16)]
RULES = [('m_w3', 'NEW: wind, then square'), ('along', 'Turning plane, along'), ('twoplane', 'Two planes'), ('oneplane', 'One plane')]
n = 250
im = Image.new('RGB', (len(RULES) * (3 * n + 16) + 12, len(SPOTS) * (n + 30) + 70), (12, 13, 18)); dr = ImageDraw.Draw(im); f = T.font(14); fb = T.font(18)
dr.text((8, 6), 'One bud, worked point by point (80 steps, cream = inside). Three cuts at right angles through its middle: in the flat plane | across the x-axis | the third way. A ball shows as three discs.', fill=(230, 230, 230), font=fb)
for j, (rule, name) in enumerate(RULES):
    F = R.get(rule); x0 = 8 + j * (3 * n + 16); dr.text((x0, 34), name, fill=(240, 220, 150), font=fb)
    for i, (lab, c, (cx, cy), half) in enumerate(SPOTS):
        y0 = 62 + i * (n + 30)
        if j == 0:
            dr.text((8, y0), lab + '   (each tile %.2f wide)' % (2 * half), fill=(210, 210, 210), font=f)
        u = np.linspace(-half, half, n); v = np.linspace(half, -half, n); U, V = np.meshgrid(u, v); O = np.zeros_like(U)
        for k, (X, Y, Z) in enumerate(((cx + U, cy + V, O), (cx + O, cy + V, U), (cx + U, cy + O, V))):
            ins, death = B.inside(F, X, Y, Z, c=c, steps=80)
            a = np.zeros((n, n, 3), np.uint8); t = np.clip(death / 14.0, 0, 1)
            for ch, (lo, hi) in enumerate(((22, 60), (26, 90), (44, 160))):
                a[..., ch] = (lo + (hi - lo) * t).astype(np.uint8)
            a[ins] = (238, 228, 200)
            im.paste(Image.fromarray(a), (x0 + k * (n + 2), y0 + 20))
im.save(os.path.join(HERE, 'bud.png')); print('wrote bud.png', im.size)

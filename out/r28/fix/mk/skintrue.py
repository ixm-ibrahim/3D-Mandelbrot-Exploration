"""Round 28, Track A, the fixer: E2. At the places where the light's ray from the pale patches reads its smallest
10 x estimate / length (out/r28/fix/logs/skinray.txt), how far is the nearest ball REALLY (the truth checker's list)?

  python out/r28/fix/mk/skintrue.py     -> out/r28/fix/logs/skintrue.txt      (no browser)
"""
import math, os, re, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); FIX = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(FIX, 'truth', 'mk'))
import tkit as T
import bc_page as B

el, az = math.radians(48), math.radians(250)
LIGHT = np.array([math.cos(el) * math.cos(az), math.cos(el) * math.sin(az), math.sin(el)])
p_, rho, gname = 300.0, 0.25, 'square'; top = T.top_of(p_); grid = T.Grid(gname)
reps, info = T.build(grid, top, rho, 3e-4); ix = T.Index(reps, grid, top)
out = ['size 300, second sphere 25, square grid: %d listed balls, every one of radius >= %.1e (finer near the second sphere)' % (info['n'], T.SLACK * 3e-4)]
C = np.array([0.525 + 0.525 * 3, 0.0, 0.0])
for line in open(os.path.join(FIX, 'logs', 'skinray.txt'), encoding='utf-8'):
    m = re.match(r'pixel \((\d+), (\d+)\): skin point \(([-\d.]+), ([-\d.]+), ([-\d.]+)\).*as the page reads it, ([\d.]+) from "best" alone \| read at length ([\d.]+): best ([\d.]+), free ([\d.]+)', line)
    if not m:
        continue
    px, py = int(m.group(1)), int(m.group(2)); p = np.array([float(m.group(i)) for i in (3, 4, 5)]); ts = float(m.group(7)); best = float(m.group(8)); free = float(m.group(9))
    n = (p - C) / np.linalg.norm(p - C); q = p + 0.002 * n + LIGHT * ts
    td = float(B.true_dist(q[None, :], [1.0], ix, top)[0])
    out.append('pixel (%d, %d): at length %.3f along the light\'s ray the page reads best %.4f and free %.4f; the nearest listed ball is really %.4f away, so 10 x true distance / length = %.2f (the page: %.2f; from "best" alone: %.2f)'
               % (px, py, ts, best, free, td, 10 * td / ts, 10 * min(best, free) / ts, 10 * best / ts))
open(os.path.join(FIX, 'logs', 'skintrue.txt'), 'w', encoding='utf-8', newline='\n').write('\n'.join(out) + '\n')
print('\n'.join(out))

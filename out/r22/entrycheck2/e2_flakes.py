"""Round 22, entrycheck second pass: are the "two flat flakes" of Along once for c = (-1, 0, 0.3) films in the plane
y = 0? That plane is kept by every step when c lies in it (along squares a point of it inside it; the one-plane rule
sends (x, 0, z) to a point with y = 0; c adds nothing along y). Random points of space never lie in it, so
"0 of 400,000 stay" cannot see a film there. Here: a grid IN the plane, and thin slabs beside it.
  python out/r22/entrycheck2/e2_flakes.py -> flakes.txt, flakes.png
"""
import os, sys
import numpy as np
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, 'out', 'r21', 'lib')); sys.path.insert(0, os.path.join(ROOT, 'out', 'r21', 'judge'))
import mem as M
import myrules as J

AO = J.get('alongmem.c_wake1'); ONE = M.bench('oneplane'); PP = J.get('sheet.evc005e70k16')
out = []
def say(t):
    out.append(t); print(t); sys.stdout.flush()

W, H = 720, 560
xs = -1.8 + 3.6 * (np.arange(W) + 0.5) / W; zs = -1.4 + 2.8 * (np.arange(H) + 0.5) / H
gx, gz = np.meshgrid(xs, zs); c = (-1.0, 0.0, 0.3)
tiles = []
for name, r in (('Along once', AO), ('one plane', ONE), ('Pulled plane', PP)):
    n = M.stay(r, gx, np.zeros_like(gx), gz, *c, 300, r2=4096.0)
    say('%-12s c = (-1, 0, 0.3), IN the plane y = 0, %d points: stay 30 / 40 / 80 / 300 steps: %d / %d / %d / %d' % (name, W * H, (n >= 30).sum(), (n >= 40).sum(), (n >= 80).sum(), (n >= 300).sum()))
    tiles.append(np.where(n >= 300, 255, np.where(n >= 40, 150, np.minimum(n * 3, 90))).astype(np.uint8)[::-1])
    for dy in (1e-9, 1e-6, 1e-3, 1e-2):
        m = M.stay(r, gx, np.full_like(gx, dy), gz, *c, 300, r2=4096.0)
        say('             lifted off that plane by %g: %d / %d / %d / %d' % (dy, (m >= 30).sum(), (m >= 40).sum(), (m >= 80).sum(), (m >= 300).sum()))
Image.fromarray(np.hstack(tiles)).save(os.path.join(HERE, 'flakes.png'))
say('flakes.png: the plane y = 0 (x to the right, z up) for Along once | one plane | Pulled plane; white = stays 300 steps, grey = stays 40, dark = leaves sooner')
open(os.path.join(HERE, 'flakes.txt'), 'w', encoding='utf-8', newline='\n').write('\n'.join(out) + '\n')

"""One sheet for the round-19 foldpre report: bench tiles of the basilica beside a point-by-point cut of the rabbit.
    python out/r19/foldpre/sheet.py           -> out/r19/foldpre/sheet-foldpre.png"""
import os, sys
import numpy as np
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, 'out', 'r16', 'bench')); sys.path.insert(0, os.path.join(ROOT, 'out', 'me', 'r16'))
import truth as T
import rules as R
sys.path.insert(0, HERE)
import stack as K

ROWS = [('oneplane', 'One plane (the yardstick): clean, buds only in the flat plane'),
        ('g_p12', 'Fold above 12 degrees: copies nearly round (stretch 2.18) but everything is fused into a ribbed barrel; film on the necks'),
        ('g_p245', 'Fold above 24.5 degrees: copy of the whole row at 45 degrees (stretch 2.83): four extra long arms; film on the necks'),
        ('g_pl', 'Four pleats leaning over the bud directions: no extra arms, no film; bud copies are spindles (stretch 3.2 and 5.3); rabbit shredded'),
        ('g_pt8', 'The same pleats lower and through the pole: bud copies stretch 2.7 and 3.3; rabbit shredded')]
COLS = [('front', 'Basilica, front'), ('alongx', 'Basilica, along the x-axis'), ('cut_y0', 'Basilica, upright cut (y = 0)'), ('cut_x0', 'Basilica, cut across the middle (x = 0)'),
        ('close2', 'Basilica, one bud close up'), (None, 'Rabbit, cut across the middle (x = 0), point by point')]
S = 330
if __name__ == '__main__':
    pad = 8; W = pad + len(COLS) * (S + pad); H = 44 + len(ROWS) * (S + 54)
    im = Image.new('RGB', (W, H), (12, 14, 20)); d = ImageDraw.Draw(im)
    d.text((pad, 8), 'Fold the direction first, then square (round 19, foldpre). Basilica tiles from the bench (voxels); the rabbit worked point by point, 60 steps.',
           fill=(235, 235, 240), font=T.font(19))
    for i, (nm, lab) in enumerate(ROWS):
        y0 = 44 + i * (S + 54)
        d.text((pad, y0), f'{nm}: {lab}', fill=(225, 228, 235), font=T.font(17))
        for j, (tile, cap) in enumerate(COLS):
            x0 = pad + j * (S + pad)
            if tile:
                p = os.path.join(ROOT, 'out', 'r16', 'bench', 'tiles', nm, tile + '.png')
                t = Image.open(p).convert('RGB').resize((S, S), Image.LANCZOS) if os.path.exists(p) else Image.new('RGB', (S, S), (30, 30, 36))
            else:
                c, steps, half = K.SETS['rabbit']
                n = K.plane(R.get(nm), c, steps, (0, 0, 0), (0, 1, 0), (0, 0, 1), half * 0.62, n=S)
                t = Image.fromarray(T.shade(n, steps))
            im.paste(t, (x0, y0 + 24)); d.text((x0 + 4, y0 + 26), cap, fill=(255, 255, 255), font=T.font(13))
    out = os.path.join(HERE, 'sheet-foldpre.png'); im.save(out); print('wrote', out)

"""Round 27, measure: a quick look at the ring of three with three different grids (working picture, not for the user).

    python out/r27/measure/try_rings.py  -> try-rings.png
"""
import os, sys, time
import numpy as np
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import ballkit as K
import family as F

w, h, pad = 380, 380, 6; t0 = time.time()
cases = [('check grid, ring of 3', K.Grid('check'), 3), ('square grid every 2nd, ring of 3', K.Grid('gauss', 2.0), 3), ('line every 2nd, ring of 3', K.Grid('line', 2.0), 3),
         ('square grid every 2nd, ring of 4', K.Grid('gauss', 2.0), 4), ('square grid every 2nd, ring of 5', K.Grid('gauss', 2.0), 5)]
im = Image.new('RGB', (pad + len(cases) * (w + pad), 30 + 3 * (h + 6)), F.BG); d = ImageDraw.Draw(im)
for j, (name, g, m) in enumerate(cases):
    t = float(np.cos(np.pi / m)); c0, k2, centre = F.ring_frame(t); B, info = F.balls(g, 2 * t, c0=c0, k2=k2, r_min=0.006, cap=600000)
    x = pad + j * (w + pad); hw = 2.4
    F.text(d, (x, 6), '%s (%d balls)' % (name, len(B)), 14, (235, 220, 170))
    im.paste(F.cutimg(B, w, h, (centre[0] - hw, centre[0] + hw, centre[1] - hw, centre[1] + hw)), (x, 30))
    im.paste(F.solidimg(B, w, h, hw, centre, cam=(0.25, 0.3, 1.0)), (x, 30 + h + 6))
    im.paste(F.solidimg(B, w, h, hw, centre, cam=(1.0, 0.45, 0.5)), (x, 30 + 2 * (h + 6)))
    print(name, len(B), info, '%.0f s' % (time.time() - t0)); sys.stdout.flush()
im.save(os.path.join(HERE, 'try-rings.png')); print('wrote try-rings.png')

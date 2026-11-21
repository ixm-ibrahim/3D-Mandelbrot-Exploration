"""Skeptic, job 1: what a FAKE 'not spun' Mandelbrot solid looks like.  python out/r21/skeptic/fake.py
These recipes have nothing fixed off the x-axis; in exact arithmetic their Mandelbrot solid is the lathe's. The
library's 16 digits push the orbit off the sheet of c, the recipe magnifies the push, and the solid is eaten away,
except on the flat page and the upright sheet, where the numbers happen to be exact. The picture is rounding."""
import sys, time
import numpy as np
from PIL import Image, ImageDraw
sys.path.insert(0, 'out/r21/lib'); sys.path.insert(0, 'out/r21/skeptic')
import mem as M
import myrules as R

names = ['lathe', 'S1 lag25, no start page', 'S2 delay, no start page', 'S4 ahead 1', 'S6 span2', 'S8 far sheet']
ANG = (0.0, 11.25, 22.5, 45.0, 90.0); steps = 150; w, h = 330, 300; pad = 8; t0 = time.time()
heads = ['along the sheet turned %g' % a for a in ANG] + ['across at x = -0.12']
W = pad + 5 * (w + pad) + h + pad; H = 44 + len(names) * (h + 44)
im = Image.new('RGB', (W, H), (12, 14, 20)); d = ImageDraw.Draw(im)
d.text((pad, 8), 'Mandelbrot solids of recipes with NOTHING fixed off the x-axis, as the library computes them (%d steps)' % steps, fill=(240, 240, 245), font=M.font(20))
ref = None
for i, nm in enumerate(names):
    r = M.bench(nm) if nm == 'lathe' else R.BY[nm]
    arrs = [M.cut_axis(r, a, w, h, steps) for a in ANG] + [M.cut_across(r, -0.12, h, steps)]
    if ref is None:
        ref = [a >= steps for a in arrs]
    y = 44 + i * (h + 44); d.text((pad, y), '%s: %s' % (r.name, r.label), fill=(235, 220, 170), font=M.font(16)); x = pad
    for hd, a, rf in zip(heads, arrs, ref):
        gone = int((rf & ~(a >= steps)).sum())
        d.text((x, y + 22), '%s: %d of %d lathe pixels gone' % (hd, gone, int(rf.sum())), fill=(150, 160, 175), font=M.font(12)); im.paste(Image.fromarray(M.shade(a, steps)), (x, y + 40)); x += a.shape[1] + pad
    print(nm, '%.0f s' % (time.time() - t0)); sys.stdout.flush()
im.save('out/r21/skeptic/fake-notspun.png'); print('wrote out/r21/skeptic/fake-notspun.png')

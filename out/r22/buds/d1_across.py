"""Diagnostic (not for the user): cuts across the x-axis through the four flat-bud rings, five rules, basilica.
   python out/r22/buds/d1_across.py [c]  -> d1-across[-sm].png"""
import os, sys, time
import numpy as np
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import budlib as B
M = B.M

sm = len(sys.argv) > 1 and sys.argv[1] == 'sm'
c = B.SANMARCO if sm else B.BASILICA
fc = B.flat_centres(c[0]); W = 440; STEPS = 60; pad = 8
cols = [('g1', 1.0), ('g2', 0.55), ('g3', 0.75), ('g4', 0.4), ('small', 0.3)]
im = Image.new('RGB', (pad + len(cols) * (W + pad), 30 + len(B.RULES) * (W + 26)), (12, 14, 20)); d = ImageDraw.Draw(im); f = M.font(14)
t0 = time.time()
for i, name in enumerate(B.RULES):
    y = 30 + i * (W + 26)
    for j, (g, L) in enumerate(cols):
        x0 = fc[g].real if g != 'small' else fc['small']; rad = abs(fc[g].imag) if g != 'small' else 0.0
        n = M.cut_across(B.RULES[name], x0, W, STEPS, c=c, L=L); x = pad + j * (W + pad)
        im.paste(Image.fromarray(M.shade(n, STEPS)), (x, y + 18))
        d.text((x, y), '%s | cut across x = %.3f, half-width %.2f, ring %s radius %.3f' % (name, x0, L, g, rad), fill=(200, 200, 170), font=f)
        if rad > 0:
            rr = rad / L * (W - 1) / 2; cx_, cy_ = x + (W - 1) / 2, y + 18 + (W - 1) / 2
            d.ellipse([cx_ - rr, cy_ - rr, cx_ + rr, cy_ + rr], outline=(90, 200, 120), width=1)
    print(name, '%.0f s' % (time.time() - t0)); sys.stdout.flush()
out = os.path.join(HERE, 'd1-across%s.png' % ('-sm' if sm else '')); im.save(out); print(out, im.size)

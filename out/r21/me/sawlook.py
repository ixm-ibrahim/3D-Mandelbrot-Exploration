"""A quick look, in rough blocks, at the torn form of 'wind, then square' (m_w3saw: each 60-degree wedge turned whole
onto the flat wedge, no ramp) beside 'along' and the sinus form that is in the lab (m_w3).
    python out/r21/me/sawlook.py   -> out/r21/me/saw-look.png
"""
import os, sys, time
import numpy as np
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(ROOT, 'out', 'r16', 'bench')); sys.path.insert(0, os.path.join(ROOT, 'out', 'me', 'r16'))
import rules as R
import truth as T
import cplane as C

SETS = [('basilica, c = -1', (-1.0, 0.0, 0.0)), ('rabbit', (-0.122561, 0.744862, 0.0)), ('Siegel disc', (-0.390541, -0.586788, 0.0)),
        ('San Marco, c = -0.75', (-0.75, 0.0, 0.0))]
RULES = [('along', 'Turning plane, along'), ('m_w3', 'Wind, then square (in the lab: smooth ramp)'), ('m_w3saw', 'Wind, then square, cut form (a tear half way between the planes)')]
w, h, nd, steps = 400, 300, 260, 30
pad = 10
W = pad + len(SETS) * (w + pad); H = 60 + len(RULES) * (h + 40)
im = Image.new('RGB', (W, H), (12, 14, 20)); d = ImageDraw.Draw(im)
d.text((pad, 10), 'Rough blocks, %d steps' % steps, fill=(240, 240, 245), font=T.font(24))
t0 = time.time()
for i, (rn, label) in enumerate(RULES):
    G = C.fixed(R.get(rn)); y = 60 + i * (h + 40)
    d.text((pad, y), label, fill=(235, 220, 170), font=T.font(19))
    for j, (sn, c) in enumerate(SETS):
        dep, px = C.solid(G, 'j', c, (0.0, 0.0, 0.0), 1.75, w, h, nd, steps)
        x = pad + j * (w + pad)
        im.paste(Image.fromarray(C.shade_solid(dep, px)), (x, y + 28))
        d.text((x + 6, y + 32), sn, fill=(150, 160, 175), font=T.font(14))
    print(rn, '%.0f s' % (time.time() - t0)); sys.stdout.flush()
out = os.path.join(HERE, 'saw-look.png'); im.save(out); print(out, im.size)

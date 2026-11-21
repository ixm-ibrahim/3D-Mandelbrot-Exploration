"""Round 20 check: what a person sees at ONE BUD. Voxel boxes (257 a side, 60 steps) round one bud or one ear,
for m_w3 and for the rules beside it, two views each. -> out/r20/check/closeup.png
python out/r20/check/closeup.py"""
import os, sys, json, time
import numpy as np
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, 'out', 'r16', 'bench')); sys.path.insert(0, os.path.join(ROOT, 'out', 'me', 'r16'))
import bench as B
import rules as R
import truth as T
turns = R.turns
RAB = (-0.122561, 0.744862, 0.0); z = complex(RAB[0], RAB[1]); z2 = z * z + z
c60 = np.cos(np.radians(60)); s60 = np.sin(np.radians(60)); c30 = np.cos(np.radians(30)); s30 = np.sin(np.radians(30))
# (label, c, centre of the box, half box)
SPOTS = [
    ('Basilica: the bud on top of the middle body', (-1.0, 0, 0), (0.0, 0.62, 0.0), 0.2),
    ('Basilica: the same place one third of the way round (60 degrees up)', (-1.0, 0, 0), (0.0, 0.62 * c60, 0.62 * s60), 0.2),
    ('Basilica: half way between (30 degrees up), skin of the middle body', (-1.0, 0, 0), (0.0, 0.52 * c30, 0.52 * s30), 0.2),
    ('San Marco: half way between (30 degrees up), where two bodies meet', (-0.75, 0, 0), (-0.5, 0.3 * c30, 0.3 * s30), 0.3),
    ('Rabbit: the ear round c', RAB, (z.real, z.imag, 0.0), 0.3),
    ('Rabbit: the ear round c^2 + c', RAB, (z2.real, z2.imag, 0.0), 0.35),
    ('Rabbit: middle body, half way between (30 degrees up)', RAB, (0.0, 0.3 * c30, 0.3 * s30), 0.3),
    ('Basilica nudged (-1, 0.05, 0.03): the bud on top of the middle body', (-1.0, 0.05, 0.03), (0.0, 0.62, 0.0), 0.2),
    ('Basilica nudged (-1, 0.05, 0.03): skin of the middle body, 30 degrees up', (-1.0, 0.05, 0.03), (0.0, 0.52 * c30, 0.52 * s30), 0.2),
    ('Cauliflower: skin half way between (30 degrees up)', (0.25, 0, 0), (0.0, 0.75 * c30, 0.75 * s30), 0.3),
]
RULES = sys.argv[1:] or ['m_w3', 'along', 'twoplane', 'oneplane']
S = 257
im = Image.new('RGB', (len(RULES) * (2 * S + 12) + 8, len(SPOTS) * (S + 26) + 60), (12, 13, 18)); dr = ImageDraw.Draw(im); f = T.font(14); fb = T.font(18)
dr.text((8, 6), 'One bud close up: voxel boxes (257 a side, 60 steps). Each pair: seen from the side, and seen along the x-axis.', fill=(230, 230, 230), font=fb)
for j, rule in enumerate(RULES):
    dr.text((8 + j * (2 * S + 12), 32), R.RULES[rule][1][:60] + '  [' + rule + ']', fill=(240, 220, 150), font=f)
    F = R.get(rule)
    for i, (lab, c, cen, half) in enumerate(SPOTS):
        t0 = time.time(); vol = B.volume(F, S, L=half, centre=cen, c=c, steps=60)
        y0 = 56 + i * (S + 26)
        im.paste(Image.fromarray(turns.render(vol, az=-60, el=22)), (8 + j * (2 * S + 12), y0 + 18))
        im.paste(Image.fromarray(turns.render(vol, az=0, el=0)), (8 + j * (2 * S + 12) + S, y0 + 18))
        if j == 0:
            dr.text((8, y0), lab + '  (box %.2f wide)' % (2 * half), fill=(210, 210, 210), font=f)
        print(rule, lab, 'filled %.3f' % vol.mean(), '%.0f s' % (time.time() - t0), flush=True)
    im.save(os.path.join(HERE, 'closeup.png'))
print('wrote closeup.png')

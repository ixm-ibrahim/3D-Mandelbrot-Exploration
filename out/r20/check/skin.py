"""Round 20 check: the skin of the basilica between the planes, the same place for four rules, at panel2's three widths.
Tiles are panel2's own (read from out/r19/panel2/wide/*.npz). -> out/r20/check/skin-<set>.png"""
import os, sys, json
import numpy as np
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
P2 = os.path.join(ROOT, 'out', 'r19', 'panel2'); sys.path.insert(0, P2); sys.path.insert(0, os.path.join(ROOT, 'out', 'me', 'r16'))
import hairnum as H
import truth as T
tag = sys.argv[1] if len(sys.argv) > 1 else 'basilica'
RULES = [('m_w3', 'Wind, then square (new)'), ('along', 'Turning plane, along'), ('twoplane', 'Two planes (the liked look)'), ('oneplane', 'One plane')]
ANG = [float(a) for a in sys.argv[2].split(',')] if len(sys.argv) > 2 else [22.5, 45.0]
OFF = -0.5
W, Hh = 300, 210
im = Image.new('RGB', (len(ANG) * 3 * (W + 6) + 250, len(RULES) * (Hh + 40) + 70), (12, 13, 18)); dr = ImageDraw.Draw(im); f = T.font(13); fb = T.font(17)
dr.text((8, 6), '%s: the skin of the biggest body, cut through the x-axis, worked point by point (80 steps). Cream = inside. Red = thin things counted, purple = film of dust.' % tag, fill=(230, 230, 230), font=fb)
for j, a in enumerate(ANG):
    dr.text((250 + j * 3 * (W + 6), 30), '%.1f degrees from the flat plane: tile 0.2, 0.04 and 0.008 of the body wide' % a, fill=(210, 210, 210), font=f)
for i, (rule, name) in enumerate(RULES):
    y0 = 52 + i * (Hh + 40); dr.text((8, y0 + 80), name, fill=(240, 220, 150), font=fb)
    p = os.path.join(P2, 'wide', '%s-%s.npz' % (rule, tag))
    if not os.path.exists(p):
        dr.text((8, y0 + 104), 'no tiles (outside)', fill=(200, 200, 200), font=f); continue
    z = np.load(p); meta = json.loads(str(z['meta'])); masks = z['masks']
    for j, a in enumerate(ANG):
        for q in (0, 1, 2):
            mm = [m for m in meta if 'k' in m and m['angle'] == a and m['off'] == OFF and m['q'] == q]
            if not mm:
                continue
            mask = np.unpackbits(masks[mm[0]['k']], axis=1)[:, :420].astype(bool); s, marks = H.score(mask, want_marks=True)
            x0 = 250 + (j * 3 + q) * (W + 6); im.paste(Image.fromarray(H.paint(mask, marks)).resize((W, Hh), Image.NEAREST), (x0, y0))
            bad = s['fins'] is not None and (s['fins'] > H.T_FINS or s['film_pct'] > H.T_FILM)
            dr.text((x0, y0 + Hh + 2), 'thin %.2f  film %.1f %%  %s   (%.4f wide)' % (s['fins'] or 0, s['film_pct'], 'NOT CLEAN' if bad else 'clean', mm[0]['width']), fill=(235, 130, 120) if bad else (150, 220, 150), font=f)
im.save(os.path.join(HERE, 'skin-%s.png' % tag)); print('wrote', tag)

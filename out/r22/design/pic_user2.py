"""Second picture for the user (plain words only): a second page CAN show the flat rabbit, and what it costs.
python out/r22/design/pic_user2.py -> out/r22/design/q4-second-page.png"""
import sys, os, time
import numpy as np
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dlib as L
M, D = L.M, L.D
r = D.get('preturn'); c = M.RABBIT; t0 = time.time()
al = (1 - np.sqrt(1 - 4 * complex(c[0], c[1]))) / 2
print('rabbit: meeting point %.4f %+.4fi, the flat rule turns things round it by %.2f degrees a step and stretches them %.4f times'
      % (al.real, al.imag, np.degrees(np.angle(2 * al)), abs(2 * al)))
CW, CH, SW, SH = 400, 290, 400, 290
flat = M.shade(M.cut_axis(r, 0.0, CW, CH, 80, c=c), 80)
up = M.shade(M.cut_axis(r, 90.0, CW, CH, 80, c=c), 80)
dep, px = M.solid(r, c, SW, SH, 280, 60, cam=(0.45, 0.5, 1.0)); s1 = M.shade_solid(dep, px); print('solid 1 %.0f s' % (time.time() - t0)); sys.stdout.flush()
dep, px = M.solid(r, c, SW, SH, 280, 60, cam=(1.0, 0.45, 0.25)); s2 = M.shade_solid(dep, px); print('solid 2 %.0f s' % (time.time() - t0))
pad = 14; f_t, f_h, f_c = M.font(24), M.font(15), M.font(16)
W = pad + 4 * (CW + pad); H = 60 + 22 + CH + 86
im = Image.new('RGB', (W, H), (12, 14, 20)); d = ImageDraw.Draw(im)
d.text((pad, 10), 'New try 3: swing the upright page down onto the flat page, then square in the flat page (the rabbit)', fill=(240, 240, 245), font=f_t)
heads = ['cut along the flat page', 'cut along the upright page', 'the whole shape', 'the whole shape, seen from the side']
x = pad
for hd, t in zip(heads, (flat, up, s1, s2)):
    d.text((x, 58), hd, fill=(170, 180, 195), font=f_h); im.paste(Image.fromarray(t), (x, 80)); x += CW + pad
cap = ('A second page CAN show the flat picture of the rabbit: the upright page shows it, place for place (the lower half of the flat\n'
       'picture, once above and once below). What it costs: between the two pages the shape is shells and ribs, not buds, and the\n'
       'second rabbit shares only the x-axis with the first, so it brings bodies of its own instead of adding buds to the first one.')
d.multiline_text((pad, 80 + CH + 8), cap, fill=(225, 228, 235), font=f_c, spacing=4)
im.save(os.path.join(L.HERE, 'q4-second-page.png')); print('saved')

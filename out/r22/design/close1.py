"""Closer look at one rule on one set (internal names): cuts across the hinge at 30 and 80 steps, tilted pages, two solids.
python out/r22/design/close1.py rabbit alonghinge"""
import sys, os, time
import numpy as np
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dlib as L
import sheet2 as S2
M, D = L.M, L.D
R = L.refs()
which, name = sys.argv[1], sys.argv[2]
c = S2.SETS[which]; r = R[name] if name in R else D.get(name)
a = float(D.meeting_turn(c[0], c[1])) if name == 'alonghinge' or len(sys.argv) > 3 else 0.0
al = (1 - np.sqrt(1 - 4 * complex(c[0], c[1]))) / 2; um = al.real * np.cos(a) + al.imag * np.sin(a)
t0 = time.time(); n = 380; pad = 8
tiles = []; heads = []
for u in (0.0, um / 2, um):
    c30 = S2.hinge_across(r, c, a, u, n, 30, Lh=0.9) >= 30; c80 = S2.hinge_across(r, c, a, u, n, 80, Lh=0.9)
    img = M.shade(c80, 80); lost = c30 & ~(c80 >= 80); img[lost] = (230, 90, 70)
    tiles.append(img); heads.append('across the hinge at %.2f (red: inside at 30 steps, gone at 80: %d of %d)' % (u, lost.sum(), c30.sum()))
for t in (33.75, 67.5):
    c80 = S2.hinge_cut(r, c, a, t, 506, n, 80); tiles.append(M.shade(c80, 80)); heads.append('page through the hinge, tilted %g, 80 steps' % t)
print('cuts %.0f s' % (time.time() - t0)); sys.stdout.flush()
sol = []
for cm in ((0.45, 0.5, 1.0), (-0.3, 1.0, 0.35), (1.0, 0.45, 0.25)):
    dep, px = M.solid(r, c, 520, 400, 320, 60, cam=cm); sol.append(M.shade_solid(dep, px)); print('solid %.0f s' % (time.time() - t0)); sys.stdout.flush()
W = pad + 3 * (n + pad) + 2 * (506 + pad); H = 40 + n + 30 + 400 + 30
im = Image.new('RGB', (max(W, pad + 3 * (520 + pad)), H), (12, 14, 20)); d = ImageDraw.Draw(im)
d.text((pad, 8), '%s under %s (hinge turned %.1f degrees)' % (which, name, np.degrees(a)), fill=(240, 240, 245), font=M.font(18))
x = pad
for hd, t in zip(heads, tiles):
    d.text((x, 34), hd[:int(t.shape[1] / 6.2)], fill=(150, 160, 175), font=M.font(11)); im.paste(Image.fromarray(t), (x, 50)); x += t.shape[1] + pad
x = pad
for t, cm in zip(sol, ('eye (0.45, 0.5, 1)', 'eye (-0.3, 1, 0.35)', 'eye (1, 0.45, 0.25)')):
    d.text((x, 50 + n + 8), 'solid, 60 steps, ' + cm, fill=(150, 160, 175), font=M.font(11)); im.paste(Image.fromarray(t), (x, 50 + n + 24)); x += 520 + pad
im.save(os.path.join(L.HERE, 'close-%s-%s.png' % (which, name)))

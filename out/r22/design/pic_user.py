"""The picture for the user (plain words only): what was tried from the findings, beside one plane and along.
python out/r22/design/pic_user.py            -> out/r22/design/q4-tries.png   (tiles are cached in tiles-user.npz)"""
import sys, os, time
import numpy as np
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dlib as L
import sheet2 as S2
M, D = L.M, L.D
R = L.refs()
ROWS = [
    ('oneplane', 'Sphere inversions, one plane: every point is squared in the flat page',
     'Clean bodies for every c, but buds only round the flat page.'),
    ('along', 'Turning plane, along: the pages are the pages of a book whose spine is the x-axis',
     'c = -1: round buds in eight directions. Rabbit: one lump. In the cut its bodies are joined along a whole wall instead of touching at one point.'),
    ('alonghinge', 'New try 1: the same rule, with the spine of the book turned so that it runs through the point where the big bodies meet',
     'c = -1: exactly the shape above (there the bodies meet on the x-axis). Rabbit: no lump, the bodies touch at one point again. But the skin is ridges and thin loose arcs, not round buds.'),
    ('capfold45', 'New try 2: fold the top and the bottom of space down onto the flat page, then square in the flat page',
     'A second copy of the flat picture stands up on a cone through the middle. Spikes and loose bits on both shapes, no buds.'),
]
HEADS = ['the c = -1 shape', 'the rabbit', 'the rabbit cut straight across where its three big bodies meet\n(the meeting point is in the middle of the picture)']
SW, SH, CW = 430, 320, 320
cache = os.path.join(L.HERE, 'tiles-user.npz'); tiles = dict(np.load(cache)) if os.path.exists(cache) else {}
a = float(D.meeting_turn(*M.RABBIT[:2])); al = (1 - np.sqrt(1 - 4 * complex(*M.RABBIT[:2]))) / 2; um = al.real * np.cos(a) + al.imag * np.sin(a)
t0 = time.time()
for nm, _, _ in ROWS:
    r = R[nm] if nm in R else D.get(nm)
    for key, c in (('bas', L.BAS), ('rab', L.RAB)):
        k = nm + '_' + key
        if k not in tiles:
            dep, px = M.solid(r, c, SW, SH, 280, 60, cam=(0.45, 0.5, 1.0)); tiles[k] = M.shade_solid(dep, px); np.savez(cache, **tiles)
            print(k, '%.0f s' % (time.time() - t0)); sys.stdout.flush()
    k = nm + '_cut'
    if k not in tiles:
        tiles[k] = M.shade(S2.hinge_across(r, M.RABBIT, a, um, CW, 80, Lh=0.75), 80); np.savez(cache, **tiles)
pad = 14; f_t, f_h, f_r, f_c = M.font(26), M.font(15), M.font(18), M.font(16)
W = pad + SW + pad + SW + pad + CW + pad; rowh = 30 + SH + 78; TOP = 118
im = Image.new('RGB', (W, TOP + len(ROWS) * rowh), (12, 14, 20)); d = ImageDraw.Draw(im)
d.text((pad, 10), 'Two new tries that follow from what the orbits do, beside the two rules you know', fill=(240, 240, 245), font=f_t)


def wrap(text, font, width):
    words = text.split(); lines = []; cur = ''
    for wd in words:
        t = (cur + ' ' + wd).strip()
        if d.textlength(t, font=font) <= width:
            cur = t
        else:
            lines.append(cur); cur = wd
    lines.append(cur); return '\n'.join(lines)


x = pad
for hd, w in zip(HEADS, (SW, SW, CW)):
    d.multiline_text((x, 50), wrap(hd.replace('\n', ' '), f_h, w - 4), fill=(170, 180, 195), font=f_h, spacing=2); x += w + pad
for i, (nm, label, cap) in enumerate(ROWS):
    y = TOP + i * rowh
    d.text((pad, y), label, fill=(235, 220, 170), font=f_r)
    x = pad
    for key in ('bas', 'rab', 'cut'):
        t = tiles[nm + '_' + key]; im.paste(Image.fromarray(t), (x, y + 28)); x += t.shape[1] + pad
    d.multiline_text((pad, y + 28 + SH + 4), wrap(cap, f_c, W - 2 * pad), fill=(225, 228, 235), font=f_c, spacing=3)
im.save(os.path.join(L.HERE, 'q4-tries.png')); print('saved')

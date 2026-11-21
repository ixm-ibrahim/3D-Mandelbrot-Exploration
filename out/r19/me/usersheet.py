"""One sheet for the user: one plane, along and the new rule side by side, from the panel's own rough 3D tiles.
python out/r19/me/usersheet.py   -> out/r19/me/wind-vs-along.png"""
import os, sys
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, 'out', 'me', 'r16'))
import truth as T

SETS = [('basilica', 'Basilica, c = -1 (on the x-axis)'), ('sanmarco', 'San Marco, c = -0.75 (on the x-axis)'),
        ('rabbit', 'Rabbit (c off the x-axis, in the flat plane)'), ('dendrite', 'Dendrite, c = i (a tree, no inside)'),
        ('siegel', 'Siegel disc (c off the x-axis)')]
RULES = [('oneplane', 'One plane'), ('along', 'Turning plane, along'), ('m_w3', 'NEW: wind, then square')]
VIEWS = [('front', 'from the front'), ('above', 'from above')]
S = 2          # enlarge the 257-pixel tiles
pad = 10


def find(rule, st, view):
    for base in (os.path.join(ROOT, 'out', 'r19', 'panel2', 'tiles'), os.path.join(ROOT, 'out', 'r18', 'panel', 'tiles')):
        p = os.path.join(base, rule, st, view + '.png')
        if os.path.exists(p):
            return p
    return None


rows = [(st, nm) for st, nm in SETS if all(find(r, st, 'front') for r, _ in RULES)]
tw = 257 * S
W = pad + len(RULES) * len(VIEWS) * (tw + pad)
H = 96 + len(rows) * (tw + 40)
im = Image.new('RGB', (W, H), (12, 14, 20)); d = ImageDraw.Draw(im)
d.text((pad, 8), 'Three rules on the same Julia sets (rough block pictures, 40 steps)', fill=(240, 240, 245), font=T.font(26))
for i, (r, nm) in enumerate(RULES):
    x = pad + i * len(VIEWS) * (tw + pad)
    d.text((x, 46), nm, fill=(235, 220, 170) if r == 'm_w3' else (200, 205, 215), font=T.font(22))
    for j, (_, vn) in enumerate(VIEWS):
        d.text((x + j * (tw + pad), 74), vn, fill=(150, 160, 175), font=T.font(15))
for k, (st, nm) in enumerate(rows):
    y = 96 + k * (tw + 40)
    d.text((pad, y + 6), nm, fill=(228, 230, 236), font=T.font(19))
    for i, (r, _) in enumerate(RULES):
        for j, (v, _) in enumerate(VIEWS):
            p = find(r, st, v)
            x = pad + (i * len(VIEWS) + j) * (tw + pad)
            if p:
                a = Image.open(p).convert('RGB').resize((tw, tw), Image.LANCZOS)
                im.paste(a, (x, y + 34))
out = os.path.join(HERE, 'wind-vs-along.png'); im.save(out); print(out, im.size, [r[0] for r in rows])

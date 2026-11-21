"""Bench tiles of several rules side by side (the bench made the tiles; this only pastes them).
python tilesheet.py <out.png> <rule> ...   rows = rules; columns = along the x-axis, close-up 1, 2, 3, cut across one bud, cut across a bud's bud"""
import os, sys
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, 'out', 'me', 'r16')); sys.path.insert(0, os.path.join(ROOT, 'out', 'r16', 'bench'))
import truth as T, rules as R
COLS = [('front', 'front'), ('alongx', 'along the x-axis'), ('close1', 'close-up: middle body'), ('close2', 'close-up: one bud'), ('close3', 'close-up: on that bud'), ('bud_across', 'cut across that bud'), ('sub_across', "cut across a bud's bud")]
S = int(os.environ.get('TILE', '330'))
out = sys.argv[1]; names = sys.argv[2:]
W = 8 + len(COLS) * (S + 8); H = 40 + len(names) * (S + 30)
im = Image.new('RGB', (W, H), (12, 13, 18)); dr = ImageDraw.Draw(im); f = T.font(15); fb = T.font(18)
dr.text((8, 8), 'Basilica, bench tiles (voxels, 321 a side; the two cuts are point by point)', fill=(230, 230, 230), font=fb)
for j, nm in enumerate(names):
    y0 = 40 + j * (S + 30)
    for i, (t, lab) in enumerate(COLS):
        p = os.path.join(ROOT, 'out', 'r16', 'bench', 'tiles', nm, t + '.png')
        dr.text((8 + i * (S + 8), y0), f'{nm}: {lab}', fill=(210, 210, 210), font=f)
        if os.path.exists(p):
            im.paste(Image.open(p).convert('RGB').resize((S, S), Image.LANCZOS), (8 + i * (S + 8), y0 + 22))
im.save(os.path.join(HERE, out)); print('wrote', out)

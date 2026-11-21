"""Reviewer check 4: does a group-C verdict depend on the step count? `along` at rabbit30, 161 a side, several counts.
python out/r18/review/drain.py -> out/r18/review/drain.json, drain-along-rabbit30.png"""
import os, sys, json, numpy as np
from scipy import ndimage
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, 'out', 'r16', 'bench'))
import bench as B, rules as R
turns = R.turns
C30 = (-0.122561, 0.645069, 0.372431); N = 161; L = 1.4
a = np.linspace(-L, L, N); X, Y, Z = np.meshgrid(a, a, a, indexing='ij'); h = 2 * L / (N - 1)
ins, death = B.inside(R.get('along'), X, Y, Z, c=C30, steps=80)
rows = []; tiles = []
for s in (10, 14, 20, 30, 40, 60, 80):
    vol = ins | (death > s)
    lab, k = ndimage.label(vol, structure=B.FULL)
    big = float(np.bincount(lab.ravel())[1:].max() / max(vol.sum(), 1)) if k else 0.0
    thick = float(ndimage.distance_transform_edt(vol).max() * h) if k else 0.0
    rows.append(dict(steps=s, volume=float(vol.sum() * h ** 3), pieces=int(k), biggest_piece_pct=100 * big, thickest=thick)); print(rows[-1], flush=True)
    if s in (14, 20, 40, 80):
        tiles.append((s, turns.render(vol, az=-78, el=24)))
json.dump(rows, open(os.path.join(HERE, 'drain.json'), 'w'), indent=1)
w = tiles[0][1].shape[1]; hh = tiles[0][1].shape[0]
sheet = Image.new('RGB', (len(tiles) * (w + 4), hh + 22), (12, 14, 20)); dr = ImageDraw.Draw(sheet)
for i, (s, t) in enumerate(tiles):
    sheet.paste(Image.fromarray(t), (i * (w + 4), 22)); dr.text((i * (w + 4) + 4, 4), 'along, rabbit30, %d steps' % s, fill=(235, 235, 235))
sheet.save(os.path.join(HERE, 'drain-along-rabbit30.png'))

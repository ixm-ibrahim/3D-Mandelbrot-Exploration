"""Reviewer check 3: cuts ACROSS the x-axis (plane x = const), point by point, for the sets `along` passes.
python out/r18/review/across.py  -> out/r18/review/across-*.png"""
import os, sys, numpy as np
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, 'out', 'r16', 'bench'))
import bench as B, rules as R
N = 520
def cut(F, c, x0, hw, cy=0.0, cz=0.0, steps=80):
    a = np.linspace(-hw, hw, N); Y, Z = np.meshgrid(cy + a, cz - a)
    ins, death = B.inside(F, np.full_like(Y, x0), Y, Z, c=c, steps=steps)
    t = np.clip(death / float(steps), 0, 1) ** 0.6
    img = np.zeros((N, N, 3), np.uint8); img[..., 0] = (20 + 40 * t); img[..., 1] = (26 + 70 * t); img[..., 2] = (40 + 150 * t); img[ins] = (238, 228, 200)
    return img
JOBS = [('cauliflower', (0.25, 0, 0), [(0.0, 1.15, 0, 0, 'x = 0, whole'), (0.0, 0.12, 0.60, 0.60, 'x = 0, skin at 45 deg, 0.24 wide'), (0.0, 0.03, 0.795, 0.33, 'x = 0, skin at 22.5 deg, 0.06 wide')]),
        ('airplane', (-1.754878, 0, 0), [(0.0, 0.16, 0, 0, 'x = 0, middle body'), (0.0, 0.02, 0.0735, 0.0735, 'x = 0, skin at 45 deg, 0.04 wide'), (0.06, 0.16, 0, 0, 'x = 0.06')])]
for tag, c, views in JOBS:
    rules = ['oneplane', 'twoplane', 'along']
    sheet = Image.new('RGB', (len(views) * (N + 6), len(rules) * (N + 26)), (12, 14, 20)); dr = ImageDraw.Draw(sheet)
    for r, rule in enumerate(rules):
        for k, (x0, hw, cy, cz, lab) in enumerate(views):
            sheet.paste(Image.fromarray(cut(R.get(rule), c, x0, hw, cy, cz)), (k * (N + 6), r * (N + 26) + 22))
            dr.text((k * (N + 6) + 4, r * (N + 26) + 4), '%s | %s | %s' % (tag, rule, lab), fill=(235, 235, 235))
    sheet.save(os.path.join(HERE, 'across-%s.png' % tag)); print('wrote', tag, flush=True)

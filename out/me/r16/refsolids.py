"""Steering only, no verdicts: the Mandelbrot solids of rules we ALREADY know (two planes nearest, one plane, lathe)
next to the two turning-plane rules, all drawn the same rough way. Question: what does the best member of the
'few exact planes' family look like as a Mandelbrot solid, so the next rule has a concrete target?"""
import os, sys, time
import numpy as np
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, 'out', 'r16', 'bench'))
sys.path.insert(0, os.path.join(ROOT, 'out', 'r14', 'turns'))
sys.path.insert(0, HERE)
import bench as B
import rules as R
import turns

N = int(sys.argv[1]) if len(sys.argv) > 1 else 161
STEPS = 40
L = 1.3; CEN = (-0.55, 0.0, 0.0)
names = sys.argv[2:] or ['twoplane', 'oneplane', 'lathe', 'away', 'along']
S = 300
VIEWS = [('front', -90, 12), ('from above', -90, 80), ('along the x-axis', 180, 0), ('three-quarter', -55, 28)]


def cutimg(F, plane, at=0.0, n=S):
    ins, death = B.cut(F, plane, at=at, L=L, n=n, centre={'z': (CEN[0], 0.0), 'y': (CEN[0], 0.0), 'x': (0.0, 0.0)}[plane], steps=STEPS, mandel=True)
    return np.transpose(B.cut_img(ins, death), (1, 0, 2))[::-1]


rows = []
for nm in names:
    F = R.get(nm); t = time.time()
    vol = B.volume(F, N, L=L, centre=CEN, steps=STEPS, mandel=True)
    h = 2 * L / (N - 1)
    tiles = [turns.render(vol, az=a, el=e, out=S) for _, a, e in VIEWS]
    tiles += [cutimg(F, 'z'), cutimg(F, 'y'), cutimg(F, 'x', at=-0.2), cutimg(F, 'x', at=-1.0)]
    rows.append((R.RULES[nm][1], tiles, vol.sum() * h ** 3))
    print(nm, 'volume', round(vol.sum() * h ** 3, 3), 'in', round(time.time() - t), 's', flush=True)

cols = [v[0] for v in VIEWS] + ['cut z = 0', 'cut y = 0', 'cut x = -0.2', 'cut x = -1 (period-2 body)']
pad, top, lab = 8, 54, 26
W = pad + len(cols) * (S + pad); H = top + len(rows) * (S + lab + pad)
im = Image.new('RGB', (W, H), (12, 14, 20)); d = ImageDraw.Draw(im)
d.text((pad, 8), f'Mandelbrot solids, rough voxels ({N} a side, {STEPS} steps). Steering only.', fill=(235, 235, 240), font=turns.font(22))
for i, (title, tiles, v) in enumerate(rows):
    y = top + i * (S + lab + pad)
    d.text((pad, y), f'{title}   (volume {v:.2f})', fill=(210, 215, 225), font=turns.font(17))
    for j, t in enumerate(tiles):
        t = np.asarray(t)
        if t.shape[0] != S:
            t = np.asarray(Image.fromarray(t).resize((S, S), Image.LANCZOS))
        im.paste(Image.fromarray(t), (pad + j * (S + pad), y + lab))
        d.text((pad + j * (S + pad) + 4, y + lab + 2), cols[j], fill=(150, 160, 175), font=turns.font(13))
im.save(os.path.join(HERE, f'refsolids-{N}.png'))
print('saved')

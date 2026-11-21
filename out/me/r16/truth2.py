"""Close point-by-point cut of the 'along' basilica skin between its planes: are the fine grooves the lab draws real?"""
import sys, os
import numpy as np
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(__file__))
import truth as T, scout3 as S3, scout as S
along = S3.turning(+1)
STEPS = 80
def edge(F, ang, x0):
    s = np.linspace(0.05, 1.0, 20001); a = np.radians(ang)
    n = T.member(F, np.full_like(s, x0), s * np.cos(a), s * np.sin(a), (-1.0, 0.0, 0.0), STEPS)
    ins = n >= STEPS
    return float(s[np.flatnonzero(ins).max()]) if ins.any() else 0.3
rows = []
for name, F in (('along', along), ('two planes (reference)', S.twoplane)):
    for ang in (22.5, 11.25):
        e = edge(F, ang, -0.3)
        tiles = []
        for hw in (0.1, 0.02, 0.004):
            n = T.cut(F, ang, (-0.3 - hw, -0.3 + hw, e - 0.7 * hw, e + 0.7 * hw), 600, 420, STEPS)
            tiles.append(T.shade(n, STEPS))
        rows.append((f'{name}, plane at {ang} degrees, {STEPS} steps, skin near x = -0.3 (height {e:.4f}). Widths 0.2, 0.04, 0.008', tiles))
        print(name, ang, e, flush=True)
W = 10 + 3 * 610; H = 10 + len(rows) * 454
im = Image.new('RGB', (W, H), (12, 14, 20)); d = ImageDraw.Draw(im)
for i, (t, tiles) in enumerate(rows):
    y = 10 + i * 454
    d.text((10, y), t, fill=(230, 230, 235), font=T.font(18))
    for j, a in enumerate(tiles):
        im.paste(Image.fromarray(a), (10 + j * 610, y + 26))
im.save(os.path.join(os.path.dirname(__file__), 'truth2.png'))
print('ok')

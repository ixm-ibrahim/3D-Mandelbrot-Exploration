"""The basilica (c = -1) under the two turning-plane rules, next to the two rules it must beat. For the user.
python out/me/r16/basilicas.py [N]"""
import os, sys, numpy as np
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import scout as S, scout2 as S2, scout3 as S3
turns = S.turns
N = int(sys.argv[1]) if len(sys.argv) > 1 else 257
S.STEPS = 60
ROWS = [('Turning plane, away (new)', 'Tear-free for every c. Buds in 4 directions.', S3.turning(-1)),
        ('Turning plane, along (new)', 'Tear-free for every c. Buds in 8 directions.', S3.turning(1)),
        ('Two planes, as before', 'The look you liked. Tears away from the x-axis.', S.twoplane),
        ('One plane, as before', 'Buds only in the flat plane.', S.oneplane)]
COLS = ['Seen from the front', 'Seen from above', 'Seen along the x-axis', 'Cut at z = 0 (flat plane)', 'Cut at y = 0 (upright plane)', 'Cut across the middle (x = 0)']
W, L0 = 330, 300
sheet = Image.new('RGB', (L0 + W * len(COLS), 40 + W * len(ROWS)), (12, 14, 20)); dr = ImageDraw.Draw(sheet); f1, f2, f3 = S2.font(17), S2.font(16), S2.font(13)
for k, t in enumerate(COLS): dr.text((L0 + 6 + k * W, 10), t, fill=(235, 235, 235), font=f1)
a = np.linspace(-1.75, 1.75, N); X, Y, Z = np.meshgrid(a, a, a, indexing='ij'); C = (-1, 0, 0)
for r, (name, note, F) in enumerate(ROWS):
    vol, _ = S.run(F, X, Y, Z)
    tiles = [turns.render(vol, az=-60, el=22), turns.render(vol, az=-60, el=75), turns.render(vol, az=0, el=0),
             S3.cutc(F, 'z', C, n=601), S3.cutc(F, 'y', C, n=601), S3.cutc(F, 'x', C, L=1.0, n=601)]
    y0 = 40 + r * W
    dr.text((10, y0 + W // 2 - 24), name, fill=(240, 240, 240), font=f2)
    for j, line in enumerate([note[:38], note[38:]] if len(note) > 38 else [note]):
        dr.text((10, y0 + W // 2 + j * 18), line.strip(), fill=(185, 190, 200), font=f3)
    for k, im in enumerate(tiles): sheet.paste(Image.fromarray(im).resize((W - 6, W - 6), Image.LANCZOS), (L0 + k * W, y0))
    print(name, 'volume %.3f' % (vol.mean() * 3.5 ** 3), flush=True)
out = os.path.join(HERE, 'basilicas.png'); sheet.save(out); print('wrote', out, sheet.size)

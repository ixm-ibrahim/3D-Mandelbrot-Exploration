"""The section's sheets: rough solids, one row per rule, the four standard sets, two eyes.

    python out/r25/pillow/sheet.py job <rule key> <eye: a|top> [sets]     one row's solids, kept in cache/
    python out/r25/pillow/sheet.py make                                    sheet.png (eye a) and sheet-top.png
"""
import os, sys, time
import numpy as np
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import pil as P
import best as B
M = P.M

CAMS = {'a': (0.45, 0.5, 1.0), 'top': (0.2, 1.0, 0.35)}
SETS = [('m1', 'c = -1', (-1.0, 0.0, 0.0)), ('rab', 'rabbit', M.RABBIT), ('m075', 'c = -0.75', (-0.75, 0.0, 0.0)), ('sie', 'Siegel disc', M.SIEGEL)]
ROWS = [
    ('one', 'One plane (what we have: clean, nothing above or below the bodies)'),
    ('square', 'Square pillow of round 15: the two seams one above the other'),
    ('tetra', 'Tetrahedron pillow: the two seams crossed'),
    ('skew', 'Skew pillow: the top seam turned 135 degrees against the bottom one'),
]
W, H_, ND, STEPS = 320, 240, 140, 30
CACHE = os.path.join(HERE, 'cache')


def get(key):
    return M.bench('oneplane') if key == 'one' else B.rule(key)


def job(key, eye, only=None):
    os.makedirs(CACHE, exist_ok=True); r = get(key); t0 = time.time()
    for sk, sn, c in SETS:
        if only and sk not in only:
            continue
        path = os.path.join(CACHE, '%s-%s-%s.npz' % (key, sk, eye))
        if os.path.exists(path):
            continue
        dep, px = M.solid(r, c, W, H_, ND, STEPS, cam=CAMS[eye]); np.savez_compressed(path, dep=dep, px=px)
        print(key, sk, eye, '%.0f s' % (time.time() - t0)); sys.stdout.flush()


def make():
    pad = 10
    for eye, name, head in (('a', 'sheet.png', 'seen from the front, a little from above'), ('top', 'sheet-top.png', 'seen from the side, looking along the flat picture')):
        Wd = pad + len(SETS) * (W + pad); Ht = 50 + len(ROWS) * (H_ + 34)
        im = Image.new('RGB', (Wd, Ht), (12, 14, 20)); d = ImageDraw.Draw(im)
        d.text((pad, 10), 'Even-spacing rules ("pillows"), rough solids, %s' % head, fill=(240, 240, 245), font=M.font(21))
        for i, (key, label) in enumerate(ROWS):
            y = 50 + i * (H_ + 34); d.text((pad, y), label, fill=(235, 220, 170), font=M.font(16))
            for j, (sk, sn, c) in enumerate(SETS):
                path = os.path.join(CACHE, '%s-%s-%s.npz' % (key, sk, eye)); x = pad + j * (W + pad)
                if os.path.exists(path):
                    z = np.load(path); im.paste(Image.fromarray(M.shade_solid(z['dep'], float(z['px']))), (x, y + 24))
                d.text((x + 6, y + 28), sn, fill=(150, 160, 175), font=M.font(13))
        im.save(os.path.join(HERE, name)); print('wrote', name, im.size)


if __name__ == '__main__':
    if sys.argv[1] == 'job':
        job(sys.argv[2], sys.argv[3], sys.argv[4].split(',') if len(sys.argv) > 4 else None)
    else:
        make()

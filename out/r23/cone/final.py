"""The sheet of this section: rough solids, rows = rules, columns = c = -1, c = -0.75, rabbit, Siegel disc.

    python out/r23/cone/final.py render eye key [key ...]   compute and keep the depth pictures (cache/)
    python out/r23/cone/final.py sheet eye out.png key [key ...]
"""
import os, sys, time
import numpy as np
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import conelib as L
import variants as V
M = L.M
EYES = {'a': (0.45, 0.5, 1.0), 'top': (0.2, 1.0, 0.35), 'y': (-0.9, 0.45, 0.6)}
W, H, ND, STEPS = 340, 255, 210, int(os.environ.get('STEPS', '30'))
CACHE = os.path.join(HERE, 'cache'); os.makedirs(CACHE, exist_ok=True)
PLAIN = {'oneplane': 'Sphere inversions, one plane', 'along': 'Turning plane, along',
         'weld90b2': 'New this round: the flat picture also rolled up into two cones (one fixed rule)',
         'weldc': 'The same, with the cones turned to follow c',
         'weld0b2': 'The same rule with the cones opening along +x (mirror-symmetric choice)',
         'weldpib2': 'The same rule with the cones opening along -x (mirror-symmetric choice)',
         'scout+': 'The scout rule (cones opening along +x)', 'scout-': 'The scout rule (cones opening along -x)'}


def fn(key, si, eye):
    return os.path.join(CACHE, '%s-%d-%s-%d.npy' % (key.replace('+', 'p').replace('-', 'm'), si, eye, STEPS))


def render(eye, keys):
    t0 = time.time()
    for k in keys:
        r = V.get(k)
        for si, (sn, c) in enumerate(L.SETS):
            p = fn(k, si, eye)
            if os.path.exists(p):
                continue
            dep, px = M.solid(r, c, W, H, ND, STEPS, cam=EYES[eye]); np.save(p, dep)
            print('rendered', k, sn, eye, '%.0f s' % (time.time() - t0)); sys.stdout.flush()


def sheet(eye, out, keys, title=None):
    pad = 10; px = 3.5 / (W - 1)
    im = Image.new('RGB', (pad + 4 * (W + pad), 50 + len(keys) * (H + 34)), (12, 14, 20)); d = ImageDraw.Draw(im)
    d.text((pad, 10), title or 'Real shapes (rough blocks, %d steps)' % STEPS, fill=(240, 240, 245), font=M.font(21))
    for i, k in enumerate(keys):
        y = 50 + i * (H + 34); d.text((pad, y), PLAIN.get(k, k), fill=(235, 220, 170), font=M.font(17))
        for si, (sn, c) in enumerate(L.SETS):
            dep = np.load(fn(k, si, eye)); x = pad + si * (W + pad)
            im.paste(Image.fromarray(M.shade_solid(dep, px)), (x, y + 26)); d.text((x + 6, y + 30), sn, fill=(150, 160, 175), font=M.font(13))
    im.save(out); print('wrote', out, im.size)


if __name__ == '__main__':
    if sys.argv[1] == 'render':
        render(sys.argv[2], sys.argv[3:])
    else:
        sheet(sys.argv[2], os.path.join(HERE, sys.argv[3]), sys.argv[4:])

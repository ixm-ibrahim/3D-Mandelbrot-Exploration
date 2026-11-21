"""Stage 1b pictures: the rabbit Julia set, c = (-0.122561, 0.744862, 0), for one rule (bench functions called directly).
    python out/r17/profiles/rabbit.py run <rule> [N]      -> out/r17/profiles/rabbit/<rule>-*.png, <rule>.json
    python out/r17/profiles/rabbit.py sheet <rule> ...    -> out/r17/profiles/rabbits.png
Only Julia sets. For p_ rules this is run only after the rule's stage 1 passed; for the known rules it is the yardstick."""
import os, sys, json, time
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, 'out', 'me', 'r16')); sys.path.insert(0, os.path.join(ROOT, 'out', 'r16', 'bench'))
import rules as R, bench as B, truth as T
turns = R.turns
OUT = os.path.join(HERE, 'rabbit'); os.makedirs(OUT, exist_ok=True)
C = (-0.122561, 0.744862, 0.0); STEPS = 40; L = 1.6
VIEWS = (('front', -60, 22), ('above', -60, 75), ('alongx', 0, 0), ('side', 30, 15))

def run(name, N=201):
    F = R.get(name); t0 = time.time()
    vol = B.volume(F, N, L=L, c=C, steps=STEPS); h = 2 * L / (N - 1)
    lab, n = ndimage.label(vol, structure=B.FULL); sz = np.bincount(lab.ravel())[1:]
    fat = ndimage.binary_dilation(vol, structure=B.FULL); lab2, n2 = ndimage.label(fat, structure=B.FULL); s2 = np.bincount(lab2[vol], minlength=n2 + 1)[1:]
    res = dict(rule=name, N=N, volume=float(vol.sum() * h ** 3), pieces=int(n), biggest_pct=float(100 * sz.max() / max(vol.sum(), 1)) if n else 0.0,
               pieces_gap=int((s2 > 0).sum()), biggest_pct_gap=float(100 * s2.max() / max(vol.sum(), 1)) if n else 0.0)
    # how far the solid reaches off the flat plane, against how far it reaches in it (a flat slab is small, a lump is 1)
    idx = np.argwhere(vol)
    if len(idx):
        ext = (idx.max(0) - idx.min(0)) * h; res['reach_x_y_z'] = [float(v) for v in ext]
    for tag, az, el in VIEWS:
        Image.fromarray(turns.render(vol, az=az, el=el)).save(os.path.join(OUT, '%s-%s.png' % (name, tag)))
    for pl in 'zyx':
        ins, death = B.cut(F, pl, L=L, n=501, c=C, steps=STEPS)
        Image.fromarray(B.cut_img(ins, death)).save(os.path.join(OUT, '%s-cut%s.png' % (name, pl)))
        if pl == 'z':
            flat = B.flat_set(L=L, n=501, c=C, steps=STEPS); res['cut_z0_differs'] = int((ins ^ flat).sum()); res['flat_points'] = int(flat.sum())
    # the cut through the x-axis at 45 degrees (the diagonal plane, where the two-plane rule tears)
    a = np.linspace(-L, L, 501); A, Bb = np.meshgrid(a, a, indexing='ij'); s = np.sqrt(0.5)
    ins, death = B.inside(F, A, Bb * s, Bb * s, c=C, steps=STEPS)
    Image.fromarray(B.cut_img(ins, death)).save(os.path.join(OUT, '%s-cutd.png' % name))
    # the cut x = 0 close to the diagonal: 3 times closer
    res['seconds'] = time.time() - t0
    json.dump(res, open(os.path.join(OUT, name + '.json'), 'w'), indent=1)
    print(name, res, flush=True)

def sheet(names, out='rabbits.png', title='Stage 1b: the rabbit, c = (-0.122561, 0.744862, 0). Julia sets only. 201 points a side, 40 steps.'):
    S = 300; cols = [('front', 'Front'), ('above', 'From above'), ('alongx', 'Along the x-axis'), ('side', 'From the side'), ('cutz', 'Cut z = 0 (must be the flat rabbit)'), ('cuty', 'Cut y = 0'), ('cutx', 'Cut x = 0'), ('cutd', 'Cut through the x-axis at 45 degrees')]
    im = Image.new('RGB', (10 + len(cols) * (S + 6), 50 + len(names) * (S + 52)), (12, 14, 20)); d = ImageDraw.Draw(im)
    d.text((10, 10), title, fill=(235, 235, 240), font=T.font(22))
    for r, nm in enumerate(names):
        y = 50 + r * (S + 52); j = json.load(open(os.path.join(OUT, nm + '.json')))
        d.text((10, y), '%s  [%s]:  volume %.2f; biggest piece %.2f %% (%d pieces; with a one-voxel gap allowed %.3f %%, %d pieces); reach x, y, z = %.2f, %.2f, %.2f; cut z = 0 differs from the flat rabbit in %d of %d points' % (
            R.RULES[nm][1], nm, j['volume'], j['biggest_pct'], j['pieces'], j['biggest_pct_gap'], j['pieces_gap'], *j['reach_x_y_z'], j['cut_z0_differs'], j['flat_points']), fill=(225, 225, 230), font=T.font(15))
        for k, (tag, lab) in enumerate(cols):
            t = Image.open(os.path.join(OUT, '%s-%s.png' % (nm, tag))).convert('RGB').resize((S, S), Image.LANCZOS)
            im.paste(t, (10 + k * (S + 6), y + 40)); d.text((14 + k * (S + 6), y + 22), lab, fill=(170, 175, 190), font=T.font(13))
    im.save(os.path.join(HERE, out)); print('wrote', os.path.join(HERE, out))

if __name__ == '__main__':
    if sys.argv[1] == 'run':
        run(sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 201)
    else:
        sheet(sys.argv[2:])

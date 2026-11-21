"""Round 23 outside1: rough solids of c = -1 and the rabbit, two eye positions, for every outside formula.
    python out/r23/outside1/draw.py tiles name [name ...]     makes tiles/<name>-<shape>-<eye>.png (skips those that exist)
    python out/r23/outside1/draw.py all                       pastes all-solids-1.png, all-solids-2.png from the tiles
    python out/r23/outside1/draw.py sheet a b c               sheet.png: one plane, two planes, along, then a, b, c (bigger tiles)
    python out/r23/outside1/draw.py cuts name [name ...]      cuts-<name>.png: c = -1 and rabbit, flat / 22.5 / 45 / 90 degrees and across x
"""
import os, sys, time
import numpy as np
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(ROOT, 'out', 'r21', 'lib'))
import mem as M, outrules as O

EYES = {'front': (0.45, 0.5, 1.0), 'side': (1.0, 0.42, 0.22)}
SHAPES = {'c-1': (-1.0, 0.0, 0.0), 'rabbit': M.RABBIT}
REF = ['oneplane', 'twoplane', 'along']
REFLABEL = {'oneplane': 'Sphere inversions, one plane (ours)', 'twoplane': 'Sphere inversions, two planes (ours)', 'along': 'Turning plane, along (ours)'}
STEPS = 28


def rule(nm):
    return M.bench(nm) if nm in REF else O.get(nm)


def label(nm):
    return REFLABEL.get(nm) or O.LABEL[nm]


def tile(nm, shape, eye, w, h, nd, folder):
    p = os.path.join(HERE, folder, '%s-%s-%s.png' % (nm, shape, eye))
    if not os.path.exists(p):
        with np.errstate(all='ignore'):
            dep, px = M.solid(rule(nm), SHAPES[shape], w, h, nd, STEPS, cam=EYES[eye])
        Image.fromarray(M.shade_solid(dep, px)).save(p)
    return Image.open(p)


def strip_sheet(names, path, w, h, nd, folder, title):
    os.makedirs(os.path.join(HERE, folder), exist_ok=True)
    cols = [(s, e) for s in ('c-1', 'rabbit') for e in ('front', 'side')]
    heads = ['c = -1, from the front', 'c = -1, looking along the x-axis', 'rabbit, from the front', 'rabbit, looking along the x-axis']
    pad = 10; W = pad + 4 * (w + pad); H = 50 + len(names) * (h + 34)
    im = Image.new('RGB', (W, H), (12, 14, 20)); d = ImageDraw.Draw(im)
    d.text((pad, 10), title, fill=(240, 240, 245), font=M.font(21))
    for i, nm in enumerate(names):
        y = 50 + i * (h + 34); d.text((pad, y), label(nm), fill=(235, 220, 170), font=M.font(17)); t0 = time.time()
        for j, (s, e) in enumerate(cols):
            x = pad + j * (w + pad); im.paste(tile(nm, s, e, w, h, nd, folder), (x, y + 26)); d.text((x + 6, y + 30), heads[j], fill=(150, 160, 175), font=M.font(13))
        print(nm, '%.0f s' % (time.time() - t0), flush=True)
    im.save(path); return path


def cuts(nm, steps=60, w=300, h=220):
    r = rule(nm); pad = 8; angs = (0.0, 22.5, 45.0, 90.0)
    W = pad + 5 * (w + pad); H = 40 + 2 * (h + 26)
    im = Image.new('RGB', (W, H), (12, 14, 20)); d = ImageDraw.Draw(im)
    d.text((pad, 8), '%s: cuts (%d steps). Row 1: c = -1, row 2: rabbit' % (label(nm), steps), fill=(240, 240, 245), font=M.font(18))
    for i, (sn, c) in enumerate(SHAPES.items()):
        y = 40 + i * (h + 26)
        with np.errstate(all='ignore'):
            pics = [M.shade(M.cut_axis(r, a, w, h, steps, c=c), steps) for a in angs] + [M.shade(M.cut_across(r, -0.5 if sn == 'c-1' else 0.0, h, steps, c=c), steps)]
        x = pad
        for hd, pic in zip(['plane turned %g' % a for a in angs] + ['across the x-axis at x = %g' % (-0.5 if sn == 'c-1' else 0.0)], pics):
            d.text((x, y), hd, fill=(150, 160, 175), font=M.font(13)); im.paste(Image.fromarray(pic), (x, y + 18)); x += pic.shape[1] + pad
    p = os.path.join(HERE, 'cuts-%s.png' % nm); im.save(p); return p


if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'tiles':
        os.makedirs(os.path.join(HERE, 'tiles'), exist_ok=True)
        for nm in sys.argv[2:]:
            t0 = time.time()
            for s in SHAPES:
                for e in EYES:
                    tile(nm, s, e, 250, 190, 150, 'tiles')
            print(nm, '%.0f s' % (time.time() - t0), flush=True)
    elif cmd == 'all':
        names = REF + O.NAMES
        strip_sheet(names[:10], os.path.join(HERE, 'all-solids-1.png'), 250, 190, 150, 'tiles', 'Outside formulas, rough solids (%d steps), part 1' % STEPS)
        strip_sheet(names[10:], os.path.join(HERE, 'all-solids-2.png'), 250, 190, 150, 'tiles', 'Outside formulas, rough solids (%d steps), part 2' % STEPS)
    elif cmd == 'sheet':
        strip_sheet(REF + sys.argv[2:], os.path.join(HERE, 'sheet.png'), 300, 228, 190, 'tiles-big', 'Three of ours, then the three outside formulas that come closest')
    elif cmd == 'cuts':
        for nm in sys.argv[2:]:
            print(cuts(nm), flush=True)

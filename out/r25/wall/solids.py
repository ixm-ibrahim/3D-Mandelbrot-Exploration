"""Rough solids, one job per (rule, set, eye), kept in cache/ so that sheets can be put together afterwards.

    python out/r25/wall/solids.py job <rule key> <set key> <a|top> [nd] [steps]
    python out/r25/wall/solids.py sheet <name>          (name: square | cube)
"""
import os, sys, time
import numpy as np
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import wall as W
import pil as PL
M = W.M
CACHE = os.path.join(HERE, 'cache'); os.makedirs(CACHE, exist_ok=True)
CAMS = {'a': (0.45, 0.5, 1.0), 'top': (0.2, 1.0, 0.35), 'side': (1.0, 0.35, 0.3)}
w, h = 400, 300


def rule_of(key):
    if key in W.RULES:
        return W.RULES[key]()
    return {'p3b': lambda: PL.rule_pillow(3, True, np.pi / 4), 'p2': lambda: PL.rule_lop(2), 'pillow': lambda: M.bench('pillow'), 'p3': lambda: PL.rule_pillow(3), 'o3': lambda: PL.rule_oneplane(3), 'p5': lambda: PL.rule_pillow(5), 'o5': lambda: PL.rule_oneplane(5),
            'twoplane': lambda: M.bench('twoplane'), 'along': lambda: M.bench('along')}[key]()


def set_of(key):
    if key.startswith('c_'):                       # any c in the flat plane: c_<re>_<im>, e.g. c_0.1_1.0
        a, b = (float(t) for t in key[2:].split('_')); return ('c = %g %+gi' % (a, b), (a, b, 0.0))
    s3 = PL.sets3()
    return {'m1': ('c = -1', (-1.0, 0.0, 0.0)), 'rab': ('rabbit', M.RABBIT), 'c0': ('c = 0', (0.0, 0.0, 0.0)),
            'i': ('c = i', s3[0][1]), 'p3': ('c = 0.558 + 0.540i', s3[1][1]), 'r3': ('c = 0.3', s3[2][1]), 'j': ('c = 0.59i', s3[3][1]),
            'g': ('c = 0.45 + 0.35i', (0.45, 0.35, 0.0))}[key]


def path(rk, sk, eye):
    return os.path.join(CACHE, '%s_%s_%s.npz' % (rk, sk, eye))


def job(rk, sk, eye, nd=180, steps=28):
    t0 = time.time(); r = rule_of(rk); nm, c = set_of(sk)
    dep, px = M.solid(r, c, w, h, nd, steps, cam=CAMS[eye], half_w=1.75)
    np.savez_compressed(path(rk, sk, eye), dep=dep, px=px, nd=nd, steps=steps)
    print('solid %s %s %s nd %d steps %d: %.0f s, %d pixels hit' % (rk, sk, eye, nd, steps, time.time() - t0, int(np.isfinite(dep).sum()))); sys.stdout.flush()


SHEETS = {
    'square': dict(title='The square, z -> z^2 + c. Real shapes, rough blocks.', rows=[
        ('oneplane', 'One plane (the baseline): clean blown-up bodies, buds only round the flat picture'),
        ('ws', 'Three times round the unit circle, then one plane: the one thing the list of four had missed'),
        ('zooA', 'The same flat rule written another way, z (z + c / z): not "a square, then add c"')],
        cols=[('m1', 'a'), ('m1', 'top'), ('rab', 'a'), ('rab', 'top')]),
    'cube': dict(title='The cube, z -> z^3 + c, where an evenly spaced pattern can sit the same above and below. Real shapes, rough blocks.', rows=[
        ('o3', 'One plane for the cube (the baseline)'),
        ('p3', 'Evenly spaced cube (square pillow, four special spots)')],
        cols=[('i', 'a'), ('i', 'top'), ('p3', 'a'), ('p3', 'top')]),
}
SHEETS['scan'] = dict(title='Evenly spaced cube: c moved off the y-axis, and other c. Rough blocks, from the front.', rows=[
    ('p3', 'Evenly spaced cube (square pillow)')],
    cols=[('i', 'a'), ('c_0.08_1.0', 'a'), ('c_0.16_0.96', 'a'), ('c_0_0.59', 'a'), ('c_0.3_0.5', 'a')])
SHEETS['band'] = dict(title='Evenly spaced cube, laid like one plane beside the flat picture (the band layout).', rows=[
    ('p3', 'Evenly spaced cube'), ('p3b', 'The same, laid like one plane up to 41 degrees above and below the flat picture')],
    cols=[('i', 'a'), ('i', 'top'), ('p3', 'a'), ('p3', 'top')])

SHEETS['five'] = dict(title='The fifth power, z -> z^5 + c: a test of where the lumps come. Real shapes, rough blocks.', rows=[
    ('o5', 'One plane for the fifth power (the baseline)'),
    ('p5', 'Evenly spaced bulbs for the fifth power (same pillow, four special spots)')],
    cols=[('c_0.7071_0.7071', 'a'), ('c_0.7071_0.7071', 'top'), ('c_0.2639_0.767', 'a'), ('c_0.2639_0.767', 'top'), ('c_0.767_0.2639', 'a')])

# the two sheets that go into the report: every rule of this section from one eye
FINAL = [
    ('oneplane', ['m1', 'rab'], 'One plane (z^2 + c, the baseline).', 'Clean blown-up bodies. Buds sit only round the flat picture.'),
    ('p2', ['m1', 'rab'], 'Evenly spaced bulbs for the square (z^2 + c).', None),
    ('ws', ['m1', 'rab'], 'Three times round the unit circle, then one plane (z^2 + c).', None),
    ('zooA', ['m1', 'rab'], 'The flat rule written as z times (z + c / z)  (z^2 + c).', None),
    ('o3', ['i', 'p3'], 'One plane for the cube (z^3 + c, the baseline).', None),
    ('p3', ['i', 'p3'], 'Evenly spaced bulbs for the cube (z^3 + c).', None),
]
CAPTIONS = {}


def final(eye, out):
    pad = 10; ncol = 2
    Wd = pad + ncol * (w + pad); H = 50 + len(FINAL) * (h + 52)
    im = Image.new('RGB', (Wd, H), (12, 14, 20)); d = ImageDraw.Draw(im)
    d.text((pad, 10), 'Real shapes, rough blocks, %s' % EYE[eye], fill=(240, 240, 245), font=M.font(20))
    for i, (rk, sks, lab, cap) in enumerate(FINAL):
        y = 50 + i * (h + 52); d.text((pad, y), lab, fill=(235, 220, 170), font=M.font(16))
        cap = CAPTIONS.get(rk, cap)
        if cap:
            d.text((pad, y + 22), cap, fill=(190, 195, 205), font=M.font(13))
        for j, sk in enumerate(sks):
            x = pad + j * (w + pad); p = path(rk, sk, eye)
            if os.path.exists(p):
                z = np.load(p); im.paste(Image.fromarray(M.shade_solid(z['dep'], float(z['px']))), (x, y + 42))
            else:
                d.rectangle([x, y + 42, x + w, y + 42 + h], outline=(60, 60, 70)); d.text((x + 8, y + 60), 'not drawn', fill=(120, 120, 130), font=M.font(13))
            d.text((x + 6, y + 46), set_of(sk)[0], fill=(150, 160, 175), font=M.font(13))
    p = os.path.join(HERE, out); im.save(p); print('wrote', p, im.size)


EYE = {'a': 'from the front', 'top': 'from above', 'side': 'from the side'}


def sheet(name, out=None):
    S = SHEETS[name]; pad = 10
    Wd = pad + len(S['cols']) * (w + pad); H = 50 + len(S['rows']) * (h + 34)
    im = Image.new('RGB', (Wd, H), (12, 14, 20)); d = ImageDraw.Draw(im)
    d.text((pad, 10), S['title'], fill=(240, 240, 245), font=M.font(20))
    for i, (rk, lab) in enumerate(S['rows']):
        y = 50 + i * (h + 34); d.text((pad, y), lab, fill=(235, 220, 170), font=M.font(16))
        for j, (sk, eye) in enumerate(S['cols']):
            x = pad + j * (w + pad); p = path(rk, sk, eye)
            if os.path.exists(p):
                z = np.load(p); im.paste(Image.fromarray(M.shade_solid(z['dep'], float(z['px']))), (x, y + 24))
            else:
                d.rectangle([x, y + 24, x + w, y + 24 + h], outline=(60, 60, 70)); d.text((x + 8, y + 40), 'not drawn', fill=(120, 120, 130), font=M.font(13))
            d.text((x + 6, y + 28), '%s, %s' % (set_of(sk)[0], EYE[eye]), fill=(150, 160, 175), font=M.font(13))
    p = os.path.join(HERE, out or ('sheet-%s.png' % name)); im.save(p); print('wrote', p, im.size)


if __name__ == '__main__':
    if sys.argv[1] == 'job':
        job(sys.argv[2], sys.argv[3], sys.argv[4], *(int(t) for t in sys.argv[5:7]))
    elif sys.argv[1] == 'final':
        import json
        cp = os.path.join(HERE, 'captions.json')
        if os.path.exists(cp):
            CAPTIONS.update(json.load(open(cp, encoding='utf-8')))
        final('a', 'sheet.png'); final('top', 'sheet-top.png')
    else:
        sheet(sys.argv[2], *(sys.argv[3:4]))

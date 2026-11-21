"""One sheet for the user: the reference-plane family from its gentle end to its tear end.
python out/r17/profiles/family_sheet.py"""
import os, sys, json
import numpy as np
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, HERE)
import screen as S
import myrules as M
R, T, CC = S.R, S.T, S.CC
BENCH = os.path.join(ROOT, 'out', 'r16', 'bench')
sys.path.insert(0, BENCH)
import bench as B

ROWS = [  # rule, plain name, hair numbers (None = read from cc/<rule>.json)
    ('p_lin',    'Fades to the spun rule at the x-axis (the first candidate)', None),
    ('p_n8',     'Narrow flat spots, gentle crossing', None),
    ('along',    'Round 16: Turning plane, along', [0.53, 1.19, 0.29, 1.21, 3.12, 0.57]),
    ('p_h4',     'Wide flat spots, steeper crossing', None),
    ('p_tt16',   'Nearest plane, crossing in a band about 7 degrees wide', None),
    ('p_tt64',   'Nearest plane, crossing in a band about 1.8 degrees wide', None),
    ('p_tt256',  'Nearest plane, crossing in a band about 0.45 degrees wide', None),
    ('p_tt1024', 'Nearest plane, crossing in a band about 0.1 degrees wide', None),
    ('twoplane', 'Two planes, nearest plane: the tear itself (the look you liked)', [0.02, 0.03, 0.03, 0.01, 0.04, 0.01]),
]
RABBIT = {'along': 'one swollen lump (one piece)', 'p_tt256': 'FAIL: breaks into pieces', 'p_tt1024': 'FAIL: breaks into pieces', 'twoplane': 'breaks into pieces'}
cover = json.load(open(os.path.join(HERE, 'cover.json'))) if os.path.exists(os.path.join(HERE, 'cover.json')) else {}


def tt(k):
    return lambda p: 0.5 * np.pi * 0.5 * (1 + np.tanh(k * np.tan(np.pi * (np.clip(p / (0.5 * np.pi), 1e-12, 1 - 1e-12) - 0.5))))


FORMS = {'p_lin': lambda p: p - np.sin(4 * p) / 4, 'p_n8': lambda p: p - M.g_notch(8)(4 * p) / 4, 'along': lambda p: p - np.sin(4 * p) / 4,
         'p_h4': lambda p: p - M.g_hump(4)(4 * p) / 4, 'twoplane': lambda p: np.where(p < np.pi / 4, 0.0, np.pi / 2),
         'p_tt16': tt(16), 'p_tt64': tt(64), 'p_tt256': tt(256), 'p_tt1024': tt(1024)}


def plot_profile(name, S_=300):
    phi = np.linspace(0, np.pi / 2, 600); psi = FORMS[name](phi)
    im = Image.new('RGB', (S_, S_), (16, 18, 26)); d = ImageDraw.Draw(im); m = 34

    def xy(p, q):
        return (m + (S_ - 2 * m) * p / (np.pi / 2), S_ - m - (S_ - 2 * m) * q / (np.pi / 2))
    d.rectangle([m, m, S_ - m, S_ - m], outline=(70, 75, 90))
    d.line([xy(0, 0), xy(np.pi / 2, np.pi / 2)], fill=(70, 75, 90))
    if name == 'p_lin':
        for a in (0.25, 0.5, 0.75):
            d.line([xy(p, p - a * np.sin(4 * p) / 4) for p in phi], fill=(120, 105, 60), width=1)
    d.line([xy(a, b) for a, b in zip(phi, psi)], fill=(240, 200, 90), width=3)
    d.text((m, 8), 'reference plane (up) against the point (across)', fill=(170, 175, 190), font=T.font(12))
    d.text((m - 4, S_ - m + 4), 'flat plane', fill=(170, 175, 190), font=T.font(12)); d.text((S_ - m - 78, S_ - m + 4), 'upright plane', fill=(170, 175, 190), font=T.font(12))
    if name == 'p_lin':
        d.text((m + 6, m + 6), 'thick: on the plane x = 0\nthin: nearer the x-axis', fill=(170, 175, 190), font=T.font(12))
    return im


def tile(rule, tag, S_=300):
    p = os.path.join(BENCH, 'tiles', rule, tag + '.png')
    return Image.open(p).convert('RGB').resize((S_, S_), Image.LANCZOS) if os.path.exists(p) else Image.new('RGB', (S_, S_), (16, 18, 26))


def cc_tile(rule, hair, S_=300):
    p = os.path.join(HERE, 'cc', 'closecut-%s.png' % rule)
    if not os.path.exists(p):
        p = os.path.join(ROOT, 'out', 'me', 'r16', 'closecut-%s.png' % rule)
    k = int(np.nanargmax(hair)); i, j = divmod(k, 3)
    im = Image.open(p).convert('RGB'); x = 10 + j * 610; y = 10 + i * 454 + 26
    return im.crop((x, y, x + 600, y + 420)).resize((int(S_ * 600 / 420), S_), Image.LANCZOS), (0.2, 0.04, 0.008)[j], (22.5, 11.25)[i]


def cliff(F, g=1e-3, n=200000):
    rng = np.random.default_rng(11); th = np.arccos(rng.uniform(-1, 1, n)); x = np.cos(th); rho = np.sin(th)
    d = np.minimum(g / 2 / np.maximum(rho, 1e-12), 0.7)
    a = np.stack(F(x, rho * np.cos(np.pi / 4 - d), rho * np.sin(np.pi / 4 - d)), 1); b = np.stack(F(x, rho * np.cos(np.pi / 4 + d), rho * np.sin(np.pi / 4 + d)), 1)
    return float(np.linalg.norm(a - b, axis=1).max())


S_ = 300; CW = int(S_ * 600 / 420); TXT = 600
W = 10 + 4 * (S_ + 6) + CW + 6 + TXT; RH = S_ + 44
im = Image.new('RGB', (W, 100 + len(ROWS) * RH), (12, 14, 20)); d = ImageDraw.Draw(im)
d.text((10, 8), 'Round 17, profiles: the reference-plane family at the basilica (c = -1), from its gentle end (top) to its tear end (bottom)', fill=(235, 235, 240), font=T.font(22))
d.text((10, 40), 'Every rule here squares a point by the one-plane rule about a plane through the x-axis that depends on where the point is. Gentle crossing between the planes: hair, droplets, rings.', fill=(190, 195, 205), font=T.font(14))
d.text((10, 60), 'Sharp crossing: clean skin, but the rule is then the two-plane tear in all but name and its rabbit breaks into pieces just as the two-plane rabbit does. No member passes. No Mandelbrot solid was drawn.', fill=(190, 195, 205), font=T.font(14))
xs = [10, 10 + S_ + 6, 10 + 2 * (S_ + 6), 10 + 3 * (S_ + 6), 10 + 3 * (S_ + 6) + CW + 6, 10 + 4 * (S_ + 6) + CW + 6]
summary = {}
for r, (rule, plain, hair) in enumerate(ROWS):
    y = 100 + r * RH
    if hair is None:
        hair = json.load(open(os.path.join(HERE, 'cc', rule + '.json')))['hair']
    worst = float(np.nanmax(hair)); F = R.get(rule)
    res = B.load(rule); ver = B.verdicts(res) if res else None
    fails = [k for k, v in ver.items() if not v[0]] if ver else None
    bench_line = 'not run' if ver is None else ('passes all eight' if not fails else 'fails ' + ', '.join(fails))
    cl = cliff(F); cv = cover.get(rule, {})
    d.text((10, y), '%s   [%s]' % (plain, rule), fill=(235, 235, 240), font=T.font(17))
    im.paste(plot_profile(rule), (xs[0], y + 26)); im.paste(tile(rule, 'front'), (xs[1], y + 26)); im.paste(tile(rule, 'close2'), (xs[2], y + 26))
    ct, wd, ang = cc_tile(rule, hair); im.paste(ct, (xs[3], y + 26))
    rb = os.path.join(HERE, 'rabbit', rule + '-front.png')
    if rule in RABBIT and os.path.exists(rb):
        im.paste(Image.open(rb).convert('RGB').resize((S_, S_), Image.LANCZOS), (xs[4], y + 26))
    else:
        t = Image.new('RGB', (S_, S_), (16, 18, 26)); dd = ImageDraw.Draw(t)
        dd.text((40, 130), 'rabbit not drawn:\nthe basilica did not pass', fill=(150, 155, 170), font=T.font(15)); im.paste(t, (xs[4], y + 26))
    ok_cc = worst <= 0.3
    lines = [('Close cut (skin between the planes, %g wide): hair %.2f  %s' % (wd, worst, 'pass' if ok_cc else 'FAIL (limit 0.3)'), ok_cc),
             ('Bench, eight basilica tests: %s' % bench_line, bool(ver) and not fails),
             ('Cliff: two points 0.001 apart across the diagonal land %.3g apart' % cl, cl < 0.05),
             ('   (a gentle rule gives about 0.006; a tear gives 1.95)', None),
             ('Directions turned inside out: %s' % ('%.1f %%; they cover the sphere %.2f times' % (cv['reversed_pct'], cv['inside_out']) if cv else 'see the report'), None),
             ('Rabbit (stage 1b): %s' % RABBIT.get(rule, 'not run, the basilica failed'), None if rule not in RABBIT else rule == 'along')]
    for k, (t, ok) in enumerate(lines):
        d.text((xs[5], y + 44 + k * 28), t, fill=(200, 205, 215) if ok is None else ((150, 215, 150) if ok else (240, 140, 130)), font=T.font(15))
    summary[rule] = dict(hair_worst=worst, bench=bench_line, cliff_1e3=cl)
for k, t in enumerate(['How the reference plane turns', 'Basilica, front (bench, rough voxels)', 'One bud close up (bench)', 'Skin between the planes: the worst close cut', 'Rabbit, front (only where allowed)', 'Numbers']):
    d.text((xs[k], 82), t, fill=(170, 175, 190), font=T.font(13))
im.save(os.path.join(HERE, 'sheet.png')); json.dump(summary, open(os.path.join(HERE, 'sheet.json'), 'w'), indent=1); print('wrote sheet.png', im.size)

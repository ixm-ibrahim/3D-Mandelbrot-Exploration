"""python out/r21/alongmem/sheets.py julia|mandel|cuts <tag> name [name ...] [steps=28] [cam=x,y,z]
Sheets drawn with the library, bench rows first (bench:along, bench:oneplane are added unless 'nobench' is given).
    julia  -> julia-<tag>.png     M.julia_sheet
    mandel -> mandel-<tag>.png    M.mandel_sheet
    cuts   -> cuts-<tag>.png      my own: cuts of the basilica and the rabbit that show rings, buds and lumps"""
import os, sys, time
import numpy as np
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import tools as T, myrules as R
M = T.M


def rule(name):
    return M.bench(name[6:]) if name.startswith('bench:') else R.get(name)


def plane_cut(r, c, o, e1, e2, L1, L2, w, h, steps):
    """A cut along the plane o + a e1 + b e2, a in -L1..L1 (to the right), b in -L2..L2 (up)."""
    a, b = np.meshgrid(np.linspace(-L1, L1, w), np.linspace(L2, -L2, h))
    Pn = [o[i] + a * e1[i] + b * e2[i] for i in range(3)]
    return M.stay(r, Pn[0], Pn[1], Pn[2], c[0], c[1], c[2], steps)


def cuts_sheet(rules, path, steps=60, w=300, h=230):
    BAS, RAB = T.BAS, T.RAB; al = T.ALPHA; s2 = np.sqrt(0.5)
    cols = [
        ('basilica: across the x-axis at x = 0', lambda r: plane_cut(r, BAS, (0, 0, 0), (0, 1, 0), (0, 0, 1), 1.0, 1.0 * h / w, w, h, steps)),
        ('basilica: along the sheet turned 22.5', lambda r: M.cut_axis(r, 22.5, w, h, steps, c=BAS, box=(-1.8, 1.8, -1.38, 1.38))),
        ('basilica: along the sheet turned 45', lambda r: M.cut_axis(r, 45.0, w, h, steps, c=BAS, box=(-1.8, 1.8, -1.38, 1.38))),
        ('rabbit: level cut at height z = 0.1', lambda r: plane_cut(r, RAB, (0, 0, 0.1), (1, 0, 0), (0, 1, 0), 1.6, 1.6 * h / w, w, h, steps)),
        ('rabbit: level cut at height z = 0.3', lambda r: plane_cut(r, RAB, (0, 0, 0.3), (1, 0, 0), (0, 1, 0), 1.6, 1.6 * h / w, w, h, steps)),
        ('rabbit: upright cut through the pinch point', lambda r: plane_cut(r, RAB, (al[0], al[1], 0), (al[0] / np.hypot(*al), al[1] / np.hypot(*al), 0), (0, 0, 1), 1.6, 1.6 * h / w, w, h, steps)),
        ('rabbit: across the x-axis at x = 0', lambda r: plane_cut(r, RAB, (0, 0, 0), (0, 1, 0), (0, 0, 1), 1.6, 1.6 * h / w, w, h, steps)),
    ]
    pad = 10; t0 = time.time(); W = pad + len(cols) * (w + pad); H = 56 + len(rules) * (h + 58)
    im = Image.new('RGB', (W, H), (12, 14, 20)); d = ImageDraw.Draw(im)
    d.text((pad, 10), 'Cuts of two Julia sets (%d steps; pale = inside)' % steps, fill=(240, 240, 245), font=M.font(22))
    for i, r in enumerate(rules):
        y = 56 + i * (h + 58); d.text((pad, y), '%s: %s' % (r.name, r.label), fill=(235, 220, 170), font=M.font(17))
        for j, (hd, fn) in enumerate(cols):
            x = pad + j * (w + pad); d.text((x, y + 24), hd, fill=(150, 160, 175), font=M.font(13))
            im.paste(Image.fromarray(M.shade(fn(r), steps)), (x, y + 44))
        print('cuts', r.name, '%.0f s' % (time.time() - t0)); sys.stdout.flush()
    im.save(path); return path


def angles_sheet(rules, path, steps=80, w=300, h=230):
    """The trap of the mirror plane: cuts of the basilica along sheets that are NOT mirror planes of along (11.25,
    22.5, 33.75 degrees), across the x-axis at three places, and a close cut of the top bud across the x-axis."""
    BAS = T.BAS
    cols = [('basilica: along the sheet turned %g' % a, (lambda a: lambda r: M.cut_axis(r, a, w, h, steps, c=BAS, box=(-1.8, 1.8, -1.38, 1.38)))(a)) for a in (11.25, 22.5, 33.75)]
    cols += [('basilica: across the x-axis at x = %g' % x0, (lambda x0: lambda r: plane_cut(r, BAS, (x0, 0, 0), (0, 1, 0), (0, 0, 1), 1.0, 1.0 * h / w, w, h, steps))(x0)) for x0 in (0.0, -0.3, -1.0)]
    cols += [('close: across at x = 0, round the top bud', lambda r: plane_cut(r, BAS, (0, 0.62, 0), (0, 0, 1), (0, 1, 0), 0.3, 0.3 * h / w, w, h, steps)),
             ('close: across at x = 0, round the bud at 45', lambda r: plane_cut(r, BAS, (0, 0.62 * np.sqrt(0.5), 0.62 * np.sqrt(0.5)), (0, -np.sqrt(0.5), np.sqrt(0.5)), (0, np.sqrt(0.5), np.sqrt(0.5)), 0.3, 0.3 * h / w, w, h, steps))]
    pad = 10; t0 = time.time(); W = pad + len(cols) * (w + pad); H = 56 + len(rules) * (h + 58)
    im = Image.new('RGB', (W, H), (12, 14, 20)); d = ImageDraw.Draw(im)
    d.text((pad, 10), 'The basilica, cut where a mirror plane cannot hide faults (%d steps; pale = inside)' % steps, fill=(240, 240, 245), font=M.font(22))
    for i, r in enumerate(rules):
        y = 56 + i * (h + 58); d.text((pad, y), '%s: %s' % (r.name, r.label), fill=(235, 220, 170), font=M.font(17))
        for j, (hd, fn) in enumerate(cols):
            x = pad + j * (w + pad); d.text((x, y + 24), hd, fill=(150, 160, 175), font=M.font(13))
            im.paste(Image.fromarray(M.shade(fn(r), steps)), (x, y + 44))
        print('angles', r.name, '%.0f s' % (time.time() - t0)); sys.stdout.flush()
    im.save(path); return path


if __name__ == '__main__':
    kind, tag = sys.argv[1], sys.argv[2]; args = sys.argv[3:]
    opt = dict(a.split('=') for a in args if '=' in a); names = [a for a in args if '=' not in a and a != 'nobench']
    if 'nobench' not in args:
        names = ['bench:along', 'bench:oneplane'] + names
    rules = [rule(n) for n in names]
    cam = tuple(float(t) for t in opt['cam'].split(',')) if 'cam' in opt else (0.45, 0.5, 1.0)
    if kind == 'julia':
        steps = int(opt.get('steps', 28))
        M.julia_sheet(rules, os.path.join(HERE, 'julia-%s.png' % tag), steps=steps, cam=cam, w=int(opt.get('w', 380)), h=int(opt.get('h', 285)), nd=int(opt.get('nd', 240)))
    elif kind == 'mandel':
        M.mandel_sheet(rules, os.path.join(HERE, 'mandel-%s.png' % tag), cam=cam, angles=(0.0, 11.25, 22.5, 45.0, 90.0), cw=260, ch=250, w=340)
    elif kind == 'cuts':
        cuts_sheet(rules, os.path.join(HERE, 'cuts-%s.png' % tag), steps=int(opt.get('steps', 60)))
    elif kind == 'angles':
        angles_sheet(rules, os.path.join(HERE, 'angles-%s.png' % tag), steps=int(opt.get('steps', 80)))
    print('done')

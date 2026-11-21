"""Pictures for the explanation.

    python out/r21/sheet/pics.py across     -> explain-across.png : cuts ACROSS the x-axis as the sheet goes from still to following
    python out/r21/sheet/pics.py film       -> explain-film.png   : which parts of the flat picture have no body (lost when lifted a millionth)
"""
import os, sys, time
import numpy as np
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import myrules as R
M = R.M


def lagrule(lam):
    return R.lam_rule('lag %.2f' % lam, '', lambda d, x, y, z, k: lam)


def across():
    s = 232; steps = 80; pad = 8; t0 = time.time()
    lags = [0.0, 0.25, 0.4, 0.6, 2 / 3., 0.75, 0.9]
    rows = [('The sheet moves the share shown toward the point before each squaring. Basilica (c = -1), cut ACROSS the x-axis at x = 0', [lagrule(l) for l in lags], (-1.0, 0.0, 0.0), 0.0, 1.0),
            ('The same rules. Mandelbrot solid, cut ACROSS the x-axis at x = -0.1226 (through the period-3 buds of the flat set, which sit at the far left and right)', [lagrule(l) for l in lags], None, -0.1226, 1.05),
            ('Other rules. Basilica, cut across at x = 0', [R.get(n) for n in ('ease', 'over', 'mirror', 'vote025', 'evsum010', 'vote4', 'along')], (-1.0, 0.0, 0.0), 0.0, 1.0),
            ('The same rules. Mandelbrot solid, cut across at x = -0.1226', [R.get(n) for n in ('ease', 'over', 'mirror', 'vote025', 'evsum010', 'vote4', 'along')], None, -0.1226, 1.05)]
    W = pad + 7 * (s + pad); H = 44 + len(rows) * (s + 50)
    im = Image.new('RGB', (W, H), (12, 14, 20)); d = ImageDraw.Draw(im)
    d.text((pad, 8), 'Buds round the x-axis: cuts across the axis (y to the right, z up), %d steps' % steps, fill=(240, 240, 245), font=M.font(19))
    for i, (head, rules, c, x0, L) in enumerate(rows):
        y = 44 + i * (s + 50); d.text((pad, y), head, fill=(235, 220, 170), font=M.font(14))
        for j, r in enumerate(rules):
            n = M.cut_across(r, x0, s, steps, c=c, L=L); x = pad + j * (s + pad)
            im.paste(Image.fromarray(M.shade(n, steps)), (x, y + 40)); d.text((x, y + 21), r.name, fill=(170, 180, 195), font=M.font(13))
        print(i, '%.0f s' % (time.time() - t0)); sys.stdout.flush()
    im.save(os.path.join(HERE, 'explain-across.png'))


def film():
    names = ['fixed', 'lag25', 'lag50', 'lag67', 'delay', 'ease', 'mirror', 'vote025', 'evsum010', 'cpull']
    w, h, steps, lift = 250, 232, 200, 1e-6; pad = 8; t0 = time.time()
    u, v = np.meshgrid(np.linspace(-2.1, 0.7, w), np.linspace(1.3, -1.3, h)); flat = M.flat_stay(u, v, u, v, steps) >= steps
    W = pad + 5 * (w + pad); H = 66 + 2 * (h + 30)
    im = Image.new('RGB', (W, H), (12, 14, 20)); d = ImageDraw.Draw(im)
    d.text((pad, 8), 'The flat Mandelbrot set, lifted a millionth off the flat page (%d steps)' % steps, fill=(240, 240, 245), font=M.font(19))
    d.text((pad, 36), 'cream: still inside (the flat picture has body there).  red: lost (there the flat picture is only a film)', fill=(200, 200, 205), font=M.font(14))
    for i, nm in enumerate(names):
        r = R.get(nm); k = M.mandel(r, u, v, np.full_like(u, lift), steps) >= steps
        img = np.zeros((h, w, 3), np.uint8); img[...] = (22, 28, 46); img[flat & k] = (238, 228, 200); img[flat & ~k] = (214, 60, 50); img[~flat & k] = (90, 200, 120)
        x = pad + (i % 5) * (w + pad); y = 66 + (i // 5) * (h + 30)
        im.paste(Image.fromarray(img), (x, y + 22)); d.text((x, y), '%s: %.1f%% lost' % (nm, 100.0 * (flat & ~k).sum() / flat.sum()), fill=(235, 220, 170), font=M.font(14))
        print(nm, '%.0f s' % (time.time() - t0)); sys.stdout.flush()
    im.save(os.path.join(HERE, 'explain-film.png'))


if __name__ == '__main__':
    {'across': across, 'film': film}[sys.argv[1]]()

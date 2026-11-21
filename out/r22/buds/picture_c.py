"""Picture for the user: buds ON a bud.   python out/r22/buds/picture_c.py -> buds-on-a-bud.png
The big bud of the middle body of the c = -1 shape, in three directions round the x-axis (flat page, slanted page,
upright page), each cut ACROSS its own stalk, 0.6641 from the x-axis (where the flat picture has the bud's two side buds)."""
import os, sys, time
import numpy as np
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import budlib as B
import pictures as P
M = B.M
C = B.BASILICA; W = 330; L = 0.15; STEPS = 60; H0 = 0.6641; pad = 14
ROWS = [('oneplane', 'Sphere inversions, one plane',
         'There is a big bud in the flat page only. It carries two small buds, both in the flat page. Nothing to see in the other two directions.'),
        ('along', 'Turning plane, along',
         'There is a big bud in all three directions, and each carries sixteen small buds, all the way round its own stalk. Only two of the sixteen lie in the page of the big bud itself; the others stick out of it to all sides: buds of 3D. Some are round, some are thin.'),
        ('once', 'Along once, then one plane',
         'The big bud is there in all three directions, because one step carries it to the x-axis. But each carries only two small buds: small buds need a second step, and that one is squared about the flat page.'),
        ('pulled', 'Pulled plane',
         'A big bud in the flat page and in the upright page, none in the slanted page. Each carries two small buds, in its own page; the upright one also has thin loose flakes.')]
COLS = [(0.0, 'The big bud in the flat page'), (45.0, 'The big bud in the slanted page'), (90.0, 'The big bud in the upright page')]


def main():
    t0 = time.time(); f_t, f_h, f_c, f_s = M.font(30), M.font(21), M.font(17), M.font(15)
    SW, SH = 400, W
    Wd = pad + SW + pad + len(COLS) * (W + pad)
    im = Image.new('RGB', (Wd, 4000), P.BG); d = ImageDraw.Draw(im)
    d.text((pad, 14), 'Buds on a bud', fill=P.INK, font=f_t)
    intro = ['The middle body of the c = -1 shape has a big bud on top. Is that bud a body of its own, with small buds all round it?',
             'Left: the middle body. Then the big bud in three directions round the x-axis, each cut straight across its own stalk and enlarged:',
             'the big pale disc is the bud itself, the small pale spots round it are the buds it carries. Left-right in these cuts is along the x-axis.']
    y = 58
    for s in intro:
        d.text((pad, y), s, fill=P.GREY, font=f_c); y += 24
    y += 14
    u, v = np.meshgrid(np.linspace(-L, L, W), np.linspace(L, -L, W))
    for name, head, cap in ROWS:
        r = B.RULES[name]
        d.text((pad, y), head, fill=P.GOLD, font=f_h); y += 30
        d.text((pad, y), 'The middle body this rule makes (rough blocks)', fill=P.DIM, font=f_s)
        for j, (a, s) in enumerate(COLS):
            d.text((pad + SW + pad + j * (W + pad), y), s, fill=P.DIM, font=f_s)
        y += 22
        im.paste(P.solid(r, (0.0, 0.0, 0.0), 0.95, SW, SH), (pad, y))
        for j, (a, s) in enumerate(COLS):
            ar = np.radians(a); er = (0, np.cos(ar), np.sin(ar)); ep = (0, -np.sin(ar), np.cos(ar))
            Q = [H0 * er[k] + u * (1 if k == 0 else 0) + v * ep[k] for k in range(3)]
            n = M.stay(r, Q[0], Q[1], Q[2], *C, STEPS); x = pad + SW + pad + j * (W + pad)
            im.paste(Image.fromarray(M.shade(n, STEPS)), (x, y))
            if not (n >= STEPS).any():
                d.text((x + W // 2 - 62, y + W // 2 - 10), 'no bud here', fill=P.DIM, font=f_c)
            print(name, a, 'inside %.1f%% of the cut' % (100 * (n >= STEPS).mean()), '%.0f s' % (time.time() - t0)); sys.stdout.flush()
        y += W + 8
        for ln in P.wrap(d, cap, f_c, Wd - 2 * pad):
            d.text((pad, y), ln, fill=P.TXT, font=f_c); y += 23
        y += 30
    im = im.crop((0, 0, Wd, y)); out = os.path.join(HERE, 'buds-on-a-bud.png'); im.save(out); print(out, im.size)


if __name__ == '__main__':
    main()

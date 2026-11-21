"""Judge: the three pictures for the user, put together from my own solids (cache/depth-*.npz) and my own flat cuts.

    python jcompose.py 1     1-how-close.png        the balls object against the true flat picture of c = -1
    python jcompose.py 2     2-carried-over.png     the bulbs carried onto the true flat picture (c = -1 and the rabbit)
    python jcompose.py 3     3-pinched.png          kisses swapped for pinches (c = -1 and the rabbit)
"""
import os, sys
import numpy as np
from PIL import Image, ImageDraw
import jlib as J

BG = (12, 14, 20); DARK = (14, 17, 26); CREAM = (232, 224, 200); LAB = (176, 184, 198); CAP = (236, 236, 240)
TW, TH = 620, 465; PAD = 12


def solid_tile(tag, crop=1.0):
    """crop < 1: only the middle part of the kept solid is shown (the same shape, closer)."""
    d = np.load(os.path.join(J.HERE, 'cache', 'depth-%s.npz' % tag)); im = Image.fromarray(J.shade(d['depth'], float(d['px'])))
    if crop < 1.0:
        w, h = im.size; cw, ch = int(w * crop), int(h * crop); im = im.crop(((w - cw) // 2, (h - ch) // 2, (w - cw) // 2 + cw, (h - ch) // 2 + ch))
    return im.resize((TW, TH), Image.LANCZOS)


def tag_box(d, xy, text):
    x, y = xy; f = J.font(16); w = d.textlength(text, font=f)
    d.rectangle((x - 5, y - 2, x + w + 5, y + 22), fill=(12, 14, 20)); d.text((x, y), text, fill=CAP, font=f)


def flat_tile(fn, w, h, box, ss=3):
    """A filled flat picture: fn(x, y) -> bool, drawn with ss x ss samples a pixel."""
    xs = np.linspace(box[0], box[1], w * ss); ys = np.linspace(box[3], box[2], h * ss); gx, gy = np.meshgrid(xs, ys)
    a = fn(gx, gy).astype(float).reshape(h, ss, w, ss).mean((1, 3))
    img = (np.array(DARK)[None, None] * (1 - a[..., None]) + np.array(CREAM)[None, None] * a[..., None]).astype(np.uint8)
    return Image.fromarray(img)


def overlay_tile(fa, ft, w, h, box, ss=3):
    xs = np.linspace(box[0], box[1], w * ss); ys = np.linspace(box[3], box[2], h * ss); gx, gy = np.meshgrid(xs, ys)
    A = fa(gx, gy); T = ft(gx, gy); ov = J.overlay(A, T); ov[~A & ~T] = DARK; big = ov.astype(float).reshape(h, ss, w, ss, 3).mean((1, 3))
    return Image.fromarray(big.astype(np.uint8)), J.wrong_share(A, T)


def sheet(path, rows, caption, labels):
    """rows: list of lists of PIL tiles (all TW wide); labels: same shape, one short label a tile; caption: 1 or 2 lines."""
    ncol = max(len(r) for r in rows); W = PAD + ncol * (TW + PAD); H = PAD + sum(r[0].size[1] + 26 + PAD for r in rows) + 30 * len(caption) + 14
    im = Image.new('RGB', (W, H), BG); d = ImageDraw.Draw(im); y = PAD
    for r, ls in zip(rows, labels):
        for k, (t, lab) in enumerate(zip(r, ls)):
            x = PAD + k * (TW + PAD); d.text((x + 2, y), lab, fill=LAB, font=J.font(16)); im.paste(t, (x, y + 24))
        y += r[0].size[1] + 26 + PAD
    for k, line in enumerate(caption):
        d.text((PAD + 2, y + 2 + 30 * k), line, fill=CAP, font=J.font(21))
    im.save(path); print('wrote', path, im.size)


def pic1():
    FH = 448; box = J.BOX

    def ball(x, y):
        return J.balls(x, y, 0 * x, grid='line', rounds=40) == 1

    def true(x, y):
        return J.truth(x, y, -1.0, 300)
    a1 = flat_tile(true, TW, FH, box); a2 = flat_tile(ball, TW, FH, box); a3, ws = overlay_tile(ball, true, TW, FH, box)
    print('picture 1: wrong share on its own grid %.1f of 100' % (100 * ws))
    # close-ups of the meeting point of the middle body with its left neighbour, 10 times closer
    cw = (TW - PAD) // 2; hw = 0.05; hh = hw * TH / cw
    al = (1 - np.sqrt(5)) / 2
    c1 = flat_tile(lambda x, y: J.truth(x, y, -1.0, 600), cw, TH, (al - hw, al + hw, -hh, hh))
    c2 = flat_tile(lambda x, y: J.balls(x, y, 0 * x, grid='line', rounds=60) == 1, cw, TH, (-0.525 - hw, -0.525 + hw, -hh, hh))
    cl = Image.new('RGB', (TW, TH), BG); cl.paste(c1, (0, 0)); cl.paste(c2, (cw + PAD, 0))
    dd = ImageDraw.Draw(cl); tag_box(dd, (cw // 2 - 62, TH - 34), 'the true picture: a pinch'.replace('the true picture', 'true')); tag_box(dd, (cw + PAD + cw // 2 - 46, TH - 34), 'balls: a kiss')
    rows = [[a1, a2, a3], [solid_tile('balls-front', 0.8), solid_tile('balls-above', 0.8), cl]]
    labels = [['The true flat picture of c = -1', 'Balls on balls: its flat cut', 'One on the other.  Cream: both.  Blue: only the true picture.  Orange: only the balls.'],
              ['Balls on balls, from the front', 'The same, from above', 'Where the middle body meets its neighbour, ten times closer']]
    sheet(os.path.join(J.HERE, '1-how-close.png'), rows,
          ['The same layout, but round balls where the true bodies are pointed: about 39 of every 100 parts of the true area come out wrong.',
           'Where two true bodies pinch, two balls only kiss.'], labels)


def pic2():
    rows = [[solid_tile('carry-c1-front'), solid_tile('carry-c1-above')], [solid_tile('carry-rabbit-front'), solid_tile('carry-rabbit-above')]]
    labels = [['c = -1, from the front', 'c = -1, from above'], ['The rabbit, from the front', 'The rabbit, from above']]
    sheet(os.path.join(J.HERE, '2-carried-over.png'), rows,
          ['The bulbs of Balls on balls carried onto the true flat picture: the flat cut is now exact.',
           'But needles and upright walls grow wherever bodies meet, and the rabbit is worst.'], labels)


def pic3():
    rows = [[solid_tile('lemon-c1-front'), solid_tile('lemon-c1-above')], [solid_tile('lemon-rabbit-front'), solid_tile('lemon-rabbit-above')]]
    labels = [['c = -1, from the front', 'c = -1, from above'], ['The rabbit, from the front', 'The rabbit, from above']]
    sheet(os.path.join(J.HERE, '3-pinched.png'), rows,
          ['Kisses swapped for pinches: every body becomes a lemon, and the flat cut is near, not exact.',
           'The buds then sit only round the flat picture; none come all over.'], labels)


if __name__ == '__main__':
    for a in sys.argv[1:] or ['1', '2', '3']:
        {'1': pic1, '2': pic2, '3': pic3}[a]()

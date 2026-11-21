"""One step of each rule, shown on a ring of test points round the basilica's middle body.
    python out/r22/me/ring.py   -> out/r22/me/one-step-ring.png

A point is in the shape only if the point it jumps to is in the shape. So: put test points on a circle round the
x-axis at x = 0 (radius 0.62, through the middle of the buds), take ONE step (square, add c = -1), and look where
they land. Left: before, over the cut across x = 0. Middle: after, over the cut across the left-hand body near
where they land. Right: the rough solid of the middle body."""
import os, sys, time, colorsys
import numpy as np
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, 'out', 'r21', 'lib'))
import mem as M

C = (-1.0, 0.0, 0.0); RHO = 0.62; N = 48; STEPS = 80
ROWS = [('lathe', 'Quaternion square (Lathe): every point is squared in the page it lies in',
         'All the test points jump to one and the same spot, inside the left-hand body. So the whole ring is inside: the bud is a ring.'),
        ('oneplane', 'Sphere inversions, one plane: every point is squared about the flat page',
         'The test points jump to a tall line. Only the ones that started beside the flat page land inside. Two buds; smooth everywhere else.'),
        ('along', 'Turning plane, along: flat page or upright page, whichever is nearer',
         'The test points jump to a small cluster. Eight of them land dead centre, inside. Eight buds, one for each direction where a point lies in its own page.')]
PW = 380; SW, SH = 500, 380; LA, LB = 0.95, 0.5; pad = 14


def hue(i):
    r, g, b = colorsys.hsv_to_rgb(i / N, 0.85, 1.0); return int(255 * r), int(255 * g), int(255 * b)


def to_px(y, z, L, w):
    return (y + L) / (2 * L) * (w - 1), (L - z) / (2 * L) * (w - 1)


def dots(d, ox, oy, ys, zs, inside, L, w):
    for i in np.argsort(inside):                               # the ones that stay are drawn last, on top
        px, py = to_px(ys[i], zs[i], L, w)
        if not (0 <= px < w and 0 <= py < w):
            continue
        if inside[i]:
            d.ellipse([ox + px - 8, oy + py - 8, ox + px + 8, oy + py + 8], fill=hue(i), outline=(255, 255, 255), width=2)
        else:
            d.ellipse([ox + px - 4, oy + py - 4, ox + px + 4, oy + py + 4], fill=hue(i), outline=(0, 0, 0), width=1)


def main():
    t0 = time.time(); f_t, f_h, f_c, f_s = M.font(30), M.font(21), M.font(17), M.font(15)
    W = pad + PW + pad + PW + pad + SW + pad; rowh = 30 + 22 + PW + 8 + 26 + 30
    H = 150 + len(ROWS) * rowh + 20
    im = Image.new('RGB', (W, H), (12, 14, 20)); d = ImageDraw.Draw(im)
    d.text((pad, 14), 'What one step does to the points round a body', fill=(240, 240, 245), font=f_t)
    d.text((pad, 58), 'A point belongs to the shape only if the place it jumps to next belongs too. So: a ring of test points round the middle body of the', fill=(170, 178, 192), font=f_c)
    d.text((pad, 82), 'c = -1 shape, one step taken. Same colour = same point, before and after. Big dot with a white rim = it stays in the shape. Small dot = it flies away.', fill=(170, 178, 192), font=f_c)
    d.text((pad, 106), 'The first two pictures in each row look along the x-axis: the flat page is the level line through the middle. The third shows the shape from the side.', fill=(170, 178, 192), font=f_c)
    phi = np.arange(N) * 2 * np.pi / N
    x0, y0, z0 = np.zeros(N), RHO * np.cos(phi), RHO * np.sin(phi)
    cx, cy, cz = (np.full(N, t) for t in C)
    y = 150
    for name, head, cap in ROWS:
        r = M.bench(name)
        inside = M.stay(r, x0, y0, z0, *C, STEPS) >= STEPS
        X, Y, Z, _ = r.step(x0.copy(), y0.copy(), z0.copy(), tuple(r.init(N)), 0, cx, cy, cz)
        X, Y, Z = X + C[0], Y + C[1], Z + C[2]
        xm = C[0] - RHO * RHO                                  # where a point squared in its own page lands
        print(name, 'stay %d of %d' % (inside.sum(), N), 'land x %.3f..%.3f' % (X.min(), X.max()), 'off-axis max %.3f' % np.hypot(Y, Z).max(), '%.0f s' % (time.time() - t0)); sys.stdout.flush()
        d.text((pad, y), head, fill=(240, 222, 160), font=f_h); y += 30
        xs = [pad, pad + PW + pad, pad + 2 * (PW + pad)]
        d.text((xs[0], y), 'Before: test points round the middle body', fill=(150, 160, 175), font=f_s)
        d.text((xs[1], y), 'After one step: where they landed (enlarged)', fill=(150, 160, 175), font=f_s)
        d.text((xs[2], y), 'The shape this rule makes (middle body, rough blocks)', fill=(150, 160, 175), font=f_s); y += 22
        A = M.shade(M.cut_across(r, 0.0, PW, 60, c=C, L=LA), 60); im.paste(Image.fromarray(A), (xs[0], y))
        B = M.shade(M.cut_across(r, xm, PW, 60, c=C, L=LB), 60); im.paste(Image.fromarray(B), (xs[1], y))
        for xx in xs[:2]:
            d.line([xx, y + PW // 2, xx + 26, y + PW // 2], fill=(150, 160, 175), width=1); d.line([xx + PW - 26, y + PW // 2, xx + PW, y + PW // 2], fill=(150, 160, 175), width=1)
        d.text((xs[0] + 6, y + PW - 24), 'level line = the flat page, seen edge-on', fill=(150, 160, 175), font=f_s)
        d.text((xs[1] + 6, y + PW - 24), 'pale = the left-hand body, cut where the centre dot lands', fill=(150, 160, 175), font=f_s)
        dots(d, xs[0], y, y0, z0, inside, LA, PW); dots(d, xs[1], y, Y, Z, inside, LB, PW)
        dep, px = M.solid(r, C, SW, SH, 300, 40, centre=(0.0, 0.0, 0.0), half_w=0.95, cam=(0.75, 0.45, 1.0))
        im.paste(Image.fromarray(M.shade_solid(dep, px)), (xs[2], y)); y += PW + 8
        d.text((pad, y), cap, fill=(215, 218, 226), font=f_c); y += 26 + 30
        print(name, 'drawn', '%.0f s' % (time.time() - t0)); sys.stdout.flush()
    im = im.crop((0, 0, W, y)); out = os.path.join(HERE, 'one-step-ring.png'); im.save(out); print(out, im.size)


if __name__ == '__main__':
    main()

"""The two pictures for the user.   python out/r22/mandel/pictures.py [1|2]
    1 -> out/r22/mandel/c-swung-out.png     c swung out of the flat page: which c stay, and the orbit of two of them
    2 -> out/r22/mandel/bud-from-above.png  the bud on top of each solid, cut level through its middle: is it a ball?
Everything is made point by point with the library's rules (out/r21/lib/mem.py), no renderer.
"""
import os, sys, time
import numpy as np
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import mlib as L
M = L.M

C3 = (-0.122561, 0.744862)                      # middle of the bud on top of the flat Mandelbrot set
SPOTS = (0.744862, 0.562, 0.0)                  # how far the three spots of the flat hop are from the x-axis
ROWS = [('lathe', 'Quaternion square (Lathe): every point is squared in the page it lies in',
         'The orbit never leaves the page c lies in, and does there exactly what it does in the flat picture. Every position stays: the bud runs right round as a ring.'),
        ('oneplane', 'Sphere inversions, one plane: every point is squared about the flat page',
         'A c lifted a little off the flat page lifts its orbit more at every step, until the orbit is thrown out. Only two thin slices stay: the bud is a blade, the solid a flat cushion.'),
        ('wake', 'Along once, then one plane: first step as "along", every later step about the flat page',
         'Only the first step differs from the row above, and it does not help: every later step is one plane\'s, with the same lifted c added again. The same positions stay.'),
        ('evc', 'Pulled plane: c and the orbit pull the plane toward the page they lie in',
         'A c standing upright gets the plane at once: the flat picture is there a second time, upright. A c in between gets it only part of the way, and is thrown out before it arrives.'),
        ('along', 'Turning plane, along: flat, upright or one of the two slanted pages, whichever is nearer',
         'The plane swings after a point that strays, so straying is hardly punished. Four patches stay, each nearly twice as wide as a round bud (plus four thin slices), with ragged rims: the rock.')]
BG = (12, 14, 20); GREY = (150, 160, 175); pad = 14


def to_px(y, z, Lw, w):
    return (y + Lw) / (2 * Lw) * (w - 1), (Lw - z) / (2 * Lw) * (w - 1)


def dashed(d, p0, p1, fill, width=1, on=7, off=6):
    p0, p1 = np.array(p0, float), np.array(p1, float); n = np.linalg.norm(p1 - p0)
    if n < 1:
        return
    u = (p1 - p0) / n; t = 0.0
    while t < n:
        a, b = p0 + u * t, p0 + u * min(t + on, n); d.line([a[0], a[1], b[0], b[1]], fill=fill, width=width); t += on + off


def dashed_circle(d, cx, cy, r, fill, width=2, n=40):
    for i in range(0, n, 2):
        a0, a1 = 360.0 * i / n, 360.0 * (i + 1) / n; d.arc([cx - r, cy - r, cx + r, cy + r], a0, a1, fill=fill, width=width)


def heat(t):
    """Early steps pale yellow, late steps red."""
    t = float(np.clip(t, 0, 1)); return (255, int(235 - 150 * t), int(150 - 120 * t))


def trail_panel(im_all, d_all, ox_all, oy_all, key, deg, PW, Lw, f_s, f_b, nshow=45):
    """The orbit of one c (the bud's middle swung deg out of the flat page), seen along the x-axis.
    Drawn on its own tile, so that the line of an orbit that flies away is cut off at the tile's edge."""
    im = Image.new('RGB', (PW, PW), (24, 30, 52)); d = ImageDraw.Draw(im); ox = oy = 0
    a = np.radians(deg); c = (C3[0], C3[1] * np.cos(a), C3[1] * np.sin(a))
    pts, page, ns = L.trace(key, *c, 300)
    mid = PW // 2
    d.line([ox, oy + mid, ox + PW - 1, oy + mid], fill=(110, 120, 140), width=1)                                  # the flat page
    e = np.array([np.cos(a), -np.sin(a)]) * (PW / 2 - 4)
    dashed(d, (ox + mid - e[0], oy + mid - e[1]), (ox + mid + e[0], oy + mid + e[1]), (225, 225, 235), 1)         # c's own page
    for rr in SPOTS:                                                                                              # where the flat hop would stand in c's page
        px, py = to_px(rr * np.cos(a), rr * np.sin(a), Lw, PW); d.ellipse([ox + px - 11, oy + py - 11, ox + px + 11, oy + py + 11], outline=(225, 225, 235), width=1)
    n = min(nshow, int(ns[0]) + 1); P = pts[:n + 1, 0]
    xy = [to_px(P[i, 1], P[i, 2], Lw, PW) for i in range(len(P)) if np.isfinite(P[i, 1])]
    for i in range(len(xy) - 1):
        d.line([ox + xy[i][0], oy + xy[i][1], ox + xy[i + 1][0], oy + xy[i + 1][1]], fill=(150, 138, 110), width=1)
    for i, (px, py) in enumerate(xy):
        if 0 <= px < PW and 0 <= py < PW:
            r = 7 if i == 0 else 5
            d.ellipse([ox + px - r, oy + py - r, ox + px + r, oy + py + r], fill=heat(i / max(nshow - 1, 1)), outline=(0, 0, 0), width=1)
    px, py = xy[0]; d.text((ox + min(px + 10, PW - 20), oy + py - 22), 'c', fill=(255, 255, 255), font=f_b)
    stays = bool(ns[0] >= 300)
    if stays:
        last = pts[-13:-1, 0]
        for q in last:                                                                                            # where it has settled
            px, py = to_px(q[1], q[2], Lw, PW); d.ellipse([ox + px - 8, oy + py - 8, ox + px + 8, oy + py + 8], outline=(255, 255, 255), width=2)
        txt = 'STAYS: hops round three spots for ever' if len(set(np.round(last[:, 0], 5))) <= 3 else 'STAYS'
        d.rectangle([0, PW - 34, PW - 1, PW - 1], fill=(24, 30, 52)); d.text((ox + 8, oy + PW - 30), txt, fill=(170, 235, 170), font=f_b)
    else:
        d.rectangle([0, PW - 34, PW - 1, PW - 1], fill=(24, 30, 52)); d.text((ox + 8, oy + PW - 30), 'THROWN OUT after %d steps' % ns[0], fill=(255, 150, 130), font=f_b)
    im_all.paste(im, (ox_all, oy_all))
    return stays, int(ns[0])


def picture1():
    t0 = time.time(); f_t, f_h, f_c, f_s, f_b = M.font(30), M.font(21), M.font(17), M.font(15), M.font(17)
    PW = 330; SW, SH = 420, 330; Lw = 1.0; N = 72
    W = pad + 3 * (PW + pad) + SW + pad; rowh = 30 + 22 + PW + 8 + 26 + 30
    im = Image.new('RGB', (W, 300 + len(ROWS) * rowh + 60), BG); d = ImageDraw.Draw(im)
    d.text((pad, 14), 'The Mandelbrot solid: what happens to a c that is swung out of the flat page', fill=(240, 240, 245), font=f_t)
    intro = ['A c belongs to the Mandelbrot solid if its orbit (start at c, then square and add c, again and again) never flies away. In the flat picture the bud on top',
             'is made of the c whose orbit ends up hopping round three spots for ever. Here the middle of that bud is swung round the x-axis, like a point on a',
             'page of a book that is being turned, and each rule is asked: does the orbit still stay?',
             'All pictures but the last in a row look along the x-axis (along the spine of the book). Level line = the flat page, seen edge-on.',
             'First picture: 72 positions of c. Big dot with a white rim = the orbit stays. Small dot = it flies away. Pale shape = the solid, cut across at this place.',
             'Second and third: the orbit of ONE c, step by step (pale yellow first, red last). Dashed line = the page c lies in; thin rings = where the three spots would be in that page;',
             'thick white rings = the spots the orbit has settled on, if it stays.']
    for i, s in enumerate(intro):
        d.text((pad, 58 + 24 * i), s, fill=(170, 178, 192), font=f_c)
    y = 58 + 24 * len(intro) + 18
    phi = np.arange(N) * 2 * np.pi / N; cx, cy, cz = np.full(N, C3[0]), C3[1] * np.cos(phi), C3[1] * np.sin(phi)
    for key, head, cap in ROWS:
        r = L.RULES[key]
        d.text((pad, y), head, fill=(240, 222, 160), font=f_h); y += 30
        xs = [pad + i * (PW + pad) for i in range(3)] + [pad + 3 * (PW + pad)]
        for xx, s in zip(xs, ['c swung right round: which positions stay?', 'Orbit of the c swung a little (8 degrees)',
                              'Orbit of the c swung upright', 'The Mandelbrot solid this rule makes (rough blocks)']):
            d.text((xx, y), s, fill=GREY, font=f_s)
        y += 22
        A = M.shade(M.cut_across(r, C3[0], PW, 100, c=None, L=Lw), 100); im.paste(Image.fromarray(A), (xs[0], y))
        d.line([xs[0], y + PW // 2, xs[0] + 22, y + PW // 2], fill=GREY, width=1); d.line([xs[0] + PW - 22, y + PW // 2, xs[0] + PW, y + PW // 2], fill=GREY, width=1)
        ins = M.mandel(r, cx, cy, cz, 300) >= 300
        for i in np.argsort(ins):
            px, py = to_px(cy[i], cz[i], Lw, PW)
            if ins[i]:
                d.ellipse([xs[0] + px - 7, y + py - 7, xs[0] + px + 7, y + py + 7], fill=(255, 190, 60), outline=(255, 255, 255), width=2)
            else:
                d.ellipse([xs[0] + px - 3, y + py - 3, xs[0] + px + 3, y + py + 3], fill=(120, 170, 255), outline=(0, 0, 0), width=1)
        d.text((xs[0] + 6, y + PW - 24), '%d of %d positions stay' % (ins.sum(), N), fill=(215, 218, 226), font=f_s)
        s8 = trail_panel(im, d, xs[1], y, key, 8, PW, Lw, f_s, f_b); s90 = trail_panel(im, d, xs[2], y, key, 90, PW, Lw, f_s, f_b)
        dep, px = M.solid(r, None, SW, SH, 260, 40, cam=(0.45, 0.5, 1.0)); im.paste(Image.fromarray(M.shade_solid(dep, px)), (xs[3], y)); y += PW + 8
        d.text((pad, y), cap, fill=(215, 218, 226), font=f_c); y += 26 + 30
        print(key, 'stay %d of %d' % (ins.sum(), N), '8 deg:', s8, '90 deg:', s90, '%.0f s' % (time.time() - t0)); sys.stdout.flush()
    im = im.crop((0, 0, W, y)); out = os.path.join(HERE, 'c-swung-out.png'); im.save(out); print(out, im.size)


FOOT = [('lathe', 'Quaternion square (Lathe)', 'A ring: sideways it never ends.'),
        ('oneplane', 'Sphere inversions, one plane', 'A blade: a fifth as thick as a ball.'),
        ('wake', 'Along once, then one plane', 'The same blade.'),
        ('evc', 'Pulled plane', 'A lens: 0.6 as thick as a ball.'),
        ('along', 'Turning plane, along', 'A ragged bun, 1.8 times as wide.')]


def picture2():
    t0 = time.time(); f_t, f_h, f_c, f_s = M.font(30), M.font(19), M.font(17), M.font(15)
    PW = 300; Lw = 0.34; R = 0.0947
    W = pad + len(FOOT) * (PW + pad); H = 215 + 2 * (PW + 60) + 110
    im = Image.new('RGB', (W, H), BG); d = ImageDraw.Draw(im)
    d.text((pad, 14), 'Is the bud a ball? The bud on top of each Mandelbrot solid, close up', fill=(240, 240, 245), font=f_t)
    intro = ['In the flat picture this bud is nearly a round disc. A bud "of 3D in its own right" would be a ball of the same size: as you move c away from the bud\'s middle,',
             'its orbit would have to stop hopping round the three spots equally soon in every direction, also sideways, out of the flat page.',
             'Top row: the bud cut level through its middle and seen from straight above (the flat page is the level line; up and down in these pictures is OUT of the flat page).',
             'Dashed circle = what a ball would show. Bottom row: the same bud as a solid (rough blocks), standing on the big body, seen looking along the x-axis and a little from above:',
             'the flat page runs away from you, so a bud that is thin sideways looks thin.']
    for i, s in enumerate(intro):
        d.text((pad, 58 + 24 * i), s, fill=(170, 178, 192), font=f_c)
    y0 = 58 + 24 * len(intro) + 16
    u, s = np.meshgrid(np.linspace(C3[0] - Lw, C3[0] + Lw, PW), np.linspace(Lw, -Lw, PW))
    for j, (key, name, verdict) in enumerate(FOOT):
        r = L.RULES[key]; x = pad + j * (PW + pad); y = y0
        d.text((x, y), name, fill=(240, 222, 160), font=f_h); y += 28
        n = M.mandel(r, u, np.full_like(u, C3[1]), s, 300); im.paste(Image.fromarray(M.shade(n, 300)), (x, y))
        d.line([x, y + PW // 2, x + 18, y + PW // 2], fill=GREY, width=1); d.line([x + PW - 18, y + PW // 2, x + PW, y + PW // 2], fill=GREY, width=1)
        dashed_circle(d, x + PW / 2, y + PW / 2, R / (2 * Lw) * (PW - 1), (255, 190, 60), 2)
        y += PW + 6; d.text((x, y), verdict, fill=(215, 218, 226), font=f_c); y += 30
        dep, px = M.solid(r, None, 200, 200, 130, 50, centre=(C3[0], 0.74, 0.0), half_w=0.27, cam=(1.0, 0.42, 0.22))
        im.paste(Image.fromarray(M.shade_solid(dep, px)).resize((PW, PW), Image.LANCZOS), (x, y))
        print(key, 'inside the level cut: %d places' % int((n >= 300).sum()), '%.0f s' % (time.time() - t0)); sys.stdout.flush()
    y += PW + 10
    for s in ['What the orbit of c does when c is moved sideways out of the bud: under the Lathe nothing changes (so the bud never ends: a ring); under one plane it is thrown out five times',
              'sooner than within the page (a blade); under the pulled plane somewhat sooner (a lens); under "along" later, and raggedly (a wide bun). No rule here lets go of the orbit',
              'equally soon in every direction. And each rule only has such a bud where c lies in a page that the rule squares in: one page, two pages, four pages, or all of them.']:
        d.text((pad, y), s, fill=(215, 218, 226), font=f_c); y += 24
    im = im.crop((0, 0, W, y + 12)); out = os.path.join(HERE, 'bud-from-above.png'); im.save(out); print(out, im.size)


if __name__ == '__main__':
    which = sys.argv[1] if len(sys.argv) > 1 else '12'
    if '1' in which:
        picture1()
    if '2' in which:
        picture2()

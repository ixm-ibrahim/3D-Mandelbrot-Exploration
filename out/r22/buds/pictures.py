"""The two pictures for the user.   python out/r22/buds/pictures.py [a|b] [quick]
   a -> bud-two-steps.png      a ring of test points round the LEFT-hand body of the c = -1 shape, followed for two steps
   b -> ball-rib-ring.png      which page each test point is squared in, and the bud shape that follows
Orbits are the library's (out/r21/lib/mem.py); pages come from budlib.page_used (checked against the library's step)."""
import os, sys, time, colorsys
import numpy as np
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import budlib as B
M = B.M
C = B.BASILICA; N = 96; STEPS = 80
QUICK = 'quick' in sys.argv
BG = (12, 14, 20); INK = (240, 240, 245); GREY = (170, 178, 192); DIM = (150, 160, 175); GOLD = (240, 222, 160); TXT = (215, 218, 226)


def hue(i, n=N):
    r, g, b = colorsys.hsv_to_rgb((i / n) % 1.0, 0.85, 1.0); return int(255 * r), int(255 * g), int(255 * b)


def to_px(y, z, L, w):
    return (y + L) / (2 * L) * (w - 1), (L - z) / (2 * L) * (w - 1)


def dots(d, ox, oy, ys, zs, inside, L, w, big=8, small=4, mono=False):
    for i in np.argsort(inside, kind='stable'):                 # the ones that stay are drawn last, on top
        if not (np.isfinite(ys[i]) and np.isfinite(zs[i])):
            continue
        px, py = to_px(ys[i], zs[i], L, w)
        if not (0 <= px < w and 0 <= py < w):
            continue
        if inside[i]:
            d.ellipse([ox + px - big, oy + py - big, ox + px + big, oy + py + big], fill=(255, 190, 60) if mono else hue(i), outline=(255, 255, 255), width=2)
        else:
            d.ellipse([ox + px - small, oy + py - small, ox + px + small, oy + py + small], fill=(120, 130, 150) if mono else hue(i), outline=(0, 0, 0), width=1)


def level(d, xx, y, w):
    d.line([xx, y + w // 2, xx + 26, y + w // 2], fill=DIM, width=1); d.line([xx + w - 26, y + w // 2, xx + w, y + w // 2], fill=DIM, width=1)


def cut(rule, x0, w, L):
    st = 30 if QUICK else 60
    return Image.fromarray(M.shade(M.cut_across(rule, x0, w, st, c=C, L=L), st))


def solid(rule, centre, half_w, w, h):
    dep, px = M.solid(rule, C, w, h, 60 if QUICK else 240, 20 if QUICK else 40, centre=centre, half_w=half_w, cam=(0.75, 0.45, 1.0))
    return Image.fromarray(M.shade_solid(dep, px))


def wrap(d, text, font, width):
    words = text.split(); lines = []; cur = ''
    for w in words:
        t = (cur + ' ' + w).strip()
        if d.textlength(t, font=font) <= width:
            cur = t
        else:
            lines.append(cur); cur = w
    lines.append(cur); return lines


# ============================================================================================ picture a
def picture_a():
    t0 = time.time(); f_t, f_h, f_c, f_s = M.font(30), M.font(21), M.font(17), M.font(15)
    fc = B.flat_centres(C[0]); x0, rad = fc['g2'].real, abs(fc['g2'].imag); xs_small = fc['small']
    PW = 150 if QUICK else 360; SW, SH = (160, 150) if QUICK else (440, 360); pad = 14
    L1, L2, L3 = 0.5, 0.95, 0.45
    ROWS = [('oneplane', None, 'Sphere inversions, one plane: every step is squared about the flat page',
             'Only the points beside the flat page are still beside it after the first jump, and land in the small body after the second. Two buds on the left-hand body.'),
            ('along', None, 'Turning plane, along: each point is squared about a page that turns with it and meets it at the flat, the upright and the two slanted pages',
             'A point that lies in one of those four pages stays in it at every step, so it lands dead centre: eight buds. Eight more start between the pages and are thrown beside the flat or the upright page by the first jump: sixteen buds.'),
            ('once', 'oneplane', 'Along once, then one plane: the first step is squared as in the row above, every later step about the flat page',
             'The first jump is the same as in the row above. The second is squared about the flat page, so only the points that the first jump put beside the flat page come through: six buds, all near the flat page. The upright and slanted buds are lost.')]
    W = pad + 3 * (PW + pad) + SW + pad
    im = Image.new('RGB', (W, 4000), BG); d = ImageDraw.Draw(im)
    d.text((pad, 14), 'Following the points of a bud for two steps', fill=INK, font=f_t)
    intro = ['A bud is a place whose points are carried, in a few jumps, into a bigger body. Here: a ring of test points round the LEFT-hand body of the c = -1 shape.',
             'From there it takes two jumps to reach the x-axis. Same colour = same point in all three pictures. Big dot with a white rim = it stays in the shape. Small dot = it flies away.',
             'The first three pictures in each row look along the x-axis (the x-axis is the centre; the flat page is the level line). The fourth shows the left-hand body from the side.']
    y = 58
    for s in intro:
        d.text((pad, y), s, fill=GREY, font=f_c); y += 24
    y += 14
    phi = np.arange(N) * 2 * np.pi / N; xx0 = np.full(N, x0); y0, z0 = rad * np.cos(phi), rad * np.sin(phi)
    for name, later, head, cap in ROWS:
        r = B.RULES[name]; rl = B.RULES[later] if later else r
        ins = B.inside(name, xx0, y0, z0, C, STEPS); t = B.trace(name, xx0, y0, z0, C, 2)
        p1, p2 = t['pos'][1], t['pos'][2]
        print(name, 'stay %d of %d' % (ins.sum(), N), '| after 1 jump: x %.3f..%.3f (those that stay %.3f..%.3f)' % (np.nanmin(p1[0]), np.nanmax(p1[0]), p1[0][ins].min(), p1[0][ins].max()),
              '| after 2 jumps: x %.3f..%.3f (those that stay %.3f..%.3f), off-axis of those that stay up to %.3f'
              % (np.nanmin(p2[0]), np.nanmax(p2[0]), p2[0][ins].min(), p2[0][ins].max(), np.hypot(p2[1], p2[2])[ins].max()), '%.0f s' % (time.time() - t0)); sys.stdout.flush()
        d.text((pad, y), head, fill=GOLD, font=f_h); y += 30
        xs = [pad + i * (PW + pad) for i in range(4)]
        for xx, s in zip(xs, ('Before: test points round the left-hand body', 'After one jump: round the middle body', 'After two jumps: at the small body (enlarged)', 'The left-hand body (at the right edge: the middle body)')):
            d.text((xx, y), s, fill=DIM, font=f_s)
        y += 22
        im.paste(cut(r, x0, PW, L1), (xs[0], y)); im.paste(cut(rl, 0.0, PW, L2), (xs[1], y)); im.paste(cut(rl, xs_small, PW, L3), (xs[2], y))
        for xx in xs[:3]:
            level(d, xx, y, PW)
        d.text((xs[0] + 6, y + PW - 24), 'pale = the left-hand body, cut across', fill=DIM, font=f_s)
        d.text((xs[1] + 6, y + PW - 24), 'pale = from here a point stays' if later else 'pale = the middle body, cut across', fill=DIM, font=f_s)
        d.text((xs[2] + 6, y + PW - 24), 'pale = from here a point stays' if later else 'pale = the small body at the far left', fill=DIM, font=f_s)
        dots(d, xs[0], y, y0, z0, ins, L1, PW); dots(d, xs[1], y, p1[1], p1[2], ins, L2, PW); dots(d, xs[2], y, p2[1], p2[2], ins, L3, PW)
        im.paste(solid(r, (-0.98, 0.0, 0.0), 0.62, SW, SH), (xs[3], y)); y += PW + 8
        for ln in wrap(d, cap, f_c, W - 2 * pad):
            d.text((pad, y), ln, fill=TXT, font=f_c); y += 23
        y += 30
        print(name, 'drawn', '%.0f s' % (time.time() - t0)); sys.stdout.flush()
    im = im.crop((0, 0, W, y)); out = os.path.join(HERE, 'bud-two-steps%s.png' % ('-quick' if QUICK else '')); im.save(out); print(out, im.size)


# ============================================================================================ picture b
def page_first(name, rule, ys, zs):
    """Turn of the page each start point (0, ys, zs) is first squared in."""
    if name.startswith('follow'):
        a = float(name[6:]); ph = np.arctan2(zs, ys); return ph - a * np.sin(4 * ph) / 4
    t = B.trace(name, np.zeros_like(ys), ys, zs, C, 1); return t['page'][0]


def picture_b():
    t0 = time.time(); f_t, f_h, f_c, f_s = M.font(30), M.font(21), M.font(17), M.font(15)
    fc = B.flat_centres(C[0]); rad = abs(fc['g1'].imag)
    PW = 150 if QUICK else 360; SW, SH = (160, 150) if QUICK else (440, 360); pad = 14; L = 0.95
    half = M.fixed(M.S.switch(0.5), 'follow0.5')
    ROWS = [('oneplane', B.RULES['oneplane'], 'Sphere inversions, one plane: the page never moves',
             'All seven lines lie on the flat page. Only the red point is in its own page. Step a little to the side and you are off your page at once: a bud at the flat page only (one on each side of the body), as wide as it is tall. A ball.'),
            ('follow0.5', half, 'A rule in between: the page follows the point half-way',
             'The page catches up with the point at the flat, the slanted and the upright page. But a point has to go twice as far to the side before it is as far off its page: each bud is twice as long round the x-axis as it is tall. Ribs.'),
            ('lathe', B.RULES['lathe'], 'Quaternion square (Lathe): the page follows the point all the way',
             'Every line goes through its own point. No point is ever off its page, so the bud never ends: it runs all the way round the x-axis. A ring.'),
            ('along', B.RULES['along'], 'Turning plane, along: the page waits at the flat and upright pages and overtakes the point at the slanted one',
             'Near the flat and upright pages the page stands still, as in the first row. At the slanted page it runs ahead twice as fast as the point, so a point a little to the side is that same little behind its page. Either way: eight buds, each as wide as it is tall. Balls.'),
            ('pulled', B.RULES['pulled'], 'Pulled plane: the point pulls the page toward itself, weakly when it is near, all the way when it stands upright to it',
             'Near the flat page the page follows the point about a third of the way: a bud there, a little long. A point on the upright page pulls the page upright: a bud there. In between the page is left well behind the point: no slanted buds. Four directions.')]
    W = pad + 2 * (PW + pad) + SW + pad
    im = Image.new('RGB', (W, 5000), BG); d = ImageDraw.Draw(im)
    d.text((pad, 14), 'What makes a bud a ball, a rib or a ring', fill=INK, font=f_t)
    intro = ['A test point makes a bud only if it lies in the page it is squared in (then it lands on the x-axis, inside).',
             'So what counts is how the page moves when the point moves to the side. Left: seven test points round the middle body of the',
             'c = -1 shape, a quarter of the way round, looking along the x-axis. The line of the same colour is the page that point is squared in.',
             'White rim = the point lies in its own page. Middle: the whole ring, cut across; big orange dots stay in the shape, small grey ones fly away. Right: the body.']
    y = 58
    for s in intro:
        d.text((pad, y), s, fill=GREY, font=f_c); y += 24
    y += 14
    phi = np.arange(N) * 2 * np.pi / N; y0, z0 = rad * np.cos(phi), rad * np.sin(phi); xx0 = np.zeros(N)
    qa = np.radians(np.arange(7) * 15.0); qy, qz = rad * np.cos(qa), rad * np.sin(qa)
    for name, r, head, cap in ROWS:
        ins = B.inside(name, xx0, y0, z0, C, STEPS, rule=r)
        pg = page_first(name, r, qy, qz); off = np.degrees(np.abs(B.fold(qa - pg)))
        print(name, 'stay %d of %d' % (ins.sum(), N), '| pages of the seven points (deg):', np.round(np.degrees(B.fold(pg)), 1), '| off their page (deg):', np.round(off, 1), '%.0f s' % (time.time() - t0)); sys.stdout.flush()
        d.text((pad, y), head, fill=GOLD, font=f_h); y += 30
        xs = [pad, pad + PW + pad, pad + 2 * (PW + pad)]
        for xx, s in zip(xs, ('Seven test points and the page each is squared in', 'The ring of test points, cut across the middle body', 'The middle body this rule makes (rough blocks)')):
            d.text((xx, y), s, fill=DIM, font=f_s)
        y += 22
        # ---- the diagram: a quarter of the way round; the x-axis is the corner at the lower left
        ox, oy = xs[0] + 46, y + PW - 46; R = PW - 110
        d.rectangle([xs[0], y, xs[0] + PW - 1, y + PW - 1], fill=(20, 26, 40))
        d.line([ox, oy, ox + R + 40, oy], fill=(70, 80, 100), width=1); d.line([ox, oy, ox, oy - R - 40], fill=(70, 80, 100), width=1)
        d.text((ox + R - 30, oy + 8), 'flat page', fill=DIM, font=f_s); d.text((ox + 8, oy - R - 44), 'upright page', fill=DIM, font=f_s)
        d.text((xs[0] + 6, oy + 22), 'the x-axis, seen end-on', fill=DIM, font=f_s)
        deg = np.degrees(B.fold(pg)); deg = np.where((deg < -45), deg + 180, deg)             # -90 and 90 are the same page: draw it upward
        order = np.argsort(deg); groups = []
        for i in order:
            if groups and abs(deg[i] - deg[groups[-1][-1]]) < 1.5:
                groups[-1].append(i)
            else:
                groups.append([i])
        for g in groups:
            for j, i in enumerate(g):
                wd = 3 + 4 * (len(g) - 1 - j); a = np.radians(deg[i])
                d.line([ox, oy, ox + (R + 30) * np.cos(a), oy - (R + 30) * np.sin(a)], fill=hue(i, 9), width=wd)
        d.ellipse([ox - 5, oy - 5, ox + 5, oy + 5], fill=(230, 230, 235))
        for i in range(7):
            px, py = ox + R * np.cos(qa[i]), oy - R * np.sin(qa[i])
            if off[i] < 1.5:
                d.ellipse([px - 11, py - 11, px + 11, py + 11], fill=hue(i, 9), outline=(255, 255, 255), width=3)
            else:
                d.ellipse([px - 7, py - 7, px + 7, py + 7], fill=hue(i, 9), outline=(0, 0, 0), width=1)
        # ---- the cut across and the solid
        im.paste(cut(r, 0.0, PW, L), (xs[1], y)); level(d, xs[1], y, PW)
        d.text((xs[1] + 6, y + PW - 24), 'level line = the flat page, seen edge-on', fill=DIM, font=f_s)
        dots(d, xs[1], y, y0, z0, ins, L, PW, big=7, small=3, mono=True)
        im.paste(solid(r, (0.0, 0.0, 0.0), 0.95, SW, SH), (xs[2], y)); y += PW + 8
        for ln in wrap(d, cap, f_c, W - 2 * pad):
            d.text((pad, y), ln, fill=TXT, font=f_c); y += 23
        y += 30
        print(name, 'drawn', '%.0f s' % (time.time() - t0)); sys.stdout.flush()
    im = im.crop((0, 0, W, y)); out = os.path.join(HERE, 'ball-rib-ring%s.png' % ('-quick' if QUICK else '')); im.save(out); print(out, im.size)


if __name__ == '__main__':
    which = [a for a in sys.argv[1:] if a in ('a', 'b')] or ['a', 'b']
    if 'a' in which:
        picture_a()
    if 'b' in which:
        picture_b()

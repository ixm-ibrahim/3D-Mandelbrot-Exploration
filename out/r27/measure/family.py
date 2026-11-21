"""Round 27, measure, part 5: the object's own dials as a family, in the flat cut and as solids.

    python out/r27/measure/family.py t          family-t.png        the dial t (1 and above) and the grid
    python out/r27/measure/family.py rings      family-rings.png    t below 1: the rungs where the balls close up in rings
    python out/r27/measure/family.py slide      family-slide.png    the sideways slide of the glued copy
    python out/r27/measure/family.py klein      family-klein.png    the lab's old Kleinian group: lean and spiral
    python out/r27/measure/family.py rabbit     rabbit-nearest.png  the nearest thing to a rabbit, next to the true rabbit
    python out/r27/measure/family.py check      family-check.log    finer checks of the settings that are drawn

All pictures are drawn from the list of balls (ballkit.py): exact balls, no blocks.
"""
import os, sys, time
import numpy as np
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import ballkit as K

K.BASIS['check'] = [[1.0, 1.0], [1.0, -1.0]]                 # the square grid's every second point (diagonal neighbours), turned so that a mirror is the flat plane
K.BASIS['gauss45'] = [[np.sqrt(0.5), np.sqrt(0.5)], [np.sqrt(0.5), -np.sqrt(0.5)]]   # the square grid turned by 45 degrees
BG = (12, 14, 20)


def balls(grid, top, slide=(0.0, 0.0), c0=(0.0, 0.0, 1.0), k2=1.05, r_min=0.003, klein=None, cap=2_500_000):
    gens = K.klein_gens(klein) if klein is not None else K.recipe_gens(top, slide)
    reps, info = K.build(grid, gens, top, rho_min=r_min / 6.0, cap=cap, strict=klein is None)
    return K.picture(reps, grid, top, c0=c0, k2=k2, r_min=r_min), info


def text(d, xy, s, sz=16, fill=(200, 205, 215)):
    d.text(xy, s, fill=fill, font=K.font(sz))


def cutimg(B, w, h, box, ang=0.0):
    return Image.fromarray(K.paint(K.cut(B, w, h, box, ang=ang), fg=(232, 224, 200), bg=(22, 28, 44)))


def solidimg(B, w, h, half_w, centre=(0, 0, 0), cam=(0.45, 0.5, 1.0)):
    return Image.fromarray(K.solid_img(B, w, h, half_w, centre, cam))


# ---------------------------------------------------------------- the dial t and the grid
def sheet_t():
    ts = [2.5, 1.4, 1.15, 1.0]; w, h, pad = 440, 316, 8; t0 = time.time()
    rows = [('flat cut (the same for every grid)', 'line', 'cut'), ('square grid, solid', 'gauss', 'solid'), ('honeycomb grid, solid', 'eisen', 'solid'), ('a line only, solid', 'line', 'solid')]
    W = pad + len(ts) * (w + pad); H = 52 + len(rows) * (h + 26) + 34
    im = Image.new('RGB', (W, H), BG); d = ImageDraw.Draw(im)
    text(d, (pad, 8), 'The dial t: how big the neighbours are. From small (left) to as big as the middle ball (right).', 23, (240, 240, 245))
    for j, t in enumerate(ts):
        for i, (rn, gname, kind) in enumerate(rows):
            g = K.Grid(gname); B, info = balls(g, 2 * t, r_min=0.0035 if kind == 'solid' else 0.0015)
            x = pad + j * (w + pad); y = 52 + i * (h + 26)
            pic = cutimg(B, w, h, (-1.95, 1.95, -1.4, 1.4)) if kind == 'cut' else solidimg(B, w, h, 1.95)
            im.paste(pic, (x, y + 22)); text(d, (x + 2, y), 't = %.2f: %s' % (t, rn), 15, (235, 220, 170))
            print('t', t, gname, kind, len(B), '%.0f s' % (time.time() - t0)); sys.stdout.flush()
    text(d, (pad, H - 30), 'At t = 1 the chain never ends: it runs out of the picture as an endless string of equal balls.', 16)
    im.save(os.path.join(HERE, 'family-t.png')); print('wrote family-t.png', im.size)


# ---------------------------------------------------------------- the rungs below 1
def ring_frame(t, k2=None):
    s = np.sqrt(1 - t * t); k2 = k2 or 1.0 * t; c0 = (s, 0.0, t); centre = (k2 / (2 * t), -k2 / (2 * s), 0.0)
    return c0, k2, centre


def sheet_rings():
    ms = [3, 4, 5, 6, 8]; w, h, pad = 400, 400, 8; t0 = time.time(); g = K.Grid('check'); g2 = K.Grid('gauss', 2.0)
    W = pad + len(ms) * (w + pad); H = 80 + 3 * (h + 26) + 60
    im = Image.new('RGB', (W, H), BG); d = ImageDraw.Draw(im)
    text(d, (pad, 8), 'Below t = 1 the dial has rungs. On each rung the balls close up in a ring: of three, four, five, six, eight ...', 23, (240, 240, 245))
    text(d, (pad, 42), 'Rows: the cut through the ring; the solid with few buds (every second whole number both ways); the solid with buds all over (every second point of the square grid).', 16)
    for j, m in enumerate(ms):
        t = float(np.cos(np.pi / m)); c0, k2, centre = ring_frame(t)
        B, info = balls(g, 2 * t, c0=c0, k2=k2, r_min=0.006); B2, info2 = balls(g2, 2 * t, c0=c0, k2=k2, r_min=0.002)
        x = pad + j * (w + pad); hw = 2.3
        y = 80; im.paste(cutimg(B, w, h, (centre[0] - hw, centre[0] + hw, centre[1] - hw, centre[1] + hw)), (x, y + 22))
        text(d, (x + 2, y), 'ring of %d  (t = %.4f)' % (m, t), 16, (235, 220, 170))
        y = 80 + h + 26; im.paste(solidimg(B2, w, h, hw, centre, cam=(0.25, 0.3, 1.0)), (x, y + 22))
        y = 80 + 2 * (h + 26); im.paste(solidimg(B, w, h, hw, centre, cam=(0.25, 0.3, 1.0)), (x, y + 22))
        print('ring', m, len(B), info, len(B2), info2, '%.0f s' % (time.time() - t0)); sys.stdout.flush()
    text(d, (pad, H - 54), 'Between the rungs there is no object: the balls would cut into each other. From t = 1 on the ring is open and the dial moves freely.', 16)
    text(d, (pad, H - 30), 'Each ball in a ring kisses its two neighbours. The balls never meet in one point: they stand round a hole.', 16)
    im.save(os.path.join(HERE, 'family-rings.png')); print('wrote family-rings.png', im.size)


# ---------------------------------------------------------------- the sideways slide
def sheet_slide():
    w, h, pad = 400, 300, 8; t0 = time.time()
    cols = [('square grid, no slide', 'gauss', (0, 0), 1.15), ('square grid, slid half a step', 'gauss', (0.5, 0), 1.15), ('square grid, half a step both ways', 'gauss', (0.5, 0.5), 1.15),
            ('every second point of the grid, slide 0.3', 'check', (0.3, 0), 1.15), ('every second point of the grid, slide 1', 'check', (1.0, 0), 1.15)]
    W = pad + len(cols) * (w + pad); H = 80 + 3 * (h + 26) + 60
    im = Image.new('RGB', (W, H), BG); d = ImageDraw.Draw(im)
    text(d, (pad, 8), 'The sideways slide of the glued copy (t = 1.15): the chain forks or bends, and stays a chain of exact balls', 23, (240, 240, 245))
    text(d, (pad, 42), 'Rows: the flat cut; the solid from the front; the solid from above.', 16)
    for j, (name, gname, sl, t) in enumerate(cols):
        g = K.Grid(gname); B, info = balls(g, 2 * t, slide=sl, r_min=0.0035)
        x = pad + j * (w + pad)
        for i, pic in enumerate((cutimg(B, w, h, (-2.0, 2.0, -1.5, 1.5)), solidimg(B, w, h, 2.0), solidimg(B, w, h, 2.0, cam=(0.2, 1.0, 0.35)))):
            y = 80 + i * (h + 26); im.paste(pic, (x, y + 22))
            if i == 0:
                text(d, (x + 2, y), name, 15, (235, 220, 170))
        print('slide', name, len(B), '%.0f s' % (time.time() - t0)); sys.stdout.flush()
    text(d, (pad, H - 54), 'With slides by every whole number the copy can only be slid by half a step: the chain forks. Any other slide makes the balls cut into each other.', 16)
    text(d, (pad, H - 30), 'With every second point of the grid the slide is free, as long as no ball of the floor cuts a ball of the ceiling. The chain bends to one side; it never spirals.', 16)
    im.save(os.path.join(HERE, 'family-slide.png')); print('wrote family-slide.png', im.size)


# ---------------------------------------------------------------- the lab's old Kleinian group
def sheet_klein():
    w, h, pad = 400, 400, 8; t0 = time.time(); g = K.Grid('line', 2.0)
    mus = [(0.0, 2.2), (0.5, 2.0), (0.9, 1.85), (1.0, 1.75), (1.5, 1.95)]
    W = pad + len(mus) * (w + pad); H = 80 + (h + 26) + 60
    im = Image.new('RGB', (W, H), BG); d = ImageDraw.Draw(im)
    text(d, (pad, 8), "The lab's Kleinian group has the dial with two numbers: slide and height. Its chains lean and spiral.", 23, (240, 240, 245))
    text(d, (pad, 42), 'Flat pictures, each seen from the point half way between the two big bodies.', 16)
    for j, mu in enumerate(mus):
        m3 = (mu[0], 0.0, mu[1]); c0 = (mu[0] / 2, 0.0, mu[1] / 2); k2 = 0.9 * mu[1] / 2
        B, info = balls(g, mu[1], c0=c0, k2=k2, r_min=0.0012, klein=m3)
        x = pad + j * (w + pad); cx = k2 / mu[1]; hw = 1.9
        im.paste(cutimg(B, w, h, (cx - hw, cx + hw, -hw, hw)), (x, 80 + 22)); text(d, (x + 2, 80), 'slide %.2f, height %.2f' % mu, 16, (235, 220, 170))
        cnt, deep = K.overlaps(B, n_big=300); print('klein', mu, len(B), 'overlapping pairs', cnt, '%.0f s' % (time.time() - t0)); sys.stdout.flush()
    text(d, (pad, H - 54), 'All of these are the same family tree of round bodies, bent. Two bodies meet at every meeting point, never three.', 16)
    text(d, (pad, H - 30), 'So this dial is like moving c inside one bulb of the Mandelbrot set. It cannot take you to the next bulb.', 16)
    im.save(os.path.join(HERE, 'family-klein.png')); print('wrote family-klein.png', im.size)


# ---------------------------------------------------------------- the nearest thing to a rabbit
RABBIT = (-0.122561, 0.744862)


def sheet_rabbit():
    w, h, pad = 470, 470, 10; t0 = time.time(); t = 0.5
    c0, k2, centre = ring_frame(t)
    B2, info2 = balls(K.Grid('gauss', 2.0), 2 * t, c0=c0, k2=k2, r_min=0.0015)           # every second whole number both ways: the ring shows
    B1, info1 = balls(K.Grid('check'), 2 * t, c0=c0, k2=k2, r_min=0.004)                # every second point of the square grid: buds all over
    W = pad + 4 * (w + pad); H = 60 + h + 26 + 88
    im = Image.new('RGB', (W, H), BG); d = ImageDraw.Draw(im)
    text(d, (pad, 8), 'The nearest thing to a rabbit in the family of balls: a ring of three balls (the dial t at 0.5)', 25, (240, 240, 245))
    y = 60; hw = 1.6
    cov = K.julia_cov(RABBIT[0], RABBIT[1], w, h, (-1.6, 1.6, -1.6, 1.6), 600, ss=3)
    box = (centre[0] - hw, centre[0] + hw, centre[1] - hw, centre[1] + hw)
    pics = [('the true flat picture of the rabbit', Image.fromarray(K.paint(cov, fg=(232, 224, 200), bg=(22, 28, 44)))),
            ('ring of three: the cut through the ring', cutimg(B2, w, h, box)),
            ('ring of three: the solid (every second whole number)', solidimg(B2, w, h, hw, centre, cam=(0.3, 0.35, 1.0))),
            ('the same ring with buds all over: a ball of balls', solidimg(B1, w, h, hw, centre, cam=(0.3, 0.35, 1.0)))]
    for j, (name, pic) in enumerate(pics):
        x = pad + j * (w + pad); im.paste(pic, (x, y + 22)); text(d, (x + 2, y), name, 16, (235, 220, 170))
    text(d, (pad, H - 82), 'In the rabbit three bodies meet in ONE point, at every meeting point, and c moves it smoothly into other pictures.', 16)
    text(d, (pad, H - 58), 'Three balls cannot do that. They kiss two at a time, round a small hole, and everything sits inside a round outline. It is a packing of circles, not a rabbit.', 16)
    text(d, (pad, H - 34), 'And it is one single setting of the dial. Next to it on both sides the balls cut into each other. With buds all over, the ring is hidden inside a ball.', 16)
    im.save(os.path.join(HERE, 'rabbit-nearest.png')); print('wrote rabbit-nearest.png', im.size, len(B1), info1, len(B2), info2, '%.0f s' % (time.time() - t0))
    cnt, deep = K.overlaps(B2, n_big=400); print('   every second whole number: overlapping pairs', cnt)
    # how the three big balls stand: radii, and the distances between their centres
    b = B2[np.argsort(-B2[:, 3])[:3]]; dd = [float(np.linalg.norm(b[i, :3] - b[j, :3])) for i, j in ((0, 1), (0, 2), (1, 2))]
    print('   the three largest balls: radii %s; distances between centres %s (sum of radii = kiss)' % (np.round(b[:, 3], 5), np.round(dd, 5)))
    # the small hole in the middle: the largest circle about the ring's centre that meets no ball, in the cut
    discs = B2[np.abs(B2[:, 2]) < B2[:, 3]]; gap = np.min(np.hypot(discs[:, 0] - centre[0], discs[:, 1] - centre[1]) - np.sqrt(discs[:, 3] ** 2 - discs[:, 2] ** 2))
    print('   hole in the middle of the ring (cut): radius %.5f = %.3f of a big ball\'s radius' % (gap, gap / b[0, 3]))


def check():
    log = open(os.path.join(HERE, 'family-check.log'), 'w')

    def say(s):
        print(s); log.write(s + '\n'); log.flush()
    sys.path.insert(0, HERE); import valid as V
    say('Finer checks of the settings that are drawn (balls down to radius 0.003 in the object\'s own coordinates; 300 largest against all)')
    for tag, gname, per, t, sl in [('ring of 3, check grid', 'check', 1.0, 0.5, (0, 0)), ('ring of 4, check grid', 'check', 1.0, np.cos(np.pi / 4), (0, 0)), ('ring of 5, check grid', 'check', 1.0, np.cos(np.pi / 5), (0, 0)),
                                   ('ring of 6, check grid', 'check', 1.0, np.cos(np.pi / 6), (0, 0)), ('ring of 8, check grid', 'check', 1.0, np.cos(np.pi / 8), (0, 0)),
                                   ('between rungs, check grid', 'check', 1.0, 0.62, (0, 0)), ('between rungs, check grid', 'check', 1.0, 0.9, (0, 0)),
                                   ('square, half step', 'gauss', 1.0, 1.15, (0.5, 0)), ('square, half step both ways', 'gauss', 1.0, 1.15, (0.5, 0.5)), ('square, slide 0.3', 'gauss', 1.0, 1.15, (0.3, 0)),
                                   ('check grid, slide 0.3', 'check', 1.0, 1.15, (0.3, 0)), ('check grid, slide 1', 'check', 1.0, 1.15, (1.0, 0)), ('check grid, slide (0.37, 0.21)', 'check', 1.0, 1.15, (0.37, 0.21)),
                                   ('check grid, slide 1, t = 0.9', 'check', 1.0, 0.9, (1.0, 0)), ('check grid, slide 1, t = 0.85', 'check', 1.0, 0.85, (1.0, 0)),
                                   ('honeycomb, slid to the middle of a triangle', 'eisen', 1.0, 1.15, (0.5, 0.5 / np.sqrt(3))), ('honeycomb, slid half a step', 'eisen', 1.0, 1.15, (0.5, 0.0)),
                                   ('honeycomb sqrt 3, slide 0.3', 'eisen', np.sqrt(3), 1.15, (0.3, 0.1))]:
        g = K.Grid(gname, per); r = V.test(g, 2 * t, slide=sl, rho=0.003, cap=40000)
        say('   ' + V.line('%s: t = %.4f slide (%.3g, %.3g)' % (tag, t, sl[0], sl[1]), r))
    log.close()


def twist():
    """How much does one step along the main chain turn? The step is the move that carries each ball of the chain to
    the next but one. Found numerically: its resting point, and the turn of the move there."""
    log = open(os.path.join(HERE, 'family-twist.log'), 'w')

    def say(s):
        print(s); log.write(s + '\n'); log.flush()

    def measure(step):
        p = np.array([0.31, 0.17, 0.63])
        for _ in range(4000):
            q = np.array(step(*p));
            if np.linalg.norm(q - p) < 1e-14:
                break
            p = q
        h = 1e-6; Jm = np.zeros((3, 3))
        for a in range(3):
            e = np.zeros(3); e[a] = h; Jm[:, a] = (np.array(step(*(p + e))) - np.array(step(*(p - e)))) / (2 * h)
        s = abs(np.linalg.det(Jm)) ** (1 / 3); R = Jm / s; flip = np.linalg.det(Jm) < 0
        ang = np.degrees(np.arccos(np.clip((np.trace(R) - 1) / 2, -1, 1)))
        return p, s, ang, flip, float(np.abs(R @ R.T - np.eye(3)).max())
    say('One step along the main chain: how much smaller, and how much it turns (0 = no spiral)')
    for top, sl in ((2.3, (0, 0)), (2.3, (0.5, 0)), (2.3, (0.3, 0)), (2.3, (1.0, 0)), (2.3, (0.37, 0.21))):
        gf, gc = K.recipe_gens(top, sl); step = lambda x, y, z: gf.point(*gc.point(x, y, z))
        p, s, ang, flip, err = measure(step)
        say('   recipe (two sphere inversions), slide (%.2f, %.2f), t = %.2f: each step %.4f times the size, turn %.4f degrees (shape kept to %.1e)' % (sl[0], sl[1], top / 2, s, ang, err))
    for mu in ((0.0, 2.2), (0.5, 2.0), (0.9, 1.85), (1.0, 1.75), (1.5, 1.95)):
        gf, gc = K.klein_gens((mu[0], 0.0, mu[1])); step = lambda x, y, z: gc.point(x, y, z)
        p = np.array([0.31, 0.0, 0.63])                           # in the flat plane (its move turns space inside out, so the turn is read in the flat plane)
        for _ in range(4000):
            q = np.array(step(*p))
            if np.linalg.norm(q - p) < 1e-14:
                break
            p = q
        h = 1e-6; a = (np.array(step(p[0] + h, 0.0, p[2])) - np.array(step(p[0] - h, 0.0, p[2]))) / (2 * h)
        s = float(np.hypot(a[0], a[2])); ang = float(np.degrees(np.arctan2(a[2], a[0])))
        say("   lab's old Kleinian group (flat), slide %.2f, height %.2f: each step %.4f times the size, turn %.2f degrees" % (mu[0], mu[1], s, ang))
    log.close()


if __name__ == '__main__':
    a = sys.argv[1] if len(sys.argv) > 1 else 't'
    {'t': sheet_t, 'rings': sheet_rings, 'slide': sheet_slide, 'klein': sheet_klein, 'rabbit': sheet_rabbit, 'check': check, 'twist': twist}[a]()

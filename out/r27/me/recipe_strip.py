"""Round 27, orchestrator: two pictures for the user that show how the balls object is made, one move at a time.

    python out/r27/me/recipe_strip.py      -> out/r27/me/recipe-1-the-recipe.png, out/r27/me/recipe-2-what-comes-out.png

Everything is drawn in the flat cut. The recipe is the one in out/r25/klein/tree.py (grid 'line', t = 1.40, k^2 = 1.05).
"""
import os, sys, math
import numpy as np
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, 'out', 'r21', 'lib'))
import mem as M

T = 1.40; TOP = 2 * T; K2 = 1.05
SS = 2                                             # everything is drawn twice as large and then shrunk
BG = (12, 14, 20); OPEN = (24, 28, 40); BODY = (206, 192, 150); BODY_DIM = (122, 114, 92); WALL = (244, 244, 248)
GUIDE = (128, 138, 160); HOT = (255, 214, 120); A_COL = (255, 150, 60); B_COL = (96, 200, 255); RING = (130, 232, 150)
INK = (236, 236, 242); SOFT = (176, 184, 200); EDGE = (52, 58, 76)
X0, X1, Z0, Z1 = -2.75, 2.75, -0.78, 3.58          # the window in the object's own coordinates
PW, PH, CAP, PAD = 560, 444, 78, 14                # one panel: picture, caption, gap


def inside_model(mx, mz, rounds=60):
    """The recipe for the flat cut. True where the point lands behind a wall."""
    mx = mx.copy(); mz = mz.copy()
    res = np.zeros(mx.shape, bool); alive = np.ones(mx.shape, bool)
    for _ in range(rounds):
        ins = alive & ((mz < 0) | (mz > TOP)); res |= ins; alive &= ~ins
        mx = mx - np.round(mx)
        rb = mx * mx + mz * mz; rt = mx * mx + (mz - TOP) ** 2
        inb = alive & (rb < 1); itp = alive & ~inb & (rt < 1)
        alive &= (inb | itp)
        sb = 1 / np.where(rb > 0, rb, 1.0); st = 1 / np.where(rt > 0, rt, 1.0)
        mx, mz = np.where(inb, mx * sb, np.where(itp, mx * st, mx)), np.where(inb, mz * sb, np.where(itp, TOP + (mz - TOP) * st, mz))
    return res | alive


def balls_cut(px, py):
    """The flat cut of the balls object in the lab's frame (picture x along the chain, picture y up)."""
    uz = px - K2 / 2; dd = py * py + uz * uz; dd = np.where(dd > 0, dd, 1e-300)
    return inside_model(K2 * py / dd, 1 + K2 * uz / dd)


def true_flat(px, py, cx=-1.0, cy=0.0, steps=400):
    """The true flat picture of z^2 + c: True where the orbit stays."""
    zx = px.copy(); zy = py.copy(); alive = np.ones(px.shape, bool)
    for _ in range(steps):
        zx, zy = np.where(alive, zx * zx - zy * zy + cx, zx), np.where(alive, 2 * zx * zy + cy, zy)
        alive &= (zx * zx + zy * zy <= 16.0)
    return alive


def path(mx, mz, rounds=12):
    """The moves of one point: a list of ('slide' | 'flip', from, to, centre) and the verdict."""
    moves = []
    for _ in range(rounds):
        if mz < 0 or mz > TOP:
            return moves, 'inside'
        nx = mx - round(mx)
        if abs(nx - mx) > 1e-9:
            moves.append(('slide', (mx, mz), (nx, mz), None)); mx = nx
        rb = mx * mx + mz * mz; rt = mx * mx + (mz - TOP) ** 2
        if rb < 1:
            n = (mx / rb, mz / rb); moves.append(('flip', (mx, mz), n, (0.0, 0.0))); mx, mz = n
        elif rt < 1:
            n = (mx / rt, TOP + (mz - TOP) / rt); moves.append(('flip', (mx, mz), n, (0.0, TOP))); mx, mz = n
        else:
            return moves, 'outside'
    return moves, 'undecided'


class Panel:
    def __init__(self, im, ox, oy):
        self.im = im; self.d = ImageDraw.Draw(im); self.ox = ox * SS; self.oy = oy * SS

    def xy(self, mx, mz):
        return (self.ox + (mx - X0) / (X1 - X0) * PW * SS, self.oy + (Z1 - mz) / (Z1 - Z0) * PH * SS)

    def clip_line(self, pts, col, w, dash=None):
        """A polyline, drawn only where it lies in the panel."""
        x0, y0, x1, y1 = self.ox, self.oy, self.ox + PW * SS, self.oy + PH * SS
        run = []
        for i, p in enumerate(pts):
            ok = x0 <= p[0] <= x1 and y0 <= p[1] <= y1
            if ok and (dash is None or (i // dash) % 2 == 0):
                run.append(p)
            else:
                if len(run) > 1: self.d.line(run, fill=col, width=w * SS, joint='curve')
                run = []
        if len(run) > 1: self.d.line(run, fill=col, width=w * SS, joint='curve')

    def base(self, fill=None):
        """The open space, the two bodies behind the walls, the walls."""
        x0, y0 = self.ox, self.oy; x1, y1 = x0 + PW * SS, y0 + PH * SS
        if fill is None:
            self.d.rectangle([x0, y0, x1, y1], fill=OPEN)
            self.d.rectangle([x0, self.xy(0, 0)[1], x1, y1], fill=BODY_DIM)
            self.d.rectangle([x0, y0, x1, self.xy(0, TOP)[1]], fill=BODY_DIM)
        else:
            self.im.paste(fill, (x0, y0))
        for z in (0.0, TOP):
            y = self.xy(0, z)[1]; self.d.line([x0, y, x1 - 1, y], fill=WALL, width=3 * SS)

    def balls(self, hot=None):
        """The unit balls on the walls (their halves between the walls), dashed; one of them can be lit."""
        for cz, sgn in ((0.0, 1), (TOP, -1)):
            for n in range(-4, 5):
                pts = [self.xy(n + math.cos(a), cz + sgn * math.sin(a)) for a in np.linspace(0, math.pi, 181)]
                lit = hot is not None and abs(n - hot[0]) < 1e-9 and abs(cz - hot[1]) < 1e-9
                if not lit: self.clip_line(pts, GUIDE, 2, 6)
        if hot is not None:
            sgn = 1 if hot[1] == 0.0 else -1
            pts = [self.xy(hot[0] + math.cos(a), hot[1] + sgn * math.sin(a)) for a in np.linspace(0, math.pi, 181)]
            self.clip_line(pts, HOT, 3)
            c = self.xy(*hot); r = 5 * SS; self.d.ellipse([c[0] - r, c[1] - r, c[0] + r, c[1] + r], fill=HOT)

    def dot(self, p, col, r=7, ring=False):
        c = self.xy(*p); r *= SS
        if ring:
            self.d.ellipse([c[0] - r, c[1] - r, c[0] + r, c[1] + r], outline=col, width=3 * SS)
        else:
            self.d.ellipse([c[0] - r, c[1] - r, c[0] + r, c[1] + r], fill=col, outline=BG, width=SS)

    def arrow(self, p, q, col, w=3, head=13):
        a = self.xy(*p); b = self.xy(*q)
        ang = math.atan2(b[1] - a[1], b[0] - a[0]); h = head * SS
        tip = (b[0] - 8 * SS * math.cos(ang), b[1] - 8 * SS * math.sin(ang))          # stop just short of the dot
        back = (tip[0] - 0.8 * h * math.cos(ang), tip[1] - 0.8 * h * math.sin(ang))
        self.d.line([a, back], fill=col, width=w * SS)
        self.d.polygon([tip, (tip[0] - h * math.cos(ang - 0.42), tip[1] - h * math.sin(ang - 0.42)),
                        (tip[0] - h * math.cos(ang + 0.42), tip[1] - h * math.sin(ang + 0.42))], fill=col)

    def slide(self, p, q, col, w=3):
        self.arrow(p, q, col, w)
        steps = int(round(abs(q[0] - p[0])))
        for i in range(1, steps):                                                     # a tick at every whole step
            x = p[0] + (q[0] - p[0]) * i / steps; c = self.xy(x, p[1])
            self.d.line([c[0], c[1] - 7 * SS, c[0], c[1] + 7 * SS], fill=col, width=2 * SS)

    def text(self, p, s, col, size=17, dx=0, dy=0, anchor='la'):
        c = self.xy(*p); f = M.font(size * SS); pos = (c[0] + dx * SS, c[1] + dy * SS)
        box = self.d.textbbox(pos, s, font=f, anchor=anchor)                           # a dark plate keeps words readable over lines
        self.d.rectangle([box[0] - 4 * SS, box[1] - 2 * SS, box[2] + 4 * SS, box[3] + 3 * SS], fill=tuple(self.im.getpixel((int(min(max(box[0], 0), self.im.width - 1)), int(min(max(box[1], 0), self.im.height - 1))))) if False else None)
        self.d.text(pos, s, fill=col, font=f, anchor=anchor)

    def plate(self, p, s, col, size=17, dx=0, dy=0, anchor='la', back=OPEN):
        c = self.xy(*p); f = M.font(size * SS); pos = (c[0] + dx * SS, c[1] + dy * SS)
        box = self.d.textbbox(pos, s, font=f, anchor=anchor)
        self.d.rectangle([box[0] - 5 * SS, box[1] - 3 * SS, box[2] + 5 * SS, box[3] + 4 * SS], fill=back)
        self.d.text(pos, s, fill=col, font=f, anchor=anchor)

    def frame(self):
        self.d.rectangle([self.ox, self.oy, self.ox + PW * SS - 1, self.oy + PH * SS - 1], outline=EDGE, width=SS)


def wrap(d, s, font, width):
    words = s.split(); lines = []; cur = ''
    for w in words:
        t = (cur + ' ' + w).strip()
        if d.textlength(t, font=font) <= width: cur = t
        else: lines.append(cur); cur = w
    lines.append(cur); return lines


def sheet(cols, rows, title):
    W = PAD + cols * (PW + PAD); H = 56 + rows * (PH + CAP + PAD)
    im = Image.new('RGB', (W * SS, H * SS), BG); d = ImageDraw.Draw(im)
    d.text((PAD * SS, 14 * SS), title, fill=INK, font=M.font(24 * SS))
    return im, d


def caption(d, ox, oy, s):
    f = M.font(18 * SS)
    for i, ln in enumerate(wrap(d, s, f, (PW - 8) * SS)):
        d.text(((ox + 4) * SS, (oy + PH + 8 + i * 23) * SS), ln, fill=INK, font=f)


def spot(i, cols):
    return PAD + (i % cols) * (PW + PAD), 56 + (i // cols) * (PH + CAP + PAD)


def paste_mask(im, ox, oy, ins):
    img = np.where(ins[..., None], np.array(BODY, np.uint8), np.array(OPEN, np.uint8)).astype(np.uint8)
    im.paste(Image.fromarray(img), (ox * SS, oy * SS))


def save(im, name):
    out = os.path.join(HERE, name)
    im.resize((im.width // SS, im.height // SS), Image.LANCZOS).save(out); print('wrote', out)


def the_recipe():
    a0 = (2.1409, 0.3439); b0 = (-2.20, 0.70)
    ma, va = path(*a0); mb, vb = path(*b0)
    print('orange:', va, [(k, tuple(round(v, 3) for v in q)) for k, p, q, c in ma])
    print('blue:  ', vb, [(k, tuple(round(v, 3) for v in q)) for k, p, q, c in mb])
    assert va == 'inside' and [m[0] for m in ma] == ['slide', 'flip', 'slide', 'flip']
    assert vb == 'outside' and [m[0] for m in mb] == ['slide', 'flip']
    im, d = sheet(2, 3, 'How the balls object is made: the recipe')
    # 1: the frame
    ox, oy = spot(0, 2); P = Panel(im, ox, oy); P.base(); P.balls(); P.frame()
    P.plate((-2.6, -0.42), 'behind this wall: a body', INK, 17, anchor='lm', back=BODY_DIM)
    P.plate((-2.6, 3.2), 'behind this wall: another body', INK, 17, anchor='lm', back=BODY_DIM)
    P.plate((0, 1.4), 'open space', SOFT, 17, anchor='mm')
    for n in range(-2, 3):
        P.plate((n, 0), str(n), INK, 15, dy=8, anchor='ma', back=BODY_DIM)
    caption(d, ox, oy, '1. Two flat walls. On each wall sits a ball of radius 1 round every whole number (dashed).')
    # 2: slide
    ox, oy = spot(1, 2); P = Panel(im, ox, oy); P.base(); P.balls(); P.frame()
    P.slide(ma[0][1], ma[0][2], A_COL); P.dot(ma[0][1], A_COL); P.dot(ma[0][2], A_COL, ring=True)
    P.plate(ma[0][1], 'a point', A_COL, 17, dx=0, dy=-18, anchor='ms')
    P.plate((1.0, 1.02), 'slide 2 whole steps', A_COL, 17, anchor='mm')
    caption(d, ox, oy, '2. Take a point. Slide it sideways by whole steps until it is as near the middle as it can get.')
    # 3: flip
    ox, oy = spot(2, 2); P = Panel(im, ox, oy); P.base(); P.balls(hot=(0, 0.0)); P.frame()
    P.arrow(ma[1][1], ma[1][2], A_COL); P.dot(ma[1][1], A_COL); P.dot(ma[1][2], A_COL, ring=True)
    P.plate((-1.12, 0.5), 'it is inside this ball', HOT, 17, anchor='rm')
    P.plate(ma[1][2], 'flipped out', A_COL, 17, dx=16, dy=0, anchor='lm')
    caption(d, ox, oy, '3. If it is inside a ball now, flip it inside out through that ball. A point near the centre lands far away.')
    # 4: repeat: the point ends behind a wall
    ox, oy = spot(3, 2); P = Panel(im, ox, oy); P.base(); P.balls(hot=(0, TOP)); P.frame()
    dim = tuple(int(0.5 * v + 0.5 * o) for v, o in zip(A_COL, OPEN))
    P.slide(ma[0][1], ma[0][2], dim, 2); P.arrow(ma[1][1], ma[1][2], dim, 2); P.dot(ma[0][1], dim, 5)
    P.slide(ma[2][1], ma[2][2], A_COL); P.arrow(ma[3][1], ma[3][2], A_COL)
    P.dot(ma[2][1], A_COL, 6); P.dot(ma[3][1], A_COL, 6); P.dot(ma[3][2], A_COL, 8)
    P.plate(ma[2][1], 'slide again', A_COL, 17, dx=14, dy=0, anchor='lm')
    P.plate((-1.12, TOP - 0.5), 'now inside this ball', HOT, 17, anchor='rm')
    P.plate(ma[3][2], 'behind a wall: INSIDE', A_COL, 17, dx=16, dy=0, anchor='lm', back=BODY_DIM)
    caption(d, ox, oy, '4. Repeat: slide, flip, slide, flip. This point ends behind a wall, so it is inside a body.')
    # 5: another point ends in the open
    ox, oy = spot(4, 2); P = Panel(im, ox, oy); P.base(); P.balls(hot=(0, 0.0)); P.frame()
    P.slide(mb[0][1], mb[0][2], B_COL); P.arrow(mb[1][1], mb[1][2], B_COL)
    P.dot(mb[0][1], B_COL); P.dot(mb[1][1], B_COL, 6); P.dot(mb[1][2], B_COL, 8)
    P.plate(mb[0][1], 'another point', B_COL, 17, dy=-16, anchor='ms')
    P.plate(mb[1][2], 'in no ball, behind no wall: OUTSIDE', B_COL, 17, dx=16, dy=0, anchor='lm')
    caption(d, ox, oy, '5. Another point. After one slide and one flip it sits in the open, inside no ball. It is outside for good.')
    # 6: every point
    ox, oy = spot(5, 2)
    gx, gz = np.meshgrid(np.linspace(X0, X1, PW * SS), np.linspace(Z1, Z0, PH * SS))
    img = np.where(inside_model(gx, gz)[..., None], np.array(BODY, np.uint8), np.array(OPEN, np.uint8)).astype(np.uint8)
    P = Panel(im, ox, oy); P.base(fill=Image.fromarray(img))
    k = math.sqrt(K2); pts = [P.xy(k * math.cos(a), 1 + k * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 361)]
    P.clip_line(pts, RING, 3, 5); P.frame()
    caption(d, ox, oy, '6. Do this for every point and colour in the ones that end behind a wall. Balls sit on the walls, smaller balls on those, and so on.')
    save(im, 'recipe-1-the-recipe.png')


def what_comes_out():
    im, d = sheet(2, 2, 'What comes out, and the true flat picture next to it')
    w, h = PW * SS, PH * SS
    half = 1.78; hy = half * PH / PW
    px, py = np.meshgrid(np.linspace(-half, half, w), np.linspace(hy, -hy, h))
    f = M.font(16 * SS)
    # 7: the last flip: the flat cut in the lab's frame
    ox, oy = spot(0, 2); paste_mask(im, ox, oy, balls_cut(px, py))
    cx = lambda x: (ox + (x + half) / (2 * half) * PW) * SS
    cy = lambda y: (oy + (hy - y) / (2 * hy) * PH) * SS
    d.text((cx(0.0), cy(0.0)), 'was the space\nbehind the lower wall', fill=(40, 36, 28), font=f, anchor='mm', align='center')
    rn = K2 / (2 * T - 1)
    d.text((cx(K2 / 2 + rn / 2), cy(-0.66)), 'was the space behind\nthe upper wall', fill=INK, font=f, anchor='ma', align='center')
    d.line([cx(K2 / 2 + rn / 2), cy(-0.64), cx(K2 / 2 + rn / 2), cy(-0.14)], fill=INK, width=2 * SS)
    d.rectangle([ox * SS, oy * SS, (ox + PW) * SS - 1, (oy + PH) * SS - 1], outline=EDGE, width=SS)
    caption(d, ox, oy, '7. One last flip, through the green ring of step 6, bends the two walls round into the two biggest bodies. This is the flat cut of the balls object.')
    # 8: the true flat picture of c = -1, same size
    ox, oy = spot(1, 2); paste_mask(im, ox, oy, true_flat(px, py))
    d.rectangle([ox * SS, oy * SS, (ox + PW) * SS - 1, (oy + PH) * SS - 1], outline=EDGE, width=SS)
    caption(d, ox, oy, '8. For comparison: the true flat picture of c = -1, same size. The same bodies in the same order, but not circles.')
    # 9: where two bodies meet, close up, both
    ox, oy = spot(2, 2)
    hw = 0.20; wl = w // 2 - 2 * SS; hh = hw * h / wl
    qx, qy = np.meshgrid(np.linspace(-hw, hw, wl), np.linspace(hh, -hh, h))
    left = balls_cut(K2 / 2 + qx, qy); right = true_flat(0.5 * (1 + math.sqrt(5)) - 1 + qx, qy, steps=1500)
    img = np.full((h, w, 3), BG, np.uint8)
    img[:, :wl] = np.where(left[..., None], np.array(BODY, np.uint8), np.array(OPEN, np.uint8))
    img[:, w - wl:] = np.where(right[..., None], np.array(BODY, np.uint8), np.array(OPEN, np.uint8))
    im.paste(Image.fromarray(img), (ox * SS, oy * SS))
    fb = M.font(17 * SS)
    for x0, s in ((ox, 'balls object: a kiss'), (ox + PW // 2 + 2, 'true flat picture: a pinch')):
        box = d.textbbox(((x0 + 10) * SS, (oy + 10) * SS), s, font=fb)
        d.rectangle([box[0] - 5 * SS, box[1] - 3 * SS, box[2] + 5 * SS, box[3] + 4 * SS], fill=OPEN)
        d.text(((x0 + 10) * SS, (oy + 10) * SS), s, fill=INK, font=fb)
    d.rectangle([ox * SS, oy * SS, (ox + PW) * SS - 1, (oy + PH) * SS - 1], outline=EDGE, width=SS)
    caption(d, ox, oy, '9. Close up where the two biggest bodies meet. Balls touch round against round. The true bodies come to a point.')
    # 10: the solid (round 25's own picture)
    ox, oy = spot(3, 2)
    big = Image.open(os.path.join(ROOT, 'out', 'r25', 'klein', 'tree-big.png')).convert('RGB').crop((12, 44, 568, 458))
    sc = min(w / big.width, h / big.height); big = big.resize((int(big.width * sc), int(big.height * sc)), Image.LANCZOS)
    d.rectangle([ox * SS, oy * SS, (ox + PW) * SS - 1, (oy + PH) * SS - 1], fill=tuple(big.getpixel((4, 4))))
    im.paste(big, (ox * SS + (w - big.width) // 2, oy * SS + (h - big.height) // 2))
    d.rectangle([ox * SS, oy * SS, (ox + PW) * SS - 1, (oy + PH) * SS - 1], outline=EDGE, width=SS)
    caption(d, ox, oy, '10. The solid. In 3D the slide may go in two directions instead of one. Nothing else in the recipe changes.')
    save(im, 'recipe-2-what-comes-out.png')


if __name__ == '__main__':
    the_recipe(); what_comes_out()

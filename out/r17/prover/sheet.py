"""Prover sheet: one picture per claim. Everything drawn here is computed, except where the caption says 'drawn straight'.
    python out/r17/prover/sheet.py        (needs c2_reversed.npz from c2_degree.py and c3_profile.npz from c3_profile.py)
"""
import os, sys, cmath
import numpy as np
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, 'out', 'me', 'r16'))
sys.path.insert(0, os.path.join(ROOT, 'out', 'r14', 'turns'))
import scout as S, scout3 as S3

BG = (12, 14, 20); INK = (232, 232, 236); DIM = (160, 166, 178)
CREAM = (235, 225, 200); RED = (240, 90, 70); CYAN = (90, 200, 230); ORANGE = (240, 160, 60); GREEN = (120, 210, 130)


def font(s, bold=False):
    for nme in (('segoeuib.ttf',) if bold else ()) + ('segoeui.ttf', 'arial.ttf'):
        try: return ImageFont.truetype(nme, s)
        except OSError: pass
    return ImageFont.load_default()


# ---------- C1: Julia pictures with their 'spine' ----------
def julia(c, box, w, h, steps=300):
    x0, x1, y0, y1 = box
    X, Y = np.meshgrid(np.linspace(x0, x1, w), np.linspace(y1, y0, h))
    z = X + 1j * Y; n = np.zeros(z.shape, np.int32); alive = np.ones(z.shape, bool)
    for k in range(steps):
        z[alive] = z[alive] ** 2 + c
        esc = alive & (np.abs(z) > 4); n[esc] = k + 1; alive &= ~esc
    img = np.zeros((h, w, 3), np.uint8)
    t = np.clip(n / 18.0, 0, 1)
    for ch, col in enumerate((60, 95, 150)): img[:, :, ch] = (18 + (col - 18) * t).astype(np.uint8)
    img[alive] = CREAM
    return Image.fromarray(img)


def ray0(c, smax=2.2, smin=3e-4, k=0.94):
    """the line that comes in from far right (external ray of angle 0), by Newton's method on the escape coordinate."""
    s = smax; z = cmath.exp(s); pts = []
    while s > smin:
        n = 0
        while (2 ** n) * s < 14: n += 1
        ok = False
        for _ in range(60):
            w = z; dw = 1.0
            for _j in range(n):
                dw = 2 * w * dw; w = w * w + c
            g = cmath.log(w) - (2 ** n) * s
            step = w * g / dw
            if abs(step) > 0.2: step *= 0.2 / abs(step)
            z -= step
            if abs(step) < 1e-11: ok = True; break
        if not ok: break
        pts.append(z); s *= k
    return pts


def fN(z, c, n):
    for _ in range(n): z = z * z + c
    return z


def spiral_spine(lam):
    """c inside the main body with flat multiplier lam (not real). Returns c, the resting point a, and the two arms of an
    invariant spine: (0 -> a) through the whole orbit of 0, and (a -> the end point beta)."""
    a = lam / 2; c = a - a * a; N = 90
    xi = lambda z: (fN(z, c, N) - a) / lam ** N
    dxi = lambda z: (xi(z + 1e-6) - xi(z - 1e-6)) / 2e-6
    xi0 = xi(0j); L = cmath.log(lam)

    def solve(z, target):
        for _ in range(50):
            st = (xi(z) - target) / dxi(z)
            z -= st
            if abs(st) < 1e-12: break
        return z
    ts = np.linspace(1, 2, 161)
    # arm 1: through c, f(c), ... to a; and back from c to 0
    A = []; z = c
    for t in ts:
        z = solve(z, xi0 * cmath.exp(t * L)); A.append(z)
    A = np.array(A)
    back = []; prev = c
    for zz in A[::-1]:                       # t from 2 down to 1 gives t - 1 from 1 down to 0
        r = cmath.sqrt(zz - c)
        if abs(r - prev) > abs(-r - prev): r = -r
        back.append(r); prev = r
    arm1 = list(back[::-1])                  # 0 ... c
    seg = A.copy()
    for _ in range(40):
        arm1 += list(seg); seg = seg * seg + c
    # arm 2: the opposite spiral, from a outwards, pulled back until it lands
    z = a + (-xi0 * cmath.exp(30 * L)) / dxi(a)
    B = []
    for t in np.linspace(30, 1, 30 * 40 + 1):
        z = solve(z, -xi0 * cmath.exp(t * L)); B.append(z)
    B = np.array(B[::-1])                    # t from 1 up to 30
    arm2 = list(B[::-1])                     # a ... t = 1
    seg = B[:41].copy()                      # t in [1, 2]
    for _ in range(70):
        new = []; prev = arm2[-1]
        for zz in seg[::-1]:                 # going down in t
            r = cmath.sqrt(zz - c)
            if abs(r - prev) > abs(-r - prev): r = -r
            new.append(r); prev = r
        arm2 += new; seg = np.array(new[::-1])
    return c, a, np.array(arm1), np.array(arm2)


def to_px(pts, box, w, h):
    x0, x1, y0, y1 = box
    return [((p.real - x0) / (x1 - x0) * (w - 1), (y1 - p.imag) / (y1 - y0) * (h - 1)) for p in pts]


def line(d, pts, box, w, h, col, width=2):
    px = to_px(pts, box, w, h)
    d.line(px, fill=col, width=width, joint='curve')


def dot(d, p, box, w, h, col, r=4):
    (x, y), = to_px([p], box, w, h)
    d.ellipse((x - r, y - r, x + r, y + r), fill=col)


def panel_c1(kind, w=580, h=400):
    box = (-1.9, 1.9, -1.31, 1.31)
    if kind == 'basilica':
        c = -1 + 0j; im = julia(c, box, w, h); d = ImageDraw.Draw(im)
        line(d, [-1.9 + 0j, 1.9 + 0j], box, w, h, RED, 2)
        for p in ((1 - 5 ** 0.5) / 2, (1 + 5 ** 0.5) / 2, -(1 + 5 ** 0.5) / 2): dot(d, complex(p), box, w, h, RED)
    elif kind == 'spiral':
        c, a, arm1, arm2 = spiral_spine(0.85 * cmath.exp(2j * np.pi * 0.2))
        im = julia(c, box, w, h); d = ImageDraw.Draw(im)
        r0 = ray0(c)
        line(d, r0, box, w, h, RED); line(d, [-p for p in r0], box, w, h, RED)
        line(d, arm1, box, w, h, RED); line(d, -arm1, box, w, h, RED)
        line(d, arm2, box, w, h, RED); line(d, -arm2, box, w, h, RED)
        dot(d, a, box, w, h, RED); dot(d, -a, box, w, h, RED); dot(d, 0j, box, w, h, CYAN, 3)
        print('spiral case: c = %.4f%+.4fi, resting point %.4f%+.4fi; arm to the end point finishes at %.4f%+.4fi, end point beta = %.4f%+.4fi; ray finishes at %.4f%+.4fi'
              % (c.real, c.imag, a.real, a.imag, arm2[-1].real, arm2[-1].imag, (1 - a).real, (1 - a).imag, r0[-1].real, r0[-1].imag))
    else:
        c = -0.122561 + 0.744862j; im = julia(c, box, w, h); d = ImageDraw.Draw(im)
        a = (1 - cmath.sqrt(1 - 4 * c)) / 2
        r0 = ray0(c)
        line(d, r0, box, w, h, RED); line(d, [-p for p in r0], box, w, h, RED)
        for q in (0j, c, c * c + c): line(d, [a, q], box, w, h, RED, 3); dot(d, q, box, w, h, CYAN, 3)
        dot(d, a, box, w, h, RED, 5)
        print('rabbit: junction point %.4f%+.4fi; ray finishes at %.4f%+.4fi (end point beta = %.4f%+.4fi)' % (a.real, a.imag, r0[-1].real, r0[-1].imag, (1 - a).real, (1 - a).imag))
    return im


# ---------- C2: turning of the sideways part, and where the rule turns space over ----------
def lathe(x, y, z): return x * x - y * y - z * z, 2 * x * y, 2 * x * z


def sigma(F, n=1441, eps=1e-3):
    ph = np.linspace(0, 2 * np.pi, n)
    X, Y, Z = F(np.full_like(ph, -1.0), eps * np.cos(ph), eps * np.sin(ph))
    sg = np.unwrap(np.arctan2(Z, Y)) / (2 * np.pi)
    return np.degrees(ph), sg - np.round(sg[0] - 0.5)          # every curve starts at half a turn (pointing at -y)


def plot_sigma(w=760, h=400):
    im = Image.new('RGB', (w, h), (18, 21, 30)); d = ImageDraw.Draw(im); f = font(13)
    L, R, T, B = 60, w - 150, 14, h - 40
    ymin, ymax = -3.0, 2.0
    X = lambda v: L + (R - L) * v / 360.0
    Y = lambda v: B - (B - T) * (v - ymin) / (ymax - ymin)
    for g in range(-3, 3):
        d.line((L, Y(g), R, Y(g)), fill=(44, 50, 64)); d.text((L - 34, Y(g) - 8), '%+d' % g, fill=DIM, font=f)
    for g in (0, 90, 180, 270, 360):
        d.line((X(g), T, X(g), B), fill=(60, 68, 88) if g % 180 else (80, 90, 120)); d.text((X(g) - 12, B + 6), '%d' % g, fill=DIM, font=f)
    d.text((L + 150, B + 22), 'where the point stands round the negative x-axis (degrees)', fill=DIM, font=f)
    # the directions the two exact planes demand: at 0, 90, 180, 270 degrees the answer points at phi + half a turn (any whole turns added)
    for g in (0, 90, 180, 270, 360):
        for kk in range(-4, 4):
            v = 0.5 + g / 360.0 + kk
            if ymin <= v <= ymax: d.ellipse((X(g) - 5, Y(v) - 5, X(g) + 5, Y(v) + 5), outline=INK, width=2)
    rules = [('one plane (clean, buds in one plane)', S.oneplane, GREEN), ('lathe (rings)', lathe, DIM), ('along (folds)', S3.turning(1), ORANGE), ('away (3 turns back)', S3.turning(-1), CYAN)]
    for i, (nm, F, col) in enumerate(rules):
        ph, sg = sigma(F)
        d.line([(X(a), Y(b)) for a, b in zip(ph, sg) if ymin <= b <= ymax], fill=col, width=3)
        d.text((R + 8, T + 8 + 34 * i), nm.split(' (')[0], fill=col, font=font(14, True)); d.text((R + 8, T + 24 + 34 * i), '(' + nm.split(' (')[1], fill=DIM, font=font(11))
    d.text((R + 8, T + 160), 'rings = where two\nexact planes force\nthe answer to point', fill=INK, font=font(11))
    return im


def disc(mask, back, size=230):
    nt, npz = mask.shape
    u = (np.arange(size) + 0.5) / size * 2 - 1
    U, V = np.meshgrid(u, -u)
    r = np.sqrt(U * U + V * V); P = np.mod(np.arctan2(V, U), 2 * np.pi)
    T = (np.pi - r * np.pi / 2) if back else r * np.pi / 2
    it = np.clip((T / np.pi * nt).astype(int), 0, nt - 1); ip = np.clip((P / (2 * np.pi) * npz).astype(int), 0, npz - 1)
    m = mask[it, ip]
    img = np.zeros((size, size, 3), np.uint8); img[:] = BG
    img[(r <= 1) & ~m] = (58, 78, 118); img[(r <= 1) & m] = ORANGE
    im = Image.fromarray(img); d = ImageDraw.Draw(im)
    d.line((0, size / 2, size, size / 2), fill=(200, 200, 210)); d.line((size / 2, 0, size / 2, size), fill=(200, 200, 210))
    return im


# ---------- C3: the main body cut from centre to rim ----------
def plot_profile(name, rows, title, w=580, h=330):
    im = Image.new('RGB', (w, h), (18, 21, 30)); d = ImageDraw.Draw(im); f = font(13)
    L, R, T, B = 50, w - 16, 30, h - 36
    X = lambda v: L + (R - L) * v
    Y = lambda v: B - (B - T) * v / 0.9
    for g in (0, 0.2, 0.4, 0.6, 0.8):
        d.line((L, Y(g), R, Y(g)), fill=(44, 50, 64)); d.text((L - 30, Y(g) - 8), '%.1f' % g, fill=DIM, font=f)
    d.line((L, B, R, B), fill=INK, width=2)
    d.text((L, B + 8), 'centre of the main body', fill=DIM, font=f); d.text((R - 110, B + 8), 'its flat rim', fill=DIM, font=f)
    d.text((L + 6, T - 22), title, fill=INK, font=font(14, True))
    rho, hs, code, hv = rows.T
    ok = np.isfinite(hs) & (hs > 0.002)
    d.line([(X(a), Y(min(b, 0.9))) for a, b in zip(rho, hv)], fill=(120, 126, 140), width=1)
    for a, b in zip(rho, hv): d.ellipse((X(a) - 2, Y(min(b, 0.9)) - 2, X(a) + 2, Y(min(b, 0.9)) + 2), fill=(150, 156, 170))
    cols = {0: INK, 1: CYAN, 2: RED, 3: INK, 4: DIM}
    pts = [(X(a), Y(b)) for a, b in zip(rho[ok], hs[ok])]
    for (p, q), k in zip(zip(pts[:-1], pts[1:]), code[ok][1:]): d.line((p, q), fill=cols[int(k)], width=3)
    for p, k in zip(pts, code[ok]): d.ellipse((p[0] - 4, p[1] - 4, p[0] + 4, p[1] + 4), fill=cols[int(k)])
    return im


if __name__ == '__main__':
    W = 1800
    sheet = Image.new('RGB', (W, 1640), BG); d = ImageDraw.Draw(sheet)
    f0, f1, f2 = font(24, True), font(16, True), font(14)
    d.text((16, 10), 'Round 17, prover: what the three claims look like', fill=INK, font=f0)
    # C1
    y = 52
    d.text((16, y), 'C1. A second upright sheet has to stand on a line in the flat picture that the flat rule maps into itself (red). Only on the x-axis is that line straight.', fill=INK, font=f1)
    caps = [('basilica', 'c = -1 (on the x-axis): the red line is the x-axis itself. An upright plane can stand on it.'),
            ('spiral', 'c inside the main body, off the x-axis: the line still exists but winds round two points for ever\n(computed). A sheet on it would be a scroll, not a plane.'),
            ('rabbit', 'the rabbit: the two lines from far away end at the tips; inside, the path that is kept is a\nthree-armed star (arms drawn straight). A sheet on it would be a book with three pages.')]
    for i, (k, cap) in enumerate(caps):
        im = panel_c1(k); sheet.paste(im, (16 + i * 596, y + 28)); d.multiline_text((16 + i * 596, y + 432), cap, fill=DIM, font=f2)
    # C2
    y = 540
    d.text((16, y), 'C2. Walk once round the negative x-axis: which way does the sideways part of the answer point? (in whole turns)', fill=INK, font=f1)
    sheet.paste(plot_sigma(), (16, y + 28))
    d.multiline_text((16, y + 434), 'With two exact planes a rule must pass through the rings (one plane does not: it misses at 90 and 270).\nUp one turn in all: either a rigid turn (lathe: rings) or it also runs backwards on the way, a fold (along).\nDown: three turns back, so shapes are pulled at least 3 to 1 (away: 5 to 1 at the diagonals).\nNothing else fits the rings.',
                     fill=DIM, font=f2)
    Z = np.load(os.path.join(HERE, 'c2_reversed.npz'))
    x0 = 800
    d.text((x0, y + 30), 'Where the rule turns the sphere of directions over (orange). Cross = the two planes.', fill=INK, font=f2)
    for i, (nm, lab) in enumerate((('along', 'along: 39 % turned over, wraps 0 times net'), ('away', 'away: 4 % turned over, wraps 4 times'), ('lathe', 'lathe: back half turned over, wraps 0 times'), ('oneplane', 'one plane: nothing turned over, wraps twice'))):
        for j, back in enumerate((True, False)):
            xx = x0 + i * 248; yy = y + 56 + j * 200
            sheet.paste(disc(Z[nm], back, 184), (xx + 20, yy))
        d.text((x0 + i * 248 + 4, y + 56 + 400 - 6), lab.split(': ')[0], fill=INK, font=font(13, True)); d.text((x0 + i * 248 + 4, y + 56 + 400 + 12), lab.split(': ')[1], fill=DIM, font=font(12))
    d.text((x0 - 2, y + 130), 'back', fill=DIM, font=font(11)); d.text((x0 - 2, y + 330), 'front', fill=DIM, font=font(11))
    # C3
    y = 1090
    d.text((16, y), 'C3. The main body of the Mandelbrot solid of three known rules, cut upward along one line from its centre to its flat rim (height above the flat plane).', fill=INK, font=f1)
    Pf = np.load(os.path.join(HERE, 'c3_profile.npz'))
    tit = {'oneplane': 'One plane: a thin lens, bare skin', 'lathe': 'Lathe: full, spinning skin (rings)', 'along': 'Along: full, spinning and flipping skin'}
    for i, nm in enumerate(('oneplane', 'lathe', 'along')):
        sheet.paste(plot_profile(nm, Pf[nm], tit[nm]), (16 + i * 596, y + 28))
    d.multiline_text((16, y + 368),
                     'Thick line = where the resting point stops attracting (the skin of the main body). Its colour says how:\n'
                     'white = the resting point simply vanishes: bare skin, nothing can grow there (so the one-plane body carries buds only on its rim, where it is 7 to 10 times thinner than the lathe);\n'
                     'blue = a pair of directions starts to spin: here buds attach, and the place where the spin is p/q of a turn is a LINE on the skin, so each bud is a ring or a ridge;\n'
                     'red = one direction flips: the period-2 body is grown on over a whole patch.   Thin grey line = up to where the orbit of 0 stays bounded (what the picture of the solid shows).',
                     fill=DIM, font=f2)
    d.multiline_text((16, y + 460), 'Measured on one line only (flat multiplier rho * exp(2.0 i)); the hunter maps the whole skin. Heights at 90 / 98.5 / 99.5 % of the way to the rim: one plane 0.044 / 0.014 / 0.008, lathe 0.317 / 0.128 / 0.074.', fill=DIM, font=f2)
    out = os.path.join(HERE, 'sheet.png'); sheet.save(out); print('wrote', out)

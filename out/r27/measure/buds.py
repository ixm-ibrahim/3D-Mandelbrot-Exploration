"""Round 27, measure, part 3: where the buds sit. Fractions against halvings.

    python out/r27/measure/buds.py        -> buds.png, buds-ruler.png, buds.log

The rim of the middle body, from the meeting point with the left neighbour (0) to the bud on top (1), unrolled: the way
round runs to the right, the distance from the middle of the body runs up. Real pixels of both flat pictures, so every
bud is a bump of its true size at its true place.

True picture (c = -1): the buds of the middle body are found exactly, by undoing the rule: a bud is carried onto the
middle body by an odd number of steps; where it is attached goes to the left meeting point alpha, its far tip goes to
the right meeting point -alpha. Its number: two steps of the rule double the way round, so the numbers are halvings.
Balls object: the bud at the fraction p/q sits at the turn 2 atan(p/q) from the left meeting point and is
k2 / (2 t (p^2 + q^2) - 1) wide (one line of arithmetic from the recipe; checked against the picture here).
"""
import os, sys
from fractions import Fraction
import numpy as np
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import ballkit as K

K2, T0 = 1.05, 1.40
ALPHA = (1 - np.sqrt(5)) / 2
LOG = open(os.path.join(HERE, 'buds.log'), 'w')


def say(s):
    print(s); LOG.write(s + '\n'); LOG.flush()


def true_buds(depth=7):
    """Buds of the middle body of c = -1: list of (theta, attach, tip). theta = the way round the rim by the rule's own
    count (two steps of the rule double it), 0 at the left meeting point, counted anticlockwise."""
    buds = [(Fraction(0), complex(ALPHA), complex(-np.sqrt(1 - ALPHA))), (Fraction(1, 2), complex(-ALPHA), complex(np.sqrt(1 - ALPHA)))]
    layer = [buds[1]]
    for _ in range(depth):
        nxt = []
        for th, a, tp in layer:
            wa, wt = 1 - np.sqrt(1 + a), 1 - np.sqrt(1 + tp)             # one step back onto the left neighbour, shifted by 1
            sa, st = np.sqrt(wa + 0j), np.sqrt(wt + 0j)
            if (sa * np.conj(st)).real < 0:
                st = -st
            for sg in (1, -1):
                A, Tp = sg * sa, sg * st
                nxt.append((th / 2 if A.imag < 0 else th / 2 + Fraction(1, 2), A, Tp))
        buds += nxt; layer = nxt
    return buds


def strip(inside, r0, r1, p0, p1, w, h, ss=2):
    """Unrolled picture: column = the turn psi (degrees, from the left meeting point over the top), row = distance r."""
    W, H = w * ss, h * ss
    psi = np.radians(p0 + (np.arange(W) + 0.5) * (p1 - p0) / W); r = r1 - (np.arange(H) + 0.5) * (r1 - r0) / H
    P, R = np.meshgrid(psi, r)
    return inside(-R * np.cos(P), R * np.sin(P)).reshape(h, ss, w, ss).mean((1, 3))


def frac_label(fr):
    return '%d/%d' % (fr.numerator, fr.denominator) if fr.denominator > 1 else '%d' % fr.numerator


def main():
    g = K.Grid('line')
    # ---- numbers
    tb = true_buds(7)
    quarter = sorted([(4 * (1 - th), a, tp) for th, a, tp in tb if Fraction(3, 4) <= th < 1] + [(Fraction(0), tb[0][1], tb[0][2])], key=lambda q: q[0])
    say('TRUE c = -1, middle body: buds between the left meeting point (0) and the top bud (1)')
    say('   number   where it is attached     turn psi (deg)   share of the way   length (attach to tip)')
    tr = {}
    for lam, a, tp in quarter:
        psi = np.degrees(np.arctan2(a.imag, -a.real)); tr[lam] = (psi, abs(tp - a), a, tp)
        if lam.denominator <= 16:
            say('   %-6s   %+.4f %+.4fi      %7.2f          %.3f              %.4f' % (frac_label(lam), a.real, a.imag, psi, psi / 90, abs(tp - a)))
    say('BALLS OBJECT (k2 = %.2f, t = %.2f), middle ball: buds between the left meeting point (0/1) and the top bud (1/1)' % (K2, T0))
    say('   fraction   turn psi (deg)   share of the way   diameter')
    ob = {}
    for q in range(1, 9):
        for p in range(0, q + 1):
            if np.gcd(p, q) == 1:
                fr = Fraction(p, q); psi = np.degrees(2 * np.arctan(p / q)); dia = K2 / (2 * T0 * (p * p + q * q) - 1); ob[fr] = (psi, dia)
    for fr in sorted(ob):
        if fr.denominator <= 5:
            say('   %-6s     %7.2f          %.3f              %.4f' % (frac_label(fr), ob[fr][0], ob[fr][0] / 90, ob[fr][1]))
    # check the formula against the list of balls: the ball that touches the middle ball at the fraction's place
    reps, _ = K.build(g, K.recipe_gens(2 * T0), 2 * T0, rho_min=5e-5); Bl = K.picture(reps, g, 2 * T0, k2=K2, r_min=3e-4); worst = 0.0
    for fr, (psi, dia) in ob.items():
        R = K2 / 2 + dia / 2; cx, cy = -R * np.cos(np.radians(psi)), R * np.sin(np.radians(psi))
        a = int(np.argmin((Bl[:, 0] - cx) ** 2 + (Bl[:, 1] - cy) ** 2)); worst = max(worst, abs(Bl[a, 3] - dia / 2), float(np.hypot(Bl[a, 0] - cx, Bl[a, 1] - cy)))
    say('   formula for place and size against the list of balls (%d fractions): largest difference %.2e' % (len(ob), worst))
    # check the true buds: where a bud is attached must land on alpha after an odd number of steps; a point 0.9 of the way to the tip must be inside
    worst = 0.0; bad = 0
    for lam, (psi, ln, a, tp) in tr.items():
        z = a; hit = 9.0
        for k in range(1, 40):
            z = z * z - 1
            if k % 2 == 1:
                hit = min(hit, abs(z - ALPHA))
        worst = max(worst, hit); zz = a + 0.9 * (tp - a); bad += int(not K.julia(np.array([zz.real]), np.array([zz.imag]), -1.0, 0.0, 2000)[0])
    say('   true buds (%d): the attach point lands on the left meeting point after an odd number of steps to within %.1e; 0.9 of the way to the tip is inside for all but %d' % (len(tr), worst, bad))
    say('sizes compared (true length / object diameter): top bud %.3f / %.3f; the bud halfway by count (true 1/2: %.4f at %.3f of the way; object 1/2: %.4f at %.3f of the way)'
        % (tr[Fraction(1)][1], ob[Fraction(1)][1], tr[Fraction(1, 2)][1], tr[Fraction(1, 2)][0] / 90, ob[Fraction(1, 2)][1], ob[Fraction(1, 2)][0] / 90))
    seq = [Fraction(1, 2 ** n) for n in range(1, 7)]
    say('toward the left meeting point, TRUE: number, distance along the rim from the meeting point (as turn x 0.618), length, length / distance')
    for lam in seq:
        psi, ln, a, tp = tr[lam]; dist = abs(a - ALPHA); say('   %-5s  %.5f  %.5f  %.3f' % (frac_label(lam), dist, ln, ln / dist))
    say('toward the left meeting point, OBJECT: fraction, distance from the meeting point, diameter, diameter / distance')
    for q in (2, 3, 4, 6, 8, 12, 16, 32):
        psi = 2 * np.arctan(1 / q); dist = K2 * np.sin(psi / 2); dia = K2 / (2 * T0 * (1 + q * q) - 1); say('   1/%-3d  %.5f  %.5f  %.3f' % (q, dist, dia, dia / dist))

    # ---- picture 1: the two rims unrolled, real pixels
    w, h = 1640, 538; p0, p1, r0, r1 = -9.0, 99.0, 0.44, 0.78
    ct = strip(lambda x, y: K.julia(x, y, -1.0, 0.0, 1500), r0, r1, p0, p1, w, h)
    co = strip(lambda x, y: K.inside_picture(x, y, 0 * x, g, 2 * T0, 60, K2) == 1, r0, r1, p0, p1, w, h)
    pad = 16; W = w + 2 * pad; H = 96 + 2 * (h + 86)
    im = Image.new('RGB', (W, H), (12, 14, 20)); d = ImageDraw.Draw(im)
    d.text((pad, 10), 'Where the buds sit: the rim of the middle body, unrolled', fill=(240, 240, 245), font=K.font(28))
    d.text((pad, 50), 'A walk along the rim from the meeting point with the left neighbour (0) to the bud on top (1). Every bud is drawn at its true place and true size.', fill=(200, 205, 215), font=K.font(17))
    X = lambda psi: pad + (psi - p0) / (p1 - p0) * w
    Yr = lambda y0, r: y0 + (r1 - r) / (r1 - r0) * h
    for row, (cov, head, col) in enumerate(((ct, 'True flat picture of c = -1: the buds sit at the HALVINGS  (1/2, then 1/4 and 3/4, then the eighths ...)', (72, 146, 240)),
                                            (co, 'Balls on balls: the buds sit at the FRACTIONS  (1/2, then 1/3 and 2/3, then 1/4 and 3/4, then the fifths ...)', (236, 138, 52)))):
        y0 = 96 + row * (h + 86)
        d.text((pad, y0), head, fill=col, font=K.font(21)); y0 += 34
        im.paste(Image.fromarray(K.paint(cov, fg=(232, 224, 200), bg=(22, 28, 44))), (pad, y0))
        f1, f2 = K.font(19), K.font(14)
        if row == 0:
            for lam, (psi, ln, a, tp) in tr.items():
                if lam.denominator <= 16 and 0 < lam < 1:
                    rr = abs(a); txt = frac_label(lam); f = f1 if lam.denominator <= 8 else f2
                    xx = X(psi); yy = Yr(y0, rr) + (10 if lam.denominator <= 8 else 8)
                    d.line([xx, Yr(y0, rr) + 2, xx, yy - 1], fill=(40, 60, 110), width=1)
                    d.text((xx - d.textlength(txt, font=f) / 2, yy), txt, fill=(30, 50, 100), font=f)
            for lam, txt in ((Fraction(0), '0  (the meeting point with the left neighbour)'), (Fraction(1), '1  (the bud on top)')):
                psi, ln, a, tp = tr[lam]; xx = X(psi); yy = y0 + h - 34
                d.line([xx, Yr(y0, abs(a)) + 3, xx, yy - 2], fill=(40, 60, 110), width=1)
                d.text((xx - 6 if lam == 0 else xx - 150, yy), txt, fill=(30, 50, 100), font=f1)
        else:
            for fr, (psi, dia) in ob.items():
                if fr.denominator <= 7 and 0 < fr < 1:
                    txt = frac_label(fr); f = f1 if fr.denominator <= 4 else f2
                    xx = X(psi); yy = Yr(y0, K2 / 2) + (10 if fr.denominator <= 4 else 8)
                    d.line([xx, Yr(y0, K2 / 2) + 2, xx, yy - 1], fill=(120, 60, 10), width=1)
                    d.text((xx - d.textlength(txt, font=f) / 2, yy), txt, fill=(110, 55, 10), font=f)
            for fr, txt in ((Fraction(0), '0  (the meeting point with the left neighbour)'), (Fraction(1), '1  (the bud on top)')):
                xx = X(ob[fr][0]); yy = y0 + h - 34
                d.line([xx, Yr(y0, K2 / 2) + 3, xx, yy - 2], fill=(120, 60, 10), width=1)
                d.text((xx - 6 if fr == 0 else xx - 150, yy), txt, fill=(110, 55, 10), font=f1)
            for lam in (Fraction(1, 4), Fraction(1, 2), Fraction(3, 4)):            # where the true picture has its buds, for the eye
                xx = X(tr[lam][0]); yy = Yr(y0, K2 / 2) + 46
                d.polygon([(xx, yy), (xx - 7, yy + 13), (xx + 7, yy + 13)], fill=(60, 120, 215))
                txt = 'true ' + frac_label(lam); d.text((xx - d.textlength(txt, font=f2) / 2, yy + 15), txt, fill=(40, 90, 180), font=f2)
        cap = ('Each new bud sits between two older ones, and the buds crowd right into the meeting point: the two bodies end in a point there.',
               'The bigger the bottom number of the fraction, the smaller the bud. Next to a big bud the rim stays almost bare: there two balls kiss, round against round. (Blue marks: where the true picture has its buds.)')[row]
        d.text((pad, y0 + h + 8), cap, fill=(200, 205, 215), font=K.font(17))
    im.save(os.path.join(HERE, 'buds.png')); say('wrote buds.png %s' % (im.size,))

    # ---- picture 2: the object's rim seen from the meeting point on the right: a ruler
    w2, h2 = 1640, 470; s0, s1 = -0.16, 1.16; z0 = -0.07; z1 = z0 + (s1 - s0) * h2 / w2; ss = 2
    sx = s0 + (np.arange(w2 * ss) + 0.5) * (s1 - s0) / (w2 * ss); sz = z1 - (np.arange(h2 * ss) + 0.5) * (z1 - z0) / (h2 * ss)
    SX, SZ = np.meshgrid(sx, sz); cov = (K.recipe(SX, 0 * SX, SZ, g, 2 * T0, 60) == 1).reshape(h2, ss, w2, ss).mean((1, 3))
    im = Image.new('RGB', (w2 + 2 * pad, h2 + 150), (12, 14, 20)); d = ImageDraw.Draw(im)
    d.text((pad, 10), 'Balls on balls, looked at from a meeting point: the rim is a ruler, and there is a bud at every fraction', fill=(240, 240, 245), font=K.font(26))
    im.paste(Image.fromarray(K.paint(cov, fg=(232, 224, 200), bg=(22, 28, 44))), (pad, 56))
    Xs = lambda s: pad + (s - s0) / (s1 - s0) * w2; yrim = 56 + (z1 - 0) / (z1 - z0) * h2
    for q in range(1, 8):
        for p in range(0, q + 1):
            if np.gcd(p, q) == 1:
                f = K.font(20 if q <= 4 else (15 if q <= 6 else 12)); txt = '%d/%d' % (p, q) if q > 1 else '%d' % p
                d.text((Xs(p / q) - d.textlength(txt, font=f) / 2, yrim + 6 + (0 if q <= 6 else 0)), txt, fill=(110, 55, 10), font=f)
    d.text((pad, 56 + h2 + 10), 'One whole number to the next. The bud at 1/2 is a quarter as wide as the bud at 0, the buds at 1/3 and 2/3 a ninth, at 1/4 and 3/4 a sixteenth.', fill=(200, 205, 215), font=K.font(17))
    d.text((pad, 56 + h2 + 36), 'The true flat picture has no such ruler: its buds are numbered by halvings, and there is never a bud at 1/3.', fill=(200, 205, 215), font=K.font(17))
    im.save(os.path.join(HERE, 'buds-ruler.png')); say('wrote buds-ruler.png %s' % (im.size,))
    # check of the caption: the buds on the ruler, from the list of balls in the object's own coordinates
    for q in (1, 2, 3, 4, 5):
        cx, cz = 1.0 / q, 1 / (4 * T0 * q * q); c = reps[:, :3].copy(); c[:, 0] -= np.round(c[:, 0] - cx)
        a = int(np.argmin((c[:, 0] - cx) ** 2 + (c[:, 2] - cz) ** 2 + c[:, 1] ** 2))
        say('   ruler: bud at 1/%d: diameter %.6f (1 / (2 t q^2) = %.6f), share of the bud at 0: %.4f (1/q^2 = %.4f)' % (q, 2 * reps[a, 3], 1 / (2 * T0 * q * q), 2 * reps[a, 3] * 2 * T0, 1 / q ** 2))


if __name__ == '__main__':
    main()

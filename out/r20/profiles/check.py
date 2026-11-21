"""Seconds-long checks of the wind rules, and point-by-point cuts.
python out/r19/me/check.py rules            -> flat plane exact, length squared, no jump, copy planes exact
python out/r19/me/check.py cuts <rule> ...  -> out/r19/me/cuts-<rule>.png : basilica, rabbit, dendrite, Siegel disc,
                                               each cut in the flat plane, in the plane at 60 degrees, in the plane
                                               at 30 degrees (half way), and across the x-axis
"""
import os, sys
import numpy as np
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, 'out', 'me', 'r16')); sys.path.insert(0, os.path.join(ROOT, 'out', 'r16', 'bench'))
import truth as T
import rules as R

SETS = [('basilica', (-1.0, 0.0, 0.0), 0.0), ('rabbit', (-0.122561, 0.744862, 0.0), 0.0),
        ('dendrite', (0.0, 1.0, 0.0), 0.0), ('siegel', (-0.390541, -0.586788, 0.0), 0.0)]


def member(F, X, Y, Z, c, steps):
    return T.member(F, X, Y, Z, c, steps)


def plane_cut(F, c, ang, half, n, steps, x0=0.0):
    """Cut through the x-axis by the plane turned ang degrees from the flat plane. Across: x, up: distance from axis."""
    a = np.radians(ang)
    u = np.linspace(x0 - half, x0 + half, n); s = np.linspace(half, -half, n)
    U, Sg = np.meshgrid(u, s)
    return member(F, U, Sg * np.cos(a), Sg * np.sin(a), c, steps)


def cross_cut(F, c, x0, half, n, steps):
    y = np.linspace(-half, half, n); z = np.linspace(half, -half, n)
    Y, Z = np.meshgrid(y, z)
    return member(F, np.full_like(Y, x0), Y, Z, c, steps)


def rules_check():
    rng = np.random.default_rng(1)
    for name in sys.argv[2:] or ['m_w3', 'm_w3lin', 'm_w3f', 'm_w5']:
        F = R.get(name)
        v = rng.normal(size=(3, 200000))
        X, Y, Z = F(*v)
        r2 = (v * v).sum(0)
        e_len = np.abs(np.sqrt(X * X + Y * Y + Z * Z) - r2).max()
        x, y = rng.normal(size=(2, 200000)); z = np.zeros_like(x)
        X, Y, Z = F(x, y, z)
        e_flat = max(np.abs(X - (x * x - y * y)).max(), np.abs(Y - 2 * x * y).max(), np.abs(Z).max())
        # copy plane at 60 degrees: the answer must lie in the flat plane and equal the flat square of the point turned there
        a = np.radians(60.0); s = rng.normal(size=200000)
        X, Y, Z = F(x, s * np.cos(a), s * np.sin(a))
        e_copy = max(np.abs(Z).max(), np.abs(X - (x * x - s * s)).max(), np.abs(Y - 2 * x * (-s)).max())
        # jump test: pairs a small gap apart
        out = []
        for gap in (1e-3, 1e-4, 1e-5, 1e-6):
            d = rng.normal(size=(3, 200000)); d *= gap / np.sqrt((d * d).sum(0))
            A = np.array(F(*v)); B = np.array(F(*(v + d)))
            out.append(float(np.sqrt(((A - B) ** 2).sum(0)).max() / gap))
        print(f'{name:9s} length squared err {e_len:.1e}  flat plane err {e_flat:.1e}  copy plane (60 deg) err {e_copy:.1e}  '
              f'largest move/gap at gaps 1e-3..1e-6: ' + ' '.join(f'{o:.1f}' for o in out))


def cuts():
    steps = 60; n = 420
    for name in sys.argv[2:]:
        F = R.get(name)
        cols = [('flat plane', 0.0), ('plane at 60 degrees', 60.0), ('half way, 30 degrees', 30.0), ('upright plane, 90 degrees', 90.0)]
        W = (len(cols) + 2) * (n + 8) + 8; H = len(SETS) * (n + 30) + 40
        im = Image.new('RGB', (W, H), (12, 13, 18)); dr = ImageDraw.Draw(im); f = T.font(15); fb = T.font(18)
        dr.text((8, 8), f'{name}: {R.RULES[name][1]}.  Point by point, {steps} steps. Cream = inside.', fill=(230, 230, 230), font=fb)
        for j, (tag, c, _) in enumerate(SETS):
            y0 = 40 + j * (n + 30)
            half = 1.75 if tag in ('basilica',) else 1.6
            for i, (lab, ang) in enumerate(cols):
                m = plane_cut(F, c, ang, half, n, steps)
                im.paste(Image.fromarray(T.shade(m, steps)), (8 + i * (n + 8), y0 + 20))
                dr.text((8 + i * (n + 8), y0), f'{tag}: {lab}', fill=(210, 210, 210), font=f)
            for k, x0 in enumerate((0.0, -0.3 if tag == 'basilica' else c[0])):
                i = len(cols) + k
                m = cross_cut(F, c, x0, 1.2, n, steps)
                im.paste(Image.fromarray(T.shade(m, steps)), (8 + i * (n + 8), y0 + 20))
                dr.text((8 + i * (n + 8), y0), f'{tag}: cut across the x-axis at x = {x0:.2f}', fill=(210, 210, 210), font=f)
        p = os.path.join(HERE, f'cuts-{name}.png'); im.save(p); print('wrote', p)


if __name__ == '__main__':
    {'rules': rules_check, 'cuts': cuts}[sys.argv[1]]()

"""Point-by-point cuts (no voxels) that show what a fold-before rule does to a Julia set.
    python out/r19/foldpre/stack.py <tag> <rule> [more rules]        tag: basilica | rabbit | dendrite
One row per rule: the upright cut through the x-axis (y = 0), the cut across the middle (x = 0), and the cone
that carries the copy of the flat plane (latitude L1, unrolled: across = longitude, up = distance from the centre)
beside the flat plane itself, for comparison. Crease directions are drawn as thin lines when the rule is a pole cap.
Writes out/r19/foldpre/stack-<tag>-<rules>.png"""
import os, sys
import numpy as np
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, 'out', 'r16', 'bench')); sys.path.insert(0, os.path.join(ROOT, 'out', 'me', 'r16'))
import truth as T
import rules as R

SETS = {'basilica': ((-1.0, 0.0, 0.0), 60, 1.75), 'rabbit': ((-0.122561, 0.744862, 0.0), 60, 1.5), 'dendrite': ((0.0, 1.0, 0.0), 24, 1.6),
        'sanmarco': ((-0.75, 0.0, 0.0), 60, 1.7)}
CREASE = {'g_p12': 12.0, 'g_p22': 22.0, 'g_p245': 24.4698, 'g_p30': 30.0, 'g_p45': 45.0, 'g_k12': 12.0, 'g_k245': 24.4698, 'g_mix': 24.4698}
S = 520


def mirror_lat(L):
    s0 = np.tan(np.radians(45 - L / 2)); return 90 - 2 * np.degrees(np.arctan(s0 * s0))


def plane(F, c, steps, o, u, v, half, n=S):
    a = np.linspace(-half, half, n); A, B = np.meshgrid(a, a[::-1])
    P = [o[k] + A * u[k] + B * v[k] for k in range(3)]
    return T.member(F, P[0], P[1], P[2], c, steps)


def cone(F, c, steps, lat, rmax, n=S):
    lon = np.linspace(-np.pi, np.pi, n); r = np.linspace(rmax, 0.0, n); LO, RR = np.meshgrid(lon, r); la = np.radians(lat)
    return T.member(F, RR * np.cos(la) * np.cos(LO), RR * np.cos(la) * np.sin(LO), RR * np.sin(la) + 0 * LO, c, steps)


def rays(im, half, lats, col):
    d = ImageDraw.Draw(im); cx = cy = S / 2; k = S / (2 * half)
    for L in lats:
        for sx in (1, -1):
            for sz in (1, -1):
                a = np.radians(L); x1 = cx + sx * half * 1.5 * np.cos(a) * k; y1 = cy - sz * half * 1.5 * np.sin(a) * k
                d.line([(cx, cy), (x1, y1)], fill=col, width=1)
    return im


if __name__ == '__main__':
    tag = sys.argv[1]; names = sys.argv[2:]
    c, steps, half = SETS[tag]
    cols = ['Upright cut through the x-axis (y = 0)', 'Cut across the middle (x = 0)', 'On the flat plane, unrolled (longitude across, distance up)',
            'On the cone that carries the copy, unrolled the same way']
    pad = 10; W = pad + len(cols) * (S + pad); H = 40 + len(names) * (S + 56)
    sheet = Image.new('RGB', (W, H), (12, 14, 20)); d = ImageDraw.Draw(sheet)
    d.text((pad, 8), f'{tag}, c = {c}, {steps} steps, point by point. Cream = inside. Orange lines: creases. Green lines: where the copy of the flat plane lies.',
           fill=(235, 235, 240), font=T.font(18))
    for i, nm in enumerate(names):
        F = R.get(nm); y0 = 40 + i * (S + 56)
        L = CREASE.get(nm); L1 = mirror_lat(L) if L else 45.0
        tiles = []
        t = Image.fromarray(T.shade(plane(F, c, steps, (0, 0, 0), (1, 0, 0), (0, 0, 1), half), steps))
        if L: rays(t, half, [L], (255, 150, 40)); rays(t, half, [L1], (90, 220, 120))
        tiles.append(t)
        t = Image.fromarray(T.shade(plane(F, c, steps, (0, 0, 0), (0, 1, 0), (0, 0, 1), half * 0.62), steps))
        if L: rays(t, half * 0.62, [L], (255, 150, 40)); rays(t, half * 0.62, [L1], (90, 220, 120))
        tiles.append(t)
        n0 = cone(F, c, steps, 0.0, half); n1 = cone(F, c, steps, L1, half)
        tiles.append(Image.fromarray(T.shade(n0, steps))); tiles.append(Image.fromarray(T.shade(n1, steps)))
        same = float(((n0 >= steps) == (n1 >= steps)).mean())
        lab = R.RULES[nm][1]
        d.text((pad, y0), f'{nm}: {lab}.' + (f'  Crease at {L:.1f}, copy of the flat plane at {L1:.1f} degrees.' if L else '  (last tile: cone at 45 degrees)')
               + f'  Flat plane and cone agree on {100 * same:.2f} % of points.', fill=(215, 220, 230), font=T.font(17))
        for j, t in enumerate(tiles):
            sheet.paste(t, (pad + j * (S + pad), y0 + 26))
            d.text((pad + j * (S + pad) + 4, y0 + 28), cols[j], fill=(255, 255, 255), font=T.font(14))
        print(nm, 'flat plane vs copy cone agree', round(100 * same, 3), '%', flush=True)
    out = os.path.join(HERE, f'stack-{tag}-' + '-'.join(names) + '.png'); sheet.save(out); print('wrote', out)

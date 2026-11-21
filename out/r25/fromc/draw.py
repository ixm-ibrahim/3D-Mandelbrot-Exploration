"""Round 25, fromc: pictures.

    python out/r25/fromc/draw.py cuts  NAME,NAME,...  [tag]        cuts (seconds): flat, tilted 45, upright through the
                                                                   x-axis, upright through the line 0 - meeting point
    python out/r25/fromc/draw.py solids NAME,NAME,... a|top [tag] [nd] [steps] [sets]   rough solids, one row per rule
    python out/r25/fromc/draw.py mandel NAME,NAME,... [tag]        cuts of the Mandelbrot solid (flat, 45, upright)
"""
import os, sys, time
import numpy as np
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import rules as R
M = R.M
SETS = {'b': ('c = -1', (-1.0, 0.0, 0.0)), 'r': ('rabbit', M.RABBIT), 's': ('c = -0.75', (-0.75, 0.0, 0.0)), 'd': ('Siegel disc', M.SIEGEL),
        'q': ('middle of the 1/4 bud', (0.28227139, 0.53006062, 0.0))}
CAMS = {'a': (0.45, 0.5, 1.0), 'top': (0.2, 1.0, 0.35)}


def cut_plane(rule, c, e1, e2, w, h, steps, L=1.8):
    u, s = np.meshgrid(np.linspace(-L, L, w), np.linspace(L * h / w, -L * h / w, h))
    P = [u * e1[i] + s * e2[i] for i in range(3)]
    return M.stay(rule, P[0], P[1], P[2], c[0], c[1], c[2], steps)


def cuts(names, tag='', sets='br'):
    rules = [R.get(n) for n in names]; w, h, steps, pad = 300, 220, 60, 8; f = M.font(15); f2 = M.font(12)
    cols = []
    for key in sets:
        sn, c = SETS[key]; a = R.alpha(complex(c[0], c[1])); ah = a / abs(a)
        cols += [(sn + ', flat cut', c, (1, 0, 0), (0, 1, 0)), (sn + ', cut tilted 45 about the x-axis', c, (1, 0, 0), (0, 0.7071, 0.7071)),
                 (sn + ', upright cut through the x-axis', c, (1, 0, 0), (0, 0, 1)),
                 (sn + ', upright cut through 0 and the meeting point', c, (ah.real, ah.imag, 0), (0, 0, 1))]
    W = pad + len(cols) * (w + pad); H = 30 + len(rules) * (h + 26)
    im = Image.new('RGB', (W, H), (12, 14, 20)); d = ImageDraw.Draw(im); t0 = time.time()
    for i, r in enumerate(rules):
        y = 30 + i * (h + 26); d.text((pad, y - 20), r.name + ': ' + r.label, fill=(235, 220, 170), font=f)
        for j, (lab, c, e1, e2) in enumerate(cols):
            x = pad + j * (w + pad)
            im.paste(Image.fromarray(M.shade(cut_plane(r, c, e1, e2, w, h, steps), steps)), (x, y)); d.text((x + 4, y + 2), lab, fill=(150, 160, 175), font=f2)
        print('cuts', r.name, '%.0f s' % (time.time() - t0)); sys.stdout.flush()
    path = os.path.join(HERE, 'cuts%s.png' % (('-' + tag) if tag else '')); im.save(path); print('wrote', path, im.size)


def solids(names, cam='a', tag='', nd=150, steps=28, sets='br', w=340, h=255):
    rules = [R.get(n) for n in names]
    path = os.path.join(HERE, 'solids%s-%s.png' % (('-' + tag) if tag else '', cam))
    M.julia_sheet(rules, path, sets=[SETS[k] for k in sets], w=w, h=h, nd=nd, steps=steps, cam=CAMS[cam],
                  title='Rough solids (%d blocks deep, %d steps), eye at %s' % (nd, steps, CAMS[cam]))
    print('wrote', path)


def mandel(names, tag=''):
    rules = [R.get(n) for n in names]; w, h, steps, pad = 320, 300, 50, 8; f = M.font(15); f2 = M.font(12)
    angs = [0.0, 45.0, 90.0]
    W = pad + len(angs) * (w + pad); H = 30 + len(rules) * (h + 26)
    im = Image.new('RGB', (W, H), (12, 14, 20)); d = ImageDraw.Draw(im); t0 = time.time()
    for i, r in enumerate(rules):
        y = 30 + i * (h + 26); d.text((pad, y - 20), r.name + ': ' + r.label, fill=(235, 220, 170), font=f)
        for j, a in enumerate(angs):
            x = pad + j * (w + pad)
            im.paste(Image.fromarray(M.shade(M.cut_axis(r, a, w, h, steps), steps)), (x, y))
            d.text((x + 4, y + 2), 'Mandelbrot solid, cut turned %g about the x-axis' % a, fill=(150, 160, 175), font=f2)
        print('mandel', r.name, '%.0f s' % (time.time() - t0)); sys.stdout.flush()
    path = os.path.join(HERE, 'mandel%s.png' % (('-' + tag) if tag else '')); im.save(path); print('wrote', path, im.size)


if __name__ == '__main__':
    a = sys.argv[1]; names = sys.argv[2].split(',')
    if a == 'cuts':
        cuts(names, sys.argv[3] if len(sys.argv) > 3 else '', sys.argv[4] if len(sys.argv) > 4 else 'br')
    elif a == 'solids':
        cam = sys.argv[3] if len(sys.argv) > 3 else 'a'; tag = sys.argv[4] if len(sys.argv) > 4 else ''
        nd = int(sys.argv[5]) if len(sys.argv) > 5 else 150; steps = int(sys.argv[6]) if len(sys.argv) > 6 else 28
        solids(names, cam, tag, nd, steps, sys.argv[7] if len(sys.argv) > 7 else 'br')
    else:
        mandel(names, sys.argv[3] if len(sys.argv) > 3 else '')

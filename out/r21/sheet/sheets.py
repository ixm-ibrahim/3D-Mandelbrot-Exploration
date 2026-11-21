"""Pictures for groups of rules.

    python out/r21/sheet/sheets.py cuts   <tag> name name ...     cuts of the basilica and the rabbit  -> cuts-<tag>.png
    python out/r21/sheet/sheets.py julia  <tag> name name ...     rough solids, small                  -> julia-<tag>.png
    python out/r21/sheet/sheets.py mandel <tag> name name ...     Mandelbrot cuts and solid, small     -> mandel-<tag>.png
    python out/r21/sheet/sheets.py juliaF / mandelF ...           the same at the library's full size
Names are rules of myrules.py, of the scout (fixed, lag25, ...) or of the bench (along, oneplane, lathe).
"""
import os, sys, time
import numpy as np
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import myrules as R
M = R.M

CUTS = [('basilica ACROSS, x = 0', 'x', (-1.0, 0.0, 0.0), 0.0), ('basilica ACROSS, x = -1', 'x', (-1.0, 0.0, 0.0), -1.0),
        ('basilica along 22.5', 'a', (-1.0, 0.0, 0.0), 22.5), ('basilica along 45', 'a', (-1.0, 0.0, 0.0), 45.0), ('basilica along 90', 'a', (-1.0, 0.0, 0.0), 90.0),
        ('rabbit along 22.5', 'a', M.RABBIT, 22.5), ('rabbit along 90', 'a', M.RABBIT, 90.0), ('rabbit ACROSS, x = 0', 'x', M.RABBIT, 0.0)]


def cuts_sheet(rules, path, s=176, steps=60):
    pad = 8; t0 = time.time(); W = pad + len(CUTS) * (s + pad); H = 40 + len(rules) * (s + 30)
    im = Image.new('RGB', (W, H), (12, 14, 20)); d = ImageDraw.Draw(im)
    d.text((pad, 8), 'Cuts of two Julia sets (%d steps). ACROSS = across the x-axis (y right, z up); along = a sheet through the x-axis' % steps, fill=(240, 240, 245), font=M.font(17))
    for i, r in enumerate(rules):
        y = 40 + i * (s + 30); d.text((pad, y), '%s: %s' % (r.name, r.label), fill=(235, 220, 170), font=M.font(14))
        for j, (nm, kind, c, a) in enumerate(CUTS):
            n = M.cut_across(r, a, s, steps, c=c, L=1.1) if kind == 'x' else M.cut_axis(r, a, s, s, steps, c=c, box=(-1.8, 1.8, -1.8, 1.8))
            x = pad + j * (s + pad); im.paste(Image.fromarray(M.shade(n, steps)), (x, y + 20)); d.text((x + 4, y + 22), nm, fill=(150, 160, 175), font=M.font(11))
        print('cuts', r.name, '%.0f s' % (time.time() - t0)); sys.stdout.flush()
    im.save(path); return path


if __name__ == '__main__':
    opt = dict(a.split('=') for a in sys.argv[1:] if '=' in a); argv = [a for a in sys.argv[1:] if '=' not in a]
    kind, tag, names = argv[0], argv[1], argv[2:]
    rules = [R.get(n) for n in names]
    if kind == 'cuts':
        cuts_sheet(rules, os.path.join(HERE, 'cuts-%s.png' % tag))
    elif kind == 'julia':
        M.julia_sheet(rules, os.path.join(HERE, 'julia-%s.png' % tag), w=236, h=177, nd=int(opt.get('nd', 128)), steps=int(opt.get('steps', 24)))
    elif kind == 'juliaF':
        M.julia_sheet(rules, os.path.join(HERE, 'julia-%s.png' % tag))
    elif kind == 'mandel':
        M.mandel_sheet(rules, os.path.join(HERE, 'mandel-%s.png' % tag), w=250, cw=200, ch=186, nd=128, steps=20, cut_steps=50)
    elif kind == 'mandelF':
        M.mandel_sheet(rules, os.path.join(HERE, 'mandel-%s.png' % tag))

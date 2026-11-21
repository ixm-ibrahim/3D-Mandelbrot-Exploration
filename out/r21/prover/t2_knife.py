"""Why does 'delay_cov' (covariant, so spun in exact arithmetic) not come out exactly spun on a computer?

    python out/r21/prover/t2_knife.py  ->  out/r21/prover/t2_knife.txt, t2_knife.png

Test: the cut along a sheet at 0 degrees (z = 0 exactly: no rounding can leave the page), the same cut with every c
lifted off the page by 1e-13, and the cut along the sheet at 22.5 degrees, at 40, 80 and 160 steps.
In exact arithmetic all three are the flat Mandelbrot set.
"""
import os, sys
import numpy as np
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, 'out', 'r21', 'lib')); sys.path.insert(0, HERE)
import mem as M, myrules as R

W, H = 420, 390
u, s = np.meshgrid(np.linspace(-2.1, 0.7, W), np.linspace(1.3, -1.3, H))
out = []


def say(t=''):
    print(t); sys.stdout.flush(); out.append(t)


def main():
    tiles = []; names = ('delay_cov', 'lag50_cov', 'lag25_cov', 'lathe_x')
    scout = {r.name: r for r in M.SCOUT}
    for steps in (40, 80, 160):
        flat = M.flat_stay(u, s, u, s, steps) >= steps
        say('%d steps: the flat Mandelbrot set holds %d of %d grid points' % (steps, flat.sum(), flat.size))
        for nm in names:
            r = R.BY[nm]
            a0 = M.mandel(r, u, s, 0 * u, steps) >= steps
            a1 = M.mandel(r, u, s, 0 * u + 1e-13, steps) >= steps
            a = np.radians(22.5); a2 = M.mandel(r, u, s * np.cos(a), s * np.sin(a), steps) >= steps
            say('  %-10s z = 0 exactly: lost %6d gained %4d | lifted by 1e-13: lost %6d gained %4d | sheet at 22.5: lost %6d gained %4d'
                % (nm, (flat & ~a0).sum(), (a0 & ~flat).sum(), (flat & ~a1).sum(), (a1 & ~flat).sum(), (flat & ~a2).sum(), (a2 & ~flat).sum()))
            if nm in ('delay_cov', 'lag50_cov') and steps in (40, 160):
                img = M.shade(np.where(a2, steps, 0), steps); img[flat & ~a2] = (200, 70, 60)
                tiles.append(('%s, sheet at 22.5, %d steps' % (nm, steps), img))
    # the scout's 'delay' (flat page as the fixed start): the rabbit's flat cycle, is it stable against a lift off the page?
    say()
    say("Does a small lift off the page die out? The rabbit, start points on the flat page lifted by h; share of the flat rabbit's points that stay (200 steps)")
    zr, zi = np.meshgrid(np.linspace(-1.6, 1.6, 300), np.linspace(1.2, -1.2, 225)); c = M.RABBIT
    fl = M.flat_stay(zr, zi, c[0], c[1], 200) >= 200
    for nm, r in [(n, scout[n]) for n in ('fixed', 'lag25', 'lag50', 'lag75', 'delay', 'first', 'own')] + [(n, R.BY[n]) for n in ('delay_cov', 'lag50_cov')] + [('along', M.bench('along'))]:
        row = []
        for h in (0.0, 1e-12, 1e-6, 1e-3):
            j = M.stay(r, zr, zi, 0 * zr + h, c[0], c[1], c[2], 200) >= 200
            row.append(100.0 * (j & fl).sum() / fl.sum())
        say('  %-10s h = 0: %6.2f%%   h = 1e-12: %6.2f%%   h = 1e-6: %6.2f%%   h = 1e-3: %6.2f%%' % (nm, *row))
    pad = 8; im = Image.new('RGB', (pad + len(tiles) * (W + pad), H + 40), (12, 14, 20)); d = ImageDraw.Draw(im)
    for i, (t, img) in enumerate(tiles):
        x = pad + i * (W + pad); d.text((x, 8), t, fill=(235, 220, 170), font=M.font(15)); im.paste(Image.fromarray(img), (x, 34))
    im.save(os.path.join(HERE, 't2_knife.png'))
    open(os.path.join(HERE, 't2_knife.txt'), 'w', encoding='utf-8').write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()

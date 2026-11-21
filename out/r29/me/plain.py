"""Round 29, the orchestrator's first look: what the plain recipe of Balls on balls gives when NOTHING keeps the two
spheres from cutting into each other (the user asked for the automatic rule to go). Flat cuts (picture z = 0) and
one cut across the chain, by the recipe alone (numpy, no page).

  python -B out/r29/me/plain.py      -> out/r29/me/plain-*.png, out/r29/me/plain.txt
"""
import os, sys
import numpy as np
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(HERE)), 'r28', 'me'))
from own import mine, K2
from PIL import Image, ImageDraw

# (size of the neighbours p, second sphere rho, grid, rounds)
SETS = [(100.0, 1.0, 0, 16), (120.0, 1.0, 0, 16), (120.0, 1.0, 0, 80), (150.0, 1.0, 0, 16), (150.0, 1.0, 0, 80),
        (200.0, 1.0, 0, 16), (200.0, 1.0, 0, 80), (300.0, 1.0, 0, 16), (300.0, 1.0, 0, 80), (150.0, 1.0, 2, 80),
        (150.0, 1.0, 1, 80), (80.0, 0.75, 0, 16), (80.0, 0.75, 0, 80), (150.0, 0.75, 0, 80), (300.0, 0.5, 0, 80)]


def t_plain(p):
    return 0.5 * (100.0 / p + 1)


def inside(x, y, z, p, rho, grid, rounds):
    # own.mine reads t from p with the 55.56 special case; none of these settings is near it
    return mine(x, y, z, p, rho, grid, rounds)


def cut(p, rho, grid, rounds, plane, n=520):
    half = K2 * (0.5 + p / 100.0) * 1.08
    xs = np.linspace(-half, half, n)
    hy = half * 0.62
    ys = np.linspace(hy, -hy, int(n * 0.62))
    X, Y = np.meshgrid(xs, ys)
    if plane == 'flat':
        ins = inside(X.ravel(), Y.ravel(), 0 * X.ravel(), p, rho, grid, rounds)
    else:                      # the plane through the chain that stands on the flat one
        ins = inside(X.ravel(), 0 * X.ravel(), Y.ravel(), p, rho, grid, rounds)
    return ins.reshape(X.shape)


if __name__ == '__main__':
    lines = []
    tiles = []
    for (p, rho, grid, rounds) in SETS:
        a = cut(p, rho, grid, rounds, 'flat')
        b = cut(p, rho, grid, rounds, 'up')
        share = float(a.mean())
        lines.append('size %6.1f, second sphere %5.1f %%, grid %d, depth %3d: inside share of the flat cut %.3f, of the cut across %.3f'
                     % (p, 100 * rho, grid, rounds, share, float(b.mean())))
        for name, m in (('flat', a), ('up', b)):
            im = Image.fromarray(np.where(m, 40, 235).astype(np.uint8), 'L').convert('RGB')
            d = ImageDraw.Draw(im)
            d.rectangle([0, 0, 330, 16], fill=(255, 255, 255))
            d.text((4, 2), 'size %g  second %g  grid %d  depth %d  %s' % (p, 100 * rho, grid, rounds, name), fill=(180, 0, 0))
            tiles.append(im)
    w, h = tiles[0].size
    cols = 4
    rows = (len(tiles) + cols - 1) // cols
    sheet = Image.new('RGB', (cols * w, rows * h), (255, 255, 255))
    for i, im in enumerate(tiles):
        sheet.paste(im, ((i % cols) * w, (i // cols) * h))
    half = len(tiles) // 2
    sheet.save(os.path.join(HERE, 'plain-all.png'))
    open(os.path.join(HERE, 'plain.txt'), 'w', encoding='utf-8', newline='\n').write('\n'.join(lines) + '\n')
    print('\n'.join(lines))

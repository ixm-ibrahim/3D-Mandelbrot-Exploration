"""The pictures of the notes, from the flat cuts (recomputed) and the kept solids (depth-*.npz).
    python compose.py   -> pinch-flat.png, pinch-solids.png, pinch-turn.png, compose.log
"""
import numpy as np
from PIL import Image
import pinchlib as PL, objs

TW, THh = 480, 347


def small(img, size=(TW, THh)):
    return np.asarray(Image.fromarray(img).resize(size, Image.LANCZOS))


def solid_tile(name, eye, size=(570, 428)):
    d = np.load(PL.os.path.join(PL.HERE, 'depth-%s-%s.npz' % (name, eye)))
    return small(PL.M.shade_solid(d['depth'], float(d['px'])), size)


def per100(x):
    return '%d of 100 parts wrong' % round(100 * x)


# ---- flat
tiles = []
for key in ('c1', 'rabbit'):
    T = PL.true_flat(PL.CS[key]); nm = PL.NAMES[key]
    tiles.append((small(PL.overlay(T, T)), 'The true flat picture, %s.' % nm))
    for obj, cap in (('abest', 'Two fitted moves, sphere inversions only: %s.'),
                     ('treeball', 'True layout, a ball for each body: %s.'),
                     ('tree', 'True layout, pointed bodies: %s.')):
        A = PL.flat_union(objs.get('%s-%s' % (obj, key))); ws = PL.wrong_share(A, T)
        print('flat %s-%s: wrong share %.3f' % (obj, key, ws))
        tiles.append((small(PL.overlay(A, T)), cap % per100(ws)))
PL.sheet(tiles, 4, PL.os.path.join(PL.HERE, 'pinch-flat.png'),
         title='Flat cuts against the true flat picture. Cream: right. Blue: only in the true picture. Orange: only in the built object.')

# ---- solids
tiles = []
for key in ('c1', 'rabbit'):
    nm = PL.NAMES[key]
    tiles.append((solid_tile('tree-%s' % key, 'a'), '%s: true layout, bodies pointed at both ends.' % nm))
    tiles.append((solid_tile('tree-%s' % key, 'top'), 'The same from a second eye: buds only round the flat picture.'))
    tiles.append((solid_tile('abest-%s' % key, 'a'), '%s: two fitted moves, each a chain of sphere inversions.' % nm))
PL.sheet(tiles, 3, PL.os.path.join(PL.HERE, 'pinch-solids.png'), title='Solids (first inside block on each line of sight, skin refined by halving).')

# ---- the turn
tiles = []
for eye, en in (('a', 'from the front'), ('end', 'nearly along the chain')):
    for obj, cap in (('tree-c1', 'No turn: buds in the flat plane only'), ('turn90-c1', 'A quarter turn at each step'), ('turn137.5-c1', 'A turn of 137.5 degrees at each step')):
        tiles.append((solid_tile(obj, eye), '%s, %s.' % (cap, en)))
PL.sheet(tiles, 3, PL.os.path.join(PL.HERE, 'pinch-turn.png'),
         title='c = -1: the stretch about the meeting point, given a turn about the chain. The buds swing out of the flat plane, some come loose, no new ones come.')
print('wrote pinch-flat.png, pinch-solids.png, pinch-turn.png')

"""Rough solids of a list of rules.

    python out/r25/pillow/solids.py <tag> <eye: a|top|below|side> <sets: m1,rab,...> <nd> <spec> <spec> ...
    spec as in cuts.py; a trailing ~ flips the rule upside down (0.25,1~)
"""
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import pil as P
import cuts as C
M = P.M

CAMS = {'a': (0.45, 0.5, 1.0), 'top': (0.2, 1.0, 0.35), 'below': (0.45, -0.5, 1.0), 'side': (1.0, 0.35, 0.3), 'under': (0.2, -1.0, 0.35)}
SETS = {'m1': ('c = -1', (-1.0, 0.0, 0.0)), 'rab': ('rabbit', M.RABBIT), 'm075': ('c = -0.75', (-0.75, 0.0, 0.0)), 'sie': ('Siegel disc', M.SIEGEL),
        'arab': ('rabbit, mirror image', (M.RABBIT[0], -M.RABBIT[1], 0.0)), 'air': ('airplane', (-1.754878, 0.0, 0.0))}


def get(spec):
    if spec.endswith('~'):
        r = C.get(spec[:-1]); return P.mirror(r, name=r.name + ' (upside down)')
    return C.get(spec)


if __name__ == '__main__':
    tag, eye, sets, nd = sys.argv[1], sys.argv[2], sys.argv[3].split(','), int(sys.argv[4])
    rules = [get(s) for s in sys.argv[5:]]
    w = 340; h = 255
    M.julia_sheet(rules, os.path.join(HERE, 'solids-%s-%s.png' % (tag, eye)), sets=[SETS[s] for s in sets], w=w, h=h, nd=nd, steps=30, cam=CAMS[eye],
                  title='Rough solids, eye at %s' % (CAMS[eye],))
    print('done', tag, eye)

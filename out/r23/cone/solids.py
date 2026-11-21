"""Rough solids.  python out/r23/cone/solids.py name eye key [key ...]     eye: a | top | side | y
bench names (oneplane, along, twoplane) may be mixed in with the keys of variants.py."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import conelib as L
import variants
M = L.M
EYES = {'a': (0.45, 0.5, 1.0), 'top': (0.2, 1.0, 0.35), 'side': (1.0, 0.45, 0.3), 'y': (0.25, 0.3, -1.0), 'up': (0.5, 0.25, 1.0)}


def get(k):
    if k in L.DIRS:
        return L.rule(k)
    return M.bench(k)


if __name__ == '__main__':
    name, eye = sys.argv[1], sys.argv[2]; keys = sys.argv[3:]
    steps = int(os.environ.get('STEPS', '30')); w = int(os.environ.get('W', '300')); nd = int(os.environ.get('ND', '200'))
    sets = L.SETS
    if os.environ.get('SETS'):
        sets = [s for s in L.SETS + [('dendrite, c = i', (0.0, 1.0, 0.0))] if any(t in s[0] for t in os.environ['SETS'].split(','))]
    M.julia_sheet([get(k) for k in keys], os.path.join(HERE, 'solids-%s-%s.png' % (name, eye)), sets=sets, w=w, h=int(w * 0.75), nd=nd, steps=steps, cam=EYES[eye],
                  title='Rough solids, %d steps, eye at %s' % (steps, EYES[eye]))
    print('done')

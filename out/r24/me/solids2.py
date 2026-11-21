"""Round 24 scout, part 3: is the roughness made by the blend, or does it belong to the idea?

The decisive comparison. R_t alone turns every angle truly (no blend, no squeeze anywhere) but its flat picture is
wrong; the blended rule has the exact flat picture and a squeezing zone beside it. If R_t alone gives clean bodies
and the blended one does not, the roughness is the blend's. If both are rough, it belongs to the idea.

    python out/r24/me/solids2.py a      (front eye)        python out/r24/me/solids2.py top
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, 'out', 'r21', 'lib')); sys.path.insert(0, os.path.join(ROOT, 'out', 'r23', 'me')); sys.path.insert(0, HERE)
import mem as M
import cone as C
import tri as T


def raw(t):
    return C.cone_rule(t, blend=False, name='raw %+.2f' % t, label='dial %.2f with NO blend (every angle true, flat picture wrong)' % t)


def main():
    tag = sys.argv[1] if len(sys.argv) > 1 else 'a'
    cam = {'a': (0.45, 0.5, 1.0), 'top': (0.2, 1.0, 0.35)}[tag]
    rules = [M.bench('oneplane'), raw(-0.268), T.cone(-0.268), raw(-0.5), T.tri_rule()]
    M.julia_sheet(rules, os.path.join(HERE, 'raw-vs-blend-%s.png' % tag), sets=[T.SETS[0], T.SETS[1]], w=420, h=315, nd=230, steps=30, cam=cam,
                  title='Rough solids, eye at %s' % (cam,))
    print('sheet', tag, 'done')


if __name__ == '__main__':
    main()

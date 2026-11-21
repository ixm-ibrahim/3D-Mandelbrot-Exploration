"""E1: walk round the x-axis on the circle through a bud of the flat picture; which places stay, and what did
each step do to them?   python out/r22/buds/e1_rings.py  -> rings.txt

Rings: g1 through the bud on top of the middle body (its centre needs 1 step to reach the x-axis), g2 through a side
bud of the left body (2 steps), g3 through a slanted bud of the middle body (3 steps), g4 a small bud of the right
body (4 steps). For every inside arc: where its centre is, how wide, and step by step which page was used, how far
the point was from that page, and how far from the x-axis it landed."""
import os, sys, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import budlib as B

N = 2880; STEPS = 80; NTR = 6
out = open(os.path.join(HERE, 'rings.txt'), 'w', encoding='utf-8')


def say(*a):
    s = ' '.join(str(t) for t in a); print(s); out.write(s + '\n'); out.flush()


def main():
    t0 = time.time(); phi = np.arange(N) * 2 * np.pi / N
    for cname, c in (('basilica', B.BASILICA), ('San Marco', B.SANMARCO)):
        fc = B.flat_centres(c[0])
        say('=' * 100); say('%s, c = %g. flat centres: %s' % (cname, c[0], {k: np.round(v, 4) for k, v in fc.items()}))
        for gi, g in enumerate(('g1', 'g2', 'g3', 'g4')):
            x0, rad = fc[g].real, abs(fc[g].imag)
            say('-' * 100); say('ring %s: x = %.4f, radius %.4f (flat bud centre needs %d step(s) to reach the x-axis)' % (g, x0, rad, gi + 1))
            x, y, z = np.full(N, x0), rad * np.cos(phi), rad * np.sin(phi)
            for name in B.RULES:
                ins = B.inside(name, x, y, z, c, STEPS); ar = B.arcs(ins)
                t = B.trace(name, x, y, z, c, NTR)
                off = np.array(t['off']); H = np.nanmax(off[:gi + 1], axis=0)       # farthest from its page during the steps to the axis
                hin = H[ins].max() if ins.any() else float('nan'); hout = H[~ins].min() if (~ins).any() else float('nan')
                say('  %-9s inside %5.1f%% of the ring, %d arc(s) | farthest from its page in the first %d step(s): inside points up to %.4f, outside points down to %.4f'
                    % (name, 100 * ins.mean(), len(ar), gi + 1, hin, hout))
                for ci, ln in sorted(ar, key=lambda a: -a[1])[:16]:
                    i = int(round(ci)) % N
                    steps = []
                    for k in range(NTR):
                        px, py, pz = (t['pos'][k + 1][j][i] for j in range(3))
                        steps.append('page %6.1f off %.4f -> x %7.4f, %.4f from axis' % (np.degrees(B.fold(t['page'][k][i])), t['off'][k][i], px, np.hypot(py, pz)))
                    say('      arc at %6.2f deg, width %5.2f deg' % (np.degrees(phi[i]), ln * 360.0 / N))
                    for k in range(min(NTR, gi + 3)):
                        say('          step %d: %s' % (k + 1, steps[k]))
                if len(ar) > 16:
                    say('      ... and %d smaller arcs, widths %s' % (len(ar) - 16, np.round(sorted([a[1] * 360.0 / N for a in ar])[:len(ar) - 16], 2)[-12:]))
            say('  (%.0f s)' % (time.time() - t0))


if __name__ == '__main__':
    main()

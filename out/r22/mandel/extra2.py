"""Two more side measurements.   python out/r22/mandel/extra2.py -> out/r22/mandel/extra2.txt
1. One plane with a c swung out of the flat page: does ANY start point stay? (If none does, no first step can save
   the orbit of c: that is why 'Along once' has one plane's Mandelbrot solid.)
2. The bench rule m_w3 (the lab's 'Wind, then square', whose Mandelbrot solid was never judged), asked the same
   questions as the others: arcs on the circles through the buds.
"""
import os, sys, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import mlib as L
M = L.M
lines = []


def say(s=''):
    print(s); sys.stdout.flush(); lines.append(s)


def part1():
    say('1. ONE PLANE, c = the middle of a bud swung out of the flat page: of 300,000 random start points (|x|, |y|, |z| < 1.5), how many stay 200 steps')
    rng = np.random.default_rng(21); v = rng.uniform(-1.5, 1.5, size=(300000, 3))
    for label, x0, rho in (('period-3 bud', -0.122561, 0.744862), ('big disc at -1, radius 0.2', -1.0, 0.2), ('heart, x = -0.12, radius 0.3', -0.12, 0.3)):
        row = []
        for deg in (0, 1, 2, 5, 8, 15, 30, 45, 90):
            a = np.radians(deg); c = (x0, rho * np.cos(a), rho * np.sin(a))
            n = int((M.stay(L.RULES['oneplane'], v[:, 0], v[:, 1], v[:, 2], *c, 200) >= 200).sum())
            mine = int(M.mandel(L.RULES['oneplane'], np.array([c[0]]), np.array([c[1]]), np.array([c[2]]), 200)[0] >= 200)
            row.append('%d:%d%s' % (deg, n, '*' if mine else ''))
        say('   %-28s tilt:start points that stay (* = the orbit of c itself stays): %s' % (label, '  '.join(row)))


def part2():
    say(); say('2. m_w3 (the lab\'s "Wind, then square"): c walked round the x-axis, 1,440 places, 600 steps; arcs as (middle, width) in degrees')
    try:
        r = M.bench('m_w3')
    except Exception as e:
        say('   could not load m_w3: %r' % (e,)); return
    f = M.flat_check(r, n=8000); say('   flat check: verdicts that differ M %d, basilica %d, rabbit %d, Siegel %d of %d' % (f['mandelbrot'], f['basilica'], f['rabbit'], f['siegel'], f['of']))
    for label, x0, rho in (('period-3 bud', -0.1226, 0.7449), ('period-4 bud', 0.2823, 0.5301), ('big disc at -1, radius 0.125', -1.0, 0.125), ('big disc at -1, radius 0.2', -1.0, 0.2),
                           ('bud at -1.3107, radius 0.04', -1.3107, 0.04), ('heart x = -0.12, radius 0.3', -0.12, 0.3), ('heart x = -0.12, radius 0.55', -0.12, 0.55)):
        x, y, z, phi = L.ring(x0, rho, 1440)
        ins = M.mandel(r, x, y, z, 600) >= 600; ins80 = M.mandel(r, x, y, z, 80) >= 80
        a = L.arcs(ins); a.sort(key=lambda t: -t[1])
        say('   %-30s inside %5.1f%% (at 80 steps %5.1f%%)  arcs %3d: %s' % (label, 100 * ins.mean(), 100 * ins80.mean(), len(a), ', '.join('(%.1f, %.2f)' % (c * 0.25, w * 0.25) for c, w in a[:8])))


if __name__ == '__main__':
    t0 = time.time(); part1(); part2(); say(); say('(%.0f s)' % (time.time() - t0))
    open(os.path.join(HERE, 'extra2.txt'), 'w', encoding='utf-8').write('\n'.join(lines) + '\n')

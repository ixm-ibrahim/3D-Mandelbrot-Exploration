"""Along's slanted page (45 degrees): is the flat picture there a body or a film?   python out/r22/mandel/slant.py -> slant.txt
1. The cut along the page at 45 degrees against the flat set, at 80, 300 and 1000 steps (and the upright page, for comparison).
2. One orbit started exactly in the slanted page: how far it stands from that page, step by step.
3. Lift test: the flat-inside places of the slanted cut moved 1e-9, 1e-6, 1e-3 sideways: how many are still inside.
"""
import os, sys, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import mlib as L
M = L.M
lines = []


def say(s=''):
    print(s); sys.stdout.flush(); lines.append(s)


def main():
    t0 = time.time(); r = L.RULES['along']
    u, s = np.meshgrid(np.linspace(-2.1, 0.7, 420), np.linspace(1.3, -1.3, 390))
    say('1. ALONG: the cut along a page against the flat set (420 x 390 places)')
    for deg in (45.0, 90.0, 0.0):
        a = np.radians(deg)
        for steps in (80, 300, 1000):
            fl = M.flat_stay(u, s, u, s, steps) >= steps
            cu = M.mandel(r, u, s * np.cos(a), s * np.sin(a), steps) >= steps
            say('   page at %2.0f, %4d steps: flat set holds %d, the cut holds %d, verdicts that differ %d (flat-inside places lost %d)' % (deg, steps, fl.sum(), cu.sum(), (fl != cu).sum(), (fl & ~cu).sum()))
    say(); say('2. ALONG: orbits of c started exactly in the slanted page: distance of the orbit from that page (largest so far) after 5, 10, 20, 30, 40, 60, 100, 200 steps')
    for nm, cx, rho in (('middle of the top bud', -0.122561, 0.744862), ('middle of the period-5 bud', -0.504340, 0.562766), ('disc at -1, radius 0.2', -1.0, 0.2), ('heart, radius 0.3', -0.12, 0.3)):
        a = np.radians(45.0); pts, page, ns = L.trace('along', cx, rho * np.cos(a), rho * np.sin(a), 200)
        d = np.abs(pts[:, 0, 2] * np.cos(a) - pts[:, 0, 1] * np.sin(a)); run = np.fmax.accumulate(np.nan_to_num(d))
        say('   %-28s %s  %s' % (nm, ' '.join('%.1e' % run[k] for k in (5, 10, 20, 30, 40, 60, 100, 200)), 'stays' if ns[0] >= 200 else 'leaves after %d' % ns[0]))
    say(); say('3. LIFT TEST (300 steps): the flat-inside places of a cut, moved sideways out of the page by a small distance: how many are still inside')
    fl = M.flat_stay(u, s, u, s, 300) >= 300; U, S = u[fl], s[fl]
    for nm, key, deg in (('along, slanted page', 'along', 45.0), ('along, upright page', 'along', 90.0), ('along, flat page', 'along', 0.0), ('pulled plane, upright page', 'evc', 90.0), ('one plane, flat page', 'oneplane', 0.0)):
        a = np.radians(deg); row = []
        for h in (0.0, 1e-9, 1e-6, 1e-3, 1e-2):
            y, z = S * np.cos(a) - h * np.sin(a), S * np.sin(a) + h * np.cos(a)
            row.append('%g: %d' % (h, int((M.mandel(L.RULES[key], U, y, z, 300) >= 300).sum())))
        say('   %-28s of %d flat-inside places, still inside when lifted by %s' % (nm, U.size, ', '.join(row)))
    say(); say('(%.0f s)' % (time.time() - t0))
    open(os.path.join(HERE, 'slant.txt'), 'w', encoding='utf-8').write('\n'.join(lines) + '\n')


if __name__ == '__main__':
    main()

"""The two buds that sit ON the x-axis (the big disc at -1 and the bud at -1.3107), and along's route to its ragged skin.
    python out/r22/mandel/axisbuds.py  -> out/r22/mandel/axisbuds.txt

A. c on a circle round the x-axis inside the bud, tilted 0, 5, 10, 20, 30, 45, 60, 80, 90 degrees out of the flat page:
   stays or leaves, the first steps written own>used (the page the orbit point lies in > the page it is squared
   about, degrees from the flat page), and where the orbit ends.
B. 'along' only: c walked from the flat page to the slanted page (0 to 45 degrees) on four circles; at each stop
   the length of the cycle the orbit settles on (0 = it never repeats, x = it leaves), and the pages its points lie in.
"""
import os, sys, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import mlib as L
STEPS = 600; lines = []


def say(s=''):
    print(s); sys.stdout.flush(); lines.append(s)


def part_a():
    say('A. THE ORBIT OF c ON A CIRCLE ROUND THE x-AXIS INSIDE A BUD THAT SITS ON THE AXIS. %d steps. Steps written own>used.' % STEPS)
    for label, x0, rho in (('big disc at -1 (the orbit hops between two spots), circle of radius 0.2', -1.0, 0.2),
                           ('bud at -1.3107 (four spots), circle of radius 0.04', -1.3107, 0.04)):
        say(); say(' ' + label)
        for key in ('lathe', 'oneplane', 'wake', 'evc', 'along'):
            say('  %s (%s)' % (key, L.LAB[key]))
            for deg in (0, 5, 10, 20, 30, 45, 60, 80, 90):
                a = np.radians(deg); pts, page, ns = L.trace(key, x0, rho * np.cos(a), rho * np.sin(a), STEPS)
                per, kind = L.fate(pts, ns, STEPS)
                own = (np.arctan2(pts[:-1, 0, 2], pts[:-1, 0, 1]) * L.DEG) % 180; used = (page[:, 0] * L.DEG) % 180
                first = ' '.join('%.0f>%.0f' % (o, u) for o, u in zip(own[:8], used[:8]) if np.isfinite(o))
                if ns[0] >= STEPS:
                    off = np.abs(L.fold(np.radians(own[-64:] - used[-64:]))) * L.DEG
                    h = np.hypot(pts[-65:-1, 0, 1], pts[-65:-1, 0, 2]).max()
                    end = 'STAYS, %s%s, off its page by up to %.0f, at most %.3f from the x-axis' % (kind[0], (' of length %d' % per[0]) if per[0] else '', off.max(), h)
                else:
                    end = 'leaves after %d steps' % ns[0]
                say('   tilt %2d: %-66s | %s' % (deg, end, first))


def part_b():
    say(); say('B. ALONG: c walked from the flat page (0) to the slanted page (45), every 1.5 degrees. Cycle length at each stop (0 = never repeats in 600 steps, x = leaves, ~ = nearly settled):')
    for label, x0, rho in (('heart, x = -0.12, radius 0.55', -0.12, 0.55), ('big disc at -1, radius 0.2', -1.0, 0.2), ('big disc at -1, radius 0.24', -1.0, 0.24),
                           ('bud at -1.3107, radius 0.04', -1.3107, 0.04), ('period-3 bud, radius 0.7449', -0.122561, 0.744862)):
        deg = np.arange(0, 45.01, 1.5); a = np.radians(deg)
        pts, page, ns = L.trace('along', np.full(a.size, x0), rho * np.cos(a), rho * np.sin(a), STEPS)
        per, kind = L.fate(pts, ns, STEPS)
        row = ' '.join('x' if k == 'out' else ('0' if k == 'cloud' else ('~%d' % p if k == 'near' else '%d' % p)) for p, k in zip(per, kind))
        say('   %-30s %s' % (label, row))
        # how long do the leaving ones take, and how far off their page are the staying ones
        lv = ns[ns < STEPS]
        if lv.size:
            say('   %-30s the ones that leave take %d to %d steps (median %d)' % ('', lv.min(), lv.max(), np.median(lv)))


if __name__ == '__main__':
    t0 = time.time(); part_a(); part_b(); say(); say('(%.0f s)' % (time.time() - t0))
    open(os.path.join(HERE, 'axisbuds.txt'), 'w', encoding='utf-8').write('\n'.join(lines) + '\n')

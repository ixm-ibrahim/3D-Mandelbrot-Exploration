"""Where should "Orbit steps the trap reads" start? python out/r6/colour/reachzoom.py <page> <reach> [<reach> ...]

For each value: the twelve equation set-ups of the acceptance list at Balanced, and zoomed in 2 and 8 times, with the
dial at that value (label reach<value>). Prints how much the colours of the same places move when zooming in.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import scenes as s

page = sys.argv[1]
for reach in sys.argv[2:]:
    label = 'reach' + reach
    todo = [(n, j + " C.reach = %s;" % reach) for n, j in s.ACCEPT if n.split('-')[1] != 'k' and n.split('-')[-1] in ('qB', 'z2', 'z8')]
    if '--measure-only' not in sys.argv:
        s.shoot(page, label, (), extra=todo)
    tot = {'z2': [0, 0, 0, 0], 'z8': [0, 0, 0, 0]}
    for sn, _ in s.SUBJECTS[:3]:
        for un, _ in s.SETUPS:
            base = s.load(label, 'a-%s-%s-qB' % (sn, un)); line = '%-3s %-8s' % (sn, un)
            for vn in ('z2', 'z8'):
                m = s.measure(base, s.load(label, 'a-%s-%s-%s' % (sn, un, vn)), s.ZOOM[vn])
                line += '  %s %5.1f %5.1f %3.0f%%' % (vn, m[0], m[2], m[1])
                t = tot[vn]; t[0] = max(t[0], m[0]); t[1] += m[0]; t[2] = max(t[2], m[1]); t[3] += 1
            print(line)
    print('dial at %s: ' % reach + '; '.join('%s worst %.1f, average %.1f, worst hue share %.0f%%' % (k, v[0], v[1] / v[3], v[2]) for k, v in tot.items()))

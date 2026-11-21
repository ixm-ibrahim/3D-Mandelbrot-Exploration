"""Walk c round the x-axis on circles through buds of the flat Mandelbrot set, and say where the orbit of c ends up.
    python out/r22/mandel/circles.py  -> out/r22/mandel/circles.txt

For each rule and circle (1,440 places, 600 steps): the inside stretches (arcs) with their middle and width in
degrees; of the orbits that stay, how many settle on a cycle (and its length), how many never repeat; for those that
stay, how far the orbit points stand from the page they are squared about (median angle over the last 100 steps),
and how far the orbit is from lying in ONE page through the x-axis.
"""
import os, sys, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import mlib as L

N = 1440; STEPS = 600
CIRCLES = [('period-3 bud, middle -0.1226 + 0.7449i (a round ball would cover about 14 degrees)', -0.1226, 0.7449),
           ('period-4 bud, middle 0.2823 + 0.5301i', 0.2823, 0.5301),
           ('big disc at -1, circle of radius 0.05', -1.0, 0.05), ('big disc at -1, radius 0.125', -1.0, 0.125), ('big disc at -1, radius 0.2', -1.0, 0.2),
           ('big disc at -1, radius 0.24 (the flat disc ends at 0.25)', -1.0, 0.24),
           ('bud at -1.3107, radius 0.02', -1.3107, 0.02), ('bud at -1.3107, radius 0.04 (the flat bud ends near 0.058)', -1.3107, 0.04),
           ('heart, x = -0.12, radius 0.3', -0.12, 0.3), ('heart, x = -0.12, radius 0.55 (the flat heart ends near 0.63)', -0.12, 0.55)]


def main():
    t0 = time.time(); lines = []
    def say(s=''):
        print(s); sys.stdout.flush(); lines.append(s)
    say('ORBIT OF c, c WALKED ROUND THE x-AXIS: %d places on each circle, %d steps. Angles in degrees, 0 = the flat page.' % (N, STEPS))
    say('arcs: (middle, width). cycle lengths: length:count. off-page: median angle between an orbit point\'s own page and the page it is squared about, last 100 steps.')
    say('one-page: 0 means all the last 100 orbit points lie in one page through the x-axis; 1 means they are spread over all pages.')
    keep = {}
    for label, x0, rho in CIRCLES:
        say(); say(label)
        x, y, z, phi = L.ring(x0, rho, N)
        for key in ('lathe', 'oneplane', 'wake', 'evc', 'along'):
            pts, page, ns = L.trace(key, x, y, z, STEPS)
            ins = ns >= STEPS; per, kind = L.fate(pts, ns, STEPS)
            a = L.arcs(ins); a.sort(key=lambda t: -t[1])
            txt = ', '.join('(%.1f, %.2f)' % (c * 360.0 / N, w * 360.0 / N) for c, w in a[:8]) + (' ... %d more' % (len(a) - 8) if len(a) > 8 else '')
            cyc = {}
            for p, kd in zip(per[ins], kind[ins]):
                nm = ('%d' % p) if kd == 'cycle' else ('~%d' % p if kd == 'near' else 'never repeats'); cyc[nm] = cyc.get(nm, 0) + 1
            # last 100 steps of the staying orbits
            tail = pts[-101:-1][:, ins]; pg = page[-100:][:, ins]
            own = np.arctan2(tail[..., 2], tail[..., 1]); off = np.abs(L.fold(own - pg)) * L.DEG
            rr = np.hypot(tail[..., 1], tail[..., 2]); wgt = rr ** 2
            # spread over pages: 1 - |mean of the doubled-angle unit vectors weighted by distance from the axis squared|
            m1 = (wgt * np.cos(2 * own)).sum(0) / np.maximum(wgt.sum(0), 1e-300); m2 = (wgt * np.sin(2 * own)).sum(0) / np.maximum(wgt.sum(0), 1e-300)
            spread = 1 - np.hypot(m1, m2)
            say('  %-9s inside %5.1f%%  arcs %3d: %s' % (key, 100 * ins.mean(), len(a), txt))
            if ins.any():
                say('            ends: %s | off-page median %.2f (largest %.2f) | one-page median %.3f (largest %.3f)'
                    % (', '.join('%s:%d' % kv for kv in sorted(cyc.items(), key=lambda kv: -kv[1])[:6]), np.median(np.median(off, 0)), np.max(np.median(off, 0)), np.median(spread), np.max(spread)))
            keep['%s|%s' % (label[:12], key)] = (ins, per)
        say('  (%.0f s)' % (time.time() - t0))
    open(os.path.join(HERE, 'circles.txt'), 'w', encoding='utf-8').write('\n'.join(lines) + '\n')


if __name__ == '__main__':
    main()

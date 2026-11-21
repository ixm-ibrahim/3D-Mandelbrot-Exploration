"""The orbit of single c's, step by step, and how near the orbit comes back to the middle.
    python out/r22/mandel/orbits.py  -> out/r22/mandel/orbits.txt

A. c = the middle of the period-3 bud, tilted out of the flat page by 0, 1, 2, 5, 10, 20, 30, 45, 60, 80, 90 degrees:
   does the orbit stay, when does it leave, which page each of the first steps was squared about, how far the point
   stood from that page, and where the orbit ends.
B. The bud's size in three directions (through its middle): along the x-axis, away from the x-axis, and sideways
   (round the x-axis), for the bud standing in each page where a rule has one.
C. The 'return distance': on the settled cycle, how near the orbit comes to the middle (0, 0, 0), as c is moved off
   the middle of the bud by s within the page and by s sideways.
"""
import os, sys, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import mlib as L

C3 = (-0.122561, 0.744862)          # middle of the period-3 bud of the flat Mandelbrot set
KEYS = ('lathe', 'oneplane', 'wake', 'evc', 'along')
STEPS = 600
lines = []


def say(s=''):
    print(s); sys.stdout.flush(); lines.append(s)


def tilt(c2, deg):
    a = np.radians(deg); return c2[0], c2[1] * np.cos(a), c2[1] * np.sin(a)


def part_a():
    say('A. THE ORBIT OF c = middle of the period-3 bud, tilted out of the flat page. %d steps.' % STEPS)
    say('   own = the page the orbit point lies in; used = the page it is squared about; both as turns in degrees from the flat page (0..180).')
    say('   Each step is written own>used. "ends": cycle length, and how far (largest, degrees) its points stand from the page they are squared about.')
    for key in KEYS:
        say(); say('  %s (%s)' % (key, L.LAB[key]))
        for deg in (0, 1, 2, 5, 10, 20, 30, 45, 60, 80, 90):
            cx, cy, cz = tilt(C3, deg)
            pts, page, ns = L.trace(key, cx, cy, cz, STEPS)
            per, kind = L.fate(pts, ns, STEPS)
            own = (np.arctan2(pts[:-1, 0, 2], pts[:-1, 0, 1]) * L.DEG) % 180; used = (page[:, 0] * L.DEG) % 180
            first = ' '.join('%.0f>%.0f' % (o, u) for o, u in zip(own[:9], used[:9]) if np.isfinite(o))
            if ns[0] >= STEPS:
                off = np.abs(L.fold(np.radians(own[-64:] - used[-64:]))) * L.DEG
                rmin = np.nanmin(np.linalg.norm(pts[-65:-1, 0], axis=1))
                end = 'STAYS, %s %s, off its page by up to %.1f, comes back to %.3f from the middle' % (kind[0], ('of length %d' % per[0]) if per[0] else '', off.max(), rmin)
            else:
                end = 'leaves after %d steps' % ns[0]
            say('   tilt %2d: %-42s | %s' % (deg, end, first))


def extent(key, centre, direction, smax=0.3, n=1200):
    """How far the inside reaches from the centre along +direction and -direction (first place that is outside)."""
    s = np.linspace(0, smax, n); out = []
    for sg in (1, -1):
        P = [centre[i] + sg * s * direction[i] for i in range(3)]
        ins = L.M.mandel(L.RULES[key], P[0], P[1], P[2], 300) >= 300
        out.append(s[np.argmin(ins)] if not ins.all() else smax)
    return out


def part_b():
    say(); say('B. THE SIZE OF THE PERIOD-3 BUD through its middle, in three directions (reach to each side; 300 steps). The flat bud: about 0.094 each way.')
    say('   sideways = round the x-axis, as a length (and as an angle in degrees). round = sideways reach / mean of the two in-page reaches.')
    for key in KEYS:
        for deg in ((0,) if key in ('oneplane', 'wake', 'lathe') else (0, 90) if key == 'evc' else (0, 45, 90)):
            a = np.radians(deg); c = tilt(C3, deg)
            ex = extent(key, c, (1, 0, 0)); er = extent(key, c, (0, np.cos(a), np.sin(a)))
            # sideways: along the circle
            n = 2400; d = np.linspace(0, np.radians(60), n); side = []
            for sg in (1, -1):
                ins = L.M.mandel(L.RULES[key], np.full(n, c[0]), C3[1] * np.cos(a + sg * d), C3[1] * np.sin(a + sg * d), 300) >= 300
                side.append(d[np.argmin(ins)] if not ins.all() else np.radians(60))
            sw = [C3[1] * t for t in side]; inpage = np.mean(ex + er)
            say('   %-9s bud in the page at %2d: along x %.3f / %.3f | away from the axis %.3f / %.3f | sideways %.3f / %.3f (%.1f / %.1f degrees) | round %.2f'
                % (key, deg, ex[0], ex[1], er[0], er[1], sw[0], sw[1], np.degrees(side[0]), np.degrees(side[1]), np.mean(sw) / inpage))


def part_c():
    say(); say('C. HOW NEAR THE ORBIT COMES BACK TO THE MIDDLE (smallest distance from 0 on the last 64 points), c moved by s off the middle of the period-3 bud.')
    say('   "-" = the orbit has left. In the flat picture the bud ends where this distance reaches about 0.3 x ... (see NOTES).')
    S = (0.002, 0.005, 0.01, 0.02, 0.03, 0.05, 0.07, 0.09, 0.12, 0.16)
    say('   s:                                  ' + ' '.join('%6.3f' % s for s in S))
    for key in KEYS:
        for deg in ((0,) if key in ('oneplane', 'wake', 'lathe') else (0, 90) if key == 'evc' else (0, 45, 90)):
            a = np.radians(deg)
            for nm in ('in the page (away from axis)', 'sideways'):
                row = []
                for s in S:
                    if nm == 'sideways':
                        b = a + s / C3[1]; c = (C3[0], C3[1] * np.cos(b), C3[1] * np.sin(b))
                    else:
                        c = (C3[0], (C3[1] + s) * np.cos(a), (C3[1] + s) * np.sin(a))
                    pts, page, ns = L.trace(key, *c, STEPS)
                    row.append('%6.3f' % np.nanmin(np.linalg.norm(pts[-65:-1, 0], axis=1)) if ns[0] >= STEPS else '     -')
                say('   %-9s page %2d %-28s %s' % (key, deg, nm, ' '.join(row)))


if __name__ == '__main__':
    t0 = time.time(); part_a(); part_b(); part_c(); say(); say('(%.0f s)' % (time.time() - t0))
    open(os.path.join(HERE, 'orbits.txt'), 'w', encoding='utf-8').write('\n'.join(lines) + '\n')

"""How round are the buds of each Mandelbrot solid?   python out/r22/mandel/roundness.py -> out/r22/mandel/roundness.txt
For three buds of the flat set (periods 3, 4, 5) and each page in which a rule has the bud: the reach of the inside
from the bud's middle along the x-axis (both ways), away from the x-axis, and sideways (round the x-axis, both ways),
300 steps. round = sideways reach / mean in-page reach (1 = a ball, 0 = a film, large = a rib or ring).
"""
import os, sys, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import mlib as L
import importlib.util
_s = importlib.util.spec_from_file_location('mandel_rules', os.path.join(HERE, 'myrules.py'))
R = importlib.util.module_from_spec(_s); _s.loader.exec_module(R)
M = L.M
BUDS = [('period 3', (-0.122561, 0.744862)), ('period 4', (0.282271, 0.530061)), ('period 5', (-0.504340, 0.562766))]
RULES = [('oneplane', L.RULES['oneplane'], (0,)), ('wake', L.RULES['wake'], (0,)), ('evc', L.RULES['evc'], (0, 90)),
         ('along', L.RULES['along'], (0, 45, 90)), ('flip', R.get('flip'), (0,))]
lines = []


def say(s=''):
    print(s); sys.stdout.flush(); lines.append(s)


def reach(rule, pts_of_s, smax, n=1500, steps=300):
    s = np.linspace(0, smax, n); P = pts_of_s(s)
    ins = M.mandel(rule, P[0], P[1], P[2], steps) >= steps
    return s[np.argmin(ins)] if not ins.all() else smax


def main():
    t0 = time.time()
    say('ROUNDNESS OF THE BUDS OF THE MANDELBROT SOLID (reach of the inside from the bud\'s middle, 300 steps)')
    for bn, (bx, br) in BUDS:
        say(); say('%s bud, middle %.4f + %.4fi' % (bn, bx, br))
        for key, rule, pages in RULES:
            for deg in pages:
                a = np.radians(deg); o = np.ones(1500)
                xp = reach(rule, lambda s: (bx + s, br * np.cos(a) * o, br * np.sin(a) * o), 0.3)
                xm = reach(rule, lambda s: (bx - s, br * np.cos(a) * o, br * np.sin(a) * o), 0.3)
                ro = reach(rule, lambda s: (bx * o, (br + s) * np.cos(a), (br + s) * np.sin(a)), 0.3)
                sp = reach(rule, lambda s: (bx * o, br * np.cos(a + s / br), br * np.sin(a + s / br)), 0.6)
                sm = reach(rule, lambda s: (bx * o, br * np.cos(a - s / br), br * np.sin(a - s / br)), 0.6)
                inp = (xp + xm + ro) / 3
                say('   %-9s page %2d: along x %.3f / %.3f, away from the axis %.3f | sideways %.4f / %.4f (%.1f degrees each way) | round %.2f'
                    % (key, deg, xp, xm, ro, sp, sm, np.degrees(sp / br), sp / inp if inp > 0 else float('nan')))
    say(); say('(%.0f s)' % (time.time() - t0))
    open(os.path.join(HERE, 'roundness.txt'), 'w', encoding='utf-8').write('\n'.join(lines) + '\n')


if __name__ == '__main__':
    main()

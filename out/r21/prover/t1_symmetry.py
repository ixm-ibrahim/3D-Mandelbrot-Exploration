"""Numeric tests of Claim S and of its Julia version (NOTES.md, parts 1 and 2).

    python out/r21/prover/t1_symmetry.py  ->  out/r21/prover/t1_symmetry.txt

For every rule: verdicts are compared between a test point and the same point (a) turned by a random angle round the
x-axis, (b) mirrored in the flat page (z -> -z), (c) mirrored in the upright page (y -> -y), (d) turned half a turn.
"""
import os, sys, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, 'out', 'r21', 'lib')); sys.path.insert(0, HERE)
import mem as M, myrules as R

N, STEPS = 40000, 40
rng = np.random.default_rng(11)
ang = rng.uniform(0, 2 * np.pi, N); co, si = np.cos(ang), np.sin(ang)
C = rng.uniform([-2.1, -1.3, -1.3], [0.7, 1.3, 1.3], size=(N, 3))
V = rng.uniform([-1.8, -1.3, -1.3], [1.8, 1.3, 1.3], size=(N, 3))


def rot(p):
    return p[:, 0], co * p[:, 1] - si * p[:, 2], si * p[:, 1] + co * p[:, 2]


def mz(p):
    return p[:, 0], p[:, 1], -p[:, 2]


def my(p):
    return p[:, 0], -p[:, 1], p[:, 2]


def half(p):
    return p[:, 0], -p[:, 1], -p[:, 2]


def col(p):
    return p[:, 0], p[:, 1], p[:, 2]


def pct(a, b):
    return 100.0 * float((a != b).mean())


def mandel_row(r):
    m = M.mandel(r, *col(C), STEPS) >= STEPS
    return [100 * m.mean()] + [pct(m, M.mandel(r, *T(C), STEPS) >= STEPS) for T in (rot, mz, my, half)]


def julia_row(r, c):
    j = M.stay(r, *col(V), c[0], c[1], c[2], STEPS) >= STEPS
    return [100 * j.mean()] + [pct(j, M.stay(r, *T(V), c[0], c[1], c[2], STEPS) >= STEPS) for T in (rot, mz, my, half)]


def family_row(r, c):
    """Turn the start point AND c together: a covariant recipe must give 0."""
    j = M.stay(r, *col(V), c[0], c[1], c[2], STEPS) >= STEPS
    cy, cz = co * c[1] - si * c[2], si * c[1] + co * c[2]
    return pct(j, M.stay(r, *rot(V), c[0], cy, cz, STEPS) >= STEPS)


def main():
    np.seterr(all='ignore')
    out = []
    def say(s=''):
        print(s); sys.stdout.flush(); out.append(s)
    scout = {r.name: r for r in M.SCOUT}
    rules = [scout[n] for n in ('fixed', 'lag25', 'lag50', 'lag75', 'delay', 'first', 'own')] + \
            [R.BY[n] for n in ('delay_cov', 'lag50_cov', 'lag25_cov', 'twist', 'twist8', 'delay_twist', 'csheet_flat', 'csheet_own', 'csheet_twist')] + [M.bench('along')]
    say('%d test points, %d steps. Every number is the share (in %%) of test points whose verdict changes.' % (N, STEPS))
    say()
    say('THE MANDELBROT SOLID')
    say('%-13s %7s | %8s %8s %8s %8s' % ('rule', 'inside', 'turned', 'z->-z', 'y->-y', 'half turn'))
    t0 = time.time()
    for r in rules:
        v = mandel_row(r); say('%-13s %6.2f%% | %8.3f %8.3f %8.3f %8.3f' % (r.name, *v))
    say('(%.0f s)' % (time.time() - t0)); say()
    for nm, c in (('THE BASILICA, c = -1 (c ON the x-axis)', (-1.0, 0.0, 0.0)), ('THE RABBIT (c in the flat page, OFF the x-axis)', M.RABBIT)):
        say(nm)
        say('%-13s %7s | %8s %8s %8s %8s | %s' % ('rule', 'inside', 'turned', 'z->-z', 'y->-y', 'half turn', 'start and c turned together'))
        for r in rules:
            v = julia_row(r, c); say('%-13s %6.2f%% | %8.3f %8.3f %8.3f %8.3f | %8.3f' % (r.name, *v, family_row(r, c)))
        say('(%.0f s)' % (time.time() - t0)); say()
    # a c that is off the x-axis and off the flat page: mirror in c's OWN sheet (here the sheet at 35 degrees)
    th = np.radians(35.0); c35 = (M.RABBIT[0], M.RABBIT[1] * np.cos(th), M.RABBIT[1] * np.sin(th))
    say('THE RABBIT TURNED 35 DEGREES (c off the flat page): start points mirrored in the sheet of c')
    def mc(p):                                               # mirror in the sheet at 35 degrees
        y, z = p[:, 1], p[:, 2]; c2, s2 = np.cos(2 * th), np.sin(2 * th)
        return p[:, 0], c2 * y + s2 * z, s2 * y - c2 * z
    for r in rules:
        j = M.stay(r, *col(V), *c35, STEPS) >= STEPS
        say('%-13s inside %6.2f%% | mirrored in the sheet of c: %8.3f' % (r.name, 100 * j.mean(), pct(j, M.stay(r, *mc(V), *c35, STEPS) >= STEPS)))
    say()
    # is the rabbit of 'csheet' the one-plane rule's rabbit? and the basilica: which convention gives what
    say('THE SHEET OF c: Julia sets against the one-plane rule and the lathe (verdicts that differ, of %d)' % N)
    for nm, c in (('basilica', (-1.0, 0.0, 0.0)), ('rabbit', M.RABBIT)):
        ref = {k: M.stay(r, *col(V), *c, STEPS) >= STEPS for k, r in (('oneplane', M.bench('oneplane')), ('lathe', M.bench('lathe')))}
        for rn in ('csheet_flat', 'csheet_own'):
            j = M.stay(R.BY[rn], *col(V), *c, STEPS) >= STEPS
            say('%-9s %-12s differs from the one-plane rule in %6d, from the lathe in %6d' % (nm, rn, int((j != ref['oneplane']).sum()), int((j != ref['lathe']).sum())))
    say()
    # along: the count 8 is the symmetry of its fixed data (sin 4 phi): quarter turn and eighth turn
    say("'along' (bench): the basilica turned by a quarter turn / by 45 degrees / by 22.5 degrees")
    al = M.bench('along'); j = M.stay(al, *col(V), -1.0, 0.0, 0.0, STEPS) >= STEPS
    for deg in (90.0, 45.0, 22.5):
        a = np.radians(deg); T = (V[:, 0], np.cos(a) * V[:, 1] - np.sin(a) * V[:, 2], np.sin(a) * V[:, 1] + np.cos(a) * V[:, 2])
        say('  turned %5.1f: %6.3f%% of verdicts change' % (deg, pct(j, M.stay(al, *T, -1.0, 0.0, 0.0, STEPS) >= STEPS)))
    m = M.mandel(al, *col(C), STEPS) >= STEPS
    for deg in (90.0, 45.0, 22.5):
        a = np.radians(deg); T = (C[:, 0], np.cos(a) * C[:, 1] - np.sin(a) * C[:, 2], np.sin(a) * C[:, 1] + np.cos(a) * C[:, 2])
        say('  Mandelbrot solid turned %5.1f: %6.3f%% of verdicts change' % (deg, pct(m, M.mandel(al, *T, STEPS) >= STEPS)))
    open(os.path.join(HERE, 't1_symmetry.txt'), 'w', encoding='utf-8').write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()

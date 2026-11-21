"""Extra, unfriendly measurements on the rules under judgment.   python out/r21/judge/hostile.py > out/r21/judge/hostile.txt

 1. SAME AS THE ONE-PLANE RULE?  Rabbit and basilica on the 120^3 grid at 80 steps: how many verdicts differ from the
    one-plane rule's, and from along's. A rule whose rabbit is the one-plane rabbit has not "cured" anything.
 2. FLOATING BODIES.  Rabbit on a 160^3 grid (cube -1.5..1.5, cell 0.019) at 80 steps: pieces of 200 cells or more,
    each with its share of the volume and its GAP to the nearest other inside cell. Bodies that meet in a point have
    a gap of about one cell; a gap of several cells is a body that floats free.
 3. SIEGEL DISC, San Marco: inside count on the 120^3 grid at 30, 80, 200, 500 steps (a slow leak shows here).
 4. c JUST OFF THE x-AXIS (still in the flat page): c = -1 + 0.03i, -1 + 0.1i, -0.75 + 0.1i. Inside count at 30, 80,
    200 steps, number of specks (pieces under 50 cells) and their share at 80 steps.
 5. THE RABBIT TURNED OUT OF THE PAGE: c = rabbit turned 10, 30, 45, 90 degrees round the x-axis. Inside count at 80
    steps. (The user's test 1 asks nothing here; it shows what the Mandelbrot solid is made of off the flat page.)
"""
import os, sys
import numpy as np
from scipy import ndimage
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import myrules as J
M = J.M
BAS = (-1.0, 0.0, 0.0); N = 120
names = [r.name for r in J.RULES]


def grid(n=N, lx=1.8, ly=1.5):
    xs = np.linspace(-lx, lx, n); ys = np.linspace(-ly, ly, n)
    return np.meshgrid(xs, ys, ys, indexing='ij')


G = grid()
print('1. VERDICTS THAT DIFFER on the 120^3 grid at 80 steps (of 1,728,000; in brackets: as a share of the rule\'s own inside count)')
ref = {}
for nm in ('oneplane', 'along'):
    r = J.get(nm); ref[nm] = {s: M.stay(r, *G, *c, 80) >= 80 for s, c in (('basilica', BAS), ('rabbit', M.RABBIT))}
print('%-22s | %-34s | %-34s' % ('rule', 'rabbit: vs one-plane, vs along', 'basilica: vs one-plane, vs along'))
for nm in names:
    r = J.get(nm); cells = []
    for s, c in (('rabbit', M.RABBIT), ('basilica', BAS)):
        m = M.stay(r, *G, *c, 80) >= 80; tot = max(int(m.sum()), 1)
        cells.append('%7d (%5.1f%%) %7d (%5.1f%%)' % ((m != ref['oneplane'][s]).sum(), 100.0 * (m != ref['oneplane'][s]).sum() / tot,
                                                      (m != ref['along'][s]).sum(), 100.0 * (m != ref['along'][s]).sum() / tot))
    print('%-22s | %-34s | %-34s' % (nm, *cells)); sys.stdout.flush()

print('\n2. FLOATING BODIES of the rabbit, 160^3 grid on the cube -1.5..1.5 (cell 0.0189), 80 steps.')
print('   For each piece of 200 cells or more: share of the volume, gap to the nearest other inside cell, where its middle is.')
n2 = 160; xs = np.linspace(-1.5, 1.5, n2); cell = xs[1] - xs[0]; G2 = np.meshgrid(xs, xs, xs, indexing='ij')
for nm in ('along', 'oneplane', 'sheet.evc005e70k16', 'alongmem.c_wake1', 'alongmem.c_wake2', 'span.c_lag10', 'frame.area_1_px'):
    r = J.get(nm); m = M.stay(r, *G2, *M.RABBIT, 80) >= 80
    lab, k = ndimage.label(m, structure=np.ones((3, 3, 3))); sz = np.bincount(lab.ravel()); sz[0] = 0; tot = int(m.sum())
    big = [i for i in np.argsort(sz)[::-1] if sz[i] >= 200]; small = int(sum(sz[i] for i in range(1, k + 1) if sz[i] < 200))
    print('%-22s inside %d cells, %d pieces in all, %d of 200 cells or more; %.2f%% of the volume in smaller pieces' % (nm, tot, k, len(big), 100.0 * small / max(tot, 1)))
    for i in big[:8]:
        if len(big) == 1:
            print('      piece of %5.1f%%: the only big piece' % (100.0 * sz[i] / tot)); continue
        d = ndimage.distance_transform_edt(~(m & (lab != i)), sampling=cell)
        gap = float(d[lab == i].min()); cm = [float(g[lab == i].mean()) for g in G2]
        print('      piece of %5.1f%%: gap %.3f (%.1f cells), middle at (%.2f, %.2f, %.2f)' % (100.0 * sz[i] / tot, gap, gap / cell, *cm))
    sys.stdout.flush()

print('\n3. SIEGEL DISC and SAN MARCO, 120^3 grid: inside count at 30 / 80 / 200 / 500 steps (kept from 30 to 500)')
for nm in names:
    r = J.get(nm); out = []
    for c in (M.SIEGEL, (-0.75, 0.0, 0.0)):
        n = M.stay(r, *G, *c, 500); a = [(n >= s).sum() for s in (30, 80, 200, 500)]
        out.append('%6d %6d %6d %6d (%5.1f%%)' % (*a, 100.0 * a[3] / max(a[0], 1)))
    print('%-22s | Siegel %s | San Marco %s' % (nm, *out)); sys.stdout.flush()

print('\n4. c JUST OFF THE x-AXIS, in the flat page. 120^3 grid: inside at 30 / 80 / 200 steps (kept 30 -> 200), specks at 80 steps (pieces under 50 cells: count, share of volume)')
CS = [('-1 + 0.03i', (-1.0, 0.03, 0.0)), ('-1 + 0.1i', (-1.0, 0.1, 0.0)), ('-0.75 + 0.1i', (-0.75, 0.1, 0.0))]
for nm in names:
    r = J.get(nm); out = []
    for cn, c in CS:
        n = M.stay(r, *G, *c, 200); a = [int((n >= s).sum()) for s in (30, 80, 200)]
        lab, k = ndimage.label(n >= 80, structure=np.ones((3, 3, 3))); sz = np.bincount(lab.ravel())[1:]
        out.append('%s: %6d %6d %6d (%5.1f%%) specks %4d, %5.2f%%' % (cn, *a, 100.0 * a[2] / max(a[0], 1), int((sz < 50).sum()), 100.0 * sz[sz < 50].sum() / max(a[1], 1)))
    print('%-22s | %s' % (nm, ' | '.join(out))); sys.stdout.flush()

print('\n5. THE RABBIT TURNED OUT OF THE PAGE by 0 / 10 / 30 / 45 / 90 degrees: inside count at 80 steps on the 120^3 grid')
for nm in names:
    r = J.get(nm); out = []
    for t in (0.0, 10.0, 30.0, 45.0, 90.0):
        a = np.radians(t); c = (M.RABBIT[0], M.RABBIT[1] * np.cos(a), M.RABBIT[1] * np.sin(a))
        out.append('%6d' % int((M.stay(r, *G, *c, 80) >= 80).sum()))
    print('%-22s | %s' % (nm, ' '.join(out))); sys.stdout.flush()

"""Judge, re-measurement 4: the orbit of c (Mandelbrot solid).  -> j4_mandel.txt"""
import os, sys, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import jlib as L
M = L.M
t0 = time.time(); out = open(os.path.join(HERE, 'j4_mandel.txt'), 'w', encoding='utf-8')


def say(*a):
    s = ' '.join(str(t) for t in a); print(s); out.write(s + '\n'); out.flush()


R = L.rules(); rng = np.random.default_rng(4)
c3 = complex(-0.122561, 0.744862)                      # middle of the top bud (period 3)

say('== A. the top bud\'s middle swung round the x-axis: 1,440 places, 600 steps')
a = np.arange(1440) * 2 * np.pi / 1440
cx = np.full(1440, c3.real); cy = c3.imag * np.cos(a); cz = c3.imag * np.sin(a)
for name, r in R.items():
    ar = L.arcs(M.mandel(r, cx, cy, cz, 600) >= 600)
    say('%-9s %2d arcs: %s' % (name, len(ar), ' '.join('%.2f@%.0f' % (t[1], t[0]) for t in sorted(ar))))
say('  %.0f s' % (time.time() - t0))

say('\n== B. "along once" against one plane: 2,000,000 random c in the box, 80 steps')
P = rng.uniform([-2.1, -1.3, -1.3], [0.7, 1.3, 1.3], size=(2000000, 3))
a1 = M.mandel(R['oneplane'], P[:, 0], P[:, 1], P[:, 2], 80) >= 80
a2 = M.mandel(R['once'], P[:, 0], P[:, 1], P[:, 2], 80) >= 80
d = a1 != a2
say('one plane keeps %d, along once %d, verdicts differ %d' % (a1.sum(), a2.sum(), d.sum()))
if d.any():
    q = P[d]; say('  the differing c: distance from the x-axis %.2f..%.2f, tilt %s' % (np.hypot(q[:, 1], q[:, 2]).min(), np.hypot(q[:, 1], q[:, 2]).max(), np.round(np.degrees(np.arctan2(np.abs(q[:, 2]), np.abs(q[:, 1]))), 0)))
Q = rng.uniform([-2.1, -1.3, -0.15], [0.7, 1.3, 0.15], size=(1500000, 3))
b1 = M.mandel(R['oneplane'], Q[:, 0], Q[:, 1], Q[:, 2], 80) >= 80; b2 = M.mandel(R['once'], Q[:, 0], Q[:, 1], Q[:, 2], 80) >= 80
say('slab within 0.15 of the flat page, 1,500,000 c: one plane keeps %d, verdicts differ %d' % (b1.sum(), (b1 != b2).sum()))
say('  %.0f s' % (time.time() - t0))

say('\n== C. along against the flat set spun round the x-axis: 60,000 random c, 600 steps')
P2 = P[:60000]
al = M.mandel(R['along'], P2[:, 0], P2[:, 1], P2[:, 2], 600) >= 600
sp = M.flat_stay(P2[:, 0], np.hypot(P2[:, 1], P2[:, 2]), P2[:, 0], np.hypot(P2[:, 1], P2[:, 2]), 600) >= 600
op = M.mandel(R['oneplane'], P2[:, 0], P2[:, 1], P2[:, 2], 600) >= 600
say('along keeps %d, the spun flat set %d, both %d, only along %d, only spun %d | one plane keeps %d (in the spun set: %d)' % (al.sum(), sp.sum(), (al & sp).sum(), (al & ~sp).sum(), (sp & ~al).sum(), op.sum(), (op & sp).sum()))
a80 = M.mandel(R['along'], P2[:, 0], P2[:, 1], P2[:, 2], 80) >= 80
say('along at 80 steps: %d (still leaking: %d lost by 600)' % (a80.sum(), a80.sum() - al.sum()))
say('  %.0f s' % (time.time() - t0))

say('\n== D. pulled plane: its upright cut against the flat Mandelbrot set (700 x 480 places, 200 steps)')
u, s = np.meshgrid(np.linspace(-2.1, 0.7, 700), np.linspace(1.3, -1.3, 480))
up = M.mandel(R['pulled'], u, 0 * s, s, 200) >= 200; fl = M.flat_stay(u, s, u, s, 200) >= 200
dd = up != fl
say('differ at %d of %d places; the differing places are within %.3f of the x-axis' % (dd.sum(), dd.size, np.abs(s[dd]).max() if dd.any() else 0))
for ang in (22.5, 45.0, 67.5):
    aa = np.radians(ang)
    cut = M.mandel(R['pulled'], u, s * np.cos(aa), s * np.sin(aa), 200) >= 200
    say('  cut along the page turned %.1f: %d places inside (flat set: %d)' % (ang, cut.sum(), fl.sum()))

say('\n== E. is the top bud a ball? reach sideways (out of the flat page) against reach along x, through the bud\'s middle, 300 steps')


def reach(rule, base, direction, hi=0.3, n=3001, steps=300):
    sgrid = np.linspace(-hi, hi, n); q = base[None] + sgrid[:, None] * direction[None]
    ins = M.mandel(rule, q[:, 0], q[:, 1], q[:, 2], steps) >= steps; mid = n // 2
    if not ins[mid]:
        return 0.0
    i = mid
    while i > 0 and ins[i - 1]:
        i -= 1
    j = mid
    while j < n - 1 and ins[j + 1]:
        j += 1
    return sgrid[j] - sgrid[i]


base = np.array([c3.real, c3.imag, 0.0])
for name, r in R.items():
    wx = reach(r, base, np.array([1.0, 0, 0])); wz = reach(r, base, np.array([0, 0, 1.0]))
    say('%-9s along x %.4f, sideways %.4f, sideways / along x %.2f' % (name, wx, wz, wz / wx if wx else float('nan')))
basu = np.array([c3.real, 0.0, c3.imag])
for name in ('pulled', 'along'):
    wx = reach(R[name], basu, np.array([1.0, 0, 0])); wz = reach(R[name], basu, np.array([0, 1.0, 0]))
    say('%-9s the same bud standing upright: along x %.4f, sideways %.4f, ratio %.2f' % (name, wx, wz, wz / wx if wx else float('nan')))

say('\n== F. one plane: a c lifted by 0.0001 off the page; height of the third orbit point (the one that returns to the middle) / the lift')
for name in ('oneplane', 'along', 'lathe'):
    r = R[name]; lift = 1e-4
    x, y, z = np.array([c3.real]), np.array([c3.imag]), np.array([lift]); C3 = (c3.real, c3.imag, lift)
    p = (x, y, z); st = tuple(r.init(1)); hs = []
    for k in range(3):
        X, Y, Z, st = r.step(*p, st, k, *(np.array([t]) for t in C3)); st = tuple(st)
        p = (X + C3[0], Y + C3[1], Z + C3[2]); hs.append(p[2][0] / lift)
    say('%-9s heights of the next three orbit points / lift of c: %s' % (name, ' '.join('%.2f' % h for h in hs)))

say('\n== G. one plane with the top bud\'s middle tilted: does ANY start point stay? 300,000 random starts, 200 steps')
S = rng.uniform([-1.8, -1.5, -1.5], [1.8, 1.5, 1.5], size=(300000, 3))
for tilt in (0.0, 1.0, 2.0, 5.0, 20.0):
    t = np.radians(tilt); cc = (c3.real, c3.imag * np.cos(t), c3.imag * np.sin(t))
    n1 = (M.stay(R['oneplane'], S[:, 0], S[:, 1], S[:, 2], *cc, 200) >= 200).sum()
    oc = M.mandel(R['oneplane'], np.array([cc[0]]), np.array([cc[1]]), np.array([cc[2]]), 600)[0]
    say('tilt %4.1f: %6d start points stay; the orbit of c itself stays %d of 600 steps' % (tilt, n1, oc))
say('done %.0f s' % (time.time() - t0))

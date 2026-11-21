"""Judge, re-measurement 1: the bud census, the thrown-in buds, buds on a bud.  -> j1_buds.txt"""
import os, sys, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import jlib as L
M = L.M
t0 = time.time(); out = open(os.path.join(HERE, 'j1_buds.txt'), 'w', encoding='utf-8')


def say(*a):
    s = ' '.join(str(t) for t in a); print(s); out.write(s + '\n'); out.flush()


R = L.rules(); C = L.BAS; N = 2880; STEPS = 80
# bud centres of the flat basilica, found here as preimages of 0 (not copied from the reports)
g1 = np.sqrt(complex(-np.sqrt(2) + 1))                  # top bud of the middle body: z^2 - 1 = -sqrt 2
g2 = -np.sqrt(1 + g1)                                    # side bud of the left body
g3 = np.sqrt(1 + g2)
g4 = np.sqrt(1 + g3)
say('bud centres from preimages: g1 %s g2 %s g3 %s g4 %s' % tuple('(%.4f, %.4f)' % (abs(g.real) if i == 2 else g.real, abs(g.imag)) for i, g in enumerate((g1, g2, g3, g4))))
RINGS = [('g1', 0.0, abs(g1.imag)), ('g2', g2.real, abs(g2.imag)), ('g3', abs(g3.real), abs(g3.imag)), ('g4', abs(g4.real), abs(g4.imag))]

say('\n== A. ring census, basilica, %d places, %d steps: number of arcs and their widths' % (N, STEPS))
for rn, x0, rad in RINGS:
    x, y, z, deg = L.ring(x0, rad, N)
    for name, r in R.items():
        ins = M.stay(r, x, y, z, *C, STEPS) >= STEPS
        a = L.arcs(ins)
        w = sorted(round(t[1], 1) for t in a)
        first = ' '.join('%.1f@%.1f' % (t[1], t[0]) for t in sorted(a)[:9] if t[0] <= 100)
        say('%s x=%.4f rad=%.4f %-9s arcs %3d  widths %s   | in the first quarter: %s' % (rn, x0, rad, name, len(a), sorted(set(w)), first))
    say('  %.0f s' % (time.time() - t0))

say('\n== B. the one-step law on g1: is "inside" the same as "closer to its first page than a fixed distance"? (along, oneplane)')
x, y, z, deg = L.ring(0.0, abs(g1.imag), N); phi = np.radians(deg)
for name, psi in (('oneplane', 0 * phi), ('along', phi - np.sin(4 * phi) / 4)):
    ins = M.stay(R[name], x, y, z, *C, STEPS) >= STEPS
    off = abs(g1.imag) * np.abs(np.sin(phi - psi))
    say('%-9s inside: farthest from its page %.4f | outside: nearest to its page %.4f' % (name, off[ins].max(), off[~ins].min()))

say('\n== C. a thrown-in bud of along on g2: find the arc near 27 degrees, follow its middle two steps')
x, y, z, deg = L.ring(g2.real, abs(g2.imag), N)
ins = M.stay(R['along'], x, y, z, *C, STEPS) >= STEPS
a = [t for t in L.arcs(ins) if 20 < t[0] < 35]
say('arcs of along between 20 and 35 degrees on g2:', a)
if a:
    d0 = np.radians(a[0][0]); p = (np.array([g2.real]), np.array([abs(g2.imag) * np.cos(d0)]), np.array([abs(g2.imag) * np.sin(d0)]))
    phi0 = d0; psi0 = phi0 - np.sin(4 * phi0) / 4
    say('start turn %.2f deg, squared about the page at %.2f deg, %.4f off it' % (np.degrees(phi0), np.degrees(psi0), abs(g2.imag) * abs(np.sin(phi0 - psi0))))
    for k in range(3):
        p = L.one(R['along'], *p, C)
        say('  after step %d: x %.4f, %.4f from the x-axis, turn %.2f deg' % (k + 1, p[0][0], np.hypot(p[1][0], p[2][0]), np.degrees(np.arctan2(p[2][0], p[1][0]))))

say('\n== D. buds ON a bud: ring round the STALK of the big top bud of the middle body (stalk = the y direction)')
s3 = -np.sqrt(1 + g2)          # hmm: chain kept explicit below
b_right = np.sqrt(1 + g1)                 # bud of the right body that is carried to the top bud
b_small = -np.sqrt(1 + b_right)           # bud of the small far-left body carried to it
w = np.sqrt(1 + b_small)                  # small bud ON the top bud (and its mirror)
if w.imag < 0:
    w = -w
say('small bud on the top bud, flat picture: (%.4f, %.4f); top bud middle (0, %.4f); offset along x %.4f' % (w.real, w.imag, abs(g1.imag), w.real))
rho = abs(w.real); y1 = w.imag
for tilt in (0.0, 45.0, 90.0):
    # the big bud standing in the page turned `tilt` round the x-axis: its stalk is the direction (0, cos, sin)
    ct, st = np.cos(np.radians(tilt)), np.sin(np.radians(tilt))
    a = np.arange(N) * 2 * np.pi / N
    u = rho * np.cos(a); v = rho * np.sin(a)          # u along x, v across the page of the bud
    x = u; y = y1 * ct - v * st; z = y1 * st + v * ct
    for name in ('oneplane', 'along', 'once', 'pulled'):
        for steps in (80, 200):
            ins = M.stay(R[name], x, y, z, *C, steps) >= steps
            ar = L.arcs(ins); big = [t for t in ar if t[1] >= 2.0]
            say('bud in the page at %4.1f, ring radius %.4f round its stalk, %-9s %3d steps: %2d arcs, %2d of them 2 degrees or wider: %s'
                % (tilt, rho, name, steps, len(ar), len(big), ' '.join('%.1f@%.0f' % (t[1], t[0]) for t in sorted(big))))
    say('  %.0f s' % (time.time() - t0))
say('done %.0f s' % (time.time() - t0))

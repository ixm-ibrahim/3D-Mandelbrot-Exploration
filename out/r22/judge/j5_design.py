"""Judge, re-measurement 5: the design section's rules, above all 'alonghinge'.  -> j5_design.txt"""
import os, sys, time
import numpy as np
from scipy import ndimage
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import jlib as L
M = L.M
t0 = time.time(); out = open(os.path.join(HERE, 'j5_design.txt'), 'w', encoding='utf-8')


def say(*a):
    s = ' '.join(str(t) for t in a); print(s); out.write(s + '\n'); out.flush()


R = L.rules(); H = L.design('alonghinge'); PT = L.design('preturn'); CF = L.design('capfold45')
rng = np.random.default_rng(5)

say('== A. is the hinged rule "along" for c on the x-axis? 200,000 random start points, 80 steps')
P = rng.uniform([-1.8, -1.3, -1.3], [1.8, 1.3, 1.3], size=(200000, 3))
for cx in (-1.0, -0.75, -1.754878, 0.2):
    a = M.stay(R['along'], P[:, 0], P[:, 1], P[:, 2], cx, 0.0, 0.0, 80) >= 80
    h = M.stay(H, P[:, 0], P[:, 1], P[:, 2], cx, 0.0, 0.0, 80) >= 80
    say('c = %8.4f: %d verdicts differ (inside: %d)' % (cx, (a != h).sum(), a.sum()))
say('but for c on the x-axis RIGHT of 1/4 (c = 0.3, meeting point off the axis):')
a = M.stay(R['along'], P[:, 0], P[:, 1], P[:, 2], 0.3, 0.0, 0.0, 80) >= 80; h = M.stay(H, P[:, 0], P[:, 1], P[:, 2], 0.3, 0.0, 0.0, 80) >= 80
say('c = 0.3: %d verdicts differ (inside along %d, hinged %d)' % ((a != h).sum(), a.sum(), h.sum()))

say('\n== B. flat page: verdicts that differ from the flat picture (20,000 places), and the lift test (flat-inside points lifted by a millionth)')
for name, r in (('hinge', H), ('preturn', PT), ('capfold45', CF)):
    f = M.flat_check(r, n=20000)
    zr, zi = rng.uniform(-1.8, 1.8, 20000), rng.uniform(-1.3, 1.3, 20000); res = []
    for cc in (L.BAS, L.RABBIT):
        fl = L.flat_inside(zr, zi, cc, 80)
        up = M.stay(r, zr[fl], zi[fl], np.full(fl.sum(), 1e-6), *cc, 80) >= 80
        res.append('%d of %d' % (up.sum(), fl.sum()))
    say('%-9s differ: M %d, basilica %d, rabbit %d, Siegel %d | lifted and still inside: basilica %s, rabbit %s' % (name, f['mandelbrot'], f['basilica'], f['rabbit'], f['siegel'], res[0], res[1]))

say('\n== C. the hinged rule off the x-axis: volume, leak between 30 and 80 and 300 steps, loose bits (96^3 grid)')
n = 96
GX, GY, GZ = np.meshgrid(np.linspace(-1.8, 1.8, n), np.linspace(-1.5, 1.5, n), np.linspace(-1.5, 1.5, n), indexing='ij')
SETS = [('rabbit', L.RABBIT), ('Siegel', L.SIEGEL), ('c=-1+0.2i', (-1.0, 0.2, 0.0)), ('period 4', (0.2823, 0.5301, 0.0)), ('San Marco', (-0.75, 0.0, 0.0)), ('dendrite c=i', (0.0, 1.0, 0.0)), ('c=-0.6+0.4i', (-0.6, 0.4, 0.0))]
for sn, cc in SETS:
    for name, r in (('oneplane', R['oneplane']), ('along', R['along']), ('hinge', H)):
        st = M.stay(r, GX, GY, GZ, *cc, 300)
        i30, i80, i300 = st >= 30, st >= 80, st >= 300
        raw, k = ndimage.label(i80, structure=np.ones((3, 3, 3), bool)); rc = np.bincount(raw.ravel())[1:]
        say('%-13s %-9s inside at 30 / 80 / 300 steps: %6d / %6d / %6d | lost 30->80 %.1f %%, 80->300 %.1f %% | pieces %3d, biggest %.0f %%, in pieces under 8 blocks %.1f %%'
            % (sn, name, i30.sum(), i80.sum(), i300.sum(), 100 * (i30.sum() - i80.sum()) / max(i30.sum(), 1), 100 * (i80.sum() - i300.sum()) / max(i80.sum(), 1),
               k, 100 * rc.max() / max(i80.sum(), 1) if k else 0, 100 * rc[rc < 8].sum() / max(i80.sum(), 1) if k else 0))
    say('  %.0f s' % (time.time() - t0))

say('\n== D. buds of the hinged rabbit? rings round the hinge through the middle body (2,880 places, 80 and 300 steps)')
c = complex(*L.RABBIT[:2]); alpha = (1 - np.sqrt(1 - 4 * c)) / 2; e = alpha / abs(alpha)      # the hinge direction in the flat page
perp = e * 1j; a = np.arange(2880) * 2 * np.pi / 2880
for s0, rad in ((0.0, 0.46), (0.0, 0.50), (0.15, 0.40)):
    base = s0 * e
    px = base.real + rad * np.cos(a) * perp.real; py = base.imag + rad * np.cos(a) * perp.imag; pz = rad * np.sin(a)
    for name, r in (('hinge', H), ('along', R['along']), ('oneplane', R['oneplane'])):
        for steps in (80, 300):
            ins = M.stay(r, px, py, pz, *L.RABBIT, steps) >= steps; ar = L.arcs(ins)
            w = np.array([t[1] for t in ar]) if ar else np.zeros(0)
            say('ring at %.2f along the hinge, radius %.2f, %-9s %3d steps: %3d arcs, %5.1f degrees inside, arcs of 5 degrees or more: %d, under 1 degree: %d'
                % (s0, rad, name, steps, len(ar), w.sum(), (w >= 5).sum(), (w < 1).sum()))

say('\n== E. "preturn": is its upright page the flat rabbit? (360 x 260, 120 steps)')
u, s = np.meshgrid(np.linspace(-1.8, 1.8, 360), np.linspace(1.3, -1.3, 260))
for cn, cc in (('basilica', L.BAS), ('rabbit', L.RABBIT)):
    ins = M.stay(PT, u, 0 * s, s, *cc, 120) >= 120
    # the upright half-page above is laid onto the half of the flat page with y < 0; below: mirrored
    flat = L.flat_inside(u, -np.abs(s), cc, 120)
    say('%-8s upright page of preturn against the lower half of the flat picture: %d places differ (flat picture there: %d)' % (cn, (ins != flat).sum(), flat.sum()))
say('done %.0f s' % (time.time() - t0))

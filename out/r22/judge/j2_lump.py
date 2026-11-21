"""Judge, re-measurement 2: the rabbit's lump.  -> j2_lump.txt"""
import os, sys, time
import numpy as np
from scipy import ndimage
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import jlib as L
M = L.M
t0 = time.time(); out = open(os.path.join(HERE, 'j2_lump.txt'), 'w', encoding='utf-8')


def say(*a):
    s = ' '.join(str(t) for t in a); print(s); out.write(s + '\n'); out.flush()


R = L.rules(); R['hinge'] = L.design('alonghinge')
C = L.RABBIT; c = complex(C[0], C[1])
CYC = np.array([0, c, c * c + c])
alpha = (1 - np.sqrt(1 - 4 * c)) / 2
say('rabbit c = %s, cycle %s, meeting point %.4f %+.4fi, flat stretch there %.4f' % (c, np.round(CYC, 4), alpha.real, alpha.imag, abs(2 * alpha)))
rng = np.random.default_rng(22)

say('\n== A. where do staying orbits end? 400,000 random starts, inside = stays 80 steps, then followed to step 729')
P = rng.uniform([-1.8, -1.5, -1.5], [1.8, 1.5, 1.5], size=(400000, 3))
for name in ('along', 'oneplane', 'once', 'lathe', 'hinge'):
    ins = M.stay(R[name], P[:, 0], P[:, 1], P[:, 2], *C, 80) >= 80
    x, y, z, al = L.follow(R[name], P[ins, 0], P[ins, 1], P[ins, 2], C, 729)
    w = x[al] + 1j * y[al]; d = np.abs(w[:, None] - CYC[None]).min(1); h = np.abs(z[al])
    say('%-9s inside %6d | still there at step 729: %6d | of those within 1e-6 of a flat cycle point and under 1e-9 high: %6d | farthest %.1e, highest %.1e'
        % (name, ins.sum(), al.sum(), ((d < 1e-6) & (h < 1e-9)).sum(), d.max() if al.any() else 0, h.max() if al.any() else 0))
say('  %.0f s' % (time.time() - t0))

say('\n== A2. c = -1 + 0.2i and the Siegel disc under along')
c2 = complex(-1, 0.2); zz = 0j
for _ in range(4000):
    zz = zz * zz + c2
cyc2 = np.array([zz, zz * zz + c2])
for name in ('along', 'oneplane'):
    ins = M.stay(R[name], P[:, 0], P[:, 1], P[:, 2], -1.0, 0.2, 0.0, 80) >= 80
    x, y, z, al = L.follow(R[name], P[ins, 0], P[ins, 1], P[ins, 2], (-1.0, 0.2, 0.0), 3000)
    w = x[al] + 1j * y[al]; d = np.abs(w[:, None] - cyc2[None]).min(1); h = np.abs(z[al])
    say('c=-1+0.2i %-9s inside %6d | alive at 3000: %6d | on the flat two-cycle (1e-6): %6d | highest %.1e' % (name, ins.sum(), al.sum(), ((d < 1e-6) & (h < 1e-9)).sum(), h.max()))
S = L.SIEGEL
for name in ('along', 'oneplane'):
    ins = M.stay(R[name], P[:60000, 0], P[:60000, 1], P[:60000, 2], *S, 300) >= 300
    Q = P[:60000][ins]
    for steps in (10, 100, 1000, 5000):
        x, y, z, al = L.follow(R[name], Q[:, 0], Q[:, 1], Q[:, 2], S, steps)
        say('Siegel %-9s %5d starts that stay 300 steps: after %5d steps alive %5d, median height %.1e' % (name, len(Q), steps, al.sum(), np.nanmedian(np.abs(z))))
say('  %.0f s' % (time.time() - t0))

say('\n== B. height after one step / height before, straight above the meeting point')
hs = np.array([0.005, 0.04, 0.075, 0.12, 0.2, 0.3, 0.4, 0.6])
for name in ('along', 'oneplane', 'lathe', 'hinge', 'once'):
    X, Y, Z = L.one(R[name], np.full(hs.size, alpha.real), np.full(hs.size, alpha.imag), hs, C)
    say('%-9s' % name, ' '.join('%6.2f' % t for t in Z / hs), '  | sideways move at height 0.2: %.3f' % np.hypot(X[4] - alpha.real, Y[4] - alpha.imag))

say('\n== C. the space over the meeting point: share inside (120 steps) of a box 0.2 wide round it, by height band; and the line straight above it')
bands = [(0, 0.02), (0.02, 0.05), (0.05, 0.1), (0.1, 0.2), (0.2, 0.3), (0.3, 0.5)]
for name in ('along', 'oneplane', 'lathe', 'once', 'hinge'):
    row = []
    for lo, hi in bands:
        q = rng.uniform([alpha.real - 0.1, alpha.imag - 0.1, lo], [alpha.real + 0.1, alpha.imag + 0.1, hi], size=(20000, 3))
        row.append(100 * (M.stay(R[name], q[:, 0], q[:, 1], q[:, 2], *C, 120) >= 120).mean())
    hh = np.linspace(0.0005, 0.6, 1200)
    line = M.stay(R[name], np.full(hh.size, alpha.real), np.full(hh.size, alpha.imag), hh, *C, 300) >= 300
    say('%-9s box %s %% | line straight above the meeting point: %4d of 1200 heights inside (300 steps)' % (name, ' / '.join('%4.0f' % t for t in row), line.sum()))
say('  %.0f s' % (time.time() - t0))

say('\n== D. bodies and walls on a 96^3 grid (inside = 120 steps; colour = flat cycle point the orbit is on at step 120)')
n = 96
gx = np.linspace(-1.8, 1.8, n); gy = np.linspace(-1.5, 1.5, n); gz = np.linspace(-1.5, 1.5, n)      # n even: no grid point on z = 0
GX, GY, GZ = np.meshgrid(gx, gy, gz, indexing='ij')
grids = {}
for name in ('along', 'oneplane', 'once', 'lathe', 'hinge'):
    x, y, z, al = L.follow(R[name], GX, GY, GZ, C, 120)
    col = np.zeros(GX.size, np.int8)
    w = x[al] + 1j * y[al]; dd = np.abs(w[:, None] - CYC[None]); near = dd.argmin(1) + 1; near[dd.min(1) > 0.05] = 4
    col[al] = near; col = col.reshape(GX.shape); grids[name] = col
    ins = col > 0; walls = 0; skin = 0
    for ax in range(3):
        a = np.moveaxis(col, ax, 0); p, q = a[:-1], a[1:]
        walls += int(((p > 0) & (q > 0) & (p != q)).sum()); skin += int(((p > 0) != (q > 0)).sum())
    say('%-9s inside blocks %6d (no colour: %d) | faces between two bodies %6d, faces to the outside %6d, wall share %.1f %%'
        % (name, ins.sum(), (col == 4).sum(), walls, skin, 100 * walls / max(walls + skin, 1)))
a_, o_ = grids['along'] > 0, grids['oneplane'] > 0
say('share of along\'s rabbit that is not in one plane\'s: %.1f %%; of one plane\'s inside along\'s: %.1f %%' % (100 * (a_ & ~o_).sum() / a_.sum(), 100 * (a_ & o_).sum() / o_.sum()))
say('blocks higher than 0.4 off the page: along %d, one plane %d, hinge %d' % ((a_ & (np.abs(GZ) > 0.4)).sum(), (o_ & (np.abs(GZ) > 0.4)).sum(), ((grids['hinge'] > 0) & (np.abs(GZ) > 0.4)).sum()))
say('  %.0f s' % (time.time() - t0))

say('\n== E. pieces of "along once" (128^3, 80 steps, gaps of two cells bridged), and where one step puts the loose ones')
n = 128
gx = np.linspace(-1.8, 1.8, n); gy = np.linspace(-1.5, 1.5, n); gz = np.linspace(-1.5, 1.5, n)
GX2, GY2, GZ2 = np.meshgrid(gx, gy, gz, indexing='ij')
for name in ('once', 'oneplane', 'along', 'hinge'):
    ins = (M.stay(R[name], GX2, GY2, GZ2, *C, 80) >= 80)
    fat = ndimage.binary_dilation(ins, structure=np.ones((3, 3, 3), bool))
    lab, k = ndimage.label(fat, structure=np.ones((3, 3, 3), bool)); lab = lab * ins
    cnt = np.bincount(lab.ravel())[1:]; order = np.argsort(-cnt)
    raw, kraw = ndimage.label(ins, structure=np.ones((3, 3, 3), bool)); rc = np.bincount(raw.ravel())[1:]
    say('%-9s inside %7d | pieces (bridged): %d, the biggest three hold %s %% | not bridged: %d pieces, %.1f %% of blocks in pieces under 8 blocks'
        % (name, ins.sum(), k, ' / '.join('%.2f' % (100 * cnt[i] / ins.sum()) for i in order[:3]), kraw, 100 * rc[rc < 8].sum() / ins.sum()))
    if name == 'once':
        for i in order[1:3]:
            m = lab == i + 1; px, py, pz = GX2[m], GY2[m], GZ2[m]
            X, Y, Z = L.one(R['along'], px, py, pz, C)
            dd = np.abs((X + 1j * Y)[:, None] - CYC[None]).argmin(1)
            say('   loose piece: %d blocks, middle (%.3f, %.3f, %.3f), heights %.2f..%.2f | after one step of along: median height %.3f, largest %.3f, nearest cycle point: 0: %d, c: %d, c^2+c: %d'
                % (m.sum(), px.mean(), py.mean(), pz.mean(), np.abs(pz).min(), np.abs(pz).max(), np.median(np.abs(Z)), np.abs(Z).max(), (dd == 0).sum(), (dd == 1).sum(), (dd == 2).sum()))
            ins1 = M.stay(R['oneplane'], X, Y, Z, *C, 80) >= 79
            say('   after that step inside the one-plane rabbit: %d of %d' % (ins1.sum(), m.sum()))
say('  %.0f s' % (time.time() - t0))

say('\n== F. along\'s resting place above the meeting point')
p = np.array([-0.2764, 0.4816, 0.0754])
for _ in range(60):                                   # Newton on F(p) - p with a finite-difference matrix
    f0 = np.array([t[0] for t in L.one(R['along'], [p[0]], [p[1]], [p[2]], C)]) - p
    Jm = np.zeros((3, 3)); e = 1e-6
    for j in range(3):
        q = p.copy(); q[j] += e
        Jm[:, j] = (np.array([t[0] for t in L.one(R['along'], [q[0]], [q[1]], [q[2]], C)]) - q - f0) / e
    p = p - np.linalg.solve(Jm, f0)
f0 = np.array([t[0] for t in L.one(R['along'], [p[0]], [p[1]], [p[2]], C)]) - p
say('resting place (%.4f, %.4f, %.4f), one step moves it by %.1e; stretches there %s' % (p[0], p[1], p[2], np.abs(f0).max(), np.round(np.sort(np.abs(np.linalg.eigvals(Jm + np.eye(3)))), 3)))

say('\n== G. along\'s pages: is the cut along the page at 45 / 90 degrees the flat picture? (360 x 260 places, 120 steps)')
u, s = np.meshgrid(np.linspace(-1.8, 1.8, 360), np.linspace(1.3, -1.3, 260))
for cn, cc in (('basilica', L.BAS), ('rabbit', C)):
    flat = L.flat_inside(u, s, cc, 120)
    for ang in (0.0, 45.0, 90.0):
        a = np.radians(ang)
        ins = M.stay(R['along'], u, s * np.cos(a), s * np.sin(a), *cc, 120) >= 120
        say('%-8s page at %4.1f: %5d places differ from the flat picture (flat picture has %d)' % (cn, ang, (ins != flat).sum(), flat.sum()))
say('done %.0f s' % (time.time() - t0))

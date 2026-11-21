"""The sixth rule, alonghinge: is it along on the x-axis, flat check, lift test, leak, pieces, walls between bodies.
python out/r22/design/check2.py > out/r22/design/check2.txt"""
import sys, os, time
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dlib as L
M, D = L.M, L.D
R = L.refs(); H = D.get('alonghinge'); A = R['along']; O = R['oneplane']
rng = np.random.default_rng(5)

print('A. along turned half-way round the upright axis: is it the same rule? (so that the hinge has no front and back)')
V = rng.normal(size=(20000, 3))
X1, Y1, Z1 = L.one(A, V[:, 0], V[:, 1], V[:, 2]); X2, Y2, Z2 = L.one(A, -V[:, 0], -V[:, 1], V[:, 2])
print('   largest difference %.2e' % max(np.abs(X1 - X2).max(), np.abs(Y1 - Y2).max(), np.abs(Z1 - Z2).max()))

print('B. For c on the x-axis the rule is along (verdicts that differ, 200,000 random start points, 60 steps)')
P = rng.uniform([-1.8, -1.3, -1.3], [1.8, 1.3, 1.3], size=(200000, 3))
for cn, c in (('c = -1', (-1.0, 0, 0)), ('c = -0.75', (-0.75, 0, 0)), ('c = -1.7549', (-1.754878, 0, 0)), ('c = 0.2', (0.2, 0, 0))):
    a = M.stay(A, P[:, 0], P[:, 1], P[:, 2], *c, 60) >= 60; h = M.stay(H, P[:, 0], P[:, 1], P[:, 2], *c, 60) >= 60
    print('   %-12s along inside %d, hinged inside %d, differ %d' % (cn, a.sum(), h.sum(), (a != h).sum()))

print('C. The hinge for some c: the meeting point and its turn')
for cn, c in (('basilica', (-1.0, 0.0)), ('rabbit', M.RABBIT[:2]), ('Siegel', M.SIEGEL[:2]), ('-1 + 0.2i', (-1.0, 0.2)), ('i', (0.0, 1.0)), ('-0.12 - 0.74i', (-0.122561, -0.744862))):
    al = (1 - np.sqrt(1 - 4 * complex(*c))) / 2
    print('   %-14s meeting point %.4f %+.4fi  turn of the hinge %.2f degrees' % (cn, al.real, al.imag, np.degrees(D.meeting_turn(c[0], c[1]))))

print('D. Flat check and lift test')
f = M.flat_check(H, n=20000, steps=60)
print('   verdicts that differ: M %d, basilica %d, rabbit %d, Siegel %d of %d; strays %.1e' % (f['mandelbrot'], f['basilica'], f['rabbit'], f['siegel'], f['of'], f['off_the_page']))
for cn, c in (('basilica', L.BAS), ('rabbit', L.RAB), ('Siegel', M.SIEGEL), ('-1 + 0.2i', (-1.0, 0.2, 0.0))):
    lb = L.lift_test(H, c); print('   lifted 1e-6, %-10s %d of %d stay' % (cn, lb[0], lb[1]))

print('E. 72^3 grid: inside blocks at 30 and 80 steps, biggest piece, pieces, dust; rabbit, Siegel, c = -1 + 0.2i, c = -1 + 0.03i')
t0 = time.time()
for cn, c in (('rabbit', L.RAB), ('Siegel', M.SIEGEL), ('-1+0.2i', (-1.0, 0.2, 0.0)), ('-1+0.03i', (-1.0, 0.03, 0.0))):
    for r in (O, A, H):
        v30 = L.grid(r, c, 72, 30); v80 = L.grid(r, c, 72, 80); b, n, dust = L.pieces(v80)
        print('   %-9s %-11s 30 steps %6d  80 steps %6d (%.1f %% lost)  biggest %.1f %%  pieces %d  dust %.2f %%  [%.0f s]'
              % (cn, r.name, v30.sum(), v80.sum(), 100 * (1 - v80.sum() / max(v30.sum(), 1)), 100 * b, n, 100 * dust, time.time() - t0)); sys.stdout.flush()

print('F. Rabbit: height after one step / before, straight above the meeting point (the lump section\'s table)')
al = (1 - np.sqrt(1 - 4 * complex(*M.RABBIT[:2]))) / 2
hs = np.array([0.005, 0.04, 0.075, 0.12, 0.2, 0.3, 0.4, 0.6])
for r in (O, A, R['lathe'], H):
    X, Y, Z = r.step(np.full(hs.size, al.real), np.full(hs.size, al.imag), hs, tuple(r.init(hs.size)), 0, np.full(hs.size, M.RABBIT[0]), np.full(hs.size, M.RABBIT[1]), np.zeros(hs.size))[:3]
    print('   %-11s' % r.name, ' '.join('%6.2f' % t for t in Z / hs))
print('   heights     ', ' '.join('%6.3f' % t for t in hs))

print('G. Rabbit: share of a box 0.2 wide round the meeting point that is inside, by height band (120 steps)')
bands = [(0.0, 0.02), (0.02, 0.05), (0.05, 0.1), (0.1, 0.2), (0.2, 0.3)]
for r in (O, A, H):
    out = []
    for lo, hi in bands:
        q = rng.uniform([al.real - 0.1, al.imag - 0.1, lo], [al.real + 0.1, al.imag + 0.1, hi], size=(20000, 3))
        out.append(100 * (M.stay(r, q[:, 0], q[:, 1], q[:, 2], *M.RABBIT, 120) >= 120).mean())
    print('   %-11s' % r.name, ' '.join('%5.1f %%' % t for t in out))

print('H. Rabbit: which flat cycle point each inside block sits on after 120 steps, and walls between bodies (64^3)')
cyc = [0j, complex(*M.RABBIT[:2])]; cyc.append(cyc[1] ** 2 + cyc[1])
n = 64; xs = np.linspace(-1.8, 1.8, n); ys = np.linspace(-1.5, 1.5, n); zs = np.linspace(-1.5, 1.5, n)
Xg, Yg, Zg = np.meshgrid(xs, ys, zs, indexing='ij')
for r in (O, A, H):
    x, y, z = Xg.ravel().copy(), Yg.ravel().copy(), Zg.ravel().copy(); idx = np.arange(x.size); st = tuple(r.init(x.size))
    cxa, cya, cza = (np.full(x.size, t) for t in M.RABBIT)
    for k in range(120):
        o = r.step(x, y, z, st, k, cxa, cya, cza); x, y, z, st = o[0] + cxa, o[1] + cya, o[2] + cza, tuple(o[3])
        keep = x * x + y * y + z * z < 36
        idx, x, y, z, cxa, cya, cza = idx[keep], x[keep], y[keep], z[keep], cxa[keep], cya[keep], cza[keep]; st = tuple(t[keep] for t in st)
    d = np.stack([np.sqrt((x - p.real) ** 2 + (y - p.imag) ** 2 + z * z) for p in cyc]); col = d.argmin(0); far = d.min(0) > 0.05
    lab = np.full(Xg.size, -1); lab[idx] = col; lab = lab.reshape(Xg.shape)
    skin = 0; wall = 0
    for ax in range(3):
        a = np.moveaxis(lab, ax, 0); p, q = a[:-1], a[1:]
        skin += ((p >= 0) != (q >= 0)).sum(); wall += ((p >= 0) & (q >= 0) & (p != q)).sum()
    print('   %-11s inside %6d, not near a flat cycle point %d, height at the end at most %.1e, walls %.1f %% of skin (%d faces)'
          % (r.name, idx.size, far.sum(), np.abs(z).max() if z.size else 0, 100 * wall / max(skin + wall, 1), wall))

"""Quick checks of the findings the design rests on, and the first numbers of the new rules.
python out/r22/design/check1.py > out/r22/design/check1.txt"""
import sys, os, time
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dlib as L
M, D = L.M, L.D
R = L.refs(); NEW = D.RULES
rng = np.random.default_rng(11)

print('A. Length squared, and the flat page against complex squaring (20,000 random points)')
P3 = rng.normal(size=(20000, 3))
for r in list(R.values()) + NEW:
    X, Y, Z = L.one(r, P3[:, 0], P3[:, 1], P3[:, 2])
    ln = np.abs(np.sqrt(X * X + Y * Y + Z * Z) - (P3 ** 2).sum(1)).max()
    X, Y, Z = L.one(r, P3[:, 0], P3[:, 1], 0 * P3[:, 2])
    pl = max(np.abs(X - (P3[:, 0] ** 2 - P3[:, 1] ** 2)).max(), np.abs(Y - 2 * P3[:, 0] * P3[:, 1]).max(), np.abs(Z).max())
    print('  %-12s length %.1e  flat page %.1e' % (r.name, ln, pl))

print('B. Turning the point round the UPRIGHT axis by a, does the square turn by 2a? (largest miss, 20,000 points, |v| = 1)')
U = P3 / np.linalg.norm(P3, axis=1, keepdims=True); a = rng.uniform(0, 2 * np.pi, 20000)
for r in list(R.values()) + NEW:
    X, Y, Z = L.one(r, U[:, 0], U[:, 1], U[:, 2])
    x2, y2 = np.cos(a) * U[:, 0] - np.sin(a) * U[:, 1], np.sin(a) * U[:, 0] + np.cos(a) * U[:, 1]
    X2, Y2, Z2 = L.one(r, x2, y2, U[:, 2])
    Xr, Yr = np.cos(2 * a) * X - np.sin(2 * a) * Y, np.sin(2 * a) * X + np.cos(2 * a) * Y
    miss = np.sqrt((X2 - Xr) ** 2 + (Y2 - Yr) ** 2 + (Z2 - Z) ** 2)
    print('  %-12s largest %.2e  median %.2e' % (r.name, miss.max(), np.median(miss)))

print('C. Directions above the page that one squaring puts ON or BELOW the page (share of 400,000 directions with z > 0),')
print('   and how many places one squaring sends onto one spot of the flat page (counted on a fine grid of directions)')
N = 400000; V = rng.normal(size=(N, 3)); V[:, 2] = np.abs(V[:, 2]); V /= np.linalg.norm(V, axis=1, keepdims=True)
th = np.linspace(-np.pi, np.pi, 1441)[:-1]; la = np.linspace(0.002, np.pi / 2 - 0.002, 720)
TH, LA = np.meshgrid(th, la)
gx, gy, gz = np.cos(LA) * np.cos(TH), np.cos(LA) * np.sin(TH), np.sin(LA)
for r in list(R.values()) + NEW:
    X, Y, Z = L.one(r, V[:, 0], V[:, 1], V[:, 2])
    share = float((Z <= 0).mean())
    # places above the page that land on the page inside a small arc of directions round the flat direction 100 degrees
    X, Y, Z = L.one(r, gx.ravel(), gy.ravel(), gz.ravel()); Z = Z.reshape(gz.shape); A = np.arctan2(Y, X).reshape(gz.shape)
    cross = (np.sign(Z[1:]) != np.sign(Z[:-1]))                       # the height changes sign between two rows: lands on the page
    tgt = np.radians(100.0); near = np.abs(((A[1:] - tgt + np.pi) % (2 * np.pi)) - np.pi) < np.radians(0.25)
    hits = cross & near
    # count separate places: cluster by row/column proximity
    from scipy import ndimage
    lab, nl = ndimage.label(ndimage.binary_dilation(hits, iterations=2))
    print('  %-12s share thrown onto or below the page %.3f   places above the page landing on the flat direction 100 deg: %d  (+ 2 in the page itself)' % (r.name, share, nl))

print('D. Flat check and lift test (a film would lose every lifted point)')
for r in NEW:
    f = M.flat_check(r, n=20000, steps=60)
    lb = L.lift_test(r, L.BAS); lr = L.lift_test(r, L.RAB)
    print('  %-12s verdicts that differ: M %d, basilica %d, rabbit %d, Siegel %d of %d; strays %.1e | lifted 1e-6: basilica %d of %d stay, rabbit %d of %d'
          % (r.name, f['mandelbrot'], f['basilica'], f['rabbit'], f['siegel'], f['of'], f['off_the_page'], lb[0], lb[1], lr[0], lr[1]))
for nm in ('oneplane', 'along'):
    r = R[nm]; lb = L.lift_test(r, L.BAS); lr = L.lift_test(r, L.RAB)
    print('  %-12s lifted 1e-6: basilica %d of %d stay, rabbit %d of %d' % (nm, lb[0], lb[1], lr[0], lr[1]))

print('E. Volumes and pieces, 72^3 grid, 30 against 80 steps (inside blocks; biggest piece; pieces; share in pieces under 8 blocks)')
t0 = time.time()
for cn, c in (('basilica', L.BAS), ('rabbit', L.RAB)):
    for r in [R['oneplane'], R['along']] + NEW:
        v30 = L.grid(r, c, 72, 30); v80 = L.grid(r, c, 72, 80)
        b, n, dust = L.pieces(v80)
        print('  %-9s %-12s 30 steps %6d  80 steps %6d (%.1f %% lost)  biggest %.1f %%  pieces %d  dust %.2f %%   [%.0f s]'
              % (cn, r.name, v30.sum(), v80.sum(), 100 * (1 - v80.sum() / max(v30.sum(), 1)), 100 * b, n, 100 * dust, time.time() - t0)); sys.stdout.flush()

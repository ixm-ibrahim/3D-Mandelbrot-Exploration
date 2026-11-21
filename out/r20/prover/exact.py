"""W1..W4, the symmetries, even k, two planes, the cover count, the power-n symmetry. Numbers only, seconds.
    python out/r20/prover/exact.py > out/r20/prover/logs/exact.log
Every block prints EXPECT (written before running) and then the measured numbers."""
import numpy as np
import lib as L
S = L.S
rng = np.random.default_rng(20)
F3 = L.M19.wind(3, 'sin')              # the orchestrator's own m_w3 code
F5 = L.M19.wind(5, 'sin')
N = 200000

def mx(*a):
    return max(float(np.abs(t).max()) for t in a)

print('== 0. my P_2 is the bench one-plane rule; my wind(g_sin(3)) is m_w3')
v = rng.normal(size=(3, N))
print('   |P_2 - S.oneplane| max', mx(*(np.array(L.Pn(2)(*v)) - np.array(S.oneplane(*v)))))
print('   |wind(g_sin 3) - m_w3| max', mx(*(np.array(L.wind(L.g_sin(3))(*v)) - np.array(F3(*v)))))

print('\n== W1. copy half-planes: EXPECT answer in the flat plane (|Z| ~ 1e-15), equal to the flat square of x + i rho at 0, 120, 240 degrees')
print('        and of x - i rho (the MIRROR image) at 60, 180, 300 degrees.')
x = rng.normal(size=N); rho = np.abs(rng.normal(size=N))
for ang in (0, 60, 120, 180, 240, 300):
    a = np.radians(ang)
    X, Y, Z = F3(x, rho * np.cos(a), rho * np.sin(a))
    e_plus = mx(X - (x * x - rho * rho), Y - 2 * x * rho); e_minus = mx(X - (x * x - rho * rho), Y + 2 * x * rho)
    print(f'   half-plane {ang:3d} deg: |Z| max {np.abs(Z).max():.1e}   error vs (x + i rho)^2 {e_plus:.1e}   vs (x - i rho)^2 {e_minus:.1e}')
print('   whole sets, 60 steps, 401 x 401 points, box 1.7: points where the cut differs from the flat set (mirrored at 60, plain at 120)')
u = np.linspace(-1.7, 1.7, 401); s = np.linspace(1.7, -1.7, 401); U, Sg = np.meshgrid(u, s)
for name, c in L.SETS.items():
    flat = L.flat_member(U, Sg, c, 60) >= 60; flatm = L.flat_member(U, -Sg, c, 60) >= 60
    out = []
    for ang in (60, 120):
        a = np.radians(ang)
        cut = L.member(F3, U, Sg * np.cos(a), Sg * np.sin(a), c, 60) >= 60
        out.append(f'{ang} deg: differs from flat {int((cut ^ flat).sum())}, from mirrored flat {int((cut ^ flatm).sum())}')
    print(f'   {name:9s} inside points {int(flat.sum()):6d}   ' + '   '.join(out))

print('\n== W2. even k. EXPECT: on the half y < 0 of the flat plane the answer is the MIRROR image conj(z^2), error vs z^2 = 4|x y| (order 1);')
print('        the cut z = 0 is still the flat set for c on the x-axis (0 points differ) and is wrong for the rabbit.')
for k in (2, 4):
    Fk = L.wind(L.g_sin(k))
    xx, yy = rng.normal(size=(2, N)); X, Y, Z = Fk(xx, yy, 0 * xx)
    up = yy > 0
    print(f'   k = {k}: flat plane, half y > 0: error vs z^2 {mx(X[up] - (xx[up]**2 - yy[up]**2), Y[up] - 2*xx[up]*yy[up]):.1e};  half y < 0: error vs z^2 '
          f'{mx(Y[~up] - 2*xx[~up]*yy[~up]):.2f}, error vs conj(z^2) {mx(X[~up] - (xx[~up]**2 - yy[~up]**2), Y[~up] + 2*xx[~up]*yy[~up]):.1e}, |Z| {np.abs(Z).max():.1e}')
    for name in ('basilica', 'rabbit', 'siegel'):
        c = L.SETS[name]
        flat = L.flat_member(U, Sg, c, 60) >= 60
        cut = L.member(Fk, U, Sg, 0 * U, c, 60) >= 60
        print(f'      {name:9s} cut z = 0: {int((cut ^ flat).sum())} of {int(flat.sum())} points differ from the flat set ({100.0 * (cut ^ flat).sum() / max(flat.sum(), 1):.1f} %)')
print('   odd k (3, 5): flat plane error', end=' ')
for Fk in (F3, F5):
    xx, yy = rng.normal(size=(2, N)); X, Y, Z = Fk(xx, yy, 0 * xx); print(f'{mx(X - (xx*xx - yy*yy), Y - 2*xx*yy, Z):.1e}', end=' ')
print()

print('\n== W3 and the other symmetries of F (m_w3). EXPECT all ~1e-13.')
v = rng.normal(size=(3, N)); A = np.array(F3(*v))
def dev(B):
    return float(np.abs(A - np.array(B)).max())
print('   F(turn 120 about x) - F                      ', dev(F3(*L.rotx(120, *v))))
print('   F(turn 60 about x) - half-turn-about-x of F  ', dev(L.rotx(180, *F3(*L.rotx(60, *v)))))
B = F3(v[0], v[1], -v[2]); print('   F(mirror z) - mirror z of F                  ', dev((B[0], B[1], -B[2])))
B = F3(v[0], -v[1], v[2]); print('   F(mirror y) - mirror y of F                  ', dev((B[0], -B[1], B[2])))
print('   F(half turn about the upright axis) - F      ', dev(F3(-v[0], -v[1], v[2])))
B = F3(-v[0], -v[1], -v[2]); print('   F(-v) - mirror z of F(v)                     ', dev((B[0], B[1], -B[2])))
print('   control, must NOT vanish: F(turn 60) - F     ', dev(F3(*L.rotx(60, *v))))

print('\n== W4. the map of directions D = P o T on the unit sphere (m_w3).')
print('   EXPECT: never mirror-reversed (signed area factor >= 0); it vanishes only at the six directions at right angles to the x-axis')
print('   half way between the planes; covers the sphere 6 times; -x is hit from six directions with both stretches exactly 2;')
print('   +x is hit only from +x and -x; near the x-axis the two stretches are 2 and 2 g\'(a): 2..10 (a cone point, NOT in W4).')
def Dmap(F, Q):
    Q = Q / np.linalg.norm(Q, axis=1)[:, None]
    W = np.stack(F(Q[:, 0], Q[:, 1], Q[:, 2]), 1)
    return W / np.linalg.norm(W, axis=1)[:, None]
def jac(F, V, h=1e-6):
    a = np.cross(V, np.array([1.0, 0, 0])); a /= np.linalg.norm(a, axis=1)[:, None]; b = np.cross(V, a)   # a: round the x-axis, b: along the meridian
    W0 = Dmap(F, V); da = (Dmap(F, V + h * a) - Dmap(F, V - h * a)) / (2 * h); db = (Dmap(F, V + h * b) - Dmap(F, V - h * b)) / (2 * h)
    det = np.einsum('ij,ij->i', W0, np.cross(da, db))
    return W0, da, db, det
V = rng.normal(size=(600000, 3)); V /= np.linalg.norm(V, axis=1)[:, None]
V = V[np.abs(V[:, 0]) < 0.9999]
W0, da, db, det = jac(F3, V)
# with a = round-the-axis unit vector and b = meridian unit vector, (a, b, V) orientation: check sign on the one-plane rule
_, _, _, det1 = jac(S.oneplane, V)
sg = np.sign(np.median(det1))
det *= sg; det1 *= sg
sa = np.linalg.norm(da, axis=1); sb = np.linalg.norm(db, axis=1)
print(f'   one-plane rule (control): share reversed {100*(det1 < 0).mean():.3f} %, covers {det1.mean():.3f} times')
print(f'   m_w3: share reversed {100*(det < -1e-6).mean():.4f} %, smallest area factor {det.min():.2e}, covers {det.mean():.3f} times (mean area factor), largest stretch {max(sa.max(), sb.max()):.2f}')
low = V[det < 0.02]; ang = np.degrees(np.arctan2(low[:, 2], low[:, 1])) % 60; col = np.degrees(np.arccos(low[:, 0]))
print(f'   area factor < 0.02 at {len(low)} sampled directions: turn round the axis mod 60 in [{ang.min():.1f}, {ang.max():.1f}] deg, angle from +x in [{col.min():.1f}, {col.max():.1f}] deg')
ratio = sa / np.maximum(sb, 1e-12); a_of = np.arctan2(V[:, 2], V[:, 1]); gp = L.dg_sin(3)(a_of)
print(f'   stretch round the axis / stretch along the meridian, against g\'(a): largest relative difference {np.abs(ratio / gp - 1).max():.1e}  (so the squeeze IS g\')')
for ang in (0, 60, 120, 180, 240, 300, 30, 90):
    a = np.radians(ang); u = np.array([[0.0, np.cos(a), np.sin(a)]])
    w0, d1, d2, dt = jac(F3, u)
    print(f'   direction at right angles to x, {ang:3d} deg round: sent to ({w0[0,0]:+.3f}, {w0[0,1]:+.3f}, {w0[0,2]:+.3f}), stretches {np.linalg.norm(d1):.4f} and {np.linalg.norm(d2):.4f}')
Vb = rng.normal(size=(3000000, 3)); Vb /= np.linalg.norm(Vb, axis=1)[:, None]
Wb = Dmap(F3, Vb)
for tag, sel in (('-x', Wb[:, 0] < -np.cos(np.radians(1.0))), ('+x', Wb[:, 0] > np.cos(np.radians(1.0)))):
    Q = Vb[sel]; col = np.degrees(np.arccos(np.clip(Q[:, 0], -1, 1))); lon = np.degrees(np.arctan2(Q[:, 2], Q[:, 1])) % 360
    if tag == '-x':
        bins = np.round(lon / 60) % 6
        print(f'   sent within 1 deg of -x: {len(Q)} of 3,000,000; angle from +x {col.min():.1f}..{col.max():.1f}; turn round the axis within {np.abs(lon - 60*np.round(lon/60)).max():.2f} deg of a multiple of 60; per half-plane {np.bincount(bins.astype(int), minlength=6).tolist()}')
    else:
        print(f'   sent within 1 deg of +x: {len(Q)} of 3,000,000; angle from +x: {int((col < 5).sum())} within 5 deg of +x, {int((col > 175).sum())} within 5 deg of -x, {int(((col >= 5) & (col <= 175)).sum())} elsewhere')
for th in (0.5, 5.0, 30.0):
    out = []
    for ang in (0, 10, 20, 30):
        a = np.radians(ang); t = np.radians(th); u = np.array([[np.cos(t), np.sin(t) * np.cos(a), np.sin(t) * np.sin(a)]])
        w0, d1, d2, dt = jac(F3, u); out.append(f'{ang} deg: {np.linalg.norm(d2):.2f} x {np.linalg.norm(d1):.2f}')
    print(f'   {th:4.1f} deg from the +x direction (meridian x round-the-axis stretch): ' + ';  '.join(out))

print('\n== The count. EXPECT covers = n k; "round on average" needs n^2.')
for n, k in ((2, 1), (2, 3), (2, 5), (3, 3), (3, 5), (4, 3), (4, 5), (5, 5)):
    Fnk = L.wind(L.g_sin(k), L.Pn(n))
    _, d1, d2, dt = jac(Fnk, V[:200000]); dt = dt * sg
    print(f'   power {n}, k = {k}: covers {dt.mean():6.2f} times (n k = {n*k:2d}); round on average needs n^2 = {n*n:2d}; ratio {n*k/(n*n):.2f}; '
          f'root-mean-square stretch {np.sqrt(dt.mean()):.2f} against {n}')

print('\n== Flat plane exact and the count k at whole powers. EXPECT flat error ~1e-13 for odd k at every power.')
for n, k in ((2, 3), (3, 3), (4, 5), (5, 5), (4, 3), (3, 2), (4, 4)):
    Fnk = L.wind(L.g_sin(k), L.Pn(n)); xx, yy = rng.normal(size=(2, N)); zc = (xx + 1j * yy) ** n
    X, Y, Z = Fnk(xx, yy, 0 * xx); print(f'   power {n}, k = {k}: flat plane error {mx(X - zc.real, Y - zc.imag, Z):.1e}')

print('\n== Power-n symmetry the flat picture has: z -> z e^(2 pi i / n) leaves z^n alone (turn about the UPRIGHT axis).')
print('   EXPECT: P_n alone keeps it for every n; wind-then-square keeps it only at n = 2.')
for n, k in ((2, 3), (3, 3), (4, 5), (5, 5)):
    Fnk = L.wind(L.g_sin(k), L.Pn(n)); th = 2 * np.pi / n; c_, s_ = np.cos(th), np.sin(th)
    v = rng.normal(size=(3, N)); v /= np.sqrt((v * v).sum(0))
    A0 = np.array(Fnk(*v)); A1 = np.array(Fnk(c_ * v[0] - s_ * v[1], s_ * v[0] + c_ * v[1], v[2]))
    P0 = np.array(L.Pn(n)(*v)); P1 = np.array(L.Pn(n)(c_ * v[0] - s_ * v[1], s_ * v[0] + c_ * v[1], v[2]))
    print(f'   power {n}, k = {k}: one-plane rule changes by {np.abs(P0 - P1).max():.1e};  wind-then-square changes by up to {np.abs(A0 - A1).max():.2f} (unit vectors), '
          f'median {np.median(np.sqrt(((A0 - A1) ** 2).sum(0))):.2f}')

print('\n== TWO planes. (a) lopsided k = 2 (once round above, three half turns below). EXPECT flat exact, mirror z broken, extra half-planes at 240 and 300 only.')
Fl = L.wind(L.g_lop2()); xx, yy = rng.normal(size=(2, N)); X, Y, Z = Fl(xx, yy, 0 * xx)
print(f'   flat plane error {mx(X - (xx*xx - yy*yy), Y - 2*xx*yy, Z):.1e}')
v = rng.normal(size=(3, N)); A = np.array(Fl(*v)); B = Fl(v[0], v[1], -v[2]); print(f'   F(mirror z) - mirror z of F: {dev((B[0], B[1], -B[2])):.2f}  (order 1 = the solid is not the same above and below)')
aa = np.radians(np.arange(0.0, 360.0, 0.5)); gg = L.g_lop2()(aa)
print('   half-planes sent into the flat plane (deg):', [float(np.degrees(t)) for t, q in zip(aa, gg) if abs(np.sin(q)) < 1e-9])
print('   (b) one fold a side (g_fold2). EXPECT flat exact, mirror z kept, upright plane sent into the flat plane with BOTH halves landing on y < 0:')
Ff = L.wind(L.g_fold2()); X, Y, Z = Ff(xx, yy, 0 * xx); print(f'   flat plane error {mx(X - (xx*xx - yy*yy), Y - 2*xx*yy, Z):.1e}')
A = np.array(Ff(*v)); B = Ff(v[0], v[1], -v[2]); print(f'   F(mirror z) - mirror z of F: {dev((B[0], B[1], -B[2])):.1e}')
for sgn in (1, -1):
    X, Y, Z = Ff(x, 0 * x, sgn * rho); print(f'   upright half-plane z {"> 0" if sgn > 0 else "< 0"}: |Z| {np.abs(Z).max():.1e}; error vs (x - i rho)^2 {mx(X - (x*x - rho*rho), Y + 2*x*rho):.1e}; vs (x + i rho)^2 {mx(Y - 2*x*rho):.2f}')
for name in ('basilica', 'rabbit'):
    c = L.SETS[name]; flat = L.flat_member(U, Sg, c, 60) >= 60
    cut = L.member(Ff, U, 0 * U, Sg, c, 60) >= 60
    dbl = L.flat_member(U, -np.abs(Sg), c, 60) >= 60
    print(f'      {name:9s} upright cut: differs from the flat set at {int((cut ^ flat).sum())} points, from the lower half doubled by a mirror at {int((cut ^ dbl).sum())}')
aa = np.radians(np.array([100.0, 120.0, 134.0])); bb = np.radians(np.array([170.0, 150.0, 136.0]))
print('   fold check: g at 100, 120, 134 deg =', np.degrees(L.g_fold2()(aa)).round(1).tolist(), ' and at 170, 150, 136 deg =', np.degrees(L.g_fold2()(bb)).round(1).tolist(), '(same answers: mirror copies across the crease at 135)')
print('   (c) parity: for any rising g with g(0) = 0 and g(180) = 180 + 360 m, the half-planes strictly above the flat plane sent into it number 2 m (even).')

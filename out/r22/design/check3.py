"""Checks of findings I build on, and bud counts of the new rules.
python out/r22/design/check3.py > out/r22/design/check3.txt"""
import sys, os
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dlib as L
import sheet2 as S2
M, D = L.M, L.D
R = L.refs()


def arcs(ins):
    """Inside arcs on a closed ring of places: (number, widths in degrees)."""
    n = ins.size
    if ins.all():
        return 1, [360.0]
    if not ins.any():
        return 0, []
    k = int(np.argmin(ins)); v = np.roll(ins, -k); w = []; run = 0
    for t in v:
        if t:
            run += 1
        elif run:
            w.append(run * 360.0 / n); run = 0
    if run:
        w.append(run * 360.0 / n)
    return len(w), w


def ring(rule, c, a, u0, rad, n=2880, steps=80):
    """A ring of places round the hinge line (turn a) at the place u0 on it, distance rad from it."""
    ph = np.arange(n) * 2 * np.pi / n; hx, hy = np.cos(a), np.sin(a); nx, ny = -np.sin(a), np.cos(a)
    p, q = rad * np.cos(ph), rad * np.sin(ph)
    return M.stay(rule, u0 * hx + p * nx, u0 * hy + p * ny, q, c[0], c[1], c[2], steps) >= steps


print('A. Basilica, the ring through the top bud of the middle body (x = 0, radius 0.6436) and through the side bud of the left body')
print('   (x = -1.0462, radius 0.3076): inside arcs (the buds section had: one plane 2, along 8 and 16)')
for nm in ['oneplane', 'along', 'lathe'] + [r.name for r in D.RULES]:
    r = R[nm] if nm in R else D.get(nm)
    out = []
    for u0, rad in ((0.0, 0.6436), (-1.0462, 0.3076)):
        k, w = arcs(ring(r, L.BAS, 0.0, u0, rad))
        out.append('%2d arcs, widths %s' % (k, ' '.join('%.1f' % t for t in sorted(w, reverse=True)[:8])))
    print('   %-12s middle body: %s | left body: %s' % (nm, out[0], out[1]))

print('B. Rabbit: rings round the hinge of alonghinge (and the same rings for one plane and along), through the middle of the body round 0')
a = float(D.meeting_turn(*M.RABBIT[:2]))
for rad in (0.30, 0.40, 0.46, 0.50, 0.55):
    line = []
    for nm in ('oneplane', 'along', 'alonghinge'):
        r = R[nm] if nm in R else D.get(nm)
        k, w = arcs(ring(r, M.RABBIT, a, 0.0, rad)); line.append('%s %2d arcs (%.0f deg inside)' % (nm, k, sum(w)))
    print('   radius %.2f: %s' % (rad, ' | '.join(line)))

print('C. Rabbit, alonghinge: is the page through the hinge standing upright the flat rabbit turned upright? (it was for along on the basilica)')
H = D.get('alonghinge'); w, h = 360, 260
up = S2.hinge_cut(H, M.RABBIT, a, 90.0, w, h, 120) >= 120
u, s = np.meshgrid(np.linspace(-1.8, 1.8, w), np.linspace(1.3, -1.3, h))
flat = M.flat_stay(u * np.cos(a) - s * np.sin(a), u * np.sin(a) + s * np.cos(a), M.RABBIT[0], M.RABBIT[1], 300) >= 300
print('   places inside the flat rabbit (turned into that page) %d, inside the upright cut %d, differ %d' % (flat.sum(), up.sum(), (flat != up).sum()))
fl = S2.hinge_cut(H, M.RABBIT, a, 0.0, w, h, 120) >= 120
print('   the flat page itself: differ %d' % (flat != fl).sum())

print('D. One step of alonghinge on the upright page through the hinge (rabbit): how far from the upright plane through c and the meeting point do the points land?')
rng = np.random.default_rng(3); n = 20000
uu, hh = rng.uniform(-1.2, 1.2, n), rng.uniform(-1.0, 1.0, n)
x, y, z = uu * np.cos(a), uu * np.sin(a), hh
X, Y, Z = L.one(H, x, y, z, M.RABBIT); X, Y = X + M.RABBIT[0], Y + M.RABBIT[1]
al = (1 - np.sqrt(1 - 4 * complex(*M.RABBIT[:2]))) / 2; dv = complex(*M.RABBIT[:2]) - al; dv /= abs(dv)
dist = np.abs((X - al.real) * (-dv.imag) + (Y - al.imag) * dv.real)
print('   largest distance after one step %.1e;' % dist.max(), end=' ')
o = L.one(H, X, Y, Z, M.RABBIT); X2, Y2 = o[0] + M.RABBIT[0], o[1] + M.RABBIT[1]
p3 = complex(*M.RABBIT[:2]) ** 2 + complex(*M.RABBIT[:2]); d3 = p3 - al; d3 /= abs(d3)
dist2 = np.abs((X2 - al.real) * (-d3.imag) + (Y2 - al.imag) * d3.real)
print('after two steps, from the upright plane through c^2 + c and the meeting point: median %.3f, largest %.2f' % (np.median(dist2), dist2.max()))

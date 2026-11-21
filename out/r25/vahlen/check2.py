"""Two more identities behind the notes. python out/r25/vahlen/check2.py"""
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import vrules as V
rng = np.random.default_rng(5); n = 20000

# 1. the mixed one-term product  mu b^-1 v b j vbar j^-1 mu^-1  (b = e^(i beta), mu = e^(i (beta/2 + 45 deg)))  is lathe_b(beta - 90)
p = rng.normal(size=(3, n)); zero = np.zeros(n); v = (p[0], p[1], p[2], zero); vb = (p[0], -p[1], -p[2], zero)
one = lambda q: tuple(np.full(n, float(t)) for t in q)
for beta in (0.0, 40.0, 90.0, 200.0):
    b = np.radians(beta); g = b / 2 + np.pi / 4
    bq = one((np.cos(b), np.sin(b), 0, 0)); bi = one((np.cos(b), -np.sin(b), 0, 0)); mu = one((np.cos(g), np.sin(g), 0, 0)); mi = one((np.cos(g), -np.sin(g), 0, 0))
    j = one((0, 0, 1, 0)); ji = one((0, 0, -1, 0))
    t = V.qmul(V.qmul(V.qmul(V.qmul(V.qmul(V.qmul(V.qmul(mu, bi), v), bq), j), vb), ji), mi)
    best = min(max(np.abs(s * t[i] - F[i]).max() for i in range(3)) for s in (1,) for F in (V.lathe_b(beta - 90)(*p), V.lathe_b(beta + 90)(*p)))
    print('beta %5.1f: v b vbar product against the Lathe about a flat axis: %.1e, k part %.1e' % (beta, best, np.abs(t[3]).max()))

# 2. spinor halves about the upright axis: v = (2 a conj(b), |a|^2 - |b|^2); halves squared, times root 2; any phase
a = rng.normal(size=n) + 1j * rng.normal(size=n); b = rng.normal(size=n) + 1j * rng.normal(size=n)
for ph in (0.0, 1.3):
    a1, b1 = a * np.exp(1j * ph), b * np.exp(1j * ph)
    f = 2 * a1 * np.conj(b1); x, y, z = f.real, f.imag, np.abs(a1) ** 2 - np.abs(b1) ** 2
    A, B = np.sqrt(2) * a1 * a1, np.sqrt(2) * b1 * b1; F = 2 * A * np.conj(B); X, Y, Z = F.real, F.imag, np.abs(A) ** 2 - np.abs(B) ** 2
    H = V.holo(x, y, z)
    print('phase %.1f: halves squared against (x^2 - y^2, 2xy, 2 z |v|): %.1e' % (ph, max(np.abs(X - H[0]).max(), np.abs(Y - H[1]).max(), np.abs(Z - H[2]).max())))

# 3. the quaternion square of the spinor DOES depend on the phase: the circle of squares of one point
x, y, z = 0.3, 0.5, 0.4; pts = []
for deg in (0, 30, 60, 90, 120, 150):
    s = V.roll(V.lift_V(np.array([x]), np.array([y]), np.array([z])), deg); w = V.point_of(V.qmul(s, s)); pts.append((w[0][0], w[1][0], w[2][0]))
print('one point (0.3, 0.5, 0.4), spinor rolled by 0..150 degrees, its squares:', ' '.join('(%.2f %.2f %.2f)' % q for q in pts))
print('   the Lathe gives', tuple(round(float(t), 2) for t in V.lathe(x, y, z)), ' and |v|^2 on the x-axis is', round(x * x + y * y + z * z, 2))

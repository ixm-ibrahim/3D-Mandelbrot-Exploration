"""Quick independent check of the triangular-pillow rule (radial layout): exactness on z = 0 and continuity.

Run: python notes/pillow_check.py
"""
import math, random

S3 = math.sqrt(3.0)
ANG = [0.0, 2 * math.pi / 3, 4 * math.pi / 3]


def layout(l):                      # weights (lA, lB, lC) -> direction with z >= 0
    m = min(l)
    s = 1.0 - 3.0 * m
    if s < 1e-14:
        return (0.0, 0.0, 1.0)
    lp = [(x - (1.0 - s) / 3.0) / s for x in l]
    k = min(range(3), key=lambda i: lp[i])          # the weight that is zero names the edge
    if k == 2: tau = ANG[1] * max(0.0, min(1.0, lp[1]))                     # edge AB, 0..120
    elif k == 0: tau = ANG[1] + ANG[1] * max(0.0, min(1.0, lp[2]))          # edge BC, 120..240
    else: tau = ANG[2] + ANG[1] * max(0.0, min(1.0, lp[0]))                 # edge CA, 240..360
    th = 0.5 * math.pi * s
    return (math.sin(th) * math.cos(tau), math.sin(th) * math.sin(tau), math.cos(th))


def layout_inv(dx, dy, dz):         # direction with dz >= 0 -> weights
    th = math.acos(max(-1.0, min(1.0, dz)))
    s = th / (0.5 * math.pi)
    tau = math.atan2(dy, dx) % (2 * math.pi)
    e = min(2, int(tau / ANG[1])); t = tau / ANG[1] - e
    lp = [(1 - t, t, 0.0), (0.0, 1 - t, t), (t, 0.0, 1 - t)][e]
    return [(1.0 - s) / 3.0 + s * x for x in lp]


def phi_inv(d):
    l = layout_inv(d[0], d[1], abs(d[2]))
    sg = -1.0 if d[2] >= 0 else 1.0
    return (l[1] + 0.5 * l[2], sg * 0.5 * S3 * l[2])


def phi(u):
    b = u[1] / (0.5 * S3); a = u[0] + 0.5 * b
    i = math.floor(a); j = math.floor(b); fa = a - i; fb = b - j
    l = [0.0, 0.0, 0.0]
    if fa >= fb:                    # points up: a bottom triangle
        for (ci, cj, w) in ((i, j, 1 - fa), (i + 1, j, fa - fb), (i + 1, j + 1, fb)): l[(ci + cj) % 3] += w
        d = layout(l); return (d[0], d[1], -d[2])
    for (ci, cj, w) in ((i, j, 1 - fb), (i + 1, j + 1, fa), (i, j + 1, fb - fa)): l[(ci + cj) % 3] += w
    return layout(l)


def F(v, n):
    r = math.sqrt(v[0] ** 2 + v[1] ** 2 + v[2] ** 2)
    if r == 0: return (0.0, 0.0, 0.0)
    u = phi_inv((v[0] / r, v[1] / r, v[2] / r))
    d = phi((n * u[0], n * u[1]))
    k = r ** n
    return (k * d[0], k * d[1], k * d[2])


random.seed(7)
print("exactness on z = 0 (worst relative error)")
for n in (2, 3, 4, 5, 8, -1, -2, -3):
    worst = 0.0
    for _ in range(4000):
        r = 10 ** random.uniform(-2, 0.5); a = random.uniform(-math.pi, math.pi)
        if random.random() < 0.3: a = random.choice([0, 2.0944, 3.14159, -2.0944]) + random.uniform(-1e-3, 1e-3)
        z = complex(r * math.cos(a), r * math.sin(a)); w = z ** n
        f = F((z.real, z.imag, 0.0), n)
        worst = max(worst, math.sqrt((f[0] - w.real) ** 2 + (f[1] - w.imag) ** 2 + f[2] ** 2) / abs(w))
    print("  n = %2d  %.2e" % (n, worst))


def rnd_dir():
    while True:
        x, y, z = (random.gauss(0, 1) for _ in range(3))
        r = math.sqrt(x * x + y * y + z * z)
        if r > 1e-6: return (x / r, y / r, z / r)


def near(d, eps):
    e = rnd_dir(); q = [d[i] + eps * e[i] for i in range(3)]
    r = math.sqrt(sum(c * c for c in q)); return tuple(c / r for c in q)


print("continuity: largest |F(d1) - F(d2)| / |d1 - d2| over nearby pairs (a jump would give ~1e4 or more)")
special = [(1, 0, 0), (-0.5, 0.5 * S3, 0), (-0.5, -0.5 * S3, 0), (0, 0, 1), (0, 0, -1), (-1, 0, 0), (0.5, 0.5 * S3, 0), (0, 1, 0)]
for n in (2, 3, -2):
    worst = 0.0; where = None; ratios = []
    for t in range(120000):
        if t % 4 == 0:
            base = random.choice(special); d1 = near(base, 10 ** random.uniform(-6, -1))
        elif t % 4 == 1:              # straddle the equator
            a = random.uniform(0, 2 * math.pi); h = 10 ** random.uniform(-7, -3)
            d1 = (math.cos(a), math.sin(a), h)
            rr = math.sqrt(1 + h * h); d1 = (d1[0] / rr, d1[1] / rr, d1[2] / rr)
        else:
            d1 = rnd_dir()
        d2 = near(d1, 1e-5)
        if t % 4 == 1: d2 = (d2[0], d2[1], -abs(d2[2]))
        f1 = F(d1, n); f2 = F(d2, n)
        num = math.sqrt(sum((f1[i] - f2[i]) ** 2 for i in range(3))); den = math.sqrt(sum((d1[i] - d2[i]) ** 2 for i in range(3)))
        if den > 0:
            q = num / den; ratios.append(q)
            if q > worst: worst, where = q, d1
    ratios.sort()
    print("  n = %2d  max %.1f at %s   99.9%% %.1f   median %.2f" % (n, worst, tuple(round(c, 4) for c in where), ratios[int(0.999 * len(ratios))], ratios[len(ratios) // 2]))

print("round trip Phi(PhiInv(d)) = d:", max(math.sqrt(sum((a - b) ** 2 for a, b in zip(d, phi(phi_inv(d))))) for d in (rnd_dir() for _ in range(20000))))

# does the result depend on which copy of the triangle is used? turn u by 120 degrees about lattice points, shift by colour-A points
def rot(u, c, k):
    a = 2 * math.pi * k / 3; x, y = u[0] - c[0], u[1] - c[1]
    return (c[0] + x * math.cos(a) - y * math.sin(a), c[1] + x * math.sin(a) + y * math.cos(a))
def latt(i, j): return (i - 0.5 * j, 0.5 * S3 * j)
worst = 0.0
for _ in range(20000):
    d = rnd_dir(); u = phi_inv(d); n = random.choice([2, 3, 4, 5, -1, -2, -3, 7])
    i, j = random.randint(-3, 3), random.randint(-3, 3)
    u2 = rot(u, latt(i, j), random.choice([1, 2]))
    while True:
        a, b = random.randint(-4, 4), random.randint(-4, 4)
        if (a + b) % 3 == 0: break
    t = latt(a, b); u2 = (u2[0] + t[0], u2[1] + t[1])
    same = math.sqrt(sum((p - q) ** 2 for p, q in zip(phi(u2), d)))
    f1 = phi((n * u[0], n * u[1])); f2 = phi((n * u2[0], n * u2[1]))
    worst = max(worst, same, math.sqrt(sum((p - q) ** 2 for p, q in zip(f1, f2))))
print("independence of the copy used (should be ~1e-9):", worst)

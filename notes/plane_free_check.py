"""Does the sum of sphere inversions, with NO plane chosen, equal the quaternion square (the Lathe)?

For power 2 the two inversion centres are +1 and -1, both on the x-axis, so the formula needs no plane:
    F(v) = e + 2 * inv( inv(v - e) - inv(v + e) ),   e = (1, 0, 0),   inv(w) = w / |w|^2
The quaternion square of v = x + y i + z j is (x^2 - y^2 - z^2, 2xy, 2xz).

Run: python notes/plane_free_check.py
"""
import math, random

def inv(w):
    s = w[0] * w[0] + w[1] * w[1] + w[2] * w[2]
    return (w[0] / s, w[1] / s, w[2] / s)

def plane_free(v):
    a = inv((v[0] - 1.0, v[1], v[2]))
    b = inv((v[0] + 1.0, v[1], v[2]))
    d = inv((a[0] - b[0], a[1] - b[1], a[2] - b[2]))
    return (1.0 + 2.0 * d[0], 2.0 * d[1], 2.0 * d[2])

def quaternion_square(v):
    x, y, z = v
    return (x * x - y * y - z * z, 2.0 * x * y, 2.0 * x * z)

random.seed(11)
worst = 0.0
for _ in range(200000):
    r = 10 ** random.uniform(-2, 1)
    while True:
        d = [random.gauss(0, 1) for _ in range(3)]
        n = math.sqrt(sum(c * c for c in d))
        if n > 1e-6:
            break
    v = tuple(r * c / n for c in d)
    f, q = plane_free(v), quaternion_square(v)
    size = math.sqrt(sum(c * c for c in q))
    if size < 1e-9:
        continue
    err = math.sqrt(sum((f[i] - q[i]) ** 2 for i in range(3))) / size
    worst = max(worst, err)
print("200,000 random points in space: worst relative difference between the two = %.2e" % worst)
print("a point off both planes, v = (0.3, 0.5, -0.7):", [round(c, 6) for c in plane_free((0.3, 0.5, -0.7))], "against", [round(c, 6) for c in quaternion_square((0.3, 0.5, -0.7))])

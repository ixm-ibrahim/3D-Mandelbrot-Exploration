"""The geometric-algebra recipe of the user's image, checked with real rotor (quaternion) arithmetic.

Recipe: R = the rotor that turns the reference axis a onto the direction of v (the short way); v^2 := |v|^2 R^2 a R^-2.
Claims: (1) with a = x-axis this is the quaternion square (x^2-y^2-z^2, 2xy, 2xz), the lab's Lathe;
        (2) with any other a it is the same rule turned in space;
        (3) the frame version R = Rz(lon) Ry(lat): flat plane exact; plane y = 0 exact only for x > 0.
Run: python out/me/r14/rotor_check.py
"""
import math, random

def qmul(p, q):
    a, b, c, d = p; e, f, g, h = q
    return (a*e - b*f - c*g - d*h, a*f + b*e + c*h - d*g, a*g - b*h + c*e + d*f, a*h + b*g - c*f + d*e)
def qconj(q): return (q[0], -q[1], -q[2], -q[3])
def rot(q, v):
    w = qmul(qmul(q, (0.0,) + tuple(v)), qconj(q)); return w[1:]
def axis_angle(n, t):
    s = math.sin(t / 2); return (math.cos(t / 2), n[0] * s, n[1] * s, n[2] * s)
def cross(a, b): return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])
def dot(a, b): return sum(x*y for x, y in zip(a, b))
def norm(a): return math.sqrt(dot(a, a))
def unit(a): n = norm(a); return tuple(x / n for x in a)

def rotor_square(v, a):
    """|v|^2 R^2 a R^-2 with R the short-way rotor from a to v/|v|."""
    r = norm(v); d = unit(v)
    n = cross(a, d); s = norm(n)
    if s < 1e-12: return tuple(r * r * x for x in a)        # v along a (or against it: the turn has no single sheet)
    R = axis_angle(unit(n), math.atan2(s, dot(a, d)))
    return tuple(r * r * x for x in rot(qmul(R, R), a))
def lathe(v): x, y, z = v; return (x*x - y*y - z*z, 2*x*y, 2*x*z)

random.seed(5)
pts = [tuple(random.uniform(-1.5, 1.5) for _ in range(3)) for _ in range(20000)]
ex = (1.0, 0.0, 0.0)
w1 = max(norm(tuple(p - q for p, q in zip(rotor_square(v, ex), lathe(v)))) for v in pts)
print("1. reference = x-axis: worst difference from the quaternion square on 20,000 points = %.1e" % w1)

worst = 0.0
for _ in range(200):
    a = unit(tuple(random.gauss(0, 1) for _ in range(3)))
    n = cross(ex, a); s = norm(n)
    T = axis_angle(unit(n), math.atan2(s, dot(ex, a)))          # the turn that carries the x-axis to a
    for v in pts[:100]:
        lhs = rotor_square(v, a)
        rhs = rot(T, lathe(rot(qconj(T), v)))                     # turn back, Lathe, turn forward
        worst = max(worst, norm(tuple(p - q for p, q in zip(lhs, rhs))))
print("2. any reference axis: worst difference from (turn, Lathe, turn back) on 200 axes x 100 points = %.1e" % worst)
ez = (0.0, 0.0, 1.0)
print("   reference = z-axis, a point of the flat plane (0.6, 0.5, 0):", [round(x, 4) for x in rotor_square((0.6, 0.5, 0.0), ez)],
      " (complex squaring would give", [round(x, 4) for x in (0.6*0.6 - 0.25, 2*0.6*0.5, 0.0)], ")")

def frame_square(v):
    r = norm(v); d = unit(v)
    lon = math.atan2(d[1], d[0]); lat = math.atan2(d[2], math.hypot(d[0], d[1]))
    R = qmul(axis_angle((0, 0, 1), lon), axis_angle((0, -1, 0), lat))     # tip up by lat, then turn about z by lon
    assert norm(tuple(p - q for p, q in zip(rot(R, ex), d))) < 1e-9
    return tuple(r * r * x for x in rot(qmul(R, R), ex))
wf = 0.0; wy = 0.0; wneg = 0.0
for _ in range(5000):
    x, y = random.uniform(-1.5, 1.5), random.uniform(-1.5, 1.5)
    f = frame_square((x, y, 0.0)); wf = max(wf, norm((f[0] - (x*x - y*y), f[1] - 2*x*y, f[2])))
    xp, z = random.uniform(0.01, 1.5), random.uniform(-1.5, 1.5)
    f = frame_square((xp, 0.0, z)); wy = max(wy, norm((f[0] - (xp*xp - z*z), f[1], f[2] - 2*xp*z)))
    f = frame_square((-xp, 0.0, z)); wneg = max(wneg, norm((f[0] - (xp*xp - z*z), f[1], f[2] + 2*xp*z)))
print("3. frame version: flat plane, worst difference from complex squaring = %.1e" % wf)
print("   plane y = 0, x > 0: worst difference = %.1e;   x < 0: worst difference = %.2f (not squaring there)" % (wy, wneg))
print("   a point with x < 0 in the plane y = 0, (-0.6, 0, 0.5) ->", [round(x, 4) for x in frame_square((-0.6, 0.0, 0.5))])
d = 0.0
for v in pts[:5000]:
    d = max(d, norm(tuple(p - q for p, q in zip(frame_square(v), lathe(v)))))
print("   frame version against the Lathe on 5,000 points: worst difference = %.2f (a different rule)" % d)

"""The "fixed spheres" variant of the sphere-inversion power, characterised numerically.

Following spheres (what the lab draws):  v^n = |v|^n * F(v / |v|)
Fixed spheres (this script):             v^n = F(v)
with F(q) = 1 + n * inv( sum_k R_k inv(q - w_k) ), w_k the n-th roots of unity on the unit circle of the
xy-plane, R_k the turn about the z-axis by the angle of w_k, inv(v) = (x, -y, -z) / |v|^2.

Run:  python notes/fixed_spheres.py          (prints the numbers quoted in notes/inversions.md and writes
                                              the slice pictures to out/approaches/fixed-*.png)
"""
import math, os
import numpy as np
from PIL import Image

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "out", "approaches")
os.makedirs(OUT, exist_ok=True)


def inv(v):
    r2 = np.maximum((v * v).sum(-1, keepdims=True), 1e-300)
    return v * np.array([1.0, -1.0, -1.0]) / r2


def rotz(v, t):
    c, s = math.cos(t), math.sin(t)
    return np.stack([c * v[..., 0] - s * v[..., 1], s * v[..., 0] + c * v[..., 1], v[..., 2]], -1)


def fixed(q, n):
    """F(q): the inversion formula applied to the point itself."""
    acc = np.zeros_like(q)
    for k in range(n):
        t = 2 * math.pi * k / n
        acc = acc + rotz(inv(q - np.array([math.cos(t), math.sin(t), 0.0])), t)
    out = n * inv(acc)
    out[..., 0] += 1.0
    return out


def mercator(v, n):
    r = np.sqrt((v * v).sum(-1))
    Z = np.clip(v[..., 2] / r, -0.999999999999, 0.999999999999)
    Zn = np.tanh(n * np.arctanh(Z)); h = np.sqrt(np.maximum(0, 1 - Zn * Zn)); p = np.arctan2(v[..., 1], v[..., 0]) * n
    R = r ** n
    return np.stack([R * h * np.cos(p), R * h * np.sin(p), R * Zn], -1)


def following(v, n):
    r = np.sqrt((v * v).sum(-1, keepdims=True))
    return r ** n * fixed(v / r, n)


def length(v):
    return np.sqrt((v * v).sum(-1))


rng = np.random.default_rng(7)
print("1. Where the two versions agree, and where they part")
for n in (2, 3, 4, 8):
    d = rng.normal(size=(4000, 3)); d /= length(d)[:, None]
    d = d[np.abs(d[:, 2]) < 0.999]
    on_sphere = length(fixed(d, n) - mercator(d, n)).max()
    a = rng.uniform(0, 2 * math.pi, 4000); r = rng.uniform(0.2, 1.8, 4000)
    flat = np.stack([r * np.cos(a), r * np.sin(a), 0 * a], -1)
    want = np.stack([r ** n * np.cos(n * a), r ** n * np.sin(n * a), 0 * a], -1)
    in_plane = (length(fixed(flat, n) - want) / (1 + r ** n)).max()
    q = d * rng.uniform(0.3, 2.5, len(d))[:, None]
    off = length(fixed(q, n) - mercator(q, n)) / (1 + length(q) ** n)
    ratio = length(fixed(q, n)) / length(q) ** n
    print(f"  n={n}: unit sphere, fixed vs Mercator {on_sphere:.1e};  plane z=0, fixed vs complex z^n {in_plane:.1e};  "
          f"elsewhere they differ by up to {off.max():.2f} (relative), and |F(q)|/|q|^n runs from {ratio.min():.3g} to {ratio.max():.3g}")

print("2. The z-axis: F leaves every point of it where it is")
for n in (2, 3, 8):
    t = np.array([[0, 0, s] for s in (-5, -1.3, -0.2, 0.4, 1, 3, 40.0)])
    print(f"  n={n}: max |F(0,0,t) - (0,0,t)| = {length(fixed(t, n) - t).max():.1e}")

print("3. Growth far from the origin: |F(q)| at |q| = 100, by latitude (a true n-th power would give 100^n)")
for n in (2, 3, 8):
    row = []
    for lat in (0, 0.01, 0.1, 5, 30, 60, 89):
        la = math.radians(lat); q = 100 * np.array([[math.cos(la) * math.cos(0.3), math.cos(la) * math.sin(0.3), math.sin(la)]])
        row.append(f"{lat}°: {length(fixed(q, n))[0]:.3g}")
    print(f"  n={n}: " + ", ".join(row))
print("   Off the plane the growth is about |q| / sin(latitude): linear in |q|, not |q|^n.")


def escape(c, n, iters, rule, bail=64.0):
    """Mandelbrot-style count for z -> rule(z) + c from z = 0. Returns the step of escape (iters if never)."""
    z = np.zeros_like(c); out = np.full(c.shape[:-1], iters, dtype=np.int32); live = np.ones(c.shape[:-1], bool)
    for i in range(iters):
        zl = z[live]
        r = length(zl)
        w = np.where((r > 1e-12)[:, None], rule(np.where((r > 1e-12)[:, None], zl, 1.0), n), 0.0) + c[live]
        z[live] = w
        gone = length(w) > bail
        idx = np.flatnonzero(live)
        out[idx[gone]] = i + 1
        live[idx[gone]] = False
        if not live.any():
            break
    return out


def picture(name, plane, n, iters, rule, half=2.2, centre=(-0.4, 0.0), size=360, level=0.0):
    xs = np.linspace(centre[0] - half, centre[0] + half, size); ys = np.linspace(centre[1] + half, centre[1] - half, size)
    X, Y = np.meshgrid(xs, ys)
    if plane == "xy":
        c = np.stack([X, Y, np.full_like(X, level)], -1)
    else:  # xz
        c = np.stack([X, np.full_like(X, level), Y], -1)
    e = escape(c.reshape(-1, 3), n, iters, rule).reshape(size, size)
    inside = e >= iters
    shade = (255 * (0.25 + 0.75 * np.minimum(e, 24) / 24)).astype(np.uint8)
    img = np.stack([np.where(inside, 20, shade), np.where(inside, 24, shade), np.where(inside, 40, shade)], -1).astype(np.uint8)
    Image.fromarray(img).save(os.path.join(OUT, name))
    return inside


print("4. The set of z -> z^2 + c from z = 0, counted on a 360 x 360 grid of c (share of the grid that never escapes)")
for iters in (14, 60, 240):
    fx = picture(f"fixed-n2-xz-{iters}.png", "xz", 2, iters, fixed)
    fo = picture(f"following-n2-xz-{iters}.png", "xz", 2, iters, following)
    fp = picture(f"fixed-n2-xy-{iters}.png", "xy", 2, iters, fixed)
    print(f"  {iters} steps: slice y=0  fixed {fx.mean():.3f}, following {fo.mean():.3f};  slice z=0 fixed {fp.mean():.3f}")
print("   On the z-axis itself the fixed version only adds c each step (z_k = k c), so a point (0, 0, t) leaves")
print("   the radius-64 ball after 64/|t| steps: the solid there is a spike whose height is 64 / (number of steps).")
for iters in (14, 60, 240, 1000):
    t = np.linspace(0.001, 8, 4000); c = np.stack([0 * t, 0 * t, t], -1)
    e = escape(c, 2, iters, fixed)
    top = t[e >= iters].max() if (e >= iters).any() else 0
    print(f"  {iters} steps: the solid reaches up the z-axis to {top:.2f}   (64/steps = {64 / iters:.2f})")
print("5. A horizontal slice a little above the plane (z = 0.3), fixed version, by step count")
for iters in (14, 60, 240):
    s = picture(f"fixed-n2-z03-{iters}.png", "xy", 2, iters, fixed, level=0.3)
    print(f"  {iters} steps: share never escaping {s.mean():.3f}")

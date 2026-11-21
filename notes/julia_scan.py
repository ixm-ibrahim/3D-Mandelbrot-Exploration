"""How solid is a Julia set of the sphere-inversion ("mercator") approach? A check that does not use the renderer.

  python notes/julia_scan.py                         table for every preset in data/julia-presets.json
  python notes/julia_scan.py -1 0.08 0.08 [planes [iterations]]   one constant

The squaring rule is a numpy port of MATH.mercator / GL_MERCATOR in base/js/10-approaches.js at n = 2,
with the same fold onto the nearest of k planes, and the same test the shader uses for "inside":
the orbit has not passed |v| = 64 after the preset's iteration count (14, the lab's default, unless it says more).

For a grid of start points in the cube [-2.2, 2.2]^3 it reports
  volume    the filled volume in cubic scene units (the unit ball, c = 0, is 4.19)
  pieces    how many separate pieces the filled cells form (26-neighbour connectivity)
  largest   the share of the volume in the largest piece
  extent    the half-width of the set along x, y and z
A preset worth showing has one dominant piece. Dust shows up as a small volume in many pieces.
"""
import json, math, os, sys
import numpy as np
from scipy import ndimage

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def foldk(v, k):
    """Fold the spin angle around the x-axis so the nearest of k planes through that axis lands on the xy-plane."""
    if k < 1.5:
        return v
    x, y, z = v
    rho = np.hypot(y, z)
    w = math.pi / k
    psi = np.arctan2(z, y)
    s = np.where(psi < 0, -1.0, 1.0)
    a = np.abs(psi)
    j = np.floor(a / w + 0.5)
    d = a - j * w
    near = (2 * j < k - 0.5) | ((np.abs(2 * j - k) < 0.5) & (d < 0))
    a2 = np.where(near, np.where(np.mod(j, 2) < 0.5, d, -d), math.pi + np.where(np.mod(k - j, 2) < 0.5, d, -d)) * s
    return x, rho * np.cos(a2), rho * np.sin(a2)


def msq(v):
    x, y, z = v
    r2 = x * x + y * y + z * z
    f = np.where(r2 > 1e-30, r2 / np.maximum(r2 + z * z, 1e-300), 0.0)
    return f * (x * x - y * y), f * 2 * x * y, f * 2 * np.sqrt(r2) * z


def filled(c, planes=2, iters=14, n=120, box=2.2, bail=64.0):
    g = np.linspace(-box, box, n)
    v = np.meshgrid(g, g, g, indexing="ij")
    cf = foldk(tuple(np.array(float(t)) for t in c), planes)
    alive = np.ones((n, n, n), bool)
    with np.errstate(over="ignore", invalid="ignore"):
        for _ in range(iters):
            r = np.sqrt(v[0] ** 2 + v[1] ** 2 + v[2] ** 2)
            alive &= ~(r > bail)
            w = msq(foldk(v, planes))
            v = [np.where(alive, w[i] + cf[i], v[i]) for i in range(3)]
        r = np.sqrt(v[0] ** 2 + v[1] ** 2 + v[2] ** 2)
        alive &= ~(r > bail)
    return alive, g


def facts(c, planes=2, **kw):
    inside, g = filled(c, planes, **kw)
    cell = (g[1] - g[0]) ** 3
    lab, count = ndimage.label(inside, structure=np.ones((3, 3, 3)))
    sizes = np.bincount(lab.ravel())[1:] if count else np.array([0])
    idx = np.argwhere(inside)
    ext = [float(np.abs(g[idx[:, i]]).max()) if len(idx) else 0.0 for i in range(3)]
    total = float(inside.sum() * cell)
    return {"volume": total, "pieces": int(count), "largest": float(sizes.max() * cell / total) if total else 0.0, "extent": ext}


def line(name, c, planes, iters=14):
    f = facts(c, planes, iters=iters)
    return "%-28s c = (%9.6f, %9.6f, %9.6f)  %d pl  %2d it  volume %5.2f  pieces %4d  largest %5.1f%%  extent %.2f %.2f %.2f" % (
        name[:28], c[0], c[1], c[2], planes, iters, f["volume"], f["pieces"], 100 * f["largest"], *f["extent"])


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")   # preset names hold a true minus sign
    args = sys.argv[1:]
    if len(args) >= 3:
        c = [float(a) for a in args[:3]]
        print(line("given", c, int(args[3]) if len(args) > 3 else 2, int(args[4]) if len(args) > 4 else 14))
        return
    with open(os.path.join(ROOT, "data", "julia-presets.json"), encoding="utf-8") as f:
        presets = json.load(f)
    print(line("reference: unit ball, c = 0", [0, 0, 0], 1))
    for p in presets:
        print(line(p["name"], p["c"], int(p.get("planes", 2)), int(p.get("iter", 14))))


if __name__ == "__main__":
    main()

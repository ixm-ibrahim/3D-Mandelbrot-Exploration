"""The eyes' views for section 1.4 c (holes, missing balls, shells, noise). Every view is reached the way a hand
reaches it: Reset this section, a typed size, (a typed second sphere), the grid, a typed depth, Frame it, and then,
for a close view, the camera.

A view: grid (0 square, 1 honeycomb, 2 a line only), p (typed into Size of the neighbours), rho (typed into Second
sphere, in %; None = whatever the size dial made it), depth, cam (None = the start view, or (target, direction from
the target to the eye, distance)), flat (the 2D view; then cam is None or (x, y, h) for S.v2).

  python out/r28/fix/eyes/mk/views.py     -> logs/cams.txt: every eye checked with my own recipe (outside every ball,
                                         and how far the nearest solid point is by a walk on shells)
"""
import math, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import recipe

K2 = 1.05
KISS = (0.525, 0.0, 0.0)


def bud(p, a, b):
    """where the whole number (a, b) of the top wall lands on the right neighbour (picture coordinates)"""
    h = 100.0 / p; D = h * h + a * a + b * b
    return (0.525 + K2 * h / D, K2 * a / D, K2 * b / D)


def neighbour(p):
    R = 0.525 * p / 100.0
    return (0.525 + R, 0.0, 0.0), R


def unit(v):
    n = math.sqrt(sum(x * x for x in v)); return tuple(x / n for x in v)


def outward(p, T, tilt=(0.0, 0.0, 0.0)):
    """from the neighbour's centre out through T, tilted by `tilt`"""
    C, R = neighbour(p)
    n = unit(tuple(T[i] - C[i] for i in range(3)))
    return unit(tuple(n[i] + tilt[i] for i in range(3)))


def expected_rho(p, rho):
    """what the dials should hold after: reset, size typed p, second sphere typed rho (decisions 1.2 point 4)"""
    r = 1.0
    if p * r > 100 * (1 + 1e-9):
        r = max(0.02, min(0.5, 50.0 / p))
    if rho is not None:
        r2 = 1.0 if rho > 75 else min(0.5, max(0.02, rho / 100.0))
        if p * r2 > 100 * (1 + 1e-9):
            p = 50.0 / r2
        r = r2
    return p, r


V = {}
# ---- the start view
V['p101-r50-start'] = dict(grid=0, p=101, rho=50, depth=16, cam=None)
V['p150-r50-start'] = dict(grid=0, p=150, rho=50, depth=16, cam=None)
V['p199.9-r50-start'] = dict(grid=0, p=199.9, rho=50, depth=16, cam=None)
V['p200-r50-start'] = dict(grid=0, p=200, rho=50, depth=16, cam=None)
V['p300-r25-start'] = dict(grid=0, p=300, rho=25, depth=16, cam=None)
V['p400-r25-hex-start'] = dict(grid=1, p=400, rho=25, depth=16, cam=None)
V['p300-r12.5-hex-start'] = dict(grid=1, p=300, rho=12.5, depth=16, cam=None)
V['p400-r12.5-line-start'] = dict(grid=2, p=400, rho=12.5, depth=16, cam=None)
V['p1000-start'] = dict(grid=0, p=1000, rho=None, depth=16, cam=None)
V['p2000-start'] = dict(grid=0, p=2000, rho=None, depth=16, cam=None)
V['p150-auto-line-start'] = dict(grid=2, p=150, rho=None, depth=16, cam=None)
# ---- a close view of a neighbour
V['p150-r50-hex-neighbour'] = dict(grid=1, p=150, rho=50, depth=16, cam=(bud(150, 1, 0), outward(150, bud(150, 1, 0), (0.25, 0.0, 0.45)), 0.7))
V['p200-r50-hex-neighbour'] = dict(grid=1, p=200, rho=50, depth=16, cam=(bud(200, 1, 0), outward(200, bud(200, 1, 0), (0.2, 0.0, -0.5)), 0.6))
V['p400-r25-neighbour'] = dict(grid=0, p=400, rho=25, depth=16, cam=(bud(400, 1, 1), outward(400, bud(400, 1, 1), (0.3, 0.1, 0.0)), 0.8))
V['p400-r12.5-far-pole'] = dict(grid=0, p=400, rho=12.5, depth=16, cam=((0.525 + 4.2, 0.0, 0.0), unit((0.8, -0.4, 0.45)), 0.6))
V['p300-r25-graze'] = dict(grid=0, p=300, rho=25, depth=16, cam=((2.1 + 1.575 * 0.3078, 1.575 * 0.2052, 1.575 * 0.9290), unit((0.55, 0.80, 0.22)), 1.1))
V['p1000-middle'] = dict(grid=0, p=1000, rho=None, depth=16, cam=((0.0, 0.0, 0.0), unit((0.05, -0.8, 0.6)), 2.6))
# ---- where two balls kiss (the eye stands in the plane x = k^2 / 2 that touches both balls there, or just off it)
V['p199.9-r50-kiss'] = dict(grid=0, p=199.9, rho=50, depth=16, cam=(KISS, unit((0.0, -0.95, 0.31)), 0.4))
V['p200-r50-line-kiss'] = dict(grid=2, p=200, rho=50, depth=16, cam=(KISS, unit((0.0, 0.76, -0.65)), 0.45))
V['p200-r50-kiss-near'] = dict(grid=0, p=200, rho=50, depth=16, cam=(KISS, unit((0.0, 0.92, 0.39)), 0.12))
# ---- along the chain
V['p150-auto-along'] = dict(grid=0, p=150, rho=None, depth=16, cam=((1.3, 0.0, 0.0), unit((2.9, 0.35, 0.5)), 2.96))
V['p300-auto-hex-along'] = dict(grid=1, p=300, rho=None, depth=16, cam=((2.1, 0.0, 0.0), unit((3.4, -0.3, 0.45)), 3.45))
# ---- the 2D view
V['p150-r50-2d'] = dict(grid=0, p=150, rho=50, depth=16, cam=None, flat=True)
V['p200-r50-2d'] = dict(grid=0, p=200, rho=50, depth=16, cam=None, flat=True)
V['p300-r25-2d'] = dict(grid=1, p=300, rho=25, depth=16, cam=None, flat=True)
V['p1000-2d'] = dict(grid=2, p=1000, rho=None, depth=16, cam=None, flat=True)
V['p199.9-r50-2d-kiss'] = dict(grid=0, p=199.9, rho=50, depth=16, cam=(0.525, 0.0, 0.5), flat=True)
V['p400-r25-2d-neighbour'] = dict(grid=0, p=400, rho=25, depth=16, cam=(0.9, 0.9, 1.2), flat=True)
# ---- small values and long searches (section 1.4 c, last sentence)
V['p2-start'] = dict(grid=0, p=2, rho=None, depth=16, cam=None)
V['p2-r2-start'] = dict(grid=0, p=2, rho=2, depth=16, cam=None)
V['p2-close'] = dict(grid=0, p=2, rho=None, depth=16, cam=(KISS, unit((0.3, -0.8, 0.5)), 0.25))
V['depth1'] = dict(grid=0, p=55.56, rho=None, depth=1, cam=None)
V['depth3'] = dict(grid=0, p=55.56, rho=None, depth=3, cam=None)
V['depth5'] = dict(grid=0, p=55.56, rho=None, depth=5, cam=None)
V['depth100'] = dict(grid=0, p=55.56, rho=None, depth=100, cam=None)
V['depth400'] = dict(grid=0, p=55.56, rho=None, depth=400, cam=None)
V['p150-depth1'] = dict(grid=0, p=150, rho=None, depth=1, cam=None)
V['p150-depth3'] = dict(grid=0, p=150, rho=None, depth=3, cam=None)
V['p150-depth5'] = dict(grid=0, p=150, rho=None, depth=5, cam=None)
V['p150-r50-depth100'] = dict(grid=0, p=150, rho=50, depth=100, cam=None)
V['p200-r50-depth400'] = dict(grid=0, p=200, rho=50, depth=400, cam=None)
V['p200-r50-depth400-kiss'] = dict(grid=0, p=200, rho=50, depth=400, cam=(KISS, unit((0.0, -0.95, 0.31)), 0.4))
V['p100-depth400-2d'] = dict(grid=0, p=100, rho=None, depth=400, cam=None, flat=True)
V['p2000-r2-start'] = dict(grid=0, p=2000, rho=2, depth=16, cam=None)

# ---- second look at a find: with the second sphere at 50 the 2D view paints a bump where two buds on a neighbour kiss
BK = bud(150, 0.5, 0)       # the point of the right neighbour's skin where the buds at the whole numbers 0 and 1 kiss (p = 150)
V['p150-r50-2d-budkiss'] = dict(grid=0, p=150, rho=50, depth=16, cam=(BK[0] + 0.01, BK[1] + 0.045, 0.3), flat=True)
V['p150-r50-2d-budkiss-d100'] = dict(grid=0, p=150, rho=50, depth=100, cam=(BK[0] + 0.01, BK[1] + 0.045, 0.3), flat=True)
V['p150-r50-budkiss'] = dict(grid=0, p=150, rho=50, depth=16, cam=(BK, outward(150, BK, (0.35, 0.0, 0.5)), 0.35))
V['p150-r50-budkiss-d100'] = dict(grid=0, p=150, rho=50, depth=100, cam=(BK, outward(150, BK, (0.35, 0.0, 0.5)), 0.35))
V['p55-r50-2d'] = dict(grid=0, p=55.56, rho=50, depth=16, cam=None, flat=True)
V['p100-r50-2d'] = dict(grid=0, p=100, rho=50, depth=16, cam=None, flat=True)
V['p100-r50-hex-2d'] = dict(grid=1, p=100, rho=50, depth=16, cam=None, flat=True)
V['p101-auto-2d'] = dict(grid=0, p=101, rho=None, depth=16, cam=None, flat=True)
V['p150-r48-2d'] = dict(grid=0, p=150, rho=48, depth=16, cam=None, flat=True)
V['p150-r40-2d'] = dict(grid=0, p=150, rho=40, depth=16, cam=None, flat=True)
V['p150-auto-2d'] = dict(grid=0, p=150, rho=None, depth=16, cam=None, flat=True)
V['p55-r100-2d'] = dict(grid=0, p=55.56, rho=None, depth=16, cam=None, flat=True)      # the old object, for the same measure

# ---- second look at a find: faint cracks in the shading of a neighbour's bare skin (seen at 400 with the second sphere at 25)
V['p300-r25-neighbour'] = dict(grid=0, p=300, rho=25, depth=16, cam=(bud(300, 1, 1), outward(300, bud(300, 1, 1), (0.3, 0.1, 0.0)), 0.8))
V['p400-r25-neighbour-d100'] = dict(grid=0, p=400, rho=25, depth=100, cam=(bud(400, 1, 1), outward(400, bud(400, 1, 1), (0.3, 0.1, 0.0)), 0.8))
V['p390-r25-neighbour'] = dict(grid=0, p=390, rho=25, depth=16, cam=(bud(390, 1, 1), outward(390, bud(390, 1, 1), (0.3, 0.1, 0.0)), 0.8))
V['p150-r49-budkiss'] = dict(grid=0, p=150, rho=49, depth=16, cam=(BK, outward(150, BK, (0.35, 0.0, 0.5)), 0.35))
V['p150-r49-2d-budkiss'] = dict(grid=0, p=150, rho=49, depth=16, cam=(BK[0] + 0.01, BK[1] + 0.045, 0.3), flat=True)
V['p60-r50-2d-budkiss'] = dict(grid=0, p=60, rho=50, depth=16, cam=(bud(60, 0.5, 0)[0], bud(60, 0.5, 0)[1] + 0.02, 0.2), flat=True)

for k, v in V.items():
    v.setdefault('flat', False)


def cam_numbers(v):
    """(yaw, pitch, dist, target) for the page: the eye is target + dist (cos pitch cos yaw, cos pitch sin yaw, sin pitch)"""
    T, n, d = v['cam']
    return [math.atan2(n[1], n[0]), math.asin(max(-1.0, min(1.0, n[2]))), d, list(T)]


if __name__ == '__main__':
    lines = []
    rng = np.random.default_rng(7)
    dirs = rng.normal(size=(6000, 3)); dirs /= np.linalg.norm(dirs, axis=1)[:, None]
    for name, v in V.items():
        if v['flat'] or v['cam'] is None:
            continue
        p, rho = expected_rho(v['p'], v['rho'])
        top = 1 + 100.0 / p
        T, n, d = v['cam']
        eye = np.array(T) + d * np.array(n)
        ve = int(recipe.verdict(eye[None, :], top, rho, v['grid'], 300)[0])
        # how far the nearest solid point is: shells round the eye, each a tenth wider than the last
        free = None; r = 1e-4
        while r < 30:
            if recipe.solid(eye[None, :] + r * dirs, top, rho, v['grid'], 300).any():
                free = r; break
            r *= 1.1
        y, pi, dd, tt = cam_numbers(v)
        lines.append('%-26s p %-6s rho %.4f grid %d: eye (%.4f, %.4f, %.4f) verdict %d (0 = outside every ball); first solid point on shells at about %s; yaw %.4f pitch %.4f dist %.3f'
                     % (name, p, rho, v['grid'], eye[0], eye[1], eye[2], ve, 'none within 30' if free is None else '%.4g' % free, y, pi, dd))
    text = '\n'.join(lines) + '\n'
    os.makedirs(os.path.join(os.path.dirname(HERE), 'logs'), exist_ok=True)
    open(os.path.join(os.path.dirname(HERE), 'logs', 'cams.txt'), 'w', encoding='utf-8', newline='\n').write(text)
    print(text)

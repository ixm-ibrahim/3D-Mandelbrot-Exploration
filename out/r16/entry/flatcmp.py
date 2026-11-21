"""Round 16, entry: (1) the page's 2D view of the cut at z = 0 for the two Turning plane rules against Sphere inversions,
one plane (whose cut is the flat set), same page, same settings, pixel by pixel. (2) with numpy: the sideways stretch
of "along" in the plane y = z, and the brief's literal q = -1 at power 3."""
import sys, numpy as np
from PIL import Image
D = 'out/r16/entry/'
for t in ('ta', 'tl'):
    for n in ('cut-m', 'cut-bas', 'cut-rabbit', 'cut-off'):
        a = np.asarray(Image.open(D + t + '-' + n + '.png').convert('RGB')).astype(int)
        b = np.asarray(Image.open(D + 'ref-' + n + '.png').convert('RGB')).astype(int)
        d = np.abs(a - b).max(axis=2)
        print('%s-%-11s %dx%d: pixels that differ at all: %d, by more than 8 levels: %d' % (t, n, a.shape[1], a.shape[0], int((d > 0).sum()), int((d > 8).sum())))
sys.path.insert(0, 'out/me/r16')
import scout as S, scout3
F = scout3.turning(1)
print('\n"along", power 2: a point of the plane y = z at the angle t from the x-axis, moved sideways by d = 1e-6 rad round the x-axis;')
print('how far its answer leaves the plane y = z, divided by (d * distance from the x-axis). Formula: 4x - 2r.')
for tdeg in (20, 40, 55, 59, 60, 61, 65, 90, 120, 150, 170):
    t = np.radians(tdeg); r = 1.0; x, rho = r * np.cos(t), r * np.sin(t); d = 1e-6
    ph = np.pi / 4 + d
    X, Y, Z = F(np.array([x]), np.array([rho * np.cos(ph)]), np.array([rho * np.sin(ph)]))
    off = (Z[0] - Y[0]) / np.sqrt(2)          # distance from the plane y = z, signed
    print('  t = %3d deg: measured %+.4f   formula %+.4f' % (tdeg, off / (d * rho), 4 * x - 2 * r))

def gen(n, q, m):
    def G(x, y, z):
        phi = np.arctan2(z, y); psi = q * (phi - np.sin(2 * m * phi) / (2 * m)); c, s = np.cos(psi), np.sin(psi)
        yy, zz = c * y + s * z, -s * y + c * z
        r = np.sqrt(x * x + yy * yy + zz * zz); Zr = np.clip(zz / r, -0.999999, 0.999999); mm = n * np.arctanh(Zr); p = np.arctan2(yy, x) * n; R = r ** n
        X, Y, Zo = R * np.cos(p) / np.cosh(mm), R * np.sin(p) / np.cosh(mm), R * np.tanh(mm)
        return X, c * Y - s * Zo, s * Y + c * Zo
    return G
rng = np.random.default_rng(1)
print('\npower 3, "away": does the plane at 60 degrees round the x-axis follow the complex cube? largest distance from it, as a share of the length (500 points)')
for q, tag in ((-1, 'the brief\'s q = -1'), (-2, 'q = 1 - m = -2 (what the entry uses)')):
    G = gen(3, q, 3); a = np.radians(60)
    r = 0.05 + 1.5 * rng.random(500); t = (rng.random(500) * 2 - 1) * np.pi; x, rho = r * np.cos(t), r * np.sin(t)
    X, Y, Z = G(x, rho * np.cos(a), rho * np.sin(a)); R = r ** 3
    e = np.sqrt((X - R * np.cos(3 * t)) ** 2 + (Y - R * np.sin(3 * t) * np.cos(a)) ** 2 + (Z - R * np.sin(3 * t) * np.sin(a)) ** 2) / R
    # and the turn by 60 degrees about the x-axis: does the rule commute with it?
    P = rng.normal(size=(500, 3)); ca, sa = np.cos(a), np.sin(a)
    A = np.stack(G(P[:, 0], ca * P[:, 1] - sa * P[:, 2], sa * P[:, 1] + ca * P[:, 2]), 1); B = np.stack(G(P[:, 0], P[:, 1], P[:, 2]), 1)
    B = np.stack([B[:, 0], ca * B[:, 1] - sa * B[:, 2], sa * B[:, 1] + ca * B[:, 2]], 1)
    print('  %-38s plane at 60 degrees: %.2e;   turn by 60 degrees about the x-axis: off by %.2e of the length' % (tag, e.max(), (np.linalg.norm(A - B, axis=1) / np.linalg.norm(P, axis=1) ** 3).max()))

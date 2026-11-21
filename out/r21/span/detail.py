"""Closer looks.
python out/r21/span/detail.py fan            -> fan-rabbit.png : the rabbit of "the point and c", cut by planes through the line of c
python out/r21/span/detail.py tears          -> tears.txt      : how big the jumps are where the plane is not defined
python out/r21/span/detail.py cuts <rule>... -> cuts-<rule>.png: Julia cuts at 0, 11.25, 22.5, 33.75, 90 degrees and across, two eye positions
"""
import os, sys, time
import numpy as np
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import myrules as R
M = R.M


def cut_plane(rule, o, e1, e2, hw, w, h, steps, c):
    """A cut by the plane through o spanned by the unit vectors e1 (to the right) and e2 (up)."""
    u, s = np.meshgrid(np.linspace(-hw, hw, w), np.linspace(hw * h / w, -hw * h / w, h))
    Pt = [o[i] + u * e1[i] + s * e2[i] for i in range(3)]
    return M.stay(rule, *Pt, c[0], c[1], c[2], steps) if c is not None else M.mandel(rule, *Pt, steps)


def sheet(tiles, path, title, cols):
    """tiles: list of (caption, rgb array)."""
    pad = 10; w = max(t[1].shape[1] for t in tiles); h = max(t[1].shape[0] for t in tiles); rows = (len(tiles) + cols - 1) // cols
    im = Image.new('RGB', (pad + cols * (w + pad), 50 + rows * (h + 30)), (12, 14, 20)); d = ImageDraw.Draw(im)
    d.text((pad, 10), title, fill=(240, 240, 245), font=M.font(20))
    for i, (cap, pic) in enumerate(tiles):
        x = pad + (i % cols) * (w + pad); y = 50 + (i // cols) * (h + 30)
        d.text((x, y), cap, fill=(160, 170, 185), font=M.font(13)); im.paste(Image.fromarray(pic), (x, y + 20))
    im.save(path); print('wrote', path)


def fan():
    r = R.get('c_page'); c = np.array(M.RABBIT); ch = c / np.linalg.norm(c); cp = np.array([-ch[1], ch[0], 0.0]); ez = np.array([0.0, 0.0, 1.0])
    tiles = []; steps = 80
    for tau in (0, 30, 50, 60, 75, 90):
        t = np.radians(tau); m = np.cos(t) * cp + np.sin(t) * ez
        # in the plane: right = the plane's real axis (x pressed into it), up = square to it
        a = np.array([1.0, 0, 0]); a = (a @ ch) * ch + (a @ m) * m; a /= np.linalg.norm(a); b = np.cross(np.cross(ch, m), a); b /= np.linalg.norm(b)
        if b @ ch < 0:
            b = -b
        n = cut_plane(r, (0, 0, 0), a, b, 1.7, 340, 300, steps, M.RABBIT)
        g = complex(c @ a, c @ b)
        tiles.append(('through the line of c, turned %d: gamma = %.3f %+.3fi' % (tau, g.real, g.imag), M.shade(n, steps)))
    for d0 in (0.0, 0.35):
        n = cut_plane(r, tuple(d0 * ch), cp, ez, 1.7, 340, 300, steps, M.RABBIT)
        tiles.append(('ACROSS the line of c, %.2f along it (up: z)' % d0, M.shade(n, steps)))
    sheet(tiles, os.path.join(HERE, 'fan-rabbit.png'), 'c_page, the rabbit: every plane through the line of c holds a flat Julia set of its own (80 steps)', 4)


def tears():
    out = []; rng = np.random.default_rng(4); n = 20000
    def F(name, x, y, z, c):
        r = R.get(name); st = r.init(x.size); X, Y, Z, _ = r.step(x, y, z, st, 0, np.full(x.size, c[0]), np.full(x.size, c[1]), np.full(x.size, c[2])); return np.stack([X, Y, Z])
    # 1. plane square to the x-axis: partner c = (0, 1, 0); points just left and right of the plane x = 0
    y, z = rng.uniform(-1, 1, n), rng.uniform(-1, 1, n); e = np.full(n, 1e-7)
    for nm in ('c_page', 'c_lathe'):
        d = np.linalg.norm(F(nm, e, y, z, (0, 1, 0)) - F(nm, -e, y, z, (0, 1, 0)), axis=0) / (y * y + z * z)
        out.append('1. %-8s c = i (c square to the x-axis): jump of the square across the plane x = 0, as a share of |v|^2: median %.3f, largest %.3f (2 = thrown to the opposite point)' % (nm, np.median(d), d.max()))
    # 2. point parallel to its partner: a small circle round the line of c (rabbit)
    c = np.array(M.RABBIT); ch = c / np.linalg.norm(c); m1 = np.array([-ch[1], ch[0], 0.0]); m2 = np.array([0, 0, 1.0])
    for eps in (1e-3, 1e-6):
        phi = np.linspace(0, 2 * np.pi, 721); t = 0.6
        v = t * ch[:, None] + eps * (np.cos(phi) * m1[:, None] + np.sin(phi) * m2[:, None])
        S = F('c_page', v[0], v[1], v[2], M.RABBIT); d = np.linalg.norm(S[:, :, None] - S[:, None, :], axis=0).max() / (t * t)
        out.append('2. c_page   rabbit: on a circle of radius %.0e round the line of c (at 0.6 along it) the squares differ by up to %.3f of |v|^2: a whirl; it does not shrink with the circle' % (eps, d))
    # 3. the first plane "nearest the flat page": a small circle round the z-axis
    for eps in (1e-3, 1e-6):
        phi = np.linspace(0, 2 * np.pi, 721); zz = 0.6
        S = F('prev_page', eps * np.cos(phi), eps * np.sin(phi), np.full(phi.size, zz), (-1, 0, 0)); d = np.linalg.norm(S[:, :, None] - S[:, None, :], axis=0).max() / (zz * zz)
        out.append('3. prev_page first step: on a circle of radius %.0e round the z-axis (at height 0.6) the squares differ by up to %.3f of |v|^2: a whirl on the z-axis' % (eps, d))
        S = F('prev_lathe', np.full(phi.size, zz), eps * np.cos(phi), eps * np.sin(phi), (-1, 0, 0)); d = np.linalg.norm(S[:, :, None] - S[:, None, :], axis=0).max() / (zz * zz)
        out.append('3. prev_lathe first step: on a circle of radius %.0e round the x-axis (at 0.6 along it) the squares differ by up to %.1e of |v|^2: no jump' % (eps, d))
    # 4. moving part of the way: the made plane square to the carried plane (lam = 0.5). c = -1, carried plane = flat page; points just either side of the x-z plane
    x, z = rng.uniform(-1, 1, n), rng.uniform(0.2, 1, n)
    for nm in ('c_lag50', 'c_lag25', 'c_lag10'):
        d = np.linalg.norm(F(nm, x, e, z, (-1, 0, 0)) - F(nm, x, -e, z, (-1, 0, 0)), axis=0) / (x * x + z * z)
        out.append('4. %-8s c = -1: jump of the square across the x-z plane (where the made plane stands square to the carried one), share of |v|^2: median %.3f, largest %.3f' % (nm, np.median(d), d.max()))
    for s in out:
        print(s)
    with open(os.path.join(HERE, 'tears.txt'), 'w', encoding='utf-8') as fh:
        fh.write('\n'.join(out) + '\n')


def cuts(names):
    for nm in names:
        r = R.get(nm) if nm not in ('along', 'oneplane', 'lathe') else M.bench(nm); tiles = []; t0 = time.time()
        for sn, c in (('basilica', (-1.0, 0.0, 0.0)), ('rabbit', M.RABBIT)):
            for ang in (0.0, 11.25, 22.5, 33.75, 90.0):
                tiles.append(('%s: cut along the sheet turned %g' % (sn, ang), M.shade(M.cut_axis(r, ang, 300, 220, 80, c=c), 80)))
            x0 = -1.0 if sn == 'basilica' else -0.12
            tiles.append(('%s: cut across the x-axis at x = %g' % (sn, x0), M.shade(M.cut_across(r, x0, 220, 80, c=c, L=1.1), 80)))
            for cam in ((0.45, 0.5, 1.0), (0.2, 1.0, 0.25), (1.0, 0.25, 0.3)):
                dep, px = M.solid(r, c, 300, 220, 170, 60, cam=cam); tiles.append(('%s: solid, 60 steps, eye at %s' % (sn, cam), M.shade_solid(dep, px)))
        sheet(tiles, os.path.join(HERE, 'cuts-%s.png' % nm), '%s: %s' % (r.name, r.label), 6)
        print(nm, '%.0f s' % (time.time() - t0)); sys.stdout.flush()


def sweep():
    """The Mandelbrot solid of c_page (the same as the flat set swept along the level lines of one angle), against the lathe."""
    tiles = []
    for r in (R.get('c_page'), M.bench('lathe')):
        for x0 in (-1.0, -0.12):
            tiles.append(('%s: cut across the x-axis at x = %g' % (r.name, x0), M.shade(M.cut_across(r, x0, 260, 60), 60)))
        for ang in (67.5, 85.0):
            tiles.append(('%s: cut along the sheet turned %g' % (r.name, ang), M.shade(M.cut_axis(r, ang, 300, 260, 60), 60)))
        for cam in ((0.45, 0.5, 1.0), (0.2, 1.0, 0.25), (-0.6, 0.3, 1.0)):
            dep, px = M.solid(r, None, 300, 260, 200, 30, cam=cam); tiles.append(('%s: solid, 30 steps, eye at %s' % (r.name, cam), M.shade_solid(dep, px)))
    sheet(tiles, os.path.join(HERE, 'sweep-c_page.png'), 'Mandelbrot solid of c_page (first plane: nearest the flat page) against the lathe (first plane: own sheet)', 7)


if __name__ == '__main__':
    what = sys.argv[1]
    if what == 'sweep':
        sweep()
    elif what == 'fan':
        fan()
    elif what == 'tears':
        tears()
    else:
        cuts(sys.argv[2:])

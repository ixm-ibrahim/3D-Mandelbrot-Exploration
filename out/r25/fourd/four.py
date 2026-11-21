"""Round 25, section fourd: do it in 4D, come down to 3D otherwise than by a flat cut.

Three families, all drawn point by point (one orbit, or a few flat orbits, per block):

A. SPINOR rule (new 4D rule, not the plain quaternion one).
   A point of space v is the shadow of a quaternion q:  v = q i q*  (the Hopf map; |v| = |q|^2).
   Square the quaternion (turns compose properly there), add c in SPACE, and carry the quaternion along
   by the one transport that adds no twist (the horizontal lift of the straight move from w to w + c):
        q  ->  sqrt(1 + c w^-1) q^2 ,   w = q^2 i (q^2)*      (c, w taken as pure quaternions)
   On the flat plane with the flat quaternion (q = a + d k) this is sqrt(s^4 + c): the flat rule, exactly.
   Every 3D point has a whole circle of quaternions above it (q e^{i theta}); ways down:
     'min'   the quaternion of the least turn from the x-axis        (3-plane 1, j, k)
     'twi'   the quaternion in the 3-plane 1, i, k (twist = the point's angle round the x-axis)
     'any'   a 3D point is in if SOME quaternion above it stays;  'all'  if EVERY one stays.

B. PRODUCT of two flat pictures (the bicomplex rule is this: u1 = m + d, u2 = m - d each follow the flat rule).
   Ways down from the pair (u1, u2) to a 3D point (m, t), m = the middle of the pair, t = half its length:
     'pany'  some pair with that middle and that half length has both ends inside        (shadow)
     'pall'  every such pair has (= the whole circle round m of radius t is inside)       (core)
     'perp'  the one pair that lies square to the line from the centre to m
             = both ends at the same distance from the centre = the cut of the product by the cone
             over the Clifford torus |u1| = |u2|.  In ball coordinates (r, longitude L, latitude D):
             the 3D point is in  iff  r e^{i(L+D)} and r e^{i(L-D)} are both in the flat picture.

C. Checks of the 'only natural 4D squares' claim (Hurwitz): a twisted quaternion square in 4D gives the plain one.

    python out/r25/fourd/four.py algebra | flat | cuts | sheet <tag> <cam> | ...
"""
import os, sys, time
import numpy as np
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, 'out', 'r21', 'lib'))
import mem as M

TINY = 1e-300
SETS = [('c = -1', (-1.0, 0.0, 0.0)), ('rabbit', M.RABBIT), ('c = -0.75', (-0.75, 0.0, 0.0)), ('Siegel disc', M.SIEGEL)]
CAMS = {'a': (0.45, 0.5, 1.0), 'top': (0.2, 1.0, 0.35)}


# ------------------------------------------------------------------ quaternions as 4 arrays (1, i, j, k)
def qmul(p, q):
    a1, b1, c1, d1 = p; a2, b2, c2, d2 = q
    return (a1 * a2 - b1 * b2 - c1 * c2 - d1 * d2, a1 * b2 + b1 * a2 + c1 * d2 - d1 * c2,
            a1 * c2 - b1 * d2 + c1 * a2 + d1 * b2, a1 * d2 + b1 * c2 - c1 * b2 + d1 * a2)


def qsq(q):
    a, b, c, d = q
    return a * a - b * b - c * c - d * d, 2 * a * b, 2 * a * c, 2 * a * d


def hopf(q):
    """The shadow q i q*: space is x i + y j + z k, the flat plane is (i, j), upright is k."""
    a, b, c, d = q
    return a * a + b * b - c * c - d * d, 2 * (b * c + a * d), 2 * (b * d - a * c)


def lift_min(x, y, z):
    """The quaternion of the least turn that carries the x-axis to the point (|q|^2 = |v|)."""
    r = np.sqrt(x * x + y * y + z * z); s = r + x; ok = s > 1e-14 * np.maximum(r, TINY)
    n = np.sqrt(np.where(ok, 2 * s, 1.0))
    return (np.where(ok, s / n, 0.0), np.zeros_like(r), np.where(ok, -z / n, 0.0), np.where(ok, y / n, np.sqrt(r)))


def phase(q, th):
    """q e^{i theta}: the same shadow, the frame twisted by 2 theta about the point."""
    return qmul(q, (np.cos(th), np.sin(th), 0.0 * np.asarray(th), 0.0 * np.asarray(th)))


def lift_plane(x, y, z, alpha):
    """The quaternion above the point that lies in the 3-plane (1, k, cos(alpha) j + sin(alpha) i).
    alpha = 0: lift_min. alpha = 90 degrees: the 3-plane (1, i, k)."""
    q = lift_min(x, y, z); a0, _, c0, d0 = q
    th = np.arctan2(c0 * np.sin(alpha), a0 * np.cos(alpha) - d0 * np.sin(alpha))
    return phase(q, th)


def transport(p, cx, cy, cz):
    """Move the shadow of p by c along the straight line, with no twist: p -> sqrt(1 + c w^-1) p."""
    wx, wy, wz = hopf(p)
    n2 = p[0] * p[0] + p[1] * p[1] + p[2] * p[2] + p[3] * p[3]; ok = n2 > 1e-280; n = np.sqrt(np.where(ok, n2, 1.0))   # |p|, and |w| = |p|^2
    ph = tuple(np.where(ok, t / n, e) for t, e in zip(p, (1.0, 0.0, 0.0, 0.0)))        # the unit quaternion (kept exact when the orbit falls into 0)
    hx, hy, hz = hopf(ph)                                                               # the unit direction of w
    s0 = np.where(ok, n2, 0.0) + cx * hx + cy * hy + cz * hz                            # (w + c) w^-1 times |w|: scalar part
    ux, uy, uz = -(cy * hz - cz * hy), -(cz * hx - cx * hz), -(cx * hy - cy * hx)       #                          vector part
    m = np.sqrt(s0 * s0 + ux * ux + uy * uy + uz * uz)                                  # = |w + c|
    sm = np.sqrt(m); bad = (m + s0) <= 1e-13 * m          # the straight move runs through the origin: every twist is as good as any other
    den = np.sqrt(np.where(bad, 1.0, 2 * m * (m + s0)))
    # where it is bad, take the half turn about an axis square to the direction (k, or j when the direction is k)
    ax, ay, az = hy, -hx, 0.0 * hx; an = np.sqrt(ax * ax + ay * ay); flat_dir = an > 1e-9; an = np.where(flat_dir, an, 1.0)
    ax, ay, az = np.where(flat_dir, ax / an, 0.0), np.where(flat_dir, ay / an, 1.0), az
    z0 = np.where(bad, 0.0, sm * (m + s0) / den)
    return qmul((z0, np.where(bad, sm * ax, sm * ux / den), np.where(bad, sm * ay, sm * uy / den), np.where(bad, sm * az, sm * uz / den)), ph), (wx, wy, wz)


def spinor(kind='min', th=0.0, alpha=np.pi / 2):
    """The spinor rule as a rule of the library. The orbit carries the quaternion; the first step makes it."""
    def step(x, y, z, st, k, cx, cy, cz):
        if k == 0:
            q = lift_min(x, y, z) if kind in ('min', 'phase') else lift_plane(x, y, z, alpha)
            if kind == 'phase':
                q = phase(q, th)
        else:
            q = st
        p, w = transport(qsq(q), cx, cy, cz)
        return w[0], w[1], w[2], p
    label = {'min': 'spinor rule, each point starts with the least-turn quaternion', 'twi': 'spinor rule, each point starts in the 3-plane (1, i, k)',
             'phase': 'spinor rule, start twisted by %.0f degrees' % np.degrees(2 * th)}[kind]
    return M.Rule('spinor-' + kind, label, step, init=lambda n: (np.zeros(n), np.zeros(n), np.zeros(n), np.zeros(n)))


def tilt(t):
    """The known 'twisted quaternion square' (round 12): the only length-squaring quadratic 3D maps that are exact on the flat plane."""
    co, si = np.cos(t), np.sin(t); c2, s2 = np.cos(2 * t), np.sin(2 * t)
    return M.fixed(lambda x, y, z: (x * x - y * y - z * z * c2, 2 * x * y + z * z * s2, 2 * z * (x * co - y * si)), 'tilt%.0f' % np.degrees(t), 'quaternion square, twisted by %.0f degrees' % np.degrees(t))


# ------------------------------------------------------------------ what counts as inside (predicates on 3D arrays)
def pred_rule(rule, c, steps):
    return lambda x, y, z: M.stay(rule, x, y, z, c[0], c[1], c[2], steps) >= steps


def pred_lifts(c, steps, n=8, mode='any'):
    rules = [spinor('phase', th=np.pi * j / n) for j in range(n)]

    def f(x, y, z):
        x, y, z = np.broadcast_arrays(x, y, z); acc = np.zeros(x.shape, bool) if mode == 'any' else np.ones(x.shape, bool)
        far = (x * x + y * y + z * z) > 9.0                                   # nothing that far out stays (|v|^2 - |c| grows)
        for r in rules:
            todo = (~acc if mode == 'any' else acc.copy()) & ~far             # decided points need no more quaternions
            if not todo.any():
                break
            acc[todo] = M.stay(r, x[todo], y[todo], z[todo], c[0], c[1], c[2], steps) >= steps
        if mode == 'all':
            acc &= ~far
        return acc
    return f


FLAT = M.fixed(lambda x, y, z: (x * x - y * y, 2 * x * y, 0.0 * x), 'flat', 'the flat rule')


def in_flat(zr, zi, c, steps):
    """Is the flat point in the flat picture of c? (the true complex orbit; orbits that left are dropped, so it is quick)"""
    return M.stay(FLAT, zr, zi, 0.0 * np.asarray(zr), c[0], c[1], 0.0, steps) >= steps


def in_flat2(ar, ai, br, bi, c, steps):
    """Are BOTH flat points in? The second is only followed where the first stayed."""
    a = in_flat(ar, ai, c, steps); out = np.zeros(a.shape, bool)
    if a.any():
        out[a] = in_flat(np.broadcast_to(br, a.shape)[a], np.broadcast_to(bi, a.shape)[a], c, steps)
    return out


def pred_perp(c, steps):
    def f(x, y, z):
        rho = np.hypot(x, y); ok = rho > 0; rr = np.where(ok, rho, 1.0); mx, my = np.where(ok, x / rr, 1.0), np.where(ok, y / rr, 0.0)
        return in_flat2(x - z * my, y + z * mx, x + z * my, y - z * mx, c, steps)
    return f


def pred_pany(c, steps, n=16):
    def f(x, y, z):
        x, y, z = np.broadcast_arrays(x, y, z); acc = np.zeros(x.shape, bool)
        for j in range(n):
            th = np.pi * j / n; co, si = np.cos(th), np.sin(th); todo = ~acc      # a point that is already in needs no more pairs
            if not todo.any():
                break
            xx, yy, zz = x[todo], y[todo], z[todo]
            acc[todo] = in_flat2(xx + zz * co, yy + zz * si, xx - zz * co, yy - zz * si, c, steps)
        return acc
    return f


def pred_pall(c, steps, n=16):
    def f(x, y, z):
        x, y, z = np.broadcast_arrays(x, y, z); acc = np.ones(x.shape, bool)
        for j in range(2 * n):
            th = np.pi * j / n; todo = acc.copy()                                  # a point that is already out needs no more
            if not todo.any():
                break
            xx, yy, zz = x[todo], y[todo], z[todo]
            acc[todo] = in_flat(xx + zz * np.cos(th), yy + zz * np.sin(th), c, steps)
        return acc
    return f


def pred_hyper(c, steps, th=np.pi / 2):
    """The known flat cut of the product (the 'hypercomplex' rule): the pair slid apart along one fixed direction."""
    co, si = np.cos(th), np.sin(th)
    return lambda x, y, z: in_flat2(x + z * co, y + z * si, x - z * co, y - z * si, c, steps)


# ------------------------------------------------------------------ pictures
def solid_pred(pred, w, h, nd, centre=(0.0, 0.0, 0.0), half_w=1.75, cam=(0.45, 0.5, 1.0)):
    e1, e2, e3 = M.frame(cam)
    us = np.linspace(-half_w, half_w, w); vs = np.linspace(half_w * h / w, -half_w * h / w, h); ds = np.linspace(-half_w, half_w, nd)
    U, V = np.meshgrid(us, vs); depth = np.full((h, w), np.inf)
    for k0 in range(0, nd, 8):
        dk = ds[k0:k0 + 8]
        P = [centre[i] + U[None] * e1[i] + V[None] * e2[i] + dk[:, None, None] * e3[i] for i in range(3)]
        ins = pred(P[0], P[1], P[2])
        depth = np.minimum(depth, np.where(ins.any(0), dk[np.argmax(ins, 0)], np.inf))
    return depth, us[1] - us[0]


def sheet(rows, path, sets, cam, w=380, h=285, nd=200, title=None, half_w=1.75):
    """rows: (name, label, make) with make(c) -> predicate."""
    pad = 10; t0 = time.time(); W = pad + len(sets) * (w + pad); H = 56 + len(rows) * (h + 36)
    im = Image.new('RGB', (W, H), (12, 14, 20)); d = ImageDraw.Draw(im)
    d.text((pad, 10), title or 'Rough solids, eye at %s' % (cam,), fill=(240, 240, 245), font=M.font(22))
    for i, (name, label, make) in enumerate(rows):
        y = 56 + i * (h + 36); d.text((pad, y), '%s: %s' % (name, label), fill=(235, 220, 170), font=M.font(17))
        for j, (sn, c) in enumerate(sets):
            dep, px = solid_pred(make(c), w, h, nd, cam=cam, half_w=half_w); x = pad + j * (w + pad)
            im.paste(Image.fromarray(M.shade_solid(dep, px)), (x, y + 26)); d.text((x + 6, y + 30), sn, fill=(150, 160, 175), font=M.font(13))
            print('solid', name, sn, '%.0f s' % (time.time() - t0)); sys.stdout.flush()
        im.save(path)
    im.save(path); return path


def cut_pred(pred, plane, w, h, box=(-1.8, 1.8, -1.3, 1.3)):
    """plane: 'flat' (x, y), 'upx' (x, z at y = 0), 'upy' (y, z at x = 0), 'diag' (x, s) with y = z = s / sqrt 2."""
    u, s = np.meshgrid(np.linspace(box[0], box[1], w), np.linspace(box[3], box[2], h)); o = np.zeros_like(u)
    P = {'flat': (u, s, o), 'upx': (u, o, s), 'upy': (o, u, s), 'diag': (u, s * np.sqrt(0.5), s * np.sqrt(0.5))}[plane]
    return pred(*P)


def shade_bool(b):
    img = np.zeros(b.shape + (3,), np.uint8); img[...] = (24, 34, 70); img[b] = (238, 228, 200); return img


def cuts(rows, path, sets, planes=('flat', 'upx', 'upy', 'diag'), w=260, h=188, title=None):
    names = {'flat': 'flat cut', 'upx': 'upright cut through the x-axis', 'upy': 'upright cut through the y-axis', 'diag': 'cut through the x-axis, tilted 45'}
    pad = 8; W = pad + len(sets) * len(planes) * (w + pad); H = 40 + len(rows) * (h + 26)
    im = Image.new('RGB', (W, H), (12, 14, 20)); d = ImageDraw.Draw(im); t0 = time.time()
    d.text((pad, 6), title or 'Cuts', fill=(240, 240, 245), font=M.font(18))
    for i, (name, label, make) in enumerate(rows):
        y = 60 + i * (h + 26); d.text((pad, y - 20), name + ': ' + label, fill=(235, 220, 170), font=M.font(15))
        for j, (sn, c) in enumerate(sets):
            pr = make(c)
            for k, pl in enumerate(planes):
                x = pad + (j * len(planes) + k) * (w + pad)
                im.paste(Image.fromarray(shade_bool(cut_pred(pr, pl, w, h))), (x, y)); d.text((x + 4, y + 2), sn + ', ' + names[pl], fill=(150, 160, 175), font=M.font(12))
        print('cuts', name, '%.0f s' % (time.time() - t0)); sys.stdout.flush()
    im.save(path); print('wrote', path, im.size)


# ------------------------------------------------------------------ rows
def ROWS(steps=30, nl=8, npair=16):
    return {
        'one':   ('one plane', 'the baseline for "blown up"', lambda c: pred_rule(M.bench('oneplane'), c, steps)),
        'min':   ('spinor, least turn', 'square the quaternion above the point, add c in space; start with the least-turn quaternion', lambda c: pred_rule(spinor('min'), c, steps)),
        'twi':   ('spinor, 3-plane (1, i, k)', 'the same rule; start with the quaternion twisted by the angle round the x-axis', lambda c: pred_rule(spinor('twi'), c, steps)),
        'any':   ('spinor, any lift', 'in if SOME quaternion above the point stays (%d tried)' % nl, lambda c: pred_lifts(c, steps, nl, 'any')),
        'all':   ('spinor, all lifts', 'in if EVERY quaternion above the point stays (%d tried)' % nl, lambda c: pred_lifts(c, steps, nl, 'all')),
        'hyper': ('product, flat cut', 'two flat pictures slid apart along y (the known hypercomplex cut)', lambda c: pred_hyper(c, steps)),
        'perp':  ('product, cone cut', 'both r e^{i(L+D)} and r e^{i(L-D)} in the flat picture', lambda c: pred_perp(c, steps)),
        'pany':  ('product, any pair', 'some pair of flat points with this middle and half length (%d directions)' % npair, lambda c: pred_pany(c, steps, npair)),
        'pall':  ('product, all pairs', 'the whole circle round the middle is inside (%d directions)' % (2 * npair), lambda c: pred_pall(c, steps, npair)),
        'tilt90': ('twisted quaternion, 90', 'known (round 12): the Hopf map on the 3-plane (1, i, k)', lambda c: pred_rule(tilt(np.pi / 2), c, steps)),
    }


# ------------------------------------------------------------------ commands
def algebra():
    rng = np.random.default_rng(1); n = 200000
    v = rng.normal(size=(3, n)); c = rng.normal(size=(3, n)) * 0.7
    for nm, q in (('least turn', lift_min(*v)), ('3-plane (1,i,k)', lift_plane(*v, np.pi / 2)), ('3-plane 30 deg', lift_plane(*v, np.pi / 6))):
        h = hopf(q); print('%-16s shadow of the lift minus the point: %.1e' % (nm, max(np.abs(h[i] - v[i]).max() for i in range(3))))
    q = lift_plane(*v, np.pi / 2); print('3-plane (1,i,k): j-part of the lift %.1e' % np.abs(q[2]).max())
    q = phase(lift_min(*v), rng.uniform(0, np.pi, n)); p, w = transport(q, *c); h = hopf(p)
    print('transport: shadow of the new quaternion minus (w + c): %.1e' % max(np.abs(h[i] - w[i] - c[i]).max() for i in range(3)))
    # no twist: the move of the quaternion is square to its fibre (compare a small step)
    e = 1e-6; p2, _ = transport(q, *(e * c)); dq = [(p2[i] - q[i]) / e for i in range(4)]; fib = qmul(q, (0.0, 1.0, 0.0, 0.0))
    dot = sum(dq[i] * fib[i] for i in range(4)); print('transport: part of a small move along the fibre: %.1e (move size %.2f)' % (np.abs(dot).max(), np.sqrt(sum(t * t for t in dq)).mean()))
    # flat: quaternion a + d k, c in the flat plane -> stays a + d k and is sqrt(s^4 + c)
    a, d = rng.normal(size=(2, n)); cf = rng.normal(size=(2, n)); z0 = np.zeros(n)
    p, w = transport(qsq((a, z0, z0, d)), cf[0], cf[1], z0); s = (a + 1j * d); tgt = s ** 4 + cf[0] + 1j * cf[1]; got = (p[0] + 1j * p[3]) ** 2
    print('flat: i, j parts of the new quaternion %.1e, %.1e; its square minus (s^4 + c): %.1e' % (np.abs(p[1]).max(), np.abs(p[2]).max(), np.abs(got - tgt).max()))
    # real c: the least-turn start is the Lathe
    L = M.bench('lathe'); S = spinor('min'); x = rng.uniform(-1.6, 1.6, size=(3, n))
    for cc in ((-1.0, 0.0, 0.0), (-0.75, 0.0, 0.0), M.RABBIT):
        a1 = M.stay(L, x[0], x[1], x[2], *cc, 40) >= 40; a2 = M.stay(S, x[0], x[1], x[2], *cc, 40) >= 40
        print('c = %s: least-turn spinor rule against the Lathe: %d of %d verdicts differ (inside %d / %d)' % (cc, int((a1 != a2).sum()), n, int(a1.sum()), int(a2.sum())))
    # Hurwitz check: 4D quaternion square followed by a turn of the hidden plane (j, k) by omega: same 3D cut as the plain one
    for om in (0.7, 2.0):
        zr, zi, t = rng.uniform(-1.6, 1.6, size=(3, n)); res = []
        for o in (0.0, om):
            A = zr + 1j * zi; B = t.astype(complex); alive = np.ones(n, bool)
            for _ in range(40):
                A, B = np.where(alive, A * A - np.abs(B) ** 2 - 1.0, A), np.where(alive, 2 * A.real * B * np.exp(1j * o), B)
                alive &= (np.abs(A) ** 2 + np.abs(B) ** 2) < 36
            res.append(alive)
        print('4D quaternion square with the hidden plane turned by %.1f each step: %d of %d verdicts differ from the plain one' % (om, int((res[0] != res[1]).sum()), n))


def flat():
    R = ROWS(60)
    for key in ('min', 'twi'):
        r = spinor(key); print('==', r.name); print('   flat check', M.flat_check(r, n=20000, steps=60)); sys.stdout.flush()
    rng = np.random.default_rng(3); n = 20000; zr, zi = rng.uniform(-1.8, 1.8, n), rng.uniform(-1.3, 1.3, n); z0 = np.zeros(n)
    for key in ('any', 'all', 'perp', 'pany', 'pall', 'hyper'):
        out = {}
        for nm, c in SETS:
            a = R[key][2](c)(zr, zi, z0); b = in_flat(zr, zi, c, 60); out[nm] = (int((a & ~b).sum()), int((b & ~a).sum()))
        print('== %-22s flat points: (extra, missing) of %d: %s' % (R[key][0], n, out)); sys.stdout.flush()


if __name__ == '__main__':
    a = sys.argv[1] if len(sys.argv) > 1 else 'algebra'
    if a == 'algebra':
        algebra()
    elif a == 'flat':
        flat()
    elif a == 'cuts':
        keys = sys.argv[2].split(','); tag = sys.argv[3] if len(sys.argv) > 3 else 'x'
        R = ROWS(40, nl=8, npair=12)
        cuts([R[k] for k in keys], os.path.join(HERE, 'cuts-%s.png' % tag), SETS[:2] if len(sys.argv) < 5 else SETS)
    elif a == 'sheet':
        keys = sys.argv[2].split(','); tag = sys.argv[3]; cam = sys.argv[4] if len(sys.argv) > 4 else 'a'
        nd = int(sys.argv[5]) if len(sys.argv) > 5 else 180; steps = int(sys.argv[6]) if len(sys.argv) > 6 else 28
        R = ROWS(steps, nl=6, npair=12)
        sheet([R[k] for k in keys], os.path.join(HERE, 'solids-%s-%s.png' % (tag, cam)), SETS[:2], CAMS[cam], nd=nd,
              title='Rough solids (%d blocks deep, %d steps), eye at %s' % (nd, steps, CAMS[cam]))
        print('sheet done')

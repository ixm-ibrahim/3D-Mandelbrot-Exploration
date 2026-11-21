"""Round 22, section 'lump': where do bounded orbits end up?  Shared tools.

    import sys; sys.path.insert(0, 'out/r22/lump'); import lumplib as L

The rules are the library's (out/r21/lib/mem.py) and the judge's loader (out/r21/judge/myrules.py); nothing is
re-coded. M.stay only counts steps, so `follow` below is M.stay's own loop (same step call, same c added, same
ball |v| < 6) that also hands back the points. `check_follow` proves the two agree.

Fates (codes used in every picture and table of this folder):
    0 OUT      the orbit leaves
    1 FLATCYC  it ends on the cycle of the flat picture (for the Siegel disc: on a closed curve IN the flat page)
    2 PAGE     it ends in the flat page, but not on the flat cycle
    3 OFFCYC   it ends on a cycle that is not in the flat page
    4 CURVE    it never settles on a cycle: it runs round a closed curve off the page (neighbours stay beside it)
    5 CLOUD    it never settles: a cloud (neighbours drift apart; chaotic)
    6 SLOW     still creeping after all the steps (could not be told)
"""
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, 'out', 'r21', 'lib')); sys.path.insert(0, os.path.join(ROOT, 'out', 'r21', 'judge'))
import mem as M
import myrules as J

OUT, FLATCYC, PAGE, OFFCYC, CURVE, CLOUD, SLOW = range(7)
FATE_NAMES = ['leaves', 'flat cycle', 'in the page, not the cycle', 'cycle off the page', 'closed curve off the page', 'cloud', 'still creeping']
RABBIT, SIEGEL = M.RABBIT, M.SIEGEL
CSETS = {'rabbit': RABBIT, 'siegel': SIEGEL, 't003': (-1.0, 0.03, 0.0), 't010': (-1.0, 0.1, 0.0), 't020': (-1.0, 0.2, 0.0), 'basilica': (-1.0, 0.0, 0.0)}


def rule(name):
    if name in ('along', 'oneplane', 'lathe', 'away'):
        return M.bench(name)
    return J.get(name)


def follow(r, x, y, z, c, steps, trail=0, k0=0, r2=36.0):
    """M.stay's loop, handing back the points. Returns (n, idx, (x, y, z), tr):
    n     steps each orbit stayed (as M.stay)
    idx   flat indices of the orbits that never left
    x,y,z their last points
    tr    array (trail, 3, len(idx)): their last `trail` points (oldest first), or None"""
    sh = np.shape(x)
    cx, cy, cz = (np.broadcast_to(np.asarray(t, float), sh).ravel().copy() for t in c)
    x, y, z = (np.array(np.broadcast_to(np.asarray(t, float), sh)).ravel() for t in (x, y, z))
    st = tuple(r.init(x.size)); n = np.zeros(x.size, np.int32); idx = np.arange(x.size); buf = []
    for k in range(steps):
        out = r.step(x, y, z, st, k + k0, cx, cy, cz); X, Y, Z, st = out[0], out[1], out[2], tuple(out[3])
        x, y, z = X + cx, Y + cy, Z + cz
        keep = (x * x + y * y + z * z) < r2
        if not keep.all():
            idx = idx[keep]; x, y, z, cx, cy, cz = (t[keep] for t in (x, y, z, cx, cy, cz)); st = tuple(t[keep] for t in st)
            buf = [b[:, keep] for b in buf]
        n[idx] += 1
        if trail and k >= steps - trail:
            buf.append(np.stack([x, y, z]))
        if idx.size == 0:
            break
    tr = np.stack(buf) if (trail and buf and idx.size) else None
    return n.reshape(sh), idx, (x, y, z), tr


def check_follow(r, c, n=20000, steps=60, seed=1):
    rng = np.random.default_rng(seed); p = rng.uniform(-1.5, 1.5, (3, n))
    a = M.stay(r, p[0], p[1], p[2], c[0], c[1], c[2], steps); b = follow(r, p[0], p[1], p[2], c, steps)[0]
    return int((a != b).sum())


def flat_cycle(c, burn=4000, maxp=64, tol=1e-9):
    """The attracting cycle of the flat picture z -> z^2 + c from the orbit of 0, as a list of complex points
    (None if the orbit of 0 does not settle on a cycle, as for the Siegel disc)."""
    z = 0j; cc = complex(c[0], c[1])
    for _ in range(burn):
        z = z * z + cc
        if abs(z) > 6:
            return None
    pts = [z]
    for _ in range(maxp):
        z = z * z + cc
        if abs(z - pts[0]) < tol:
            return pts
        pts.append(z)
    return None


def lyap(r, x, y, z, c, steps, k0, eps=1e-7, seed=7):
    """Mean log stretch per step of a neighbour 1e-7 away (rescaled every step): > 0 neighbours drift apart."""
    n = x.size; rng = np.random.default_rng(seed); d = rng.normal(size=(3, n)); d /= np.linalg.norm(d, axis=0)
    cx, cy, cz = (np.full(n, t) for t in c)
    a = [x.copy(), y.copy(), z.copy()]; b = [a[i] + eps * d[i] for i in range(3)]
    sa = tuple(r.init(n)); sb = tuple(r.init(n)); s = np.zeros(n)
    for k in range(steps):
        oa = r.step(a[0], a[1], a[2], sa, k + k0, cx, cy, cz); ob = r.step(b[0], b[1], b[2], sb, k + k0, cx, cy, cz)
        sa, sb = tuple(oa[3]), tuple(ob[3])
        a = [oa[0] + cx, oa[1] + cy, oa[2] + cz]; b = [ob[0] + cx, ob[1] + cy, ob[2] + cz]
        dd = [b[i] - a[i] for i in range(3)]; nd = np.sqrt(dd[0] ** 2 + dd[1] ** 2 + dd[2] ** 2); nd = np.maximum(nd, 1e-300)
        s += np.log(nd / eps); b = [a[i] + dd[i] * (eps / nd) for i in range(3)]
    return s / steps


def fates(r, x, y, z, c, inside_steps=80, burn=600, trail=128, maxp=48, ptol=1e-7, ztol=1e-7, lyap_steps=300):
    """The fate code of every start point (shape of x). Also returns a dict of extras for the bounded ones:
    idx, end (3, m) last point, period (0 = none), zmax (largest |z| over the trail), dcyc (distance of the trail to
    the flat cycle), lam (neighbour drift, only where no cycle was found, else nan)."""
    sh = np.shape(x)
    n, idx, _, _ = follow(r, x, y, z, c, inside_steps)
    code = np.zeros(n.size, np.int8)
    xs, ys, zs = (np.array(np.broadcast_to(np.asarray(t, float), sh)).ravel()[idx] for t in (x, y, z))
    n2, idx2, end, tr = follow(r, xs, ys, zs, c, burn + trail, trail=trail)
    gid = idx[idx2]                                           # orbits that also survive the long run
    m = gid.size
    ex = dict(idx=gid, end=np.stack(end) if m else np.zeros((3, 0)), period=np.zeros(m, np.int32), zmax=np.zeros(m), dcyc=np.full(m, np.inf), lam=np.full(m, np.nan), leaked=int(idx.size - m))
    if m == 0:
        return code.reshape(sh), ex
    zmax = np.abs(tr[:, 2, :]).max(0); ex['zmax'] = zmax
    per = np.zeros(m, np.int32)
    for p in range(1, maxp + 1):
        d = np.sqrt(((tr[p:] - tr[:-p]) ** 2).sum(1)).max(0)
        new = (per == 0) & (d < ptol); per[new] = p
    ex['period'] = per
    fc = flat_cycle(c)
    if fc is not None:
        pts = np.array([[w.real, w.imag, 0.0] for w in fc])                       # (q, 3)
        last = tr[-1]                                                            # (3, m)
        dc = np.sqrt(((last[None, :, :] - pts[:, :, None]) ** 2).sum(1)).min(0); ex['dcyc'] = dc
    onpage = zmax < ztol
    cyc = per > 0
    codes = np.full(m, SLOW, np.int8)
    if fc is not None:
        codes[cyc & onpage & (ex['dcyc'] < 1e-5)] = FLATCYC
        codes[cyc & onpage & (ex['dcyc'] >= 1e-5)] = PAGE
        codes[~cyc & onpage] = PAGE
    else:
        codes[onpage] = FLATCYC                                                   # Siegel: the flat picture's own curves
    codes[cyc & ~onpage] = OFFCYC
    rest = np.where(~cyc & ~onpage)[0]
    if rest.size:
        lam = lyap(r, tr[-1, 0, rest], tr[-1, 1, rest], tr[-1, 2, rest], c, lyap_steps, burn + trail)
        ex['lam'][rest] = lam
        codes[rest] = np.where(lam > 0.01, CLOUD, np.where(lam > -0.01, CURVE, SLOW))
    code[gid] = codes
    return code.reshape(sh), ex


# colours for the fates (dark background pictures)
FATE_RGB = {OUT: (22, 28, 44), FLATCYC: (240, 226, 190), PAGE: (150, 200, 150), OFFCYC: (255, 120, 60), CURVE: (90, 190, 255), CLOUD: (235, 90, 200), SLOW: (130, 130, 130)}


def paint(code):
    img = np.zeros(code.shape + (3,), np.uint8)
    for k, col in FATE_RGB.items():
        img[code == k] = col
    return img


def route(r, x, y, z, c, steps=120, h0=0.02, near=0.05):
    """The way in, for every start point (arrays of the shape of x):
    n       steps it stayed (as M.stay);  inside = n >= steps
    phase   which point of the flat cycle it sits on at the last step (-1: none within `near`, or no flat cycle).
            steps should be a multiple of the cycle's length; then phase names the BODY the start point belongs to.
    land    the first step after which its height |z| is under h0 for good (0 = it started that low; steps = never)
    arrive  the first step at which it is within `near` of the flat cycle (steps = never)
    Only meaningful for the points that stay."""
    sh = np.shape(x); m = int(np.prod(sh))
    n, idx, end, _ = follow(r, x, y, z, c, steps)
    xs, ys, zs = (np.array(np.broadcast_to(np.asarray(t, float), sh)).ravel()[idx] for t in (x, y, z))
    cx, cy, cz = (np.full(idx.size, t) for t in c); st = tuple(r.init(idx.size))
    fc = flat_cycle(c); pts = None if fc is None else np.array([[w.real, w.imag, 0.0] for w in fc])
    land = np.where(np.abs(zs) < h0, 0, steps).astype(np.int32); arrive = np.full(idx.size, steps, np.int32)
    for k in range(steps):
        o = r.step(xs, ys, zs, st, k, cx, cy, cz); st = tuple(o[3]); xs, ys, zs = o[0] + cx, o[1] + cy, o[2] + cz
        low = np.abs(zs) < h0
        land = np.where(low, np.minimum(land, k + 1), steps)                    # reset whenever it rises again
        if pts is not None:
            d = np.sqrt((xs[None] - pts[:, 0, None]) ** 2 + (ys[None] - pts[:, 1, None]) ** 2 + (zs[None] - pts[:, 2, None]) ** 2).min(0)
            arrive = np.where((d < near) & (arrive == steps), k + 1, arrive)
    phase = np.full(idx.size, -1, np.int32)
    if pts is not None and idx.size:
        d = np.sqrt((xs[None] - pts[:, 0, None]) ** 2 + (ys[None] - pts[:, 1, None]) ** 2 + (zs[None] - pts[:, 2, None]) ** 2)
        phase = np.where(d.min(0) < near, d.argmin(0), -1)
    out = {}
    for nm, v, fill in (('phase', phase, -1), ('land', land, steps), ('arrive', arrive, steps)):
        a = np.full(m, fill, np.int32); a[idx] = v; out[nm] = a.reshape(sh)
    out['n'] = n; out['inside'] = n >= steps
    return out


def wrap(d, text, font, maxw):
    """Break a sentence into lines no wider than maxw pixels."""
    words = text.split(); lines = []; cur = ''
    for w in words:
        t = (cur + ' ' + w).strip()
        if d.textlength(t, font=font) <= maxw or not cur:
            cur = t
        else:
            lines.append(cur); cur = w
    if cur:
        lines.append(cur)
    return lines


def solid2(r, c, w, h, nd, steps, eye, centre=(0.0, 0.0, 0.0), half_w=1.5):
    """M.solid with the height (z) kept upright on the screen, for an eye that looks along the flat page.
    Returns (depth, pixel size, (e1, e2, e3))."""
    p = np.array(eye, float); p /= np.linalg.norm(p)
    e1 = np.cross([0.0, 0.0, 1.0], p); e1 /= np.linalg.norm(e1); e2 = np.cross(p, e1); e3 = -p
    us = np.linspace(-half_w, half_w, w); vs = np.linspace(half_w * h / w, -half_w * h / w, h); ds = np.linspace(-half_w, half_w, nd)
    U, V = np.meshgrid(us, vs); depth = np.full((h, w), np.inf)
    for k0 in range(0, nd, 8):
        dk = ds[k0:k0 + 8]
        P = [centre[i] + U[None] * e1[i] + V[None] * e2[i] + dk[:, None, None] * e3[i] for i in range(3)]
        n = M.stay(r, P[0], P[1], P[2], c[0], c[1], c[2], steps); ins = n >= steps
        depth = np.minimum(depth, np.where(ins.any(0), dk[np.argmax(ins, 0)], np.inf))
    return depth, us[1] - us[0], (e1, e2, e3)

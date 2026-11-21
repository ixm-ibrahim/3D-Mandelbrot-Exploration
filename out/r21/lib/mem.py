"""Round 21 library: RULES WITH MEMORY (the orbit carries something along besides the point), and quick pictures.

    import sys; sys.path.insert(0, '<root>/out/r21/lib'); import mem as M

A rule is M.Rule(name, label, step, init):
    step(x, y, z, st, k, cx, cy, cz) -> (X, Y, Z, st')
        x, y, z   float arrays of one length: the orbit points
        st        a tuple of float arrays of that same length: whatever the orbit carries (may be empty)
        k         how many squarings this orbit has had before this one (a plain number)
        cx, cy, cz  the constant of each orbit, for rules that look at c (c is ADDED by the library, not by step)
        returns the 'square' of the point WITHOUT c, and the new carried state
    init(n) -> the carried state of n fresh orbits. Default: the flat page as the sheet u = (1, 0).

A carried SHEET is a flat sheet through the x-axis at the turn theta. It is kept as u = (cos 2 theta, sin 2 theta):
a sheet has no front and back, so theta and theta + 180 degrees are the same sheet, and the doubled angle says so.

Every picture and number here is made point by point: one orbit per pixel or block, no renderer.
The Mandelbrot orbit is the orbit of 0. Its first step lands on c with nothing squared, so it is started at c with
k = 0 (a rule that needs the very first squaring to be special sees k == 0 at the point c).
"""
import os, sys, time
import numpy as np
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, 'out', 'me', 'r16'))
import scout as S

RABBIT = (-0.122561, 0.744862, 0.0); SIEGEL = (-0.390541, -0.586788, 0.0)
JSETS = [('basilica, c = -1', (-1.0, 0.0, 0.0)), ('San Marco, c = -0.75', (-0.75, 0.0, 0.0)), ('airplane, c = -1.7549', (-1.754878, 0.0, 0.0)),
         ('rabbit', RABBIT), ('Siegel disc', SIEGEL), ('dendrite, c = i', (0.0, 1.0, 0.0))]


class Rule:
    def __init__(self, name, label, step, init=None):
        self.name, self.label, self.step = name, label, step
        self.init = init or (lambda n: (np.ones(n), np.zeros(n)))


# ---------------------------------------------------------------- the building blocks
def half(u1, u2):
    """cos and sin of theta from the doubled-angle vector, theta in (-90, 90] degrees."""
    return np.sqrt(np.clip((1 + u1) / 2, 0, 1)), np.where(u2 >= 0, 1.0, -1.0) * np.sqrt(np.clip((1 - u1) / 2, 0, 1))


def sq_about(x, y, z, u1, u2, F=None):
    """The one-plane square (or another fixed rule F(x, y, z)) taken about the sheet u instead of the flat page."""
    co, si = half(u1, u2)
    X, Y, Z = (F or S.oneplane)(x, co * y + si * z, co * z - si * y)
    return X, co * Y - si * Z, si * Y + co * Z


def sheet_of(y, z, u1=1.0, u2=0.0):
    """The sheet that a point makes with the x-axis (u is kept where the point lies on the x-axis)."""
    q1, q2 = y * y - z * z, 2 * y * z; n = np.hypot(q1, q2); ok = n > 1e-300; m = np.where(ok, n, 1.0)
    return np.where(ok, q1 / m, u1), np.where(ok, q2 / m, u2)


def blend(u1, u2, p1, p2, lam):
    """Move the sheet u the share lam of the way toward the sheet p (kept where the two cancel)."""
    b1, b2 = (1 - lam) * u1 + lam * p1, (1 - lam) * u2 + lam * p2
    n = np.hypot(b1, b2); ok = n > 1e-9; m = np.where(ok, n, 1.0)
    return np.where(ok, b1 / m, u1), np.where(ok, b2 / m, u2)


def fixed(F, name='fixed', label=''):
    """A fixed rule F(x, y, z) -> (X, Y, Z) of the bench, wrapped so that the same tools draw it. Carries nothing."""
    return Rule(name, label or name, lambda x, y, z, st, k, cx, cy, cz: (*F(x, y, z), st), init=lambda n: ())


def bench(name):
    """A rule of the round-16 bench by its name ('along', 'oneplane', 'lathe', 'm_w3', ...)."""
    sys.path.insert(0, os.path.join(ROOT, 'out', 'r16', 'bench'))
    import rules as R
    return fixed(R.get(name), name, R.RULES[name][1])


# the scout's variants (out/r21/me/follow.py), as rules of this library
def _own(x, y, z, st, k, cx, cy, cz):
    u = sheet_of(y, z, *st); return (*sq_about(x, y, z, *u), u)


def _first(x, y, z, st, k, cx, cy, cz):
    u = sheet_of(y, z, *st) if k > 0 else st; return (*sq_about(x, y, z, *u), u)


def _delay(x, y, z, st, k, cx, cy, cz):
    return (*sq_about(x, y, z, *st), sheet_of(y, z, *st))


def lag(lam):
    def f(x, y, z, st, k, cx, cy, cz):
        u = blend(*st, *sheet_of(y, z, *st), lam); return (*sq_about(x, y, z, *u), u)
    return f


SCOUT = [
    Rule('fixed', 'The sheet never moves (the one-plane rule)', lambda x, y, z, st, k, cx, cy, cz: (*sq_about(x, y, z, *st), st)),
    Rule('lag25', 'Before each squaring the sheet moves a quarter of the way to the point', lag(0.25)),
    Rule('lag50', 'Before each squaring the sheet moves half of the way to the point', lag(0.5)),
    Rule('lag75', 'Before each squaring the sheet moves three quarters of the way to the point', lag(0.75)),
    Rule('delay', 'Each point is squared about the sheet of the point before it', _delay),
    Rule('first', 'First squaring about the flat page, every later one about the point\'s own sheet', _first),
    Rule('own', 'Each point is squared about its own sheet, at once (the lathe)', _own),
]


# ---------------------------------------------------------------- orbits
def stay(rule, x, y, z, cx, cy, cz, steps, r2=36.0):
    """How many steps each orbit stays inside the ball (steps = it never left). Orbits that have left are dropped."""
    sh = np.shape(x)
    cx, cy, cz = (np.broadcast_to(np.asarray(t, float), sh).ravel() for t in (cx, cy, cz))
    x, y, z = (np.array(np.broadcast_to(np.asarray(t, float), sh)).ravel() for t in (x, y, z))
    st = tuple(rule.init(x.size)); n = np.zeros(x.size, np.int32); idx = np.arange(x.size)
    for k in range(steps):
        out = rule.step(x, y, z, st, k, cx, cy, cz); X, Y, Z, st = out[0], out[1], out[2], tuple(out[3])
        x, y, z = X + cx, Y + cy, Z + cz
        keep = (x * x + y * y + z * z) < r2
        idx = idx[keep]; x, y, z, cx, cy, cz = (t[keep] for t in (x, y, z, cx, cy, cz)); st = tuple(t[keep] for t in st)
        n[idx] += 1
        if idx.size == 0:
            break
    return n.reshape(sh)


def mandel(rule, cx, cy, cz, steps):
    return stay(rule, cx, cy, cz, cx, cy, cz, steps)


def flat_stay(zr, zi, cr, ci, steps, r2=36.0):
    """The flat (complex) orbit, counted the same way."""
    zr, zi = np.array(zr, float), np.array(zi, float); n = np.zeros(zr.shape, np.int32); alive = np.ones(zr.shape, bool)
    for _ in range(steps):
        zr, zi = np.where(alive, zr * zr - zi * zi + cr, zr), np.where(alive, 2 * zr * zi + ci, zi)
        alive &= zr * zr + zi * zi < r2; n += alive
    return n


# ---------------------------------------------------------------- two numbers every rule should be asked for
def flat_check(rule, n=40000, steps=60, seed=3):
    """Is the flat page exactly the flat picture? Counts verdicts that differ from the complex orbit (Mandelbrot set,
    and the Julia sets of c = -1, the rabbit and the Siegel disc), and how far a flat orbit strays from the page."""
    rng = np.random.default_rng(seed); out = {}; zero = np.zeros(n)
    cr, ci = rng.uniform(-2.1, 0.7, n), rng.uniform(-1.3, 1.3, n)
    out['mandelbrot'] = int(((mandel(rule, cr, ci, zero, steps) >= steps) != (flat_stay(cr, ci, cr, ci, steps) >= steps)).sum())
    zr, zi = rng.uniform(-1.8, 1.8, n), rng.uniform(-1.3, 1.3, n)
    for nm, c in (('basilica', (-1.0, 0.0)), ('rabbit', RABBIT[:2]), ('siegel', SIEGEL[:2])):
        out[nm] = int(((stay(rule, zr, zi, zero, c[0], c[1], 0.0, steps) >= steps) != (flat_stay(zr, zi, c[0], c[1], steps) >= steps)).sum())
    x, y, z = zr.copy(), zi.copy(), zero.copy(); st = tuple(rule.init(n)); worst = 0.0
    for k in range(12):
        X, Y, Z, st = rule.step(x, y, z, st, k, np.full(n, RABBIT[0]), np.full(n, RABBIT[1]), zero); st = tuple(st)
        worst = max(worst, float(np.nanmax(np.abs(Z))))                       # how far ONE squaring throws a flat point off the page
        x, y, z = np.clip(X + RABBIT[0], -6, 6), np.clip(Y + RABBIT[1], -6, 6), 0 * Z   # put back on the page, so that rounding does not pile up
    out['off_the_page'] = worst; out['of'] = n
    return out


def spun_check(rule, n=40000, steps=40, seed=5):
    """Is the solid the same from every side of the x-axis? Each test point is paired with itself turned by a random
    angle round the x-axis; the share of pairs with different verdicts is returned (0 = spun) for the Mandelbrot solid
    and for the Julia set of c = -1, with the share that is inside."""
    rng = np.random.default_rng(seed); a = rng.uniform(0, 2 * np.pi, n); co, si = np.cos(a), np.sin(a)
    c = rng.uniform([-2.1, -1.3, -1.3], [0.7, 1.3, 1.3], size=(n, 3))
    m1 = mandel(rule, c[:, 0], c[:, 1], c[:, 2], steps) >= steps
    m2 = mandel(rule, c[:, 0], co * c[:, 1] - si * c[:, 2], si * c[:, 1] + co * c[:, 2], steps) >= steps
    v = rng.uniform([-1.8, -1.2, -1.2], [1.8, 1.2, 1.2], size=(n, 3))
    j1 = stay(rule, v[:, 0], v[:, 1], v[:, 2], -1.0, 0.0, 0.0, steps) >= steps
    j2 = stay(rule, v[:, 0], co * v[:, 1] - si * v[:, 2], si * v[:, 1] + co * v[:, 2], -1.0, 0.0, 0.0, steps) >= steps
    return {'mandel_inside': float(m1.mean()), 'mandel_differ': float((m1 != m2).mean()), 'basilica_inside': float(j1.mean()), 'basilica_differ': float((j1 != j2).mean())}


# ---------------------------------------------------------------- cuts and rough solids
def cut_axis(rule, ang, w, h, steps, c=None, box=None):
    """A cut along a sheet through the x-axis, turned ang degrees from the flat page. c = None: the Mandelbrot solid
    (default box -2.1..0.7, -1.3..1.3). c given: the Julia set of c (default box -1.8..1.8, -1.3..1.3)."""
    box = box or ((-2.1, 0.7, -1.3, 1.3) if c is None else (-1.8, 1.8, -1.3, 1.3))
    u, s = np.meshgrid(np.linspace(box[0], box[1], w), np.linspace(box[3], box[2], h)); a = np.radians(ang)
    P = (u, s * np.cos(a), s * np.sin(a))
    return mandel(rule, *P, steps) if c is None else stay(rule, *P, c[0], c[1], c[2], steps)


def cut_across(rule, x0, w, steps, c=None, L=1.3):
    """A cut across the x-axis at x = x0 (y to the right, z up)."""
    p, q = np.meshgrid(np.linspace(-L, L, w), np.linspace(L, -L, w)); P = (np.full_like(p, x0), p, q)
    return mandel(rule, *P, steps) if c is None else stay(rule, *P, c[0], c[1], c[2], steps)


def shade(n, steps):
    inside = n >= steps; t = np.clip(n / steps, 0, 1) ** 0.6
    img = np.zeros(n.shape + (3,), np.uint8)
    img[..., 0] = (20 + 40 * t).astype(np.uint8); img[..., 1] = (26 + 70 * t).astype(np.uint8); img[..., 2] = (40 + 150 * t).astype(np.uint8)
    img[inside] = (238, 228, 200)
    return img


def frame(cam):
    p = np.array(cam, float); p /= np.linalg.norm(p)
    e1 = np.cross([0.0, 1.0, 0.0], p); e1 /= np.linalg.norm(e1)
    return e1, np.cross(p, e1), -p                 # screen right, screen up, depth (away from the eye)


def solid(rule, c, w, h, nd, steps, centre=None, half_w=None, cam=(0.45, 0.5, 1.0)):
    """A rough picture: the first block on each line of sight whose orbit never leaves. c = None: the Mandelbrot solid.
    cam is where the eye stands (x to the right, y up, z toward the eye for cam = (0, 0, 1)). Returns (depth, pixel size)."""
    centre = centre or ((-0.7, 0.0, 0.0) if c is None else (0.0, 0.0, 0.0)); half_w = half_w or (1.7 if c is None else 1.75)
    e1, e2, e3 = frame(cam)
    us = np.linspace(-half_w, half_w, w); vs = np.linspace(half_w * h / w, -half_w * h / w, h); ds = np.linspace(-half_w, half_w, nd)
    U, V = np.meshgrid(us, vs); depth = np.full((h, w), np.inf)
    for k0 in range(0, nd, 8):
        dk = ds[k0:k0 + 8]
        P = [centre[i] + U[None] * e1[i] + V[None] * e2[i] + dk[:, None, None] * e3[i] for i in range(3)]
        n = mandel(rule, P[0], P[1], P[2], steps) if c is None else stay(rule, P[0], P[1], P[2], c[0], c[1], c[2], steps)
        ins = n >= steps
        depth = np.minimum(depth, np.where(ins.any(0), dk[np.argmax(ins, 0)], np.inf))     # slabs come front to back
    return depth, us[1] - us[0]


def shade_solid(depth, px):
    hit = np.isfinite(depth); d = np.where(hit, depth, 0.0); img = np.zeros(depth.shape + (3,), np.uint8); img[...] = (14, 17, 26)
    if not hit.any():
        return img
    H, W = d.shape
    for _ in range(2):                                         # soften the steps between blocks a little
        pad = np.pad(d, 1, mode='edge'); wgt = np.pad(hit.astype(float), 1)
        num = sum(np.where(wgt[i:i + H, j:j + W] > 0, pad[i:i + H, j:j + W], 0) for i in range(3) for j in range(3))
        den = sum(wgt[i:i + H, j:j + W] for i in range(3) for j in range(3))
        d = np.where(hit, num / np.maximum(den, 1), 0.0)
    gy, gx = np.gradient(d, px)
    nrm = np.stack([gx, -gy, -np.ones_like(d)], -1); nrm /= np.linalg.norm(nrm, axis=-1, keepdims=True)
    light = np.array([-0.45, 0.6, -0.66]); light /= np.linalg.norm(light)
    lam = np.clip((nrm * light).sum(-1), 0, 1)
    near = np.clip((d[hit].max() - d) / max(float(np.ptp(d[hit])), 1e-9), 0, 1)
    v = 0.18 + 0.72 * lam + 0.10 * near
    img[hit] = np.clip(v[hit, None] * np.array([238, 226, 196.0]), 0, 255).astype(np.uint8)
    return img


def font(sz):
    for f in ('segoeui.ttf', 'arial.ttf'):
        try:
            return ImageFont.truetype(f, sz)
        except Exception:
            pass
    return ImageFont.load_default()


# ---------------------------------------------------------------- sheets
def julia_sheet(rules, path, sets=None, w=380, h=285, nd=240, steps=28, cam=(0.45, 0.5, 1.0), title=None):
    """One row per rule, one rough solid per Julia set."""
    sets = sets or JSETS; pad = 10; t0 = time.time()
    W = pad + len(sets) * (w + pad); H = 56 + len(rules) * (h + 36)
    im = Image.new('RGB', (W, H), (12, 14, 20)); d = ImageDraw.Draw(im)
    d.text((pad, 10), title or 'Julia sets (rough blocks, %d steps, eye at %s)' % (steps, cam), fill=(240, 240, 245), font=font(22))
    for i, r in enumerate(rules):
        y = 56 + i * (h + 36); d.text((pad, y), '%s: %s' % (r.name, r.label), fill=(235, 220, 170), font=font(17))
        for j, (sn, c) in enumerate(sets):
            dep, px = solid(r, c, w, h, nd, steps, cam=cam); x = pad + j * (w + pad)
            im.paste(Image.fromarray(shade_solid(dep, px)), (x, y + 26)); d.text((x + 6, y + 30), sn, fill=(150, 160, 175), font=font(13))
        print('julia', r.name, '%.0f s' % (time.time() - t0)); sys.stdout.flush()
    im.save(path); return path


def mandel_sheet(rules, path, w=380, cw=300, ch=280, nd=240, steps=22, cut_steps=60, angles=(0.0, 22.5, 45.0, 90.0), x0=-0.12, cam=(0.45, 0.5, 1.0), title=None):
    """One row per rule: cuts of the Mandelbrot solid along sheets through the x-axis, one cut across it, and the rough solid."""
    pad = 10; t0 = time.time()
    heads = ['cut along the sheet turned %g' % a for a in angles] + ['cut across the x-axis at x = %g' % x0, 'the whole solid, rough']
    tw = [cw] * len(angles) + [ch, w]
    W = pad + sum(t + pad for t in tw); H = 56 + len(rules) * (ch + 58)
    im = Image.new('RGB', (W, H), (12, 14, 20)); d = ImageDraw.Draw(im)
    d.text((pad, 10), title or 'The Mandelbrot solid (cuts: %d steps, solid: %d steps)' % (cut_steps, steps), fill=(240, 240, 245), font=font(22))
    for i, r in enumerate(rules):
        y = 56 + i * (ch + 58); d.text((pad, y), '%s: %s' % (r.name, r.label), fill=(235, 220, 170), font=font(17))
        pics = [shade(cut_axis(r, a, cw, ch, cut_steps), cut_steps) for a in angles] + [shade(cut_across(r, x0, ch, cut_steps), cut_steps)]
        dep, px = solid(r, None, w, ch, nd, steps, cam=cam); pics.append(shade_solid(dep, px))
        x = pad
        for hd, pic in zip(heads, pics):
            d.text((x, y + 24), hd, fill=(150, 160, 175), font=font(13)); im.paste(Image.fromarray(pic), (x, y + 44)); x += pic.shape[1] + pad
        print('mandel', r.name, '%.0f s' % (time.time() - t0)); sys.stdout.flush()
    im.save(path); return path


if __name__ == '__main__':
    # python out/r21/lib/mem.py            the two numbers for the scout's rules and three fixed rules of the bench
    rs = SCOUT + [bench('along'), bench('lathe')]
    for r in rs:
        f = flat_check(r, n=8000); s = spun_check(r, n=8000)
        print('%-8s flat page: verdicts that differ M %d, basilica %d, rabbit %d, Siegel %d of %d; strays %.1e | turned: M differs %.2f%%, basilica differs %.2f%%'
              % (r.name, f['mandelbrot'], f['basilica'], f['rabbit'], f['siegel'], f['of'], f['off_the_page'], 100 * s['mandel_differ'], 100 * s['basilica_differ']))

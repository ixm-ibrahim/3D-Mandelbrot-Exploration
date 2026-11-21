"""The user's question of 2026-11-19 (second): "how about following whatever new plane is made during the orbit?"

Rules WITH MEMORY. The orbit carries a reference sheet along with the point: a flat sheet through the x-axis, at the
turn theta. Each step squares the point by the one-plane rule about the current sheet, adds c, and the sheet is then
(or first) moved toward the sheet that the orbit point itself makes with the x-axis. The sheet starts as the flat
page (theta = 0): that start is the only thing in the recipe that is not the same from every side of the x-axis.

    python out/r21/me/follow.py [quick]     -> out/r21/me/follow-julia.png, follow-mandel.png

The sheet is kept as the unit vector u = (cos 2 theta, sin 2 theta): a sheet has no front and back, so theta and
theta + 180 degrees are the same sheet, and the doubled angle says so.
A variant is a function (x, y, z, u1, u2, k) -> (X, Y, Z, u1', u2'), k = how many squarings came before, without c.
"""
import os, sys, time
import numpy as np
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(ROOT, 'out', 'r16', 'bench')); sys.path.insert(0, os.path.join(ROOT, 'out', 'me', 'r16'))
import scout as S
import truth as T
import cplane as C


def half(u1, u2):
    """cos and sin of theta from the doubled-angle vector, theta in (-90, 90] degrees."""
    return np.sqrt(np.clip((1 + u1) / 2, 0, 1)), np.where(u2 >= 0, 1.0, -1.0) * np.sqrt(np.clip((1 - u1) / 2, 0, 1))


def sq_about(x, y, z, u1, u2):
    """The one-plane square about the sheet u."""
    co, si = half(u1, u2)
    X, Y, Z = S.oneplane(x, co * y + si * z, co * z - si * y)
    return X, co * Y - si * Z, si * Y + co * Z


def sheet_of(y, z, u1, u2):
    """The sheet that the point makes with the x-axis (u is kept where the point lies on the x-axis)."""
    q1, q2 = y * y - z * z, 2 * y * z; n = np.hypot(q1, q2); ok = n > 1e-300; m = np.where(ok, n, 1.0)
    return np.where(ok, q1 / m, u1), np.where(ok, q2 / m, u2)


def v_fixed(x, y, z, u1, u2, k):                 # the sheet never moves: the one-plane rule
    X, Y, Z = sq_about(x, y, z, u1, u2); return X, Y, Z, u1, u2


def v_own(x, y, z, u1, u2, k):                   # the sheet is the point's own sheet, at once: the lathe
    u1, u2 = sheet_of(y, z, u1, u2); X, Y, Z = sq_about(x, y, z, u1, u2); return X, Y, Z, u1, u2


def v_first(x, y, z, u1, u2, k):                 # first squaring about the flat page, every later one about the point's own sheet
    if k > 0:
        u1, u2 = sheet_of(y, z, u1, u2)
    X, Y, Z = sq_about(x, y, z, u1, u2); return X, Y, Z, u1, u2


def v_delay(x, y, z, u1, u2, k):                 # squared about the sheet of the point BEFORE; then the sheet moves to this point's
    X, Y, Z = sq_about(x, y, z, u1, u2); n1, n2 = sheet_of(y, z, u1, u2); return X, Y, Z, n1, n2


def v_lag(lam):                                  # the sheet moves the share lam of the way to the point's own sheet, then the point is squared
    def f(x, y, z, u1, u2, k):
        p1, p2 = sheet_of(y, z, u1, u2); b1, b2 = (1 - lam) * u1 + lam * p1, (1 - lam) * u2 + lam * p2
        n = np.hypot(b1, b2); ok = n > 1e-9; m = np.where(ok, n, 1.0)
        u1, u2 = np.where(ok, b1 / m, u1), np.where(ok, b2 / m, u2)
        X, Y, Z = sq_about(x, y, z, u1, u2); return X, Y, Z, u1, u2
    return f


VARIANTS = [
    ('fixed', v_fixed, 'The sheet never moves (this is the one-plane rule)'),
    ('lag25', v_lag(0.25), 'Before each squaring the sheet moves a quarter of the way to the point'),
    ('lag50', v_lag(0.5), 'Before each squaring the sheet moves half of the way to the point'),
    ('lag75', v_lag(0.75), 'Before each squaring the sheet moves three quarters of the way to the point'),
    ('delay', v_delay, 'Each point is squared about the sheet of the point before it'),
    ('first', v_first, 'First squaring about the flat page, every later one about the point\'s own sheet'),
    ('own', v_own, 'Each point is squared about its own sheet, at once (this is the lathe)'),
]


def stay(V, x, y, z, cx, cy, cz, steps, r2=36.0):
    """How many steps each orbit stays inside. The sheet starts as the flat page."""
    sh = x.shape
    cx, cy, cz = (np.broadcast_to(np.asarray(t, float), sh).ravel() for t in (cx, cy, cz))
    x, y, z = (np.asarray(t, float).ravel() for t in (x, y, z))
    u1, u2 = np.ones(x.size), np.zeros(x.size)
    n = np.zeros(x.size, np.int32); idx = np.arange(x.size)
    for k in range(steps):
        X, Y, Z, u1, u2 = V(x, y, z, u1, u2, k)
        x, y, z = X + cx, Y + cy, Z + cz
        keep = (x * x + y * y + z * z) < r2
        idx = idx[keep]; x, y, z, cx, cy, cz, u1, u2 = (t[keep] for t in (x, y, z, cx, cy, cz, u1, u2))
        n[idx] += 1
        if idx.size == 0:
            break
    return n.reshape(sh)


def mandel(V, cx, cy, cz, steps):
    """The orbit of 0. Its first step lands on c with nothing squared, so the count of squarings starts at c."""
    return stay(V, cx, cy, cz, cx, cy, cz, steps)


def cut_axis(V, ang, w, h, steps, box=(-2.1, 0.7, -1.3, 1.3)):
    u, s = np.meshgrid(np.linspace(box[0], box[1], w), np.linspace(box[3], box[2], h)); a = np.radians(ang)
    return mandel(V, u, s * np.cos(a), s * np.sin(a), steps)


def cut_across(V, x0, w, steps, L=1.3):
    p, q = np.meshgrid(np.linspace(-L, L, w), np.linspace(L, -L, w))
    return mandel(V, np.full_like(p, x0), p, q, steps)


def solid(V, mode, c, centre, half_w, w, h, nd, steps, cam=(0.45, 0.5, 1.0)):
    e1, e2, e3 = C.frame(cam)
    us = np.linspace(-half_w, half_w, w); vs = np.linspace(half_w * h / w, -half_w * h / w, h); ds = np.linspace(-half_w, half_w, nd)
    U, Vv = np.meshgrid(us, vs); depth = np.full((h, w), np.inf)
    for k0 in range(0, nd, 8):
        dk = ds[k0:k0 + 8]
        P = [centre[i] + U[None] * e1[i] + Vv[None] * e2[i] + dk[:, None, None] * e3[i] for i in range(3)]
        n = mandel(V, P[0], P[1], P[2], steps) if mode == 'm' else stay(V, P[0], P[1], P[2], c[0], c[1], c[2], steps)
        ins = n >= steps
        depth = np.minimum(depth, np.where(ins.any(0), dk[np.argmax(ins, 0)], np.inf))
    return depth, us[1] - us[0]


JSETS = [('basilica, c = -1', (-1.0, 0.0, 0.0)), ('San Marco, c = -0.75', (-0.75, 0.0, 0.0)), ('rabbit', (-0.122561, 0.744862, 0.0)),
         ('Siegel disc', (-0.390541, -0.586788, 0.0))]


def main():
    quick = len(sys.argv) > 1 and sys.argv[1] == 'quick'
    only = [a for a in sys.argv[1:] if a != 'quick']
    var = [v for v in VARIANTS if not only or v[0] in only]
    w, h, nd, sj, sm = (200, 150, 96, 18, 16) if quick else (380, 285, 240, 28, 22)
    cw, ch, sc = (150, 140, 30) if quick else (300, 280, 60)
    pad = 10; t0 = time.time(); tag = '-quick' if quick else ''
    # ---- Julia sets
    W = pad + len(JSETS) * (w + pad); H = 56 + len(var) * (h + 36)
    im = Image.new('RGB', (W, H), (12, 14, 20)); d = ImageDraw.Draw(im)
    d.text((pad, 10), 'Julia sets when the sheet follows the orbit (rough blocks, %d steps)' % sj, fill=(240, 240, 245), font=T.font(22))
    for i, (nm, V, label) in enumerate(var):
        y = 56 + i * (h + 36); d.text((pad, y), label, fill=(235, 220, 170), font=T.font(17))
        for j, (sn, c) in enumerate(JSETS):
            dep, px = solid(V, 'j', c, (0.0, 0.0, 0.0), 1.75, w, h, nd, sj); x = pad + j * (w + pad)
            im.paste(Image.fromarray(C.shade_solid(dep, px)), (x, y + 26)); d.text((x + 6, y + 30), sn, fill=(150, 160, 175), font=T.font(13))
        print('julia', nm, '%.0f s' % (time.time() - t0)); sys.stdout.flush()
    im.save(os.path.join(HERE, 'follow-julia%s.png' % tag))
    # ---- Mandelbrot solid
    heads = ['cut along the flat page', 'cut along a sheet turned 22.5', 'cut along the upright sheet (90)', 'cut across the x-axis (x = -0.12)', 'the whole solid, rough']
    tw = [cw, cw, cw, ch, w]
    W = pad + sum(t + pad for t in tw); H = 56 + len(var) * (ch + 58)
    im = Image.new('RGB', (W, H), (12, 14, 20)); d = ImageDraw.Draw(im)
    d.text((pad, 10), 'The Mandelbrot solid when the sheet follows the orbit', fill=(240, 240, 245), font=T.font(22))
    for i, (nm, V, label) in enumerate(var):
        y = 56 + i * (ch + 58); d.text((pad, y), label, fill=(235, 220, 170), font=T.font(17))
        pics = [T.shade(cut_axis(V, a, cw, ch, sc), sc) for a in (0.0, 22.5, 90.0)] + [T.shade(cut_across(V, -0.12, ch, sc), sc)]
        dep, px = solid(V, 'm', None, (-0.7, 0.0, 0.0), 1.7, w, ch, nd, sm); pics.append(C.shade_solid(dep, px))
        x = pad
        for hd, pic in zip(heads, pics):
            d.text((x, y + 24), hd, fill=(150, 160, 175), font=T.font(13)); im.paste(Image.fromarray(pic), (x, y + 44)); x += pic.shape[1] + pad
        print('mandel', nm, '%.0f s' % (time.time() - t0)); sys.stdout.flush()
    im.save(os.path.join(HERE, 'follow-mandel%s.png' % tag)); print('done', '%.0f s' % (time.time() - t0))


if __name__ == '__main__':
    main()

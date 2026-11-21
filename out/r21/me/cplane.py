"""The user's question of 2026-11-19: why not square every tested point about the plane that c creates
(the flat plane through the x-axis and c), instead of about a plane of the point's own ("along")?

    python out/r21/me/cplane.py [quick]     -> out/r21/me/plane-follows-c.png, numbers on the screen

The rule is taken literally: for each c the base rule F is turned round the x-axis until its flat plane holds c,
    F_c(v) = Rot(a_c) F(Rot(-a_c) v),   a_c = the turn of c round the x-axis,
and the orbit is v -> F_c(v) + c. Nothing is assumed about what comes out: every pixel and every block is one
point followed step by step.
"""
import os, sys, time
import numpy as np
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, 'out', 'r16', 'bench')); sys.path.insert(0, os.path.join(ROOT, 'out', 'me', 'r16'))
import rules as R
import truth as T

QUICK = len(sys.argv) > 1 and sys.argv[1] == 'quick'


def follow(F):
    """F turned so that its flat plane is the plane through the x-axis and c."""
    def G(x, y, z, cx, cy, cz):
        rho = np.hypot(cy, cz); ok = rho > 0; q = np.where(ok, rho, 1.0)
        co = np.where(ok, cy / q, 1.0); si = np.where(ok, cz / q, 0.0)
        X, Y, Z = F(x, co * y + si * z, co * z - si * y)
        return X, co * Y - si * Z, si * Y + co * Z
    return G


def fixed(F):
    return lambda x, y, z, cx, cy, cz: F(x, y, z)


def stay(G, x, y, z, cx, cy, cz, steps, r2=36.0):
    """How many steps each orbit stays inside (steps = never left). c may be arrays (Mandelbrot) or numbers (Julia)."""
    sh = x.shape
    cx, cy, cz = (np.broadcast_to(np.asarray(t, float), sh).ravel() for t in (cx, cy, cz))
    x, y, z = (np.asarray(t, float).ravel() for t in (x, y, z))
    n = np.zeros(x.size, np.int32); idx = np.arange(x.size)
    for _ in range(steps):                                    # only the orbits still inside are carried on
        X, Y, Z = G(x, y, z, cx, cy, cz)
        x, y, z = X + cx, Y + cy, Z + cz
        keep = (x * x + y * y + z * z) < r2
        idx = idx[keep]; x, y, z, cx, cy, cz = x[keep], y[keep], z[keep], cx[keep], cy[keep], cz[keep]
        n[idx] += 1
        if idx.size == 0:
            break
    return n.reshape(sh)


def mandel(G, cx, cy, cz, steps):
    return stay(G, np.zeros_like(cx), np.zeros_like(cx), np.zeros_like(cx), cx, cy, cz, steps)


def cut_axis(G, ang, w, h, steps, box=(-2.1, 0.7, -1.3, 1.3)):
    """Mandelbrot solid cut by a plane through the x-axis, turned ang degrees from the flat plane."""
    u, s = np.meshgrid(np.linspace(box[0], box[1], w), np.linspace(box[3], box[2], h)); a = np.radians(ang)
    return mandel(G, u, s * np.cos(a), s * np.sin(a), steps)


def cut_across(G, x0, w, steps, L=1.3):
    """Mandelbrot solid cut across the x-axis at x = x0."""
    p, q = np.meshgrid(np.linspace(-L, L, w), np.linspace(L, -L, w))
    return mandel(G, np.full_like(p, x0), p, q, steps)


def frame(cam):
    p = np.array(cam, float); p /= np.linalg.norm(p)
    e1 = np.cross([0.0, 1.0, 0.0], p); e1 /= np.linalg.norm(e1); e2 = np.cross(p, e1)
    return e1, e2, -p                       # screen right, screen up, depth (away from the eye)


def solid(G, mode, c, centre, half, w, h, nd, steps, cam=(0.45, 0.5, 1.0)):
    """Rough picture of a solid: the first block on each line of sight that never leaves. mode 'm': the block is c
    and the orbit starts at 0. mode 'j': the block is the start point and c is the given constant."""
    e1, e2, e3 = frame(cam)
    us = np.linspace(-half, half, w); vs = np.linspace(half * h / w, -half * h / w, h); ds = np.linspace(-half, half, nd)
    U, V = np.meshgrid(us, vs)
    depth = np.full((h, w), np.inf)
    for k0 in range(0, nd, 8):
        dk = ds[k0:k0 + 8]
        P = [centre[i] + U[None] * e1[i] + V[None] * e2[i] + dk[:, None, None] * e3[i] for i in range(3)]
        if mode == 'm':
            n = mandel(G, P[0], P[1], P[2], steps)
        else:
            n = stay(G, P[0], P[1], P[2], c[0], c[1], c[2], steps)
        ins = n >= steps
        first = np.where(ins.any(0), dk[np.argmax(ins, 0)], np.inf)
        depth = np.minimum(depth, first)                      # slabs come front to back, so the first hit stays
    return depth, (us[1] - us[0])


def shade_solid(depth, px):
    hit = np.isfinite(depth); d = np.where(hit, depth, 0.0)
    for _ in range(2):                                        # soften the steps between blocks a little
        pad = np.pad(d, 1, mode='edge'); wgt = np.pad(hit.astype(float), 1)
        num = sum(np.where(wgt[i:i + d.shape[0], j:j + d.shape[1]] > 0, pad[i:i + d.shape[0], j:j + d.shape[1]], 0) for i in range(3) for j in range(3))
        den = sum(wgt[i:i + d.shape[0], j:j + d.shape[1]] for i in range(3) for j in range(3))
        d = np.where(hit, num / np.maximum(den, 1), 0.0)
    gy, gx = np.gradient(d, px)
    nrm = np.stack([gx, -gy, -np.ones_like(d)], -1); nrm /= np.linalg.norm(nrm, axis=-1, keepdims=True)
    light = np.array([-0.45, 0.6, -0.66]); light /= np.linalg.norm(light)
    lam = np.clip((nrm * light).sum(-1), 0, 1)
    near = np.clip((d.max() - d) / max(np.ptp(d[hit]) if hit.any() else 1, 1e-9), 0, 1)
    v = 0.18 + 0.72 * lam + 0.10 * near
    img = np.zeros(depth.shape + (3,), np.uint8); img[...] = (14, 17, 26)
    col = np.array([238, 226, 196.0])
    img[hit] = np.clip(v[hit, None] * col, 0, 255).astype(np.uint8)
    return img


def main():
    t0 = time.time()
    one, along, lathe = R.get('oneplane'), R.get('along'), R.get('lathe')
    idea, idea_along, plain_along, spun = follow(one), follow(along), fixed(along), fixed(lathe)

    # ---- numbers first: is the Mandelbrot solid of the idea the flat set spun round the x-axis?
    rng = np.random.default_rng(7); N = 60000 if QUICK else 400000
    c = rng.uniform([-2.1, -1.3, -1.3], [0.7, 1.3, 1.3], size=(N, 3)); st = 60
    a = mandel(idea, c[:, 0], c[:, 1], c[:, 2], st) >= st
    b = mandel(idea_along, c[:, 0], c[:, 1], c[:, 2], st) >= st
    s = mandel(spun, c[:, 0], c[:, 1], c[:, 2], st) >= st
    f = mandel(plain_along, c[:, 0], c[:, 1], c[:, 2], st) >= st
    # the flat Mandelbrot set itself, at the point (x, distance from the x-axis)
    zr, zi = np.zeros(N), np.zeros(N); cr, ci = c[:, 0], np.hypot(c[:, 1], c[:, 2]); alive = np.ones(N, bool)
    for _ in range(st):
        zr, zi = np.where(alive, zr * zr - zi * zi + cr, zr), np.where(alive, 2 * zr * zi + ci, zi); alive &= zr * zr + zi * zi < 36
    print('%d random points c in the box, %d steps' % (N, st))
    print('  inside: idea (one plane about the plane of c) %.3f%% | idea with along %.3f%% | lathe %.3f%% | flat set spun %.3f%% | along, fixed %.3f%%'
          % tuple(100 * t.mean() for t in (a, b, s, alive, f)))
    print('  points where the verdict differs from the flat set spun round the x-axis:')
    for nm, t in (('idea, one plane', a), ('idea, along', b), ('lathe', s), ('along, fixed', f)):
        print('    %-16s %d of %d' % (nm, int((t != alive).sum()), N))

    # ---- the sheet
    w, h = (215, 200) if QUICK else (430, 400); st2 = 30 if QUICK else 60
    sw, sh, nd, st3 = (240, 180, 96, 16) if QUICK else (520, 400, 320, 22)
    rows = [('YOUR IDEA: every point is squared about the plane that c creates', idea),
            ('"ALONG" AS IT IS NOW: every point is squared about a plane of its own', plain_along)]
    pad, top, lab = 12, 86, 30
    tiles_w = [w, w, h, sw]
    W = pad + sum(tw + pad for tw in tiles_w)
    row_h = lab + 26 + h + pad
    jw, jh = ((W - 5 * pad) // 4, int(((W - 5 * pad) // 4) * 0.72))
    H = top + 2 * row_h + lab + 26 + jh + 2 * pad + 8
    im = Image.new('RGB', (W, H), (12, 14, 20)); d = ImageDraw.Draw(im)
    d.text((pad, 10), 'What comes out if the plane is the one that c creates', fill=(240, 240, 245), font=T.font(28))
    d.text((pad, 48), 'Top two rows: the Mandelbrot solid, cut three ways and seen whole (rough blocks). Bottom row: Julia sets under your idea.', fill=(160, 170, 185), font=T.font(17))
    heads = ['cut along the flat plane', 'cut along a plane turned 22.5°', 'cut across the x-axis (x = −0.12)', 'the whole solid, rough']
    for i, (name, G) in enumerate(rows):
        y = top + i * row_h
        d.text((pad, y), name, fill=(235, 220, 170) if i == 0 else (205, 210, 220), font=T.font(21))
        pics = [T.shade(cut_axis(G, 0.0, w, h, st2), st2), T.shade(cut_axis(G, 22.5, w, h, st2), st2), T.shade(cut_across(G, -0.12, h, st2), st2)]
        dep, px = solid(G, 'm', None, (-0.7, 0.0, 0.0), 1.7, sw, sh, nd, st3)
        pics.append(shade_solid(dep, px))
        x = pad
        for hd, pic in zip(heads, pics):
            d.text((x, y + lab), hd, fill=(150, 160, 175), font=T.font(15))
            im.paste(Image.fromarray(pic), (x, y + lab + 22)); x += pic.shape[1] + pad
        print('row %d done, %.0f s' % (i, time.time() - t0)); sys.stdout.flush()
    # ---- Julia sets under the idea
    y = top + 2 * row_h
    d.text((pad, y), 'YOUR IDEA, Julia sets: the set is the one-plane set, turned to wherever the plane of c is', fill=(235, 220, 170), font=T.font(21))
    rab = (-0.122561, 0.744862)
    turn = lambda cc, deg: (cc[0], cc[1] * np.cos(np.radians(deg)), cc[1] * np.sin(np.radians(deg)))
    jul = [('rabbit, c in the flat plane', turn(rab, 0)), ('rabbit, c turned 60° round the x-axis: the same set, turned', turn(rab, 60)),
           ('basilica, c = −1 nudged a hair upward: buds point up and down', (-1.0, 1e-6, 0.0)),
           ('basilica, c = −1 nudged a hair toward you: buds point at you', (-1.0, 0.0, 1e-6))]
    x = pad
    for hd, cc in jul:
        dep, px = solid(idea, 'j', cc, (0.0, 0.0, 0.0), 1.75, jw, jh, nd, st3 + 6)
        d.text((x, y + lab), hd, fill=(150, 160, 175), font=T.font(15))
        im.paste(Image.fromarray(shade_solid(dep, px)), (x, y + lab + 22)); x += jw + pad
    out = os.path.join(HERE, 'plane-follows-c' + ('-quick' if QUICK else '') + '.png'); im.save(out)
    print(out, im.size, '%.0f s' % (time.time() - t0))


if __name__ == '__main__':
    main()

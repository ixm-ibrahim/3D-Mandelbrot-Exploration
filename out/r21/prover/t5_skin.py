"""Where on the skin of the main body CAN a bud grow?  (NOTES.md, part 4, statement D4)

    python out/r21/prover/t5_skin.py  ->  out/r21/prover/t5_skin.txt, t5_skin.png

For a fixed rule F the main body of the Mandelbrot solid is the set of c for which v -> F(v) + c has an attracting
resting point.  How the resting point loses its hold at the skin is read off the three 'multipliers' (the eigenvalues
of the 3 x 3 matrix of slopes of F at the resting point):
  * a PAIR of complex multipliers reaches size 1 first: the orbit near the skin goes ROUND the resting point by some
    angle alpha per step; where alpha is a fraction p/q of a full turn a period-q bud can root.  (This is what
    happens all along the edge of the flat main body.)  On a skin (a surface) alpha = p/q holds along LINES.
  * a single real multiplier reaches +1 or -1 first: no going round, so no row of buds: the skin there is bare
    (+1) or carries one period-2 lump (-1).
The picture colours the main body in a cut across the x-axis by which of the two it is, and by alpha.
"""
import os, sys, time
import numpy as np
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, 'out', 'r21', 'lib')); sys.path.insert(0, HERE)
import mem as M
sys.path.insert(0, os.path.join(ROOT, 'out', 'r16', 'bench'))
import rules as B

out = []


def say(t=''):
    print(t); sys.stdout.flush(); out.append(t)


def jac(F, v, h=1e-6):
    J = np.zeros((v.shape[0], 3, 3))
    for j in range(3):
        e = np.zeros(3); e[j] = h
        p = F(v[:, 0] + e[0], v[:, 1] + e[1], v[:, 2] + e[2]); m = F(v[:, 0] - e[0], v[:, 1] - e[1], v[:, 2] - e[2])
        for i in range(3):
            J[:, i, j] = (p[i] - m[i]) / (2 * h)
    return J


def classify(F, c, iters=2500):
    """For each c (n, 3): does the orbit of 0 settle on a resting point? If so its multipliers.
    Returns kind (0 left, 1 stays but no resting point, 2 complex pair leads, 3 real positive leads, 4 real negative leads), size, alpha."""
    n = c.shape[0]; v = c.copy(); alive = np.ones(n, bool)
    for _ in range(iters):
        X, Y, Z = F(v[alive, 0], v[alive, 1], v[alive, 2]); w = np.stack([X, Y, Z], 1) + c[alive]
        ok = (w * w).sum(1) < 36.0; idx = np.flatnonzero(alive); v[idx[ok]] = w[ok]; alive[idx[~ok]] = False
    kind = np.zeros(n, int); size = np.zeros(n); alpha = np.zeros(n)
    idx = np.flatnonzero(alive)
    if idx.size == 0:
        return kind, size, alpha
    vv = v[idx]; cc = c[idx]
    X, Y, Z = F(vv[:, 0], vv[:, 1], vv[:, 2]); w = np.stack([X, Y, Z], 1) + cc
    near = np.abs(w - vv).max(1) < 2e-2                       # still creeping toward a resting point near the skin: polish by Newton
    for _ in range(6):
        J = jac(F, vv); X, Y, Z = F(vv[:, 0], vv[:, 1], vv[:, 2]); g = np.stack([X, Y, Z], 1) + cc - vv
        A = J - np.eye(3)[None]
        try:
            step = np.linalg.solve(A, g[:, :, None])[:, :, 0]
        except np.linalg.LinAlgError:
            step = np.zeros_like(g)
        step = np.where(near[:, None] & np.isfinite(step).all(1)[:, None], np.clip(step, -0.05, 0.05), 0.0); vv = vv - step
    X, Y, Z = F(vv[:, 0], vv[:, 1], vv[:, 2]); res = np.abs(np.stack([X, Y, Z], 1) + cc - vv).max(1)
    rest = near & (res < 1e-9)
    ev = np.linalg.eigvals(jac(F, vv)); mod = np.abs(ev); lead = np.argmax(mod, 1); lam = ev[np.arange(len(vv)), lead]
    cplx = np.abs(lam.imag) > 1e-5 * np.maximum(1.0, np.abs(lam))
    k = np.where(~rest, 1, np.where(cplx, 2, np.where(lam.real >= 0, 3, 4)))
    k = np.where(rest & (mod.max(1) >= 1.0), 1, k)                                  # Newton found a resting point that does not hold: not the main body
    kind[idx] = k; size[idx] = mod.max(1); alpha[idx] = np.abs(np.angle(lam))
    return kind, size, alpha


def paint(kind, size, alpha):
    img = np.zeros(kind.shape + (3,), np.uint8); img[...] = (16, 20, 30)
    img[kind == 1] = (95, 95, 100)
    t = np.clip(alpha / np.pi, 0, 1)
    stripes = 0.75 + 0.25 * np.cos(2 * np.pi * t * 24)                              # level lines of alpha (24 stripes per half turn)
    cp = np.stack([40 + 60 * t, 120 + 110 * (1 - np.abs(2 * t - 1)), 235 - 120 * t], -1) * stripes[..., None]
    img[kind == 2] = np.clip(cp, 0, 255).astype(np.uint8)[kind == 2]
    img[kind == 3] = (235, 150, 60); img[kind == 4] = (200, 80, 190)
    edge = (kind >= 2) & (size > 0.97)
    img[edge] = (0.6 * img[edge] + 0.4 * 255).astype(np.uint8)
    return img


def main():
    t0 = time.time(); N = 250; L = 1.0
    rules = [('lathe', B.lathe, 'The lathe (flat set spun)'), ('oneplane', B.get('oneplane'), 'The one-plane rule'), ('along', B.get('along'), 'Turning plane, along')]
    cuts = [('across the x-axis at x = -0.12', lambda p, q: (np.full_like(p, -0.12), p, q)), ('across the x-axis at x = -0.45', lambda p, q: (np.full_like(p, -0.45), p, q)),
            ('along the sheet turned 45 degrees', lambda p, q: (p * 1.4 - 0.55, q * np.cos(np.pi / 4), q * np.sin(np.pi / 4)))]
    p, q = np.meshgrid(np.linspace(-L, L, N), np.linspace(L, -L, N))
    pad = 8; im = Image.new('RGB', (pad + len(cuts) * (N + pad), 64 + len(rules) * (N + 30)), (12, 14, 20)); d = ImageDraw.Draw(im)
    d.text((pad, 6), 'How the resting point of the main body loses its hold at the skin', fill=(240, 240, 245), font=M.font(16))
    d.text((pad, 28), 'blue-green, striped: a complex pair leads (going round: buds can root along the stripes) | orange: a real multiplier +, bare skin | pink: real -, one period-2 lump | grey: in the solid, no resting point', fill=(170, 175, 190), font=M.font(11))
    say('Share of the skin layer (largest multiplier between 0.9 and 1) of the main body where a complex pair leads / a real + / a real - multiplier leads')
    for i, (nm, F, label) in enumerate(rules):
        for j, (cn, cut) in enumerate(cuts):
            cx, cy, cz = cut(p, q); c = np.stack([cx.ravel(), cy.ravel(), cz.ravel()], 1)
            kind, size, alpha = classify(F, c); kind, size, alpha = kind.reshape(p.shape), size.reshape(p.shape), alpha.reshape(p.shape)
            skin = (kind >= 2) & (size > 0.9)
            tot = max(int(skin.sum()), 1)
            say('   %-9s %-34s skin points %5d: complex pair %5.1f%%, real + %5.1f%%, real - %5.1f%% | main body %6d points, other bounded %6d'
                % (nm, cn, skin.sum(), 100 * (skin & (kind == 2)).sum() / tot, 100 * (skin & (kind == 3)).sum() / tot, 100 * (skin & (kind == 4)).sum() / tot, (kind >= 2).sum(), (kind == 1).sum()))
            x = pad + j * (N + pad); y = 64 + i * (N + 30)
            d.text((x, y), '%s, %s' % (nm, cn), fill=(235, 220, 170), font=M.font(12)); im.paste(Image.fromarray(paint(kind, size, alpha)), (x, y + 20))
        say('   (%.0f s)' % (time.time() - t0))
    im.save(os.path.join(HERE, 't5_skin.png'))
    open(os.path.join(HERE, 't5_skin.txt'), 'w', encoding='utf-8').write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()

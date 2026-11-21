"""Round 27, explorer "pinch": pictures built from chains of sphere inversions fitted to z^2 + c.

Everything here is a UNION OF BODIES. A body is either
    a ball      ('ball', centre (3,), radius)                         or
    a spindle   ('spin', P (3,), Q (3,), a (3,), cos_theta)           a body pointed at both ends (tips P and Q).
A spindle is what one sphere inversion makes of a round cone: with  u(X) = (X - Q)/|X - Q|^2 - (P - Q)/|P - Q|^2
(P -> 0, Q -> infinity) it is the set  { X : u(X) . a >= cos_theta |u(X)| }.  theta = 90 degrees is a ball.

Flat moves are 2 x 2 complex matrices (w -> (a w + b)/(c w + d)); each is a chain of circle inversions, and its
only extension to space that keeps the flat plane (up to the mirror in that plane) carries a ball / spindle that
is centred on the flat plane to another one. So bodies made by flat moves are stored by their flat landmarks.

    import pinchlib as PL
"""
import os, sys, time
import numpy as np
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, 'out', 'r21', 'lib'))
import mem as M

BOX = (-1.8, 1.8, -1.3, 1.3)
CS = {'c1': complex(-1.0, 0.0), 'rabbit': complex(M.RABBIT[0], M.RABBIT[1])}
NAMES = {'c1': 'c = -1', 'rabbit': 'the rabbit'}
EYES = {'a': (0.45, 0.5, 1.0), 'top': (0.2, 1.0, 0.35)}


# ------------------------------------------------------------------------------------------- the flat rule
def fixed_points(c):
    r = np.sqrt(1 - 4 * c + 0j)
    return (1 - r) / 2, (1 + r) / 2                     # alpha (the meeting point), beta (the far end)


def f_jet(z, c, n):
    """f^n(z), its first and its second derivative."""
    d1, d2 = 1.0 + 0j, 0.0 + 0j
    for _ in range(n):
        d2 = 2 * d1 * d1 + 2 * z * d2; d1 = 2 * z * d1; z = z * z + c
    return z, d1, d2


def undo(sign, w, c, like=None):
    """One undo-move (a square root). like = a point whose root fixes the branch (so that a whole body moves together)."""
    r = np.sqrt(w - c + 0j)
    if like is not None:
        rl = np.sqrt(like - c + 0j); r = np.where((r * np.conj(rl)).real < 0, -r, r)
    return sign * r


def periodic(c, n):
    """The points with f^n(p) = p: (p, multiplier, second derivative, word of signs)."""
    pol = np.poly1d([1.0, 0.0])
    for _ in range(n):
        pol = pol * pol + c
    out = []
    for p in (pol - np.poly1d([1.0, 0.0])).roots:
        for _ in range(40):                                               # polish
            v, d1, _d2 = f_jet(p, c, n); p = p - (v - p) / (d1 - 1)
        v, d1, d2 = f_jet(p, c, n)
        word = []; q = p
        for _ in range(n):
            word.append(1 if q.real > 0 else -1); q = q * q + c
        out.append((p, d1, d2, tuple(word)))
    return out


def undo_word(word, w, c):
    """The n-step undo-move that belongs to the periodic point with this word of signs, applied to the point w."""
    for s in reversed(word):
        w = s * np.sqrt(w - c + 0j)
    return w


# ------------------------------------------------------------------------------------------- flat moves
def from_fixed(p, mu, kappa):
    """w -> p + mu (w - p) / (1 - kappa (w - p)): fixed point p, stretch-and-turn mu there, bend kappa."""
    return np.array([[mu - p * kappa, p + p * p * kappa - mu * p], [-kappa, 1 + kappa * p]], complex)


def ap(Mx, w):
    return (Mx[0, 0] * w + Mx[0, 1]) / (Mx[1, 0] * w + Mx[1, 1])


def other_fixed(Mx, p):
    a, b, c, d = Mx.ravel()
    if abs(c) < 1e-14:
        return np.inf
    return (a - d) / c - p                                                # the two fixed points add up to (a - d)/c


def fitted(c, n, kind):
    """The sphere-inversion moves fitted to the n-step undo-moves of z^2 + c, one per point that such an undo-move
    keeps in place and pulls toward (a point the forward rule pushes away from).
        'affine'  same fixed point, same stretch and turn; the other fixed point is infinity (a stretch about a point)
        'osc'     same fixed point, same stretch and turn, same bend (nothing left to choose)
        'pin'     same fixed point, same stretch and turn, and it sends the other fixed point of z^2 + c where the
                  true undo-move sends it (so that bodies meet where the true ones meet)
    Returns (moves, skipped): skipped = points where the undo-move has no finite stretch (centres of bodies)."""
    al, be = fixed_points(c); moves, skipped = [], []
    for p, lam, d2, word in periodic(c, n):
        if abs(lam) <= 1.0:
            skipped.append((p, lam, word)); continue
        mu = 1 / lam
        if kind == 'affine':
            kap = 0.0
        elif kind == 'osc':
            kap = -d2 / (2 * lam * lam)
        else:
            a = al if abs(p - al) > abs(p - be) else be
            if abs(p - al) < 1e-9: a = be
            if abs(p - be) < 1e-9: a = al
            b = undo_word(word, a, c)
            kap = (1 - mu * (a - p) / (b - p)) / (a - p)
        moves.append(dict(M=from_fixed(p, mu, kap), p=p, mu=mu, word=word, n=n))
    return moves, skipped


def disc_image(Mx, z0, r):
    """Image discs of the discs (z0, r) (arrays). Returns centre, radius, ok (False where the disc holds the move's pole)."""
    a, b, c, d = Mx.ravel()
    if abs(c) < 1e-14:
        return (a * z0 + b) / d, np.abs(a / d) * r, np.ones(np.shape(z0), bool)
    pole = -d / c; dz = pole - z0; ok = np.abs(dz) > r * (1 + 1e-9)
    dz = np.where(np.abs(dz) > 0, dz, 1e-300)
    q = z0 + r * r / np.conj(dz)                                          # the pole mirrored in the circle goes to the centre
    cen = ap(Mx, q); rad = np.abs(ap(Mx, z0 + r) - cen)
    return cen, rad, ok


# ------------------------------------------------------------------------------------------- bodies
def ball(zc, r, z=0.0):
    return ('ball', np.array([np.real(zc), np.imag(zc), z], float), float(r))


def to3(w):
    return np.array([np.real(w), np.imag(w), 0.0], float)


def u_of(X, P, Q):
    """The sphere inversion that sends P to 0 and Q to infinity. X has shape (..., 3)."""
    d = X - Q; n = (d * d).sum(-1, keepdims=True); n = np.where(n > 0, n, 1e-300)
    e = P - Q
    return d / n - e / (e * e).sum()


def spindle(P, Q, C, theta):
    """Tips P, Q (3,), a point C on its middle line, half opening theta (radians) at each tip."""
    a = u_of(C[None], P, Q)[0]; a = a / np.linalg.norm(a)
    return ('spin', np.asarray(P, float), np.asarray(Q, float), a, float(np.cos(theta)))


def bound(body):
    """A ball that holds the body (centre, radius); radius inf if the body is not bounded."""
    if body[0] == 'ball':
        return body[1], body[2]
    _, P, Q, a, ct = body
    e = (P - Q) / np.linalg.norm(P - Q); L = np.linalg.norm(P - Q)
    eta = np.arccos(np.clip(a @ e, -1, 1)) + np.arccos(np.clip(ct, -1, 1))
    if eta > np.pi - 0.02:
        return (P + Q) / 2, np.inf
    return (P + Q) / 2, 0.5 * L * max(1.0, np.tan(eta / 2)) * 1.02


def inside(body, X):
    if body[0] == 'ball':
        d = X - body[1]; return (d * d).sum(-1) <= body[2] ** 2
    _, P, Q, a, ct = body
    u = u_of(X, P, Q)
    return (u * a).sum(-1) >= ct * np.sqrt((u * u).sum(-1))


def flat_union(bodies, w=720, h=520, box=BOX):
    """The flat cut (z = 0) of a union of bodies, on the grid of the comparisons."""
    xs = np.linspace(box[0], box[1], w); ys = np.linspace(box[3], box[2], h); out = np.zeros((h, w), bool)
    dx = xs[1] - xs[0]
    for b in bodies:
        cen, rad = bound(b)
        if not np.isfinite(rad):
            continue
        i0 = max(int(np.floor((cen[0] - rad - box[0]) / dx)), 0); i1 = min(int(np.ceil((cen[0] + rad - box[0]) / dx)) + 1, w)
        j0 = max(int(np.floor((box[3] - cen[1] - rad) / dx)), 0); j1 = min(int(np.ceil((box[3] - cen[1] + rad) / dx)) + 1, h)
        if i1 <= i0 or j1 <= j0:
            continue
        gx, gy = np.meshgrid(xs[i0:i1], ys[j0:j1])
        out[j0:j1, i0:i1] |= inside(b, np.stack([gx, gy, np.zeros_like(gx)], -1))
    return out


def true_flat(c, w=720, h=520, box=BOX, steps=300):
    u, s = np.meshgrid(np.linspace(box[0], box[1], w), np.linspace(box[3], box[2], h))
    return M.flat_stay(u, s, c.real, c.imag, steps) >= steps


def wrong_share(A, T):
    """Share of the true area that gets the wrong verdict (the number round 25 used: 38.6% for the balls object)."""
    return float((A != T).sum()) / float(T.sum())


def overlay(A, T):
    """True only: blue. Object only: orange. Both: cream. Neither: dark."""
    img = np.zeros(A.shape + (3,), np.uint8); img[...] = (14, 17, 26)
    img[T & ~A] = (70, 120, 220); img[A & ~T] = (235, 140, 40); img[A & T] = (238, 228, 200)
    return img


def solid(bodies, w, h, nd, cam, centre=(0.0, 0.0, 0.0), half_w=1.75, refine=8):
    """The library's rough solid (first block on each line of sight that is inside), for a union of bodies.
    refine > 0: the place of the skin between the last outside block and the first inside one is then found by halving."""
    e1, e2, e3 = M.frame(cam); centre = np.asarray(centre, float)
    us = np.linspace(-half_w, half_w, w); vs = np.linspace(half_w * h / w, -half_w * h / w, h); ds = np.linspace(-half_w, half_w, nd)
    du, dv, dd = us[1] - us[0], vs[0] - vs[1], ds[1] - ds[0]
    depth = np.full((h, w), np.inf)
    for b in bodies:
        cen, rad = bound(b)
        if not np.isfinite(rad):
            continue
        rel = cen - centre; uc, vc, dc = rel @ e1, rel @ e2, rel @ e3
        i0 = max(int(np.floor((uc - rad - us[0]) / du)), 0); i1 = min(int(np.ceil((uc + rad - us[0]) / du)) + 1, w)
        j0 = max(int(np.floor((vs[0] - vc - rad) / dv)), 0); j1 = min(int(np.ceil((vs[0] - vc + rad) / dv)) + 1, h)
        k0 = max(int(np.floor((dc - rad - ds[0]) / dd)), 0); k1 = min(int(np.ceil((dc + rad - ds[0]) / dd)) + 1, nd)
        if i1 <= i0 or j1 <= j0 or k1 <= k0:
            continue
        U, V = np.meshgrid(us[i0:i1], vs[j0:j1]); best = np.full(U.shape, np.inf)
        base = centre + U[..., None] * e1 + V[..., None] * e2
        for ka in range(k0, k1, 12):
            dk = ds[ka:min(ka + 12, k1)]
            X = base[None] + dk[:, None, None, None] * e3
            ins = inside(b, X)
            best = np.minimum(best, np.where(ins.any(0), dk[np.argmax(ins, 0)], np.inf))
        hit = np.isfinite(best)
        if refine and hit.any():                                          # the skin between two blocks, by halving: no ripple marks
            bh = base[hit]; hi = best[hit]; lo = hi - dd
            for _ in range(refine):
                mid = 0.5 * (lo + hi); ins = inside(b, bh + mid[:, None] * e3)
                hi = np.where(ins, mid, hi); lo = np.where(ins, lo, mid)
            best[hit] = hi
        depth[j0:j1, i0:i1] = np.minimum(depth[j0:j1, i0:i1], best)
    return depth, du


def label(im, text, xy=(6, 4), size=14, fill=(200, 205, 215)):
    ImageDraw.Draw(im).text(xy, text, fill=fill, font=M.font(size))


def sheet(tiles, cols, path, title=None, pad=8, cap_h=22, title_h=34):
    """tiles = [(numpy image, caption)], laid out in rows of cols."""
    th, tw = tiles[0][0].shape[:2]; rows = (len(tiles) + cols - 1) // cols
    W = pad + cols * (tw + pad); H = (title_h if title else pad) + rows * (th + cap_h + pad)
    im = Image.new('RGB', (W, H), (12, 14, 20)); d = ImageDraw.Draw(im)
    if title:
        d.text((pad, 8), title, fill=(240, 240, 245), font=M.font(18))
    for k, (pic, cap) in enumerate(tiles):
        x = pad + (k % cols) * (tw + pad); y = (title_h if title else pad) + (k // cols) * (th + cap_h + pad)
        d.text((x + 2, y), cap, fill=(235, 220, 170), font=M.font(14)); im.paste(Image.fromarray(pic), (x, y + cap_h))
    im.save(path); return path

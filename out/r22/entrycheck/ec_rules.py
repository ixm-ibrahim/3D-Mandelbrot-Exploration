"""Round 22, entrycheck: the two rules written out afresh from docs/ROUND22.md section 4 (NOT from the lab's code and
NOT from the library), in numpy, so that the lab, the library and the briefing can be compared three ways.

    stay(rule, x, y, z, cx, cy, cz, steps, r2)  -> how many steps each orbit stays with |v|^2 < r2
    rule: 'alongonce' | ('pulledplane', s0, ease, kc) | 'oneplane' | 'along'
A Mandelbrot orbit is started at c (the squaring of the origin counts for nothing): stay(rule, c, c, steps).
"""
import numpy as np


def oneplane(x, y, z):
    r2 = x * x + y * y + z * z
    den = r2 + z * z
    f = np.where(den > 0, r2 / np.where(den > 0, den, 1.0), 0.0)
    return f * (x * x - y * y), f * 2 * x * y, f * 2 * np.sqrt(r2) * z


def about(x, y, z, ang):
    """Rot_x(ang) P(Rot_x(-ang) v)"""
    c, s = np.cos(ang), np.sin(ang)
    X, Y, Z = oneplane(x, c * y + s * z, c * z - s * y)
    return X, c * Y - s * Z, s * Y + c * Z


def along(x, y, z):
    phi = np.arctan2(z, y)
    return about(x, y, z, phi - np.sin(4 * phi) / 4)


def pull(w1, w2, y, z, k, e):
    pw = np.arctan2(w2, w1)
    t = np.arctan2(2 * y * z, y * y - z * z) - pw
    t = t - 2 * np.pi * np.floor(t / (2 * np.pi) + 0.5)
    a = pw + t - e * np.sin(t)
    m = k * (y * y + z * z)
    return w1 + m * np.cos(a), w2 + m * np.sin(a)


def stay(rule, x, y, z, cx, cy, cz, steps, r2=36.0):
    sh = np.broadcast(x, y, z, cx, cy, cz).shape
    x, y, z, cx, cy, cz = (np.array(np.broadcast_to(np.asarray(t, float), sh)).ravel() for t in (x, y, z, cx, cy, cz))
    n = np.zeros(x.size, np.int32); alive = np.ones(x.size, bool)
    if isinstance(rule, tuple):
        _, s0, ease, kc = rule
        w1 = np.full(x.size, float(s0)); w2 = np.zeros(x.size)
    with np.errstate(all='ignore'):
        for k in range(steps):
            if rule == 'alongonce':
                X, Y, Z = along(x, y, z) if k == 0 else oneplane(x, y, z)
            elif rule == 'oneplane':
                X, Y, Z = oneplane(x, y, z)
            elif rule == 'along':
                X, Y, Z = along(x, y, z)
            else:
                w1, w2 = pull(w1, w2, cy, cz, kc, ease)
                w1, w2 = pull(w1, w2, y, z, 1.0, ease)
                X, Y, Z = about(x, y, z, 0.5 * np.arctan2(w2, w1))
            x, y, z = X + cx, Y + cy, Z + cz
            ok = (x * x + y * y + z * z) < r2
            alive &= ok
            n += alive
            x, y, z = np.where(alive, x, 0.0), np.where(alive, y, 0.0), np.where(alive, z, 0.0)
            if not alive.any():
                break
    return n.reshape(sh)


def flat_stay(zr, zi, cr, ci, steps, r2=36.0):
    zr, zi = np.array(zr, float), np.array(zi, float)
    cr, ci = np.broadcast_to(np.asarray(cr, float), zr.shape), np.broadcast_to(np.asarray(ci, float), zr.shape)
    n = np.zeros(zr.shape, np.int32); alive = np.ones(zr.shape, bool)
    with np.errstate(all='ignore'):
        for _ in range(steps):
            zr, zi = zr * zr - zi * zi + cr, 2 * zr * zi + ci
            alive &= zr * zr + zi * zi < r2; n += alive
            zr, zi = np.where(alive, zr, 0.0), np.where(alive, zi, 0.0)
    return n

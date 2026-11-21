"""Round 21, agent 'frame': the orbit carries a whole FRAME (three unit vectors at right angles).

    e1 = where the page's real axis points, e2 = the page's 'up', e3 = out of the page.  Start: x, y, z.

Each point is squared by the one-plane rule P IN the carried frame:
    a, b, w = v.e1, v.e2, v.e3 ;  (A, B, W) = P(a, b, w) ;  F(v) = A e1 + B e2 + W e3
and the frame is then (or first) moved by what the orbit does.  The carried state is nine arrays
(e1x, e1y, e1z, e2x, e2y, e2z, e3x, e3y, e3z), plus three more for the rules that remember the last direction of travel.

Words used below
    turn vector   a rotation written as (axis) * (angle in radians), turned by Rodrigues' formula
    shortest turn from a to b: axis a x b, angle = the angle between a and b
    TILT part of a turn vector om, for the frame E: om - (om.e3) e3. It is the part whose axis lies IN the frame's
                  own page (it tips the page over); what is thrown away is the turn of the frame inside its own page.
    px / tr       after the page has tipped, the real axis e1 is either TRansported with the frame (tr) or set anew to
                  the shadow of the x-axis on the page (px)

RULES = the rules that are exact on the flat page.  FAILS = rules that break the flat page (kept to show it).
"""
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), 'lib'))
import mem as M
P = M.S.oneplane
TINY = 1e-150


# ------------------------------------------------------------------ vectors as 3-tuples of arrays
def dot(a, b): return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]
def cross(a, b): return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])
def add(a, b, s=1.0): return (a[0] + s * b[0], a[1] + s * b[1], a[2] + s * b[2])
def mul(a, s): return (a[0] * s, a[1] * s, a[2] * s)


def unit(a, fb=None):
    """a / |a|; where a is zero the fallback fb (default: the zero vector)."""
    n = np.sqrt(dot(a, a)); ok = n > TINY; m = np.where(ok, n, 1.0)
    if fb is None:
        return tuple(np.where(ok, t / m, 0.0) for t in a)
    return tuple(np.where(ok, t / m, f) for t, f in zip(a, fb))


def rot(v, om):
    """Turn the vector v by the turn vector om (Rodrigues)."""
    t2 = dot(om, om); t = np.sqrt(t2); big = t > 1e-6; ts = np.where(big, t, 1.0)
    c = np.cos(t); s1 = np.where(big, np.sin(t) / ts, 1.0 - t2 / 6.0); c1 = np.where(big, (1.0 - c) / (ts * ts), 0.5 - t2 / 24.0)
    k = cross(om, v); d = dot(om, v)
    return tuple(v[i] * c + k[i] * s1 + om[i] * d * c1 for i in range(3))


def ortho(E):
    """Make the frame orthonormal again (e3 first, then e1, then e2 = e3 x e1)."""
    e3 = unit(E[2]); e1 = unit(add(E[0], e3, -dot(E[0], e3))); return (e1, cross(e3, e1), e3)


def turn_frame(E, om): return ortho((rot(E[0], om), rot(E[1], om), rot(E[2], om)))
def unpack(st): return (tuple(st[0:3]), tuple(st[3:6]), tuple(st[6:9]))
def pack(E, *more): return E[0] + E[1] + E[2] + tuple(t for m in more for t in m)


def init_frame(extra=0):
    def f(n):
        o, z = np.ones(n), np.zeros(n)
        return (o, z, z, z, o, z, z, z, o) + tuple(np.zeros(n) for _ in range(extra))
    return f


def sq_in(v, E):
    """The one-plane square of v taken IN the frame E."""
    A, B, W = P(dot(v, E[0]), dot(v, E[1]), dot(v, E[2]))
    return tuple(A * E[0][i] + B * E[1][i] + W * E[2][i] for i in range(3))


def short_turn(a, b):
    """Turn vector of the shortest turn from direction a to direction b (zero where it is not defined)."""
    a, b = unit(a), unit(b); w = cross(a, b); s = np.sqrt(dot(w, w)); ang = np.arctan2(s, dot(a, b))
    ok = s > 1e-14; k = np.where(ok, ang / np.where(ok, s, 1.0), 0.0)
    return mul(w, k)


def tilt_part(om, E): return add(om, E[2], -dot(om, E[2]))


def shadow_e1(E, e3):
    """px: the frame with out-of-page vector e3 whose real axis is the shadow of the x-axis on the page
    (the old e1's shadow where the x-axis stands straight out of the page)."""
    old = add(E[0], e3, -dot(E[0], e3))
    e1 = unit((1.0 - e3[0] * e3[0], -e3[0] * e3[1], -e3[0] * e3[2]), unit(old, E[0]))
    return ortho((e1, cross(e3, e1), e3))


def tip_to_line(E, w, mu, mode):
    """Tip the page so that its out-of-page line e3 moves toward the line of w (w need not be a unit vector; its length
    is its weight).  The new e3 is the main axis of  e3 e3^T + mu w w^T  (a line has no sign: two lines are averaged as
    lines).  mu = inf: e3 goes all the way to the line of w.  The tip is the smallest one (at most 90 degrees)."""
    e3 = E[2]; p = dot(w, e3); wp = add(w, e3, -p); q = np.sqrt(dot(wp, wp)); m = unit(wp)
    tau = 0.5 * (np.arctan2(2 * p * q, p * p - q * q) if np.isinf(mu) else np.arctan2(2 * mu * p * q, 1.0 + mu * (p * p - q * q)))
    if mode == 'tr':
        return turn_frame(E, mul(cross(e3, m), tau))
    n3 = unit(add(mul(e3, np.cos(tau)), m, np.sin(tau)), e3)
    return shadow_e1(E, n3)


# ------------------------------------------------------------------ the rules
def r_fixed(x, y, z, st, k, cx, cy, cz):
    """The frame never moves: this must be the one-plane rule (a test of the frame code)."""
    return (*sq_in((x, y, z), unpack(st)), st)


def turn(share, full=False, to='image', smooth=False):
    """Square in the frame; then the frame is turned by `share` of the shortest turn that carries the direction of the
    point to the direction of (to = 'image') the new orbit point F(v) + c, or (to = 'square') of F(v) without c.
    full = False: only the tilt part of that turn is used.  smooth = True: the turn vector is v^ x v'^ (its size is the
    SINE of the angle, so it dies out where the point is thrown straight through the origin) instead of axis * angle."""
    def f(x, y, z, st, k, cx, cy, cz):
        E = unpack(st); v = (x, y, z); F = sq_in(v, E); n = (F[0] + cx, F[1] + cy, F[2] + cz) if to == 'image' else F
        om = cross(unit(v), unit(n)) if smooth else short_turn(v, n)
        if not full:
            om = tilt_part(om, E)
        return (*F, pack(turn_frame(E, mul(om, share))))
    return f


def e1_to_point(x, y, z, st, k, cx, cy, cz):
    """BREAKS THE FLAT PAGE (kept to show it). Before squaring, the frame is turned inside its own page (about e3)
    until its real axis e1 points at the shadow of the point on the page."""
    E = unpack(st); v = (x, y, z); a, b = dot(v, E[0]), dot(v, E[1]); rho = np.hypot(a, b); ok = rho > TINY; m = np.where(ok, rho, 1.0)
    co, si = np.where(ok, a / m, 1.0), np.where(ok, b / m, 0.0)
    e1 = add(mul(E[0], co), E[1], si); e2 = add(mul(E[1], co), E[0], -si); E = ortho((e1, e2, E[2]))
    return (*sq_in(v, E), pack(E))


def transport(share=1.0, full=False):
    """Square in the frame; then the frame is carried along the PATH of the orbit so that it stays 'parallel': it is
    turned by the shortest turn from the last direction of travel t' = (v_k - v_(k-1))^ to the new one t = (v_(k+1) - v_k)^
    (no spin about the direction of travel).  full = False: only the tilt part.  Carries t as three more arrays."""
    def f(x, y, z, st, k, cx, cy, cz):
        E = unpack(st); tp = tuple(st[9:12]); v = (x, y, z); F = sq_in(v, E)
        t = unit((F[0] + cx - x, F[1] + cy - y, F[2] + cz - z))
        om = short_turn(tp, t)                      # zero at the first step (tp = 0)
        if not full:
            om = tilt_part(om, E)
        return (*F, pack(turn_frame(E, mul(om, share)), t))
    return f


def orbplane(mu, mode):
    """Square in the frame; then the page tips toward THE PLANE THE ORBIT HAS JUST MADE: the plane through the origin,
    the point v and the new point v' = F(v) + c.  Its out-of-page line is w = v^ x v'^ (length = sine of the angle of the
    step).  See tip_to_line for mu and mode.  mu = inf: the next point is squared exactly inside the plane of the last
    two orbit points."""
    def f(x, y, z, st, k, cx, cy, cz):
        E = unpack(st); v = (x, y, z); F = sq_in(v, E); n = (F[0] + cx, F[1] + cy, F[2] + cz)
        return (*F, pack(tip_to_line(E, cross(unit(v), unit(n)), mu, mode)))
    return f


def osc(mu, mode):
    """Square in the frame; then the page tips toward the plane in which the PATH of the orbit has just bent: the plane
    of the last two directions of travel t', t (it does not pass through the origin; the page is set parallel to it).
    Its out-of-page line is w = t' x t.  Carries t as three more arrays."""
    def f(x, y, z, st, k, cx, cy, cz):
        E = unpack(st); tp = tuple(st[9:12]); v = (x, y, z); F = sq_in(v, E)
        t = unit((F[0] + cx - x, F[1] + cy - y, F[2] + cz - z))
        return (*F, pack(tip_to_line(E, cross(tp, t), mu, mode), t))
    return f


def topoint(lam, mode, soft=False):
    """BEFORE squaring, the page tips toward the point by the SHORTEST tip: about the line in the page that is square to
    the point's shadow on the page, by lam times the point's height angle L above the page (lam = 1: the page then holds
    the point).  soft = True: by lam * sin(2L) / 2 instead (dies out for points straight above the page, where the
    shortest tip has no direction).  Then the point is squared in the tipped frame."""
    def f(x, y, z, st, k, cx, cy, cz):
        E = unpack(st); v = (x, y, z); a, b, w = dot(v, E[0]), dot(v, E[1]), dot(v, E[2]); rho = np.hypot(a, b)
        ok = rho > TINY; m = np.where(ok, rho, 1.0)
        ph = tuple(np.where(ok, (a * E[0][i] + b * E[1][i]) / m, 0.0) for i in range(3))      # the shadow's direction
        L = np.arctan2(w, rho); ang = lam * (0.5 * np.sin(2 * L) if soft else L)
        om = mul(cross(ph, E[2]), ang)
        if mode == 'tr':
            E = turn_frame(E, om)
        else:
            E = shadow_e1(E, unit(rot(E[2], om), E[2]))
        return (*sq_in(v, E), pack(E))
    return f


def tip_e3_to(E, n3, share, mode):
    """Tip the frame by `share` of the shortest turn that carries its out-of-page vector e3 to the unit vector n3."""
    om = mul(short_turn(E[2], n3), share)
    if mode == 'tr':
        return turn_frame(E, om)
    return shadow_e1(E, unit(rot(E[2], om), E[2]))


def keep_height(share, mode):
    """Square in the frame; then the frame is carried by the TURNING PART OF THE SQUARING ITSELF, tilt part only.
    On each ball round the origin the one-plane square sends the compass (east, north) at the point to the compass
    (east, north) at its square; so the turning part Q of the squaring carries (v^, east, north) at v to the same three
    at F(v).  The frame's out-of-page vector is carried along:  e3 -> Q e3 = sin(L) F^ + cos(L) north(F^),  L = height
    angle of v above the page; and the frame is tipped by the shortest turn that takes e3 there (the turn of Q inside
    the page is thrown away).  In words: the page tips, about the line square to the shadow of the square, by exactly
    as much as the squaring has pushed the point toward the pole, so that the square stands as high above the new page
    as the point stood above the old one."""
    def f(x, y, z, st, k, cx, cy, cz):
        E = unpack(st); v = (x, y, z); a, b, w = dot(v, E[0]), dot(v, E[1]), dot(v, E[2])
        A, B, W = P(a, b, w); F = tuple(A * E[0][i] + B * E[1][i] + W * E[2][i] for i in range(3))
        r = np.sqrt(a * a + b * b + w * w); ok = (np.hypot(a, b) > TINY) & (np.hypot(A, B) > TINY); rs = np.where(ok, r, 1.0)
        sL, cL = w / rs, np.hypot(a, b) / rs; R2 = rs * rs; rho2 = np.where(ok, np.hypot(A, B), 1.0)
        sL2, cL2, c2, s2 = W / R2, rho2 / R2, A / rho2, B / rho2
        q = (sL * A / R2 - cL * sL2 * c2, sL * B / R2 - cL * sL2 * s2, sL * sL2 + cL * cL2)       # Q e3 in frame coordinates
        n3 = tuple(np.where(ok, q[0] * E[0][i] + q[1] * E[1][i] + q[2] * E[2][i], E[2][i]) for i in range(3))
        return (*F, pack(tip_e3_to(E, unit(n3, E[2]), share, mode)))
    return f


def orbsq(mu, mode):
    """As orbplane, but the plane is the one through the origin, the point and its SQUARE (c not counted)."""
    def f(x, y, z, st, k, cx, cy, cz):
        E = unpack(st); v = (x, y, z); F = sq_in(v, E)
        return (*F, pack(tip_to_line(E, cross(unit(v), unit(F)), mu, mode)))
    return f


def pole_to_point(mu):
    """BEFORE squaring, the out-of-page LINE of the frame moves toward the line of the point (the opposite of the page
    following): e3 = main axis of e3 e3^T + mu v^ v^^T (mu < 1: a point in the page moves nothing)."""
    def f(x, y, z, st, k, cx, cy, cz):
        E = unpack(st); v = (x, y, z); E = tip_to_line(E, unit(v), mu, 'tr')
        return (*sq_in(v, E), pack(E))
    return f


def orbmean(eps, mode):
    """Square in the frame; then the page becomes THE PLANE THAT THE WHOLE ORBIT HAS MADE SO FAR: every step so far has
    made a plane (through the origin, the point and the new point) with out-of-page line w_j = v_j^ x v_(j+1)^; the page's
    out-of-page line is the main axis of  N = eps * z z^T + sum_j w_j w_j^T  (the flat page counts as a plane of weight
    eps; each step's plane counts by the squared sine of the angle of the step).  Carries N as six more arrays."""
    def f(x, y, z, st, k, cx, cy, cz):
        E = unpack(st); v = (x, y, z); F = sq_in(v, E); n = (F[0] + cx, F[1] + cy, F[2] + cz)
        w = cross(unit(v), unit(n))
        N = (st[9] + w[0] * w[0], st[10] + w[1] * w[1], st[11] + w[2] * w[2], st[12] + w[0] * w[1], st[13] + w[0] * w[2], st[14] + w[1] * w[2])
        A = np.empty((x.size, 3, 3)); A[:, 0, 0], A[:, 1, 1], A[:, 2, 2] = N[0], N[1], N[2]
        A[:, 0, 1] = A[:, 1, 0] = N[3]; A[:, 0, 2] = A[:, 2, 0] = N[4]; A[:, 1, 2] = A[:, 2, 1] = N[5]
        bad = ~np.isfinite(A).all(axis=(1, 2)); A[bad] = np.eye(3)
        vec = np.linalg.eigh(A)[1][:, :, 2] if x.size else np.zeros((0, 3))
        n3 = (vec[:, 0], vec[:, 1], vec[:, 2]); s = np.where(dot(n3, E[2]) < 0, -1.0, 1.0)
        return (*F, pack(tip_e3_to(E, mul(n3, s), 1.0, mode), N))
    return f


def orbarea(mu, mode):
    """As orbplane, but the plane of a step is counted by the AREA it sweeps: w = v x v' (not unit vectors), the vector
    that stands square to the triangle origin - point - new point and is as long as twice its area.  A step that passes
    close to the origin sweeps no area and leaves the page alone (the direction of a tiny point is noise).  mu = how
    much a plane of area 1 counts against the page as it is."""
    def f(x, y, z, st, k, cx, cy, cz):
        E = unpack(st); v = (x, y, z); F = sq_in(v, E); n = (F[0] + cx, F[1] + cy, F[2] + cz)
        return (*F, pack(tip_to_line(E, cross(v, n), mu, mode)))
    return f


def meanarea(eps, mode):
    """As orbmean, with every step's plane counted by the squared area it sweeps: N = eps z z^T + sum_j w_j w_j^T,
    w_j = v_j x v_(j+1)."""
    def f(x, y, z, st, k, cx, cy, cz):
        E = unpack(st); v = (x, y, z); F = sq_in(v, E); n = (F[0] + cx, F[1] + cy, F[2] + cz)
        w = cross(v, n)
        N = (st[9] + w[0] * w[0], st[10] + w[1] * w[1], st[11] + w[2] * w[2], st[12] + w[0] * w[1], st[13] + w[0] * w[2], st[14] + w[1] * w[2])
        A = np.empty((x.size, 3, 3)); A[:, 0, 0], A[:, 1, 1], A[:, 2, 2] = N[0], N[1], N[2]
        A[:, 0, 1] = A[:, 1, 0] = N[3]; A[:, 0, 2] = A[:, 2, 0] = N[4]; A[:, 1, 2] = A[:, 2, 1] = N[5]
        bad = ~np.isfinite(A).all(axis=(1, 2)); A[bad] = np.eye(3)
        vec = np.linalg.eigh(A)[1][:, :, 2] if x.size else np.zeros((0, 3))
        n3 = (vec[:, 0], vec[:, 1], vec[:, 2]); s = np.where(dot(n3, E[2]) < 0, -1.0, 1.0)
        return (*F, pack(tip_e3_to(E, mul(n3, s), 1.0, mode), N))
    return f


def turnarea(share):
    """Frame turned by the tilt part of the turn vector share * (v x v') (not unit vectors: fades near the origin)."""
    def f(x, y, z, st, k, cx, cy, cz):
        E = unpack(st); v = (x, y, z); F = sq_in(v, E); n = (F[0] + cx, F[1] + cy, F[2] + cz)
        return (*F, pack(turn_frame(E, mul(tilt_part(cross(v, n), E), share))))
    return f


def keep_fade(mode):
    """keep_height with the share r^2 / (1 + r^2) of the tip (r = length of the point): fades near the origin."""
    def f(x, y, z, st, k, cx, cy, cz):
        E = unpack(st); v = (x, y, z); a, b, w = dot(v, E[0]), dot(v, E[1]), dot(v, E[2])
        A, B, W = P(a, b, w); F = tuple(A * E[0][i] + B * E[1][i] + W * E[2][i] for i in range(3))
        r = np.sqrt(a * a + b * b + w * w); ok = (np.hypot(a, b) > TINY) & (np.hypot(A, B) > TINY); rs = np.where(ok, r, 1.0)
        sL, cL = w / rs, np.hypot(a, b) / rs; R2 = rs * rs; rho2 = np.where(ok, np.hypot(A, B), 1.0)
        sL2, cL2, c2, s2 = W / R2, rho2 / R2, A / rho2, B / rho2
        q = (sL * A / R2 - cL * sL2 * c2, sL * B / R2 - cL * sL2 * s2, sL * sL2 + cL * cL2)
        n3 = tuple(np.where(ok, q[0] * E[0][i] + q[1] * E[1][i] + q[2] * E[2][i], E[2][i]) for i in range(3))
        return (*F, pack(tip_e3_to(E, unit(n3, E[2]), r * r / (1.0 + r * r), mode)))
    return f


def orbsticky(mode, fade=False):
    """Square in the frame; then the page tips toward the plane of the last two orbit points, but STICKILY, by the law
    that the bench rule 'along' uses for its sheet: if the smallest tip that would bring the page onto that plane is
    beta (between -90 and 90 degrees), the page tips by  beta - sin(4 beta) / 4.  So it stays put when the orbit's
    plane is close to the page, goes all the way when it is 45 degrees off, and flips a quarter turn when the orbit's
    plane stands square to the page.  fade = True: the tip is also multiplied by A / (1 + A), A = |v x v'|^2."""
    def f(x, y, z, st, k, cx, cy, cz):
        E = unpack(st); v = (x, y, z); F = sq_in(v, E); n = (F[0] + cx, F[1] + cy, F[2] + cz)
        w = cross(unit(v), unit(n)); e3 = E[2]; p = dot(w, e3); wp = add(w, e3, -p); q = np.sqrt(dot(wp, wp)); m = unit(wp)
        beta = 0.5 * np.arctan2(2 * p * q, p * p - q * q); tau = beta - 0.25 * np.sin(4 * beta)
        if fade:
            wa = cross(v, n); A = dot(wa, wa); tau = tau * A / (1.0 + A)
        if mode == 'tr':
            return (*F, pack(turn_frame(E, mul(cross(e3, m), tau))))
        return (*F, pack(shadow_e1(E, unit(add(mul(e3, np.cos(tau)), m, np.sin(tau)), e3))))
    return f


def init_mean(eps):
    def f(n):
        st = list(init_frame(6)(n)); st[11] = np.full(n, float(eps)); return tuple(st)
    return f


def R(name, label, step, extra=0): return M.Rule(name, label, step, init_frame(extra))


FIXED = R('fr_fixed', 'The frame never moves (must be the one-plane rule)', r_fixed)
FAILS = [
    R('turn_full', 'Frame turned by the WHOLE shortest turn point -> new point', turn(1.0, full=True)),
    R('turn_full_half', 'Frame turned by HALF of the whole shortest turn point -> new point', turn(0.5, full=True)),
    R('e1_to_point', 'Real axis of the frame turned (inside the page) to the point, then squared', e1_to_point),
    R('transport_full', 'Frame carried parallel along the path of the orbit, whole turn', transport(1.0, full=True), 3),
]
RULES = [
    R('turn1', 'Frame turned by the tilt part of the turn point -> new point', turn(1.0)),
    R('turn50', 'Frame turned by half of the tilt part of the turn point -> new point', turn(0.5)),
    R('turnsq', 'Frame turned by the tilt part of the turn point -> its square (c not counted)', turn(1.0, to='square')),
    R('turnsin', 'Frame turned by the tilt part of the turn vector v^ x v\'^ (sine in place of angle)', turn(1.0, smooth=True)),
    R('transport', 'Frame carried parallel along the path of the orbit, tilt part only', transport(1.0), 3),
    R('orb_inf_px', 'Page = the plane of the last two orbit points; real axis = shadow of the x-axis', orbplane(np.inf, 'px')),
    R('orb_inf_tr', 'Page = the plane of the last two orbit points; real axis carried along', orbplane(np.inf, 'tr')),
    R('orb_05_tr', 'Page tips part of the way (mu = 0.5) to the plane of the last two points; axis carried', orbplane(0.5, 'tr')),
    R('orb_2_tr', 'Page tips most of the way (mu = 2) to the plane of the last two points; axis carried', orbplane(2.0, 'tr')),
    R('orb_2_px', 'Page tips most of the way (mu = 2) to the plane of the last two points; axis = shadow of x', orbplane(2.0, 'px')),
    R('osc_inf_tr', 'Page = the plane in which the path has just bent; real axis carried along', osc(np.inf, 'tr'), 3),
    R('osc_1_tr', 'Page tips part of the way (mu = 1) to the plane in which the path has just bent', osc(1.0, 'tr'), 3),
    R('pt_1_tr', 'Before squaring the page tips by the shortest tip until it holds the point; axis carried', topoint(1.0, 'tr')),
    R('pt_50_tr', 'Before squaring the page tips half of the way (shortest tip) to the point; axis carried', topoint(0.5, 'tr')),
    R('pt_1_px', 'Before squaring the page tips (shortest tip) until it holds the point; axis = shadow of x', topoint(1.0, 'px')),
    R('pt_soft_tr', 'Before squaring the page tips toward the point by sin(2L)/2 (soft); axis carried', topoint(1.0, 'tr', soft=True)),
    # second batch
    R('turn25', 'Frame turned by a quarter of the tilt part of the turn point -> new point', turn(0.25)),
    R('keep_tr', 'Page tips with the squaring so that the square stands as high above it as the point did; axis carried', keep_height(1.0, 'tr')),
    R('keep_px', 'Page tips with the squaring so that the square stands as high above it as the point did; axis = shadow of x', keep_height(1.0, 'px')),
    R('keep50_tr', 'Page tips half as much as the squaring pushes the point toward the pole; axis carried', keep_height(0.5, 'tr')),
    R('orbsq_inf_px', 'Page = the plane of the point and its square (c not counted); axis = shadow of x', orbsq(np.inf, 'px')),
    R('pole_05', 'Before squaring the out-of-page line moves toward the point (mu = 0.5)', pole_to_point(0.5)),
    M.Rule('mean_1_px', 'Page = the plane the whole orbit has made so far (flat page counts 1); axis = shadow of x', orbmean(1.0, 'px'), init_mean(1.0)),
    M.Rule('mean_01_px', 'Page = the plane the whole orbit has made so far (flat page counts 0.1); axis = shadow of x', orbmean(0.1, 'px'), init_mean(0.1)),
    M.Rule('mean_01_tr', 'Page = the plane the whole orbit has made so far (flat page counts 0.1); axis carried', orbmean(0.1, 'tr'), init_mean(0.1)),
    # third batch: the same, counted by AREA (fades where the orbit passes close to the origin)
    R('area_1_px', 'Page tips to the plane of the last step, counted by the area it sweeps (mu = 1); axis = shadow of x', orbarea(1.0, 'px')),
    R('area_4_px', 'Page tips to the plane of the last step, counted by the area it sweeps (mu = 4); axis = shadow of x', orbarea(4.0, 'px')),
    R('area_16_px', 'Page tips to the plane of the last step, counted by the area it sweeps (mu = 16); axis = shadow of x', orbarea(16.0, 'px')),
    R('area_4_tr', 'Page tips to the plane of the last step, counted by the area it sweeps (mu = 4); axis carried', orbarea(4.0, 'tr')),
    M.Rule('marea_1_px', 'Page = the plane the whole orbit has made so far, by area (flat page counts 1); axis = shadow of x', meanarea(1.0, 'px'), init_mean(1.0)),
    M.Rule('marea_01_px', 'Page = the plane the whole orbit has made so far, by area (flat page counts 0.1); axis = shadow of x', meanarea(0.1, 'px'), init_mean(0.1)),
    R('turnarea', 'Frame turned by the tilt part of the turn vector v x v\' (by area)', turnarea(1.0)),
    R('keepfade_tr', 'Page tips with the squaring (height kept), fading near the origin; axis carried', keep_fade('tr')),
    # fourth batch: sticky following (the law of 'along', applied to the plane of the last two orbit points)
    R('sticky_px', 'Page tips stickily (law of along) to the plane of the last two points; axis = shadow of x', orbsticky('px')),
    R('sticky_tr', 'Page tips stickily (law of along) to the plane of the last two points; axis carried', orbsticky('tr')),
    R('stickyfade_px', 'Page tips stickily to the plane of the last two points, fading for small areas; axis = shadow of x', orbsticky('px', fade=True)),
]
BY = {r.name: r for r in [FIXED] + FAILS + RULES}

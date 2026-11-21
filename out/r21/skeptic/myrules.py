"""Skeptic's rules, round 21.

ATTEMPTS: recipes with NOTHING fixed off the x-axis (no starting page, no convention that names a page), built to try
to break Claim S. "No sheet yet" is carried as the zero vector u = (0, 0); the first point then makes the sheet.
LAGS: the scout's lag family at more lags (these DO start at the flat page, as in M.SCOUT).
"""
import sys
import numpy as np
sys.path.insert(0, 'out/r21/lib')
import mem as M


def none_yet(n):
    return (np.zeros(n), np.zeros(n))


def is_none(st):
    return (st[0] == 0) & (st[1] == 0)


def turn2(u1, u2, a):
    """The sheet u turned on by the angle a (radians, array or number), counter-clockwise for an eye on the +x side
    looking back at the origin. This is the only place where handedness (right hand rule about +x) enters."""
    c, s = np.cos(2 * a), np.sin(2 * a)
    return u1 * c - u2 * s, u1 * s + u2 * c


def signed_turn(q1, q2, p1, p2):
    """The handed angle (radians, in (-90, 90] degrees) that takes the sheet q to the sheet p."""
    return 0.5 * np.arctan2(q1 * p2 - q2 * p1, q1 * p1 + q2 * p2)


# S1: the scout's lag rule WITHOUT its starting page: the first point's own sheet is the first sheet
def lag_ns(lam):
    def f(x, y, z, st, k, cx, cy, cz):
        u = M.blend(*st, *M.sheet_of(y, z, *st), lam)       # st = (0, 0): the blend is the point's own sheet
        return (*M.sq_about(x, y, z, *u), u)
    return f


# S2: each point about the sheet of the point before it; the very first about its own
def delay_ns(x, y, z, st, k, cx, cy, cz):
    p = M.sheet_of(y, z, *st); no = is_none(st)
    u = (np.where(no, p[0], st[0]), np.where(no, p[1], st[1]))
    return (*M.sq_about(x, y, z, *u), p)


# S3: handedness alone: every point about its own sheet turned on by a fixed angle (right hand rule about +x)
def hand(deg):
    def f(x, y, z, st, k, cx, cy, cz):
        u = turn2(*M.sheet_of(y, z, *st), np.radians(deg))
        return (*M.sq_about(x, y, z, *u), st)
    return f


# S4: handedness with memory: the sheet runs AHEAD of the point, by g times the handed turn from the last point's sheet to this one's
def ahead(g):
    def f(x, y, z, st, k, cx, cy, cz):
        p = M.sheet_of(y, z, *st); no = is_none(st)
        d = np.where(no, 0.0, signed_turn(st[0], st[1], p[0], p[1]))
        u = turn2(p[0], p[1], g * d)
        return (*M.sq_about(x, y, z, *u), p)
    return f


# S5: rules that look at c
def c_sheet(x, y, z, st, k, cx, cy, cz):                     # the user's earlier question: about the sheet that c makes
    u = M.sheet_of(cy, cz, *M.sheet_of(y, z, *st))           # c on the x-axis makes no sheet: the point's own is used
    return (*M.sq_about(x, y, z, *u), st)


def c_hand(deg):                                             # about c's sheet turned on by a fixed angle (handed)
    def f(x, y, z, st, k, cx, cy, cz):
        u = turn2(*M.sheet_of(cy, cz, *M.sheet_of(y, z, *st)), np.radians(deg))
        return (*M.sq_about(x, y, z, *u), st)
    return f


def c_mid(x, y, z, st, k, cx, cy, cz):                       # about the sheet half-way between c's sheet and the point's own
    p = M.sheet_of(y, z, *st); cs = M.sheet_of(cy, cz, *p)
    u = M.blend(*cs, *p, 0.5)
    return (*M.sq_about(x, y, z, *u), st)


def c_lag(lam):                                              # the carried sheet starts as c's sheet, then lags after the point
    def f(x, y, z, st, k, cx, cy, cz):
        if k == 0:
            st = M.sheet_of(cy, cz, *st)
        u = M.blend(*st, *M.sheet_of(y, z, *st), lam)
        return (*M.sq_about(x, y, z, *u), u)
    return f


def c_ahead(g):                                              # handed, looks at c: the sheet runs ahead of the point by g times its handed turn from c's sheet
    def f(x, y, z, st, k, cx, cy, cz):
        p = M.sheet_of(y, z, *st); cs = M.sheet_of(cy, cz, *p)
        u = turn2(p[0], p[1], g * signed_turn(cs[0], cs[1], p[0], p[1]))
        return (*M.sq_about(x, y, z, *u), st)
    return f


# S6: memory of earlier POINTS: square about the plane through 0, the point before and this point (any plane, not only sheets)
def span2(x, y, z, st, k, cx, cy, cz):
    px, py, pz = st
    nx, ny, nz = py * z - pz * y, pz * x - px * z, px * y - py * x                   # normal = before x now
    nn = np.sqrt(nx * nx + ny * ny + nz * nz); sc = np.sqrt((px * px + py * py + pz * pz) * (x * x + y * y + z * z))
    ok = nn > 1e-12 * np.maximum(sc, 1e-300)
    # where there is no plane yet (first point, or the two points in line with 0): the point's own sheet, normal = x-axis x point
    rho = np.hypot(y, z); ok2 = rho > 1e-300; m = np.where(ok2, rho, 1.0)
    ax, ay, az = np.zeros_like(x), np.where(ok2, -z / m, 0.0), np.where(ok2, y / m, 1.0)
    m = np.where(ok, nn, 1.0)
    nx, ny, nz = np.where(ok, nx / m, ax), np.where(ok, ny / m, ay), np.where(ok, nz / m, az)
    # real axis of the plane: the x-axis laid down onto it; if the plane stands square to the x-axis, the point's own sheet again
    e1x, e1y, e1z = 1 - nx * nx, -nx * ny, -nx * nz
    l1 = np.sqrt(e1x * e1x + e1y * e1y + e1z * e1z); bad = l1 < 1e-9
    nx, ny, nz = np.where(bad, ax, nx), np.where(bad, ay, ny), np.where(bad, az, nz)
    e1x, e1y, e1z = 1 - nx * nx, -nx * ny, -nx * nz
    l1 = np.sqrt(e1x * e1x + e1y * e1y + e1z * e1z); e1x, e1y, e1z = e1x / l1, e1y / l1, e1z / l1
    e2x, e2y, e2z = ny * e1z - nz * e1y, nz * e1x - nx * e1z, nx * e1y - ny * e1x     # n x e1
    a, b, c = x * e1x + y * e1y + z * e1z, x * e2x + y * e2y + z * e2z, x * nx + y * ny + z * nz
    A, B, C = M.S.oneplane(a, b, c)
    return A * e1x + B * e2x + C * nx, A * e1y + B * e2y + C * ny, A * e1z + B * e2z + C * nz, (x, y, z)


# S7: the mean sheet of the whole orbit so far (this point included); the sum is carried, not normalised
def mean_sheet(x, y, z, st, k, cx, cy, cz):
    p = M.sheet_of(y, z, 0.0, 0.0); s = (st[0] + p[0], st[1] + p[1])
    n = np.hypot(*s); ok = n > 1e-9; m = np.where(ok, n, 1.0)
    u = (np.where(ok, s[0] / m, p[0]), np.where(ok, s[1] / m, p[1]))
    return (*M.sq_about(x, y, z, *u), s)


# S8: the sheet of the orbit point that has been farthest from the x-axis so far
def far_sheet(x, y, z, st, k, cx, cy, cz):
    u1, u2, d = st; rho = np.hypot(y, z); p = M.sheet_of(y, z, u1, u2); new = rho > d
    u = (np.where(new, p[0], u1), np.where(new, p[1], u2))
    return (*M.sq_about(x, y, z, *u), (u[0], u[1], np.maximum(rho, d)))


ATTEMPTS = [
    M.Rule('S1 lag25, no start page', 'lag 0.25, but the first point makes the first sheet', lag_ns(0.25), none_yet),
    M.Rule('S1 lag75, no start page', 'lag 0.75, but the first point makes the first sheet', lag_ns(0.75), none_yet),
    M.Rule('S2 delay, no start page', 'about the sheet of the point before; the first about its own', delay_ns, none_yet),
    M.Rule('S3 hand 20', 'own sheet turned on by 20 degrees, right hand rule', hand(20.0), none_yet),
    M.Rule('S3 hand 45', 'own sheet turned on by 45 degrees, right hand rule', hand(45.0), none_yet),
    M.Rule('S4 ahead 1', 'sheet runs ahead of the point by its last handed turn', ahead(1.0), none_yet),
    M.Rule('S4 ahead 3', 'sheet runs ahead of the point by 3 times its last handed turn', ahead(3.0), none_yet),
    M.Rule('S4 behind 0.5', 'sheet hangs back by half the last handed turn', ahead(-0.5), none_yet),
    M.Rule('S5 c sheet', 'about the sheet that c makes', c_sheet, none_yet),
    M.Rule('S5 c sheet + 30', 'about the sheet that c makes, turned on by 30 degrees (handed)', c_hand(30.0), none_yet),
    M.Rule('S5 c mid', 'about the sheet half-way between c\'s and the point\'s', c_mid, none_yet),
    M.Rule('S5 c lag25', 'carried sheet starts as c\'s sheet, then lag 0.25', c_lag(0.25), none_yet),
    M.Rule('S5 c ahead 1', 'sheet runs ahead of the point by its handed turn from c\'s sheet', c_ahead(1.0), none_yet),
    M.Rule('S6 span2', 'about the plane through 0, the point before and this point', span2, lambda n: (np.zeros(n), np.zeros(n), np.zeros(n))),
    M.Rule('S7 mean sheet', 'about the mean sheet of the orbit so far', mean_sheet, none_yet),
    M.Rule('S8 far sheet', 'about the sheet of the orbit point farthest from the x-axis so far', far_sheet, lambda n: (np.zeros(n), np.zeros(n), np.full(n, -1.0))),
]

LAMS = [0.05, 0.1, 0.25, 0.4, 0.5, 0.6, 0.75, 0.9, 0.95]
MORE = [0.45, 0.55, 0.65, 0.7, 0.8]          # added after the first look: the stretch where buds appear on the upright sheet
LAGS = [M.Rule('lag%02d' % round(100 * l), 'the sheet moves %g of the way to the point before each squaring' % l, M.lag(l)) for l in LAMS]
LAGS2 = [M.Rule('lag%02d' % round(100 * l), 'the sheet moves %g of the way to the point before each squaring' % l, M.lag(l)) for l in MORE]
BY = {r.name: r for r in LAGS + LAGS2 + M.SCOUT + ATTEMPTS}
RULES = LAGS + LAGS2 + ATTEMPTS

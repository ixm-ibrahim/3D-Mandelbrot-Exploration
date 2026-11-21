"""Round 21, agent 'alongmem': the fixed rule 'along' made into rules with memory.

'along' (bench name; out/me/r16/scout3.py turning(1)):
    phi = atan2(z, y)                      the point's turn round the x-axis, measured from the flat page
    psi = phi - sin(4 phi) / 4             the turn of the sheet the point is squared about
    along(v) = Rot_x(psi) P(Rot_x(-psi) v) P = the one-plane square (out/me/r16/scout.py oneplane)

Four groups of rules. In all of them the carried thing starts as the flat page.

A. THE WHOLE FRAME IS CARRIED. along is taken about a carried turn theta: Rot_x(theta) along(Rot_x(-theta) v).
   Worked out, that is the SAME rule with  psi = phi - sin(4 (phi - theta)) / 4.
   along repeats every 90 degrees, so theta is carried as u = (cos 4 theta, sin 4 theta), and with w = (cos 4 phi,
   sin 4 phi) of the point:  sin(4 (phi - theta)) = w2 u1 - w1 u2. No angle is ever taken of u: no tear from a branch.
B. ONLY THE TURNING SHEET IS CARRIED. The carried thing is the sheet s the point is squared about (P about s). It
   moves toward along's sheet psi(phi) of the point. Never moving = the one-plane rule; moving all the way = along.
C. THE FLAT SPOTS FOLLOW, THE SQUARING STAYS ABOUT THE FLAT PAGE. A carried sheet theta follows the point's own sheet;
   the point is squared by P about the sheet at  psi = (phi - theta) - sin(4 (phi - theta)) / 4  measured from the
   flat page. Never moving = along; following at once = the one-plane rule.
D. THE FRAME FOLLOWS c'S SHEET AS WELL AS THE ORBIT (group A with a second pull toward the sheet of c).
E. MADE ONCE AND KEPT (a_keep, b_keep, c_keep): the carried thing is set by the start point and never moves again.
Hand-over rules of group C: c_wake(n) = n squarings of plain along, then the one-plane rule; c_alt = taking turns.
Every definition is written out in NOTES.md; what each rule does to the Julia sets is in the table there.

    import sys; sys.path.insert(0, 'out/r21/lib'); sys.path.insert(0, 'out/r21/alongmem'); import mem as M, myrules as R
    R.RULES          the list;  R.get('a_lag25')  one rule by name
"""
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), 'lib'))
import mem as M
P = M.S.oneplane


# ---------------------------------------------------------------- building blocks
def sq_psi(x, y, z, psi):
    """The one-plane square about the sheet through the x-axis at the turn psi (radians)."""
    c, s = np.cos(psi), np.sin(psi)
    X, Y, Z = P(x, c * y + s * z, c * z - s * y)
    return X, c * Y - s * Z, s * Y + c * Z


def four(y, z, u1, u2):
    """w = (cos 4 phi, sin 4 phi) of the point's turn round the x-axis; u is kept where the point is on the x-axis."""
    q1, q2 = y * y - z * z, 2 * y * z; a, b = q1 * q1 - q2 * q2, 2 * q1 * q2
    n = np.hypot(a, b); ok = n > 1e-300; m = np.where(ok, n, 1.0)
    return np.where(ok, a / m, u1), np.where(ok, b / m, u2)


def turn_of(y, z):
    """cos and sin of the point's turn phi round the x-axis (exactly (+-1, 0) on the flat page; (1, 0) on the x-axis)."""
    rho = np.hypot(y, z); ok = rho > 0; m = np.where(ok, rho, 1.0)
    return np.where(ok, y / m, 1.0), np.where(ok, z / m, 0.0)


def sq_cs(x, y, z, c, s):
    """The one-plane square about the sheet whose turn has cosine c and sine s."""
    X, Y, Z = P(x, c * y + s * z, c * z - s * y)
    return X, c * Y - s * Z, s * Y + c * Z


def along_u(x, y, z, u1, u2):
    """along about the carried frame u = (cos 4 theta, sin 4 theta):  psi = phi - sin(4 (phi - theta)) / 4.
    u need not have length 1: its length is then the strength of the wobble (0 = the lathe, 1 = along about theta).
    Written without any angle function of phi, so that a point of the flat page stays on it to the last bit."""
    cp, sp = turn_of(y, z); w1, w2 = four(y, z, 1.0, 0.0); a = 0.25 * (w2 * u1 - w1 * u2); ca, sa = np.cos(a), np.sin(a)
    return sq_cs(x, y, z, cp * ca + sp * sa, sp * ca - cp * sa)


def along_sheet(y, z, s1, s2):
    """The sheet along squares this point about, as a doubled-angle vector (cos 2 psi, sin 2 psi); s kept on the x-axis."""
    p1, p2 = M.sheet_of(y, z, 1.0, 0.0); w1, w2 = four(y, z, 1.0, 0.0); ca, sa = np.cos(0.5 * w2), np.sin(0.5 * w2)
    ok = (y * y + z * z) > 1e-300
    return np.where(ok, p1 * ca + p2 * sa, s1), np.where(ok, p2 * ca - p1 * sa, s2)


def start2(n):
    return (np.ones(n), np.zeros(n))


# ---------------------------------------------------------------- A: the whole frame is carried
def a_fixed(x, y, z, st, k, cx, cy, cz):
    return (*along_u(x, y, z, *st), st)


def a_own(x, y, z, st, k, cx, cy, cz):
    u = four(y, z, *st); return (*along_u(x, y, z, *u), u)


def a_first(x, y, z, st, k, cx, cy, cz):
    u = four(y, z, *st) if k > 0 else st; return (*along_u(x, y, z, *u), u)


def a_delay(x, y, z, st, k, cx, cy, cz):
    return (*along_u(x, y, z, *st), four(y, z, *st))


def a_lag(lam, skip_first=False):
    """Before each squaring the frame moves the share lam of the way to the point (on the circle of 4 theta)."""
    def f(x, y, z, st, k, cx, cy, cz):
        u = st if (skip_first and k == 0) else M.blend(*st, *four(y, z, *st), lam)
        return (*along_u(x, y, z, *u), u)
    return f


def a_votes(d, w0=1.0):
    """Votes with decay: every orbit point votes with w; old votes fade by the factor d each step; the start (the flat
    page) is a vote of weight w0. The frame is the direction of the sum. State: the sum (not normalised)."""
    def f(x, y, z, st, k, cx, cy, cz):
        w = four(y, z, np.zeros_like(x), np.zeros_like(x))
        U1, U2 = d * st[0] + w[0], d * st[1] + w[1]
        n = np.hypot(U1, U2); ok = n > 1e-9; m = np.where(ok, n, 1.0)
        u1, u2 = np.where(ok, U1 / m, 0.0), np.where(ok, U2 / m, 0.0)          # no direction: no wobble (lathe step)
        return (*along_u(x, y, z, u1, u2), (U1, U2))
    return f, (lambda n: (w0 * np.ones(n), np.zeros(n)))


def a_mean(lam):
    """A running mean of the votes, NOT normalised: where the orbit's sheets agree it has length 1 (along about them),
    where they scatter it shrinks and the wobble fades (toward the lathe). No tear anywhere."""
    def f(x, y, z, st, k, cx, cy, cz):
        w = four(y, z, *st); u = ((1 - lam) * st[0] + lam * w[0], (1 - lam) * st[1] + lam * w[1])
        return (*along_u(x, y, z, *u), u)
    return f


def a_settle(p=1.0, first=1.0):
    """The frame settles: at squaring number k it moves the share first / (k + 1)^p of the way to the point."""
    def f(x, y, z, st, k, cx, cy, cz):
        u = M.blend(*st, *four(y, z, *st), min(first / (k + 1.0) ** p, 1.0))
        return (*along_u(x, y, z, *u), u)
    return f


def a_wake(n0):
    """The other way round: the frame stays the flat page for the first n0 squarings (pure along), then follows at once."""
    def f(x, y, z, st, k, cx, cy, cz):
        u = four(y, z, *st) if k >= n0 else st; return (*along_u(x, y, z, *u), u)
    return f


def a_lagaxis(lam):
    """a_lag, but a point's say is weighed by how far it stands off the x-axis: weight lam * (rho / r)^2."""
    def f(x, y, z, st, k, cx, cy, cz):
        p2 = y * y + z * z; r2 = np.maximum(x * x + p2, 1e-300); l = lam * p2 / r2
        w = four(y, z, *st); b1, b2 = (1 - l) * st[0] + l * w[0], (1 - l) * st[1] + l * w[1]
        n = np.hypot(b1, b2); ok = n > 1e-9; m = np.where(ok, n, 1.0)
        u = (np.where(ok, b1 / m, st[0]), np.where(ok, b2 / m, st[1]))
        return (*along_u(x, y, z, *u), u)
    return f


# ---------------------------------------------------------------- B: only the turning sheet is carried
def b_lag(lam):
    def f(x, y, z, st, k, cx, cy, cz):
        s = M.blend(*st, *along_sheet(y, z, *st), lam); return (*M.sq_about(x, y, z, *s), s)
    return f


def b_delay(x, y, z, st, k, cx, cy, cz):
    return (*M.sq_about(x, y, z, *st), along_sheet(y, z, *st))


def b_mean(lam):
    """The carried sheet is a running mean of along's sheets, NOT normalised; the point is squared about the sheet at
    the turn (length of the mean) * (turn of the mean): scattered votes fall back to the flat page (one-plane rule)."""
    def f(x, y, z, st, k, cx, cy, cz):
        t = along_sheet(y, z, *st); s = ((1 - lam) * st[0] + lam * t[0], (1 - lam) * st[1] + lam * t[1])
        return (*sq_psi(x, y, z, 0.5 * np.arctan2(s[1], s[0]) * np.minimum(np.hypot(*s), 1.0)), s)
    return f


# ---------------------------------------------------------------- C: flat spots follow, squaring about the flat page
def _c_sq(x, y, z, s1, s2):
    """P about the sheet at psi = d - sin(4 d) / 4, d = phi - theta, theta = the carried sheet s = (cos 2 theta, sin 2 theta)."""
    cp, sp = turn_of(y, z); ct, st_ = M.half(s1, s2); cd, sd = cp * ct + sp * st_, sp * ct - cp * st_          # cos d, sin d
    e1, e2 = cd * cd - sd * sd, 2 * cd * sd; a = 0.5 * e1 * e2; ca, sa = np.cos(a), np.sin(a)                  # a = sin(4 d) / 4
    return sq_cs(x, y, z, cd * ca + sd * sa, sd * ca - cd * sa)


def c_lag(lam):
    def f(x, y, z, st, k, cx, cy, cz):
        s = M.blend(*st, *M.sheet_of(y, z, *st), lam); return (*_c_sq(x, y, z, *s), s)
    return f


def c_delay(x, y, z, st, k, cx, cy, cz):
    return (*_c_sq(x, y, z, *st), M.sheet_of(y, z, *st))



def c_lagp(lam):
    """c_lag, but the first squaring is plain along (the sheet starts to move only after it)."""
    def f(x, y, z, st, k, cx, cy, cz):
        s = st if k == 0 else M.blend(*st, *M.sheet_of(y, z, *st), lam); return (*_c_sq(x, y, z, *s), s)
    return f


def c_settle(first=0.5, p=1.0):
    """The carried sheet settles: at squaring number k it moves the share first / (k + 1)^p of the way to the point."""
    def f(x, y, z, st, k, cx, cy, cz):
        s = M.blend(*st, *M.sheet_of(y, z, *st), min(first / (k + 1.0) ** p, 1.0)); return (*_c_sq(x, y, z, *s), s)
    return f


def c_wake(n0, lam=1.0):
    """Plain along for the first n0 squarings, after that the carried sheet moves lam of the way each step."""
    def f(x, y, z, st, k, cx, cy, cz):
        s = st if k < n0 else M.blend(*st, *M.sheet_of(y, z, *st), lam); return (*_c_sq(x, y, z, *s), s)
    return f


def c_alt(period=2, phase=0):
    """A counter is the only memory: plain along at the squarings number phase, phase + period, ...; the one-plane
    rule at all others."""
    def f(x, y, z, st, k, cx, cy, cz):
        s = st if k % period == phase else M.sheet_of(y, z, *st); return (*_c_sq(x, y, z, *s), st)
    return f


def c_lagaxis(lam):
    """c_lag, but a point's say is weighed by how far it stands off the x-axis: share lam * (rho / r)^2."""
    def f(x, y, z, st, k, cx, cy, cz):
        p2 = y * y + z * z; r2 = np.maximum(x * x + p2, 1e-300); l = lam * p2 / r2
        t = M.sheet_of(y, z, *st); b1, b2 = (1 - l) * st[0] + l * t[0], (1 - l) * st[1] + l * t[1]
        n = np.hypot(b1, b2); ok = n > 1e-9; m = np.where(ok, n, 1.0)
        s = (np.where(ok, b1 / m, st[0]), np.where(ok, b2 / m, st[1]))
        return (*_c_sq(x, y, z, *s), s)
    return f



# ---------------------------------------------------------------- E: the carried thing is made ONCE, by the first point(s), and kept
def b_keep(n0=1):
    """B, settled at once: the squaring sheet is along's sheet of the START point (of point number n0 - 1) and never
    moves again. Every later squaring is the one-plane square about that kept sheet."""
    def f(x, y, z, st, k, cx, cy, cz):
        s = along_sheet(y, z, *st) if k < n0 else st; return (*M.sq_about(x, y, z, *s), s)
    return f


def a_keep(x, y, z, st, k, cx, cy, cz):
    """A, settled at once: the frame of four sheets is turned to the START point and never moves again."""
    u = four(y, z, *st) if k == 0 else st; return (*along_u(x, y, z, *u), u)


def c_keep(x, y, z, st, k, cx, cy, cz):
    """C, settled at once: the flat spots are put at the sheet of the START point and never move again."""
    s = M.sheet_of(y, z, *st) if k == 0 else st; return (*_c_sq(x, y, z, *s), s)


def b_settle(first=1.0, p=1.0):
    """B settling: the squaring sheet is the running mean of along's sheets so far (step k moves it first / (k + 1)^p)."""
    def f(x, y, z, st, k, cx, cy, cz):
        s = M.blend(*st, *along_sheet(y, z, *st), min(first / (k + 1.0) ** p, 1.0)); return (*M.sq_about(x, y, z, *s), s)
    return f


# ---------------------------------------------------------------- D: the frame follows c's sheet as well
def d_lag(lam, mu):
    """Before each squaring the frame moves lam toward the point and mu toward the sheet of c (c on the x-axis has no
    sheet: its share goes back to the frame itself)."""
    def f(x, y, z, st, k, cx, cy, cz):
        w = four(y, z, *st); q = four(cy, cz, *st)
        b1 = (1 - lam - mu) * st[0] + lam * w[0] + mu * q[0]; b2 = (1 - lam - mu) * st[1] + lam * w[1] + mu * q[1]
        n = np.hypot(b1, b2); ok = n > 1e-9; m = np.where(ok, n, 1.0)
        u = (np.where(ok, b1 / m, st[0]), np.where(ok, b2 / m, st[1]))
        return (*along_u(x, y, z, *u), u)
    return f


def d_conly(lam):
    """The frame follows only c's sheet (never the orbit)."""
    return d_lag(0.0, lam)


_v9, _i9 = a_votes(0.9); _v5, _i5 = a_votes(0.5); _v1, _i1 = a_votes(1.0)
RULES = [
    M.Rule('a_fixed', 'A: the frame never moves (must equal along)', a_fixed),
    M.Rule('a_lag10', 'A: before each squaring the frame moves 10 % of the way to the point', a_lag(0.10)),
    M.Rule('a_lag25', 'A: before each squaring the frame moves a quarter of the way to the point', a_lag(0.25)),
    M.Rule('a_lag50', 'A: ... half of the way (tear: the blend can cancel)', a_lag(0.5)),
    M.Rule('a_lag75', 'A: ... three quarters of the way', a_lag(0.75)),
    M.Rule('a_lag25p', 'A: first squaring is plain along, then the frame moves a quarter of the way each step', a_lag(0.25, True)),
    M.Rule('a_delay', 'A: each point is squared about the frame of the point before it', a_delay),
    M.Rule('a_first', 'A: first squaring is plain along, every later one in the point\'s own frame', a_first),
    M.Rule('a_own', 'A: the point\'s own frame at once (must equal the lathe)', a_own),
    M.Rule('a_votes90', 'A: votes, old votes fade by 0.9 a step', _v9, _i9),
    M.Rule('a_votes50', 'A: votes, old votes fade by 0.5 a step', _v5, _i5),
    M.Rule('a_votes100', 'A: votes, nothing fades (the frame settles)', _v1, _i1),
    M.Rule('a_mean25', 'A: running mean of the votes, a quarter new each step; its length is the wobble\'s strength', a_mean(0.25)),
    M.Rule('a_mean50', 'A: running mean of the votes, half new each step; its length is the wobble\'s strength', a_mean(0.5)),
    M.Rule('a_settle', 'A: the frame settles: step k moves it 1 / (k + 2) of the way', a_settle(1.0, 0.5)),
    M.Rule('a_wake1', 'A: one squaring of plain along, then the point\'s own frame (same as a_first)', a_wake(1)),
    M.Rule('a_wake3', 'A: three squarings of plain along, then the point\'s own frame', a_wake(3)),
    M.Rule('a_lagaxis50', 'A: the frame moves up to half of the way; points near the x-axis have less say', a_lagaxis(0.5)),
    M.Rule('b_lag25', 'B: the squaring sheet moves a quarter of the way to along\'s sheet', b_lag(0.25)),
    M.Rule('b_lag50', 'B: the squaring sheet moves half of the way to along\'s sheet', b_lag(0.5)),
    M.Rule('b_lag75', 'B: the squaring sheet moves three quarters of the way to along\'s sheet', b_lag(0.75)),
    M.Rule('b_delay', 'B: each point is squared about along\'s sheet of the point before it', b_delay),
    M.Rule('b_mean50', 'B: running mean of along\'s sheets (half new), scattered votes fall back to the flat page', b_mean(0.5)),
    M.Rule('c_lag25', 'C: flat spots a quarter of the way to the point, squaring about the flat page', c_lag(0.25)),
    M.Rule('c_lag50', 'C: flat spots half of the way to the point, squaring about the flat page', c_lag(0.5)),
    M.Rule('c_lag75', 'C: flat spots three quarters of the way to the point, squaring about the flat page', c_lag(0.75)),
    M.Rule('c_delay', 'C: flat spots at the sheet of the point before, squaring about the flat page', c_delay),
    M.Rule('d_lag2525', 'D: the frame moves a quarter toward the point and a quarter toward c\'s sheet', d_lag(0.25, 0.25)),
    M.Rule('d_lag5025', 'D: the frame moves half toward the point and a quarter toward c\'s sheet', d_lag(0.5, 0.25)),
    M.Rule('d_conly50', 'D: the frame moves half of the way toward c\'s sheet only', d_conly(0.5)),
    M.Rule('c_lag10', 'C: flat spots 10 % of the way to the point, squaring about the flat page', c_lag(0.10)),
    M.Rule('c_lag35', 'C: flat spots 35 % of the way to the point, squaring about the flat page', c_lag(0.35)),
    M.Rule('c_lag40', 'C: flat spots 40 % of the way to the point, squaring about the flat page', c_lag(0.40)),
    M.Rule('c_lag45', 'C: flat spots 45 % of the way to the point, squaring about the flat page', c_lag(0.45)),
    M.Rule('c_lag60', 'C: flat spots 60 % of the way to the point, squaring about the flat page', c_lag(0.60)),
    M.Rule('c_lag25p', 'C: first squaring plain along, then flat spots a quarter of the way each step', c_lagp(0.25)),
    M.Rule('c_lag45p', 'C: first squaring plain along, then flat spots 45 % of the way each step', c_lagp(0.45)),
    M.Rule('c_settle', 'C: the flat spots settle: step k moves them 1 / (2 (k + 1)) of the way', c_settle(0.5, 1.0)),
    M.Rule('c_wake1', 'C: one squaring of plain along, then the one-plane rule', c_wake(1)),
    M.Rule('c_wake2', 'C: two squarings of plain along, then the one-plane rule', c_wake(2)),
    M.Rule('c_wake4', 'C: four squarings of plain along, then the one-plane rule', c_wake(4)),
    M.Rule('c_lagaxis45', 'C: flat spots up to 45 % of the way; points near the x-axis have less say', c_lagaxis(0.45)),
    M.Rule('c_lag0', 'C: flat spots never move (must equal along)', c_lag(0.0)),
    M.Rule('c_lag100', 'C: flat spots at the point at once (must equal the one-plane rule)', c_lag(1.0)),
    M.Rule('b_lag0', 'B: the squaring sheet never moves (must equal the one-plane rule)', b_lag(0.0)),
    M.Rule('b_lag100', "B: the squaring sheet is along's sheet at once (must equal along)", b_lag(1.0)),
    M.Rule('c_lag15', 'C: flat spots 15 % of the way to the point, squaring about the flat page', c_lag(0.15)),
    M.Rule('c_lag20', 'C: flat spots 20 % of the way to the point, squaring about the flat page', c_lag(0.20)),
    M.Rule('c_lag30', 'C: flat spots 30 % of the way to the point, squaring about the flat page', c_lag(0.30)),
    M.Rule('b_keep', "B: the squaring sheet is along's sheet of the START point, kept for the whole orbit", b_keep(1)),
    M.Rule('b_keep2', 'B: the squaring sheet follows along for two points, then is kept', b_keep(2)),
    M.Rule('b_keep3', 'B: the squaring sheet follows along for three points, then is kept', b_keep(3)),
    M.Rule('a_keep', 'A: the frame of four sheets is turned to the START point, kept for the whole orbit', a_keep),
    M.Rule('c_keep', "C: the flat spots are put at the START point's sheet, kept for the whole orbit", c_keep),
    M.Rule('b_settle', "B: the squaring sheet is the running mean of along's sheets so far", b_settle(1.0, 1.0)),
    M.Rule('c_wake3', 'C: three squarings of plain along, then the one-plane rule', c_wake(3)),
    M.Rule('c_wake6', 'C: six squarings of plain along, then the one-plane rule', c_wake(6)),
    M.Rule('c_wake8', 'C: eight squarings of plain along, then the one-plane rule', c_wake(8)),
    M.Rule('c_wake12', 'C: twelve squarings of plain along, then the one-plane rule', c_wake(12)),
    M.Rule('c_alt', 'C: along and the one-plane rule take turns (along first)', c_alt(2, 0)),
    M.Rule('c_altb', 'C: the one-plane rule and along take turns (one-plane first)', c_alt(2, 1)),
    M.Rule('c_alt3', 'C: along at every third squaring (the first one too), the one-plane rule at the others', c_alt(3, 0)),
]


def get(name):
    return [r for r in RULES if r.name == name][0]

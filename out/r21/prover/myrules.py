"""Round 21, the prover's TEST rules. None of these is a candidate: each one exists to test a statement in NOTES.md.

    import sys; sys.path.insert(0, 'out/r21/lib'); sys.path.insert(0, 'out/r21/prover'); import mem as M, myrules as R

"Covariant" below means: the recipe names nothing that is fixed off the x-axis (no flat page, no y, no z), so that
turning the start round the x-axis turns the whole orbit with it.  A carried sheet that has "no fixed start" is kept
as (u1, u2, d) with d = 0 while the orbit has not yet made a sheet.
"""
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), 'lib'))
import mem as M


def turn(u1, u2, deg):
    """The sheet u turned by deg degrees round the x-axis, right-handed (from +y toward +z). u is the doubled angle."""
    a = np.radians(2.0 * deg); return u1 * np.cos(a) - u2 * np.sin(a), u1 * np.sin(a) + u2 * np.cos(a)


def own_sheet(y, z):
    """The point's own sheet and whether it has one (a point on the x-axis has none)."""
    has = (y * y + z * z) > 0
    u1, u2 = M.sheet_of(y, z, 1.0, 0.0)
    return u1, u2, has


NOSHEET = lambda n: (np.ones(n), np.zeros(n), np.zeros(n))      # d = 0: no sheet yet (u is then never used)


# ---- memory with NO fixed start (covariant): Claim S says these must give spun solids
def _delay_cov(x, y, z, st, k, cx, cy, cz):
    """Each point is squared about the sheet of the last earlier point that had one; if there is none yet, about its own."""
    u1, u2, d = st; o1, o2, has = own_sheet(y, z)
    a1, a2 = np.where(d > 0, u1, o1), np.where(d > 0, u2, o2)
    X, Y, Z = M.sq_about(x, y, z, a1, a2)
    return X, Y, Z, (np.where(has, o1, u1), np.where(has, o2, u2), np.maximum(d, has))


def lag_cov(lam):
    """The carried sheet starts as the first sheet the orbit makes; before each squaring it moves the share lam toward the point's."""
    def f(x, y, z, st, k, cx, cy, cz):
        u1, u2, d = st; o1, o2, has = own_sheet(y, z)
        b1, b2 = M.blend(u1, u2, o1, o2, lam)
        n1 = np.where(d > 0, np.where(has, b1, u1), o1); n2 = np.where(d > 0, np.where(has, b2, u2), o2)
        X, Y, Z = M.sq_about(x, y, z, n1, n2)
        return X, Y, Z, (n1, n2, np.maximum(d, has))
    return f


# ---- handed and covariant: uses "turn right-handed round the x-axis", which a mirror would reverse
def twist(deg):
    """Each point is squared about its own sheet turned deg degrees to the right round the x-axis. Not exact on the flat page."""
    def f(x, y, z, st, k, cx, cy, cz):
        o1, o2, has = own_sheet(y, z); t1, t2 = turn(o1, o2, deg)
        return (*M.sq_about(x, y, z, t1, t2), st)
    return f


def _delay_twist(x, y, z, st, k, cx, cy, cz):
    """delay_cov, with the remembered sheet turned 30 degrees to the right before it is used."""
    u1, u2, d = st; o1, o2, has = own_sheet(y, z)
    a1, a2 = np.where(d > 0, u1, o1), np.where(d > 0, u2, o2); a1, a2 = turn(a1, a2, 30.0)
    X, Y, Z = M.sq_about(x, y, z, a1, a2)
    return X, Y, Z, (np.where(has, o1, u1), np.where(has, o2, u2), np.maximum(d, has))


# ---- the sheet that c makes (the user's earlier question), with the two possible conventions for c on the x-axis
def csheet(conv, twist=0.0):
    """Every point is squared about the sheet of c (turned by `twist` degrees). c on the x-axis has no sheet:
    conv = 'flat' uses the flat page (something fixed off the x-axis), conv = 'own' uses the point's own sheet (nothing fixed)."""
    def f(x, y, z, st, k, cx, cy, cz):
        c1, c2, chas = own_sheet(cy, cz)
        if conv == 'own':
            o1, o2, has = own_sheet(y, z); c1, c2 = np.where(chas, c1, o1), np.where(chas, c2, o2)
        if twist:
            c1, c2 = turn(c1, c2, twist)
        return (*M.sq_about(x, y, z, c1, c2), st)
    return f


# ---- memory that FORGETS its fixed start: the first kk squarings about the flat page, every later one about the point's own sheet
def first_k(kk):
    def f(x, y, z, st, k, cx, cy, cz):
        u = M.sheet_of(y, z, *st) if k >= kk else st
        return (*M.sq_about(x, y, z, *u), st)
    return f


def _lathe(x, y, z, st, k, cx, cy, cz):
    """The lathe written out (the quaternion square with no k part): no sheet is ever looked up."""
    return x * x - y * y - z * z, 2 * x * y, 2 * x * z, st


RULES = [
    M.Rule('delay_cov', 'Squared about the sheet of the point before; no fixed start (the first point uses its own sheet)', _delay_cov, NOSHEET),
    M.Rule('lag50_cov', 'The sheet lags half-way behind the point; it starts as the first sheet the orbit makes', lag_cov(0.5), NOSHEET),
    M.Rule('lag25_cov', 'The sheet lags three quarters behind the point; it starts as the first sheet the orbit makes', lag_cov(0.25), NOSHEET),
    M.Rule('twist', 'HANDED: squared about the own sheet turned 30 degrees to the right', twist(30.0)),
    M.Rule('twist8', 'HANDED: squared about the own sheet turned 8 degrees to the right', twist(8.0)),
    M.Rule('delay_twist', 'HANDED, with memory: the sheet of the point before, turned 30 degrees to the right; no fixed start', _delay_twist, NOSHEET),
    M.Rule('csheet_flat', 'Squared about the sheet of c; for c on the x-axis: the flat page', csheet('flat')),
    M.Rule('csheet_own', 'Squared about the sheet of c; for c on the x-axis: the point\'s own sheet', csheet('own')),
    M.Rule('csheet_twist', 'HANDED: squared about the sheet of c turned 30 degrees to the right (c on the x-axis: own sheet)', csheet('own', 30.0)),
    M.Rule('first1', 'First squaring about the flat page, later ones about the own sheet (= the scout\'s first)', first_k(1)),
    M.Rule('first2', 'First 2 squarings about the flat page, later ones about the own sheet', first_k(2)),
    M.Rule('first3', 'First 3 squarings about the flat page, later ones about the own sheet', first_k(3)),
    M.Rule('first5', 'First 5 squarings about the flat page, later ones about the own sheet', first_k(5)),
    M.Rule('first8', 'First 8 squarings about the flat page, later ones about the own sheet', first_k(8)),
    M.Rule('lathe_x', 'The lathe written out as a formula', _lathe),
]
BY = {r.name: r for r in RULES}

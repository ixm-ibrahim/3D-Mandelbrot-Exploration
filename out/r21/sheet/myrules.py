"""Round 21, agent "sheet": update rules for ONE carried sheet through the x-axis.

Every rule here: the orbit carries a sheet through the x-axis (it starts as the flat page), and each point is squared
by the one-plane rule P about a sheet. The rules differ only in HOW and WHEN the sheet is moved.

Words used below
    theta   the turn of the carried sheet from the flat page (radians; theta and theta + 180 deg are one sheet)
    phi     the turn of the point's own sheet = atan2(z, y) (the sheet that holds the x-axis and the point)
    d       phi - theta, brought into -90..90 degrees: how far the point's sheet is from the carried sheet
    h(d)    how far the sheet turns before the squaring. After the turn the point is delta = d - h(d) off its sheet.

    import sys; sys.path.insert(0, 'out/r21/sheet'); import myrules as R;  R.RULES, R.get('ease')
"""
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), 'lib'))
import mem as M

P = M.S.oneplane
PI = np.pi


def sq_at(x, y, z, th):
    """The one-plane square P taken about the sheet at the turn th."""
    co, si = np.cos(th), np.sin(th)
    X, Y, Z = P(x, co * y + si * z, co * z - si * y)
    return X, co * Y - si * Z, si * Y + co * Z


def wrap(d):
    """Bring a turn into -90..90 degrees (a sheet has no front and back)."""
    return d - PI * np.round(d / PI)


def own(y, z, th):
    """The turn of the point's own sheet; where the point lies on the x-axis, the carried turn (so that d = 0)."""
    return np.where(y * y + z * z > 1e-300, np.arctan2(z, y), th)


def toward(d, lam):
    """The turn that moves a sheet the share lam of the way to a sheet d away (blend of the doubled-angle vectors,
    the same blend as M.blend): half the angle of (1 - lam) + lam * exp(2 i d)."""
    return 0.5 * np.arctan2(lam * np.sin(2 * d), (1 - lam) + lam * np.cos(2 * d))


init1 = lambda n: (np.zeros(n),)


# ---------------------------------------------------------------- 1. the sheet turns by h(d), then the point is squared
def turn(h):
    def step(x, y, z, st, k, cx, cy, cz):
        th = st[0]; d = wrap(own(y, z, th) - th); th = wrap(th + h(d, x, y, z, k))
        return (*sq_at(x, y, z, th), (th,))
    return step


def T(name, label, h):
    return M.Rule(name, label, turn(h), init1)


def lam_rule(name, label, lam):
    """lam(d, x, y, z, k) -> the share of the way the sheet moves toward the point's sheet before the squaring."""
    return T(name, label, lambda d, x, y, z, k: toward(d, lam(d, x, y, z, k)))


def r2of(x, y, z):
    return np.maximum(x * x + y * y + z * z, 1e-300)


# ---------------------------------------------------------------- 2. votes
def vote(s, gamma, norm=False, after=False):
    """The orbit carries a sum w of votes. A point votes with the vector (y^2 - z^2, 2 y z) (its distance from the
    x-axis squared, in the direction of its own sheet, doubled angle); norm = True: that vector over |v|^2.
    w starts as (s, 0): a vote of strength s for the flat page. Each step: w <- gamma * w + vote; the sheet is the
    direction of w. after = True: the point is squared about the sheet BEFORE its own vote is counted."""
    def step(x, y, z, st, k, cx, cy, cz):
        w1, w2 = st; q1, q2 = y * y - z * z, 2 * y * z
        if norm:
            r2 = r2of(x, y, z); q1, q2 = q1 / r2, q2 / r2
        if not after:
            w1, w2 = gamma * w1 + q1, gamma * w2 + q2
        X, Y, Z = sq_at(x, y, z, 0.5 * np.arctan2(w2, w1))
        if after:
            w1, w2 = gamma * w1 + q1, gamma * w2 + q2
        return X, Y, Z, (w1, w2)
    return step, (lambda n: (np.full(n, float(s)), np.zeros(n)))


def V(name, label, *a, **kw):
    st, ini = vote(*a, **kw); return M.Rule(name, label, st, ini)


# ---------------------------------------------------------------- 3. the sheet is moved AFTER the squaring
def after(lam):
    """Square about the carried sheet, then move the sheet the share lam toward the sheet of the point just squared."""
    def step(x, y, z, st, k, cx, cy, cz):
        th = st[0]; out = sq_at(x, y, z, th); d = wrap(own(y, z, th) - th)
        return (*out, (wrap(th + toward(d, lam)),))
    return step


def image(lam, peek=False):
    """Square about the carried sheet, then move the sheet the share lam toward the sheet of the IMAGE (the square,
    before c is added). peek = True: do that first with a trial squaring, then square the point about the moved sheet."""
    def step(x, y, z, st, k, cx, cy, cz):
        th = st[0]; X, Y, Z = sq_at(x, y, z, th); d = wrap(own(Y, Z, th) - th); th = wrap(th + toward(d, lam))
        if peek:
            X, Y, Z = sq_at(x, y, z, th)
        return X, Y, Z, (th,)
    return step


# ---------------------------------------------------------------- 4. settling and waking
def settle(kown, lam=1.0):
    """For the first kown squarings the sheet moves the share lam toward the point's sheet; then it stays for good."""
    return turn(lambda d, x, y, z, k: toward(d, lam) if k < kown else 0 * d)


def late(kstay, lam=1.0):
    """For the first kstay squarings the sheet stays; after that it moves the share lam toward the point's sheet."""
    return turn(lambda d, x, y, z, k: toward(d, lam) if k >= kstay else 0 * d)


# ---------------------------------------------------------------- 5. c's own sheet in the mix
def cmix(lc, lp):
    """Before each squaring the sheet moves the share lc toward c's own sheet, then the share lp toward the point's."""
    def step(x, y, z, st, k, cx, cy, cz):
        th = st[0]
        th = th + toward(wrap(own(cy, cz, th) - th), lc)
        th = wrap(th + toward(wrap(own(y, z, th) - th), lp))
        return (*sq_at(x, y, z, th), (th,))
    return step


def bisect():
    """The sheet half-way between the own sheets of this point and of the point before it (the flat page stands in
    for 'the point before' at the first step). Carries the sheet of the point before."""
    def step(x, y, z, st, k, cx, cy, cz):
        prev = st[0]; mine = own(y, z, prev); th = prev + toward(wrap(mine - prev), 0.5)
        return (*sq_at(x, y, z, th), (mine,))
    return step


# ---------------------------------------------------------------- 6. second wave: weighted votes with an "eased" direction
def evote(s, gamma=None, ease=1.0):
    """Votes weighted by the distance from the x-axis, with the direction of each vote 'eased'.
    The orbit carries the vector w (doubled angle; it starts as (s, 0), the flat page with strength s).
    Each step: psi_w = direction of w; the point's own sheet has the doubled angle psi = atan2(2yz, y^2 - z^2);
    t = psi - psi_w brought into -180..180; the point votes with weight rho^2 = y^2 + z^2 for the direction
    psi_w + t - ease * sin(t)   (ease = 0: its own sheet, as in `vote`; ease = 1: a point near the sheet votes for
    the sheet as it is, a point square to the sheet votes for its own sheet, and near there it overshoots).
    gamma = None: w <- s * (unit vector along w) + vote  (the old weight is forgotten, only the direction is kept);
    gamma given:  w <- gamma * w + vote.   The point is squared about the sheet along the new w."""
    def step(x, y, z, st, k, cx, cy, cz):
        w1, w2 = st; pw = np.arctan2(w2, w1); rho2 = y * y + z * z
        t = np.arctan2(2 * y * z, y * y - z * z) - pw; t = t - 2 * PI * np.round(t / (2 * PI))
        a = pw + t - ease * np.sin(t)
        if gamma is None:
            b1, b2 = s * np.cos(pw), s * np.sin(pw)
        else:
            b1, b2 = gamma * w1, gamma * w2
        w1, w2 = b1 + rho2 * np.cos(a), b2 + rho2 * np.sin(a)
        return (*sq_at(x, y, z, 0.5 * np.arctan2(w2, w1)), (w1, w2))
    return step, (lambda n: (np.full(n, float(s)), np.zeros(n)))


def E(name, label, *a, **kw):
    st, ini = evote(*a, **kw); return M.Rule(name, label, st, ini)


def evc(s, ease_c=1.0, ease=1.0, kc=1.0):
    """Eased votes summed with no decay (as evote with gamma = 1), and c VOTES TOO, at every step, before the point:
    c votes with weight kc * (cy^2 + cz^2) for the direction psi_w + t_c - ease_c * sin(t_c), t_c = (doubled angle of
    c's own sheet) - psi_w. Then the point votes the same way against the new w, and is squared about the sheet along w.
    A c on the x-axis has no vote; a c off the axis anchors the sheet more firmly at every step."""
    def one(w1, w2, y, z, e, wt=1.0):
        pw = np.arctan2(w2, w1); rho2 = wt * (y * y + z * z)
        t = np.arctan2(2 * y * z, y * y - z * z) - pw; t = t - 2 * PI * np.round(t / (2 * PI)); a = pw + t - e * np.sin(t)
        return w1 + rho2 * np.cos(a), w2 + rho2 * np.sin(a)

    def step(x, y, z, st, k, cx, cy, cz):
        w1, w2 = one(*st, cy, cz, ease_c, kc); w1, w2 = one(w1, w2, y, z, ease)
        return (*sq_at(x, y, z, 0.5 * np.arctan2(w2, w1)), (w1, w2))
    return step, (lambda n: (np.full(n, float(s)), np.zeros(n)))


def C(name, label, *a, **kw):
    st, ini = evc(*a, **kw); return M.Rule(name, label, st, ini)


WAVE2 = [
    E('votefix010', 'Sheet = direction of 0.10 x (old sheet) + the point\'s vote (weight = distance from the axis squared)', 0.10, ease=0.0),
    E('votefix025', 'Sheet = direction of 0.25 x (old sheet) + the point\'s vote', 0.25, ease=0.0),
    E('votefix1',   'Sheet = direction of 1 x (old sheet) + the point\'s vote', 1.0, ease=0.0),
    E('evote005',   'Eased vote, old sheet counts 0.05: stays for near points, jumps to a far point square to it', 0.05),
    E('evote010',   'Eased vote, old sheet counts 0.10', 0.10),
    E('evote025',   'Eased vote, old sheet counts 0.25', 0.25),
    E('evsum010',   'Eased votes summed with no decay, the flat page starts with strength 0.10', 0.10, gamma=1.0),
    E('evhalf010',  'Eased votes summed, the old sum halves each step, the flat page starts with strength 0.10', 0.10, gamma=0.5),
    E('evhalf025',  'Eased votes summed, the old sum halves each step, the flat page starts with strength 0.25', 0.25, gamma=0.5),
    E('evsum005',   'Eased votes summed with no decay, the flat page starts with strength 0.05', 0.05, gamma=1.0),
    E('evsum020',   'Eased votes summed with no decay, the flat page starts with strength 0.20', 0.20, gamma=1.0),
    E('evsum040',   'Eased votes summed with no decay, the flat page starts with strength 0.40', 0.40, gamma=1.0),
    E('evslow010',  'Eased votes summed, the old sum loses a tenth each step, the flat page starts with strength 0.10', 0.10, gamma=0.9),
    E('evsumh010',  'Half-eased votes (ease 0.5) summed with no decay, the flat page starts with strength 0.10', 0.10, gamma=1.0, ease=0.5),
    C('evc002',     'Eased votes summed, c votes too at every step (eased); the flat page starts with strength 0.02', 0.02),
    C('evc005',     'Eased votes summed, c votes too at every step (eased); the flat page starts with strength 0.05', 0.05),
    C('evc010',     'Eased votes summed, c votes too at every step (eased); the flat page starts with strength 0.10', 0.10),
    C('evcp005',    'Eased votes summed, c votes too at every step for its OWN sheet (not eased); strength 0.05', 0.05, ease_c=0.0),
    C('evc005e50',  'As evc005 with ease 0.5 for the point and for c (a near point pulls the sheet half-way)', 0.05, ease_c=0.5, ease=0.5),
    C('evc005e70',  'As evc005 with ease 0.7 for the point and for c', 0.05, ease_c=0.7, ease=0.7),
    C('evc005e85',  'As evc005 with ease 0.85 for the point and for c', 0.05, ease_c=0.85, ease=0.85),
    E('evsum005e70', 'Eased votes (ease 0.7) summed with no decay, the flat page starts with strength 0.05', 0.05, gamma=1.0, ease=0.7),
    C('evc005p70',  'As evc005, the POINT eased 0.7, c eased fully', 0.05, ease_c=1.0, ease=0.7),
    C('evc005e70k4', 'As evc005e70, with c\'s vote counted four times', 0.05, ease_c=0.7, ease=0.7, kc=4.0),
    C('evc005e70k16', 'As evc005e70, with c\'s vote counted sixteen times', 0.05, ease_c=0.7, ease=0.7, kc=16.0),
]

s2 = lambda d: np.sin(2 * d)
RULES = [
    # --- the sheet turns by h(d) before the squaring
    T('ease',    'Sheet turns by d - sin(2d)/2: still when the point is near it, overtakes when the point is square to it', lambda d, x, y, z, k: d - 0.5 * s2(d)),
    T('over',    'Sheet turns by d + sin(2d)/2: overshoots a near point, comes to rest on a point square to it', lambda d, x, y, z, k: d + 0.5 * s2(d)),
    T('mirror',  'Sheet turns AWAY from the point by as much as the point is off (h = -d)', lambda d, x, y, z, k: -d),
    T('away50',  'Sheet turns away from the point by half as much as the point is off (h = -d/2)', lambda d, x, y, z, k: -0.5 * d),
    T('twice',   'Sheet overshoots: it turns twice as far as the point is off (h = 2d)', lambda d, x, y, z, k: 2 * d),
    T('over150', 'Sheet overshoots by half (h = 1.5 d)', lambda d, x, y, z, k: 1.5 * d),
    T('thrice',  'Sheet turns three times as far as the point is off (h = 3d)', lambda d, x, y, z, k: 3 * d),
    T('ease2',   'Sheet turns by d - sin(2d): turns away from a near point, overtakes a far one', lambda d, x, y, z, k: d - s2(d)),
    T('easehalf', 'Sheet turns by d - sin(2d)/4: follows a near point half-way', lambda d, x, y, z, k: d - 0.25 * s2(d)),
    T('snap45',  'Sheet stays unless the point is more than 45 degrees off; then it jumps to the point', lambda d, x, y, z, k: np.where(np.abs(d) > PI / 4, d, 0.0)),
    T('stick30', 'Sheet moves to the point only when the point is within 30 degrees of it', lambda d, x, y, z, k: np.where(np.abs(d) < PI / 6, d, 0.0)),
    # --- a lag that depends on where the point is
    lam_rule('lag60', 'Before each squaring the sheet moves 60% of the way to the point', lambda d, x, y, z, k: 0.6),
    lam_rule('lag67', 'Before each squaring the sheet moves two thirds of the way to the point', lambda d, x, y, z, k: 2.0 / 3.0),
    lam_rule('lag90', 'Before each squaring the sheet moves 90% of the way to the point', lambda d, x, y, z, k: 0.9),
    lam_rule('farfollow',  'Share = sin^2 d: the further the point is off the sheet, the more the sheet follows', lambda d, x, y, z, k: np.sin(d) ** 2),
    lam_rule('nearfollow', 'Share = cos^2 d: the sheet follows a near point and ignores a far one', lambda d, x, y, z, k: np.cos(d) ** 2),
    lam_rule('axfar',  'Share = (distance from the x-axis / length)^2: points far off the axis pull the sheet', lambda d, x, y, z, k: (y * y + z * z) / r2of(x, y, z)),
    lam_rule('axnear', 'Share = (x / length)^2: points near the axis pull the sheet', lambda d, x, y, z, k: x * x / r2of(x, y, z)),
    lam_rule('fade',   'Share halves each step (1/2, 1/4, 1/8, ...): the sheet settles', lambda d, x, y, z, k: 0.5 ** (k + 1)),
    lam_rule('mean',   'Share = 1/(k+2): the sheet is the plain average of the flat page and all points so far', lambda d, x, y, z, k: 1.0 / (k + 2)),
    lam_rule('wake',   'Share grows each step (0, 1/2, 3/4, 7/8, ...): the sheet stays at first and follows later', lambda d, x, y, z, k: 1.0 - 0.5 ** k),
    # --- votes weighted by the distance from the x-axis
    V('vote1',    'Votes (y^2-z^2, 2yz) summed, no decay, the flat page starts with strength 1', 1.0, 1.0),
    V('vote025',  'Votes summed, no decay, the flat page starts with strength 0.25', 0.25, 1.0),
    V('vote4',    'Votes summed, no decay, the flat page starts with strength 4', 4.0, 1.0),
    V('voted1',   'Votes summed, each step the old sum halves, the flat page starts with strength 1', 1.0, 0.5),
    V('voted4',   'Votes summed, each step the old sum halves, the flat page starts with strength 4', 4.0, 0.5),
    V('voten1',   'Votes over length^2 (direction only), summed, no decay, flat page strength 1', 1.0, 1.0, norm=True),
    V('votea1',   'Votes summed, no decay, strength 1; the point is squared BEFORE its own vote counts', 1.0, 1.0, after=True),
    # --- the sheet moved after the squaring
    M.Rule('after25', 'Square about the carried sheet, THEN move it a quarter of the way to the point', after(0.25), init1),
    M.Rule('after50', 'Square about the carried sheet, THEN move it half of the way to the point', after(0.5), init1),
    M.Rule('after75', 'Square about the carried sheet, THEN move it three quarters of the way to the point', after(0.75), init1),
    M.Rule('image50', 'Square about the carried sheet, then move it half-way to the sheet of the IMAGE (before c)', image(0.5), init1),
    M.Rule('image100', 'Square about the carried sheet, then the sheet becomes the sheet of the IMAGE (before c)', image(1.0), init1),
    M.Rule('peek100', 'Trial squaring about the carried sheet; the sheet becomes the trial image\'s sheet; square about that', image(1.0, peek=True), init1),
    M.Rule('peek50', 'Trial squaring; the sheet moves half-way to the trial image\'s sheet; square about that', image(0.5, peek=True), init1),
    # --- settling and waking
    M.Rule('settle1', 'First squaring about the point\'s own sheet; that sheet is kept for good', settle(1), init1),
    M.Rule('settle1h', 'First squaring about the sheet 40% of the way to the point; that sheet is kept for good', settle(1, 0.4), init1),
    M.Rule('settle3h', 'For three squarings the sheet moves 40% of the way to the point; then it stays for good', settle(3, 0.4), init1),
    M.Rule('late2', 'Two squarings about the flat page, every later one about the point\'s own sheet', late(2), init1),
    M.Rule('late3lag', 'Three squarings about the flat page, then the sheet moves half-way to the point each step', late(3, 0.5), init1),
    # --- c's own sheet in the mix
    M.Rule('cpull', 'Before each squaring the sheet moves half-way to c\'s own sheet (the point is not asked)', cmix(0.5, 0.0), init1),
    M.Rule('cpull25', 'Before each squaring the sheet moves a quarter of the way to c\'s own sheet', cmix(0.25, 0.0), init1),
    M.Rule('cmix', 'Before each squaring the sheet moves a quarter to c\'s sheet, then a quarter to the point\'s', cmix(0.25, 0.25), init1),
    M.Rule('bisect', 'The sheet half-way between this point\'s own sheet and the own sheet of the point before', bisect(), init1),
] + WAVE2


def get(name):
    for r in RULES + M.SCOUT:
        if r.name == name:
            return r
    return M.bench(name)

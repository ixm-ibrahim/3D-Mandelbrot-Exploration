"""Round 25, section "wall": the checks of W-a, W-d, W-e (numbers on the screen; nothing drawn).

    python out/r25/wall/check.py a      W-a: who treats every direction round the upright axis alike, and what each such
                                        rule does off the flat plane (nothing new / fold / crushed circle / tear / POLE)
    python out/r25/wall/check.py d      W-d: the count of special points of an evenly spaced doubling
    python out/r25/wall/check.py e      W-e: a point lifted above a meeting point: pushed away or held
    python out/r25/wall/check.py raw    the winding map without the "z == 0" shortcut: is the flat plane really kept?
"""
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, HERE)
for p in (('out', 'r24', 'me'), ('out', 'r23', 'me'), ('out', 'r25', 'me')):
    sys.path.insert(0, os.path.join(ROOT, *p))
import wall as W
M = W.M
import conefold, natural, cone as C, tri as T, mfold


def as_rule(F, name):
    return M.fixed(F, name, name)


def rules():
    return [
        M.fixed(W.P, 'one plane'),
        M.bench('twoplane'), M.bench('along'),
        M.fixed(natural.Q, 'quaternion square'),
        conefold.fold_rule(30.0, name='fold at 30 (r24)'),
        M.fixed(natural.fit, 'fitted inversion (r25)'),
        C.cone_rule(-C.T15, name='cone - (r23)'),
        mfold.rule(4, -0.2),
        T.tri_rule(name='triangle pillow (r24)'),
        M.fixed(W.ws(3, True), 'wind, square'),
        M.fixed(W.sw(3, True), 'square, wind'),
        M.fixed(W.ws(3, False), 'wind plain, square'),
    ]


def F3(rule, x, y, z, c=(0.0, 0.0, 0.0)):
    n = np.size(x); o = rule.step(np.asarray(x, float), np.asarray(y, float), np.asarray(z, float), tuple(rule.init(n)), 0,
                                  np.full(n, c[0]), np.full(n, c[1]), np.full(n, c[2]))
    return o[0], o[1], o[2]


def rotz(a, x, y, z):
    return np.cos(a) * x - np.sin(a) * y, np.sin(a) * x + np.cos(a) * y, z


# ---------------------------------------------------------------- W-a
def turn_test(rule, n=6000, seed=1):
    rng = np.random.default_rng(seed); v = rng.uniform(-1.5, 1.5, size=(3, n)); out = []
    X, Y, Z = F3(rule, *v); nrm = np.sqrt(X * X + Y * Y + Z * Z) + 1.0
    for deg in (37.0, 90.0, 120.0, 180.0):
        a = np.radians(deg); A = F3(rule, *rotz(a, *v)); B = rotz(2 * a, X, Y, Z)
        e = np.sqrt(sum((p - q) ** 2 for p, q in zip(A, B))) / nrm
        e = e[np.isfinite(e)]; out.append(float(np.percentile(e, 99)))
    return out


def profile(rule, n=500, top=2.6):
    """The rule seen in one upright half-plane (it is the same in all of them when the turn test holds)."""
    rho, z = np.meshgrid(np.linspace(0.012, top, n), np.linspace(0.006, top, n)); X, Y, Z = F3(rule, rho.ravel(), 0 * rho.ravel(), z.ravel())
    notwist = np.nanmax(np.abs(Y)) < 1e-9 * (np.nanmax(np.abs(X[np.isfinite(X)])) + 1e-300)
    # without a twist the image stays in the same upright plane, and its side of the upright axis has a sign:
    # a circle that passes over the axis shows as a change of that sign (a crushed circle), not as a fold
    R2 = (X if notwist else np.hypot(X, Y)).reshape(rho.shape); Z2 = Z.reshape(rho.shape); L = np.sqrt(R2 * R2 + Z2 * Z2)
    fin = np.isfinite(L) & (L < 1e3)
    d = rho[0, 1] - rho[0, 0]
    with np.errstate(all='ignore'):
        Rr, Rz = np.gradient(R2, d, axis=1), np.gradient(R2, d, axis=0); Zr, Zz = np.gradient(Z2, d, axis=1), np.gradient(Z2, d, axis=0)
        J = Rr * Zz - Rz * Zr
    lat = np.degrees(np.arctan2(z, rho)); body = fin & (lat < 80) & (lat > 1)
    okJ = body & np.isfinite(J)
    res = {}
    res['share of the half-plane where the picture is turned over (fold)'] = float((J[okJ] < 0).mean())
    # a jump: neighbours whose images are far apart compared with the grid step (a tear), away from poles
    jump = np.zeros_like(fin)
    step = np.hypot(np.diff(R2, axis=0), np.diff(Z2, axis=0)); big = step > 60 * d * (1 + L[1:] + L[:-1])
    jump[1:] |= big & fin[1:] & fin[:-1]
    res['share with a jump between neighbours (tear)'] = float(jump[body].mean())
    # crushed circle: an off-axis circle sent onto the upright axis (rho' = 0 with the height not 0), or |J| -> 0 without changing sign
    sr = np.sign(R2); cr = np.zeros_like(fin); cr[1:] |= (sr[1:] * sr[:-1] < 0) & fin[1:] & fin[:-1] & ~jump[1:]
    res['columns with a circle that passes over the upright axis (crushed circle)'] = int((cr & body).any(0).sum())
    # poles: far images of near points
    res['near points sent beyond 1000 (poles)'] = int((~fin).sum())
    # off-plane points sent INTO the flat plane: sign changes of the image height going up
    s = np.sign(Z2); ch = (s[1:] * s[:-1] < 0) & fin[1:] & fin[:-1] & ~jump[1:]
    res['columns (of %d) with an off-plane point sent into the flat plane' % n] = int(ch.any(0).sum())
    if ch.any():
        ii, jj = np.nonzero(ch); res['  such points: latitude from / to'] = (float(lat[ii, jj].min()), float(lat[ii, jj].max()))
        res['  such points: distance from 0 from / to'] = (float(np.hypot(rho, z)[ii, jj].min()), float(np.hypot(rho, z)[ii, jj].max()))
    return res


def verdict(res):
    k = list(res.keys()); fold, tear, crush, poles, new = res[k[0]], res[k[1]], res[k[2]], res[k[3]], res[k[4]]
    out = []
    if fold > 0.002: out.append('FOLD')
    if tear > 0.0005: out.append('TEAR')
    if crush > 3: out.append('CRUSHED CIRCLE')
    if poles > 0: out.append('POLE')
    if not out: out.append('nothing of the four')
    out.append('new copies of the flat plane' if new > 3 else 'NO new copy of the flat plane')
    return ', '.join(out)


def check_a():
    print('W-a. Turn test: turn the point by a about the upright axis; the square should turn by 2a.')
    print('     (99th percentile of the miss, relative; four angles 37, 90, 120, 180)')
    for r in rules():
        t = turn_test(r); alike = max(t) < 1e-6
        print('\n%-26s turn miss %s  -> %s' % (r.name, ' '.join('%.1e' % e for e in t), 'treats every direction alike' if alike else 'does NOT (has special upright half-planes or an axis)'))
        if alike:
            res = profile(r)
            for k, v in res.items():
                print('      %-74s %s' % (k, ('%.4f' % v) if isinstance(v, float) else v))
            print('      => ' + verdict(res))
        sys.stdout.flush()
    # the homogeneous special case: is the rule "length squared times a map of directions"?
    print('\nIs the rule "length squared times a map of directions"? (F(2v) against 4 F(v), worst relative miss)')
    rng = np.random.default_rng(2); v = rng.uniform(-0.7, 0.7, size=(3, 4000))
    for r in rules():
        A = F3(r, *(2 * v)); B = F3(r, *v); e = np.sqrt(sum((p - 4 * q) ** 2 for p, q in zip(A, B))) / (np.sqrt(sum(q * q for q in B)) * 4 + 1e-12)
        e = e[np.isfinite(e)]; print('   %-26s %.1e' % (r.name, float(np.percentile(e, 99))))


# ---------------------------------------------------------------- W-d
def check_d():
    print('W-d. An evenly spaced doubling of a closed surface needs a flat pattern with corners (corner k = 1/k of a full turn).')
    print('     Ball-like surface: sum over corners of (1 - 1/k) must be exactly 2. All solutions with k from 2 to 60 (and "inf" = a point at infinite distance):')
    from fractions import Fraction as Fr
    sols = set()
    ks = list(range(2, 61)) + ['inf']
    val = lambda k: Fr(1) if k == 'inf' else 1 - Fr(1, k)

    def rec(start, left, acc):
        if left == 0:
            sols.add(tuple(acc)); return
        if left < 0 or len(acc) >= 4:
            return
        for i in range(start, len(ks)):
            v = val(ks[i])
            if v <= left:
                rec(i, left - v, acc + [ks[i]])
    rec(0, Fr(2), [])
    for s in sorted(sols, key=lambda t: (len(t), str(t))):
        print('     corners', s)
    print('     Doughnut: the sum must be 0: no corner at all. So a ball-like surface needs 2 points at infinite distance (the two')
    print('     ends of the upright axis: that is the one-plane rule, whose buds sit only round the belt), or 3 or 4 corners.')
    print('     Branched covering of a ball-like surface by itself, d times, no fold: 2d - 2 branch points (d = 4: six).')


# ---------------------------------------------------------------- W-e
def check_e():
    print('W-e. A point lifted straight up from a meeting point of the flat picture.')
    print('     "local" = height after one step / height before, for a lift of 1e-7, next to the flat rule\'s own stretch there.')
    print('     "held"  = share of 80 lifts between 0.002 and 0.5 that still have not left after 80 steps (0 = bodies stay apart).')
    sets = [('c = -1', (-1.0, 0.0, 0.0)), ('rabbit', M.RABBIT), ('c = -0.75', (-0.75, 0.0, 0.0))]
    hs = np.geomspace(0.002, 0.5, 80)
    rs = rules() + [W.RULES['zooA'](), W.RULES['zooB']()]
    print('\n%-26s' % 'rule' + ''.join('%-34s' % s[0] for s in sets))
    for r in rs:
        row = '%-26s' % r.name
        for nm, c in sets:
            cc = complex(c[0], c[1]); al = (1 - np.sqrt(1 - 4 * cc)) / 2
            X, Y, Z = F3(r, np.array([al.real]), np.array([al.imag]), np.array([1e-7]), c)
            loc = float(Z[0] / 1e-7)
            n = M.stay(r, np.full(hs.size, al.real), np.full(hs.size, al.imag), hs, c[0], c[1], c[2], 80)
            held = float((n >= 80).mean())
            row += 'local %5.2f (flat %4.2f) held %4.2f   ' % (loc, abs(2 * al), held)
        print(row); sys.stdout.flush()
    print('\nPush all round the flat circle at small and at finite lifts (image latitude / latitude; plain doubling near the plane = 2):')
    lon = np.radians(np.arange(0.5, 360, 1.0))
    for r in rules():
        row = '   %-26s' % r.name
        for lat_deg in (0.01, 5.0, 15.0):
            la = np.radians(lat_deg); X, Y, Z = F3(r, np.cos(la) * np.cos(lon), np.cos(la) * np.sin(lon), np.sin(la) + 0 * lon)
            p = np.arcsin(np.clip(Z / np.sqrt(X * X + Y * Y + Z * Z), -1, 1)) / la; p = p[np.isfinite(p)]
            row += ' lift %5.2f deg: %6.2f .. %6.2f |' % (lat_deg, p.min(), p.max())
        print(row); sys.stdout.flush()


def check_raw():
    rng = np.random.default_rng(3); n = 20000; x, y = rng.uniform(-2, 2, n), rng.uniform(-2, 2, n)
    for shaped in (True, False):
        for h in (0.0, 1e-9, 1e-6):
            rho = np.hypot(x, y); zeta = rho + 1j * h; u = (zeta - 1) / (zeta + 1); R = np.abs(u); th = np.angle(u)
            s = 3 * th - (np.sin(2 * th) if shaped else 0.0); u2 = R * np.exp(1j * s); z2 = (1 + u2) / (1 - u2)
            print('wind %s, height %.0e: the flat distance moves by at most %.1e, the height becomes at most %.1e (height ratio %.3f .. %.3f)'
                  % ('3s - sin 2s' if shaped else '3s', h, float(np.abs(z2.real - rho).max()), float(np.abs(z2.imag).max()),
                     float((z2.imag / h).min()) if h > 0 else 0, float((z2.imag / h).max()) if h > 0 else 0))


if __name__ == '__main__':
    a = sys.argv[1] if len(sys.argv) > 1 else 'a'
    {'a': check_a, 'd': check_d, 'e': check_e, 'raw': check_raw}[a]()

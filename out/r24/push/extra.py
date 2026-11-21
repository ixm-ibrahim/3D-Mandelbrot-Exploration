"""Round 24, section "push": the extra rules of parts 3 and 4, and numbers about a direction map.

    import extra as E;  E.get('m6belt')  /  E.get('face:m6')         (a library rule; names below)
    python out/r24/push/extra.py                                     evenness, fold, copies of every candidate

Part 3 (even push with copies):
    mbelt(m, t, mu0, mu1)   the m-fold map of the scout with an EXACT belt: plain doubling for |Mercator latitude| <= mu0,
                            the scout's R (copy laid m - 2 times round) from mu1 on, the scout's own blend between.
    weld(mua)               round 23's welded cones with the exact belt up to Mercator latitude mua (0.2 = round 23's best).
    true(L0)                NO copies: plain doubling of the longitude, and the LIFT ITSELF doubled (not its Mercator
                            latitude) up to L0 degrees; above, it runs on like one plane. The reference "evenest push".
Part 4 (looks at c):
    face:<name>             the pattern of <name> turned so that its longitude 0 faces the flat fixed point of c.
"""
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import plib as P
M = P.M
sys.path.insert(0, os.path.join(P.ROOT, 'out', 'r23', 'cone'))
import conelib as CL


def mbelt(m, t, mu0, mu1):
    def G(x, y, z):
        r = np.sqrt(x * x + y * y + z * z); rs = np.where(r > 0, r, 1.0)
        Zs = np.clip(z / rs, -1 + 1e-15, 1 - 1e-15); mu = np.arctanh(Zs); north = z > 0
        den = np.where(north, rs + z, rs - z); den = np.where(den > 0, den, 1.0)
        s = (x + 1j * np.where(north, -y, y)) / den
        sm = s ** m; sm2 = s ** (m - 2)
        N = np.where(north, sm2 * (1 + t * sm), sm + t); D = np.where(north, sm + t, sm2 * (1 + t * sm))
        inb = np.abs(mu) < mu1
        if inb.any():
            sa = np.where(inb, s, 1.0); w = np.where(north, 1.0 / np.where(np.abs(sa) > 0, sa, 1.0), sa)
            q = np.clip((np.abs(mu) - mu0) / (mu1 - mu0), 0, 1); chi = q * q * q * (10 - 15 * q + 6 * q * q)
            wm = w ** m
            W = w * w * np.exp(chi * (np.log(1 + t / wm) - np.log(1 + t * wm)))
            N = np.where(inb, W, N); D = np.where(inb, 1.0 + 0j, D)
        n2, d2 = np.abs(N) ** 2, np.abs(D) ** 2; tot = n2 + d2; tot = np.where(tot > 0, tot, 1.0)
        xy = 2 * N * np.conj(D) / tot
        return xy.real, xy.imag, (n2 - d2) / tot
    return G


def weld(mua, theta=np.pi / 2):
    QS = 0.59087; mub = mua + (CL.MU60 / 3 - mua) / QS
    return lambda x, y, z: CL.weld_dir(x, y, z, theta, mua, mub, 1.0, 5)


def true(L0=30.0, w=8.0):
    """Lift doubled exactly up to L0 - w degrees; from L0 + w on the Mercator latitude runs on with slope 2 (as one plane)."""
    lat = np.radians(np.linspace(0, 89.999, 20001)); mu = np.arctanh(np.sin(lat))
    s_true = 2 * np.cos(lat) / np.maximum(np.cos(2 * lat), 1e-3)            # d mu' / d mu for lift doubling
    q = np.clip((np.degrees(lat) - (L0 - w)) / (2 * w), 0, 1); chi = q * q * (3 - 2 * q)
    slope = (1 - chi) * np.where(np.degrees(lat) < L0 + w, s_true, 2.0) + chi * 2.0
    mup = np.concatenate([[0.0], np.cumsum(0.5 * (slope[1:] + slope[:-1]) * np.diff(mu))])

    def G(x, y, z):
        r = np.sqrt(x * x + y * y + z * z); rs = np.where(r > 0, r, 1.0)
        m = np.arctanh(np.clip(np.abs(z) / rs, 0, 1 - 1e-15)); lam = np.arctan2(y, x)
        a = np.where(m <= mu[-1], np.interp(m, mu, mup), mup[-1] + 2 * (m - mu[-1])); a = np.minimum(a, 60.0)
        return np.cos(2 * lam) / np.cosh(a), np.sin(2 * lam) / np.cosh(a), np.where(z < 0, -1.0, 1.0) * np.tanh(a)
    return G


CAND = {
    'weld0': (weld(0.0), 'welded cones, no exact belt'),
    'weld3': (weld(0.3), 'welded cones, exact belt to 17 degrees'),
    'weld4': (weld(0.4), 'welded cones, exact belt to 22 degrees'),
    'v2belt': (mbelt(3, -P.T15, 0.3, 0.9), 'second version with an exact belt to 17 degrees, blend to 46'),
    'm4belt': (mbelt(4, -0.05, 0.3, 0.9), 'copy twice round, dial -0.05, exact belt to 17 degrees'),
    'm6belt': (mbelt(6, -0.02, 0.3, 0.9), 'copy four times round, dial -0.02, exact belt to 17 degrees'),
    'm6s': (P.mdir(6, -0.03), 'copy four times round, dial -0.03'),
    'm8s': (P.mdir(8, -0.02), 'copy six times round, dial -0.02'),
    'm8': (P.mdir(8, -0.10), 'copy six times round, dial -0.10'),
    'true30': (true(30.0), 'no copies: the lift itself doubled up to 30 degrees'),
}
for _k, (_g, _l) in CAND.items():
    P.add(_k, _g, _l)


def get(name):
    if name.startswith('face:'):
        base = name[5:]
        return P.facing_rule(P.DIRS[base], name, P.LABEL[base] + ', turned to face the meeting point of each c')
    return P.rule(name)


def evenness(G):
    """Push relative to plain doubling, all round, at lifts 8 / 15 / 25: (weakest, strongest) for each lift."""
    lons = np.arange(0, 360, 2.0); out = []
    for L in (8.0, 15.0, 25.0):
        p = P.push(G, lons, L) / P.push(P.one_dir, lons, L); out.append((float(p.min()), float(p.max()), float(lons[int(np.argmin(p))])))
    return out


def copies(G, n=600):
    """How many times the directions are laid over each other (signed and unsigned), the folded share, and the lowest
    latitude at which a northern direction is laid back onto the flat circle (the copy)."""
    o, (lat, lon, g, s1, s2, det) = CL.numbers(G, n=n, quiet=True)
    zi = g[..., 2]; nh = lat > np.radians(2.0); lo = 90.0
    for j in range(0, len(lon), 8):
        col = zi[nh, j]; k = np.nonzero(np.sign(col[1:]) != np.sign(col[:-1]))[0]
        if k.size:
            lo = min(lo, float(np.degrees(lat[nh][k[0]])))
    return dict(covers=o['covers'], unsigned=o['covers_unsigned'], folded=o['folded_share'], copy_lat=lo, squeeze_over_2=o['share_ratio_over_2'], squeeze_over_4=o['share_ratio_over_4'])


if __name__ == '__main__':
    names = sys.argv[1].split(',') if len(sys.argv) > 1 else ['one', 'v1', 'v2', 'm4', 'm4b', 'm6', 'cones', 'tri'] + list(CAND)
    print('push relative to plain doubling (weakest .. strongest all round) at lifts 8 | 15 | 25; then the copies')
    for nm in names:
        G = P.DIRS[nm]; e = evenness(G); c = copies(G)
        r = get(nm); f = M.flat_check(r, n=6000, steps=60)
        print('%-8s %.2f..%.2f | %.2f..%.2f | %.2f..%.2f (weakest at %3.0f) | laid over %.2f times (unsigned %.2f), folded %.4f, lowest copy at latitude %4.1f, squeezed >2: %.2f, >4: %.2f | flat differ %d  %s'
              % (nm, e[0][0], e[0][1], e[1][0], e[1][1], e[2][0], e[2][1], e[2][2], c['covers'], c['unsigned'], c['folded'], c['copy_lat'], c['squeeze_over_2'], c['squeeze_over_4'],
                 f['mandelbrot'] + f['basilica'] + f['rabbit'] + f['siegel'], P.LABEL[nm])); sys.stdout.flush()

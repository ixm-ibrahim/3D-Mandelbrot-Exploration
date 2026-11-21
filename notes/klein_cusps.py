"""Cusps of the Maskit family used by the lab's Kleinian view.

The family: a(q) = mu + 1/q, b(q) = q + 2.  The trace of the word that belongs to the fraction p/q is a
polynomial in mu, built by the Farey recursion

    T(0/1) = -i mu,   T(1/0) = 2,   T(1/1) = -i mu + 2i,
    T((p+r)/(q+s)) = T(p/q) T(r/s) - T((p-r)/(q-s)).

The p/q cusp is the root of T(p/q) = 2 that lies on the boundary of the family. It is found by Newton's
method started midway between the cusps of the two Farey parents.

Run:  python notes/klein_cusps.py            prints the checks and a table
Import: cusp(p, q) -> complex
"""
import cmath, math, sys
from functools import lru_cache


def trace(p, q, mu):
    """T(p/q)(mu) and its derivative, for 0 <= p/q <= 1, by walking down the Farey tree."""
    if (p, q) == (0, 1):
        return -1j * mu, -1j
    if (p, q) == (1, 1):
        return -1j * mu + 2j, -1j
    # left = a/b, right = c/d, and `far` = the fraction (c-a)/(d-b) that the recursion subtracts
    a, b, c, d = 0, 1, 1, 1
    tl, dl = -1j * mu, -1j
    tr, dr = -1j * mu + 2j, -1j
    tf, df = 2.0 + 0j, 0j
    while True:
        m, n = a + c, b + d
        tm, dm = tl * tr - tf, dl * tr + tl * dr - df
        if (m, n) == (p, q):
            return tm, dm
        if p * n < m * q:        # target is left of the mediant: the mediant becomes the right end
            tf, df = tr, dr
            c, d, tr, dr = m, n, tm, dm
        else:
            tf, df = tl, dl
            a, b, tl, dl = m, n, tm, dm


def parents(p, q):
    a, b, c, d = 0, 1, 1, 1
    while True:
        m, n = a + c, b + d
        if (m, n) == (p, q):
            return (a, b), (c, d)
        if p * n < m * q:
            c, d = m, n
        else:
            a, b = m, n


@lru_cache(maxsize=None)
def cusp(p, q):
    """mu of the p/q cusp, 0 <= p/q <= 1 (use cusp_any for other fractions)."""
    g = math.gcd(p, q)
    p, q = p // g, q // g
    if (p, q) == (0, 1):
        return 2j
    if (p, q) == (1, 1):
        return 2 + 2j
    (a, b), (c, d) = parents(p, q)
    mu = 0.5 * (cusp(a, b) + cusp(c, d))
    for _ in range(200):
        t, dt = trace(p, q, mu)
        step = (t - 2) / dt
        mu -= step
        if abs(step) < 1e-15:
            break
    else:
        raise RuntimeError("Newton did not settle for %d/%d" % (p, q))
    return mu


def cusp_any(p, q):
    """The family repeats under mu -> mu + 2 (p/q -> p/q + 1); fold any fraction into [0, 1]."""
    k = math.floor(p / q)
    return cusp(p - k * q, q) + 2 * k


def farey(max_q):
    out = set()
    for q in range(1, max_q + 1):
        for p in range(0, q + 1):
            if math.gcd(p, q) == 1:
                out.add((p, q))
    return sorted(out, key=lambda f: f[0] / f[1])


def main():
    known = {(0, 1): 2j, (1, 1): 2 + 2j, (1, 2): 1 + math.sqrt(3) * 1j}
    print("check against the known values")
    for (p, q), want in known.items():
        got = cusp(p, q)
        print("  mu(%d/%d) = %.12f %+.12fi   error %.1e" % (p, q, got.real, got.imag, abs(got - want)))
        assert abs(got - want) < 1e-12
    print("\ncusps with denominator up to 8 (Re mu grows with p/q; mu(1 - p/q) = 2 - conj(mu(p/q)))")
    last = -1.0
    for p, q in farey(8):
        m = cusp(p, q)
        t, _ = trace(p, q, m)
        mirror = cusp(q - p, q)
        ok_m = abs((2 - m.conjugate()) - mirror) < 1e-9
        flag = "" if (m.real > last and ok_m) else "   <-- ORDER OR MIRROR BROKEN"
        last = m.real
        print("  %d/%-2d  mu = %.10f %+.10fi   |T-2| = %.1e%s" % (p, q, m.real, m.imag, abs(t - 2), flag))
    print("\na few long ones")
    for p, q in [(1, 10), (1, 15), (2, 15), (3, 10), (2, 21), (5, 13), (8, 21), (13, 34), (21, 55), (34, 89)]:
        m = cusp(p, q)
        print("  %d/%-2d  mu = %.10f %+.10fi" % (p, q, m.real, m.imag))


if __name__ == "__main__":
    main()

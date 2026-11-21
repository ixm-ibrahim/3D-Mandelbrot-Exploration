"""Round 24 scout, part 1: what the direction map R_t does to DIRECTIONS alone, for t > 0 and t < 0.

    R_t(w) = (w^3 + t) / (w (1 + t w^3))        w = stereographic coordinate, |w| = 1 the flat plane's circle

Questions: (1) is there a direction that pulls its neighbours in (an attracting cycle)?  (2) where do the six
branch directions go?  (3) how fast are neighbouring directions pulled apart on average, and how unevenly?

    python out/r24/me/dirs.py
"""
import numpy as np


def R(w, t):
    w3 = w * w * w
    return (w3 + t) / (w * (1 + t * w3))


def dR(w, t, h=1e-6):
    return (R(w + h, t) - R(w - h, t)) / (2 * h)


def sph_deriv(w, t):
    """|R'| measured on the round sphere (stretch of directions)."""
    Rw = R(w, t)
    return np.abs(dR(w, t)) * (1 + np.abs(w) ** 2) / (1 + np.abs(Rw) ** 2)


def crit(t):
    """The six branch directions: t u^2 - (2 - 4 t^2) u + t = 0, u = w^3."""
    u = np.roots([t, -(2 - 4 * t * t), t]).astype(complex)
    out = []
    for uu in u:
        r = np.abs(uu) ** (1 / 3); a = np.angle(uu) / 3
        out += [r * np.exp(1j * (a + 2 * np.pi * k / 3)) for k in range(3)]
    return np.array(out)


def lat(w):
    return np.degrees(2 * np.arctan(np.abs(w)) - np.pi / 2)


def lon(w):
    return np.degrees(np.angle(w))


def circle_map(th, t):
    """R_t on the flat plane's circle, as a map of the angle (degrees in, degrees out)."""
    return np.degrees(np.angle(R(np.exp(1j * np.radians(th)), t))) % 360


def main():
    for t in (0.2679, 0.5, -0.1, -0.2679, -0.4, -0.5):
        print('\n== t = %+.4f' % t)
        c = crit(t)
        print('   branch directions (lat, lon):', ', '.join('(%.1f, %.0f)' % (lat(x), lon(x)) for x in c))
        v = R(c, t)
        print('   sent to           (lat, lon):', ', '.join('(%.1f, %.0f)' % (lat(x), lon(x)) for x in v))
        # follow them
        w = v.copy(); hist = []
        for n in range(400):
            w = R(w, t)
            if n >= 396:
                hist.append(w.copy())
        print('   after 400 steps   (lat, lon):', ', '.join('(%.1f, %.0f)' % (lat(x), lon(x)) for x in hist[-1]))
        # stretch at the fixed direction +x and on the circle
        th = np.linspace(0, 360, 3601)[:-1]; w = np.exp(1j * np.radians(th))
        s = sph_deriv(w, t)
        print('   stretch along the flat circle: min %.3f at %.0f deg, max %.3f at %.0f deg (plain doubling: 2 everywhere)'
              % (s.min(), th[s.argmin()], s.max(), th[s.argmax()]))
        print('   +x is sent to lon %.1f; stretch there %.3f %s' % (lon(R(1 + 0j, t)), sph_deriv(1 + 0j, t), '(pulls neighbours IN)' if sph_deriv(1 + 0j, t) < 1 else '(pushes neighbours away)'))
        # random directions: where do they end, and the average growth rate
        rng = np.random.default_rng(3); p = rng.normal(size=(3, 20000)); p /= np.sqrt((p * p).sum(0))
        w = (p[0] + 1j * p[1]) / (1 - p[2]); acc = np.zeros(w.shape)
        for n in range(300):
            acc += np.log(sph_deriv(w, t)); w = R(w, t)
            big = np.abs(w) > 1e6; w = np.where(big, 1e6 * w / np.abs(w), w)
        lam = acc / 300
        print('   20000 random directions, 300 steps: average growth per step exp(%.3f) = %.3f; share that are pulled together (rate < 0): %.3f; share ending within 2 deg of +x: %.3f'
              % (np.nanmean(lam), np.exp(np.nanmean(lam)), float((lam < 0).mean()), float((np.abs(w - 1) < 0.035).mean())))
        print('   spread of the growth rate over directions (5..95 %%): %.3f .. %.3f' % (np.exp(np.nanpercentile(lam, 5)), np.exp(np.nanpercentile(lam, 95))))


if __name__ == '__main__':
    main()

"""Round 20, section profiles (prefix w_): forms of "wind, then square".

    F(v) = P(T(v)),  T: (x, rho, a) -> (x, rho, g(a)),  P = the one-plane rule (out/me/r16/scout.py oneplane)
    a = turn of the point round the x-axis from the flat plane, rho = distance from the x-axis.

Every g here is built the same way. The planes sit at a = m * 180/k degrees (m whole); d = a - (nearest plane);
    g(a) = m * 180 + sign(d) * h(|d|),   h: [0, S] -> [0, 90 degrees],  S = 90/k degrees (half a sector)
    h(d) = d            for d <= w          (the exact band: T is a plain turn there)
    h(d) = ramp         for w <= d <= S     (slope 1 at d = w, rising to its peak half way between the planes)
so g(a) = a exactly within w of the flat plane, and g is "a plus a fixed turn" within w of each copy plane.

Ramp shapes:
  'sin'    slope = 1 + A sin^2(...)   smooth (g twice differentiable). w = 0 is exactly the orchestrator's m_w3.
  'line'   slope = 1 + A/2, constant  (a crease in g at the band edge; the lowest peak a band of width w allows)
A is fixed by the rise: the ramp must take the angle from w to 90 degrees.
"""
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, 'out', 'me', 'r16'))
import scout as S


def profile(k, w_deg, ramp='sin'):
    Sh = np.pi / (2 * k); w = np.radians(w_deg); A = 2 * (np.pi / 2 - Sh) / (Sh - w)

    def h(d):
        t = np.clip(d - w, 0.0, None)
        if ramp == 'sin':
            r = t + A * (t / 2 - (Sh - w) / (2 * np.pi) * np.sin(np.pi * t / (Sh - w)))
        elif ramp == 'line':
            r = (1 + A / 2) * t
        else:
            raise ValueError(ramp)
        return np.minimum(d, w) + r

    def g(a):
        m = np.round(a / (2 * Sh)); d = a - m * 2 * Sh
        return m * np.pi + np.sign(d) * h(np.abs(d))

    def slope(a):
        m = np.round(a / (2 * Sh)); d = np.abs(a - m * 2 * Sh); t = np.clip(d - w, 0.0, None)
        if ramp == 'sin':
            return np.where(d <= w, 1.0, 1 + A * np.sin(np.pi * t / (2 * (Sh - w))) ** 2)
        return np.where(d <= w, 1.0, 1 + A / 2)
    g.slope = slope; g.peak = 1 + (A if ramp == 'sin' else A / 2)
    return g


def wind(g):
    def F(x, y, z):
        x, y, z = (np.asarray(t, float) for t in (x, y, z))
        rho = np.hypot(y, z); ga = g(np.arctan2(z, y))
        return S.oneplane(x, rho * np.cos(ga), rho * np.sin(ga))
    F.g = g
    return F


RULES = {
    'w_b05': (wind(profile(3, 5)),  'Wind 3 times, exact band 5 degrees round each plane, smooth ramp', ''),
    'w_b10': (wind(profile(3, 10)), 'Wind 3 times, exact band 10 degrees, smooth ramp', ''),
    'w_b15': (wind(profile(3, 15)), 'Wind 3 times, exact band 15 degrees, smooth ramp', ''),
    'w_b20': (wind(profile(3, 20)), 'Wind 3 times, exact band 20 degrees, smooth ramp', ''),
    'w_b25': (wind(profile(3, 25)), 'Wind 3 times, exact band 25 degrees, smooth ramp', ''),
    'w_c10': (wind(profile(3, 10, 'line')), 'Wind 3 times, exact band 10 degrees, straight ramp (crease)', ''),
    'w_c15': (wind(profile(3, 15, 'line')), 'Wind 3 times, exact band 15 degrees, straight ramp (crease)', ''),
    'w_s0':  (wind(profile(3, 0)),  'Wind 3 times, no band (must equal m_w3)', ''),
    'w_5b05': (wind(profile(5, 5)), 'Wind 5 times, exact band 5 degrees, smooth ramp', ''),
}


def profile_round(k, w_deg, e_deg):
    """The straight ramp with its corner rounded: slope 1 up to w - e, a smooth rise over w - e .. w + e, then the same
    constant slope as the straight ramp of band w (the rise is symmetric about w, so the total turn is unchanged)."""
    Sh = np.pi / (2 * k); w = np.radians(w_deg); e = np.radians(e_deg); B_ = (np.pi / 2 - Sh) / (Sh - w)     # plateau slope = 1 + B_

    def h(d):
        t = np.clip(d - (w - e), 0.0, 2 * e)
        rise = B_ * (t / 2 - e / np.pi * np.sin(np.pi * t / (2 * e)))          # integral of B_ sin^2(pi t / (4 e))
        return d + rise + B_ * np.clip(d - (w + e), 0.0, None)

    def g(a):
        m = np.round(a / (2 * Sh)); d = a - m * 2 * Sh
        return m * np.pi + np.sign(d) * h(np.abs(d))
    g.peak = 1 + B_
    return g


RULES['w_c15r'] = (wind(profile_round(3, 15, 3)), 'Wind 3 times, band 15 degrees, straight ramp with the corner rounded over 3 degrees each side', '')

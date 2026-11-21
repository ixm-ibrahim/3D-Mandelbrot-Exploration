"""Orchestrator's own trial rules of round 19 (prefix m_w). Loaded by the bench's registry hook.

WIND, THEN SQUARE. Every earlier many-plane rule (two planes, along, away and their relatives) gives each of its
planes its own arithmetic: a point in the upright plane is squared inside the upright plane. That only fits
together when c lies on the x-axis (claim C1, round 17), which is why every one of them breaks for the rabbit.

Here the other planes have no arithmetic of their own. The turn of a point round the x-axis is first multiplied
(wound) by a whole odd number k, and then the one-plane rule is applied, with nothing turned back:

    F(v) = P(T(v)),   T: (x, rho, a) -> (x, rho, g(a)),   a = turn round the x-axis from the flat plane,
    g(a) = k a - (k - 1) sin(2 k a) / (2 k)        (slope exactly 1 wherever g(a) is a multiple of 180 degrees)

k must be odd for the flat plane to stay exact (both halves of the flat plane must be sent to themselves); k = 1 is
the one-plane rule; k = 3 is the first new one. The half-planes at a = 60, 120, ... degrees are sent INTO the flat
plane, so for every c in the flat plane (on the x-axis or not) they carry exact copies of the flat picture.
"""
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, 'out', 'me', 'r16'))
import scout as S


def wind(k, profile='sin'):
    def g(a):
        if profile == 'lin':
            return k * a
        if profile == 'sin':                      # slope 1 at the copy planes, k on average, 2k - 1 half way
            return k * a - (k - 1) * np.sin(2 * k * a) / (2 * k)
        if profile == 'flat':                     # slope 1 and curvature 0 at the copy planes (wider round band)
            c = (k - 1) / 1.5
            return k * a - c * (2 * np.sin(2 * k * a) / (2 * k) - 0.5 * np.sin(4 * k * a) / (4 * k))
        if profile == 'saw':                      # each wedge turned whole onto the flat wedge: a tear half way, no ramp
            w = np.pi / k
            j = np.round(a / w)
            return (a - j * w) + j * np.pi
        if profile.startswith('band'):            # g = a exactly within b degrees of each copy plane, smooth ramp between
            b = np.radians(float(profile[4:])); w = np.pi / k
            j = np.round(a / w); d = a - j * w          # d in [-w/2, w/2]
            L = w / 2 - b                                # half of the ramp between two bands
            t = np.clip((np.abs(d) - b) / L, 0.0, 1.0)   # 0 at the band edge, 1 half way
            extra = (np.pi - w) / 2                      # what the ramp must add on each side of half way
            ramp = extra * (t - np.sin(np.pi * t) / np.pi)   # slope 0 at both ends... rises to extra at t = 1
            return j * np.pi + d + np.sign(d) * ramp
        raise ValueError(profile)

    def F(x, y, z):
        x, y, z = (np.asarray(t, float) for t in (x, y, z))
        rho = np.hypot(y, z)
        a = np.arctan2(z, y)
        ga = g(a)
        return S.oneplane(x, rho * np.cos(ga), rho * np.sin(ga))
    return F


RULES = {
    'm_w3':    (wind(3, 'sin'),  'Wind three times round the x-axis, then one plane', ''),
    'm_w3lin': (wind(3, 'lin'),  'Wind three times, evenly (no round band)', ''),
    'm_w3f':   (wind(3, 'flat'), 'Wind three times, wider round band', ''),
    'm_w5':    (wind(5, 'sin'),  'Wind five times round the x-axis, then one plane', ''),
    'm_w3saw': (wind(3, 'saw'),  'Three planes, each wedge turned whole onto the flat plane (tear half way)', ''),
    'm_w3b20': (wind(3, 'band20'), 'Wind three times, untouched within 20 degrees of each plane', ''),
    'm_w3b25': (wind(3, 'band25'), 'Wind three times, untouched within 25 degrees of each plane', ''),
}

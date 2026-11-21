"""Round 20, entry: the rule in Python (numpy), written from the formula, for comparing with the page's MATH.windsq
and for the stretch numbers. wn(n) is the power n: wind k times, then the one-plane power n."""
import numpy as np


def kof(n):
    m = max(1, int(np.floor(abs(n) + 0.5)))
    return m if m % 2 else m + 1


def oneplane(x, y, z, n):
    r = np.sqrt(x * x + y * y + z * z)
    Z = np.clip(z / np.maximum(r, 1e-300), -0.999999, 0.999999)
    m = np.clip(n * np.arctanh(Z), -20, 20); p = n * np.arctan2(y, x); R = r ** n
    return R * np.cos(p) / np.cosh(m), R * np.sin(p) / np.cosh(m), R * np.tanh(m)


def g(a, k):
    return k * a - (k - 1) * np.sin(2 * k * a) / (2 * k)


def wn(n):
    k = kof(n)

    def F(x, y, z):
        x, y, z = (np.asarray(t, float) for t in (x, y, z))
        rho = np.hypot(y, z); ga = g(np.arctan2(z, y), k)
        return oneplane(x, rho * np.cos(ga), rho * np.sin(ga), n)
    return F

"""Round 17, section "hunter" (prefix h_). Stand-alone numpy.

ONE rule is registered, and only so that the basilica screen (closecut) can be run on it. It came out of the hunt for
a counterexample to claim C3; its Mandelbrot solid was looked at under the hunt's licence, NOT because its basilica
had passed. It has not been through stage 1.

h_ud55, "one plane near the flat plane, lathe about the upright axis elsewhere":
    within 15 degrees of the flat plane z = 0:  the one-plane square P (so the cut z = 0 is exact and keeps angles);
    within 55 degrees of the z-axis:            the lathe about the z-axis, sign chosen so that both mirrors hold,
                                                 lower cone +Lz, upper cone -Lz,  Lz = (2 z x, 2 z y, z^2 - x^2 - y^2);
    between (55 to 75 degrees from the z-axis): the two answers blended on the sphere of directions, infinitely smooth.
On the z-axis it is t -> -t |t| (a point goes to the other side); at (0, 0, +-1/2) the derivative is -identity.
The two angles 55 and 75 are free choices (a dial); the probe in probe.py says 30 / 50 leaves dust at the touching
point and 55 / 75 does not.
"""
import numpy as np

EPS = 1e-300


def _g(t):
    return np.where(t > 0, np.exp(-1.0 / np.maximum(t, 1e-12)), 0.0)


def make(b1, b2):
    """Lathe about the z-axis within b1 degrees of it, one-plane square beyond b2 degrees, blended between."""
    B1, B2 = np.radians(float(b1)), np.radians(float(b2))
    def F(x, y, z):
        x = np.asarray(x, float); y = np.asarray(y, float); z = np.asarray(z, float)
        r2 = x * x + y * y + z * z; r = np.sqrt(r2); rr = np.maximum(r, EPS)
        beta = np.arccos(np.clip(np.abs(z) / rr, -1.0, 1.0))               # angle from the z-axis, either end
        t = np.clip((beta - B1) / (B2 - B1), 0.0, 1.0)
        s = _g(1 - t) / (_g(t) + _g(1 - t))                                 # 1 inside b1 degrees, 0 beyond b2
        sg = np.where(z > 0, -1.0, 1.0)
        f = r2 / np.maximum(r2 + z * z, EPS)
        X1, Y1, Z1 = f * (x * x - y * y), f * 2 * x * y, f * 2 * z * r      # the one-plane square
        X2, Y2, Z2 = sg * 2 * z * x, sg * 2 * z * y, sg * (z * z - x * x - y * y)
        X, Y, Z = (1 - s) * X1 + s * X2, (1 - s) * Y1 + s * Y2, (1 - s) * Z1 + s * Z2
        n = np.sqrt(X * X + Y * Y + Z * Z)
        k = np.where(n > 0, r2 / np.maximum(n, EPS), 0.0)
        return X * k, Y * k, Z * k
    return F


h_ud55 = make(55, 75)

RULES = {
    'h_ud55': (h_ud55, 'One plane near the flat plane, lathe about the upright axis elsewhere, cone 55 / 75 (hunt rule)', ''),
    # the same with other cones: registered ONLY for the basilica close-cut screen (no Mandelbrot solid drawn for 4085)
    'h_ud30': (make(30, 50), 'The same, cone 30 / 50 (hunt rule)', ''),
    'h_ud45': (make(45, 60), 'The same, cone 45 / 60 (hunt rule)', ''),
    'h_ud65': (make(65, 85), 'The same, cone 65 / 85 (hunt rule)', ''),
    'h_ud4085': (make(40, 85), 'The same, wide blend 40 / 85 (hunt rule)', ''),
}

import numpy as np
c0, s0 = -0.5, np.sqrt(3) / 2
X, Y, Z = -0.44533888, -0.64384816, -0.62219999
zb, zt = (1 - c0) / s0, (1 + c0) / s0
a = max(abs(X), -Z / zb, Z / zt, 0); b = max(zb, zt) * 1.0001; x = b
for it in range(16):
    A = (1 - c0) * x + s0 * Z; B = (1 + c0) * x - s0 * Z; C = s0 * x + c0 * Z; q = x * x - X * X
    g = q * A * B - Y * Y * C * C
    dg = 2 * x * A * B + q * ((1 - c0) * B + (1 + c0) * A) - 2 * s0 * Y * Y * C
    print(it, x, g, dg, a, b)
    if g > 0: b = x
    else: a = x
    xn = x - g / dg
    if not (dg > 0) or not (xn > a) or not (xn < b): xn = 0.5 * (a + b)
    x = xn

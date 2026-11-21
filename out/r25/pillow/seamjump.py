"""Which seam turns (rho) give a rule without a tear? Pairs of directions straddling each seam, 2e-7 apart.

The folding of the top seam and the map z -> 2 conj(z) agree only if 4 rho is a whole number (NOTES.md, section 2).
"""
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import pil as P

rng = np.random.default_rng(4); n = 40000; eps = 1e-7


def across(pl, north):
    a = pl.an if north else pl.as_; rot = pl.rotn if north else pl.rots
    half = 2 * a / (1 + a * a); u = rng.uniform(-0.98 * half, 0.98 * half, n)
    out = []
    for sgn in (1, -1):
        p = (u + 1j * sgn * eps) * rot; r2 = np.abs(p) ** 2; k = 2 / (1 + r2); zz = (1 - r2) / (1 + r2)
        out.append(np.stack(pl.G(k * p.real, k * p.imag, zz if north else -zz)))
    return np.sqrt(((out[0] - out[1]) ** 2).sum(0))


for kind in ('J', 'JA'):
    for rho in (0.0, 0.1, 0.125, 0.2, 0.25, 1 / 3, 0.4, 0.5, 0.6, 0.75, 0.9):
        if kind == 'JA' and rho not in (0.0, 0.25, 0.5, 0.75):
            continue
        pl = P.Pillow(rho, 1.0 if rho != 0.5 else np.sqrt(3) / 2, kind); jt = across(pl, True); jb = across(pl, False)
        print('%-2s rho %.3f: across the top seam largest %.1e (median %.1e); across the bottom seam largest %.1e   %s'
              % (kind, rho, jt.max(), np.median(jt), jb.max(), 'TEAR' if max(jt.max(), jb.max()) > 1e-3 else 'no tear'))

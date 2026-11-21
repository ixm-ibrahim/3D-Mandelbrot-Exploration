"""Prover, claim C3: the main body of three KNOWN rules cut along one line from its centre to its flat rim.
For each rho (0 = centre, 1 = flat rim; flat multiplier rho * exp(2.0 i)): the height h* at which the resting point
stops attracting and which eigenvalue does it, and the height up to which the orbit of 0 stays bounded.
Writes c3_profile.npz for the sheet.      python out/r17/prover/c3_profile.py
"""
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import c3_edge as E

RHOS = np.concatenate([np.linspace(0.05, 0.85, 9), [0.9, 0.94, 0.97, 0.985, 0.995]])
THETA = 2.0


def vis(F, rho, hmax=1.2):
    lam = rho * np.exp(1j * THETA); a = lam / 2; c2 = a - a * a
    hs = np.linspace(0.002, hmax, 600)
    lo = 0.0
    for h in hs:
        if not E.bounded(F, np.array([c2.real, c2.imag, h]), 400):
            break
        lo = h
    return lo


if __name__ == '__main__':
    out = {}
    for name, F in E.RULES:
        rows = []
        for rho in RHOS:
            hstar, what, ev = E.climb(F, rho, THETA, dh=5e-4)
            code = 0 if 'lost' in what else (1 if 'complex' in what else (2 if 'real -' in what else (3 if 'real +' in what else 4)))
            hv = vis(F, rho)
            rows.append((rho, hstar if hstar else np.nan, code, hv))
            print('%-9s rho %.3f  h* %-8s %-48s bounded up to %.3f' % (name, rho, '%.4f' % hstar if hstar else 'none', what, hv), flush=True)
        out[name] = np.array(rows)
    np.savez(os.path.join(HERE, 'c3_profile.npz'), **out)

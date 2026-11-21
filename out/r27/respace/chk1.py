"""Check of the re-spacing functions in carry.py."""
import numpy as np
import carry as C

xs = np.array([0, 0.5, 1 / 3, 2 / 3, 0.25, 0.75, 0.4, 0.6, 1.0])
want = np.array([0, 0.5, 0.25, 0.75, 0.125, 0.875, 0.375, 0.625, 1.0])
print('qmark at simple fractions, worst miss', np.abs(C.qmark(xs) - want).max())
y = np.linspace(0, 1, 20001)
print('qmark(qinv(y)) - y, worst', np.abs(C.qmark(C.qinv(y)) - y).max())
ps = np.linspace(0, np.pi, 20001)
print('Psi(Omega(a)) - a, worst', np.abs(C.Psi(C.Omega(ps)) - ps).max())
deg = np.array([0, 11.25, 22.5, 45, 67.5, 90, 135, 180.0])
print('true angle', deg)
print('ball angle', np.round(np.degrees(C.Omega(np.radians(deg))), 2))

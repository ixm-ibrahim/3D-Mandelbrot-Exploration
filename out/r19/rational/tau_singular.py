"""Is the change of angle that makes the flat circle exact a smooth function? (No iteration of the 3D rule.)
tau solves R(e^(i tau(t))) = e^(i tau(2t)). Printed: the slope of tau measured over shorter and shorter steps
(a smooth function settles to one value; this one does not), at the fixed direction +x where the theory gives
tau ~ t^(log R'(1) / log 2), and the spread of slopes over the whole circle at each step size."""
import os, sys, importlib.util
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sp = importlib.util.spec_from_file_location('qr', os.path.join(HERE, 'myrules.py')); M = importlib.util.module_from_spec(sp); sp.loader.exec_module(M)
for d, beta in ((2, -M.B6), (2, -0.03), (1, 0.268), (1, 0.05)):
    n = d + 2
    grid, tau, gf, fine = M.angle_table(beta, d, 1 << 20)
    g1 = (d + 2) * (1 - beta * beta) / (1 - beta) ** 2 - d      # R'(1) on the circle
    lo = (d + 2) * (1 - abs(beta)) / (1 + abs(beta)) - d; hi = (d + 2) * (1 + abs(beta)) / (1 - abs(beta)) - d
    print('d = %d, beta = %+.4f: stretch along the flat circle %.2f to %.2f; at +x it is %.3f, so tau ~ t^%.3f there (1 = smooth)'
          % (d, beta, lo, hi, g1, np.log(g1) / np.log(2)))
    row = []
    for k in (3, 6, 9, 12, 15):
        t = 2 * np.pi / 2 ** k
        row.append('%.3g' % (np.interp(t, grid, tau) / t))
    print('   slope of tau from +x over steps of 1/8, 1/64, 1/512, 1/4096, 1/32768 of a turn: ' + ', '.join(row))
    row = []
    for k in (6, 9, 12, 15):
        m = 2 ** k; t = np.linspace(0, 2 * np.pi, m + 1); s = np.diff(np.interp(t, grid, tau)) / (2 * np.pi / m)
        row.append('%.3g to %.3g' % (s.min(), s.max()))
    print('   least and largest slope anywhere, steps of 1/64, 1/512, 1/4096, 1/32768 of a turn: ' + '; '.join(row), flush=True)

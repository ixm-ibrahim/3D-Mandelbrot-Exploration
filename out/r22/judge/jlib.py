"""Round 22, judge: my own small tools. Orbits are the library's rules (rule.step); the loops here are mine.

    import sys; sys.path.insert(0, 'out/r22/judge'); import jlib as L
"""
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, 'out', 'r21', 'lib'))
sys.path.insert(0, os.path.join(ROOT, 'out', 'r21', 'judge'))
import mem as M
import myrules as J

RABBIT = M.RABBIT; SIEGEL = M.SIEGEL; BAS = (-1.0, 0.0, 0.0)


def rules():
    return {'lathe': M.bench('lathe'), 'oneplane': M.bench('oneplane'), 'along': M.bench('along'),
            'once': J.get('alongmem.c_wake1'), 'pulled': J.get('sheet.evc005e70k16')}


def design(name):
    import importlib.util
    spec = importlib.util.spec_from_file_location('design_rules', os.path.join(ROOT, 'out', 'r22', 'design', 'myrules.py'))
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    return mod.get(name)


def follow(rule, x, y, z, c, steps, r2=36.0):
    """My own loop: positions after `steps` steps (nan where the orbit left |v| < 6) and the alive mask."""
    x, y, z = (np.array(t, float).ravel() for t in np.broadcast_arrays(x, y, z))
    n = x.size; cx, cy, cz = (np.full(n, float(t)) for t in c)
    st = tuple(rule.init(n)); alive = np.ones(n, bool)
    for k in range(steps):
        with np.errstate(all='ignore'):
            X, Y, Z, st = rule.step(x, y, z, st, k, cx, cy, cz); st = tuple(st)
        x, y, z = X + cx, Y + cy, Z + cz
        bad = ~((x * x + y * y + z * z) < r2)
        alive &= ~bad
        x[bad] = 100.0; y[bad] = 0.0; z[bad] = 0.0          # parked far away; stays dead through the mask
    x[~alive] = np.nan; y[~alive] = np.nan; z[~alive] = np.nan
    return x, y, z, alive


def one(rule, x, y, z, c, k=0, st=None):
    """One squaring plus c, of fresh orbits (k = 0)."""
    x, y, z = (np.array(t, float).ravel() for t in np.broadcast_arrays(x, y, z))
    n = x.size; cx, cy, cz = (np.full(n, float(t)) for t in c)
    X, Y, Z, st = rule.step(x, y, z, tuple(rule.init(n)) if st is None else st, k, cx, cy, cz)
    return X + cx, Y + cy, Z + cz


def arcs(inside):
    """Runs of True on a closed ring: list of (centre in degrees, width in degrees)."""
    n = inside.size
    if inside.all():
        return [(0.0, 360.0)]
    if not inside.any():
        return []
    s = int(np.argmin(inside)); v = np.roll(inside, -s); out = []; i = 0
    while i < n:
        if v[i]:
            j = i
            while j < n and v[j]:
                j += 1
            out.append((((i + j - 1) / 2 + s) % n * 360.0 / n, (j - i) * 360.0 / n)); i = j
        else:
            i += 1
    return out


def ring(x0, rad, n):
    a = np.arange(n) * 2 * np.pi / n
    return np.full(n, x0), rad * np.cos(a), rad * np.sin(a), np.degrees(a)


def flat_inside(zr, zi, c, steps):
    return M.flat_stay(zr, zi, c[0], c[1], steps) >= steps

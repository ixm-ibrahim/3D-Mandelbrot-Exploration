"""Round 25, judge: loader for the eight sections' rules (their module names clash, so each is loaded alone).

    import sys; sys.path.insert(0, 'out/r25/judge'); import jl
    r = jl.get('skew')      # see NAMES below
"""
import os, sys, importlib
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, 'out', 'r21', 'lib'))
import mem as M

CLASH = ['best', 'pil', 'rules', 'wall', 'tree', 'repair', 'four', 'roots', 'vrules', 'torus', 'paper2d']
_cache = {}


def _bench(name):
    for nm in CLASH:
        sys.modules.pop(nm, None)
    r = M.bench(name)
    sys.modules.pop('rules', None)
    return r


def section(sec):
    """The module best.py of one section, loaded alone."""
    if sec in _cache:
        return _cache[sec]
    p = os.path.join(ROOT, 'out', 'r25', sec)
    for nm in CLASH:
        sys.modules.pop(nm, None)
    sys.path.insert(0, p)
    try:
        b = importlib.import_module('best')
    finally:
        for nm in CLASH:
            sys.modules.pop(nm, None)
        sys.path[:] = [q for q in sys.path if os.path.normcase(os.path.abspath(q)) != os.path.normcase(os.path.abspath(p))]
    _cache[sec] = b
    return b


NAMES = {
    'oneplane': lambda: _bench('oneplane'),
    'twoplane': lambda: _bench('twoplane'),
    'along': lambda: _bench('along'),
    'skew': lambda: section('pillow').rule('skew'),
    'skew-mirror': lambda: section('pillow').rule('skew-mirror'),
    'tetra': lambda: section('pillow').rule('tetra'),
    'sqpillow': lambda: section('pillow').rule('square'),
    'twin_tri': lambda: section('fromc').rule('twin_tri'),
    'face_tri': lambda: section('fromc').rule('face_tri'),
    'axis_once': lambda: section('fromc').rule('axis_once'),
    'cube': lambda: section('wall').rule(),
    'wsquare': lambda: section('wall').rule_square(),
    'cone': lambda: section('fourd').rule(),
    'holo': lambda: section('vahlen').rule(),
    'zip1': lambda: section('inverse').rule(1.0),
    'zip2': lambda: section('inverse').rule(2.0),
    'ring3': lambda: section('torus').rule(),
    'kfix': lambda: section('klein').repaired(),
    'pearl': lambda: section('klein').rule(),
    'pearl-eisen': lambda: section('klein').rule('eisen'),
}
_rules = {}


def get(name):
    if name not in _rules:
        _rules[name] = NAMES[name]()
    return _rules[name]


RABBIT = M.RABBIT; SIEGEL = M.SIEGEL
SETS = {'c1': (-1.0, 0.0, 0.0), 'rabbit': RABBIT, 'c075': (-0.75, 0.0, 0.0), 'siegel': SIEGEL,
        'rabbit-mirror': (RABBIT[0], -RABBIT[1], 0.0), 'ci': (0.0, 1.0, 0.0), 'c3b': (0.5575728, 0.5403468, 0.0)}


def flat_true(zr, zi, cr, ci, steps, power=2, r2=36.0):
    """The true flat orbit of z^power + c, the judge's own: complex numbers, same count as M.stay."""
    z = np.array(zr, float) + 1j * np.array(zi, float); c = np.asarray(cr, float) + 1j * np.asarray(ci, float)
    n = np.zeros(z.shape, np.int32); alive = np.ones(z.shape, bool)
    for _ in range(steps):
        z = np.where(alive, z ** power + c, z)
        alive &= (z.real ** 2 + z.imag ** 2) < r2; n += alive
    return n


def tilt(c, deg):
    """c lifted out of the flat plane by deg degrees, its length kept."""
    cx, cy, _ = c; r = np.hypot(cx, cy); a = np.radians(deg)
    if r == 0:
        return c
    return (cx * np.cos(a), cy * np.cos(a), r * np.sin(a))

"""Round 16 bench: the registry of rules. Stand-alone numpy.

A rule is a function F(x, y, z) -> (X, Y, Z) on float arrays of one shape: the 'square' of the point, without c.
Every rule here squares the length of the point (|F(v)| = |v|^2); the bench relies on that for its escape radius.

To add a rule: write the function and add one line to RULES (see README.md).
"""
import os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
for p in (os.path.join(ROOT, 'out', 'me', 'r16'), os.path.join(ROOT, 'out', 'r15', 'study'), os.path.join(ROOT, 'out', 'r14', 'turns')):
    if p not in sys.path:
        sys.path.insert(0, p)
import scout as S, scout2 as S2, scout3 as S3      # the orchestrator's scouts hold the closed forms
import fastpil                                      # the square pillow (round 15 study)
import turns                                        # voxel renderer, Kleinian squaring

EPS = 1e-300


def lathe(x, y, z):
    """Quaternion square: the flat rule spun round the x-axis."""
    return x * x - y * y - z * z, 2 * x * y, 2 * x * z


oneplane = S.oneplane          # Sphere inversions, one plane
twoplane = S.twoplane          # nearest plane's one-plane rule (the Figure 4 look; tears on |y| = |z|)
wind2 = S2.wind(2)             # pure winding, psi = -phi (no flat spot)
away = S3.turning(-1)          # one-plane square about a plane that turns against the point
along = S3.turning(1)          # ... that turns with the point and overtakes it


def pillow(x, y, z):
    """Square pillow, power 2, the reference layout of round 15 (fastpil.REF)."""
    sh = np.shape(x)
    X, Y, Z = fastpil.F(np.ravel(x).astype(float), np.ravel(y).astype(float), np.ravel(z).astype(float), fastpil.get_lay(fastpil.REF))
    return X.reshape(sh), Y.reshape(sh), Z.reshape(sh)


def kleinian(x, y, z):
    """Kleinian squaring (round 14). Known: the cut at z = 0 is not the flat set."""
    return turns.K1(x, y, z)


def mandelbulb(x, y, z):
    """Mandelbulb, power 2 (latitude and longitude both doubled). Known: smear."""
    p2 = x * x + y * y
    ok = p2 > 0
    q = np.where(ok, p2, 1.0)
    k = (p2 - z * z) / q
    X = np.where(ok, k * (x * x - y * y), -z * z)
    Y = np.where(ok, k * 2 * x * y, 0.0)
    return X, Y, 2 * z * np.sqrt(p2)


# name -> (function, plain label, what is known about it before the bench: '' for a new rule)
RULES = {
    'twoplane':   (twoplane,   'Two planes, nearest plane (reference look)', 'known: the look the user liked; tears on |y| = |z| (must fail J6 only)'),
    'oneplane':   (oneplane,   'Sphere inversions, one plane',               'known: buds only in the flat plane (must fail J4)'),
    'lathe':      (lathe,      'Quaternion square (lathe)',                  'known: the flat set spun round the x-axis (must fail J3)'),
    'pillow':     (pillow,     'Square pillow',                              'known: bodies joined, lopsided, streaks (must fail J2 and J7)'),
    'kleinian':   (kleinian,   'Kleinian squaring',                          'known: cut at z = 0 is not the flat set (must fail J1)'),
    'mandelbulb': (mandelbulb, 'Mandelbulb, power 2',                        'known: smear'),
    'latlon3':    (S.latlon(lambda L: 3 * L), 'Latitude times 3, longitude times 2', 'known from the scout: falls apart (must fail J5)'),
    'wind2':      (wind2,      'Pure winding, two planes (no flat spot)',    ''),
    'away':       (away,       'Turning plane, away',                        ''),
    'along':      (along,      'Turning plane, along',                       ''),
}
# Round 17: each searcher keeps its rules in out/r17/<name>/myrules.py, as a dict RULES of the same shape.
# A file that fails to load is skipped with a warning, so one searcher cannot stop another.
import glob, importlib.util, traceback
for _p in sorted(glob.glob(os.path.join(ROOT, 'out', 'r17', '*', 'myrules.py')) + glob.glob(os.path.join(ROOT, 'out', 'r19', '*', 'myrules.py'))
                 + glob.glob(os.path.join(ROOT, 'out', 'r20', '*', 'myrules.py'))):
    try:
        _s = importlib.util.spec_from_file_location('myrules_' + os.path.basename(os.path.dirname(os.path.dirname(_p))) + '_' + os.path.basename(os.path.dirname(_p)), _p)
        _m = importlib.util.module_from_spec(_s); _s.loader.exec_module(_m)
        RULES.update(_m.RULES)
    except Exception:
        print('WARNING: could not load', _p, file=sys.stderr); traceback.print_exc()

KNOWN = ['twoplane', 'oneplane', 'lathe', 'pillow', 'kleinian', 'mandelbulb', 'latlon3']
NEW = ['wind2', 'away', 'along']


def get(name):
    return RULES[name][0]


if __name__ == '__main__':
    rng = np.random.default_rng(1)
    P = rng.normal(size=(20000, 3))
    for name, (F, label, known) in RULES.items():
        X, Y, Z = F(P[:, 0], P[:, 1], P[:, 2])
        ln = np.abs(np.sqrt(X * X + Y * Y + Z * Z) - (P ** 2).sum(1)).max()
        X, Y, Z = F(P[:, 0], P[:, 1], 0 * P[:, 2])
        pl = max(np.abs(X - (P[:, 0] ** 2 - P[:, 1] ** 2)).max(), np.abs(Y - 2 * P[:, 0] * P[:, 1]).max(), np.abs(Z).max())
        print('%-11s %-44s length squared to %.1e | plane z = 0 against complex squaring %.1e' % (name, label, ln, pl))

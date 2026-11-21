"""Round 19, section foldpost (prefix f_): the one-plane ANSWER folded with sphere inversions.
See folds.py for the construction and scan1.py / scan2.py for how the numbers were chosen.
Angles: psi = angle of a cap centre from +x in the upright plane y = 0 (90 = straight up);
e = elevation above -x along the upright great circle (running over straight-up to +x at 180)."""
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import folds as FO


def _psi(p):
    p = np.radians(p); return np.array([np.cos(p), 0.0, np.sin(p)])


def _e(e):
    e = np.radians(e); return np.array([-np.cos(e), 0.0, np.sin(e)])


def one(psi, alpha):
    return FO.fold_one(_psi(psi), np.radians(alpha))


def pleat(g1, E1, g2, E2):
    return FO.fold_pleat(_e((g1 + E1) / 2), np.radians((E1 - g1) / 2), _e((E2 - g2) / 2), np.radians((E2 + g2) / 2))


FOLDS = {
    # one fold; radius fixed by "the extra copy of -x arrives with stretch exactly 2" (scan1.py, table A)
    'f_one80': (one(80.0, 31.95), 'One fold, cap 10 deg off straight-up, bud copy stretch 2'),
    'f_one85': (one(85.0, 27.75), 'One fold, cap 5 deg off straight-up, bud copy stretch 2'),
    'f_one60': (one(60.0, 55.20), 'One fold, big cap 30 deg off straight-up, bud copy stretch 2'),
    # two folds (a pleat): three layers only over the ring between the rims; -x is in the ring, +x is not
    'f_cres10': (pleat(10.0, 90.0, 10.0, 90.0), 'Pleat closing at straight-up, rims 10 deg either side of -x'),
    'f_pl10': (pleat(10.0, 140.0, 10.0, 150.0), 'Wide pleat, rims 10 deg either side of -x'),
    'f_pl5': (pleat(10.0, 140.0, 5.0, 142.0), 'Wide thin pleat, rims 10 above and 5 below -x'),
}
RULES = {k: (FO.rule(f), lab, '') for k, (f, lab) in FOLDS.items()}

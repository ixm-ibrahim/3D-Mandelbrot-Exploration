"""Round 28, Track A, the final checker: section 1.4 a once more (is it an object?), no browser.

  python -B out/r28/final/mk/a5.py     -> out/r28/final/truth/logs/a_object.txt

REUSED: the truth checker's a_object.py (functions one and bad_rho) and its list of balls tkit.py: no two listed
balls cut into each other, and the recipe of section 1.1 (300 rounds) equals "lies in a listed ball" at 20000 points.
MINE: the settings (five; three with a smaller second sphere and the neighbours past 100; none of them is one of the
truth checker's 90, whose sizes were 5, 30, 60, 90, 99 and 100 % of the touching size), and one more look at 70 %.
"""
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); FINAL = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(FINAL, 'truth', 'mk'))
import a_object as A

if __name__ == '__main__':
    rng = np.random.default_rng(20281120)
    A.say('Round 28, final check, 1.4 a, on lists of balls (no page is needed: this is the recipe of section 1.1 itself).')
    A.say('')
    ok = True; n = 0
    #         grid      rho        p
    for g, rho, p in (('square', 1.0, 100 / 1.8), ('hex', 1.0, 75.0), ('square', 0.5, 150.0), ('hex', 0.2, 480.0), ('line', 1.0 / 3.0, 150.0), ('hex', 0.5, 120.0)):
        r, _ = A.one(g, rho, p * rho / 100.0, 4e-5 if g == 'line' else 8e-4, rng); ok &= r; n += 1
    A.say('')
    A.say('ALL %d SETTINGS HOLD' % n if ok else 'SOME SETTINGS FAIL (see the lines marked FAILS)')
    A.say('')
    A.say('A second sphere of 70 % of the first (not offered by the dial), and 50 % with the same coarse lists for comparison:')
    for g, rho, p in (('square', 0.7, 100 / 1.8), ('hex', 0.7, 120.0), ('line', 0.7, 80.0), ('square', 0.5, 100 / 1.8), ('hex', 0.5, 120.0)):
        A.bad_rho(g, rho, p, 2e-4 if g == 'line' else 8e-3, rng)

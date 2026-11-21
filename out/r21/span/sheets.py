"""Julia and Mandelbrot sheets for groups of rules.
python out/r21/span/sheets.py <group> [julia|mandel|both]
groups: c, prev, lag, guess, bench
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import myrules as R
M = R.M

GROUPS = {
    'c': ['c_lathe', 'c_page', 'c_Pfirst', 'c_lag50'],
    'prev': ['prev_lathe', 'prev_page', 'prev_Pfirst', 'prev_axis'],
    'lag': ['prev_keep', 'prev_lag50in', 'prev_lag50P', 'prev_lag25P', 'prev_delay'],
    'guess': ['guessP', 'guessPc', 'guessN', 'guessNc'],
    'extra': ['c_lag10', 'c_lag25', 'prev_lag10P', 'roll'],
}

if __name__ == '__main__':
    g = sys.argv[1]; what = sys.argv[2] if len(sys.argv) > 2 else 'both'
    rules = [M.bench('along'), M.bench('oneplane'), M.bench('lathe')] if g == 'bench' else [R.get(n) for n in GROUPS[g]]
    if what in ('julia', 'both'):
        M.julia_sheet(rules, os.path.join(HERE, 'julia-%s.png' % g), w=250, h=188, nd=150, steps=28)
    if what in ('mandel', 'both'):
        M.mandel_sheet(rules, os.path.join(HERE, 'mandel-%s.png' % g), w=280, cw=240, ch=220, nd=160, steps=22, cut_steps=60)

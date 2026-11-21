"""Round 28, truth checker, an addition to 1.4 a: just PAST the place where the two spheres touch (p rho > 100).

  python out/r28/fix/truth/mk/a_past.py      -> out/r28/fix/truth/logs/a_past.txt

The dials never show this (the size gives way, and the page holds t to (1 + rho) / 2 or more). It is here to show
that the wall "p rho <= 100" is real: with the same tool as a_object.py, do listed balls cut into each other when
the spheres cut into each other by 2 %, 5 %, 20 %?
"""
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); TRUTH = os.path.dirname(HERE); sys.path.insert(0, HERE)
import tkit as T
lines = []
for gname in ('line', 'square', 'hex'):
    grid = T.Grid(gname)
    for rho in (1.0, 0.5, 0.2):
        for f in (1.0, 1.02, 1.05, 1.2):
            p = f * 100 / rho; top = T.top_of(p)
            reps, info = T.build(grid, top, rho, 4e-4 if gname == 'line' else 4e-3, cap=400_000, max_levels=80)
            ov = T.overlaps(reps, grid, top)
            s = '%-6s rho %-4g p %-8.2f (p rho = %.0f) top %.4f | %6d balls | pairs that cut into each other: %d, deepest %.4f | %s' % (
                gname, rho, p, p * rho, top, info['n'], ov['pairs'], ov['deepest'], 'OVERLAPS' if ov['pairs'] else 'no overlap')
            print(s, flush=True); lines.append(s)
open(os.path.join(TRUTH, 'logs', 'a_past.txt'), 'w', encoding='utf-8', newline='\n').write('\n'.join(lines) + '\n')

"""Pictures for NOTES.md, part 3: the solid as the sheet forgets its start later and later.

    python out/r21/prover/t7_forget.py [julia]  ->  out/r21/prover/t7_forget_mandel.png (and t7_forget_julia.png)

Rows: the lathe (forgets at once), first 1, 2, 3, 8 squarings about the flat page and the own sheet afterwards,
the one-plane rule (never forgets).  Not a search for a rule: an illustration of statements F1 to F4.
"""
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, 'out', 'r21', 'lib')); sys.path.insert(0, HERE)
import mem as M, myrules as R

if __name__ == '__main__':
    np.seterr(all='ignore')
    scout = {r.name: r for r in M.SCOUT}
    rules = [scout['own'], R.BY['first1'], R.BY['first2'], R.BY['first3'], R.BY['first8'], scout['fixed']]
    if len(sys.argv) > 1 and sys.argv[1] == 'julia':
        M.julia_sheet([R.BY['first1'], R.BY['first2'], R.BY['first3'], M.bench('along')], os.path.join(HERE, 't7_forget_julia.png'), w=330, h=250, nd=200,
                      title='Julia sets when the sheet forgets its start after 1, 2, 3 squarings; "along" for comparison (rough blocks, 28 steps)')
    else:
        M.mandel_sheet(rules, os.path.join(HERE, 't7_forget_mandel.png'), angles=(0.0, 11.25, 22.5, 45.0, 90.0), w=340, cw=270, ch=250, nd=220,
                       title='The Mandelbrot solid when the sheet forgets its start after k squarings (cuts: 60 steps, solid: 22 steps)')

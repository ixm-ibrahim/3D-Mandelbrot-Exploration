"""The same numbers as checks.py for the bench rules, for comparison. python out/r21/span/benchnum.py -> benchnum.txt"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import checks as C
M = C.M
out = []
for nm in ('along', 'oneplane', 'lathe'):
    r = M.bench(nm); s = M.spun_check(r)
    vb = [C.volume(r, (-1.0, 0.0, 0.0), k) for k in (30, 80)]; vr = [C.volume(r, M.RABBIT, k) for k in (30, 80)]; vm = [C.mvolume(r, k) for k in (30, 80)]
    out.append('%-9s turned: M differs %.2f%% (inside %.1f%%), basilica differs %.2f%% (inside %.1f%%) | volume 30/80 steps: basilica %.2f%%/%.2f%%, rabbit %.2f%%/%.2f%%, M %.2f%%/%.2f%%'
               % (nm, 100 * s['mandel_differ'], 100 * s['mandel_inside'], 100 * s['basilica_differ'], 100 * s['basilica_inside'], 100 * vb[0], 100 * vb[1], 100 * vr[0], 100 * vr[1], 100 * vm[0], 100 * vm[1]))
    print(out[-1])
open(os.path.join(HERE, 'benchnum.txt'), 'w', encoding='utf-8').write('\n'.join(out) + '\n')

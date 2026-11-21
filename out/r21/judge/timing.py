"""Timing of one rough solid per rule, and a first sanity check that every rule loads.  python out/r21/judge/timing.py"""
import os, sys, time
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))
import myrules as J
M = J.M
for r in J.RULES + J.EXTRA:
    t0 = time.time(); dep, px = M.solid(r, (-1.0, 0.0, 0.0), 200, 150, 120, 28)
    t1 = time.time(); dep, px = M.solid(r, M.RABBIT, 200, 150, 120, 28)
    print('%-22s basilica %.1f s, rabbit %.1f s (200x150x120, 28 steps)' % (r.name, t1 - t0, time.time() - t1)); sys.stdout.flush()

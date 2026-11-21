"""Round 24, rough: compute and cache the block grids.   python out/r24/rough/vox.py rule:set,rule:set,..."""
import os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import rl as L

if __name__ == '__main__':
    t0 = time.time()
    for job in sys.argv[1].split(','):
        nm, sn = job.split(':'); n = L.blocks(nm, sn)
        print('%-10s %-8s inside %d blocks (volume %.3f)  [%.0f s]' % (nm, sn, int((n >= 80).sum()), float((n >= 80).sum()) * L.H ** 3, time.time() - t0)); sys.stdout.flush()

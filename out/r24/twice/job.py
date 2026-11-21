"""Blocks and picture tiles for one rule and some shapes (cached).   python out/r24/twice/job.py <key> <set> [<set> ...]"""
import os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import tw

if __name__ == '__main__':
    key = sys.argv[1]; t0 = time.time()
    for sn in sys.argv[2:]:
        n = tw.vox(key, sn)
        for eye in ('a', 'top'):
            for steps in (30, 120):
                tw.tile(key, sn, eye, steps)
        print('%s %s done: inside after 30 steps %.4f, after 120 steps %.4f of the box  [%.0f s]' % (key, sn, 2 * (n >= 30).mean(), 2 * (n >= 120).mean(), time.time() - t0)); sys.stdout.flush()

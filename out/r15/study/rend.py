"""Render voxel solids to PNG tiles in parallel. python out/r15/study/rend.py job.json  (list of [npy, az, el, png, n])"""
import os, sys, json, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, 'out', 'r14', 'turns'))

def one(job):
    import turns
    from PIL import Image
    npy, az, el, png, n = job
    if os.path.exists(png): return png
    vol = np.load(npy) == 0
    Image.fromarray(turns.render(vol, az=az, el=el, out=n)).save(png)
    return png

if __name__ == '__main__':
    import multiprocessing as mp
    jobs = json.load(open(sys.argv[1]))
    with mp.Pool(int(sys.argv[2]) if len(sys.argv) > 2 else 5) as pool:
        for p in pool.imap_unordered(one, jobs): print('rendered', os.path.basename(p), flush=True)

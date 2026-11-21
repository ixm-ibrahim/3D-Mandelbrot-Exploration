"""Does the J4 count on the middle body depend on the wearing radius? Redo it from the saved solids at three radii.
python out/r16/bench/wear_check.py [rule ...]"""
import os, sys, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import bench as B

for n in sys.argv[1:] or ['twoplane', 'oneplane', 'away', 'along', 'wind2']:
    vol, L, _c = B.take(n, 'solid'); N = vol.shape[0]; h = 2 * L / (N - 1); m = N // 2
    hw = int(round(1.0 / h)); cube = vol[m - hw:m + hw + 1, m - hw:m + hw + 1, m - hw:m + hw + 1]; org = [-hw * h] * 3
    line = []
    for rad in (0.07, 0.11, 0.15):
        rv = rad / h; op, rs = B.wear(cube, rv); lab, ps = B.pieces(rs, h, org)
        ps = [p for p in ps if p['voxels'] >= B.vmin(rv) and abs(p['centre'][0]) <= 0.5]
        buds = [p for p in ps if not (p['extent'] >= 300) and p['rho'] > 0.1]
        off = [p for p in buds if abs(np.sin(np.radians(p['phi']))) > B.SIN20]
        rnd = [p for p in off if p['round'] >= 0.45]
        line.append('radius %.2f: %2d come off, %2d off the flat plane, %2d of those round, roundness %s' % (rad, len(buds), len(off), len(rnd), 'none' if not buds else '%.2f' % B.roundness(buds)))
    print('%-9s %s' % (n, ' | '.join(line)), flush=True)

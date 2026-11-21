"""Print the raw J5 / J8 numbers of every saved result (a working aid for calibration)."""
import json, glob, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
order = ['twoplane', 'oneplane', 'lathe', 'pillow', 'kleinian', 'mandelbulb', 'latlon3', 'wind2', 'away', 'along']
f = lambda v: 'none' if v is None else '%.2f' % v
for n in order:
    p = os.path.join(HERE, 'results', n + '.json')
    if not os.path.exists(p):
        continue
    r = json.load(open(p)); j8 = r['J8']; j5 = r['J5']
    print('%-10s J5 strict %.2f tol %.3f pieces %d loose2 %s loose3 %s' % (n, j5['biggest_pct'], j5['biggest_pct_one_voxel_gap_allowed'], j5['pieces'], f(j5.get('loose_in_close_up_2_pct')), f(j5.get('loose_in_close_up_3_pct'))))
    for k in (1, 2, 3):
        rl = j8.get('relief_%d' % k)
        print('     size %d: roundness of pieces %s | relief round %s spread %s streak share %s bumpy share %s | evenness %s' % (
            k, f(j8.get('roundness_%d' % k)), f(rl and rl['relief_round']), ('%.3f' % rl['mean_spread']) if rl else 'none', ('%.3f' % rl['streak_share']) if rl else 'none',
            ('%.3f' % rl['bumpy_share']) if rl else 'none', f(j8.get('evenness_%d' % k))))

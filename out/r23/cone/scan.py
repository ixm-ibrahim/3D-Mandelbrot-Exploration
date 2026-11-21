"""Numbers only, many variants of the direction map.  python out/r23/cone/scan.py [weld|rt]"""
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import conelib as L


def line(tag, G, n=500):
    o, _ = L.numbers(G, n=n, quiet=True); cr = o['critical (lat, lon -> lat, lon, stretch)']; co = o['cone']
    crs = '; '.join('(%.0f,%.0f)->(%.0f,%.0f)' % c[:4] for c in cr[:4])
    print('%-34s covers %.3f folded %.4f  ratio>2: %.2f >4: %.2f | cone img lat %.1f..%.1f stretch %.2f..%.2f / %.2f..%.2f | crit %s'
          % (tag, o['covers'], o['folded_share'], o['share_ratio_over_2'], o['share_ratio_over_4'], co['image_lat_min_max'][0], co['image_lat_min_max'][1],
             co['stretch_small'][0], co['stretch_small'][1], co['stretch_large'][0], co['stretch_large'][1], crs)); sys.stdout.flush()
    return o


what = sys.argv[1] if len(sys.argv) > 1 else 'weld'
if what == 'weld':
    for kind in (3, 5):
        for bend in (0.6, 0.8, 1.0, 1.25, 1.5, 2.0):
            line('weld kind %d bend %.2f' % (kind, bend), lambda x, y, z: L.weld_dir(x, y, z, 0.0, 0.0, L.MU60, bend, kind))
    for mua, mub in ((0.1, L.MU60), (0.2, L.MU60), (0.0, 1.1), (0.0, 0.9), (0.2, 1.1), (0.3, 1.0)):
        for bend in (0.8, 1.0, 1.25):
            line('weld mua %.1f mub %.2f bend %.2f' % (mua, mub, bend), lambda x, y, z: L.weld_dir(x, y, z, 0.0, mua, mub, bend, 3))
if what == 'rt':
    for mu1 in (0.2, 0.3, 0.4):
        line('rt exp mu1 %.1f' % mu1, lambda x, y, z: L.rt_dir(x, y, z, L.T15, 0.0, mu1, 'exp'))
    for mu1 in (0.3, 0.44, 0.6, 0.8, 1.0, 1.3):
        line('rt tvar mu1 %.2f' % mu1, lambda x, y, z: L.rt_dir(x, y, z, L.T15, 0.0, mu1, 'tvar'))
    for mu1 in (0.6, 1.0):
        line('rt tvar mu1 %.2f + exact top' % mu1, lambda x, y, z: L.rt_dir(x, y, z, L.T15, 0.0, mu1, 'tvar', top=(1.0, L.MU60)))
    line('rt tvar mu1 0.8 turned 30', lambda x, y, z: L.rt_dir(x, y, z, L.T15, np.pi / 6, 0.8, 'tvar'))

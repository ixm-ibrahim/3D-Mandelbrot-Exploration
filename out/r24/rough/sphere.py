"""Round 24, rough, step 0: how hard does ONE step of each rule squeeze, and where on the sphere of directions?

    python out/r24/rough/sphere.py [rule,rule,...]      -> prints the table, writes cache/sphere.json

One step at the point v stretches by 2|v| along the ray and by |v| s1, |v| s2 across it. squeeze = max(2, s1) / min(2, s2).
"""
import os, sys, json
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import rl as L

NAMES = ['oneplane', 'shear', 'second', 'second_raw', 'cones', 'cones_raw', 'm4', 'm4_raw', 'm6', 'm6_raw', 'tri']


def branch_dirs(tab, thr=0.25):
    """Directions of the upper half where the direction map stops stretching (s2 below thr): clustered, (lat, lon, s1, s2, image lat)."""
    la, lo, s1, s2, g = tab['la'], tab['lo'], tab['s1'], tab['s2'], tab['g']
    m = np.nonzero(s1 < thr)[0]; out = []
    if m.size == 0:
        m = np.nonzero(s2 < thr * 0.4)[0]
    d = np.stack([np.cos(la) * np.cos(lo), np.cos(la) * np.sin(lo), np.sin(la)], 1)
    order = m[np.argsort(s1[m] + s2[m])]
    for i in order:
        if all(np.dot(d[i], d[j]) < np.cos(np.radians(12.0)) for j in out):
            out.append(i)
        if len(out) >= 12:
            break
    return [(float(np.degrees(la[i])), float(np.degrees(lo[i])), float(s1[i]), float(s2[i]), float(np.degrees(np.arcsin(np.clip(g[i, 2], -1, 1))))) for i in out]


if __name__ == '__main__':
    names = sys.argv[1].split(',') if len(sys.argv) > 1 else NAMES
    path = os.path.join(L.CACHE, 'sphere.json'); allm = json.load(open(path)) if os.path.exists(path) else {}
    for nm in names:
        r = L.get(nm); rows, keep, tab = L.sphere_table(r)
        br = branch_dirs(tab)
        w = np.cos(tab['la']); cover = float((np.abs(tab['det']) * w).sum() / w.sum() / 2)      # upper half: area of the image / area of the half
        print('\n== %s (%s)' % (nm, r.plain))
        print('   covers the sphere %.2f times; share of all directions where a step keeps shapes within a quarter (squeeze < 1.25): %.1f %%' % (cover, 100 * keep))
        print('   latitude band: squeeze median (90 %%) | stretches s1, s2 (medians) | smallest s2 | folded share')
        for b in rows:
            print('   %7s: %6.2f (%6.2f) | %5.2f %5.2f | %5.3f | %.3f' % b)
        print('   directions where the map stops stretching (upper half): ' + ('; '.join('lat %.0f lon %.0f (s %.2f, %.2f; sent to lat %.0f)' % t for t in br) or 'none below the threshold'))
        allm[nm] = dict(rows=rows, keep=keep, cover=cover, branch=br); sys.stdout.flush()
    json.dump(allm, open(path, 'w'), indent=1)

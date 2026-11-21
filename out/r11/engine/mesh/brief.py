"""One short line a job from the checks of a page: python out/r10/engine/mesh/brief.py <page> [<page> ...]"""
import glob, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
for page in sys.argv[1:]:
    print(page)
    for p in sorted(glob.glob(os.path.join(HERE, page, 'checks', '*.json'))):
        c = json.load(open(p, encoding='utf-8')); col = c.get('colour') or {}; sil = c.get('silhouette') or {}
        r = json.load(open(os.path.join(HERE, page, 'runs', c['job'] + '.json'), encoding='utf-8'))
        print('  %-16s hue %5.1f deg, within 30: %4.1f %%, overlap %.3f, tris %7s, job %5.1f s' % (c['job'], col.get('hue_diff_median_deg', -1), 100 * col.get('hue_diff_within_30deg_share', 0), sil.get('iou', 0), c.get('stl', {}).get('count'), r.get('seconds', 0)))

"""Before and after for the model jobs: python out/r9/mesh/cmp.py <tagA> <tagB> <job> ... Prints shape and colour numbers side by side,
whether the STL files are the same byte for byte, and for cut solids the share of the picture's cut face that is plain in the model."""
import json, os, sys
import numpy as np
from PIL import Image
BASE = os.path.dirname(os.path.abspath(__file__))
def load(tag, job):
    p = os.path.join(BASE, tag, 'checks', job + '.json')
    return json.load(open(p, encoding='utf-8')) if os.path.exists(p) else None
def face(tag, job):
    p = os.path.join(BASE, tag, 'pics', 'cmp-' + job + '.png')
    if not os.path.exists(p): return None
    im = np.asarray(Image.open(p).convert('RGB')).astype(float) / 255; w = im.shape[1] // 3
    pic, mod = im[:, :w], im[:, w:2 * w]
    def sat(a): mx, mn = a.max(2), a.min(2); return np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-9), 0), mx
    sp, vp = sat(pic); sm, vm = sat(mod)
    cream = (vp > 0.6) & (sp < 0.25)            # the picture's plain cut face
    shown = cream & (vm > 0.18)                 # where the model is drawn too
    return float(((sm < 0.3) & shown).sum() / max(1, shown.sum())), int(shown.sum())
a, b = sys.argv[1], sys.argv[2]
for job in sys.argv[3:]:
    A, B = load(a, job), load(b, job)
    if not A or not B: print(job, 'missing', bool(A), bool(B)); continue
    def row(X):
        s, sil, c = X.get('stl') or {}, X.get('silhouette', {}), X.get('colour', {})
        return 'tris %s closed %s oriented %s pieces %s vol %.2f size %s | overlap %.3f pic-only %.3f model-only %.3f | hue %.1f deg, %.0f%% within 30' % (
            s.get('count'), s.get('closed'), s.get('oriented'), s.get('components'), s.get('volume_cm3', 0), [round(v, 1) for v in s.get('size_mm', [])],
            sil.get('iou', 0), sil.get('picture_only_share', 0), sil.get('model_only_share', 0), c.get('hue_diff_median_deg', -1), 100 * c.get('hue_diff_within_30deg_share', 0))
    print(job)
    print('  %-8s %s' % (a, row(A))); print('  %-8s %s' % (b, row(B)))
    print('  same STL bytes: %s; same PLY bytes: %s' % (A.get('sha1_stl') == B.get('sha1_stl'), A.get('sha1_ply') == B.get('sha1_ply')))
    if job.startswith('cut'):
        fa, fb = face(a, job), face(b, job)
        print('  share of the picture\'s plain cut face that is plain in the model: %s %.3f (%d px), %s %.3f (%d px)' % (a, fa[0], fa[1], b, fb[0], fb[1]))

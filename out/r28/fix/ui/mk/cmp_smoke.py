"""Round 28, dial checker (ui): the old smoke list on the new page against the same list on the frozen page.
  python -B out/r28/fix/ui/mk/cmp_smoke.py   -> out/r28/fix/ui/logs/cmp-smoke.txt
The result line of every step is compared word for word, and every picture the list saves is compared pixel by
pixel (new page against frozen page). Nothing is run here; it reads logs/smoke-new*.* and logs/smoke-old*.*."""
import json, os, sys
import numpy as np
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); UI = os.path.dirname(HERE)
L = os.path.join(UI, 'logs')
new = json.load(open(os.path.join(L, 'smoke-new-results.json'), encoding='utf-8'))
old = json.load(open(os.path.join(L, 'smoke-old-results.json'), encoding='utf-8'))
out = ['steps with a result: new page %d, frozen page %d' % (len(new), len(old))]
same = 0
for k in sorted(set(new) | set(old), key=int):
    a, b = new.get(k), old.get(k)
    if a == b:
        same += 1
    else:
        out.append('step %s differs:\n    new:    %s\n    frozen: %s' % (k, str(a)[:700], str(b)[:700]))
out.append('result lines that are the same word for word: %d of %d' % (same, len(set(new) | set(old))))
pn, po = os.path.join(UI, 'smoke-smoke-new'), os.path.join(UI, 'smoke-smoke-old')
names = sorted(set(os.listdir(pn)) | set(os.listdir(po)))
ident = 0; rows = []
for n in names:
    a, b = os.path.join(pn, n), os.path.join(po, n)
    if not (os.path.exists(a) and os.path.exists(b)):
        rows.append('%s: only on the %s page' % (n, 'new' if os.path.exists(a) else 'frozen')); continue
    A = np.asarray(Image.open(a).convert('RGB')).astype(int); B = np.asarray(Image.open(b).convert('RGB')).astype(int)
    if A.shape != B.shape:
        rows.append('%s: sizes differ %s %s' % (n, A.shape, B.shape)); continue
    d = np.abs(A - B).max(axis=2); nd = int((d > 0).sum())
    if nd == 0:
        ident += 1
    else:
        ys, xs = np.nonzero(d)
        rows.append('%s: %d of %d pixels differ (largest difference %d of 255), all inside the box x %d..%d, y %d..%d of a %d x %d picture' % (n, nd, d.size, int(d.max()), xs.min(), xs.max(), ys.min(), ys.max(), A.shape[1], A.shape[0]))
out.append('pictures saved by the list: %d; the same to the pixel on both pages: %d' % (len(names), ident))
out += ['   ' + r for r in rows]
text = '\n'.join(out) + '\n'
open(os.path.join(L, 'cmp-smoke.txt'), 'w', encoding='utf-8', newline='\n').write(text)
sys.stdout.reconfigure(encoding='utf-8', errors='replace'); print(text)

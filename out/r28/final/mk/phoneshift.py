"""The final checker: on the phone the WHOLE WINDOW differs in three states that are not Balls on balls (same.py,
390x800 light). Is it the same content, only scrolled? For each: the pinned part at the top compared as it is, and
the scrolled part below compared at every shift from -800 to 800 px; the best shift and what still differs there.
  python -B out/r28/final/mk/phoneshift.py   -> out/r28/final/logs/phoneshift.txt"""
import os, sys
import numpy as np
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); FINAL = os.path.dirname(HERE)
D = os.path.join(FINAL, 'eyes', 'same'); out = []
for name in ('k-first-group-as-it-opens', 'k-first-group-preset5-2d', 'm-quat4-power4', 'j-turnalong-cut', 'j-pulledplane-2d', 'm-as-the-page-opens', 'learn-tab'):
    a = np.asarray(Image.open(os.path.join(D, 'new-390x800-light-%s-window.png' % name)).convert('RGB')).astype(int)
    b = np.asarray(Image.open(os.path.join(D, 'old-390x800-light-%s-window.png' % name)).convert('RGB')).astype(int)
    d = np.abs(a - b).max(axis=2); n = int((d > 0).sum())
    if n == 0:
        out.append('%-28s whole window: 0 pixels differ' % name); continue
    rows = np.nonzero((d > 0).any(axis=1))[0]; top = int(rows.min())          # everything above `top` is the same (the pinned picture and its controls)
    best = None
    for s in range(-800, 801):
        # new row y against old row y + s, for rows from `top` down
        y0 = max(top, top - s); y1 = min(a.shape[0], a.shape[0] - s)
        if y1 - y0 < 60:
            continue
        dd = int((np.abs(a[y0:y1] - b[y0 + s:y1 + s]).max(axis=2) > 0).sum())
        if best is None or dd < best[1] or (dd == best[1] and y1 - y0 > best[2]):
            best = (s, dd, y1 - y0)
    out.append('%-28s whole window: %d pixels differ as it stands; rows 0 to %d are the same; below, the new page shifted by %d px against the frozen one: %d pixels differ in the %d rows both show'
               % (name, n, top - 1, best[0], best[1], best[2]))
text = '\n'.join(out) + '\n'
open(os.path.join(FINAL, 'logs', 'phoneshift.txt'), 'w', encoding='utf-8', newline='\n').write(text); print(text)

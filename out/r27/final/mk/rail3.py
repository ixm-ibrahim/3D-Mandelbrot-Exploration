"""Round 27, final: the zoom rail's marks, third look: eight fresh runs of "the page as it opens", the frozen page
and the final page taken in turn (old, new, new, old, old, new, new, old), the stage with its controls; every run
compared with the first one, and the other seven with each other.
  python out/r27/final/mk/rail3.py   -> logs/rail3.txt, same/rail3-*.png
(This is the code I ran from the command line for logs/rail3.txt, kept here as a file; the comparison of the other
seven among themselves was run afterwards on the saved pictures and is part of this file now.)"""
import itertools, os, sys
import numpy as np
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import run

if __name__ == '__main__':
    names = []
    for k in (1, 2, 3, 4):
        for tag, page in ((('old', run.BASE), ('new', run.PAGE)) if k % 2 else (('new', run.PAGE), ('old', run.BASE))):
            n = 'rail3-%s-%d' % (tag, k)
            code, text, vals = run.shot(page, [run.UP, dict(js=run.HEAD + "S.q.aa = 4; await settle(); return $('status').textContent;", wait='done', timeout=600, shot=run.OUT + '/same/%s.png' % n, clip='#stage')], n, '1400x950', 'dark')
            names.append((n, code, run.clean(text)))
    lines = ['order of the runs: ' + ', '.join(n for n, _, _ in names), 'all exit 0 and no console errors: %s' % all(c == 0 and ok for _, c, ok in names)]
    im = {n: np.asarray(Image.open(os.path.join(run.ENTRY, 'same', n + '.png')).convert('RGB')).astype(int) for n, _, _ in names}
    ref = names[0][0]
    for n, _, _ in names:
        d = np.abs(im[n] - im[ref]).max(axis=2); ys, xs = np.nonzero(d)
        lines.append('%s against %s: %d pixels differ%s' % (n, ref, len(xs), '' if not len(xs) else ' (x %d to %d, y %d to %d)' % (xs.min(), xs.max(), ys.min(), ys.max())))
    others = [n for n, _, _ in names[1:]]
    worst = max(int((np.abs(im[a] - im[b]).max(axis=2) > 0).sum()) for a, b in itertools.combinations(others, 2))
    lines.append('the other seven among themselves (21 pairs): at most %d pixels differ' % worst)
    text = '\n'.join(lines) + '\n'
    run.write('rail3.txt', text); print(text)

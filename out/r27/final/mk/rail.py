"""Round 27, final: the 106 pixels of the zoom rail that differ in "the page as it opens" with its controls on.
Is that the new page, or does the frozen page differ from itself between two runs? Three fresh runs of each page,
the stage with its controls, every pair compared.
  python out/r27/final/mk/rail.py   -> logs/rail.txt, same/rail-*.png"""
import itertools, os, sys
import numpy as np
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import run

if __name__ == '__main__':
    names = []
    for tag, page in (('new', run.PAGE), ('old', run.BASE)):
        for k in (1, 2, 3):
            n = 'rail-%s-%d' % (tag, k)
            code, text, vals = run.shot(page, [run.UP, dict(js=run.HEAD + "S.q.aa = 4; await settle(); return $('status').textContent;", wait='done', timeout=600, shot='out/r27/final/same/%s.png' % n, clip='#stage')], n, '1400x950', 'dark')
            names.append((n, code, run.clean(text)))
    lines = ['%s: exit %d, %s' % (n, c, 'no console errors' if ok else 'SEE THE LOG') for n, c, ok in names]
    im = {n: np.asarray(Image.open(os.path.join(run.ENTRY, 'same', n + '.png')).convert('RGB')).astype(int) for n, _, _ in names}
    for a, b in itertools.combinations([n for n, _, _ in names], 2):
        d = np.abs(im[a] - im[b]).max(axis=2); ys, xs = np.nonzero(d)
        lines.append('%s against %s: %d pixels differ%s' % (a, b, len(xs), '' if not len(xs) else ' (x %d to %d, y %d to %d)' % (xs.min(), xs.max(), ys.min(), ys.max())))
    text = '\n'.join(lines) + '\n'
    run.write('rail.txt', text); print(text)

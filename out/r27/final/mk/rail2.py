"""Round 27, final: the zoom rail's marks, second look. On each page: the stage as the page opens (A), after the
same picture has been drawn again (B), after a trip to Julia and back (C), after the window was scrolled down and
back up (D). Which of these differ within one page, and across the two pages?
  python out/r27/final/mk/rail2.py   -> logs/rail2.txt, same/rail2-*.png"""
import itertools, os, sys
import numpy as np
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import run

H = run.HEAD
if __name__ == '__main__':
    lines = []; im = {}
    for tag, page in (('new', run.PAGE), ('old', run.BASE)):
        P = 'out/r27/final/same/rail2-%s-' % tag
        steps = [run.UP,
                 dict(js=H + "S.q.aa = 4; await settle(); return 'A ' + $('status').textContent;", wait='done', timeout=600, shot=P + 'A.png', clip='#stage'),
                 dict(js=H + "go(); await settle(); return 'B ' + $('status').textContent;", wait='done', timeout=600, shot=P + 'B.png', clip='#stage'),
                 dict(js=H + "$('mode-j').click(); await settle(); $('mode-m').click(); await settle(); return 'C ' + $('status').textContent + ' mode ' + S.mode;", wait='done', timeout=600, shot=P + 'C.png', clip='#stage'),
                 dict(js=H + "scrollTo(0, 600); await sleep(300); scrollTo(0, 0); await sleep(300); await settle(); return 'D ' + $('status').textContent + ' scroll ' + scrollY;", wait='done', timeout=600, shot=P + 'D.png', clip='#stage')]
        code, text, vals = run.shot(page, steps, 'rail2-' + tag, '1400x950', 'dark')
        lines.append('%s: exit %d, %s; %s' % (page, code, 'no console errors' if run.clean(text) else 'SEE THE LOG', ' | '.join(vals[1:])))
        for k in 'ABCD':
            im[tag + '-' + k] = np.asarray(Image.open(os.path.join(run.ENTRY, 'same', 'rail2-%s-%s.png' % (tag, k))).convert('RGB')).astype(int)
    for a, b in itertools.combinations(sorted(im), 2):
        d = np.abs(im[a] - im[b]).max(axis=2); ys, xs = np.nonzero(d)
        lines.append('%s against %s: %d pixels differ%s' % (a, b, len(xs), '' if not len(xs) else ' (x %d to %d, y %d to %d)' % (xs.min(), xs.max(), ys.min(), ys.max())))
    text = '\n'.join(lines) + '\n'
    run.write('rail2.txt', text); print(text)

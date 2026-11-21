"""The eyes, section 1.4 d, a control: the frozen page against ITSELF, a second run of the same steps as mk/same.py
(wide, dark). Shows which differences of the whole window belong to the page's own run-to-run play (the handle of
the zoom slider over the 2D picture) and not to the overlay.
  python out/r28/final/eyes/mk/same_twice.py   -> same/old2-1400x950-dark-*.png, logs/same-twice.txt"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import eyerun as run
import same
pre = '1400x950-dark'
code, text, vals = run.shot(run.BASE, same.steps('old2', pre), 'same-twice', '1400x950', 'dark')
SD = os.path.join(run.EYES, 'same'); lines = ['frozen page, second run: exit %d, %s' % (code, 'no console errors' if run.clean(text) else 'SEE THE LOG')]
tp = tw = 0
for name, _ in same.STATES:
    if name != 'learn-tab':
        n, shape, fg, box = same.diff(os.path.join(SD, 'old2-%s-%s.png' % (pre, name)), os.path.join(SD, 'old-%s-%s.png' % (pre, name)))
        tp += n or 0
        lines.append('%-40s picture: frozen page run 2 against run 1: %s pixels differ' % (name, n))
    if name in same.WHOLE:
        n, shape, fg, box = same.diff(os.path.join(SD, 'old2-%s-%s-window.png' % (pre, name)), os.path.join(SD, 'old-%s-%s-window.png' % (pre, name)))
        tw += n or 0
        lines.append('%-40s whole window: frozen page run 2 against run 1: %s pixels differ%s' % (name, n, ' in the box %s' % (box,) if box else ''))
        n, shape, fg, box = same.diff(os.path.join(SD, 'old2-%s-%s-window.png' % (pre, name)), os.path.join(SD, 'new-%s-%s-window.png' % (pre, name)))
        lines.append('%-40s whole window: frozen page run 2 against the NEW page: %s pixels differ%s' % (name, n, ' in the box %s' % (box,) if box else ''))
lines.append('TOTAL frozen page against itself: picture alone %d pixels, whole window %d pixels' % (tp, tw))
run.write('same-twice.txt', '\n'.join(lines) + '\n'); print('\n'.join(lines))

# Window shots of the whole shape, Move by move, at every part of a step.
#   python out/r29/learn/mk/look.py <prefix> <size> <theme> <kind> <space> <step k> [approach id] [power] [dots] [c as x,y,z]
# Writes out/r29/learn/shots/<prefix>-<part>.png for the whole step k, every part of step k + 1, and the whole step k + 1,
# and prints the line above the sentence and the sentence for each.
import json, os, sys, time
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE))))
sys.path.insert(0, os.path.join(ROOT, 'out', 'r28', 'final', 'ui', 'mk'))
from hand import Hand

a = sys.argv[1:]
prefix, size, theme, kind, space, k = a[0], a[1], a[2], a[3], int(a[4]), int(a[5])
ap = a[6] if len(a) > 6 and a[6] != '-' else ''
power = float(a[7]) if len(a) > 7 and a[7] != '-' else None
dots = a[8] if len(a) > 8 and a[8] != '-' else 'some'
c = [float(x) for x in a[9].split(',')] if len(a) > 9 else [-1, 0, 0]
page = os.environ.get('LEARN_PAGE', 'dist/r29-learn.html')

with Hand(page, size, theme) as h:
    if ap:
        h.js("const i = L.APPROACHES.findIndex(a => a.id === %s); if (i < 0) throw new Error('no such approach'); S.approach = i; L.refresh(false); return 1;" % json.dumps(ap))
        h.done()
    if power is not None:
        h.js("S.n = %s; L.refresh(false); return 1;" % power)
        h.done()
    st = h.js("return L.learn.shape.set({ on: true, kind: %s, space: %d, c: %s, dots: %s, pos: %d });" % (json.dumps(kind), space, json.dumps(c), json.dumps(dots), k))
    time.sleep(1.2 if space == 3 else 0.4)
    n = len(st['parts'])
    print('parts:', st['parts'], 'shown:', st['shown'])
    stops = [('0-whole', k)] + [('%d-%s' % (i + 1, st['parts'][i].lower().replace(' ', '')), k + (i + 0.55) / n) for i in range(n)] + [('%d-whole' % (n + 1), k + 1)]
    for name, pos in stops:
        s = h.js("return L.learn.shape.set({ pos: %r });" % pos)
        time.sleep(1.0 if space == 3 else 0.35)
        s = h.js("return L.learn.shape.state();")
        h.window_shot('out/r29/learn/shots/%s-%s.png' % (prefix, name))
        print('%-14s | %s | %s   [frame %.1f ms, dots %.1f ms]' % (name, s['where'], s['sentence'], s['ms']['frame'], s['ms']['dots']))
    bad = h.problems()
    print('problems:', bad if bad else 'none')

# On a phone the transport of the whole shape is one row taller than in Version 21. Is the picture still held at the
# top of the window while the controls scroll (85-pin.js lets go when the block is taller than 0.72 of the window)?
#   python out/r29/learn/mk/pin.py     -> for a few window heights, on the frozen page and on the new one
import json, os, sys, time
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE))))
sys.path.insert(0, os.path.join(ROOT, 'out', 'r28', 'final', 'ui', 'mk'))
from hand import Hand

for page in ('dist/r29-learn-b0.html', os.environ.get('LEARN_PAGE', 'dist/r29-learn.html')):
    for height in (560, 600, 640, 667, 700, 740, 800):
        with Hand(page, '390x%d' % height, 'dark') as h:
            h.js("L.learn.shape.set({ on: true, kind: 'j', pos: 2 }); return 1;"); time.sleep(0.4)
            r = h.js("const b = $('learnShapeBar').getBoundingClientRect(), s = $('stage').getBoundingClientRect(), m = document.querySelector('.bench-main').getBoundingClientRect(), c = document.documentElement.classList;"
                     " return { stage: Math.round(s.height), bar: Math.round(b.height), block: Math.round(m.height), share: +(m.height / innerHeight).toFixed(3), held: c.contains('pin-on') && !c.contains('pin-let-go') };")
            print('%-24s window 390 x %d: %s' % (page, height, json.dumps(r)), flush=True)

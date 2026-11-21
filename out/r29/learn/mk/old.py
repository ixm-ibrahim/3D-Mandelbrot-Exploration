# Section 4.2 of docs/ROUND29-LEARN.md: nothing old changed.
#   python out/r29/learn/mk/old.py [size] [theme] [set]        set: shape | point | lab | all
# The same list of states is gone through on the frozen page (dist/r29-learn-b0.html, built from base21a alone) and
# on the new page. For each state the picture (the stage, cut out of a window shot) is compared pixel by pixel, and
# the words word for word. On the new page the whole shape is set to Each step: At once first.
import io, json, os, sys, time
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE))))
sys.path.insert(0, os.path.join(ROOT, 'out', 'r28', 'final', 'ui', 'mk'))
from hand import Hand
import numpy as np
from PIL import Image

size = sys.argv[1] if len(sys.argv) > 1 else '1400x950'
theme = sys.argv[2] if len(sys.argv) > 2 else 'dark'
which = sys.argv[3] if len(sys.argv) > 3 else 'all'
NEW = os.environ.get('LEARN_PAGE', 'dist/r29-learn.html')
OLD = 'dist/r29-learn-b0.html'
OUT = os.path.join('out', 'r29', 'learn', 'old', '%s-%s' % (size, theme))
os.makedirs(os.path.join(ROOT, OUT), exist_ok=True)

WORDS = """const pick = id => { const e = $(id); return e && vis(e) ? e.textContent.replace(/\\s+/g, ' ').trim() : null; };
return { where: pick('learnShapeWhere') || pick('learnWhere'), say: pick('learnShapeSay') || pick('learnSay'), hint: pick('learnHint'), stageNote: pick('learnShapeNote'),
  intro: pick('learnShapeIntro'), helpJ: pick('learnShapeHelpJ'), helpBoth: pick('learnShapeHelpBoth'), rule: pick('learnShapeRule'), notice: pick('learnShapeNotice') || pick('learnNotice'),
  note: pick('learnNote'), hidden: pick('learnHiddenNote'), ticks: pick('learnTicks'), summary: document.querySelector('#learnPanel summary').textContent,
  gl: (() => { const c = document.querySelector('.learn-shape-gl'); return c && !c.hidden ? [c.width, c.height] : null; })() };"""

states = []
if which in ('shape', 'all'):
    rabbit = [-0.1226, 0.7449, 0]
    for space in (2, 3):
        for kind, c in (('m', [-0.4, 0.3, 0]), ('j', [-1, 0, 0]), ('both', rabbit), ('j', [-0.3, 0.2, 0.1] if space == 3 else [0.9, 0.8, 0])):
            for pos in (0, 1, 2, 2.5, 5, 7.35, 16) if kind != 'both' else (0, 3, 3.5, 9):
                states.append(('shape-%dd-%s-%s-%s' % (space, kind, 'x'.join(str(v) for v in c), pos),
                               "L.learn.shape.set({ on: true, each: 'once', kind: %s, space: %d, c: %s, pos: %r }); return 1;" % (json.dumps(kind), space, json.dumps(c), pos), 1.6 if space == 3 else 0.5))
    # another approach and power in 3D, a power that is not whole on the page
    states.append(('shape-3d-lathe-n3-j-4.5', "S.approach = L.APPROACHES.findIndex(a => a.id === 'lathe'); S.n = 3; L.refresh(false); L.learn.shape.set({ on: true, each: 'once', kind: 'j', space: 3, c: [-0.3, 0.2, 0.1], pos: 4.5 }); return 1;", 2.0))
    states.append(('shape-2d-n2.5-m-3.5', "S.approach = 0; S.n = 2.5; L.refresh(false); L.learn.shape.set({ on: true, each: 'once', kind: 'm', space: 2, pos: 3.5 }); return 1;", 0.8))
    states.append(('shape-reset', "S.n = 2; L.refresh(false); L.learn.shape.set({ on: true, each: 'once', kind: 'm', space: 2, pos: 0 }); return 1;", 0.5))
if which in ('point', 'all'):
    first = "L.learn.shape.set({ on: false }); L.learn.setOn(true); "
    for space in (1, 2, 3):
        for show in ('point', 'circle', 'all'):
            for hid in ((False, True) if space < 3 else (False,)):
                for mv, t in ((0, 0), (0, 0.5), (1, 0.4), (9, 1)):
                    states.append(('point-%dd-%s-%s-%s-%s' % (space, show, 'hid' if hid else 'flat', mv, t),
                                   first + "L.learn.set({ space: %d, show: %s, hidden: %s }); L.learn.again(); L.learn.goto(%d, %r); return 1;" % (space, json.dumps(show), 'true' if hid else 'false', mv, t), 0.35))
            states.append(('point-%dd-%s-step2' % (space, show), first + "L.learn.set({ space: %d, show: %s, hidden: false }); L.learn.again(); L.learn.next(); L.learn.goto(1, 0.6); return 1;" % (space, json.dumps(show)), 0.35))
    states.append(('point-3d-lathe-all', first + "S.approach = L.APPROACHES.findIndex(a => a.id === 'lathe'); L.refresh(false); L.learn.set({ space: 3, show: 'all' }); L.learn.again(); L.learn.goto(0, 0.5); return 1;", 0.5))
    states.append(('point-reset', "S.approach = 0; L.refresh(false); L.learn.reset(); return 1;", 'done'))
if which in ('lab', 'all'):
    states.append(('lab-mandelbrot', "L.learn.setOn(false); $('mode-m').click(); return 1;", 'done'))
    states.append(('lab-julia', "$('mode-j').click(); return 1;", 'done'))
    states.append(('lab-julia-lathe', "S.approach = L.APPROACHES.findIndex(a => a.id === 'lathe'); L.refresh(true); return 1;", 'done'))
    states.append(('lab-kleinian', "S.approach = 0; $('mode-k').click(); return 1;", 'done'))
    states.append(('lab-balls', "L.ballsShow(); return 1;", 'done'))
    states.append(('lab-back', "$('mode-m').click(); return 1;", 'done'))


def run(page, tag):
    got = {}
    with Hand(page, size, theme) as h:
        for name, js, wait in states:
            h.js(js)
            if wait == 'done':
                time.sleep(0.4); h.done(); time.sleep(0.3)
            else:
                time.sleep(wait)
                if name.startswith('shape'):
                    h.js("L.learn.shape.state(); return 1;")      # the finished picture
                    time.sleep(0.25)
            words = h.js(WORDS) if not name.startswith('lab') else {'status': h.js("return $('status').textContent;")}
            path = os.path.join(OUT, '%s--%s.png' % (name, tag))
            h.shot(path, '#stage')
            got[name] = (words, path)
        bad = h.problems()
        print('%s: %d states, console: %s' % (page, len(states), json.dumps(bad[:5]) if bad else 'clean'), flush=True)
    return got


old = run(OLD, 'old')
new = run(NEW, 'new')
lines = ['%s against %s, %s %s, %d states' % (NEW, OLD, size, theme, len(states))]
same_pic = same_words = 0
for name, js, wait in states:
    a = np.asarray(Image.open(os.path.join(ROOT, old[name][1])).convert('RGB')).astype(int)
    b = np.asarray(Image.open(os.path.join(ROOT, new[name][1])).convert('RGB')).astype(int)
    if a.shape != b.shape:
        lines.append('PICTURE %s: sizes differ, %s and %s' % (name, a.shape, b.shape)); continue
    d = np.abs(a - b).max(axis=2)
    n = int((d > 0).sum())
    if n:
        lines.append('PICTURE %s: %d of %d pixels differ (largest step %d of 255; %d differ by more than 2)  gl buffers %s / %s' % (name, n, d.size, int(d.max()), int((d > 2).sum()), old[name][0].get('gl'), new[name][0].get('gl')))
    else:
        same_pic += 1
        os.remove(os.path.join(ROOT, new[name][1]))        # identical: one copy is enough
    wa, wb = old[name][0], new[name][0]
    if wa == wb:
        same_words += 1
    else:
        for k in sorted(set(wa) | set(wb)):
            if wa.get(k) != wb.get(k):
                lines.append('WORDS %s, %s:\n    frozen: %s\n    new:    %s' % (name, k, wa.get(k), wb.get(k)))
lines.append('pictures identical pixel for pixel: %d of %d;  words identical: %d of %d' % (same_pic, len(states), same_words, len(states)))
print('\n'.join(lines))
io.open(os.path.join(ROOT, 'out', 'r29', 'learn', 'old-%s-%s-%s.txt' % (which, size, theme)), 'w', encoding='utf-8', newline='\n').write('\n'.join(lines) + '\n')

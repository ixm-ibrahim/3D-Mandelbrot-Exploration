# Section 4.4 of docs/ROUND29-LEARN.md: how long a frame takes with Dots: Many.
#   python out/r29/learn/mk/speed.py [size] [theme]
# How it is measured: one step is played at the speed Normal (the page's own clock, requestAnimationFrame). A second
# requestAnimationFrame loop of the test reads, once a frame, what the page itself measured for its last redraw
# (LEARN.shape.timing(): `frame` is the time from the start to the end of learnShapeDraw, in which the backdrop, the
# dots and everything over them are drawn; `dots` the part of it spent on the dots), where the slider stood, and the
# time since the frame before (the browser's own frame clock: on this screen 16.7 ms when nothing holds it up, so
# this number also shows time that is spent outside the script, by the graphics card).
# Frames are sorted by the part of the step the slider stood in. "moving" = the parts in which the dots move
# (where the dots are now, the moves of the rule, back home).
import io, json, os, sys, time
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE))))
sys.path.insert(0, os.path.join(ROOT, 'out', 'r28', 'final', 'ui', 'mk'))
from hand import Hand

size = sys.argv[1] if len(sys.argv) > 1 else '1400x950'
theme = sys.argv[2] if len(sys.argv) > 2 else 'dark'
page = os.environ.get('LEARN_PAGE', 'dist/r29-learn.html')
PROBE = """
const SH = L.learn.shape, rows = [];
let last = performance.now();
await new Promise(done => {
  const tick = now => { const m = SH.timing(); rows.push([m.pos, m.frame, m.dots, now - last]); last = now; if (m.playing) requestAnimationFrame(tick); else done(); };
  SH.set({ pos: %d }); SH.state();
  setTimeout(() => { $('learnShapeFwd').click(); last = performance.now(); requestAnimationFrame(tick); }, 700);
});
return rows;"""
lines = []


def say(s):
    print(s, flush=True); lines.append(s)


def pct(v, p):
    v = sorted(v)
    return v[min(len(v) - 1, int(p * len(v)))] if v else float('nan')


cases = []
for kind in ('j', 'm', 'both'):
    cases.append((2, kind, 'mercator', 2))
cases.append((2, 'j', 'mercator', 2.5))
for ap in ('mercator', 'lathe', 'fold', 'softfold', 'kleinsq2', 'pulledplane', 'alongonce'):
    for kind in (('j', 'm', 'both') if ap in ('mercator', 'pulledplane') else ('j',)):
        cases.append((3, kind, ap, 2))
worst = {2: [0, 0], 3: [0, 0]}
with Hand(page, size, theme) as h:
    ids = h.js("return L.APPROACHES.map(a => a.id);")
    say('%s %s %s, Dots: Many, one step played at Normal' % (page, size, theme))
    say('space kind approach     n   step | dots on | frames | moving parts: draw ms median / 95%% / max  (dots ms max) | frame clock ms median / 95%% / max | throwing out: draw ms max, clock ms 95%% / max')
    for space, kind, ap, n in cases:
        h.js("S.approach = %d; S.n = %r; L.refresh(false); L.learn.shape.set({ on: true, each: 'moves', dots: 'many', kind: %s, space: %d, c: %s, pos: 0 }); return 1;" % (
            ids.index(ap), n, json.dumps(kind), space, json.dumps([-0.3, 0.2, 0.1] if space == 3 else [-1, 0, 0])))
        time.sleep(1.5 if space == 3 else 0.5)
        for k in (0, 2):
            st = h.js("return L.learn.shape.set({ pos: %d });" % k)
            parts = len(st['parts']); on = sum(x['on'] for x in st['shown'])
            rows = h.js(PROBE % k)
            rows = rows[2:]                                   # the first two frames carry the click
            mov = [r for r in rows if 0 < (r[0] - k) < 1 and int((r[0] - k) * parts) != parts - 2]
            gone = [r for r in rows if 0 < (r[0] - k) < 1 and int((r[0] - k) * parts) == parts - 2]
            d = [r[1] for r in mov]; dd = [r[2] for r in mov]; c = [r[3] for r in mov]
            say('%dD    %-4s %-12s %-3s %d    | %5d   | %4d   | %5.1f / %5.1f / %5.1f   (%4.1f)            | %5.1f / %5.1f / %5.1f     | %5.1f, %5.1f / %5.1f' % (
                space, kind, ap, n, k + 1, on, len(rows), pct(d, 0.5), pct(d, 0.95), max(d), max(dd), pct(c, 0.5), pct(c, 0.95), max(c),
                max(r[1] for r in gone) if gone else 0, pct([r[3] for r in gone], 0.95), max(r[3] for r in gone) if gone else 0))
            worst[space][0] = max(worst[space][0], max(d)); worst[space][1] = max(worst[space][1], pct(c, 0.95))
    h.js("S.approach = 0; S.n = 2; L.refresh(false); return 1;")
    say('')
    say('largest draw time of a frame of the moving parts: 2D %.1f ms (limit 20), 3D %.1f ms (limit 35)' % (worst[2][0], worst[3][0]))
    say('95%% of the frame clock in the moving parts, worst case: 2D %.1f ms, 3D %.1f ms' % (worst[2][1], worst[3][1]))
    bad = h.problems()
    say('console: ' + (json.dumps(bad[:6]) if bad else 'no error or warning'))
io.open(os.path.join(ROOT, 'out', 'r29', 'learn', 'speed-%s-%s.txt' % (size, theme)), 'w', encoding='utf-8', newline='\n').write('\n'.join(lines) + '\n')

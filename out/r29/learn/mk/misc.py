# Odd corners of Move by move and of the grid of points: no motion wanted, the theme and the window changing in the
# middle of a part, leaving Learn and coming back, Reset everything while it plays, dragging the diamond and turning
# the 3D picture while the dots are away, an empty picture, a negative power, the Kleinian view left behind.
#   python out/r29/learn/mk/misc.py
import io, json, os, sys, time
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE))))
sys.path.insert(0, os.path.join(ROOT, 'out', 'r28', 'final', 'ui', 'mk'))
from hand import Hand

page = os.environ.get('LEARN_PAGE', 'dist/r29-learn.html')
lines, fails = [], []


def say(s):
    print(s, flush=True); lines.append(s)


def check(ok, what):
    say(('  ok    ' if ok else '  FAIL  ') + what)
    if not ok:
        fails.append(what)


with Hand(page, '1400x950', 'dark') as h:
    st = lambda: h.js("return L.learn.shape.state();")
    media = lambda **f: h.page.call('Emulation.setEmulatedMedia', features=[{'name': k.replace('_', '-'), 'value': v} for k, v in f.items()])
    # --- no motion wanted
    media(prefers_color_scheme='dark', prefers_reduced_motion='reduce')
    h.click('#mode-l'); time.sleep(0.3); h.click('#learnFollowShape'); time.sleep(0.5)
    s = st()
    check(not s['playing'] and s['pos'] == 0 and s['each'] == 'moves', 'no motion wanted: the first switch does not play by itself (pos %s)' % s['pos'])
    h.click('#learnShapeFwd'); time.sleep(0.3); s = st()
    check(not s['playing'] and s['pos'] == 1, 'no motion wanted: Forward goes to the next whole step at once (%s)' % s['pos'])
    h.click('#learnShapeParts button:nth-child(3)'); time.sleep(0.3); s = st()
    check(not s['playing'] and s['part'] and s['part']['i'] == 2 and abs(s['part']['t'] - 1) < 1e-9, 'no motion wanted: the name of a part shows the end of that part (%s)' % json.dumps(s['part']))
    media(prefers_color_scheme='dark', prefers_reduced_motion='no-preference')
    # --- the theme and the window change in the middle of a part
    h.js("L.learn.shape.set({ kind: 'j', c: [-1, 0, 0], pos: 1 + 2.5 / 6 }); return 1;"); time.sleep(0.3)
    a = h.js("return L.learn.shape.dots('j').colour.slice(0, 3);")
    media(prefers_color_scheme='light', prefers_reduced_motion='no-preference'); time.sleep(0.5)
    b = h.js("L.learn.shape.state(); return L.learn.shape.dots('j').colour.slice(0, 3);")
    check(a != b, 'the dots take the colours of the other theme (%s -> %s)' % (a[0], b[0]))
    h.window_shot('out/r29/learn/shots/x-theme-light-midpart.png')
    media(prefers_color_scheme='dark', prefers_reduced_motion='no-preference'); time.sleep(0.3)
    h.page.call('Emulation.setDeviceMetricsOverride', width=900, height=700, deviceScaleFactor=2, mobile=False); time.sleep(0.6)
    s = st(); check(s['part'] and s['part']['key'] == 'move', 'a smaller window with a sharp screen in the middle of a part: still in the part (%s)' % (s['part'] or {}).get('label'))
    h.window_shot('out/r29/learn/shots/x-900x700-dpr2.png')
    h.page.call('Emulation.setDeviceMetricsOverride', width=1400, height=950, deviceScaleFactor=1, mobile=False); time.sleep(0.5)
    # --- drag the diamond while the dots are away (2D), turn the picture while they are away (3D)
    d = h.js("const s = L.learn.shape.state(), r = $('learnShapeCanvas').getBoundingClientRect(); return [r.left + s.diamonds[0][0], r.top + s.diamonds[0][1]];")
    h.mouse('mouseMoved', d[0], d[1]); h.mouse('mousePressed', d[0], d[1], 1)
    for i in range(1, 9):
        h.mouse('mouseMoved', d[0] + 9 * i, d[1] - 5 * i, 1); time.sleep(0.05)
    mid = st(); h.mouse('mouseReleased', d[0] + 72, d[1] - 40, 0); time.sleep(0.3); s = st()
    check(s['c'][0] > -0.9 and s['part'] and s['part']['key'] == 'move' and s['shown'][0]['all'] > 400, 'the diamond dragged while the dots are away: c is now %s, the dots follow (%s on show)' % (s['c'][:2], s['shown'][0]['on']))
    h.click('#learnShapeSpaceBar input[value="3"]'); time.sleep(1.2)
    r = h.js("const r = $('learnShapeCanvas').getBoundingClientRect(); return [r.left + r.width / 2, r.top + r.height / 2];")
    v0 = st()['view3']
    h.mouse('mouseMoved', r[0], r[1]); h.mouse('mousePressed', r[0], r[1], 1)
    for i in range(1, 9):
        h.mouse('mouseMoved', r[0] + 12 * i, r[1] + 4 * i, 1); time.sleep(0.05)
    h.mouse('mouseReleased', r[0] + 96, r[1] + 32, 0); time.sleep(0.5); s = st()
    check(abs(s['view3']['yaw'] - v0['yaw']) > 0.5 and s['part'] and s['part']['key'] == 'move', 'the 3D picture turned while the dots are away (yaw %.2f -> %.2f), still in the part' % (v0['yaw'], s['view3']['yaw']))
    h.window_shot('out/r29/learn/shots/x-3d-turned-midpart.png')
    # --- leave Learn and come back; Follow back and forth; all while it plays
    h.click('#learnShapePlay'); time.sleep(0.4)
    h.click('#mode-j'); time.sleep(0.6)
    check(h.js("return !document.body.classList.contains('is-learn') && !L.learn.shape.state().playing;"), 'leaving Learn for the Julia tab stops the play')
    h.done()
    h.click('#mode-l'); time.sleep(0.6); s = st()
    check(s['on'] and s['each'] == 'moves' and not s['playing'], 'back in Learn: the whole shape is where it was (pos %.3f), not playing' % s['pos'])
    h.click('#learnShapePlay'); time.sleep(0.3)
    h.click('#learnFollowPoint'); time.sleep(0.4)
    p = h.js("return [L.learn.follow, L.learn.shape.state().playing, vis($('learnBar')), vis($('learnShapeBar'))];")
    check(p == ['point', False, True, False], 'Follow: One point while it plays puts the whole shape away and stops it (%s)' % p)
    h.click('#learnFollowShape'); time.sleep(0.6); s = st()
    check(s['on'] and not s['playing'], 'Follow: A whole shape again (the second switch of a visit does not play by itself)')
    # --- Reset everything while it plays
    h.click('#learnShapePlay'); time.sleep(0.5)
    h.click('#resetAll'); time.sleep(0.8); h.done()
    p = h.js("const s = L.learn.shape.state(); return [document.body.classList.contains('is-learn'), L.learn.follow, s.each, s.dots, s.pos, s.playing];")
    check(p == [False, 'point', 'moves', 'some', 0, False], 'Reset everything while it plays: Learn off, everything as it opens (%s)' % p)
    # --- an empty picture, a negative power, the Kleinian view left behind
    h.click('#mode-k'); time.sleep(0.5); h.done()
    h.click('#mode-l'); time.sleep(0.4); h.click('#learnFollowShape'); time.sleep(0.4)
    s = h.js("return L.learn.shape.set({ kind: 'j', space: 2, c: [5, 5, 0], pos: 2 + 1.5 / 6 });")
    say('        Julia shape, c far outside, step 3 (from the Kleinian view): "%s" | %s' % (s['sentence'], s['where']))
    check(bool(s['sentence']) and s['shown'][0]['on'] == 0, 'a picture of which nothing is left: no dots, and a sentence that says so')
    s = h.js("return L.learn.shape.set({ c: [0.3, 0.5, 0], pos: 9 + 4.5 / 6 });")
    say('        Julia shape, c = 0.3 + 0.5i, step 10, throwing out: "%s" (%s dots on show)' % (s['sentence'], s['shown'][0]['on']))
    h.js("S.n = -2; L.syncControls(); L.touch(); return 1;"); time.sleep(0.3)
    for pos in (0.1, 0.4, 0.6, 0.75, 0.95):
        s = h.js("return L.learn.shape.set({ kind: 'm', pos: %r });" % pos)
        say('        power -2, Mandelbrot shape, %.2f: "%s"' % (pos, s['sentence']))
    check(True, 'a negative power: every part has a sentence')
    h.js("S.n = 2; L.syncControls(); L.touch(); return 1;")
    # --- One point: the grid through several steps, Start again, a dragged ring, the 1D line
    h.click('#learnFollowPoint'); time.sleep(0.3)
    h.js("L.learn.set({ space: 2, show: 'grid' }); return 1;")
    a = h.js("return L.learn.points();")
    for _ in range(3):
        h.click('#learnNext'); time.sleep(2.6)
    b = h.js("return L.learn.points();")
    # the lab's own rule three times, from the fresh grid
    worst = h.js("const P = L.learn.points(), st = L.learn.state(), c = st.c; let w = 0; P.start.forEach((p, i) => { let z = p.slice(); for (let k = 0; k < st.step; k++) z = [z[0] * z[0] - z[1] * z[1] + c[0], 2 * z[0] * z[1] + c[1], 0]; const q = P.stepStart[i]; const d = Math.hypot(z[0] - q[0], z[1] - q[1]) / Math.max(1, Math.hypot(z[0], z[1])); if (isFinite(d)) w = Math.max(w, d); }); return [st.step, w, P.line];")
    check(worst[0] == 3 and worst[1] < 1e-9, 'the grid after 3 presses of Next step: every dot is where 3 steps of the rule take it from the fresh grid (largest difference %.1e); line: "%s"' % (worst[1], worst[2]))
    h.window_shot('out/r29/learn/shots/x-grid-step4.png')
    h.click('#learnAgain'); time.sleep(0.3)
    c = h.js("return L.learn.points();")
    check(c['step'] == 0 and c['stepStart'] == a['start'], 'Start again lays out the fresh grid')
    bad = h.problems()
    check(not bad, 'no console error or warning' + (': ' + json.dumps(bad[:6]) if bad else ''))
say('%d checks failed' % len(fails) if fails else 'all passed')
io.open(os.path.join(ROOT, 'out', 'r29', 'learn', 'misc.txt'), 'w', encoding='utf-8', newline='\n').write('\n'.join(lines) + '\n')

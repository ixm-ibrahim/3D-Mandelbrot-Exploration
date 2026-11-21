# Section 4.3 of docs/ROUND29-LEARN.md: the transport of the whole shape with Each step: Move by move, by a real mouse
# and real keys. Reading the state is done with JavaScript; nothing is set by JavaScript except where the line says so.
#   python out/r29/learn/mk/transport.py [size] [theme]
import io, json, os, sys, time
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE))))
sys.path.insert(0, os.path.join(ROOT, 'out', 'r28', 'final', 'ui', 'mk'))
from hand import Hand

size = sys.argv[1] if len(sys.argv) > 1 else '1400x950'
theme = sys.argv[2] if len(sys.argv) > 2 else 'dark'
page = os.environ.get('LEARN_PAGE', 'dist/r29-learn.html')
lines, fails = [], []


def say(s):
    print(s, flush=True); lines.append(s)


def check(ok, what):
    say(('  ok    ' if ok else '  FAIL  ') + what)
    if not ok:
        fails.append(what)


with Hand(page, size, theme) as h:
    st = lambda: h.js("return L.learn.shape.state();")
    # does what is on the screen fit the words? the part the words name is the part the dots are drawn in, the line
    # above the sentence names the same step, and the sentence is there
    def fits(tag):
        s = st()
        kinds = ['m', 'j'] if s['kind'] == 'both' else [s['kind']]
        d = h.js("return L.learn.shape.dotsAt(%s);" % json.dumps(kinds[0]))
        a = s['part']['key'] if s['part'] else None
        b = d['part']['key'] if d['part'] else None
        whole = abs(s['pos'] - round(s['pos'])) < 1e-9
        ok = bool(s['sentence']) and a == b and (whole == (a is None) or s['gone'] != '' or s['each'] == 'once') and ('Step %d of' % (round(s['pos']) if whole else int(s['pos']) + 1)) in s['where']
        if not ok:
            check(False, '%s: words and picture apart: pos %.4f, words in part %s, dots in part %s, where "%s", sentence "%s"' % (tag, s['pos'], a, b, s['where'], s['sentence']))
        return s

    def until_stopped(most=40):
        t0 = time.time()
        while time.time() - t0 < most:
            if not h.js("return L.learn.shape.state().playing;"):
                return time.time() - t0
            time.sleep(0.02)
        return None

    say('--- %s %s %s' % (page, size, theme))
    h.click('#mode-l'); time.sleep(0.3)
    h.click('#learnFollowShape'); time.sleep(0.4)
    s = st()
    check(s['on'] and s['each'] == 'moves' and s['dots'] == 'some', 'A whole shape opens with Each step: Move by move and Dots: Some (each %s, dots %s)' % (s['each'], s['dots']))
    check(s['playing'], 'the first switch by hand plays by itself')
    seen = []
    t0 = time.time()
    while time.time() - t0 < 9:
        s = fits('first play'); seen.append((s['pos'], s['part']['key'] if s['part'] else 'whole'))
        time.sleep(0.12)
    keys = [k for p, k in seen]
    order = [k for i, k in enumerate(keys) if i == 0 or keys[i - 1] != k]
    say('        parts met in the first 9 s of the play: ' + ' > '.join(order))
    check(all(b[0] >= a[0] - 1e-9 for a, b in zip(seen, seen[1:])), 'the play only goes forwards')
    h.click('#learnShapePlay'); time.sleep(0.2)
    s = fits('paused')
    check(not s['playing'], 'Pause stops the play (at %.3f)' % s['pos'])
    p0 = s['pos']
    time.sleep(0.4)
    check(abs(st()['pos'] - p0) < 1e-9, 'paused: the slider stays where it is')
    h.click('#learnShapeBack'); time.sleep(0.2)
    s = fits('back')
    check(abs(s['pos'] - (int(p0 - 1e-9) if p0 > int(p0) + 1e-9 else int(p0) - 1)) < 1e-9, 'Back goes to the whole step before (%.3f -> %s)' % (p0, s['pos']))
    # Forward plays one whole step: how long, at each speed
    for speed, want in (('normal', 4.6), ('fast', 2.3), ('slow', 9.2)):
        h.js("const e = $('learnShapeSpeed'); e.focus(); return 1;")
        cur = h.js("return $('learnShapeSpeed').value;")
        order3 = ['slow', 'normal', 'fast']
        for _ in range(abs(order3.index(speed) - order3.index(cur))):
            h.key('ArrowDown' if order3.index(speed) > order3.index(cur) else 'ArrowUp')
        time.sleep(0.15)
        got = h.js("return [$('learnShapeSpeed').value, L.learn.speed];")
        a = st()['pos']
        h.click('#learnShapeFwd')
        took = until_stopped()
        s = fits('forward ' + speed)
        check(got == [speed, speed] and took is not None and abs(s['pos'] - (int(a) + 1)) < 1e-9 and abs(took - want) < 0.12 * want + 0.35,
              'Speed %s (chosen with the keys): Forward plays one whole step, %.3f -> %s, in %s s (wanted about %.1f, plus %.1f s of rest in a play from end to end)' % (
                  speed, a, s['pos'], 'no end' if took is None else '%.2f' % took, want, {'normal': 0.4, 'fast': 0.2, 'slow': 0.8}[speed]))
    h.js("$('learnShapeSpeed').focus(); return 1;"); h.key('ArrowDown'); time.sleep(0.1)       # back to Normal (from Slow)
    check(h.js("return L.learn.speed;") == 'normal', 'Speed back at Normal')
    # every tick
    bad = []
    for j in list(range(17)) + [5]:
        h.click('#learnShapeTicks button:nth-child(%d)' % (j + 1)); time.sleep(0.12)
        s = fits('tick %d' % j)
        if abs(s['pos'] - j) > 1e-9 or s['playing']:
            bad.append(j)
    check(not bad, 'every tick of the scale goes to its whole step' + (' (not: %s)' % bad if bad else ''))
    h.click('#learnShapeAgain'); time.sleep(0.2)
    check(st()['pos'] == 0, 'Start again goes to step 0')
    # the names of the parts: each plays its part and stops at the part's end, naming that part
    if h.js("return vis($('learnShapeParts'));"):
        n = len(st()['parts']); bad = []
        h.click('#learnShapeTicks button:nth-child(3)'); time.sleep(0.15)
        for i in range(n):
            h.click('#learnShapeParts button:nth-child(%d)' % (i + 1))
            took = until_stopped(8)
            s = fits('part %d' % i)
            want = 2 + (i + 1) / n
            ok = took is not None and abs(s['pos'] - want) < 1e-9 and (i == n - 1 or (s['part'] and s['part']['i'] == i and abs(s['part']['t'] - 1) < 1e-6))
            if not ok:
                bad.append((i, s['pos'], s['part']))
        check(not bad, 'the %d names of the parts each play their own part of step 3 and stop at its end' % n + (' (not: %s)' % bad if bad else ''))
    else:
        say('        (the row of part names is not on show at this size)')
    # the slider by hand, slowly forwards and backwards through all the parts of two steps
    h.click('#learnShapeTicks button:nth-child(2)'); time.sleep(0.15)
    x0, y, b = h.thumb('#learnShapePos')
    per = (b[2] - 16) / 16.0
    h.mouse('mouseMoved', x0, y); h.mouse('mousePressed', x0, y, 1); time.sleep(0.05)
    met, x = [], x0
    steps = int(2 * per)
    for dx in list(range(1, steps + 1)) + list(range(steps - 1, -1, -1)):
        h.mouse('mouseMoved', x0 + dx, y, 1); time.sleep(0.03)
        s = fits('slider')
        met.append((s['pos'], s['part']['key'] if s['part'] else 'whole', s['part']['i'] if s['part'] else -1))
    h.mouse('mouseReleased', x0, y, 0); time.sleep(0.2)
    half = len(met) // 2
    fw = [k for i, (p, k, n_) in enumerate(met[:half]) if i == 0 or met[i - 1][1] != k]
    bw = [k for i, (p, k, n_) in enumerate(met[half:]) if i == 0 or met[half + i - 1][1] != k]
    say('        %d slider places, %.1f pixels to a step; forwards: %s' % (len(met), per, ' > '.join(fw)))
    say('        backwards: %s' % ' > '.join(bw))
    partsN = len(st()['parts'])
    idx = sorted(set(n_ for p, k, n_ in met if n_ >= 0))
    check(idx == list(range(partsN)), 'dragging the slider by hand meets every part of a step (%s of %d)' % (idx, partsN))
    check(all(b[0] >= a[0] - 1e-9 for a, b in zip(met[:half], met[1:half])) and all(b[0] <= a[0] + 1e-9 for a, b in zip(met[half:], met[half + 1:])), 'forwards the slider only goes forwards, backwards only backwards')
    # the keys: on the slider the arrows go by whole steps; on the picture the space bar plays and pauses
    h.click('#learnShapeTicks button:nth-child(4)'); time.sleep(0.1)
    h.js("$('learnShapePos').focus(); return 1;")
    h.key('ArrowRight'); a = st()['pos']; h.key('ArrowRight'); b2 = st()['pos']; h.key('ArrowLeft'); c2 = st()['pos']
    check((a, b2, c2) == (4, 5, 4), 'arrow keys on the slider go by whole steps (3 -> %s -> %s -> %s)' % (a, b2, c2))
    h.js("L.learn.shape.set({ pos: 4.4 }); $('learnShapePos').focus(); return 1;")
    h.key('ArrowRight'); a = st()['pos']
    h.js("L.learn.shape.set({ pos: 4.4 }); return 1;"); h.key('ArrowLeft'); b2 = st()['pos']
    check((a, b2) == (5, 4), 'from inside a step the arrows go to the next and to the last whole step (4.4 -> %s, 4.4 -> %s)' % (a, b2))
    h.js("$('learnShapeCanvas').focus(); return 1;")
    h.key(' '); time.sleep(0.5); a = st(); h.key(' '); time.sleep(0.2); b2 = st()
    check(a['playing'] and not b2['playing'] and b2['pos'] > 4, 'the space bar on the picture plays and pauses (%.3f)' % b2['pos'])
    # changes while it plays, and while it stands
    def change(tag, act, playing):
        act(); time.sleep(0.45)
        s = fits(tag + (' while it plays' if playing else ' while it stands'))
        if playing and not s['playing'] and s['pos'] < 16:
            check(False, '%s: the play stopped at %.3f' % (tag, s['pos']))
        return s
    ids = h.js("return L.APPROACHES.map(a => a.id);")
    def setsel(sel, down):
        h.js("$(%s).focus(); return 1;" % json.dumps(sel)); h.key('ArrowDown' if down else 'ArrowUp')
    for playing in (True, False):
        h.click('#learnShapeTicks button:nth-child(2)'); time.sleep(0.1)
        if playing:
            h.click('#learnShapePlay'); time.sleep(0.3)
        n0 = len(fails)
        for kind in ('j', 'both', 'm'):
            change('shape ' + kind, lambda: h.click('#learnShapeKindBar input[value=%s]' % kind), playing)
        change('3D', lambda: h.click('#learnShapeSpaceBar input[value="3"]'), playing)
        change('Dots many', lambda: setsel('learnShapeDotsBar', True), playing)
        check(st()['dots'] == 'many', 'Dots chosen with the keys: %s' % st()['dots'])
        change('Each step at once', lambda: h.click('#learnShapeEachBar input[value=once]'), playing)
        check(st()['each'] == 'once' and st()['part'] is None, 'Each step: At once has no parts')
        change('Each step move by move', lambda: h.click('#learnShapeEachBar input[value=moves]'), playing)
        change('shape both in 3D', lambda: h.click('#learnShapeKindBar input[value=both]'), playing)
        change('another c (set by the test handle)', lambda: h.js("L.learn.shape.set({ c: [-0.12, 0.74, 0.2] }); return 1;"), playing)
        change('the power 3 (set by the lab\'s state, then touch())', lambda: h.js("S.n = 3; L.syncControls(); L.touch(); return 1;"), playing)
        for ap in ('lathe', 'pulledplane', 'fold'):
            change('approach ' + ap + ' (set by the lab\'s state, then refresh())', lambda: h.js("S.approach = %d; L.refresh(false); return 1;" % ids.index(ap)), playing)
        change('2D', lambda: h.click('#learnShapeSpaceBar input[value="2"]'), playing)
        change('Dots few', lambda: (setsel('learnShapeDotsBar', False), setsel('learnShapeDotsBar', False)), playing)
        change('the power 2', lambda: h.js("S.n = 2; S.approach = 0; L.syncControls(); L.refresh(false); return 1;"), playing)
        change('Dots some', lambda: setsel('learnShapeDotsBar', True), playing)
        change('shape m', lambda: h.click('#learnShapeKindBar input[value=m]'), playing)
        s = st()
        if playing:
            check(s['playing'] or s['pos'] >= 16, 'the play went on through every change (now at %.2f)' % s['pos'])
            h.click('#learnShapePlay'); time.sleep(0.2)
        check(len(fails) == n0, 'kind, 2D/3D, Dots, Each step, c, the power and the approach changed while it %s: the words fit the picture every time' % ('plays' if playing else 'stands'))
    # the panel's copies of the two choices follow the transport's, and the other way round
    h.click('#learnShapeEach input[value=once]'); time.sleep(0.2)
    a = h.js("return [L.learn.shape.state().each, document.querySelector('#learnShapeEachBar input[value=once]').checked, $('learnShapeDotsBar').disabled, $('learnShapeDots').disabled, vis($('learnShapeParts'))];")
    h.click('#learnShapeEach input[value=moves]'); time.sleep(0.2)
    b2 = h.js("return [L.learn.shape.state().each, document.querySelector('#learnShapeEachBar input[value=moves]').checked, $('learnShapeDotsBar').disabled, $('learnShapeDots').disabled];")
    check(a[:4] == ['once', True, True, True] and b2 == ['moves', True, False, False], 'Each step in the panel and in the transport are one choice; Dots is greyed with At once (%s, %s)' % (a, b2))
    # reset
    h.js("L.learn.shape.set({ kind: 'j', dots: 'many', each: 'once', pos: 3.3 }); return 1;")
    h.click('#learnReset button'); time.sleep(0.3)
    r = h.js("const s = L.learn.shape.state(); return [L.learn.follow, s.each, s.dots, s.kind, s.pos];")
    check(r == ['point', 'moves', 'some', 'm', 0], 'the Learn panel\'s reset puts Each step and Dots back to how they open (%s)' % r)
    bad = h.problems()
    check(not bad, 'no console error or warning' + (': ' + json.dumps(bad[:6]) if bad else ''))
say('%d checks failed' % len(fails) if fails else 'all passed')
io.open(os.path.join(ROOT, 'out', 'r29', 'learn', 'transport-%s-%s.txt' % (size, theme)), 'w', encoding='utf-8', newline='\n').write('\n'.join(lines) + '\n')

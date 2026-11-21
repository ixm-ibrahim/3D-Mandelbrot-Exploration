# Window shots of the Learn panel's new parts, wide and phone: the choice Each step with its help and Dots (A whole
# shape), and the select Show with its help and the line under it (One point), for each space.
#   python out/r29/learn/mk/panel.py <size> <theme>
import json, os, sys, time
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE))))
sys.path.insert(0, os.path.join(ROOT, 'out', 'r28', 'final', 'ui', 'mk'))
from hand import Hand

size = sys.argv[1] if len(sys.argv) > 1 else '1400x950'
theme = sys.argv[2] if len(sys.argv) > 2 else 'light'
page = os.environ.get('LEARN_PAGE', 'dist/r29-learn.html')
tag = 'p-%s-%s' % (size.split('x')[0], theme)
with Hand(page, size, theme) as h:
    h.click('#mode-l'); time.sleep(0.3)
    # One point: the select Show, each choice in each space
    for space in (2, 3, 1):
        h.click('#learnSpace%d' % space); time.sleep(0.3)
        for i, show in enumerate(('point', 'circle', 'all', 'grid')):
            h.js("$('learn-show').focus(); return 1;")
            cur = h.js("return $('learn-show').selectedIndex;")
            for _ in range(abs(i - cur)):
                h.key('ArrowDown' if i > cur else 'ArrowUp')
            time.sleep(0.25)
            r = h.js("const s = $('learn-show'), line = $('learnShowLine'); return { chosen: s.options[s.selectedIndex].text, show: L.learn.show, line: vis(line) ? line.textContent : null, help: $('learn-showHelp').textContent };")
            print('space %d | %-38s | %s | line: %s' % (space, r['chosen'], r['show'], r['line']))
            if show in ('all', 'grid'):
                h.js("$('learn-show').scrollIntoView({ block: 'center' }); return 1;"); time.sleep(0.3)
                h.window_shot('out/r29/learn/shots/%s-show-%d-%s.png' % (tag, space, show))
        print('   help: ' + r['help'])
    h.click('#learnSpace2'); time.sleep(0.2)
    h.js("window.scrollTo(0, 0); return 1;")
    # A whole shape: the panel part
    h.click('#learnFollowShape'); time.sleep(0.5)
    h.click('#learnShapePlay'); time.sleep(0.2)
    h.js("L.learn.shape.set({ pos: 2 + 2.5 / 6, kind: 'j', c: [-1, 0, 0] }); $('learnShapeEachBlock').scrollIntoView({ block: 'center' }); return 1;"); time.sleep(0.5)
    h.window_shot('out/r29/learn/shots/%s-each-moves.png' % tag)
    print('Each step help (Move by move): ' + h.js("return $('learnShapeEachHelp').textContent;"))
    h.click('#learnShapeEach input[value=once]'); time.sleep(0.4)
    h.window_shot('out/r29/learn/shots/%s-each-once.png' % tag)
    print('Each step help (At once): ' + h.js("return $('learnShapeEachHelp').textContent;"))
    h.click('#learnShapeEach input[value=moves]'); time.sleep(0.3)
    # the transport, brought fully into view, and what the picture's block takes of the window
    h.js("$('learnShapeBar').scrollIntoView({ block: 'end' }); return 1;"); time.sleep(0.4)
    h.window_shot('out/r29/learn/shots/%s-bar.png' % tag)
    r = h.js("const b = $('learnShapeBar').getBoundingClientRect(), s = $('stage').getBoundingClientRect(), m = document.querySelector('.bench-main').getBoundingClientRect();"
             " return { bar: Math.round(b.height), stage: Math.round(s.height), block: Math.round(m.height), window: innerHeight, pin: L.S ? [document.documentElement.classList.contains('pin-on'), document.documentElement.classList.contains('pin-let-go')] : null,"
             " wide: document.documentElement.scrollWidth > innerWidth + 1, each: (() => { const e = $('learnShapeEachBar').getBoundingClientRect(); return [Math.round(e.left), Math.round(e.right), Math.round(e.top), Math.round(e.bottom)]; })(),"
             " dots: (() => { const e = $('learnShapeDotsBar').getBoundingClientRect(); return [Math.round(e.left), Math.round(e.right), Math.round(e.top), Math.round(e.bottom)]; })() };")
    print('transport: ' + json.dumps(r))
    bad = h.problems()
    print('problems:', bad if bad else 'none')

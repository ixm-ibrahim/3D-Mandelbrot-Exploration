"""Round 28, dial checker (ui), section 1.4 f: every word of the group as the page shows it, and whether the panel fits.

  python -B out/r28/final/ui/mk/words.py <wide|phone> <dark|light> [words]
      -> out/r28/final/ui/logs/words-<layout>-<theme>.txt, pictures out/r28/final/ui/shots/panel-<layout>-<theme>-*.png
  With "words" the texts are collected too (labels, help, tooltips, the status sentences in every state I can reach).

The fit is measured on the page (boxes of the parts, text that is cut off, parts that lie over each other) in four
states: as the row gives it; size 150 (one status sentence); second sphere 50 with size 200 and depth 3 (three status
sentences, the longest text the place can hold); size 1999.9 (the longest numbers). The pictures are for looking at.
Input is real (hand.py).
"""
import json, os, sys, time
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from hand import Hand, ROOT, UI

LAYOUT = sys.argv[1] if len(sys.argv) > 1 else 'wide'
THEME = sys.argv[2] if len(sys.argv) > 2 else 'dark'
WORDS = 'words' in sys.argv[3:]
SIZE = {'wide': '1400x950', 'phone': '390x800'}[LAYOUT]
PAGE = 'dist/r28-final.html'
TAG = 'panel-%s-%s' % (LAYOUT, THEME)
LOG = os.path.join(UI, 'logs', 'words-%s-%s.txt' % (LAYOUT, THEME))
SHOTS = 'out/r28/final/ui/shots'
lines, wrong = [], []


def say(text):
    lines.append(text); print(text)
    with open(LOG, 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(lines) + '\n')


FIT = """
const part = $('ballsPart'), panel = $('kleinPanel'), pb = panel.getBoundingClientRect(), out = { outside: [], cut: [], over: [], sideways: document.documentElement.scrollWidth - innerWidth, panel: [Math.round(pb.left), Math.round(pb.width)], win: innerWidth };
const name = e => (e.id ? '#' + e.id : e.tagName.toLowerCase() + (e.className && typeof e.className === 'string' ? '.' + e.className.split(' ').join('.') : '')) + (e.textContent && e.children.length === 0 ? ' "' + e.textContent.trim().slice(0, 30) + '"' : '');
const box = e => e.getBoundingClientRect();
const all = [...part.querySelectorAll('*')].filter(e => vis(e) && box(e).width > 0 && box(e).height > 0 && !e.closest('svg'));
for (const e of all) { const b = box(e); if (b.left < pb.left - 0.5 || b.right > pb.right + 0.5 || b.left < -0.5 || b.right > innerWidth + 0.5) out.outside.push(name(e) + ' ' + Math.round(b.left) + '..' + Math.round(b.right)); }
// text that does not fit its own box
for (const e of part.querySelectorAll('label.label, p, button.btn, button.dial-mode, input.num, select, legend, span.kgroup-tag')) {
  if (!vis(e)) continue;
  if (e.scrollWidth > e.clientWidth + 1 || (e.tagName !== 'SELECT' && e.scrollHeight > e.clientHeight + 1 && getComputedStyle(e).overflowY !== 'visible')) out.cut.push(name(e) + ' needs ' + e.scrollWidth + ' x ' + e.scrollHeight + ', has ' + e.clientWidth + ' x ' + e.clientHeight);
}
// the number in a box against the room the box has (measured with the box's own font)
for (const n of part.querySelectorAll('input.num')) { const cs = getComputedStyle(n), c = document.createElement('canvas').getContext('2d'); c.font = cs.font; const w = c.measureText(n.value).width, room = n.clientWidth - parseFloat(cs.paddingLeft) - parseFloat(cs.paddingRight); if (w > room + 0.5) out.cut.push('the number "' + n.value + '" in #' + n.id + ' is ' + w.toFixed(1) + ' px wide, the box has ' + room.toFixed(1)); }
const hit = (a, b) => { const x = Math.min(a.right, b.right) - Math.max(a.left, b.left), y = Math.min(a.bottom, b.bottom) - Math.max(a.top, b.top); return x > 1 && y > 1; };
// the blocks of the part, top to bottom: none may lie over another
const blocks = [$('ballsNote'), $('ballsWarn'), ...$('ballsDials').children, $('ballsFrame').parentNode, $('ballsReset')].filter(vis);
for (let i = 0; i < blocks.length; i++) for (let j = i + 1; j < blocks.length; j++) if (hit(box(blocks[i]), box(blocks[j]))) out.over.push(name(blocks[i]) + ' over ' + name(blocks[j]));
// inside a dial: label, the box with its buttons, the slider, the help
for (const d of part.querySelectorAll('.dial, .field-block')) { const kids = [...d.querySelectorAll('label.label, .dial-box, input[type=range], p.dial-help, select')].filter(vis);
  for (let i = 0; i < kids.length; i++) for (let j = i + 1; j < kids.length; j++) if (!kids[i].contains(kids[j]) && !kids[j].contains(kids[i]) && hit(box(kids[i]), box(kids[j]))) out.over.push(name(kids[i]) + ' over ' + name(kids[j])); }
// inside the box of a dial: the small buttons and the number
for (const d of part.querySelectorAll('.dial-box')) { const kids = [...d.children].filter(vis); for (let i = 0; i < kids.length; i++) for (let j = i + 1; j < kids.length; j++) if (hit(box(kids[i]), box(kids[j]))) out.over.push(name(kids[i]) + ' over ' + name(kids[j]) + ' in ' + name(d.parentNode)); }
out.heights = { note: Math.round(box($('ballsNote')).height), warn: vis($('ballsWarn')) ? Math.round(box($('ballsWarn')).height) : 0, part: Math.round(box($('ballsReset')).bottom - box($('ballsNote')).top) };
out.warn = vis($('ballsWarn')) ? $('ballsWarn').textContent : '';
return out;
"""

TEXTS = """
const t = e => (e ? e.textContent.replace(/\\s+/g, ' ').trim() : null);
const dial = id => { const d = $(id).closest('.dial'), n = $(id + 'Num'), m = d.querySelector('.dial-mode'); return { label: t(d.querySelector('label')), help: t(d.querySelector('.dial-help')), boxTip: n.title, boxSaysToAScreenReader: n.getAttribute('aria-label'), up: d.querySelector('.dial-up').title, down: d.querySelector('.dial-down').title, upName: d.querySelector('.dial-up').getAttribute('aria-label'), stepButton: m ? [t(m), m.title, m.getAttribute('aria-label')] : null }; };
const sel = $('ballsGrid'), f = sel.closest('.field-block') || sel.parentNode.parentNode;
return { panelTitle: t($('kleinPanel').querySelector('summary')), legend: t($('kleinGroup').querySelector('legend')), choices: [...$('kleinGroup').querySelectorAll('label')].map(t),
  note: t($('ballsNote')), size: dial('ballsSize'), second: dial('ballsRho'), depth: dial('ballsDepth'),
  grid: { label: t(f.querySelector('label')), options: [...sel.options].map(o => o.textContent), help: t(f.querySelector('.dial-help')) },
  frame: [t($('ballsFrame')), $('ballsFrame').title], reset: t($('ballsReset').querySelector('button')),
  row: { heading: t($('apgh-cousin')), text: t($('ap-balls')), tip: $('ap-balls').title }, status: t($('status')), hint: t(document.querySelector('.stage-bar .hint')), hintBelow: t($('hintBelow')), stageNote: vis($('stageNote')) ? t($('stageNote')) : null };
"""


def scroll_shots(h, name):
    """Three looks at the panel as the window shows it: its top, the new dial, its end."""
    for k, sel in (('a-top', '#kleinGroup'), ('b-dials', '#ballsRho'), ('c-end', '#ballsReset')):
        h.box(sel, 'center'); time.sleep(0.2)
        h.window_shot('%s/%s-%s-%s.png' % (SHOTS, TAG, name, k))


def fit(h, name):
    h.done()
    r = h.js(FIT)
    bad = []
    if r['outside']: bad.append('parts outside the panel or the window: ' + '; '.join(r['outside'][:8]))
    if r['cut']: bad.append('text cut off: ' + '; '.join(r['cut'][:8]))
    if r['over']: bad.append('parts over each other: ' + '; '.join(r['over'][:8]))
    if r['sideways'] > 0: bad.append('the page scrolls sideways by %d px' % r['sideways'])
    say('%s: panel %d px wide in a window of %d; note %d px high, status sentences %d px, the whole part %d px; %s' % (
        name, r['panel'][1], r['win'], r['heights']['note'], r['heights']['warn'], r['heights']['part'], 'nothing sticks out, nothing is cut off, nothing overlaps  -> OK' if not bad else 'WRONG: ' + ' | '.join(bad)))
    if r['warn']:
        say('   status sentences shown: "%s"' % r['warn'])
    if bad:
        wrong.append(name + ': ' + ' | '.join(bad))
    scroll_shots(h, name.split(':')[0].replace(' ', '-'))


def typed(h, dial, text):
    h.type('#balls%sNum' % dial, text); h.done()


def warn(h):
    h.done(); return h.js("return vis($('ballsWarn')) ? $('ballsWarn').textContent : '';")


def main():
    os.makedirs(os.path.dirname(LOG), exist_ok=True)
    say('page %s, window %s, theme %s, started %s' % (PAGE, SIZE, THEME, time.strftime('%H:%M:%S')))
    with Hand(PAGE, SIZE, THEME) as h:
        th = h.js("return [getComputedStyle(document.documentElement).colorScheme, getComputedStyle(document.body).backgroundColor, document.documentElement.dataset.theme || ''];")
        say('theme as the page took it: colour scheme "%s", background %s, data-theme "%s"' % tuple(th))
        h.click('#apMenuBtn'); time.sleep(0.4)
        h.hover('#ap-balls'); time.sleep(0.4)
        h.window_shot('%s/%s-0-approach-list.png' % (SHOTS, TAG))
        r = h.js("""const row = $('ap-balls'), b = row.getBoundingClientRect(), pop = $('apPop').getBoundingClientRect(), info = $('apInfo'), ib = info.getBoundingClientRect();
          return { row: [b.left, b.top, b.width, b.height].map(Math.round), inWindow: b.top >= 0 && b.bottom <= innerHeight && b.left >= 0 && b.right <= innerWidth, cut: row.scrollWidth > row.clientWidth + 1,
                   info: vis(info) ? [ib.left, ib.top, ib.width, ib.height].map(Math.round) : null, infoText: vis(info) ? info.textContent : '', sideways: document.documentElement.scrollWidth - innerWidth };""")
        say('the Approach list, open, the mouse over the row Balls on balls: row box %s, wholly in the window %s, its text cut %s; the explanation beside it %s: "%s"; the page scrolls sideways by %d px' % (
            r['row'], r['inWindow'], r['cut'], r['info'], r['infoText'][:400], max(0, r['sideways'])))
        h.click('#ap-balls'); h.done()
        if WORDS:
            say('--- every word of the group (as the row gives it)')
            t = h.js(TEXTS)
            say(json.dumps(t, ensure_ascii=False, indent=1))
        fit(h, '1 as the row gives it')
        typed(h, 'Size', '150'); h.click('#ballsFrame')
        fit(h, '2 size 150')
        h.shot('%s/%s-2-size-150-picture.png' % (SHOTS, TAG), '#stage')
        h.click('#ballsReset button'); h.done()
        typed(h, 'Rho', '50'); typed(h, 'Size', '200'); typed(h, 'Depth', '3'); h.click('#ballsFrame')
        fit(h, '3 second sphere 50, size 200, depth 3: three status sentences')
        h.shot('%s/%s-3-touch-depth3-picture.png' % (SHOTS, TAG), '#stage')
        h.click('#ballsReset button'); h.done()
        typed(h, 'Size', '1999.9'); typed(h, 'Depth', '1000')
        fit(h, '4 size 1999.9, depth 1000: the longest numbers')
        h.click('#ballsFrame'); h.done()
        h.shot('%s/%s-4-size-1999.9-picture.png' % (SHOTS, TAG), '#stage')
        h.click('#ballsReset button'); h.done()
        typed(h, 'Size', '300'); h.click('#ballsFrame'); h.done()
        h.shot('%s/%s-5-size-300-picture.png' % (SHOTS, TAG), '#stage')
        h.click('#flat'); h.done(); h.click('#ballsFrame'); h.done()
        h.shot('%s/%s-5-size-300-2d-picture.png' % (SHOTS, TAG), '#stage')
        fit(h, '5 size 300, 2D view')
        h.click('#flat'); h.done()
        h.click('#ballsReset button'); h.done()

        if WORDS:
            say('--- the status sentences, in every state I could reach (typed with real keys)')
            seen = {}
            def note(label):
                w = warn(h); seen[label] = w; say('%s: "%s"' % (label, w))
            reset = lambda: (h.click('#ballsReset button'), h.done(), h.click('#ballsFrame'), h.done())
            grid = lambda g: (h.js("const e = $('ballsGrid'); e.value = '%d'; e.dispatchEvent(new Event('change', { bubbles: true })); return 1;" % g), h.done())
            reset(); note('as the row gives it')
            typed(h, 'Size', '100'); note('size 100, two equal spheres, 3D, square grid')
            grid(1); note('the same, honeycomb grid'); grid(2); note('the same, a line only'); grid(0)
            h.click('#flat'); note('the same, square grid, 2D view'); h.click('#flat'); h.done()
            reset(); typed(h, 'Size', '95'); note('size 95 typed after the start view (no Frame it)')
            h.click('#flat'); note('the same in the 2D view'); h.click('#flat'); h.done()
            reset(); typed(h, 'Size', '150'); note('size 150 typed after the start view (no Frame it)')
            h.click('#ballsFrame'); note('size 150, Frame it')
            reset(); typed(h, 'Size', '400'); note('size 400 typed after the start view (no Frame it)')
            h.click('#ballsFrame'); note('size 400, Frame it')
            reset(); typed(h, 'Size', '150'); typed(h, 'Size', '80'); note('size 150, then back to 80')
            reset(); typed(h, 'Rho', '50'); typed(h, 'Size', '200'); note('second sphere 50, size 200 (touching), 3D, square grid, no Frame it')
            h.click('#ballsFrame'); note('the same after Frame it')
            grid(2); note('the same, a line only'); grid(0)
            h.click('#flat'); note('the same, 2D view'); h.click('#flat'); h.done()
            reset(); typed(h, 'Rho', '50'); typed(h, 'Size', '199.8'); h.click('#ballsFrame'); note('second sphere 50, size 199.8 (all but touching), Frame it, 3D')
            r = h.js("return [L.ballsReach(), S.view.bound];"); say('   reach %.2f, Drawing radius %.2f' % tuple(r))
            h.click('#flat'); h.done(); h.click('#ballsFrame'); note('the same, 2D view, Frame it')
            r = h.js("return [L.ballsReach(), S.v2.h * $('stage').clientWidth / $('stage').clientHeight / 2];"); say('   reach %.2f, half the width of the 2D view %.2f' % tuple(r))
            h.shot('%s/%s-6-rho50-size199.8-2d.png' % (SHOTS, TAG), '#stage')
            h.click('#flat'); h.done()
            reset(); typed(h, 'Depth', '4'); note('depth 4')
            typed(h, 'Depth', '5'); note('depth 5')
            reset(); typed(h, 'Size', '150'); typed(h, 'Depth', '2'); note('size 150, depth 2')
            reset(); typed(h, 'Rho', '50'); typed(h, 'Size', '200'); typed(h, 'Depth', '1'); note('second sphere 50, size 200, depth 1 (the longest text)')
            say('   that text is %d characters, %d sentences' % (len(seen['second sphere 50, size 200, depth 1 (the longest text)']), seen['second sphere 50, size 200, depth 1 (the longest text)'].count('. ') + 1))
            reset()
            t = h.js("return { status: $('status').textContent, hintBelow: $('hintBelow').textContent };")
            say('status line under the picture at the start view: "%s"; hint: "%s"' % (t['status'], t['hintBelow']))
        probs = h.problems()
        say('--- console: %s' % ('no console errors or warnings' if not probs else '%d PROBLEM(S): ' % len(probs) + ' || '.join(p[:400] for p in probs[:12])))
        if probs:
            wrong.append('console problems: %d' % len(probs))
    say('=== %d thing(s) marked WRONG%s' % (len(wrong), ': ' + ' || '.join(wrong) if wrong else ''))


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        import traceback
        say('THE SCRIPT STOPPED: ' + repr(e)); say(traceback.format_exc())
        sys.exit(1)

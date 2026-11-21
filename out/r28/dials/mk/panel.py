"""Round 28, Track A, builder: the panel of Balls on balls to LOOK at, wide and phone, dark and light, with the
neighbours at 150 (so that the sentence shows), and measured: does anything in it stick out of its box or lie over
its neighbour?

  python out/r28/dials/mk/panel.py   -> out/r28/dials/shots/panel-<wide|phone>-<dark|light>.png, logs/panel.txt
"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import run28 as run

TYPE = "const type = async (id, text) => { const n = $(id + 'Num'); n.focus(); n.value = text; n.dispatchEvent(new Event('input', { bubbles: true })); n.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', bubbles: true })); n.blur(); await sleep(60); };\n"
MEASURE = run.HEAD + TYPE + """
$('ap-balls').click(); await settle(); await type('ballsSize', '150'); $('ballsFrame').click(); await settle();
const part = $('ballsPart'), panel = $('kleinPanel'), pb = panel.getBoundingClientRect();
// every piece of the Balls part: is it inside the panel sideways, and does it lie over the piece before it?
const kids = [$('ballsNote'), $('ballsWarn'), ...$('ballsDials').children, $('ballsFrame'), $('ballsReset')].filter(vis);
let out = 0, over = 0, wide = 0; const notes = [];
let prev = null;
for (const k of kids) { const b = k.getBoundingClientRect();
  if (b.left < pb.left - 0.5 || b.right > pb.right + 0.5) { out++; notes.push((k.id || k.className) + ' sticks out sideways'); }
  if (prev && b.top < prev.bottom - 0.5) { over++; notes.push((k.id || k.className) + ' lies over the piece above it by ' + (prev.bottom - b.top).toFixed(1) + ' px'); }
  if (k.scrollWidth > k.clientWidth + 1) { wide++; notes.push((k.id || k.className) + ' is wider inside than its box'); }
  prev = b; }
// inside each dial: the label, the typed box and the slider must not lie over each other
for (const d of $('ballsDials').querySelectorAll('.dial')) { const l = d.querySelector('.label').getBoundingClientRect(), n = d.querySelector('.dial-box').getBoundingClientRect(), r = d.querySelector('input[type=range]').getBoundingClientRect();
  if (l.right > n.left + 0.5 && l.bottom > n.top + 0.5 && l.top < n.bottom - 0.5) { over++; notes.push('in ' + d.querySelector('.label').textContent + ' the label lies over the typed box'); }
  if (r.top < Math.max(l.bottom, n.bottom) - 0.5) { over++; notes.push('in ' + d.querySelector('.label').textContent + ' the slider lies over the row above it'); } }
const page = document.documentElement.scrollWidth > window.innerWidth + 1;
panel.scrollIntoView({ block: 'start' }); await sleep(200);
return JSON.stringify({ window: [window.innerWidth, window.innerHeight], pieces: kids.length, stickOut: out, lieOver: over, tooWide: wide, pageScrollsSideways: page, notes, warn: warn(), labels: [...$('ballsDials').querySelectorAll('.label')].map(e => e.textContent) });
"""

if __name__ == '__main__':
    lines = []
    for size, tag in (('1400x950', 'wide'), ('390x800', 'phone')):
        for theme in ('dark', 'light'):
            name = 'panel-%s-%s' % (tag, theme)
            steps = [run.UP, {'js': MEASURE, 'wait': 'done', 'timeout': 900, 'shot': '%s/shots/%s.png' % (run.OUT, name), 'clip': '#kleinPanel'},
                     {'js': "window.scrollTo(0, 0); await new Promise(r => setTimeout(r, 200)); return 'top';", 'shot': '%s/shots/%s-window.png' % (run.OUT, name)}]
            code, text, vals = run.shot(run.PAGE, steps, name, size, theme)
            run.write(name + '.log', text + 'exit %d\n' % code)
            d = json.loads(vals[1])
            lines.append('%s %s (window %s): %d pieces; stick out sideways %d, lie over a neighbour %d, wider inside than their box %d, the page scrolls sideways: %s; %s%s'
                         % (tag, theme, 'x'.join(map(str, d['window'])), d['pieces'], d['stickOut'], d['lieOver'], d['tooWide'], d['pageScrollsSideways'], 'no console errors' if run.clean(text) else 'CONSOLE ERRORS', (' | ' + '; '.join(d['notes'])) if d['notes'] else ''))
    text = '\n'.join(lines) + '\n'
    run.write('panel.txt', text); print(text)

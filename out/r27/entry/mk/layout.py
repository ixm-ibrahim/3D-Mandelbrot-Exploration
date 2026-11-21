"""Round 27, entry: the new controls on a wide window and on a phone, dark and light; and the first-picture times.
  python out/r27/entry/mk/layout.py           -> shots/lay-*.png, logs/layout.txt
  python out/r27/entry/mk/layout.py speed     -> logs/speed.txt (first picture of each Kleinian group, on a fresh page)"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import run
H = run.HEAD
CHECK = H + """
const box = e => e.getBoundingClientRect(), vis = e => { const b = box(e); return b.width > 0 && b.height > 0; };
const bad = [];
if (document.documentElement.scrollWidth > innerWidth + 1) bad.push('the page is wider than the window: ' + document.documentElement.scrollWidth + ' of ' + innerWidth);
const items = [...document.querySelectorAll('#kleinGroup, #ballsNote, #ballsWarn, #ballsDials > *, #ballsPart .row-btns, #ballsReset')].filter(vis);
if (items.length < 6) bad.push('only ' + items.length + ' of the new pieces are on show');
for (const e of items) { const b = box(e); if (b.left < -0.5 || b.right > innerWidth + 0.5) bad.push((e.id || e.className) + ' runs out of the window: ' + Math.round(b.left) + '..' + Math.round(b.right)); }
for (let i = 0; i < items.length; i++) for (let j = i + 1; j < items.length; j++) { const a = box(items[i]), b = box(items[j]); if (a.left < b.right - 0.5 && b.left < a.right - 0.5 && a.top < b.bottom - 0.5 && b.top < a.bottom - 0.5) bad.push((items[i].id || items[i].className) + ' overlaps ' + (items[j].id || items[j].className)); }
// text that is cut off inside its own box
for (const e of document.querySelectorAll('#kleinGroup span, #ballsPart .label, #ballsPart .note, #ballsPart button, #ballsPart select')) if (vis(e) && e.scrollWidth > e.clientWidth + 1 && e.clientWidth > 0 && getComputedStyle(e).display !== 'inline') bad.push('text cut off in ' + (e.id || e.tagName + '.' + e.className) + ': "' + e.textContent.slice(0, 40) + '"');
return (bad.length ? 'PROBLEMS: ' + bad.join('; ') : 'fits: ' + items.length + ' new pieces inside the window, none overlapping, no text cut off') + ' | window ' + innerWidth + ' x ' + innerHeight + ', stage ' + $('stage').clientWidth + ' x ' + $('stage').clientHeight;
"""
MENU = H + """
$('kleinPanel').scrollIntoView({ block: 'start' }); await sleep(200);
$('apMenuBtn').scrollIntoView({ block: 'center' }); await sleep(200);
$('apMenuBtn').click(); await sleep(300);
const pop = $('apPop').getBoundingClientRect(), row = $('apBallsRow').getBoundingClientRect(), tag = $('apBallsRow').querySelector('.cousin-tag').getBoundingClientRect(), bad = [];
if (pop.left < -0.5 || pop.right > innerWidth + 0.5 || pop.top < -0.5 || pop.bottom > innerHeight + 0.5) bad.push('the open menu does not fit the window: ' + [pop.left, pop.top, pop.right, pop.bottom].map(Math.round));
if (row.top < pop.top - 0.5 || row.bottom > pop.bottom + 0.5 || row.height < 30 || tag.height < 10) bad.push('the row is not whole inside the menu');
if (!$('apBallsRow').classList.contains('is-on')) bad.push('the row is not marked as the one on show');
return (bad.length ? 'PROBLEMS: ' + bad.join('; ') : 'open menu fits, the row is whole and marked') + ' | menu ' + [pop.left, pop.top, pop.right, pop.bottom].map(Math.round) + ', row ' + [row.left, row.top, row.right, row.bottom].map(Math.round);
"""


def layout():
    lines = []
    for size in ('1400x950', '390x800'):
        for theme in ('dark', 'light'):
            tag = 'lay-%s-%s' % (size, theme); P = 'out/r27/entry/shots/' + tag
            steps = [run.UP,
                     dict(js=H + "$('apMenuBtn').click(); await sleep(200); $('ap-balls').click(); await sleep(150); await settle(); window.scrollTo(0, 0); await sleep(200); return 'Balls on balls on show, ' + $('status').textContent;", wait='done', timeout=600, shot=P + '-top.png'),
                     dict(js=H + "$('kleinPanel').scrollIntoView({ block: 'start' }); await sleep(300); return 'panel in view';", shot=P + '-panel.png'),
                     dict(js=CHECK),
                     dict(js=MENU, shot=P + '-menu.png'),
                     dict(js=H + "$('ap-balls').focus(); document.dispatchEvent(new PointerEvent('pointerdown', { bubbles: true })); await sleep(150); window.scrollTo(0, 0); $('flat').click(); await sleep(200); await settle(); return '2D view';", wait='done', timeout=600, shot=P + '-flat.png', clip='#stage')]
            code, text, vals = run.shot(run.PAGE, steps, tag, size, theme)
            run.write(tag + '.log', text + 'exit %d\n' % code)
            lines.append('%s %s: exit %d; %s' % (size, theme, code, 'no console errors' if 'no console errors' in text else 'CONSOLE PROBLEMS'))
            lines += ['   ' + v for v in vals[1:]]
    text = '\n'.join(lines) + '\n'
    run.write('layout.txt', text); print(text)


def speed():
    T = H + """
const t0 = performance.now(); let first = 0;
%s
for (let i = 0; i < 20000; i++) { if (!first && L.R.shown === 'acc') first = performance.now() - t0; if (first && L.idle()) break; await sleep(4); }
return '%s: first full-size pass on screen after ' + Math.round(first) + ' ms, finished (' + $('status').textContent + ') after ' + Math.round(performance.now() - t0) + ' ms; programs built ' + L.R.compiles;
"""
    lines = []
    for rnd in (1, 2, 3):
        for name, js in (('first group (pearls)', "$('mode-k').click();"), ('Balls on balls', "S.k.group = 1; $('mode-k').click();"), ('Balls on balls, by its row', "$('ap-balls').click();")):
            code, text, vals = run.shot(run.PAGE, [run.UP, dict(js=T % (js, name), timeout=600)], 'speed')
            lines.append('run %d  %s%s' % (rnd, vals[-1] if len(vals) > 1 else 'NO RESULT', '' if 'no console errors' in text else '  CONSOLE PROBLEMS'))
    text = '\n'.join(lines) + '\n'
    run.write('speed.txt', text); print(text)


if __name__ == '__main__':
    speed() if len(sys.argv) > 1 and sys.argv[1] == 'speed' else layout()

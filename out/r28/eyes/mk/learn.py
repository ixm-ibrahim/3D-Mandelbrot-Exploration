"""The eyes, section 1.4 d, a second look at the Learn tab: in mk/same.py the status line read "862 x 511" on the
new page and "862 x 701" on the frozen page after the same steps (the window itself was the same to the pixel).
Is that the overlay, or the moment the page was asked? Each page three times, in turn: the Learn tab straight from
the page as it opens, and the Learn tab after the walk through Balls on balls that same.py takes; the numbers are
read 0.3 s, 1.5 s and 4 s after the click.
  python out/r28/eyes/mk/learn.py   -> logs/learn.txt, same/learn-{new,old}-<n>.png"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import eyerun as run

READ = "({ status: $('status').textContent, canvas: [$('view').width, $('view').height], stage: [$('stage').clientWidth, $('stage').clientHeight], viewShown: vis($('view')), mode: S.mode, tab: (document.querySelector('.is-on[id^=mode-]') || {}).id || '', gen: L.R.gen, compiles: L.R.compiles, idle: L.idle() })"
JS = run.HEAD + """
%s
const out = [];
$('mode-l').click();
await sleep(300); out.push(%s);
await sleep(1200); out.push(%s);
await sleep(2500); out.push(%s);
return JSON.stringify(out);
"""
WALK = "$('ap-balls').click(); await settle(); await type('ballsSize', '100'); await settle(); $('kleinGroup0').click(); await settle(); $('mode-j').click(); await settle(); $('ap-pulledplane').click(); await settle();"

if __name__ == '__main__':
    lines = []
    for i in range(3):
        for tag, page in ((('new', run.PAGE), ('old', run.BASE)) if i % 2 == 0 else (('old', run.BASE), ('new', run.PAGE))):
            for kind, pre in (('straight', ''), ('after the walk', WALK)):
                code, text, vals = run.shot(page, [run.UP, {'js': JS % (pre, READ, READ, READ), 'shot': '%s/same/learn-%s-%d-%s.png' % (run.OUT, tag, i, kind.split()[0])}], 'learn-%s-%d' % (tag, i), '1400x950', 'dark')
                try:
                    v = json.loads(vals[-1])
                except (ValueError, IndexError):
                    lines.append('%s %d %s: NO RESULT %s' % (tag, i, kind, text[-300:])); continue
                lines.append('%s page, run %d, %-14s: %s | %s' % (tag, i, kind, ' -> '.join('%s, canvas %s, stage %s, drawn %s times' % (x['status'], x['canvas'], x['stage'], x['gen']) for x in v), 'no console errors' if run.clean(text) else 'CONSOLE ERRORS'))
                print(lines[-1]); sys.stdout.flush()
    run.write('learn.txt', '\n'.join(lines) + '\n')

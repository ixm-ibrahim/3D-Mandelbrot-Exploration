"""Round 27, final, number 3: time to the first picture of the new group, against the first Kleinian group.
  python out/r27/final/mk/speed.py [trials]    -> out/r27/final/logs/speed.txt
Every trial is a fresh browser: the page comes up with its Mandelbrot start picture, then ONE click, and the clock
runs from the click to (a) the first time the stage is painted again (R.painted, set by the lab's blit) and (b) the
finished picture (idle()). Three kinds, taken in turn so that a slow spell of the machine hits all of them:
  row   dist/r27-final.html, click on the row Balls on balls of the Approach list (the user's way in)
  old   dist/r27-final.html, click on Show: Kleinian (the first group)
  base  dist/r27-base.html,  click on Show: Kleinian (the first group on the frozen page)
"""
import json, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import run

N = int(sys.argv[1]) if len(sys.argv) > 1 else 4
KINDS = {'row': (run.PAGE, "$('ap-balls').click();"), 'old': (run.PAGE, "$('mode-k').click();"), 'base': (run.BASE, "$('mode-k').click();")}
JS = run.HEAD + """
await sleep(300);
const seen = [], st = () => $('status').textContent;
let last = st(), first = null;
const built0 = L.R.compiles;
L.R.painted = false;
const t0 = performance.now();
%s
for (;;) {
  await new Promise(r => setTimeout(r, 1));
  const now = performance.now() - t0, s = st();
  if (s !== last) { seen.push([Math.round(now), s]); last = s; }
  if (first === null && L.R.painted) first = now;
  if (now > 150 && first !== null && L.idle()) return JSON.stringify({ first: Math.round(first), done: Math.round(now), mode: S.mode, group: S.k.group || 0, stage: [$('stage').clientWidth, $('stage').clientHeight], built: L.R.compiles - built0, status: st(), failed: L.R.failed || '' });
  if (now > 100000) fail('no finished picture in 100 s');
}
"""

if __name__ == '__main__':
    res = {k: [] for k in KINDS}; lines = []; errors = 0
    for i in range(N):
        order = ('row', 'old', 'base') if i % 2 == 0 else ('base', 'old', 'row')
        for kind in order:
            page, click = KINDS[kind]
            code, text, vals = run.shot(page, [run.UP, {'js': JS % click, 'timeout': 300}], 'speed-%s-%d' % (kind, i), '1400x950', 'dark')
            if not run.clean(text):
                errors += 1
            try:
                v = json.loads(vals[-1])
            except (ValueError, IndexError):
                lines.append('%s trial %d: NO RESULT (exit %d)' % (kind, i, code)); continue
            res[kind].append(v)
            lines.append('%-4s trial %d: first paint after %4d ms, finished after %4d ms; mode %s, group %s, stage %s, programs built %s; %s%s' % (kind, i, v['first'], v['done'], v['mode'], v['group'], v['stage'], v['built'], v['status'], ' FAILED ' + v['failed'] if v['failed'] else ''))
    for kind in KINDS:
        f = [v['first'] for v in res[kind]]; d = [v['done'] for v in res[kind]]
        if f:
            lines.append('%-4s first paint: median %d ms (%s); finished: median %d ms (%s)' % (kind, np.median(f), ', '.join(map(str, f)), np.median(d), ', '.join(map(str, d))))
    if res['row'] and res['old']:
        lines.append('new group against the first group on the same page: first paint %.2f x, finished %.2f x (medians); the slowest new trial against the fastest old trial: %.2f x' % (
            np.median([v['first'] for v in res['row']]) / np.median([v['first'] for v in res['old']]),
            np.median([v['done'] for v in res['row']]) / np.median([v['done'] for v in res['old']]),
            max(v['done'] for v in res['row']) / min(v['done'] for v in res['old'])))
    lines.append('runs with console errors or a failure: %d of %d' % (errors, 3 * N))
    text = '\n'.join(lines) + '\n'
    run.write('speed.txt', text); print(text)

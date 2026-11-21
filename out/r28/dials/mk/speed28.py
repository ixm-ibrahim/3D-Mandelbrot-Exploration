"""Round 28, Track A, builder: time to the first picture of Balls on balls at its default, new page against the frozen
one, and how long the pictures at 150 and 300 take on the new page (the method of round 27's speed.py).

  python out/r28/dials/mk/speed28.py [trials]    -> out/r28/dials/logs/speed.txt

Every trial is a fresh browser: the page comes up with its Mandelbrot start picture, then ONE click on the row Balls
on balls, and the clock runs from the click to (a) the first time the stage is painted again and (b) the finished
picture (idle()). The two pages are taken in turn, so that a slow spell of the machine hits both. On the new page the
trial then goes on: the size is set to 150 (which needs the second program: it is prepared then, since the
background warming is switched off for the test) and the clock runs to the finished picture; then 150 once more from
the default (the program is there now); then 300.
"""
import json, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import run28 as run

N = int(sys.argv[1]) if len(sys.argv) > 1 else 3
CLOCK = """
const clock = async act => { await sleep(300); L.R.painted = false; const built0 = L.R.compiles, t0 = performance.now(); let first = null; await act();
  for (;;) { await new Promise(r => setTimeout(r, 1)); const now = performance.now() - t0; if (first === null && L.R.painted) first = now;
    if (now > 150 && first !== null && L.idle()) return { first: Math.round(first), done: Math.round(now), built: L.R.compiles - built0, status: $('status').textContent };
    if (now > 100000) fail('no finished picture in 100 s'); } };
"""
ROW = run.HEAD + CLOCK + "const v = await clock(async () => { $('ap-balls').click(); }); v.stage = [$('stage').clientWidth, $('stage').clientHeight]; v.group = S.k.group; return JSON.stringify(v);"
MORE = run.HEAD + CLOCK + """
const out = {};
out.p150first = await clock(async () => { L.S.k.brho = 1 / 3; L.S.k.bt = 0.5 * (100 / 150 + 1); L.ballsFrame(); go(); });
L.S.k.brho = 1; L.S.k.bt = 1.4; L.ballsFrame(); go(); await settle();
out.p150 = await clock(async () => { L.S.k.brho = 1 / 3; L.S.k.bt = 0.5 * (100 / 150 + 1); L.ballsFrame(); go(); });
out.p300 = await clock(async () => { L.S.k.brho = 1 / 6; L.S.k.bt = 0.5 * (100 / 300 + 1); L.ballsFrame(); go(); });
out.back = await clock(async () => { L.S.k.brho = 1; L.S.k.bt = 1.4; L.ballsFrame(); go(); });
return JSON.stringify(out);
"""

if __name__ == '__main__':
    res = {'new': [], 'base': []}; more = []; lines = []; errors = 0
    for i in range(N):
        for kind in (('new', 'base') if i % 2 == 0 else ('base', 'new')):
            page = run.PAGE if kind == 'new' else run.BASE
            steps = [run.UP, {'js': ROW, 'timeout': 300}]
            if kind == 'new':
                steps.append({'js': MORE, 'timeout': 600})
            code, text, vals = run.shot(page, steps, 'speed-%s-%d' % (kind, i), '1400x950', 'dark')
            if not run.clean(text):
                errors += 1
            try:
                v = json.loads(vals[1])
            except (ValueError, IndexError):
                lines.append('%s trial %d: NO RESULT (exit %d)' % (kind, i, code)); continue
            res[kind].append(v)
            lines.append('%-4s trial %d: first paint after %4d ms, finished after %4d ms; group %s, stage %s, programs built %s; %s' % (kind, i, v['first'], v['done'], v['group'], v['stage'], v['built'], v['status']))
            if kind == 'new' and len(vals) > 2:
                m = json.loads(vals[2]); more.append(m)
                lines.append('     then, on the new page: 150 for the first time (programs built %d): finished after %d ms; 150 again: %d ms; 300: %d ms; back to the default: %d ms'
                             % (m['p150first']['built'], m['p150first']['done'], m['p150']['done'], m['p300']['done'], m['back']['done']))
    for kind in ('new', 'base'):
        f = [v['first'] for v in res[kind]]; d = [v['done'] for v in res[kind]]
        if f:
            lines.append('%-4s first paint: median %d ms (%s); finished: median %d ms (%s)' % (kind, np.median(f), ', '.join(map(str, f)), np.median(d), ', '.join(map(str, d))))
    if res['new'] and res['base']:
        lines.append('new page against the frozen page, the default picture: first paint %.2f x, finished %.2f x (medians)' % (
            np.median([v['first'] for v in res['new']]) / np.median([v['first'] for v in res['base']]), np.median([v['done'] for v in res['new']]) / np.median([v['done'] for v in res['base']])))
    if more:
        lines.append('new page, medians: 150 for the first time %d ms, 150 with its program there %d ms, 300 %d ms, the default again %d ms' % tuple(
            np.median([m[k]['done'] for m in more]) for k in ('p150first', 'p150', 'p300', 'back')))
    lines.append('runs with console errors or a failure: %d of %d' % (errors, 2 * N))
    text = '\n'.join(lines) + '\n'
    run.write('speed.txt', text); print(text)

"""The eyes, section 1.4 g: speed.
  python out/r28/eyes/mk/speed.py first [trials] [size] -> logs/speed-first-<size>.txt
      Time to the first finished picture of Balls on balls at its default: every trial is a fresh browser, the page
      comes up with its Mandelbrot start picture and is left alone until nothing is being prepared in the background
      any more, then ONE click on the row "Balls on balls" of the Approach list. The clock runs from the click to the
      first time the stage is painted again and to the finished picture (idle()). New page and frozen page take
      turns (new, old, old, new, ...), so that a slow spell of the machine hits both.
      The page's own background preparing is left ON (as a user has it); a second set runs with it switched off.
  python out/r28/eyes/mk/speed.py past [trials] [size]  -> logs/speed-past-<size>.txt
      How long 150 and 300 take on the new page: fresh browser, the row is clicked, then
        A  at once (as soon as the default picture is finished) 150 is typed into the size dial,
        B  after a wait of 5 s 150 is typed,
      then 300 is typed, then Frame it is pressed (the whole chain at 300), then 150 is typed again and Frame it.
      Each time: from the key to the first paint and to the finished picture, and how many programs were built.
"""
import json, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import eyerun as run

CLOCK = """
const clock = async (act) => {
  const built0 = L.R.compiles; L.R.painted = false;
  const t0 = performance.now(); let first = null;
  await act();
  for (;;) {
    await new Promise(r => setTimeout(r, 1));
    const now = performance.now() - t0;
    if (first === null && L.R.painted) first = now;
    if (now > 120 && first !== null && L.idle()) return { first: Math.round(first), done: Math.round(now), built: L.R.compiles - built0, status: $('status').textContent, sig: String(L.R.sig).trim(), failed: L.R.failed || '' };
    if (now > 100000) fail('no finished picture in 100 s');
  }
};
// (my first writing waited here until the page had finished preparing its other programs in the background. That takes
//  minutes, so the wait ran to its 120 s limit every time and the click still fell in the middle of it. Now: a fixed 3 s
//  after the page is up, the same on both pages; and whether something was being prepared at the click is written down.)
const quiet = async () => { await sleep(3000); };
const key = (id, text) => async () => { const n = $(id + 'Num'); n.focus(); n.value = String(text); n.dispatchEvent(new Event('input', { bubbles: true })); n.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', bubbles: true })); };
"""
FIRST = run.HEAD + CLOCK + """
%s
await quiet();
const busy = !!L.R.warming;
const r = await clock(async () => { $('ap-balls').click(); });
r.busy = busy; r.mode = S.mode; r.group = S.k.group || 0; r.stage = [$('stage').clientWidth, $('stage').clientHeight]; r.warm = L.R.warmOn;
return JSON.stringify(r);
"""
PAST = run.HEAD + CLOCK + """
await quiet();
const out = {};
out.row = await clock(async () => { $('ap-balls').click(); });
%s
out.warmedBefore150 = !L.R.warming;
out.p150 = await clock(key('ballsSize', '150'));
out.rho150 = S.k.brho;
await sleep(1500);
out.p300 = await clock(key('ballsSize', '300'));
out.rho300 = S.k.brho;
await sleep(300);
out.p300framed = await clock(async () => { $('ballsFrame').click(); });
await sleep(300);
out.p150back = await clock(key('ballsSize', '150'));
await sleep(300);
out.p150framed = await clock(async () => { $('ballsFrame').click(); });
out.stage = [$('stage').clientWidth, $('stage').clientHeight];
return JSON.stringify(out);
"""
PLAIN_UP = {'js': "return 'page up';", 'wait': 'done', 'timeout': 900}


def first(n, size):
    lines = []; errors = 0
    for warm, label in ((True, 'background preparing ON (as a user has it)'), (False, 'background preparing OFF')):
        res = {'new': [], 'old': []}
        for i in range(n):
            order = ('new', 'old') if i % 2 == 0 else ('old', 'new')
            for kind in order:
                page = run.PAGE if kind == 'new' else run.BASE
                js = FIRST % ('' if warm else 'L.R.warmOn = false;')
                code, text, vals = run.shot(page, [PLAIN_UP, {'js': js}], 'speed-first-%s-%d' % (kind, i), size, 'dark')
                if not run.clean(text):
                    errors += 1
                try:
                    v = json.loads(vals[-1])
                except (ValueError, IndexError):
                    lines.append('%s trial %d: NO RESULT (exit %d) %s' % (kind, i, code, text[-300:])); print(lines[-1]); sys.stdout.flush(); continue
                res[kind].append(v)
                lines.append('%s, %-3s trial %d: first paint after %4d ms, finished after %4d ms; programs built %s; %s; stage %s; the page was preparing another program at the click: %s%s' % (label, kind, i, v['first'], v['done'], v['built'], v['status'], v['stage'], v.get('busy'), ' FAILED ' + v['failed'] if v['failed'] else ''))
                print(lines[-1]); sys.stdout.flush()
        for kind in ('new', 'old'):
            f = [v['first'] for v in res[kind]]; d = [v['done'] for v in res[kind]]
            if f:
                lines.append('%s, %-3s: first paint median %d ms (%s); finished median %d ms (%s)' % (label, kind, np.median(f), ', '.join(map(str, f)), np.median(d), ', '.join(map(str, d))))
        if res['new'] and res['old']:
            lines.append('%s: new against old, finished: medians %.2f x; mean %.2f x; slowest new against fastest old %.2f x. First paint: medians %.2f x' % (
                label, np.median([v['done'] for v in res['new']]) / np.median([v['done'] for v in res['old']]),
                np.mean([v['done'] for v in res['new']]) / np.mean([v['done'] for v in res['old']]),
                max(v['done'] for v in res['new']) / min(v['done'] for v in res['old']),
                np.median([v['first'] for v in res['new']]) / np.median([v['first'] for v in res['old']])))
    lines.append('runs with console errors or a failure: %d' % errors)
    return lines


def past(n, size):
    lines = []; errors = 0
    for i in range(n):
        for kind, wait in (('A at once', ''), ('B after 5 s', 'await sleep(5000);')):
            code, text, vals = run.shot(run.PAGE, [PLAIN_UP, {'js': PAST % wait}], 'speed-past-%s-%d' % (kind[0], i), size, 'dark')
            if not run.clean(text):
                errors += 1
            try:
                v = json.loads(vals[-1])
            except (ValueError, IndexError):
                lines.append('%s trial %d: NO RESULT (exit %d) %s' % (kind, i, code, text[-600:])); print(lines[-1]); sys.stdout.flush(); continue
            f = lambda k: 'first paint %4d ms, finished %4d ms, programs built %d (%s; %s)' % (v[k]['first'], v[k]['done'], v[k]['built'], v[k]['status'], v[k]['sig'])
            lines.append('%s, trial %d, stage %s:' % (kind, i, v['stage']))
            lines.append('   the row clicked (default picture):      ' + f('row'))
            lines.append('   150 typed (other program ready: %s):  %s; second sphere now %.4f' % (v['warmedBefore150'], f('p150'), v['rho150']))
            lines.append('   300 typed:                              ' + f('p300') + '; second sphere now %.4f' % v['rho300'])
            lines.append('   Frame it at 300 (the whole chain):      ' + f('p300framed'))
            lines.append('   150 typed again:                        ' + f('p150back'))
            lines.append('   Frame it at 150 (the whole chain):      ' + f('p150framed'))
            print('\n'.join(lines[-7:])); sys.stdout.flush()
    lines.append('runs with console errors or a failure: %d' % errors)
    return lines


if __name__ == '__main__':
    what = sys.argv[1]; n = int(sys.argv[2]) if len(sys.argv) > 2 else 5; size = sys.argv[3] if len(sys.argv) > 3 else '1400x950'
    lines = first(n, size) if what == 'first' else past(n, size)
    text = '\n'.join(lines) + '\n'
    run.write('speed-%s-%s.txt' % (what, size), text); print(text)

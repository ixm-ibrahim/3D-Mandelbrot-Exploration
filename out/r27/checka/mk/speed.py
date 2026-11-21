"""Round 27, checker A, bullet 6: time to the first picture, the new group against the old group, same stage size.

Every trial is a fresh browser (fresh profile) on my page: the page comes up with its Mandelbrot start picture, then
ONE click, and the clock runs from the click: to the first time the stage is painted again (R.painted, set by the
lab's blit), and to the finished picture (idle()). The status line's changes are kept with their times.
  old:  click on Show: Kleinian (first group, as the page starts)
  row:  click on the row Balls on balls of the Approach list
  new:  the group choice already on Balls on balls (S.k.group = 1 set beforehand, nothing drawn), then click on Show: Kleinian
  python speed.py [trials]  -> ../logs/speed.txt
"""
import json, os, sys
import numpy as np
import drive as D

N = int(sys.argv[1]) if len(sys.argv) > 1 else 6
CLICK = {
    'old': "$('mode-k').click();",
    'row': "$('ap-balls').click();",
    'new': "$('mode-k').click();",
}
PRE = {'old': "", 'row': "", 'new': "S.k.group = 1;"}
JS = D.HEAD + """
%s
await sleep(200);
const seen = [], st = () => $('status').textContent;
let last = st(), first = null;
L.R.painted = false;
const t0 = performance.now();
%s
for (;;) {
  await new Promise(r => setTimeout(r, 1));
  const now = performance.now() - t0, s = st();
  if (s !== last) { seen.push([Math.round(now), s]); last = s; }
  if (first === null && L.R.painted) first = now;
  if (now > 150 && first !== null && L.idle()) return JSON.stringify({ first: Math.round(first), done: Math.round(now), mode: S.mode, group: S.k.group, stage: [$('stage').clientWidth, $('stage').clientHeight], seen, failed: L.R.failed || '' });
  if (now > 100000) fail('no finished picture in 100 s');
}
"""
res = {k: [] for k in CLICK}
lines = []
for i in range(N):
    for kind in (('old', 'row', 'new') if i % 2 == 0 else ('new', 'row', 'old')):
        code, vals, text = D.run(D.PAGE, [D.UP, {'js': JS % (PRE[kind], CLICK[kind])}], 'speed-%s-%d' % (kind, i))
        if code != 0 or len(vals) < 2:
            lines.append('%s trial %d FAILED: %s' % (kind, i, text[-300:])); print(lines[-1]); continue
        v = vals[1]; res[kind].append(v)
        lines.append('%s trial %d: first paint %d ms, finished %d ms, mode %s group %s stage %s; status: %s' % (kind, i, v['first'], v['done'], v['mode'], v['group'], v['stage'], v['seen']))
        print(lines[-1]); sys.stdout.flush()
for kind in CLICK:
    f = np.array([v['first'] for v in res[kind]]); d = np.array([v['done'] for v in res[kind]])
    if f.size:
        lines.append('%s: first paint median %d ms (%s); finished median %d ms (%s)' % (kind, np.median(f), ', '.join(str(int(x)) for x in f), np.median(d), ', '.join(str(int(x)) for x in d)))
        print(lines[-1])
with open(os.path.join(D.LOGS, 'speed.txt'), 'w', encoding='utf-8', newline='\n') as f:
    f.write('\n'.join(lines) + '\n')
with open(os.path.join(D.LOGS, 'speed.json'), 'w', encoding='utf-8') as f:
    json.dump(res, f, indent=1)

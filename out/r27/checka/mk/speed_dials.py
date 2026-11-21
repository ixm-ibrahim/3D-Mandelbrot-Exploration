"""Round 27, checker A: how long a finished picture of Balls on balls takes as the dials stand (the program is
already built: this is drawing time only), next to the first group's start picture. Same page, same stage.
  python speed_dials.py -> ../logs/speed-dials.txt
"""
import json, os
import drive as D

JS = D.HEAD + """
const out = [];
const time = async (label, set) => { const r = []; for (let i = 0; i < 3; i++) { set(); L.cam.yaw += 1e-4 * (i + 1); const t0 = performance.now(); go(); await sleep(60); for (let k = 0; k < 9000 && !L.idle(); k++) await sleep(5); r.push(Math.round(performance.now() - t0)); } out.push([label, r, $('status').textContent]); };
$('mode-k').click(); await settle();
await time('first group, start view', () => {});
L.ballsShow(); await settle();
const B = (t, g, r, close) => () => { S.k.bt = t; S.k.bgrid = g; S.k.bit = r; L.ballsFrame(); if (close) { L.cam.yaw = -1.25; L.cam.pitch = 0.5; L.cam.dist = 0.3; L.cam.target = [0.525, 0, 0]; } };
await time('balls, t 1.4, square, 16 rounds, start view', B(1.4, 0, 16));
await time('balls, t 1.4, square, 40 rounds, start view', B(1.4, 0, 40));
await time('balls, t 1.4, honeycomb, 16 rounds, start view', B(1.4, 1, 16));
await time('balls, t 2.5, square, 16 rounds, start view', B(2.5, 0, 16));
await time('balls, t 1.4, square, 16 rounds, close-up at the touching point', B(1.4, 0, 16, true));
await time('balls, t 1.05, square, 16 rounds, start view', B(1.05, 0, 16));
await time('balls, t 1, square, 16 rounds, start view', B(1, 0, 16));
await time('balls, t 1, square, 40 rounds, start view', B(1, 0, 40));
await time('balls, t 1, square, 16 rounds, close-up at the touching point', B(1, 0, 16, true));
return JSON.stringify(out);
"""
code, vals, text = D.run(D.PAGE, [D.UP, {'js': JS, 'wait': 'done', 'timeout': 600}], 'speed-dials')
lines = ['%-62s finished picture after %s ms   (%s)' % (a, ', '.join(str(x) for x in b), c) for a, b, c in vals[1]] if len(vals) > 1 else [text[-800:]]
with open(os.path.join(D.LOGS, 'speed-dials.txt'), 'w', encoding='utf-8', newline='\n') as f:
    f.write('\n'.join(lines) + '\n')
print('\n'.join(lines)); print('exit', code)

"""Round 29, Track A, builder, section 4 point 6, a second look: why is a picture of X1 slower than a picture of
Version 21's (150, 33.33)? The program, or what is in the picture?

  python -B out/r29/free/mk/speed29b.py   -> out/r29/free/logs/speed-b.txt

In one page (warming off, 1400 x 950), five times in turn over the states:
  the whole picture (12 passes) drawn again from nothing, as speed29.py takes it;
  the share of the picture's pixels whose ray stops on something (609 probes with pick());
  one distance alone, at 512 x 512 points that all lie in the open (a square of side 1 where nothing is inside):
  that is the cost of one query that runs the recipe to its end OUTSIDE and works out the room there.
"""
import json, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import run29 as run
import kit29 as K

# name, size, rho, grid, depth, centre of a square of side 1 in the flat cut that lies in the open
STATES = [('V21 (150, 33.33) k-balls2', 150, 0.3333, 0, 16, [0.0, 2.5]), ('V21 (100, 100) k-balls', 100, 1.0, 0, 16, [0.0, 3.2]), ('V21 (55.56, 100) k-balls', 55.56, 1.0, 0, 16, [0.0, 2.0]),
          ('Y1 (80, 75)', 80, 0.75, 0, 16, [0.0, 2.0]), ('X9 (105, 100)', 105, 1.0, 0, 16, [0.0, 3.2]), ('X1 (120, 100)', 120, 1.0, 0, 16, [0.184, 2.043]),
          ('X1 at depth 60', 120, 1.0, 0, 60, [0.184, 2.043]), ('X6 (150, 75)', 150, 0.75, 0, 16, [0.0, 3.0])]
JS = run.HEAD + """
const states = %s, out = {};
$('ap-balls').click(); await settle();
const set = async s => { S.k.brho = s[2]; S.k.bt = s[6]; S.k.bgrid = s[3]; S.k.bit = s[4]; S.flat = false; go(); await sleep(60); $('ballsFrame').click(); await settle(); };
for (const s of states) { await set(s);
  const w = $('stage').clientWidth, h = $('stage').clientHeight; let hits = 0;
  for (let i = 0; i < 29; i++) for (let j = 0; j < 21; j++) if (L.pick(w * (i + 0.5) / 29, h * (j + 0.5) / 21)) hits++;
  let open = 0; for (let i = 0; i < 40; i++) for (let j = 0; j < 40; j++) if (!L.ballsInside(s[5][0] + (i + 0.5) / 40 - 0.5, s[5][1] + (j + 0.5) / 40 - 0.5, 0)) open++;
  out[s[0]] = { sig: String(L.R.sig).split('\\n')[0], hits: hits / 609, open: open / 1600, full: [], slice: [] }; }
for (let k = 0; k < 5; k++) for (const s of states) {
  await set(s);
  const t0 = performance.now(); L.touch();
  for (let i = 0; i < 60000; i++) { await sleep(4); if (L.idle() && /Done/.test($('status').textContent)) break; }
  out[s[0]].full.push(performance.now() - t0);
  const snap = L.takeSnapshot(); await L.sampleSlice(snap, s[5][0], s[5][1], 1, 0, 512);
  const t1 = performance.now(); for (let r = 0; r < 4; r++) await L.sampleSlice(snap, s[5][0], s[5][1], 1, 0, 512); out[s[0]].slice.push((performance.now() - t1) / 4); L.releaseSnapshot(snap);
}
return JSON.stringify(out);
"""

if __name__ == '__main__':
    st = [[n, p, rho, g, depth, c, float(K.t_of(p))] for (n, p, rho, g, depth, c) in STATES]
    steps = [run.UP, {'js': JS % json.dumps(st), 'timeout': 2400}, {'wait': 'done', 'timeout': 900}]
    code, text, vals = run.shot(run.PAGE, steps, 'speed-b', '1400x950', 'light')
    run.write('speed-b.log', text + 'exit %d\n' % code)
    lines = ['page %s, exit %d, %s' % (run.PAGE, code, 'no console errors' if run.clean(text) else 'SEE logs/speed-b.log')]
    d = json.loads(vals[-1]) if vals else {}
    base = d.get(STATES[0][0])
    for s in STATES:
        v = d.get(s[0])
        if not v:
            continue
        full = float(np.median(v['full'])); sl = float(np.median(v['slice']))
        lines.append('%-26s %-9s whole picture %6.0f ms (%.2f x) | rays that stop on something %3.0f %% | one distance in the open (512 x 512 of them, %3.0f %% in the open) %5.1f ms (%.2f x)'
                     % (s[0], v['sig'], full, full / np.median(base['full']), 100 * v['hits'], 100 * v['open'], sl, sl / np.median(base['slice'])))
    out = '\n'.join(lines) + '\n'
    run.write('speed-b.txt', out); print(out)

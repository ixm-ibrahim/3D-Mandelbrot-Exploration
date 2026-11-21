"""Round 29, Track A, builder, section 4 point 6: speed.

  python -B out/r29/free/mk/speed29.py   -> out/r29/free/logs/speed.txt

In one page (dist/r29-free.html, warming off, 1400 x 950): for each state the numbers are written into the state, Frame
it, and the picture is drawn to the end once (the program is built then). Then, five times in turn over all states:
the picture is thrown away (touch) and drawn again to the end (12 passes), and the time is taken; and the time of the
first pass alone (the quick picture a user sees while a dial moves). Medians are reported, and each state's time
against Version 21's program for a smaller second sphere at (150, 33.33).
Also the cost of one distance alone: sampleSlice on a 512 x 512 grid of the flat cut (one query a point, no marching).
"""
import json, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import run29 as run
import kit29 as K

STATES = [('V21 (150, 33.33), k-balls2', 150, 0.3333, 0), ('V21 (55.56, 100), k-balls', 55.56, 1.0, 0), ('Y1 (80, 75)', 80, 0.75, 0), ('X1 (120, 100)', 120, 1.0, 0),
          ('X6 (150, 75)', 150, 0.75, 0), ('X4 (150, 100, honeycomb)', 150, 1.0, 1), ('Y2 (60, 60, honeycomb)', 60, 0.6, 1)]
JS = run.HEAD + """
const states = %s, out = {};
$('ap-balls').click(); await settle();
const set = async s => { S.k.brho = s[2]; S.k.bt = s[4]; S.k.bgrid = s[3]; S.k.bit = 16; S.flat = false; go(); await sleep(60); $('ballsFrame').click(); await settle(); };
for (const s of states) { await set(s); out[s[0]] = { sig: String(L.R.sig).split('\\n')[0], full: [], first: [], slice: [] }; }
for (let k = 0; k < 5; k++) for (const s of states) {
  await set(s);
  const t0 = performance.now(); L.touch();
  let first = 0;
  for (let i = 0; i < 60000; i++) { await sleep(4); const st = $('status').textContent; if (!first && /Refining|Done/.test(st)) first = performance.now() - t0; if (L.idle() && /Done/.test(st)) break; }
  out[s[0]].full.push(performance.now() - t0); out[s[0]].first.push(first);
  const snap = L.takeSnapshot(), t1 = performance.now(); await L.sampleSlice(snap, 0, 0, 2 * (1.05 * (0.5 + 1.2 * s[1] / 100) + 0.4), 0, 512); out[s[0]].slice.push(performance.now() - t1); L.releaseSnapshot(snap);
}
return JSON.stringify(out);
"""

if __name__ == '__main__':
    st = [[n, p, rho, g, float(K.t_of(p))] for (n, p, rho, g) in STATES]
    steps = [run.UP, {'js': JS % json.dumps(st), 'timeout': 2400}, {'wait': 'done', 'timeout': 900}]
    code, text, vals = run.shot(run.PAGE, steps, 'speed', '1400x950', 'light')
    run.write('speed.log', text + 'exit %d\n' % code)
    lines = ['page %s, exit %d, %s' % (run.PAGE, code, 'no console errors' if run.clean(text) else 'SEE logs/speed.log')]
    d = json.loads(vals[-1]) if vals else {}
    base = d.get(STATES[0][0])
    for (n, p, rho, g) in STATES:
        v = d.get(n)
        if not v:
            continue
        full = float(np.median(v['full'])); first = float(np.median(v['first'])); sl = float(np.median(v['slice']))
        lines.append('%-28s %-9s the whole picture (12 passes) %6.0f ms (%.2f x), the first pass %5.0f ms (%.2f x), 512 x 512 distances %5.0f ms (%.2f x) | all five: %s'
                     % (n, v['sig'], full, full / np.median(base['full']), first, first / max(np.median(base['first']), 1e-9), sl, sl / np.median(base['slice']), [int(x) for x in v['full']]))
    out = '\n'.join(lines) + '\n'
    run.write('speed.txt', out); print(out)

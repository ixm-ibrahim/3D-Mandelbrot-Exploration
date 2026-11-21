"""Round 28, Track A, the final checker: states that only a hand-written state can hold (the truth checker's remark 5).
No dial leads to them; the fixer says the page now takes them as the dial would. Mine; runs through the truth
checker's pagerun.py.     python -B out/r28/final/mk/byhand.py   -> out/r28/final/logs/byhand.txt

1. S.k.brho = 0.7 written by hand (between 50 and 100 %: balls would cut into each other if it were drawn as it comes).
2. S.k.brho = 0.5 with S.k.bt = 0.6 (the two spheres would cut into each other: t below (1 + rho) / 2 = 0.75).
For each: which program is on show, what the boxes read, the twin with nothing passed against the twin with the numbers
the dial would give (4096 points), and the shader (sampleSlice, flat cut, 64 x 64) against that twin.
"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); FINAL = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(FINAL, 'truth', 'mk'))
import pagerun as R

JS = """
if (!(S.mode === 'k' && S.k.group === 1)) { $('ap-balls').click(); await settle(); }
const out = [];
const look = async (name, brho, bt, want) => {
  S.k.brho = brho; S.k.bt = bt; S.flat = false; go(); await settle();
  const o = { t: want.t, rho: want.rho, grid: 0, rounds: S.k.bit };
  let n = 0, diff = 0, ins = 0, seed = 12345;
  const rnd = () => { seed = (seed * 1103515245 + 12345) % 2147483648; return seed / 2147483648; };
  for (let i = 0; i < 4096; i++) { const x = -3 + 6 * rnd(), y = -1.5 + 3 * rnd(), z = i % 2 ? 0 : -1 + 2 * rnd();
    const a = L.ballsInside(x, y, z), b = L.ballsInside(x, y, z, o); n++; if (a !== b) diff++; if (b) ins++; }
  const N = 64, side = 5, snap = L.takeSnapshot(), arr = await L.sampleSlice(snap, 0.003, 0.002, side, 0, N); L.releaseSnapshot(snap);
  let sd = 0, sn = 0;
  for (let j = 0; j < N; j++) for (let i = 0; i < N; i++) { const d = arr[4 * (j * N + i) + 3];
    const tw = L.ballsInside(0.003 + side * ((i + 0.5) / N - 0.5), 0.002 + side * ((j + 0.5) / N - 0.5), 0, o); sn++; if (!(d > 0) !== tw) sd++; }
  const w = $('ballsWarn');
  out.push(name + ': program ' + String(L.R.sig).split('\\n')[0] + '; boxes: size ' + $('ballsSizeNum').value + ', second sphere ' + $('ballsRhoNum').value + '; twin with nothing passed against the twin with (t ' + want.t + ', rho ' + want.rho + '): ' + diff + ' of ' + n + ' verdicts differ (' + ins + ' inside); shader against that twin, flat cut: ' + sd + ' of ' + sn + ' differ; sentences: ' + (w && w.getClientRects().length ? w.textContent : '(none)') + '; status ' + $('status').textContent);
};
await look('by hand: second sphere 0.7 (70 %), t 1.2', 0.7, 1.2, { t: 1.2, rho: 0.5 });
await look('by hand: second sphere 0.9 (90 %), t 1.2', 0.9, 1.2, { t: 1.2, rho: 1 });
await look('by hand: second sphere 0.5, t 0.6 (below touching)', 0.5, 0.6, { t: 0.75, rho: 0.5 });
await look('by hand: second sphere 0.01 (below the dial\\'s 2 %), t 1.4', 0.01, 1.4, { t: 1.4, rho: 0.02 });
document.querySelector('#ballsReset button').click(); await settle();
out.push('after Reset this section: t ' + S.k.bt + ', rho ' + S.k.brho + ', program ' + String(L.R.sig).split('\\n')[0]);
return out.join('\\n');
"""

if __name__ == '__main__':
    R.LOGS = os.path.join(FINAL, 'logs')
    code, text, vals = R.run(R.PAGE, [JS], 'byhand-run')
    lines = ['page %s, exit %d, %s' % (R.PAGE, code, 'no console errors' if R.clean(text) else 'SEE logs/byhand-run.log')] + [v for v in vals[1:]]
    out = '\n'.join(lines) + '\n'
    open(os.path.join(FINAL, 'logs', 'byhand.txt'), 'w', encoding='utf-8', newline='\n').write(out); print(out)
    if code != 0:
        print(text[-2500:])

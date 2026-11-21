"""Time the default Mandelbrot picture (Balanced, 12 passes) with the soft fold and with Sphere inversions
(planes = 1 and planes = 2), back to back.   python out/lab2/softfold/speed.py   -> out/lab2/softfold/speed.txt
Four rounds, in turn. Each round: switch (first picture, which includes preparing the shader and the scorecard),
then two plain redraws; the shorter redraw is that round's time."""
import json, os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
JS = """const L = window.squaringLab, S = L.S, $ = id => document.getElementById(id), sleep = ms => new Promise(r => setTimeout(r, ms));
L.R.warmOn = false; window.__sp = { done: false, text: '' };
(async () => {
  const rows = [], t = {}, NL = String.fromCharCode(10);
  const draw = async () => { L.touch(); const t0 = performance.now(); await sleep(40); while (!L.renderIdle()) await sleep(5); return (performance.now() - t0) / 1000; };
  const CASES = [['softfold p2 a0.25 slerp', 'softfold', { planes: 2, blend: 0.25, curve: 0, mix: 0 }], ['softfold p2 a0.4 pinch', 'softfold', { planes: 2, blend: 0.4, curve: 0, mix: 2 }], ['softfold p1', 'softfold', { planes: 1 }], ['mercator p1', 'mercator', { planes: 1 }], ['mercator p2', 'mercator', { planes: 2 }]];
  for (let round = 0; round < 4; round++) for (const [name, id, par] of CASES) {
    Object.assign(S.param[id], par); $('ap-' + id).click(); L.resetCam(); L.refresh(false);
    const t0 = performance.now(); await sleep(60); while (!L.idle()) await sleep(10);
    const first = (performance.now() - t0) / 1000, again = await draw(), again2 = await draw();
    (t[name] = t[name] || []).push(Math.min(again, again2));
    rows.push(name + ' round ' + (round + 1) + ': first picture ' + first.toFixed(2) + ' s, redraw ' + again.toFixed(2) + ' s and ' + again2.toFixed(2) + ' s; parameters ' + JSON.stringify(S.param[id]));
  }
  const med = a => { const s = a.slice().sort((x, y) => x - y); return (s[1] + s[2]) / 2; }, mn = a => Math.min(...a);
  const base1 = med(t['mercator p1']), base2 = med(t['mercator p2']);
  for (const [name] of CASES) rows.push(name + ': median redraw ' + med(t[name]).toFixed(2) + ' s (best ' + mn(t[name]).toFixed(2) + '); ratio to mercator p1 ' + (med(t[name]) / base1).toFixed(2) + ', to mercator p2 ' + (med(t[name]) / base2).toFixed(2));
  rows.push('m3d-default, Balanced, 12 passes, stage ' + $('stage').clientWidth + 'x' + $('stage').clientHeight);
  window.__sp.text = rows.join(NL); window.__sp.done = true;
})();
return 'timing';"""
sj = os.path.join(HERE, 'speed.json')
json.dump([{"wait": "done", "timeout": 300}, {"js": JS, "wait": "window.__sp.done", "timeout": 1500}, {"js": "return window.__sp.text;"}], open(sj, 'w', encoding='utf-8'))
sys.exit(subprocess.call([sys.executable, os.path.join(ROOT, 'notes', 'approaches_run.py'), 'dist/lab2-softfold.html', 'out/lab2/softfold/speed.txt', '--actions', sj], cwd=ROOT))

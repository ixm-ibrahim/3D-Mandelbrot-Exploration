"""Time the default Mandelbrot picture (Balanced, 12 passes) with axisbulb settings and the lathe, back to back.
   python out/lab2/axisbulb/speed.py     -> out/lab2/axisbulb/speed.txt
Three rounds, alternating. Each round: switch approach and dials (first picture, which includes preparing the
shader and the scorecard), then two plain redraws; the shorter redraw is that round's time."""
import json, os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
JS = """const L = window.squaringLab, S = L.S, $ = id => document.getElementById(id), sleep = ms => new Promise(r => setTimeout(r, ms));
L.R.warmOn = false; window.__sp = { done: false, text: '' };
(async () => {
  const rows = [], t = {}, NL = String.fromCharCode(10);
  const draw = async () => { L.touch(); const t0 = performance.now(); await sleep(40); while (!L.renderIdle()) await sleep(5); return (performance.now() - t0) / 1000; };
  const runs = [['lathe', 'lathe', null], ['axisbulb k=1 A=0 (returns early: the lathe itself)', 'axisbulb', [1, 0, 45]], ['axisbulb k=1 A=1e-6 (the lathe solid, whole code path)', 'axisbulb', [1, 1e-6, 45]], ['axisbulb k=1 A=0.2 (best variant)', 'axisbulb', [1, 0.2, 45]], ['axisbulb k=5 A=0', 'axisbulb', [5, 0, 45]], ['axisbulb k=9 A=0.2', 'axisbulb', [9, 0.2, 45]]];
  for (let round = 0; round < 3; round++) for (const [name, id, p] of runs) {
    $('ap-' + id).click(); if (p) { S.param.axisbulb.k = p[0]; S.param.axisbulb.wob = p[1]; S.param.axisbulb.reach = p[2]; } else S.param.lathe.spin = 1;
    L.refresh(false); L.resetCam(); L.touch();
    const t0 = performance.now(); await sleep(60); while (!L.idle()) await sleep(10);
    const first = (performance.now() - t0) / 1000, again = await draw(), again2 = await draw();
    (t[name] = t[name] || []).push(Math.min(again, again2));
    rows.push(name + ' round ' + (round + 1) + ': first picture ' + first.toFixed(2) + ' s, redraw ' + again.toFixed(2) + ' s and ' + again2.toFixed(2) + ' s');
  }
  const med = a => a.slice().sort((x, y) => x - y)[1], base = med(t.lathe);
  rows.push('m3d-default, Balanced, 12 passes, stage ' + $('stage').clientWidth + 'x' + $('stage').clientHeight + ', median of 3 rounds:');
  for (const [name] of runs) rows.push('   ' + name + ': ' + med(t[name]).toFixed(2) + ' s (best ' + Math.min(...t[name]).toFixed(2) + '), ' + (med(t[name]) / base).toFixed(2) + ' x the lathe');
  window.__sp.text = rows.join(NL); window.__sp.done = true;
})();
return 'timing';"""
sj = os.path.join(HERE, 'speed.json')
json.dump([{"wait": "done", "timeout": 600}, {"js": JS, "wait": "window.__sp.done", "timeout": 1800}, {"js": "return window.__sp.text;"}], open(sj, 'w', encoding='utf-8'))
sys.exit(subprocess.call([sys.executable, os.path.join(ROOT, 'notes', 'approaches_run.py'), 'dist/lab2-axisbulb.html', 'out/lab2/axisbulb/speed.txt', '--actions', sj], cwd=ROOT))

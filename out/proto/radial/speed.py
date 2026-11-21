"""Time the default Mandelbrot picture (Balanced, 12 passes) with the pillow and with Sphere inversions, back to back.
   python out/proto/radial/speed.py     -> out/proto/radial/speed.txt
Four rounds, alternating. Each round: switch approach (first picture, which includes preparing the shader and
the scorecard), then two plain redraws; the shorter redraw is that round's time."""
import json, os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
JS = """const L = window.squaringLab, S = L.S, $ = id => document.getElementById(id), sleep = ms => new Promise(r => setTimeout(r, ms));
L.R.warmOn = false; window.__sp = { done: false, text: '' };
(async () => {
  const rows = [], t = {}, NL = String.fromCharCode(10);
  const draw = async () => { L.touch(); const t0 = performance.now(); await sleep(40); while (!L.renderIdle()) await sleep(5); return (performance.now() - t0) / 1000; };
  for (let round = 0; round < 4; round++) for (const id of ['pillow', 'mercator']) {
    $('ap-' + id).click(); L.resetCam(); L.touch();
    const t0 = performance.now(); await sleep(60); while (!L.idle()) await sleep(10);
    const first = (performance.now() - t0) / 1000, again = await draw(), again2 = await draw();
    (t[id] = t[id] || []).push(Math.min(again, again2));
    rows.push(id + ' round ' + (round + 1) + ': first picture ' + first.toFixed(2) + ' s, redraw ' + again.toFixed(2) + ' s and ' + again2.toFixed(2) + ' s; parameters ' + JSON.stringify(S.param[id]));
  }
  const med = a => { const s = a.slice().sort((x, y) => x - y); return (s[1] + s[2]) / 2; }, mn = a => Math.min(...a);
  rows.push('m3d-default, Balanced, 12 passes, stage ' + $('stage').clientWidth + 'x' + $('stage').clientHeight + ': pillow median ' + med(t.pillow).toFixed(2) + ' s (best ' + mn(t.pillow).toFixed(2) + '), mercator median ' + med(t.mercator).toFixed(2) + ' s (best ' + mn(t.mercator).toFixed(2) + '), ratio pillow / mercator = ' + (med(t.pillow) / med(t.mercator)).toFixed(2));
  window.__sp.text = rows.join(NL); window.__sp.done = true;
})();
return 'timing';"""
sj = os.path.join(HERE, 'speed.json')
json.dump([{"wait": "done", "timeout": 300}, {"js": JS, "wait": "window.__sp.done", "timeout": 900}, {"js": "return window.__sp.text;"}], open(sj, 'w', encoding='utf-8'))
sys.exit(subprocess.call([sys.executable, os.path.join(ROOT, 'notes', 'approaches_run.py'), 'dist/proto-radial.html', 'out/proto/radial/speed.txt', '--actions', sj], cwd=ROOT))

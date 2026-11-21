"""Checks run inside the test page (the page's own MATH functions), plus a back-to-back speed run.
   python out/lab2/pillow2/inpage.py      -> out/lab2/pillow2/inpage.json, inpage.log"""
import json, os, re, subprocess, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))

CHECK = r"""
const L = window.squaringLab, M = L.MATH;
let seed = 12345; const rnd = () => (seed = (seed * 1664525 + 1013904223) % 4294967296) / 4294967296;
const out = {};
for (const id of ['pillowboth', 'pillowsmooth', 'mercator']) {
  let ez = 0, ey = 0, zmax = 0, ymax = 0;
  for (let i = 0; i < 200000; i++) {
    const r = 0.2 + 1.6 * rnd(), t = 2 * Math.PI * (i < 721 ? i / 720 : rnd());
    const ex = r * r * Math.cos(2 * t), ei = r * r * Math.sin(2 * t);
    const a = M[id]([r * Math.cos(t), r * Math.sin(t), 0], 2);
    ez = Math.max(ez, Math.hypot(a[0] - ex, a[1] - ei) / (r * r)); zmax = Math.max(zmax, Math.abs(a[2]));
    const b = M[id]([r * Math.cos(t), 0, r * Math.sin(t)], 2);
    ey = Math.max(ey, Math.hypot(b[0] - ex, b[2] - ei) / (r * r)); ymax = Math.max(ymax, Math.abs(b[1]));
  }
  // continuity: the largest step along 24 great circles at two samplings (a jump keeps its size, a continuous map shrinks 10x)
  let s1 = 0, s2 = 0;
  for (let c = 0; c < 24; c++) {
    let u = [rnd() - 0.5, rnd() - 0.5, rnd() - 0.5], w = [rnd() - 0.5, rnd() - 0.5, rnd() - 0.5];
    if (c === 0) { u = [1, 0, 0]; w = [0, 1e-9, 1]; } if (c === 1) { u = [1, 0, 0]; w = [0, 1, 1e-9]; } if (c === 2) { u = [0, 1, 0]; w = [-0.5, 0, 0.8660254]; }
    const lu = Math.hypot(...u); u = u.map(x => x / lu);
    const d = u[0] * w[0] + u[1] * w[1] + u[2] * w[2]; w = w.map((x, j) => x - d * u[j]); const lw = Math.hypot(...w); w = w.map(x => x / lw);
    for (const [N, slot] of [[20000, 1], [200000, 2]]) {
      let prev = null, mx = 0;
      for (let i = 0; i <= N; i++) {
        const t = 2 * Math.PI * i / N, p = M[id]([0, 1, 2].map(j => Math.cos(t) * u[j] + Math.sin(t) * w[j]), 2);
        if (prev) mx = Math.max(mx, Math.hypot(p[0] - prev[0], p[1] - prev[1], p[2] - prev[2]));
        prev = p;
      }
      if (slot === 1) s1 = Math.max(s1, mx); else s2 = Math.max(s2, mx);
    }
  }
  out[id] = { z0_err: ez, z0_zmax: zmax, y0_err: ey, y0_ymax: ymax, step20k: s1, step200k: s2 };
}
const pts = [];
for (let i = 0; i < 400; i++) { const v = [2 * rnd() - 1, 2 * rnd() - 1, (i % 7 === 0 ? 0.001 : 1) * (2 * rnd() - 1)]; pts.push([v, M.pillowboth(v, 2), M.pillowsmooth(v, 2)]); }
out.pts = pts;
return JSON.stringify(out);
"""

SPEED = r"""
const L = window.squaringLab, S = L.S;
const wait = () => new Promise(res => { const f = () => (L.idle() ? res() : setTimeout(f, 5)); setTimeout(f, 40); });
document.getElementById('mode-m').click(); S.flat = false; S.cutOn = false; S.n = 2; S.colour.mode = 0; L.resetCam(); L.R.warmOn = false;
const ids = [['pillowsmooth', 0], ['pillowboth', 0], ['mercator', 1], ['mercator', 2]], times = {};
for (let round = 0; round < 7; round++) for (const [id, planes] of ids) {
  S.approach = L.APPROACHES.findIndex(a => a.id === id); if (planes) S.param.mercator.planes = planes;
  L.refresh(false); await wait();
  const t0 = performance.now(); L.touch(); await wait();
  if (round > 0) (times[id + (planes || '')] = times[id + (planes || '')] || []).push(Math.round(performance.now() - t0));
}
return JSON.stringify(times);
"""
acts = [{"js": CHECK}, {"js": SPEED, "wait": "done", "timeout": 900}]
json.dump(acts, open(os.path.join(HERE, 'inpage-actions.json'), 'w', encoding='utf-8'), indent=1)
env = dict(os.environ, PYTHONIOENCODING='utf-8')
log = subprocess.run([sys.executable, os.path.join(ROOT, 'tools', 'shot.py'), '--url', 'dist/lab2-pillow2.html', '--actions',
                      os.path.join(HERE, 'inpage-actions.json')], capture_output=True, text=True, encoding='utf-8', env=env, cwd=ROOT)
open(os.path.join(HERE, 'inpage.log'), 'w', encoding='utf-8').write(log.stdout[-200000:] + '\n--- stderr ---\n' + log.stderr[-5000:])
res = [json.loads(json.loads(m)) for m in re.findall(r'step \d+ result: (".*")', log.stdout)]
chk, spd = res[0], res[1]
pts = chk.pop('pts')
sys.path.insert(0, HERE)
sys.argv = [sys.argv[0], '64', '0']
import importlib.util
spec = importlib.util.spec_from_file_location('chk', os.path.join(HERE, 'checks_rules.py'))
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
V = np.array([p[0] for p in pts]).T
both_js = np.array([p[1] for p in pts]).T; smooth_js = np.array([p[2] for p in pts]).T
chk['numpy_vs_page'] = {
    'pillowboth (maths check code out/proto/maths) max difference': float(np.abs(np.array(m.sq_both(*V)) - both_js).max()),
    'pillowsmooth max difference': float(np.abs(np.array(m.sq_smooth(*V)) - smooth_js).max())}
med = {k: float(np.median(v)) for k, v in spd.items()}
chk['speed_ms'] = spd; chk['speed_median_ms'] = med
chk['speed_ratio_to_mercator1'] = {k: round(v / med['mercator1'], 2) for k, v in med.items()}
json.dump(chk, open(os.path.join(HERE, 'inpage.json'), 'w', encoding='utf-8'), indent=1)
print(json.dumps(chk, indent=1))
print(log.stdout[-300:])

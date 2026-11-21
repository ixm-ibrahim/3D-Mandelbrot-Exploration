"""Round 20, entry: which of the lab's three distance estimates may draw "Wind, then square"?

For a scene and an estimate (0 Rough, 1 One neighbour, 3 Exact) the lab draws the Julia set; then 33 x 25 rays are
sent through the picture with the lab's own pick (the same ray marcher, the same estimate), and every place where a
ray stops is compared with the set itself, worked point by point in 64-bit numbers with the page's MATH (bounded
after the same number of steps, escape radius 64, the page's own test). A stop with no point of the set within N
pixels of it is something drawn that is not there. Calibration: Turning plane, along (known false sheets with Exact)
and Sphere inversions, one plane (known good with Exact).

  python out/r20/entry/measure.py [group]     -> de-<scene>-<id>-<de>.png, measure-<group>.txt, measure-<group>.json
"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import run

BAS, RAB, SIE, DEN = [-1, 0, 0], [-0.122561, 0.744862, 0], [-0.390541, -0.586788, 0], [0, 1, 0]
SIDE = dict(yaw=-1.9, pitch=0.3, dist=4.6, target=[0, 0, 0])
SCENES = {
    'bas-whole': dict(c=BAS, it=40, cam=SIDE),
    'bas-neck': dict(c=BAS, it=40, cam=dict(yaw=-1.9, pitch=0.9, dist=0.25, target=[-0.618, 0, 0])),
    'bas-bud60': dict(c=BAS, it=40, cam=dict(yaw=-1.9, pitch=0.5, dist=0.9, target=[0, 0.3, 0.52])),
    'bas-mid30': dict(c=BAS, it=40, cam=dict(yaw=-1.2, pitch=0.5, dist=0.6, target=[0, 0.43, 0.25])),
    'rabbit-whole': dict(c=RAB, it=40, cam=SIDE),
    'siegel-whole': dict(c=SIE, it=40, cam=SIDE),
    'dendrite-whole': dict(c=DEN, it=20, cam=SIDE),
    # looking straight at the skin from outside: half way between two carrying half-planes (30 degrees), and at the bud at 60 degrees
    'bas-skin30': dict(c=BAS, it=40, cam=dict(yaw=1.5708, pitch=0.5236, dist=0.5, target=[0, 0.433, 0.25])),
    'bas-bud60out': dict(c=BAS, it=40, cam=dict(yaw=1.5708, pitch=1.0472, dist=0.8, target=[0, 0.3, 0.52])),
}
GROUPS = {
    'main': [(s, 'windsq', de) for s in SCENES for de in (0, 1, 3)],
    'skin': [(s, 'windsq', de) for s in ('bas-skin30', 'bas-bud60out') for de in (0, 1, 3)],
    # the Rough estimate with smaller ray steps (the page's "Ray step" dial; 0.8 is what the page opens with)
    'step': [(s, 'windsq', 0, k) for s in ('bas-whole', 'rabbit-whole', 'siegel-whole', 'bas-skin30') for k in (0.8, 0.4, 0.2)],
    'calib': [('bas-whole', 'turnalong', 0), ('bas-whole', 'turnalong', 3), ('bas-neck', 'turnalong', 0), ('bas-neck', 'turnalong', 3),
              ('bas-whole', 'mercator', 3), ('bas-whole', 'mercator', 0), ('rabbit-whole', 'mercator', 3), ('rabbit-whole', 'mercator', 0)],
}

HEAD = """
const L = window.squaringLab, S = L.S, M = L.MATH, $ = id => document.getElementById(id);
const sleep = ms => new Promise(r => setTimeout(r, ms));
const go = () => { L.syncControls(); L.refresh(false); L.touch(); if (L.viewChanged) L.viewChanged(); };
"""
SET = HEAD + """
const q = %s;
$('mode-j').click(); await sleep(150);                       // Julia first: no Mandelbrot picture of the rule is ever drawn
$('ap-' + q.id).click(); await sleep(250);
S.n = 2; S.iter = q.it; S.flat = false; S.cutOn = false; S.c = q.c; S.q.de = q.de; S.q.aa = 2; S.q.stepk = q.stepk || 0.8;
L.resetCam(); L.cam.yaw = q.cam.yaw; L.cam.pitch = q.cam.pitch; L.cam.dist = q.cam.dist; L.cam.target = q.cam.target;
go(); await sleep(250);
return q.scene + ' ' + q.id + ' de ' + q.de + ': mode ' + S.mode + ', approach ' + L.APPROACHES[S.approach].id + ', iter ' + S.iter + ', c ' + JSON.stringify(S.c);
"""
MEAS = HEAD + """
const q = %s;
const stage = $('stage'), W = stage.clientWidth, H = stage.clientHeight, b = L.basis(), E = b.pos, fov = S.view.fov;
const F = v => M[q.id](v, 2, {}), c = q.c, its = q.it;
const inside = p => { let z = p; for (let s = 0; s < its; s++) { if (!(Math.hypot(z[0], z[1], z[2]) <= 64)) return false; const f = F(z); z = [f[0] + c[0], f[1] + c[1], f[2] + c[2]]; } return Math.hypot(z[0], z[1], z[2]) <= 64; };
const at = (d, t) => [E[0] + t * d[0], E[1] + t * d[1], E[2] + t * d[2]];
const NX = 33, NY = 25;
let seed = 7;
const rnd = () => { seed = (seed * 1664525 + 1013904223) >>> 0; return seed / 4294967296; };
// the set itself along each ray: the first point of it, by marching in steps of 2 pixels (at most 3000 steps) and halving
window.__true = window.__true || {};
let T = window.__true[q.scene + q.id];
if (!T) {
  T = [];
  for (let j = 0; j < NY; j++) for (let i = 0; i < NX; i++) {
    const px = W * (i + 0.5) / NX, py = H * (j + 0.5) / NY, ux = (2 * px - W) / H * fov, uy = (H - 2 * py) / H * fov;
    let d = [0, 1, 2].map(k => b.f[k] + ux * b.right[k] + uy * b.up[k]); const l = Math.hypot(d[0], d[1], d[2]); d = d.map(x => x / l);
    const be = E[0] * d[0] + E[1] * d[1] + E[2] * d[2], cc = E[0] * E[0] + E[1] * E[1] + E[2] * E[2] - 2.3 * 2.3, disc = be * be - cc;
    let tT = null;
    if (disc > 0) {
      const t0 = Math.max(0, -be - Math.sqrt(disc)), t1 = -be + Math.sqrt(disc), pix0 = 2 * fov * q.cam.dist / H, dt = Math.max(2 * pix0, (t1 - t0) / 3000);
      let prev = t0;
      for (let t = t0; t <= t1; t += dt) { if (inside(at(d, t))) { let lo = prev, hi = t; for (let k = 0; k < 12; k++) { const m = 0.5 * (lo + hi); if (inside(at(d, m))) hi = m; else lo = m; } tT = hi; break; } prev = t; }
    }
    T.push({ px, py, d, tT });
  }
  window.__true[q.scene + q.id] = T;
}
// the lab's own stops, and how far each is from the set
const R = { scene: q.scene, id: q.id, de: q.de, stepk: q.stepk, rays: T.length, labHits: 0, trueHits: 0, both: 0, labOnly: 0, trueOnly: 0, resid: 0, far: {}, behind: 0, diffs: [] };
const RAD = [1, 2, 4, 8, 16, 32];
const worst = [];
for (const r of T) {
  const Hh = L.pick(r.px, r.py);
  if (r.tT !== null) R.trueHits++;
  if (!Hh) { if (r.tT !== null) R.trueOnly++; continue; }
  R.labHits++;
  const v = [Hh[0] - E[0], Hh[1] - E[1], Hh[2] - E[2]], tH = v[0] * r.d[0] + v[1] * r.d[1] + v[2] * r.d[2];
  R.resid = Math.max(R.resid, Math.hypot(v[0] - tH * r.d[0], v[1] - tH * r.d[1], v[2] - tH * r.d[2]));
  const pix = 2 * fov * tH / H;
  if (r.tT !== null) { R.both++; R.diffs.push((r.tT - tH) / pix); if (r.tT - tH < -8 * pix) R.behind++; } else R.labOnly++;
  // distance from the stop to the set, in pixels: the first ball round the stop that holds a point of the set
  let cls = '>32';
  if (inside(Hh)) cls = 0;
  else for (const k of RAD) {
    let hit = false;
    for (let s = -10; s <= 10 && !hit; s++) hit = inside(at(r.d, tH + s * k * pix / 10));
    for (let s = 0; s < 60 && !hit; s++) { const z = rnd() * 2 - 1, a = rnd() * 6.283185307, h = Math.sqrt(1 - z * z), rr = k * pix * Math.cbrt(rnd()); hit = inside([Hh[0] + rr * h * Math.cos(a), Hh[1] + rr * h * Math.sin(a), Hh[2] + rr * z]); }
    if (hit) { cls = k; break; }
  }
  R.far[cls] = (R.far[cls] || 0) + 1;
  if (cls === '>32' || cls >= 16) worst.push([Math.round(r.px), Math.round(r.py), Hh.map(x => +x.toFixed(4)), cls]);
}
R.diffs.sort((a, b) => a - b);
const qd = p => (R.diffs.length ? +R.diffs[Math.min(R.diffs.length - 1, Math.floor(p * R.diffs.length))].toFixed(2) : null);
R.diffPix = { q05: qd(0.05), q25: qd(0.25), median: qd(0.5), q75: qd(0.75), q95: qd(0.95) };
delete R.diffs;
R.worst = worst.slice(0, 12);
return JSON.stringify(R);
"""


def main(group):
    todo = GROUPS[group]
    steps = [run.UP]
    for item in todo:
        scene, id_, de = item[:3]
        q = dict(SCENES[scene], scene=scene, id=id_, de=de, stepk=item[3] if len(item) > 3 else 0.8)
        steps.append({'js': SET % json.dumps(q), 'wait': 'done', 'timeout': 900, 'shot': run.REL + 'de-%s-%s-%d%s.png' % (scene, id_, de, '-step%g' % item[3] if len(item) > 3 else ''), 'clip': '#stage canvas'})
        steps.append({'js': MEAS % json.dumps(q), 'timeout': 1800})
    # leave the page on the one-plane rule
    steps.append({'js': HEAD + "$('mode-j').click(); await sleep(100); $('ap-mercator').click(); await sleep(200); S.q.de = 3; S.q.stepk = 0.8; go(); return 'end: failed ' + L.R.failed;", 'wait': 'done', 'timeout': 600})
    code, text, vals = run.shot(run.PAGE, steps, 'measure-%s-steps' % group)
    res = [json.loads(v) for v in vals if v.startswith('{')]
    json.dump(res, open(os.path.join(HERE, 'measure-%s.json' % group), 'w', encoding='utf-8'), indent=1)
    lines = ['Each row: scene, entry, estimate (0 Rough, 1 One neighbour, 3 Exact); of 825 rays how many the lab stops (lab) and how many meet the set itself (true);',
             'then, for the lab\'s stops, how far the nearest point of the set is, in pixels of that picture: on it / within 1, 2, 4, 8, 16, 32 / further.',
             'false = stops with no point of the set within 8 pixels. missed = rays that meet the set where the lab stops nothing. through = stops more than 8 pixels behind the first point of the set.', '']
    for r in res:
        f = r['far']; g = lambda k: f.get(str(k), 0)
        false8 = g(16) + g(32) + g('>32')
        lines.append('%-15s %-9s de %d step %g: lab %3d true %3d | on %3d  1: %3d  2: %3d  4: %3d  8: %3d  16: %3d  32: %3d  further: %3d | false %3d (%.1f %% of stops)  missed %3d  through %3d | true first point minus stop, pixels: 5 %% %s, median %s, 95 %% %s | ray model off by %.1e' % (
            r['scene'], r['id'], r['de'], r.get('stepk', 0.8), r['labHits'], r['trueHits'], g(0), g(1), g(2), g(4), g(8), g(16), g(32), g('>32'), false8, 100.0 * false8 / max(1, r['labHits']),
            r['trueOnly'], r['behind'], r['diffPix']['q05'], r['diffPix']['median'], r['diffPix']['q95'], r['resid']))
    out = '\n'.join(lines) + '\n'
    run.write('measure-%s.txt' % group, out + '\n' + '\n'.join(l for l in text.splitlines() if 'result: {' not in l) + '\n')
    print(out)
    print('\n'.join(l for l in text.splitlines() if 'result: {' not in l)[-1500:])
    return code


if __name__ == '__main__':
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else 'main'))

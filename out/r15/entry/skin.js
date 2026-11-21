// Round 15, entry: how far can the skin of the 3D picture be trusted? Runs inside the page (tools/shot.py).
// For a grid of rays through the picture: where the page's own probe (L.pick, the picture's ray march) stops, against
// where a brute-force walk along the same ray first meets a point of the set (MATH.sqpillow iterated in JavaScript,
// samples 0.002 apart, then halved 24 times). depth = probe − brute force, along the ray: below 0 the picture's skin
// stands in front of the true set, above 0 the picture has gone through something the walk found.
const L = window.squaringLab, S = L.S, M = L.MATH, $ = id => document.getElementById(id);
const sleep = ms => new Promise(r => setTimeout(r, ms));
const go = () => { L.syncControls(); L.refresh(false); L.touch(); if (L.viewChanged) L.viewChanged(); };
const idle = async () => { for (let i = 0; i < 3000; i++) { await sleep(100); if (L.idle()) return true; } return false; };
const ID = window.__skinId || 'sqpillow';
const VIEWS = window.__skinViews || [['j', [-1, 0, 0]], ['j', [-0.12, 0.74, 0]], ['m', null], ['j', [0, 1, 0]]];
const out = { id: ID, iter: 0, views: [] };
let seed = 15; const rnd = () => { seed = (seed * 1664525 + 1013904223) >>> 0; return seed / 4294967296; };
const add = (a, b) => [a[0] + b[0], a[1] + b[1], a[2] + b[2]], scl = (a, k) => [a[0] * k, a[1] * k, a[2] * k];
const len = a => Math.hypot(a[0], a[1], a[2]), dot = (a, b) => a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
for (const [mode, c] of VIEWS) {
  $('ap-' + ID).click(); await sleep(250); S.n = 2; S.iter = 14;
  $('mode-' + mode).click(); await sleep(150); S.flat = false; S.cutOn = false;
  if (c) S.c = c.slice();
  L.resetCam(); go(); await sleep(200); await idle();
  const q = S.param[ID], its = S.iter, jul = mode === 'j', cc = S.c.slice();
  out.iter = its;
  const inside = P => {
    let z = jul ? P : [0, 0, 0];
    const k = jul ? cc : P;
    for (let i = 0; i <= its; i++) {
      if (!(len(z) <= 64)) return false;
      if (i === its) break;
      z = add(M[ID](z, 2, q), k);
    }
    return true;
  };
  const w = $('stage').clientWidth, h = $('stage').clientHeight, b = L.basis(), fov = S.view.fov;
  const NX = 28, NY = 22, DT = 0.002, RB = 2.6;
  const rows = [];
  let offRay = 0;
  for (let i = 1; i < NX; i++) for (let j = 1; j < NY; j++) {
    const px = w * i / NX, py = h * j / NY, ux = (2 * px - w) / h, uy = (h - 2 * py) / h;
    let d = add(b.f, add(scl(b.right, fov * ux), scl(b.up, fov * uy))); d = scl(d, 1 / len(d));
    const hit = L.pick(px, py);
    let tp = null;
    if (hit) { const rel = add(hit, scl(b.pos, -1)); tp = dot(rel, d); offRay = Math.max(offRay, len(add(rel, scl(d, -tp)))); }
    // the stretch of the ray inside the ball of radius RB
    const bq = dot(b.pos, d), cq = dot(b.pos, b.pos) - RB * RB, disc = bq * bq - cq;
    let tt = null;
    if (disc > 0) {
      const t0 = Math.max(0, -bq - Math.sqrt(disc)), t1 = -bq + Math.sqrt(disc);
      for (let t = t0; t <= t1; t += DT) {
        if (inside(add(b.pos, scl(d, t)))) {
          let lo = Math.max(t - DT, t0), hi = t;
          if (!inside(add(b.pos, scl(d, lo)))) for (let k = 0; k < 24; k++) { const m = 0.5 * (lo + hi); if (inside(add(b.pos, scl(d, m)))) hi = m; else lo = m; }
          tt = hi; break;
        }
      }
    }
    // how far the probe's stopping point is from the set in ANY direction: the smallest of a row of balls round it
    // in which 240 random points include one of the set (null: none within 0.4)
    let near = null;
    if (hit) {
      if (inside(hit)) near = 0;
      else for (const rad of [0.003, 0.006, 0.0125, 0.025, 0.05, 0.1, 0.2, 0.4]) {
        let found = false;
        for (let k = 0; k < 240 && !found; k++) {
          let e; do { e = [2 * rnd() - 1, 2 * rnd() - 1, 2 * rnd() - 1]; } while (dot(e, e) > 1);
          found = inside(add(hit, scl(e, rad)));
        }
        if (found) { near = rad; break; }
      }
      if (near === null) near = 9;
    }
    rows.push([tp, tt, near]);
  }
  const both = rows.filter(r => r[0] !== null && r[1] !== null).map(r => r[0] - r[1]).sort((a, b) => a - b);
  const qn = p => (both.length ? both[Math.min(both.length - 1, Math.floor(p * both.length))] : null);
  const ab = both.map(Math.abs).sort((a, b) => a - b), qa = p => (ab.length ? ab[Math.min(ab.length - 1, Math.floor(p * ab.length))] : null);
  out.views.push({
    mode, c: jul ? cc : null, rays: rows.length, pixel: 2 * fov * L.cam.dist / h, camDist: L.cam.dist, probeOffItsRay: offRay,
    bothHit: both.length, pictureOnly: rows.filter(r => r[0] !== null && r[1] === null).length, walkOnly: rows.filter(r => r[0] === null && r[1] !== null).length, neither: rows.filter(r => r[0] === null && r[1] === null).length,
    depth: { min: qn(0), q05: qn(0.05), median: qn(0.5), q95: qn(0.95), max: qn(0.9999) },
    absDepth: { median: qa(0.5), q90: qa(0.9), q99: qa(0.99), max: qa(0.9999) },
    // the skin's distance from the set, any direction, over every ray the picture stopped on
    skinOff: (() => { const n = rows.filter(r => r[2] !== null).map(r => r[2]), c = x => n.filter(v => v > x).length; return { stops: n.length, onOrWithin0003: n.filter(v => v <= 0.003).length, over0003: c(0.003), over00125: c(0.0125), over0025: c(0.025), over005: c(0.05), over01: c(0.1), over02: c(0.2), noneWithin04: c(0.4) }; })(),
    inFront: { over001: both.filter(x => x < -0.01).length, over003: both.filter(x => x < -0.03).length, over01: both.filter(x => x < -0.1).length, over03: both.filter(x => x < -0.3).length },
    wentThrough: { over001: both.filter(x => x > 0.01).length, over003: both.filter(x => x > 0.03).length, over01: both.filter(x => x > 0.1).length, over03: both.filter(x => x > 0.3).length },
  });
}
return JSON.stringify(out);

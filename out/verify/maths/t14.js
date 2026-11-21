// Point 14: the two Mandelbulbs against the published formulas, phases, lift and turn.
const out = { zeroPhase: [], phase: [], fails: [], texts: {} };
const rnd = rng(21), rad = d => d * PI / 180;
const space = () => { const r = 0.2 + 2 * rnd(), u = rnd() * 2 - 1, a = (rnd() * 2 - 1) * PI, s = Math.sqrt(1 - u * u); return [r * s * Math.cos(a), r * s * Math.sin(a), r * u]; };
const dist = (a, b) => Math.hypot(a[0] - b[0], a[1] - b[1], a[2] - b[2]);
// White and Nylander: theta from the z-axis, phi around it (the formula on Wikipedia)
const refClassic = (v, n, t0 = 0, p0 = 0, before = false) => {
  const r = Math.hypot(...v), th = Math.acos(v[2] / r), ph = Math.atan2(v[1], v[0]);
  const T = before ? (th + t0) * n : th * n + t0, P = before ? (ph + p0) * n : ph * n + p0, R = Math.pow(r, n);
  return [R * Math.sin(T) * Math.cos(P), R * Math.sin(T) * Math.sin(P), R * Math.cos(T)];
};
// the "cosine" Mandelbulb: latitude counted from the equator
const refBulb = (v, n, b0 = 0, p0 = 0, before = false) => {
  const r = Math.hypot(...v), la = Math.asin(v[2] / r), ph = Math.atan2(v[1], v[0]);
  const B = before ? (la + b0) * n : la * n + b0, P = before ? (ph + p0) * n : ph * n + p0, R = Math.pow(r, n);
  return [R * Math.cos(B) * Math.cos(P), R * Math.cos(B) * Math.sin(P), R * Math.sin(B)];
};
for (const n of [2, 3, 4, 8, -1, -2, -3, 2.5]) {
  let wc = 0, wb = 0, wc0 = 0, wb0 = 0;
  for (let i = 0; i < 200; i++) {
    const v = space(), m = Math.pow(Math.hypot(...v), n);
    wc = Math.max(wc, dist(M.classic(v, n, {}), refClassic(v, n)) / m);
    wb = Math.max(wb, dist(M.bulb(v, n, {}), refBulb(v, n)) / m);
    wc0 = Math.max(wc0, dist(M.classic(v, n, { theta: 0, phi: 0 }), refClassic(v, n)) / m);
    wb0 = Math.max(wb0, dist(M.bulb(v, n, { lat: 0, lon: 0 }), refBulb(v, n)) / m);
  }
  out.zeroPhase.push(`n=${n}: classic vs White-Nylander ${sci(Math.max(wc, wc0))}; bulb vs equator-latitude formula ${sci(Math.max(wb, wb0))}`);
  if (Math.max(wc, wb, wc0, wb0) > 1e-9) out.fails.push('zero-phase mismatch at n=' + n);
}
// the n = 2 closed forms printed on the page
{
  let wb = 0;
  for (let i = 0; i < 200; i++) {
    const [x, y, z] = space(), rho2 = x * x + y * y, k = (rho2 - z * z) / rho2;
    wb = Math.max(wb, dist(M.bulb([x, y, z], 2, {}), [k * (x * x - y * y), k * 2 * x * y, 2 * Math.sqrt(rho2) * z]));
  }
  out.zeroPhase.push(`bulb n=2 vs the printed closed form: ${sci(wb)}`);
}
// phases: after the multiplication (angle·n + phase) or before ((angle + phase)·n)?
for (const n of [2, 8, -2]) for (const [d1, d2] of [[20, 0], [0, 35], [47, -110]]) {
  let ca = 0, cb = 0, ba = 0, bb = 0, cbs = 0, bbs = 0;
  for (let i = 0; i < 200; i++) {
    const v = space(), m = Math.pow(Math.hypot(...v), n);
    const C = M.classic(v, n, { theta: d1, phi: d2 }), B = M.bulb(v, n, { lat: d1, lon: d2 });
    ca = Math.max(ca, dist(C, refClassic(v, n, rad(d1), rad(d2))) / m); cb = Math.max(cb, dist(C, refClassic(v, n, rad(d1), rad(d2), true)) / m);
    ba = Math.max(ba, dist(B, refBulb(v, n, rad(d1), rad(d2))) / m); bb = Math.max(bb, dist(B, refBulb(v, n, rad(d1), rad(d2), true)) / m);
    cbs = Math.max(cbs, dist(C, refClassic(v, n, rad(d1) / n, rad(d2) / n, true)) / m); bbs = Math.max(bbs, dist(B, refBulb(v, n, rad(d1) / n, rad(d2) / n, true)) / m);
  }
  out.phase.push(`n=${n} phases (${d1}°, ${d2}°): classic vs after-form ${sci(ca)}, vs before-form ${sci(cb)}, vs before-form with phase/n ${sci(cbs)}; bulb vs after ${sci(ba)}, before ${sci(bb)}, before with phase/n ${sci(bbs)}`);
}
// classic with theta phase (1 - n)·90° is the equator Mandelbulb
{
  const rows = [];
  for (const n of [2, 3, 8, -2]) { let w = 0; for (let i = 0; i < 200; i++) { const v = space(); w = Math.max(w, dist(M.classic(v, n, { theta: (1 - n) * 90 }), M.bulb(v, n, {})) / Math.pow(Math.hypot(...v), n)); } rows.push(`n=${n}: ${sci(w)}`); }
  out.thetaFix = 'classic with θ phase (1−n)·90° vs bulb: ' + rows.join(', ');
}
// Sphere inversions: lift is added to the Mercator latitude after ×n, turn to the longitude after ×n (one plane)
{
  let wl = 0, wt = 0, turnIgnored = 0, liftAt2 = 0;
  for (const n of [2, 3, 8, -2]) for (let i = 0; i < 200; i++) {
    const r = 0.3 + 2 * rnd(), u = (rnd() * 2 - 1) * 0.8, a = (rnd() * 2 - 1) * PI, s = Math.sqrt(1 - u * u), v = [r * s * Math.cos(a), r * s * Math.sin(a), r * u];
    const lift = 0.37, turn = 40, w = M.mercator(v, n, { planes: 1, lift, turn }), R = Math.hypot(...w);
    if (Math.abs(n * Math.atanh(u)) < 6) wl = Math.max(wl, Math.abs(Math.atanh(w[2] / R) - (n * Math.atanh(u) + lift)));
    let dl = Math.atan2(w[1], w[0]) - (n * a + rad(turn)); dl -= 2 * PI * Math.round(dl / (2 * PI)); wt = Math.max(wt, Math.abs(dl));
    turnIgnored = Math.max(turnIgnored, dist(M.mercator(v, n, { planes: 2, turn: 40 }), M.mercator(v, n, { planes: 2, turn: 0 })));
    liftAt2 = Math.max(liftAt2, dist(M.mercator(v, n, { planes: 2, lift: 0.37 }), M.mercator(v, n, { planes: 2, lift: 0 })));
  }
  out.liftTurn = `lift: Mercator latitude out − (n·in + lift) worst ${sci(wl)}; turn: longitude out − (n·in + turn) worst ${sci(wt)} rad; with 2 planes a turn changes the result by at most ${sci(turnIgnored)} (ignored), a lift by up to ${sci(liftAt2)} (active)`;
}
// "For z^n + c it turns the Mandelbrot solid about the z-axis": c is in the turned set  <=>  Rz(phi/(n-1)) c is in the plain set
function esc(id, q, n, c, iter = 14) { let v = [0, 0, 0]; for (let k = 0; k < iter; k++) { const w = M[id](v, n, q); v = [w[0] + c[0], w[1] + c[1], w[2] + c[2]]; if (Math.hypot(...v) > 64) return k + 1; } return 0; }
{
  const rows = [];
  for (const [id, key, base] of [['mercator', 'turn', { planes: 1 }], ['bulb', 'lon', {}], ['classic', 'phi', {}]]) for (const n of [2, 3, 8]) {
    const deg = 50, al = rad(deg) / (n - 1); let diff = 0, N = 3000, inside = 0, plainDiff = 0;
    for (let i = 0; i < N; i++) {
      const c = [rnd() * 3 - 2, rnd() * 3 - 1.5, rnd() * 2 - 1], rc = [Math.cos(al) * c[0] - Math.sin(al) * c[1], Math.sin(al) * c[0] + Math.cos(al) * c[1], c[2]];
      const a = esc(id, { ...base, [key]: deg }, n, c), b = esc(id, { ...base, [key]: 0 }, n, rc), p = esc(id, { ...base, [key]: 0 }, n, c);
      if (a !== b) diff++; if (a !== p) plainDiff++; if (!a) inside++;
    }
    rows.push(`${id}.${key}=50° n=${n}: escape counts differ from the plain set turned by ${(deg / (n - 1)).toFixed(2)}° at ${diff}/${N} points (${inside} inside); from the unturned plain set at ${plainDiff}`);
  }
  out.turnClaim = rows;
}
// what z = 0 does under each non-default parameter (the standing requirement)
{
  const pts = planePoints(3).filter(p => p[2] === 'generic');
  const worstPlane = (id, q, n) => { let w = 0, wz = 0; for (const [x, y] of pts) { const g = M[id]([x, y, 0], n, q), ref = cpow([x, y], n), m = Math.hypot(...ref); w = Math.max(w, Math.hypot(g[0] - ref[0], g[1] - ref[1], g[2]) / m); wz = Math.max(wz, Math.abs(g[2]) / m); } return `rel err vs z^n ${sci(w)}, leaves the plane by ${sci(wz)}`; };
  out.breakers = {};
  const cases = [
    ['mercator planes=1..8 (defaults else)', 'mercator', [1, 2, 3, 4, 5, 6, 7, 8].map(k => ({ planes: k }))],
    ['mercator lift=0.3 (planes 2)', 'mercator', [{ planes: 2, lift: 0.3 }]],
    ['mercator lift=0.3 (planes 1)', 'mercator', [{ planes: 1, lift: 0.3 }]],
    ['mercator turn=40 (planes 1)', 'mercator', [{ planes: 1, turn: 40 }]],
    ['mercator turn=40 (planes 2: dial hidden)', 'mercator', [{ planes: 2, turn: 40 }]],
    ['lathe spin=-7,-5,-3,-1,3,5,7,9', 'lathe', [-7, -5, -3, -1, 3, 5, 7, 9].map(s => ({ spin: s }))],
    ['lathe spin=2 (even: the dial should not allow it)', 'lathe', [{ spin: 2 }]],
    ['bulb lat=30', 'bulb', [{ lat: 30 }]], ['bulb lon=30', 'bulb', [{ lon: 30 }]], ['bulb lat=180', 'bulb', [{ lat: 180 }]],
    ['classic defaults', 'classic', [{}]], ['classic theta=30', 'classic', [{ theta: 30 }]], ['classic phi=30', 'classic', [{ phi: 30 }]],
  ];
  for (const [label, id, qs] of cases) out.breakers[label] = [2, 3, -2].map(n => `n=${n}: ` + qs.map(q => worstPlane(id, q, n)).sort().pop()).join(' | ');
}
// the texts next to the controls
for (const a of L.APPROACHES) out.texts[a.id] = { about: a.about, params: (a.params || []).map(s => (s.type === 'note' ? 'NOTE: ' + s.text : `${s.label} [${s.min}..${s.max}, default ${s.def}${s.animate ? ', play' : ''}${s.odd ? ', odd' : ''}]: ${s.help || '(no help text)'}`)) };
out.sliceTexts = {
  'mercator lift 0.3': L.APPROACHES[0].slice(true, { planes: 2, lift: 0.3, turn: 0 }, 2),
  'mercator turn 40, 1 plane': L.APPROACHES[0].slice(true, { planes: 1, lift: 0, turn: 40 }, 2),
  'bulb lat 30': L.APPROACHES[2].slice(true, { lat: 30, lon: 0 }, 2), 'bulb lon 30': L.APPROACHES[2].slice(true, { lat: 0, lon: 30 }, 2),
  'classic default n=2': L.APPROACHES[3].slice(false, { theta: 0, phi: 0 }, 2), 'classic n=8': L.APPROACHES[3].slice(false, { theta: 0, phi: 0 }, 8), 'classic n=3': L.APPROACHES[3].slice(false, { theta: 0, phi: 0 }, 3),
  'lathe spin 3': L.APPROACHES[1].slice(true, { spin: 3 }, 2),
};
return out;

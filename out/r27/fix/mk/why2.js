// Round 27, fixer: what stands at the eye of the close-up at t = 1? The two numbers of the estimate there, the place
// the recipe ends at (in the object's own coordinates), and the true distance to the nearest ball by brute force
// (the smallest radius at which one of 4000 directions is inside, 300 rounds).
const t = 1, g = 0, rounds = 16, c = [-1.25, 0.5, 0.30, [0.525, 0, 0]];
if (!(S.mode === 'k' && S.k.group === 1)) { L.ballsShow(); await settle(); }
S.k.bt = t; S.k.bgrid = g; S.k.bit = rounds; S.flat = false; S.cutOn = false;
L.ballsFrame(); L.cam.yaw = c[0]; L.cam.pitch = c[1]; L.cam.dist = c[2]; L.cam.target = c[3].slice();
go(); await settle();
const b = L.basis(), ro = b.pos, K2 = 1.05, top = 2 * t;
let seed = 5; const rnd = () => { seed = (seed * 1664525 + 1013904223) >>> 0; return seed / 4294967296; };
const dirs = []; for (let i = 0; i < 4000; i++) { const u = 2 * rnd() - 1, a = 2 * Math.PI * rnd(), s = Math.sqrt(1 - u * u); dirs.push([s * Math.cos(a), s * Math.sin(a), u]); }
const trueDist = p => { for (let r = 1e-7; r < 10; r *= 1.05) for (const v of dirs) if (L.ballsInside(p[0] + r * v[0], p[1] + r * v[1], p[2] + r * v[2], { t, grid: g, rounds: 300 })) return r; return -1; };
// the recipe, reporting where it ends
const trace = p => { const ux = p[1], uy = p[2], uz = p[0] - K2 / 2; let d = ux * ux + uy * uy + uz * uz, DF = K2 / d;
  let m = [K2 * ux / d, K2 * uy / d, 1 + K2 * uz / d]; const path = [];
  for (let i = 0; i < 300; i++) { if (m[2] < 0 || m[2] > top) return { end: 'inside', i, path };
    const n = [Math.round(m[0]), Math.round(m[1])]; m[0] -= n[0]; m[1] -= n[1];
    const rb = m[0] * m[0] + m[1] * m[1] + m[2] * m[2], rt = m[0] * m[0] + m[1] * m[1] + (m[2] - top) * (m[2] - top);
    path.push([n[0], n[1], rb < 1 ? 'b' : rt < 1 ? 't' : 'F']);
    if (rb < 1) { m = m.map(x => x / rb); DF /= rb; } else if (rt < 1) { m = [m[0] / rt, m[1] / rt, top + (m[2] - top) / rt]; DF /= rt; }
    else return { end: 'outside', rounds: i + 1, m: m.map(x => +x.toFixed(5)), DF: +DF.toPrecision(5), rho: +Math.hypot(m[0], m[1]).toFixed(5), path: path.slice(-12) }; }
  return { end: 'undecided' }; };
const at = p => { const bf = L.ballsEstimate(p[0], p[1], p[2], { t, grid: g, rounds: 300, parts: true }); return { p: p.map(x => +x.toFixed(5)), best: bf[0], free: bf[1], true: trueDist(p), trace: trace(p) }; };
const out = { eye: at(ro), along: [] };
for (const s of [0.002, 0.01, 0.03, 0.1]) out.along.push(at([0, 1, 2].map(k => ro[k] + b.f[k] * s)));
// and a cloud of points round the kiss of the two big balls: estimate against the true distance
const cloud = [];
for (let i = 0; i < 60; i++) { const p = [0.525 + 0.5 * (rnd() - 0.5), 0.5 * (rnd() - 0.5), 0.5 * (rnd() - 0.5)], bf = L.ballsEstimate(p[0], p[1], p[2], { t, grid: g, rounds: 300, parts: true });
  if (bf[0] <= 0) continue; const td = trueDist(p), tr = trace(p); cloud.push([+(Math.min(bf[0], bf[1]) / td).toFixed(3), +(bf[1] / td).toFixed(3), +(bf[0] / td).toFixed(2), tr.rounds, tr.rho, tr.m ? tr.m[2] : 0]); }
cloud.sort((a, b2) => a[0] - b2[0]);
out.cloudEstimateOverTrue_freeOverTrue_bestOverTrue_rounds_rho_z = cloud;
return JSON.stringify(out);

// Checker of round 12: points of the drawn surface (the page's own pick, 21 x 15 pixels over the stage) against MATH.
// A picked point should lie on the edge of the set MATH gives: within a small ball around it there are points that
// stay inside (|v| <= 64 for the page's number of steps) and points that escape.
const L = window.squaringLab, S = L.S, M = L.MATH, ap = L.APPROACHES[S.approach], p = S.param[ap.id], PI = Math.PI;
const st = document.getElementById('stage'), w = st.clientWidth, h = st.clientHeight;
const foldk = (v, k) => { const [x, y, z] = v, rho = Math.hypot(y, z); if (rho < 1e-300) return v; const ww = PI / k, psi = Math.atan2(z, y), s = psi < 0 ? -1 : 1, a = Math.abs(psi), j = Math.floor(a / ww + 0.5), d = a - j * ww; let a2; if (2 * j < k || (2 * j === k && d < 0)) a2 = j % 2 === 0 ? d : -d; else a2 = PI + ((k - j) % 2 === 0 ? d : -d); a2 *= s; return [x, rho * Math.cos(a2), rho * Math.sin(a2)]; };
const cm = c => (ap.id === 'fold' ? foldk(c, Math.max(2, p.planes)) : c);
const inside = (pt, its) => { let v, c; if (S.mode === 'j') { v = pt.slice(); c = cm(S.c); } else { v = [0, 0, 0]; c = cm(pt); } for (let k = 0; k <= its; k++) { if (Math.hypot(v[0], v[1], v[2]) > 64) return false; if (k === its) break; v = M[ap.id](v, S.n, p); v = [v[0] + c[0], v[1] + c[1], v[2] + c[2]]; } return true; };
let seed = 4242; const rnd = () => { seed = (Math.imul(seed, 1664525) + 1013904223) >>> 0; return seed / 4294967296; };
const ball = []; for (let i = 0; i < 80; i++) { let d; do { d = [rnd() * 2 - 1, rnd() * 2 - 1, rnd() * 2 - 1]; } while (Math.hypot(...d) > 1); ball.push(d); }
const near = (pt, del, its) => { let a = 0, b = 0; const c0 = inside(pt, its); if (c0) a++; else b++; for (const d of ball) { if (inside([pt[0] + del * d[0], pt[1] + del * d[1], pt[2] + del * d[2]], its)) a++; else b++; if (a && b) return 0; } return a ? 1 : -1; };   // 0: on the edge, 1: all inside, -1: all outside
let hits = 0, ring = 0, far = 0; const tally = { d004: [0, 0, 0], d015: [0, 0, 0], d05: [0, 0, 0], d015_one_step_less: [0, 0, 0], d015_one_step_more: [0, 0, 0] };
for (let i = 0; i < 21; i++) for (let j = 0; j < 15; j++) {
  const px = Math.round(w * (i + 0.5) / 21), py = Math.round(h * (j + 0.5) / 15), pt = L.pick(px, py);
  if (!pt) continue; hits++; if (i === 0 || j === 0 || i === 20 || j === 14) ring++; far = Math.max(far, Math.hypot(...pt));
  const put = (key, r) => { tally[key][r === 0 ? 0 : r > 0 ? 1 : 2]++; };
  put('d004', near(pt, 0.004, S.iter)); put('d015', near(pt, 0.015, S.iter)); put('d05', near(pt, 0.05, S.iter));
  put('d015_one_step_less', near(pt, 0.015, S.iter - 1)); put('d015_one_step_more', near(pt, 0.015, S.iter + 1));
}
return JSON.stringify({ entry: ap.id, params: p, mode: S.mode, iter: S.iter, hits, onOuterRing: ring, farthestPickedPoint: +far.toFixed(3), drawingRadius: S.view.bound, 'ball 0.004 [on edge, all inside, all outside]': tally.d004, 'ball 0.015': tally.d015, 'ball 0.05': tally.d05, 'ball 0.015, one step fewer': tally.d015_one_step_less, 'ball 0.015, one step more': tally.d015_one_step_more });

// Checker of round 12: the picked surface points that had no point of the MATH set within 0.05 among 80 samples,
// searched again with 6000 samples in the ball, and along the line of sight behind the point.
const L = window.squaringLab, S = L.S, M = L.MATH, ap = L.APPROACHES[S.approach], p = S.param[ap.id];
const st = document.getElementById('stage'), w = st.clientWidth, h = st.clientHeight, B = L.basis();
const inside = (pt, its) => { let v, c; if (S.mode === 'j') { v = pt.slice(); c = S.c; } else { v = [0, 0, 0]; c = pt; } for (let k = 0; k <= its; k++) { if (Math.hypot(v[0], v[1], v[2]) > 64) return false; if (k === its) break; v = M[ap.id](v, S.n, p); v = [v[0] + c[0], v[1] + c[1], v[2] + c[2]]; } return true; };
let seed = 777; const rnd = () => { seed = (Math.imul(seed, 1664525) + 1013904223) >>> 0; return seed / 4294967296; };
let hits = 0, lone = 0, foundBall = 0, foundRay = 0, none = 0; const nearest = [], rayDepth = [];
for (let i = 0; i < 21; i++) for (let j = 0; j < 15; j++) {
  const pt = L.pick(Math.round(w * (i + 0.5) / 21), Math.round(h * (j + 0.5) / 15)); if (!pt) continue; hits++;
  let any = inside(pt, S.iter); for (let k = 0; k < 80 && !any; k++) { let d; do { d = [rnd() * 2 - 1, rnd() * 2 - 1, rnd() * 2 - 1]; } while (Math.hypot(...d) > 1); any = inside([pt[0] + 0.05 * d[0], pt[1] + 0.05 * d[1], pt[2] + 0.05 * d[2]], S.iter); }
  if (any) continue; lone++;
  let best = 9; for (let k = 0; k < 6000; k++) { let d; do { d = [rnd() * 2 - 1, rnd() * 2 - 1, rnd() * 2 - 1]; } while (Math.hypot(...d) > 1); const r = 0.05 * Math.hypot(...d); if (r < best && inside([pt[0] + 0.05 * d[0], pt[1] + 0.05 * d[1], pt[2] + 0.05 * d[2]], S.iter)) best = r; }
  const dir = [pt[0] - B.pos[0], pt[1] - B.pos[1], pt[2] - B.pos[2]], dl = Math.hypot(...dir); let depth = -1; for (let k = 0; k <= 4000; k++) { const t = k * 0.0001; if (inside([pt[0] + dir[0] / dl * t, pt[1] + dir[1] / dl * t, pt[2] + dir[2] / dl * t], S.iter)) { depth = t; break; } }
  if (best < 9) { foundBall++; nearest.push(+best.toFixed(4)); } if (depth >= 0) { foundRay++; rayDepth.push(+depth.toFixed(4)); } if (best === 9 && depth < 0) none++;
}
return JSON.stringify({ entry: ap.id, params: p, mode: S.mode, iter: S.iter, hits, withNoSetPointAmong80: lone, ofThose_setPointFoundAmong6000InBall0p05: foundBall, ofThose_setPointOnLineOfSightWithin0p4: foundRay, ofThose_nothingFoundEitherWay: none, nearestFound: nearest.sort((a, b) => a - b).slice(0, 12), depthBehindSurface: rayDepth.sort((a, b) => a - b) });

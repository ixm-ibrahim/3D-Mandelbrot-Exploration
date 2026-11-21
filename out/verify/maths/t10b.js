// Point 10: count the fins around the x-axis for the Sphere inversions approach, Mandelbrot mode, z^n + c from 0.
// The orbit copies the shader: c is folded once (cmap), every power folds z first, escape radius 64.
const fold = (v, k) => { // same as foldk in 10-approaches.js, used here only for c (cmap); MATH.mercator folds z itself
  if (k < 1.5) return v; const [x, y, z] = v, rho = Math.hypot(y, z); if (rho < 1e-300) return v;
  const w = PI / k, psi = Math.atan2(z, y), s = psi < 0 ? -1 : 1, a = Math.abs(psi), j = Math.floor(a / w + 0.5), d = a - j * w; let a2;
  if (2 * j < k || (2 * j === k && d < 0)) a2 = j % 2 === 0 ? d : -d; else a2 = PI + ((k - j) % 2 === 0 ? d : -d);
  a2 *= s; return [x, rho * Math.cos(a2), rho * Math.sin(a2)];
};
function solid(n, p, c0, iter) {   // true when the point belongs to the drawn solid
  const q = { planes: p }, c = fold(c0, p); let v = [0, 0, 0], r = 0;
  for (let k = 0; k <= iter; k++) {
    if (r > 64) return n < 0;             // negative powers: the page draws the region that escapes
    if (k === iter) break;
    let w = M.mercator(v, n, q); w = [w[0] + c[0], w[1] + c[1], w[2] + c[2]];
    const w2 = w[0] * w[0] + w[1] * w[1] + w[2] * w[2];
    if (k === 0 && r < 1e-3 && w2 > 1e36) { v = [1e9, 0, 0]; r = 0; continue; }
    v = w; r = Math.sqrt(w2);
  }
  return !(n < 0);
}
const NPSI = 720, out = { rows: [], detail: {} };
function finsAt(n, p, x0, iter) {
  // radial extent R(psi): the largest rho (scanning inward from 2.2) at which the point is in the solid
  const R = new Float64Array(NPSI); let any = false;
  for (let i = 0; i < NPSI; i++) {
    const psi = 2 * PI * i / NPSI, cs = Math.cos(psi), sn = Math.sin(psi); let hit = 0;
    for (let rho = 2.2; rho > 0.004; rho -= 0.008) if (solid(n, p, [x0, rho * cs, rho * sn], iter)) { hit = rho; break; }
    R[i] = hit; if (hit) any = true;
  }
  if (!any) return null;
  let lo = Infinity, hi = 0; for (const r of R) { lo = Math.min(lo, r); hi = Math.max(hi, r); }
  // count separate humps: runs above the mid level (circular)
  const mid = (lo + hi) / 2; let humps = 0;
  for (let i = 0; i < NPSI; i++) if (R[i] > mid && !(R[(i + NPSI - 1) % NPSI] > mid)) humps++;
  // exact symmetry order: the smallest shift that leaves R unchanged (within one rho step)
  let order = 1;
  for (let s = 1; s <= NPSI / 2; s++) { if (NPSI % s) continue; let ok = true; for (let i = 0; i < NPSI && ok; i++) if (Math.abs(R[i] - R[(i + s) % NPSI]) > 0.0081) ok = false; if (ok) { order = NPSI / s; break; } }
  // where the humps point: angle of the first maximum
  let im = 0; for (let i = 0; i < NPSI; i++) if (R[i] > R[im]) im = i;
  return { humps: hi - lo < 0.03 ? 0 : humps, order, lo: +lo.toFixed(3), hi: +hi.toFixed(3), peakAt: +(360 * im / NPSI).toFixed(1) };
}

const rows = [];
for (const [n, p] of [[3, 1.5], [5, 2.5], [7, 3.5]]) { const res = [-0.2, 0.1, 0.4].map(x0 => finsAt(n, p, x0, 14)).filter(Boolean); rows.push(`n=${n} p=${p}: humps [${res.map(r => r.humps).join(',')}], exact repeat count [${res.map(r => r.order).join(',')}]`); }
// the lathe spin dial: does an even value typed into the state survive?
const spin = L.APPROACHES[1].params[0];
return { halfPlanes: rows, spinSpec: JSON.stringify(spin), planesSpec: JSON.stringify(L.APPROACHES[0].params[0]) };

const L = window.squaringLab;
const cpow = (x, y, n) => { const r = Math.hypot(x, y), a = Math.atan2(y, x) * n, R = Math.pow(r, n); return [R * Math.cos(a), R * Math.sin(a)]; };
const out = {};
for (const tilt of [0, 15, 40, 90, 137, 180, -60]) for (const n of [2, 3, 5, -1, -2, 2.5]) {
  let worst = 0, bad = 0, all = 0;
  for (let k = 0; k < 2000; k++) {
    const x = Math.sin(k * 12.9898) * 1.7, y = Math.cos(k * 78.233) * 1.7;
    const v = L.MATH.tilt([x, y, 0], n, { tilt }), w = cpow(x, y, n), s = Math.hypot(w[0], w[1]) || 1;
    const e = Math.hypot(v[0] - w[0], v[1] - w[1], v[2]) / s;
    worst = Math.max(worst, e); all++; if (e > 1e-9) bad++;
  }
  out[tilt + '/' + n] = worst.toExponential(1) + (bad ? ' (' + Math.round(100 * bad / all) + '% off)' : '');
}
// the twin: a tilt of 180 against the Lathe with z mirrored, off the plane
let tw = 0;
for (let k = 0; k < 2000; k++) {
  const v = [Math.sin(k * 1.1) * 1.3, Math.cos(k * 2.3) * 1.3, Math.sin(k * 3.7) * 1.3];
  const a = L.MATH.tilt(v, 2, { tilt: 180 }), b = L.MATH.lathe([v[0], v[1], -v[2]], 2, {});
  tw = Math.max(tw, Math.hypot(a[0] - b[0], a[1] - b[1], a[2] - b[2]));
}
// the written formula against the rule, off the plane, tilt 40
let fm = 0; const t = 40 * Math.PI / 180;
for (let k = 0; k < 2000; k++) {
  const [x, y, z] = [Math.sin(k * 1.1) * 1.3, Math.cos(k * 2.3) * 1.3, Math.sin(k * 3.7) * 1.3];
  const a = L.MATH.tilt([x, y, z], 2, { tilt: 40 });
  const b = [x * x - y * y - z * z * Math.cos(2 * t), 2 * x * y + z * z * Math.sin(2 * t), 2 * z * (x * Math.cos(t) - y * Math.sin(t))];
  fm = Math.max(fm, Math.hypot(a[0] - b[0], a[1] - b[1], a[2] - b[2]));
}
return JSON.stringify(out) + ' | twin at 180: ' + tw.toExponential(1) + ' | written formula: ' + fm.toExponential(1);

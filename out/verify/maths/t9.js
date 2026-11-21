// Point 9: MATH.mercator on z = 0 against complex z^n, and the derivation against the code.
const out = { parity: [], fails: [] };
const NS = [2, 3, 4, 5, 8, -1, -2, -3, 0.5, 2.5];
const pts = planePoints(11);
for (const planes of [1, 2, 3, 4, 8, 'default']) {
  const q = planes === 'default' ? L.S.param.mercator : { planes };
  for (const n of NS) {
    let worst = 0, worstZ = 0, at = null, bad = 0; const byKind = { generic: 0, origin: 0, negx: 0 };
    for (const [x, y, kind] of pts) {
      const got = M.mercator([x, y, 0], n, q), ref = cpow([x, y], n), m = Math.hypot(ref[0], ref[1]);
      const e = Math.hypot(got[0] - ref[0], got[1] - ref[1], got[2]) / m;
      if (!(e <= 1e-5)) bad++;
      if (!(e <= worst)) { worst = e; at = [x, y, kind]; }
      byKind[kind] = Math.max(byKind[kind], e); worstZ = Math.max(worstZ, Math.abs(got[2]) / m);
    }
    out.parity.push(`planes=${planes} n=${n}: worst rel err ${sci(worst)} (generic ${sci(byKind.generic)}, origin ${sci(byKind.origin)}, neg-x ${sci(byKind.negx)}), |z-part|/|ref| ${sci(worstZ)}, over 1e-5: ${bad}/${pts.length}`);
    if (bad) out.fails.push(`planes=${planes} n=${n}: ${bad} points over 1e-5, worst at ${JSON.stringify(at)} err ${sci(worst)}`);
  }
}
// where the cap for negative powers starts to bite (smallest |z| still within 1e-5)
out.cap = [];
for (const n of [-1, -2, -3, -8]) {
  let lo = null;
  for (let e = -1; e >= -25; e -= 0.25) { const r = Math.pow(10, e), got = M.mercator([r, 0, 0], n, { planes: 1 }), ref = Math.pow(r, n); if (Math.abs(got[0] - ref) / ref > 1e-5) { lo = r; break; } }
  out.cap.push(`n=${n}: first |z| where the rule departs from z^n: ${lo === null ? 'none down to 1e-25' : sci(lo)} (result there is capped at ${sci(M.mercator([lo || 1e-25, 0, 0], n, { planes: 1 })[0])})`);
}
// The identity quoted on the page, in the plane, with complex numbers only: z^n = 1 + n / sum_k w_k / (z - w_k)
out.identity = [];
const rnd = rng(5);
for (const n of [2, 3, 4, 5, 8]) {
  let worst = 0;
  for (let i = 0; i < 200; i++) {
    const z = [rnd() * 4 - 2, rnd() * 4 - 2]; let s = [0, 0];
    for (let k = 0; k < n; k++) { const w = [Math.cos(2 * PI * k / n), Math.sin(2 * PI * k / n)], t = cmul(w, cinv([z[0] - w[0], z[1] - w[1]])); s = [s[0] + t[0], s[1] + t[1]]; }
    const f = cinv(s), got = [1 + n * f[0], n * f[1]], ref = cpow(z, n);
    worst = Math.max(worst, Math.hypot(got[0] - ref[0], got[1] - ref[1]) / Math.max(1, Math.hypot(ref[0], ref[1])));
  }
  out.identity.push(`n=${n}: complex identity worst err ${sci(worst)}`);
}
// inversionPower (the literal sum of inversions) against MATH.mercator with one plane, anywhere in space
out.inversion = [];
for (const n of [2, 3, 4, 5, 8, -1, -2, -3, 1]) {
  let worst = 0, worstPlane = 0;
  for (let i = 0; i < 400; i++) {
    const r = 0.2 + 2 * rnd(), u = rnd() * 2 - 1, a = rnd() * 2 * PI, s = Math.sqrt(1 - u * u), v = [r * s * Math.cos(a), r * s * Math.sin(a), r * u];
    const A = L.inversionPower(v, n), B = M.mercator(v, n, { planes: 1 }), m = Math.hypot(...B);
    worst = Math.max(worst, Math.hypot(A[0] - B[0], A[1] - B[1], A[2] - B[2]) / m);
    const p = [r * Math.cos(a), r * Math.sin(a), 0], P = L.inversionPower(p, n), ref = cpow([p[0], p[1]], n);
    worstPlane = Math.max(worstPlane, Math.hypot(P[0] - ref[0], P[1] - ref[1], P[2]) / Math.hypot(ref[0], ref[1]));
  }
  out.inversion.push(`n=${n}: inversionPower vs MATH.mercator(1 plane) in space, worst rel err ${sci(worst)}; inversionPower on z=0 vs complex ${sci(worstPlane)}`);
}
// "it multiplies the longitude and the Mercator latitude by n"
let worstLon = 0, worstMerc = 0;
for (const n of [2, 3, 5, 8, -2, 2.5]) for (let i = 0; i < 300; i++) {
  const r = 0.3 + 2 * rnd(), u = (rnd() * 2 - 1) * 0.9, a = (rnd() * 2 - 1) * PI, s = Math.sqrt(1 - u * u), v = [r * s * Math.cos(a), r * s * Math.sin(a), r * u];
  const w = M.mercator(v, n, { planes: 1 }), R = Math.hypot(...w);
  let dl = Math.atan2(w[1], w[0]) - n * a; dl -= 2 * PI * Math.round(dl / (2 * PI));
  worstLon = Math.max(worstLon, Math.abs(dl));
  if (Math.abs(n * Math.atanh(u)) < 8) worstMerc = Math.max(worstMerc, Math.abs(Math.atanh(w[2] / R) - n * Math.atanh(u)));
  if (Math.abs(R / Math.pow(r, n) - 1) > 1e-9) out.fails.push('length is not |v|^n at ' + JSON.stringify(v));
}
out.mercator = `longitude out − n·longitude in: worst ${sci(worstLon)} rad; Mercator latitude out − n·Mercator latitude in: worst ${sci(worstMerc)}`;
// texts on the page
const A = L.APPROACHES.find(a => a.id === 'mercator');
out.texts = { name: A.name, tag: A.tag, about: A.about, formula: {} };
for (const n of [2, 3, 8, 1, 0, -1, -2, 2.5]) for (const p of [{ planes: 1, turn: 0, lift: 0 }, { planes: 2, turn: 0, lift: 0 }]) out.texts.formula[`n=${n},planes=${p.planes}`] = A.formula(p, n);
out.texts.formulaTurnLift = A.formula({ planes: 1, turn: 30, lift: 0.5 }, 2);
out.texts.notes = A.params.filter(s => s.type === 'note').map(s => s.text);
out.defaults = JSON.stringify(L.S.param);
return out;

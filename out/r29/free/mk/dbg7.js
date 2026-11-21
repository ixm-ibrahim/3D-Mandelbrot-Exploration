// debug: X7, where does the shader's distance leave the twin's?
$('ap-balls').click(); await settle();
S.k.brho = 0.5; S.k.bt = 0.5 * (100 / 300 + 1); S.k.bgrid = 0; S.k.bit = 16; S.flat = false; go(); await settle();
const side = 8.4, n = 160, z = 0;
const snap = L.takeSnapshot(), arr = await L.sampleSlice(snap, 0, 0, side, z, n); L.releaseSnapshot(snap);
const rows = [];
for (let j = 0; j < n; j++) for (let i = 0; i < n; i++) {
  const x = side * ((i + 0.5) / n - 0.5), y = side * ((j + 0.5) / n - 0.5), sh = arr[4 * (j * n + i) + 3], tw = L.ballsEstimate(x, y, z);
  if (sh > 0 && tw > 0) rows.push([Math.abs(sh - tw) / tw, x, y, sh, tw, L.ballsEstimate(x, y, z, { parts: true })]);
}
rows.sort((a, b) => b[0] - a[0]);
const pick = [0, 1, 2, 100, 1000, 5000, 10000, 20000].filter(k => k < rows.length).map(k => rows[k]);
return JSON.stringify({ sig: L.R.sig, n: rows.length, pick: pick.map(r => r.map(v => (Array.isArray(v) ? v.map(w => +w.toPrecision(5)) : +v.toPrecision(5)))) });

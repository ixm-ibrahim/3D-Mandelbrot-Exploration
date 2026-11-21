// debug: where does the shader's distance leave the twin's? A scan over the second sphere at size 300, and over the grid.
$('ap-balls').click(); await settle();
const out = [];
for (const [p, rho, g] of [[300, 0.49, 0], [300, 0.499, 0], [300, 0.5, 0], [300, 0.501, 0], [300, 0.51, 0], [300, 0.5, 2], [300, 0.5, 1], [250, 0.5, 0], [300, 0.4, 0], [400, 0.3, 0], [150, 0.75, 0]]) {
  S.k.brho = rho; S.k.bt = 0.5 * (100 / p + 1); S.k.bgrid = g; S.k.bit = 16; S.flat = false; go(); await settle();
  const side = 8.4, n = 120, z = 0;
  const snap = L.takeSnapshot(), arr = await L.sampleSlice(snap, 0, 0, side, z, n); L.releaseSnapshot(snap);
  let cnt = 0, far = 0, worst = 0, bigger = 0;
  for (let j = 0; j < n; j++) for (let i = 0; i < n; i++) {
    const x = side * ((i + 0.5) / n - 0.5), y = side * ((j + 0.5) / n - 0.5), sh = arr[4 * (j * n + i) + 3], tw = L.ballsEstimate(x, y, z);
    if (sh > 0 && tw > 0) { cnt++; const r = Math.abs(sh - tw) / tw; if (r > 0.01) { far++; if (sh > tw) bigger++; } if (r > worst) worst = r; }
  }
  out.push(`size ${p} second ${rho} grid ${g} program ${String(L.R.sig).split('\n')[0]}: ${cnt} points outside, more than 1 % apart ${far} (shader the larger: ${bigger}), worst ${worst.toFixed(3)}`);
}
return JSON.stringify(out, null, 1);

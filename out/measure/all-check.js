const L = window.squaringLab, T = L.T, S = L.S; const frame = () => new Promise(r => requestAnimationFrame(r));
const out = [];
for (const [i, n] of [[0, 2], [0, -2], [1, 3], [2, -1], [3, 8], [4, 0.5]]) {
  S.approach = i; S.n = n; const t0 = performance.now(); L.refresh(false); const call = performance.now() - t0;
  while (!T.cardIdle()) await frame();
  out.push(`${T.ap().name} n=${n}: refresh ${call.toFixed(1)} ms, ${T.cardRun.slices} slices, longest ${T.cardRun.longest.toFixed(1)} ms | ${document.getElementById('s-round').textContent} | ${document.getElementById('s-slice').textContent} | ${document.getElementById('cap3d').textContent}`);
}
out.push('drawStep3d registered ' + T.hooks.view.filter(f => f === T.drawStep3d).length + ' time(s); hooks.view has ' + T.hooks.view.length);
S.approach = 0; S.n = 2; L.syncControls(); L.refresh(false);
return out.join('\n');

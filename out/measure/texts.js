// Prints every sentence the scorecard and the captions can show, for a grid of approaches and powers.
const L = window.squaringLab, T = L.T, S = L.S;
const NS = [-8, -3, -2, -1, -0.5, 0, 0.5, 1, 2, 2.5, 3, 8];
const out = ['=== IN THE PLANE ==='];
for (const n of NS) {
  const p = T.cardPlane(n);
  out.push(`--- n = ${n}`, ...Object.entries(p).map(([k, v]) => `  ${k}: ${v}`), `  caption: ${T.stepCaption2d(n)}`);
}
const bad = [];
for (const a of T.APPROACHES) {
  out.push(`=== ${a.name} ===`);
  const variants = window.VARIANTS && window.VARIANTS[a.id] ? window.VARIANTS[a.id] : [{}];
  for (const v of variants) for (const n of NS) {
    const q = { ...T.specDefaults(a.params || []), ...v }, m = L.measure(x => T.MATH[a.id](x, n, q), n), c = T.cardSpace(a, q, n, m);
    out.push(`--- n = ${n} ${JSON.stringify(q)}  [used ${m.used}, round ${m.round.toFixed(3)}, rev ${m.rev.toFixed(3)}, deg ${m.deg.toFixed(2)}, sheets ${m.sheets.toFixed(2)}, stretch ${m.smin.toFixed(3)}..${m.smax.toFixed(3)} (8th smallest ${m.smin8.toFixed(3)}, 8th largest ${m.smax8.toFixed(3)}), len ${m.lmin.toFixed(3)}..${m.lmax.toFixed(3)}, plane ${m.plane}, copy ${m.copy}, turn ${m.turn}]`);
    for (const [k, [st, text]] of Object.entries(c)) { out.push(`  ${k}: [${st}] ${text}`); if (/NaN|undefined|Infinity|null/.test(text)) bad.push(`${a.id} n=${n} ${k}: ${text}`); }
    out.push(`  crush: [${a.crush(q, n)[0]}] ${a.crush(q, n)[1]}`, `  smooth: [${a.smooth(q, n)[0]}] ${a.smooth(q, n)[1]}`);
  }
}
out.push('=== BAD TEXTS: ' + bad.length + ' ===', ...bad);
return out.join('\n');

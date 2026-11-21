//#
const L = window.squaringLab, c = window.newCount; L.cam.target = [0, 0, 0]; L.cam.dist = 6;
const out = [];
L.S.n = 3; out.push(c('live approaches, n = 3, plain', { shadow: false, ao: false }));
L.S.n = -2; out.push(c('live approaches, n = -2, plain', { analytic: false, shadow: false, ao: false }));
L.S.n = -2; out.push(c('live approaches, n = -2, all on', { analytic: false }));
return out;
//#
const L = window.squaringLab, G = L.GLSL(), out = [];
window.bandRows = 120;
for (const n of [3, -2]) { L.S.n = n; const P = window.progOf(G); window.drawOnce(P, { analytic: false }); out.push('n = ' + n + ': ' + [0, 1, 2].map(() => window.drawOnce(P, { analytic: false }).toFixed(0)).join('/') + ' ms per pass (wall clock)'); }
return out;

//#
window.bandRows = 120; const nd = window.newDraw, out = [];
for (const nt of [3, 1, 0]) out.push(nd('default, all on, nt=' + nt, { nt, analytic: nt === 3 }));
for (const nt of [3, 1, 0]) out.push(nd('default, no shadow/crevices, nt=' + nt, { nt, analytic: nt === 3, shadow: false, ao: false }));
return out;
//#
const L = window.squaringLab; L.S.approach = 3; L.S.n = 8; L.S.iter = 10; L.cam.target = [0, 0, 0]; L.cam.dist = 4.2;
const nd = window.newDraw, out = [];
for (const nt of [3, 1, 0]) out.push(nd('classic n=8, all on, nt=' + nt, { nt, analytic: nt === 3 }));
for (const nt of [3, 1, 0]) out.push(nd('classic n=8, no shadow/crevices, nt=' + nt, { nt, analytic: nt === 3, shadow: false, ao: false }));
return out;

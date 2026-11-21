//#
window.bandRows = 120;
const L = window.squaringLab, G = L.GLSL();
// time several shader versions on the scene in S
window.many = (label, o) => {
  const sets = { old: G.OLD, v2: G.V2, now: G }, out = [];
  for (const k in sets) { if (!sets[k]) continue; const P = window.progOf(sets[k]); window.drawOnce(P, o); out.push(k + ' ' + Math.min(window.drawOnce(P, o), window.drawOnce(P, o), window.drawOnce(P, o)).toFixed(0)); }
  return label + ': ' + out.join(' | ');
};
return window.many('default, all on') + '\n' + window.many('default, no shadow/crevices', { shadow: false, ao: false });
//#
const L = window.squaringLab; L.S.approach = 3; L.S.n = 8; L.S.iter = 10; L.cam.target = [0, 0, 0]; L.cam.dist = 4.2;
return window.many('classic n=8, all on') + '\n' + window.many('classic, no shadow/crevices', { shadow: false, ao: false });
//#
const L = window.squaringLab; L.S.approach = 1; L.S.n = 2; L.S.iter = 14; L.S.param.lathe.spin = 3;
return window.many('lathe spin 3, all on');

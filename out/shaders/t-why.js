//#
// Which half of the new shader costs drawing time: the orbit code or main()? Cross the old and new halves.
window.bandRows = 120;
const L = window.squaringLab, G = L.GLSL(), O = G.OLD, gl = L.gl();
const sub = (s, a, b) => { if (!s.includes(a)) throw new Error('missing: ' + a); return s.split(a).join(b); };
const sets = {
  old: O,
  now: G,
  // old orbit code under the new main(): give it the new call signature
  'old orbit, new main': { GL_HEAD: G.GL_HEAD, GL_KLEIN: G.GL_KLEIN, GL_TAIL: G.GL_TAIL,
    GL_ORBIT: '\nconst bool ORBIT_SCENE = false; mat3 gB;' + sub(O.GL_ORBIT, 'float de(vec3 p, int nt){', 'float deOld(vec3 p, int nt){') +
      '\nfloat de(vec3 p, int nt, vec3 dir){ gB = mat3(1.0); if (nt == 1) gB[0] = dir; return deOld(p, nt); }' },
  // new orbit code under the old main(): give it the old call signature
  'new orbit, old main': { GL_HEAD: G.GL_HEAD, GL_KLEIN: G.GL_KLEIN, GL_ORBIT: G.GL_ORBIT,
    GL_TAIL: '\nmat3 gB; const float BOUND = 8.0;\nfloat deN(vec3 p, int nt){ gAsk = ASK_PLAIN; return de(p, nt, gB[0]); }' +
      sub(sub(O.GL_TAIL, 'float d = de(p, nt), pl', 'float d = deN(p, nt), pl'), 'nor += k * de(p + k * hh, uNT);', 'nor += k * deN(p + k * hh, uNT);') },
};
window.why = (label, o) => {
  const progs = {}, best = {};
  for (const k in sets) progs[k] = window.progOf(sets[k]);
  for (const k in progs) window.drawOnce(progs[k], o);
  for (let r = 0; r < 4; r++) for (const k in progs) best[k] = Math.min(best[k] || 1e9, window.drawOnce(progs[k], o));
  return label + ': ' + Object.keys(best).map(k => k + ' ' + best[k].toFixed(0)).join(' | ');
};
return window.why('default, all on') + '\n' + window.why('default, no shadow/crevices', { shadow: false, ao: false });
//#
const L = window.squaringLab; L.S.approach = 3; L.S.n = 8; L.S.iter = 10; L.cam.target = [0, 0, 0]; L.cam.dist = 4.2;
return window.why('classic n=8, all on') + '\n' + window.why('classic, no shadow/crevices', { shadow: false, ao: false });

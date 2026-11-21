//# wait=done timeout=300
const L = window.squaringLab; L.S.q.aa = 1; L.touch();
// Link the old and the new scene shader in turn, in one session, so machine load affects both alike.
const gl = L.gl(), G = L.GLSL();
let uid = 0;
const link = src => {
  const mk = (t, s) => { const sh = gl.createShader(t); gl.shaderSource(sh, s); gl.compileShader(sh); return sh; };
  const p = gl.createProgram(), t0 = performance.now();
  gl.attachShader(p, mk(gl.VERTEX_SHADER, G.VERT));
  gl.attachShader(p, mk(gl.FRAGMENT_SHADER, src + '\n// ' + (++uid) + ' ' + Math.random()));
  gl.linkProgram(p);
  const ok = gl.getProgramParameter(p, gl.LINK_STATUS), ms = performance.now() - t0;
  if (!ok) throw new Error(gl.getProgramInfoLog(p));
  gl.deleteProgram(p);
  return ms;
};
const src = (P, ap, eq, z0, n) => {
  const n2 = Math.abs(n - 2) < 1e-9, fc = L.compileFormula(eq, true, n2), zc = L.compileFormula(z0, false, n2);
  return P.GL_HEAD + G.GL_COLOUR + L.APPROACHES[ap].glsl + P.GL_ORBIT.replace('__F__', fc).replace('__Z0__', zc) + P.GL_TAIL;
};
const fmt = a => a.map(x => x.toFixed(0)).join('/');
window.ab = (ap, eq, z0, n) => {
  const a = [], b = [];
  for (let k = 0; k < 2; k++) { a.push(link(src(G.OLD, ap, eq, z0, n))); b.push(link(src(G, ap, eq, z0, n))); }
  return L.APPROACHES[ap].id + ' ' + eq + ' n=' + n + ': old ' + fmt(a) + ' ms, new ' + fmt(b) + ' ms';
};
window.abK = () => {
  const a = [], b = [];
  for (let k = 0; k < 2; k++) { a.push(link(G.OLD.GL_HEAD + G.GL_COLOUR + G.OLD.GL_KLEIN + G.OLD.GL_TAIL)); b.push(link(G.GL_HEAD + G.GL_COLOUR + G.GL_KLEIN + G.GL_TAIL)); }
  return 'klein: old ' + fmt(a) + ' ms, new ' + fmt(b) + ' ms';
};
return 'start';
//#
return window.ab(1, 'z^n + c', '0', 2);
//#
return window.ab(3, 'z^n + c', '0', 8);
//#
return window.ab(0, 'z^n + c', '0', 2);
//#
return window.ab(0, 'z^n + c', '0', 3);
//#
return window.ab(0, 'c*z*(1 - z)', '0.5', 2);
//#
return window.ab(0, 'z^n + c/z', '1', 2);
//#
return window.abK();

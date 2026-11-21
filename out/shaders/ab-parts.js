//# wait=done timeout=300
const L = window.squaringLab; L.S.q.aa = 1; L.touch();
const gl = L.gl(), G = L.GLSL();
let uid = 0;
const link = src => {
  const mk = (t, s) => { const sh = gl.createShader(t); gl.shaderSource(sh, s); gl.compileShader(sh); if (!gl.getShaderParameter(sh, gl.COMPILE_STATUS)) throw new Error(gl.getShaderInfoLog(sh)); return sh; };
  const p = gl.createProgram(), t0 = performance.now();
  gl.attachShader(p, mk(gl.VERTEX_SHADER, G.VERT));
  gl.attachShader(p, mk(gl.FRAGMENT_SHADER, src + '\n// ' + (++uid) + ' ' + Math.random()));
  gl.linkProgram(p);
  const ok = gl.getProgramParameter(p, gl.LINK_STATUS), ms = performance.now() - t0;
  if (!ok) throw new Error(gl.getProgramInfoLog(p));
  gl.deleteProgram(p);
  return ms;
};
const fill = (orbit, eq, z0, n) => { const n2 = Math.abs(n - 2) < 1e-9; return orbit.replace('__F__', L.compileFormula(eq, true, n2)).replace('__Z0__', L.compileFormula(z0, false, n2)); };
const MINI = '\nvoid main(){ gB = mat3(1.0); float d = de(vec3(gl_FragCoord.xy, uCut), uNT); o = vec4(d, gEsc, gIt, gGrad.x + gLast.x); }';
window.parts = (ap, eq, z0, n, edit) => {
  const A = L.APPROACHES[ap].glsl, O = G.OLD;
  let NO = G.GL_ORBIT, NT = G.GL_TAIL;
  if (edit) [NO, NT] = edit(NO, NT);
  const v = {
    old: O.GL_HEAD + G.GL_COLOUR + A + fill(O.GL_ORBIT, eq, z0, n) + O.GL_TAIL,
    new: G.GL_HEAD + G.GL_COLOUR + A + fill(NO, eq, z0, n) + NT,
    'new orbit, one call': G.GL_HEAD + G.GL_COLOUR + A + fill(NO, eq, z0, n) + MINI,
    'old orbit, one call': O.GL_HEAD + G.GL_COLOUR + A + fill(O.GL_ORBIT, eq, z0, n) + MINI,
    'old orbit, new tail': G.GL_HEAD + G.GL_COLOUR + A + 'const bool ORBIT_SCENE = false;' + fill(O.GL_ORBIT, eq, z0, n) + NT,
  };
  const out = [];
  for (const k in v) { const a = link(v[k]), b = link(v[k]); out.push(k + ': ' + Math.min(a, b).toFixed(0)); }
  return L.APPROACHES[ap].id + ' ' + eq + ' n=' + n + ' -> ' + out.join(' | ');
};
return 'start';
//#
return window.parts(1, 'z^n + c', '0', 2);
//#
return window.parts(0, 'c*z*(1 - z)', '0.5', 2);

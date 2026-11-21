//# wait=done timeout=300
// Shared helpers for the compile-time tests: window.T.link(src) links a scene shader and returns the milliseconds.
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
const sub = (s, a, b) => { if (!s.includes(a)) throw new Error('missing: ' + a); return s.replace(a, b); };
// time a table of { label: source } and report the faster of two links each
const table = v => Object.keys(v).map(k => k + ': ' + Math.min(link(v[k]), link(v[k])).toFixed(0)).join(' | ');
window.T = { L, gl, G, link, fill, sub, table };
return 'ready';

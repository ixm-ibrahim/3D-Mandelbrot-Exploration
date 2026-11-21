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
const sub = (s, a, b) => { if (!s.includes(a)) throw new Error('missing: ' + a); return s.replace(a, b); };
const E = {
  full: o => o,
  'no inside-out block': o => sub(o, 'if (insideOut && r <= uBail && r > 0.0){', 'if (false){'),
  'no mosaic': o => sub(sub(o, 'passes = mosaic ? 2 : 1', 'passes = 1'), 'mosaic = uMosaic > 0.0 && !jul && !gProbing;', 'mosaic = false;'),
  'no pole redo': o => sub(o, 'if (k == 0 && r < 1e-3 && (wild ||', 'if (false && (wild ||'),
  'no probe test': o => sub(o, 'if (gProbing && !wild && r > 1e-3){', 'if (false){'),
};
E['none of them'] = o => E['no probe test'](E['no pole redo'](E['no mosaic'](E['no inside-out block'](o))));
window.parts = (ap, eq, z0, n) => {
  const A = L.APPROACHES[ap].glsl, out = [];
  for (const k in E) {
    const s = G.GL_HEAD + G.GL_COLOUR + A + fill(E[k](G.GL_ORBIT), eq, z0, n) + G.GL_TAIL;
    out.push(k + ': ' + Math.min(link(s), link(s)).toFixed(0));
  }
  return L.APPROACHES[ap].id + ' ' + eq + ' n=' + n + ' -> ' + out.join(' | ');
};
return 'start';
//#
return window.parts(1, 'z^n + c', '0', 2);

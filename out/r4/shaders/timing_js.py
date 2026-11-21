T = r"""
const draw = async () => { const t0 = performance.now(); L.touch(); await new Promise(r => { const f = () => L.idle() ? r() : setTimeout(f, 3); setTimeout(f, 40); }); return performance.now() - t0; };
const least = async n => { let m = 1e9; for (let i = 0; i < n; i++) m = Math.min(m, await draw()); return Math.round(m); };
const compile = () => { let m = 1e9; for (let i = 0; i < 3; i++){ const c = document.createElement('canvas'), g = c.getContext('webgl2'); const src = L.R.want.src() + '\n// ' + Math.random() + '\nconst float uniq' + Math.floor(Math.random() * 1e9) + ' = ' + Math.random().toFixed(6) + ';\n';
  const vs = g.createShader(g.VERTEX_SHADER), fs = g.createShader(g.FRAGMENT_SHADER), p = g.createProgram();
  g.shaderSource(vs, '#version 300 es\nvoid main(){ vec2 p = vec2(float((gl_VertexID << 1) & 2), float(gl_VertexID & 2)); gl_Position = vec4(p * 2.0 - 1.0, 0.0, 1.0); }'); g.shaderSource(fs, src);
  const t0 = performance.now(); g.compileShader(vs); g.compileShader(fs); g.attachShader(p, vs); g.attachShader(p, fs); g.linkProgram(p);
  const ok = g.getProgramParameter(p, g.LINK_STATUS); const dt = performance.now() - t0; if (!ok) return 'FAILED ' + g.getShaderInfoLog(fs); m = Math.min(m, dt); const x = g.getExtension('WEBGL_lose_context'); if (x) x.loseContext(); }
  return Math.round(m); };
"""

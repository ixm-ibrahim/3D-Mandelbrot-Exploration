// Checker of round 12: each entry's shader code (pw, sqr, cmap) run on the GPU at 4096 points, against MATH.
const L = window.squaringLab, M = L.MATH, AP = L.APPROACHES, PI = Math.PI;
const W = 1024, H = 4, N = W * H;
const cv = document.createElement('canvas'); cv.width = W; cv.height = H;
const gl = cv.getContext('webgl2');
if (!gl) return JSON.stringify({ error: 'no webgl2' });
if (!gl.getExtension('EXT_color_buffer_float')) return JSON.stringify({ error: 'no float colour buffer' });
let seed = 1357911;
const rnd = () => { seed = (Math.imul(seed, 1664525) + 1013904223) >>> 0; return seed / 4294967296; };
const f32 = Math.fround;
const pts = new Float32Array(N * 4);
for (let i = 0; i < N; i++) {
  let v; do { v = [rnd() * 2 - 1, rnd() * 2 - 1, rnd() * 2 - 1]; } while (Math.hypot(...v) > 1 || Math.hypot(...v) < 0.1);
  const s = (0.08 + 1.9 * rnd()) / Math.hypot(...v); v = v.map(c => c * s);
  if (i >= 3072 && i < 3584) v[2] = 0;          // 512 points of the plane z = 0
  if (i >= 3584 && i < 3840) v[1] = 0;          // 256 points of the plane y = 0
  pts.set([v[0], v[1], v[2], 1], i * 4);        // the rest: 3072 points in general position, and 256 more at the end
}
const tex = gl.createTexture(); gl.bindTexture(gl.TEXTURE_2D, tex);
gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA32F, W, H, 0, gl.RGBA, gl.FLOAT, pts);
gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.NEAREST); gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.NEAREST);
const outT = gl.createTexture(); gl.bindTexture(gl.TEXTURE_2D, outT); gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA32F, W, H, 0, gl.RGBA, gl.FLOAT, null);
gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.NEAREST); gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.NEAREST);
const fbo = gl.createFramebuffer(); gl.bindFramebuffer(gl.FRAMEBUFFER, fbo); gl.framebufferTexture2D(gl.FRAMEBUFFER, gl.COLOR_ATTACHMENT0, gl.TEXTURE_2D, outT, 0);
if (gl.checkFramebufferStatus(gl.FRAMEBUFFER) !== gl.FRAMEBUFFER_COMPLETE) return JSON.stringify({ error: 'framebuffer not complete' });
const VS = '#version 300 es\nvoid main(){ vec2 p = vec2(gl_VertexID == 1 ? 3.0 : -1.0, gl_VertexID == 2 ? 3.0 : -1.0); gl_Position = vec4(p, 0.0, 1.0); }';
const head = '#version 300 es\nprecision highp float; precision highp int;\nuniform vec4 uA; uniform float uN; uniform int uWhat; uniform sampler2D uPts;\nconst float PI = 3.14159265358979;\nvec2 cmul(vec2 a, vec2 b){ return vec2(a.x * b.x - a.y * b.y, a.x * b.y + a.y * b.x); }\nfloat at2(float y, float x){ return abs(x) + abs(y) > 0.0 ? atan(y, x) : 0.0; }\n';
const tail = '\nout vec4 o;\nvoid main(){ vec3 v = texelFetch(uPts, ivec2(gl_FragCoord.xy), 0).xyz; vec3 r = uWhat == 0 ? pw(v, uN) : uWhat == 1 ? sqr(v) : cmap(v); o = vec4(r, 1.0); }';
const build = glsl => { const mk = (t, s) => { const sh = gl.createShader(t); gl.shaderSource(sh, s); gl.compileShader(sh); if (!gl.getShaderParameter(sh, gl.COMPILE_STATUS)) throw new Error(gl.getShaderInfoLog(sh)); return sh; }; const p = gl.createProgram(); gl.attachShader(p, mk(gl.VERTEX_SHADER, VS)); gl.attachShader(p, mk(gl.FRAGMENT_SHADER, head + glsl + tail)); gl.linkProgram(p); if (!gl.getProgramParameter(p, gl.LINK_STATUS)) throw new Error(gl.getProgramInfoLog(p)); return p; };
const res = new Float32Array(N * 4);
const run = (prog, uA, n, what) => { gl.useProgram(prog); gl.uniform4f(gl.getUniformLocation(prog, 'uA'), uA[0], uA[1], uA[2], uA[3]); gl.uniform1f(gl.getUniformLocation(prog, 'uN'), n); gl.uniform1i(gl.getUniformLocation(prog, 'uWhat'), what); gl.activeTexture(gl.TEXTURE0); gl.bindTexture(gl.TEXTURE_2D, tex); gl.uniform1i(gl.getUniformLocation(prog, 'uPts'), 0); gl.viewport(0, 0, W, H); gl.drawArrays(gl.TRIANGLES, 0, 3); gl.readPixels(0, 0, W, H, gl.RGBA, gl.FLOAT, res); };
const foldk = (v, k) => { const [x, y, z] = v, rho = Math.hypot(y, z); if (rho < 1e-300) return v; const w = PI / k, psi = Math.atan2(z, y), s = psi < 0 ? -1 : 1, a = Math.abs(psi), j = Math.floor(a / w + 0.5), d = a - j * w; let a2; if (2 * j < k || (2 * j === k && d < 0)) a2 = j % 2 === 0 ? d : -d; else a2 = PI + ((k - j) % 2 === 0 ? d : -d); a2 *= s; return [x, rho * Math.cos(a2), rho * Math.sin(a2)]; };
const CASES = {
  mercator: { sets: [{ turn: 0, lift: 0 }, { turn: 30, lift: 0.2 }], pows: [2, 3, -1] },
  lathe: { sets: [{ spin: 1 }, { spin: 3 }], pows: [2, 3, -1] },
  fold: { sets: [{ planes: 2, lift: 0 }, { planes: 3, lift: 0 }, { planes: 5, lift: 0.3 }], pows: [2, 3, -1, 2.5] },
  tilt: { sets: [{ tilt: 40 }, { tilt: 90 }, { tilt: 137 }, { tilt: -60 }, { tilt: 180 }, { tilt: 0 }], pows: [2, 3, 5, -1, -2, 2.5] },
  softfold: { sets: [{ planes: 2, blend: 0.25, curve: 0, mix: 0 }, { planes: 3, blend: 0.25, curve: 0, mix: 0 }, { planes: 2, blend: 0.1, curve: 1, mix: 1 }, { planes: 2, blend: 0.25, curve: 0, mix: 2 }, { planes: 4, blend: 0.4, curve: 0, mix: 2 }, { planes: 4, blend: 0, curve: 1, mix: 0 }], pows: [2, 3, -1, -2, 5] },
  axisbulb: { sets: [{ k: 1, wob: 0.2, reach: 45, pinch: 0 }, { k: 5, wob: 0.2, reach: 45, pinch: 0 }, { k: -3, wob: 0.5, reach: 30, pinch: 1.5 }, { k: 2, wob: 0, reach: 45, pinch: 0.5 }, { k: 9, wob: 1, reach: 0, pinch: 0 }], pows: [2, 3, -1, 5] },
  pillow: { sets: [{ layout: 0 }, { layout: 1 }], pows: [2, 3, 4, 8, -1, -2, 5] },
};
const out = {};
for (const id of Object.keys(CASES)) {
  const ap = AP.find(a => a.id === id), keys = (ap.params || []).filter(s => s.key !== undefined).map(s => s.key);
  let prog; try { prog = build(ap.glsl); } catch (e) { out[id] = 'DOES NOT COMPILE: ' + String(e).slice(0, 300); continue; }
  const rows = {};
  for (const q of CASES[id].sets) {
    const uA = [0, 0, 0, 0]; keys.forEach((k, i) => { if (i < 4) uA[i] = +q[k]; });
    const todo = CASES[id].pows.map(n => ['pw', n]).concat([['sqr', 2], ['cmap', 0]]);
    for (const [what, n] of todo) {
      if (id === 'pillow' && q.layout === 1 && ![2, 4, 8].includes(n) && what === 'pw') continue;
      run(prog, uA, n, what === 'pw' ? 0 : what === 'sqr' ? 1 : 2);
      let worst = 0, over = 0, worstAt = null, nan = 0, wz0 = 0, overz0 = 0, zleak = 0, wy0 = 0, overy0 = 0, gen = 0;
      for (let i = 0; i < N; i++) {
        const v = [pts[i * 4], pts[i * 4 + 1], pts[i * 4 + 2]], g = [res[i * 4], res[i * 4 + 1], res[i * 4 + 2]];
        const j = what === 'cmap' ? (id === 'fold' ? foldk(v, Math.max(2, q.planes)) : v) : M[id](v, n, q);
        if (!(isFinite(g[0]) && isFinite(g[1]) && isFinite(g[2]))) { nan++; continue; }
        const e = Math.hypot(g[0] - j[0], g[1] - j[1], g[2] - j[2]) / (1 + Math.hypot(...j));
        const onZ = i >= 3072 && i < 3584, onY = i >= 3584 && i < 3840;
        if (onZ) { wz0 = Math.max(wz0, e); if (e > 2e-3) overz0++; zleak = Math.max(zleak, Math.abs(g[2])); }
        else if (onY) { wy0 = Math.max(wy0, e); if (e > 2e-3) overy0++; }
        else { gen++; if (e > worst) { worst = e; worstAt = v.map(c => +c.toFixed(4)); } if (e > 2e-3) over++; }
      }
      const tag = JSON.stringify(q) + ' ' + what + (what === 'pw' ? ' n=' + n : '');
      rows[tag] = 'general ' + worst.toExponential(1) + ' (' + over + ' of ' + gen + ' over 2e-3' + (over ? ', worst at ' + JSON.stringify(worstAt) : '') + '); z=0 ' + wz0.toExponential(1) + ' (' + overz0 + ' over), leaves plane by ' + zleak.toExponential(1) + '; y=0 ' + wy0.toExponential(1) + ' (' + overy0 + ' of 256 over)' + (nan ? '; NOT FINITE ' + nan : '');
    }
  }
  out[id] = rows;
}
return JSON.stringify(out);

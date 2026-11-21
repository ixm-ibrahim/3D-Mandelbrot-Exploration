// Round 16, entry: the shader beside the half-plane z = 0, y < 0 (where atan2 jumps from 180 to -180 degrees).
const L = window.squaringLab, M = L.MATH, AP = L.APPROACHES;
const f32 = v => Array.from(new Float32Array(v));
const cv = document.createElement('canvas'); cv.width = 64; cv.height = 1;
const gl = cv.getContext('webgl2'); gl.getExtension('EXT_color_buffer_float');
const tex = gl.createTexture(); gl.bindTexture(gl.TEXTURE_2D, tex);
gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA32F, 64, 1, 0, gl.RGBA, gl.FLOAT, null);
gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.NEAREST); gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.NEAREST);
const fbo = gl.createFramebuffer(); gl.bindFramebuffer(gl.FRAMEBUFFER, fbo);
gl.framebufferTexture2D(gl.FRAMEBUFFER, gl.COLOR_ATTACHMENT0, gl.TEXTURE_2D, tex, 0); gl.viewport(0, 0, 64, 1);
const VERT = '#version 300 es\nvoid main(){ vec2 p = vec2(float((gl_VertexID << 1) & 2), float(gl_VertexID & 2)); gl_Position = vec4(p * 2.0 - 1.0, 0.0, 1.0); }';
const HEAD = '#version 300 es\nprecision highp float;\nprecision highp int;\nuniform vec4 uA; uniform float uPow, uJulia; uniform vec3 uC;\nout vec4 o;\nconst float PI = 3.14159265358979;\n' +
  'vec2 cmul(vec2 a, vec2 b){ return vec2(a.x * b.x - a.y * b.y, a.x * b.y + a.y * b.x); }\nfloat at2(float y, float x){ return abs(x) + abs(y) > 0.0 ? atan(y, x) : 0.0; }\n';
const MAIN = '\nuniform vec3 uP[64]; uniform int uOp;\nvoid main(){ int i = int(gl_FragCoord.x); vec3 v = uP[i];\n if (uOp == 1) o = vec4(sqr(v), 1.0); else { float phi = atan(v.z, v.y); o = vec4(phi, sin(4.0 * phi), phi - sin(4.0 * phi) / 4.0, 1.0); } }';
const sh = (type, src) => { const s = gl.createShader(type); gl.shaderSource(s, src); gl.compileShader(s); if (!gl.getShaderParameter(s, gl.COMPILE_STATUS)) throw new Error('shader: ' + gl.getShaderInfoLog(s)); return s; };
const run = (id, op, A) => {
  const a = AP.find(x => x.id === id), p = gl.createProgram(); gl.attachShader(p, sh(gl.VERTEX_SHADER, VERT)); gl.attachShader(p, sh(gl.FRAGMENT_SHADER, HEAD + a.glsl + MAIN)); gl.linkProgram(p);
  gl.useProgram(p); const U = n => gl.getUniformLocation(p, n);
  gl.uniform4fv(U('uA'), [0, 0, 0, 0]); gl.uniform1i(U('uOp'), op);
  const f = new Float32Array(192); A.forEach((v, i) => f.set(v, 3 * i)); gl.uniform3fv(U('uP[0]'), f); gl.drawArrays(gl.TRIANGLES, 0, 3);
  const r = new Float32Array(256); gl.readPixels(0, 0, 64, 1, gl.RGBA, gl.FLOAT, r);
  return A.map((_, i) => [r[4 * i], r[4 * i + 1], r[4 * i + 2]]);
};
const out = [];
for (const y of [-0.05, 0.05]) for (const sg of [1, -1]) {
  const A = [1e-7, 1e-6, 1e-5, 1e-4, 1e-3, 1e-2, 0.03].map(e => f32([-0.6, y, sg * e]));
  const ang = run('turnalong', 0, A);
  for (const id of ['turnalong', 'turnaway']) {
    const g = run(id, 1, A);
    A.forEach((v, i) => { const w = M[id](v, 2, {}), phi = Math.atan2(v[2], v[1]);
      out.push(`${id} y ${y} z ${v[2].toExponential(1)}: |shader - MATH| ${Math.hypot(g[i][0] - w[0], g[i][1] - w[1], g[i][2] - w[2]).toExponential(2)}` + (id === 'turnalong' ? `  atan off ${(ang[i][0] - phi).toExponential(2)}  sin(4phi) off ${(ang[i][1] - Math.sin(4 * phi)).toExponential(2)}  psi off ${(ang[i][2] - (phi - Math.sin(4 * phi) / 4)).toExponential(2)}` : '')); });
  }
}
return out.join('\n');

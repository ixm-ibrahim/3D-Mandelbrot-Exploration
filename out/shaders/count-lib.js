//# wait=done timeout=300
// Count the work a picture takes, independent of how busy the machine is: every evaluation of the formula
// bumps a counter, the shader writes the counter out as a colour, and the page adds the pixels up.
const L = window.squaringLab; L.S.q.aa = 1; L.touch();
const gl = L.gl(), G = L.GLSL();
const sub = (s, a, b) => { if (!s.includes(a)) throw new Error('missing: ' + a); return s.split(a).join(b); };
const fill = (orbit, eq, z0, n) => { const n2 = Math.abs(n - 2) < 1e-9; return orbit.split('__F__').join(L.compileFormula(eq, true, n2)).split('__Z0__').join(L.compileFormula(z0, false, n2)); };
// counted versions: the formula call sites add to gCount, and the last line of main() writes it out
const counted = P => {
  let o = P.GL_ORBIT, t = P.GL_TAIL;
  if (o.includes('vec3 wi = f(v + dz, c + dk);')) o = sub(o, 'vec3 wi = f(v + dz, c + dk);', 'gCount += 1.0; vec3 wi = f(v + dz, c + dk);');
  else o = sub(sub(o, 'vec3 w = f(v, c);', 'gCount += 1.0; vec3 w = f(v, c);'), 'vec3 d = f(v + dv[i], c + dc[i]) - w;', 'gCount += 1.0; vec3 d = f(v + dv[i], c + dc[i]) - w;');
  const i = t.lastIndexOf('o = vec4(col, 1.0);');
  t = t.slice(0, i) + 'o = vec4(fract(gCount / 256.0), floor(gCount / 256.0) / 255.0, lumaOf(col), 1.0);' + t.slice(i + 'o = vec4(col, 1.0);'.length);
  return { GL_HEAD: P.GL_HEAD + '\nfloat gCount = 0.0; float lumaOf(vec3 c){ return dot(c, vec3(0.3, 0.6, 0.1)) > 0.02 ? 1.0 : 0.0; }\n', GL_ORBIT: o, GL_KLEIN: P.GL_KLEIN, GL_TAIL: t };
};
const cache = new Map();
window.countWork = (P, o) => {
  const C = counted(P);
  const src = C.GL_HEAD + G.GL_COLOUR + L.APPROACHES[L.S.approach].glsl + fill(C.GL_ORBIT, L.S.eq, L.S.z0, L.S.n) + C.GL_TAIL;
  if (!cache.has(src)) cache.set(src, L.makeProgram(src));
  const prog = cache.get(src), W = gl.canvas.width, H = gl.canvas.height, rows = 60, px = new Uint8Array(W * rows * 4);
  let total = 0, lit = 0;
  gl.bindFramebuffer(gl.FRAMEBUFFER, null); gl.viewport(0, 0, W, H); gl.disable(gl.BLEND); gl.enable(gl.SCISSOR_TEST);
  for (let y = 0; y < H; y += rows) {
    const h = Math.min(rows, H - y);
    gl.scissor(0, y, W, h);
    L.setScene(prog, Object.assign({ w: W, h: H, off: [0, 0], px: 1, nt: 3, steps: L.S.q.steps, normEps: 1, ao: true, shadow: true, analytic: true }, o));
    gl.drawArrays(gl.TRIANGLES, 0, 3);
    gl.readPixels(0, y, W, h, gl.RGBA, gl.UNSIGNED_BYTE, px);
    for (let i = 0; i < W * h * 4; i += 4) { total += px[i] + 256 * px[i + 1]; if (px[i + 2] > 128) lit++; }
  }
  gl.disable(gl.SCISSOR_TEST);
  return { perPixel: total / (W * H), lit: lit / (W * H) };
};
// formula evaluations per pixel, old against new, and the share of pixels that are not background
window.abCount = (label, o) => {
  const a = window.countWork(G.OLD, o), b = window.countWork(G, o);
  return label + ': old ' + a.perPixel.toFixed(0) + ' evaluations per pixel (' + (100 * a.lit).toFixed(1) + '% lit), new ' + b.perPixel.toFixed(0) + ' (' + (100 * b.lit).toFixed(1) + '% lit), ratio ' + (b.perPixel / a.perPixel).toFixed(2);
};
window.newCount = (label, o) => { const b = window.countWork(G, o); return label + ': ' + b.perPixel.toFixed(0) + ' evaluations per pixel (' + (100 * b.lit).toFixed(1) + '% lit)'; };
return gl.canvas.width + ' x ' + gl.canvas.height;

//# wait=done timeout=300
// Draw one full-size pass with the old and with the new shader, in bands, and time the GPU work.
const L = window.squaringLab; L.S.q.aa = 1; L.touch();
const gl = L.gl(), G = L.GLSL();
const fill = (orbit, eq, z0, n) => { const n2 = Math.abs(n - 2) < 1e-9; return orbit.split('__F__').join(L.compileFormula(eq, true, n2)).split('__Z0__').join(L.compileFormula(z0, false, n2)); };
const source = P => L.S.mode === 'k' ? P.GL_HEAD + G.GL_COLOUR + P.GL_KLEIN + P.GL_TAIL
  : P.GL_HEAD + G.GL_COLOUR + L.APPROACHES[L.S.approach].glsl + fill(P.GL_ORBIT, L.S.eq, L.S.z0, L.S.n) + P.GL_TAIL;
const cache = new Map();
window.progOf = P => { const s = source(P); if (!cache.has(s)) cache.set(s, L.makeProgram(s)); return cache.get(s); };
window.drawOnce = (P, o) => {
  const W = gl.canvas.width, H = gl.canvas.height, px = new Uint8Array(4), rows = window.bandRows || 24;
  gl.bindFramebuffer(gl.FRAMEBUFFER, null); gl.viewport(0, 0, W, H); gl.disable(gl.BLEND); gl.enable(gl.SCISSOR_TEST);
  const t0 = performance.now();
  for (let y = 0; y < H; y += rows) {
    gl.scissor(0, y, W, rows);
    L.setScene(P, Object.assign({ w: W, h: H, off: [0, 0], px: 1, nt: 3, steps: L.S.q.steps, normEps: 1, ao: true, shadow: true, analytic: true }, o));
    gl.drawArrays(gl.TRIANGLES, 0, 3);
    gl.readPixels(0, y, 1, 1, gl.RGBA, gl.UNSIGNED_BYTE, px);   // waits for the band
  }
  gl.disable(gl.SCISSOR_TEST);
  return performance.now() - t0;
};
// old against new for the scene in S; o overrides the pass options (nt, shadow, ao, analytic)
window.abDraw = (label, o) => {
  const a = window.progOf(G.OLD), b = window.progOf(G), ta = [], tb = [], drawOnce = window.drawOnce;
  drawOnce(a, o); drawOnce(b, o);   // first use of a program is slow
  for (let k = 0; k < 2; k++) { ta.push(drawOnce(a, o)); tb.push(drawOnce(b, o)); }
  return label + ': old ' + ta.map(x => x.toFixed(0)).join('/') + ' ms, new ' + tb.map(x => x.toFixed(0)).join('/') + ' ms';
};
window.newDraw = (label, o) => { const b = window.progOf(G), drawOnce = window.drawOnce; drawOnce(b, o); return label + ': ' + [0, 1].map(() => drawOnce(b, o).toFixed(0)).join('/') + ' ms'; };
return gl.canvas.width + ' x ' + gl.canvas.height;

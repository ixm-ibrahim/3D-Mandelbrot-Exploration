// TEST STAND-IN (out/r4/mesh) for the render-export module: just enough of CONTRACT4 to feed the mesh job with
// the real distance field. The snapshot is not frozen here (the test leaves the page alone while a job runs).
function takeSnapshot() { return { taken: performance.now() }; }
function releaseSnapshot(snap) { snap.released = true; }
async function sampleSlice(snap, cx, cy, side, z, N) {
  await new Promise(r => setTimeout(r, 0));
  if (!gl || lost) return null;
  const want = sceneNow(), P = want && progs.get(want.key);
  if (!P || P.state !== 'ready') return null;
  const t = makeTarget(N, N, true);
  if (!t.ok) { freeTarget(t); return null; }
  const keep = [S.flat, S.v2.x, S.v2.y, S.v2.h, S.cut];
  S.flat = true; S.v2.x = cx; S.v2.y = cy; S.v2.h = side; S.cut = z;
  gl.bindFramebuffer(gl.FRAMEBUFFER, t.fbo); gl.viewport(0, 0, N, N); gl.disable(gl.SCISSOR_TEST); gl.disable(gl.BLEND);
  setScene(P, { w: N, h: N, off: [0, 0], px: 1, nt: 3, steps: 1, normEps: 1, ao: false, shadow: false, sharp: false });
  [S.flat, S.v2.x, S.v2.y, S.v2.h, S.cut] = keep;
  gl.uniform1f(P.l('uRaw'), 1);
  gl.drawArrays(gl.TRIANGLES, 0, 3);
  const out = new Float32Array(4 * N * N);
  gl.readPixels(0, 0, N, N, gl.RGBA, gl.FLOAT, out);
  gl.uniform1f(P.l('uRaw'), 0);
  gl.bindFramebuffer(gl.FRAMEBUFFER, null); freeTarget(t);
  return out;
}

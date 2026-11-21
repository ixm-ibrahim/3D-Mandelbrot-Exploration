//#
// GPU time of one full pass by timer query (less sensitive to a busy CPU than wall-clock time).
const L = window.squaringLab, gl = L.gl(), G = L.GLSL();
const ext = gl.getExtension('EXT_disjoint_timer_query_webgl2');
if (!ext) return 'no timer query extension';
const wait = ms => new Promise(r => setTimeout(r, ms));
window.gpuTime = async (P, o) => {
  const prog = window.progOf(P), W = gl.canvas.width, H = gl.canvas.height, rows = 100, qs = [];
  gl.bindFramebuffer(gl.FRAMEBUFFER, null); gl.viewport(0, 0, W, H); gl.disable(gl.BLEND); gl.enable(gl.SCISSOR_TEST);
  for (let y = 0; y < H; y += rows) {
    const q = gl.createQuery();
    gl.beginQuery(ext.TIME_ELAPSED_EXT, q);
    gl.scissor(0, y, W, rows);
    L.setScene(prog, Object.assign({ w: W, h: H, off: [0, 0], px: 1, nt: 3, steps: L.S.q.steps, normEps: 1, ao: true, shadow: true, analytic: true }, o));
    gl.drawArrays(gl.TRIANGLES, 0, 3);
    gl.endQuery(ext.TIME_ELAPSED_EXT);
    qs.push(q);
    gl.flush();
    await wait(30);
  }
  gl.disable(gl.SCISSOR_TEST);
  let ns = 0;
  for (const q of qs) {
    for (let k = 0; k < 200 && !gl.getQueryParameter(q, gl.QUERY_RESULT_AVAILABLE); k++) await wait(10);
    ns += gl.getQueryParameter(q, gl.QUERY_RESULT);
    gl.deleteQuery(q);
  }
  return ns / 1e6;
};
window.abGpu = async (label, o) => {
  const best = { old: 1e9, now: 1e9 };
  await window.gpuTime(G.OLD, o); await window.gpuTime(G, o);
  for (let r = 0; r < 3; r++) { best.old = Math.min(best.old, await window.gpuTime(G.OLD, o)); best.now = Math.min(best.now, await window.gpuTime(G, o)); }
  return label + ': old ' + best.old.toFixed(1) + ' ms, new ' + best.now.toFixed(1) + ' ms, ratio ' + (best.now / best.old).toFixed(2);
};
return await window.abGpu('default, all on');
//#
return await window.abGpu('default, no shadow/crevices', { shadow: false, ao: false });
//#
const L = window.squaringLab; L.S.approach = 3; L.S.n = 8; L.S.iter = 10; L.cam.target = [0, 0, 0]; L.cam.dist = 4.2;
return await window.abGpu('classic n=8, all on');
//#
const L = window.squaringLab; L.S.approach = 1; L.S.n = 2; L.S.iter = 14; L.S.param.lathe.spin = 3;
return await window.abGpu('lathe spin 3, all on');

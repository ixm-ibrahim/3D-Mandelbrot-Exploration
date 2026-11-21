//#
// GPU time by timer query for a strip through the middle of the picture (rows 250 to 450), best of many
// tries: on a busy machine only the quickest try is free of other programs' work.
// window.gpuCompare(label, sets, o): sets is { name: shader set }, timed in turn.
const L = window.squaringLab, gl = L.gl(), G = L.GLSL();
const ext = gl.getExtension('EXT_disjoint_timer_query_webgl2');
if (!ext) return 'no timer query extension';
const wait = ms => new Promise(r => setTimeout(r, ms));
window.subAll = (s, a, b) => { if (!s.includes(a)) throw new Error('missing: ' + a); return s.split(a).join(b); };
window.gpuTime = async (P, o) => {
  const prog = window.progOf(P), W = gl.canvas.width, H = gl.canvas.height, q = gl.createQuery();
  gl.bindFramebuffer(gl.FRAMEBUFFER, null); gl.viewport(0, 0, W, H); gl.disable(gl.BLEND); gl.enable(gl.SCISSOR_TEST);
  gl.scissor(0, 250, W, 200);
  L.setScene(prog, Object.assign({ w: W, h: H, off: [0, 0], px: 1, nt: 3, steps: L.S.q.steps, normEps: 1, ao: true, shadow: true, analytic: true }, o));
  gl.beginQuery(ext.TIME_ELAPSED_EXT, q);
  gl.drawArrays(gl.TRIANGLES, 0, 3);
  gl.endQuery(ext.TIME_ELAPSED_EXT);
  gl.flush();
  gl.disable(gl.SCISSOR_TEST);
  for (let k = 0; k < 500 && !gl.getQueryParameter(q, gl.QUERY_RESULT_AVAILABLE); k++) await wait(8);
  const ns = gl.getQueryParameter(q, gl.QUERY_RESULT);
  gl.deleteQuery(q);
  return ns / 1e6;
};
window.gpuCompare = async (label, sets, o, tries) => {
  const best = {};
  for (const k in sets) await window.gpuTime(sets[k], o);
  for (let r = 0; r < (tries || 10); r++) for (const k in sets) best[k] = Math.min(best[k] || 1e9, await window.gpuTime(sets[k], o));
  const base = best[Object.keys(sets)[0]];
  return label + ': ' + Object.keys(sets).map(k => k + ' ' + best[k].toFixed(1) + ' ms (' + (best[k] / base).toFixed(2) + ')').join(' | ');
};
return 'timer ready';

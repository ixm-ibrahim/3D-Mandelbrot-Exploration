// p4-3: mean brightness of the canvas when the preview is shown and when the finished picture is shown (same view).
const L = window.squaringLab, T = window.__t, R = L.R, $ = id => document.getElementById(id);
R.warmOn = false;
const gl = $('view').getContext('webgl2'), od = gl.drawArrays, means = { prev: [], acc: [] };
gl.drawArrays = (...a) => { od(...a); if (gl.getParameter(gl.FRAMEBUFFER_BINDING) === null) {
  const w = gl.drawingBufferWidth, h = gl.drawingBufferHeight, px = new Uint8Array(w * h * 4); gl.readPixels(0, 0, w, h, gl.RGBA, gl.UNSIGNED_BYTE, px);
  let s = 0; for (let i = 0; i < px.length; i += 4) s += px[i] + px[i + 1] + px[i + 2];
  const m = s / (w * h * 3); Promise.resolve().then(() => { (means[R.shown] || []).push(Math.round(m * 10) / 10); }); } };
const out = {};
for (const q of ['qFast', 'qBal']) {
  $(q).click(); await T.idle(60000); means.prev = []; means.acc = [];
  L.cam.yaw += 0.02; L.touch(); await T.idle(60000);
  out[q] = { preview: means.prev[means.prev.length - 1], finished: means.acc[means.acc.length - 1], previewSize: R.pw + 'x' + R.ph };
}
gl.drawArrays = od;
return out;

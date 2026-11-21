// ---------- WebGL plumbing
const canvas = $('view'), stage = $('stage');
let gl = null, lost = false, floatOK = false, acc = null, prev = null, pickT = null, blitP = null;
const progs = new Map();
function makeProgram(fs) {
  const sh = (type, src) => {
    const s = gl.createShader(type);
    gl.shaderSource(s, src); gl.compileShader(s);
    if (!gl.getShaderParameter(s, gl.COMPILE_STATUS)) { const log = gl.getShaderInfoLog(s); gl.deleteShader(s); throw new Error(log || 'compile failed'); }
    return s;
  };
  const p = gl.createProgram();
  gl.attachShader(p, sh(gl.VERTEX_SHADER, VERT)); gl.attachShader(p, sh(gl.FRAGMENT_SHADER, fs));
  gl.linkProgram(p);
  if (!gl.getProgramParameter(p, gl.LINK_STATUS)) throw new Error(gl.getProgramInfoLog(p) || 'link failed');
  const cache = {};
  return { p, l: n => (n in cache ? cache[n] : (cache[n] = gl.getUniformLocation(p, n))) };
}
function sceneProgram() {
  let key, body;
  if (S.mode === 'k') { key = 'klein'; body = () => GL_KLEIN; }
  else {
    const n2 = Math.abs(S.n - 2) < 1e-9, fc = compileFormula(S.eq, true, n2), zc = compileFormula(S.z0, false, n2);
    key = [ap().id, fc, zc].join('|');
    body = () => ap().glsl + GL_ORBIT.replace('__F__', fc).replace('__Z0__', zc);
  }
  let e = progs.get(key);
  if (e === undefined) {
    try { e = makeProgram(GL_HEAD + GL_COLOUR + body() + GL_TAIL); }
    catch (err) { console.error('Shader failed for ' + key + ': ' + err.message); e = null; }
    if (progs.size > 14) { const old = progs.keys().next().value, dead = progs.get(old); if (dead) gl.deleteProgram(dead.p); progs.delete(old); }
    progs.set(key, e);
  }
  return e;
}
function makeTarget(w, h, f32) {
  const tex = gl.createTexture();
  gl.bindTexture(gl.TEXTURE_2D, tex);
  if (f32) gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA32F, w, h, 0, gl.RGBA, gl.FLOAT, null);
  else if (floatOK) gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA16F, w, h, 0, gl.RGBA, gl.HALF_FLOAT, null);
  else gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA8, w, h, 0, gl.RGBA, gl.UNSIGNED_BYTE, null);
  const filt = f32 ? gl.NEAREST : gl.LINEAR;
  gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, filt); gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, filt);
  gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE); gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
  const fbo = gl.createFramebuffer();
  gl.bindFramebuffer(gl.FRAMEBUFFER, fbo);
  gl.framebufferTexture2D(gl.FRAMEBUFFER, gl.COLOR_ATTACHMENT0, gl.TEXTURE_2D, tex, 0);
  const ok = gl.checkFramebufferStatus(gl.FRAMEBUFFER) === gl.FRAMEBUFFER_COMPLETE;
  gl.bindFramebuffer(gl.FRAMEBUFFER, null);
  return { tex, fbo, w, h, ok };
}
function freeTarget(t) { if (t) { gl.deleteTexture(t.tex); gl.deleteFramebuffer(t.fbo); } }
function setupGL() {
  const f32 = !!gl.getExtension('EXT_color_buffer_float');
  floatOK = f32 || !!gl.getExtension('EXT_color_buffer_half_float');
  progs.clear(); acc = prev = null;
  blitP = makeProgram(BLIT);
  pickT = f32 ? makeTarget(1, 1, true) : null;
  if (pickT && !pickT.ok) pickT = null;
}
function initGL() {
  gl = canvas.getContext('webgl2', { antialias: false, alpha: false, powerPreference: 'high-performance' });
  if (!gl) { $('glfail').hidden = false; return; }
  setupGL();
  canvas.addEventListener('webglcontextlost', e => { e.preventDefault(); lost = true; R.pend = null; });
  canvas.addEventListener('webglcontextrestored', () => { lost = false; setupGL(); touch(); });
}
function ensureTargets() {
  const dpr = Math.min(window.devicePixelRatio || 1, 2);
  let w = stage.clientWidth * dpr * S.q.res, h = stage.clientHeight * dpr * S.q.res;
  const cap = Math.min(1, 3200 / Math.max(w, h));
  w = Math.max(2, Math.round(w * cap)); h = Math.max(2, Math.round(h * cap));
  if (canvas.width !== w || canvas.height !== h) { canvas.width = w; canvas.height = h; }
  if (!acc || acc.w !== w || acc.h !== h) {
    freeTarget(acc); freeTarget(prev);
    acc = makeTarget(w, h, false); prev = makeTarget(w, h, false);
    if (!acc.ok && floatOK) { floatOK = false; freeTarget(acc); freeTarget(prev); acc = makeTarget(w, h, false); prev = makeTarget(w, h, false); }
  }
}
function setScene(P, o) {
  gl.useProgram(P.p);
  const b = basis(), L = P.l, el = S.lightEl * PI / 180, az = S.lightAz * PI / 180, k = S.k;
  gl.uniform2f(L('uRes'), o.w, o.h); gl.uniform2f(L('uOff'), o.off[0], o.off[1]);
  gl.uniform3fv(L('uCamPos'), b.pos); gl.uniformMatrix3fv(L('uCam'), false, [...b.right, ...b.up, ...b.f]);
  gl.uniform1f(L('uFov'), S.view.fov); gl.uniform1f(L('uPow'), S.n); gl.uniform4fv(L('uA'), apVec());
  gl.uniform1f(L('uJulia'), S.mode === 'j' ? 1 : 0); gl.uniform3fv(L('uC'), S.c); gl.uniform1f(L('uBail'), 64);
  gl.uniform3fv(L('uAbs'), S.abs); gl.uniform3f(L('uSgn'), 1, S.flip[0] ? -1 : 1, S.flip[1] ? -1 : 1);
  gl.uniform1f(L('uCut'), S.cutOn ? S.cut : 1e9); gl.uniform1f(L('uPx'), o.px);
  gl.uniform1i(L('uIter'), S.mode === 'k' ? k.iter : S.iter); gl.uniform1i(L('uSteps'), o.steps); gl.uniform1i(L('uNT'), o.nt);
  gl.uniform1f(L('uDetail'), S.q.detail); gl.uniform1f(L('uStepK'), S.q.stepk); gl.uniform1f(L('uNormEps'), o.normEps);
  gl.uniform1f(L('uAO'), o.ao ? 1 : 0); gl.uniform1f(L('uShadow'), o.shadow ? 1 : 0); gl.uniform1i(L('uShSteps'), 28);
  gl.uniform1f(L('uAnalytic'), o.analytic && S.mode !== 'k' ? 1 : 0); gl.uniform1f(L('uPick'), o.pick ? 1 : 0);
  setColourUniforms(L);
  gl.uniform3fv(L('uBg'), lin(theme.stage)); gl.uniform3fv(L('uCutCol'), lin(theme.cut)); gl.uniform3fv(L('uCutInk'), lin(theme.cutInk));
  gl.uniform3f(L('uLight'), Math.cos(el) * Math.cos(az), Math.cos(el) * Math.sin(az), Math.sin(el));
  gl.uniform3f(L('uKMu'), k.mx, k.my, k.mz); gl.uniform3f(L('uKInvC'), k.cx, k.cy, k.cz);
  gl.uniform1f(L('uKL'), k.L); gl.uniform1f(L('uK3'), k.three ? 1 : 0); gl.uniform1f(L('uKInvR'), k.invR);
}
function blit(useAcc) {
  gl.bindFramebuffer(gl.FRAMEBUFFER, null);
  gl.viewport(0, 0, canvas.width, canvas.height);
  gl.disable(gl.SCISSOR_TEST); gl.disable(gl.BLEND);
  gl.useProgram(blitP.p);
  gl.activeTexture(gl.TEXTURE0); gl.bindTexture(gl.TEXTURE_2D, acc.tex);
  gl.activeTexture(gl.TEXTURE1); gl.bindTexture(gl.TEXTURE_2D, prev.tex);
  gl.uniform1i(blitP.l('uAcc'), 0); gl.uniform1i(blitP.l('uPrev'), 1);
  gl.uniform2f(blitP.l('uSize'), canvas.width, canvas.height);
  gl.uniform2f(blitP.l('uPrevScale'), R.pw / prev.w, R.ph / prev.h);
  gl.uniform2f(blitP.l('uPrevMax'), (R.pw - 0.5) / prev.w, (R.ph - 0.5) / prev.h);
  gl.uniform1f(blitP.l('uUseAcc'), useAcc ? 1 : 0);
  gl.drawArrays(gl.TRIANGLES, 0, 3);
}

// ---------- drawing schedule. A quick preview while anything moves; at rest, a full-size picture
// drawn in bands so the page never stalls, then refined by adding jittered passes.
const R = { pend: null, wantPrev: false, restart: false, prog: null, lastTouch: 0, ps: 0.35, rows: 32, rowMs: 0, raf: 0, pw: 2, ph: 2, total: 1 };
let uiDirty = false;
const halton = (i, b) => { let f = 1, r = 0; while (i > 0) { f /= b; r += f * (i % b); i = Math.floor(i / b); } return r; };
function kick() { // next animation frame, or a timer if the page is in the background and frames are paused
  if (R.raf) return;
  const run = bg => { cancelAnimationFrame(R.raf); clearTimeout(R.tmr); R.raf = 0; R.bg = bg; loop(); };
  R.raf = requestAnimationFrame(() => run(false)); R.tmr = setTimeout(() => run(true), 300);
}
function touch() { R.wantPrev = true; R.restart = true; R.prog = null; R.lastTouch = performance.now(); uiDirty = true; kick(); }
function fence(kind) { R.pend = { kind, sync: gl.fenceSync(gl.SYNC_GPU_COMMANDS_COMPLETE, 0), t0: performance.now() }; gl.flush(); }
function say(t) { $('status').textContent = t; }
// true once the picture on screen is the finished one for the current settings
function renderIdle() { return !R.restart && !R.prog && !R.pend && !R.wantPrev; }
// the view moved but the scene itself need not be redrawn: refresh overlays on the next frame
function viewChanged() { uiDirty = true; kick(); }
function loop() {
  R.raf = 0;
  if (uiDirty) { uiDirty = false; hooks.view.forEach(f => f()); }
  if (!gl || lost) return;
  if (R.pend) {
    if (gl.clientWaitSync(R.pend.sync, 0, 0) === gl.TIMEOUT_EXPIRED) return kick();
    gl.deleteSync(R.pend.sync);
    const job = R.pend, ms = Math.max(4, performance.now() - job.t0);
    R.pend = null;
    if (job.kind === 'prev') {
      blit(false);
      // a full-size row costs about this much; shadows, crevice shading and extra steps roughly triple it
      if (!R.bg) {
        R.rowMs = ms / R.ph * (canvas.width / R.pw) * 3;
        R.ps = clamp(R.ps * clamp(Math.sqrt(26 / ms), 0.6, 1.12), 0.12, 0.8);
      }
    } else {
      if (!R.bg) R.rows = clamp(R.rows * clamp(30 / ms, 0.2, 1.6), 2, 4096);
      if (!R.wantPrev) blit(true);
      if (!R.prog && !R.wantPrev) say(`Done: ${R.total} ${R.total === 1 ? 'pass' : 'passes'} at ${canvas.width} × ${canvas.height}`);
    }
  }
  let P = null;
  try { P = sceneProgram(); } catch (err) { P = null; }
  if (!P) { $('glfail').hidden = false; $('glfail').textContent = 'The shader for this setting did not compile on this device. Try another approach or equation.'; return; }
  $('glfail').hidden = true;
  ensureTargets();
  if (R.wantPrev) { R.wantPrev = false; preview(P); return kick(); }
  if (R.prog) { band(P); return kick(); }
  if (R.restart) {
    if (performance.now() - R.lastTouch > 170) {
      R.restart = false;
      R.total = floatOK ? Math.max(1, Math.round(S.q.aa)) : 1; R.prog = { s: 0, y: 0 };
      if (R.bg) R.rows = Math.max(R.rows, canvas.height / 6);
      else if (R.rowMs > 0) R.rows = clamp(30 / R.rowMs, 2, canvas.height);
      gl.bindFramebuffer(gl.FRAMEBUFFER, acc.fbo); gl.disable(gl.SCISSOR_TEST); gl.clearColor(0, 0, 0, 0); gl.clear(gl.COLOR_BUFFER_BIT);
      band(P);
    }
    return kick();
  }
}
function preview(P) {
  const w = Math.max(2, Math.round(canvas.width * R.ps)), h = Math.max(2, Math.round(canvas.height * R.ps));
  R.pw = w; R.ph = h;
  gl.bindFramebuffer(gl.FRAMEBUFFER, prev.fbo); gl.viewport(0, 0, w, h); gl.disable(gl.SCISSOR_TEST); gl.disable(gl.BLEND);
  setScene(P, { w, h, off: [0, 0], px: w / stage.clientWidth, nt: 3, steps: Math.min(S.q.steps, 120), normEps: 1.5, ao: false, shadow: false, analytic: S.q.normals === 'sharp' });
  gl.drawArrays(gl.TRIANGLES, 0, 3);
  fence('prev');
  say('Preview while moving');
}
function band(P) {
  const g = R.prog, W = canvas.width, H = canvas.height, rows = Math.min(Math.max(2, Math.round(R.rows)), H - g.y);
  gl.bindFramebuffer(gl.FRAMEBUFFER, acc.fbo); gl.viewport(0, 0, W, H);
  gl.enable(gl.SCISSOR_TEST); gl.scissor(0, g.y, W, rows);
  gl.enable(gl.BLEND); gl.blendFunc(gl.ONE, gl.ONE);
  const off = g.s === 0 ? [0, 0] : [halton(g.s, 2) - 0.5, halton(g.s, 3) - 0.5];
  setScene(P, { w: W, h: H, off, px: W / stage.clientWidth, nt: 3, steps: S.q.steps, normEps: S.q.smooth, ao: S.q.ao, shadow: S.q.shadow, analytic: S.q.normals === 'sharp' });
  gl.drawArrays(gl.TRIANGLES, 0, 3);
  gl.disable(gl.SCISSOR_TEST); gl.disable(gl.BLEND);
  fence('band');
  say(g.s === 0 ? 'Drawing at full size' : `Refining: pass ${g.s + 1} of ${R.total}`);
  g.y += rows;
  if (g.y >= H) { g.y = 0; g.s++; if (g.s >= R.total) R.prog = null; }
}
function pick(px, py) {
  if (!gl || lost || !pickT) return null;
  let P = null;
  try { P = sceneProgram(); } catch (err) { return null; }
  if (!P) return null;
  const w = stage.clientWidth, h = stage.clientHeight, out = new Float32Array(4);
  gl.bindFramebuffer(gl.FRAMEBUFFER, pickT.fbo); gl.viewport(0, 0, 1, 1); gl.disable(gl.SCISSOR_TEST); gl.disable(gl.BLEND);
  setScene(P, { w, h, off: [px - 0.5, h - py - 0.5], px: 1, nt: 1, steps: 300, normEps: 1, ao: false, shadow: false, analytic: false, pick: true });
  gl.drawArrays(gl.TRIANGLES, 0, 3);
  gl.readPixels(0, 0, 1, 1, gl.RGBA, gl.FLOAT, out);
  gl.bindFramebuffer(gl.FRAMEBUFFER, null);
  return out[3] > 0.5 ? [out[0], out[1], out[2]] : null;
}

// ---------- WebGL plumbing
const canvas = $('view'), stage = $('stage');
let gl = null, lost = false, floatOK = false, acc = null, prev = null, pickT = null, blitP = null;
const progs = new Map();   // scene programs by key, least recently used first
// Bookkeeping of the renderer. Other modules use renderIdle() and leave R alone. Tests may switch off R.warmOn, and
// may clear R.par or R.tq (while nothing is being drawn) to take the paths of a driver without those extensions.
const R = {
  pend: null,                // the preview or band the GPU is working on: { kind, sync, t0, q, flat | frac }
  wantPrev: false,           // a preview is due
  restart: false,            // a full-quality drawing is due once things have stopped moving
  prog: null,                // the full-quality drawing under way: { s: pass, y: next row }
  lastTouch: 0, raf: 0, tmr: 0, fast: 0,   // when touch() was last called; the loop's frame request and timers
  bg: false,                 // animation frames are paused (a background tab): the loop runs from its timer
  ps: 0.35, ps2: 1,          // preview size as a share of the full picture: ray-marched view, 2D view
  rows: 32,                  // rows in the next band
  rowMs: 0, rowExact: false, // what one full-size row costs, judged from the last preview, and whether the GPU counted it
  pw: 2, ph: 2, total: 1,    // size of the last preview; passes in the full-quality drawing
  tq: null, q: null,         // the GPU timer extension (EXT_disjoint_timer_query_webgl2) or null, and the query now running
  dt: 16.7, lastLoop: 0,     // time between animation frames, smoothed; when a frame last ran the loop
  par: null,                 // the KHR_parallel_shader_compile extension, or null where the driver lacks it
  shown: null,               // which target holds the picture on screen: 'prev' the preview, 'acc' the full-size one, null neither
  painted: false,            // the canvas has shown a picture since the context was made
  sig: '', want: null,       // the settings the wanted program was worked out from, and that program's key and source
  hold: 0, holdKey: '',      // frames waited before a compile that will block (drivers without parallel compile)
  busy: false,               // the busy label is up for a compile
  failed: '',                // why nothing can be drawn ('formula' | 'shader'), or ''
  bar: null,                 // the progress bar element
  warmOn: true, warming: null, warmT: 0,   // preparing likely programs ahead of time: allowed, the one in hand, its timer
  compiles: 0,               // programs started since the page loaded
};

// A program is compiled and linked without waiting for the result. With KHR_parallel_shader_compile the
// driver works on another thread and COMPLETION_STATUS_KHR tells when it has finished. Asking anything else
// about the program before then (link status, a uniform location) makes the page wait for the driver.
function progStart(fsSrc) {
  const p = gl.createProgram(), vs = gl.createShader(gl.VERTEX_SHADER), fs = gl.createShader(gl.FRAGMENT_SHADER);
  gl.shaderSource(vs, VERT); gl.compileShader(vs);
  gl.shaderSource(fs, fsSrc); gl.compileShader(fs);
  gl.attachShader(p, vs); gl.attachShader(p, fs); gl.linkProgram(p);
  const cache = {};
  R.compiles++;
  return { p, vs, fs, state: 'pending', log: '', told: false, l: n => (n in cache ? cache[n] : (cache[n] = gl.getUniformLocation(p, n))) };
}
const progSettled = e => !R.par || !!gl.getProgramParameter(e.p, R.par.COMPLETION_STATUS_KHR);
function progFinish(e) {   // waits for the driver, so call it after progSettled(e), or where waiting is accepted
  if (e.state !== 'pending' || gl.isContextLost()) return e;
  if (gl.getProgramParameter(e.p, gl.LINK_STATUS)) e.state = 'ready';
  else {
    e.log = [gl.getShaderInfoLog(e.fs), gl.getShaderInfoLog(e.vs), gl.getProgramInfoLog(e.p)].filter(Boolean).join('\n') || 'link failed';
    e.state = 'failed'; gl.deleteProgram(e.p);
  }
  gl.deleteShader(e.vs); gl.deleteShader(e.fs);
  return e;
}
function progFree(e) {
  if (e.state === 'pending') { gl.deleteShader(e.vs); gl.deleteShader(e.fs); }
  if (e.state !== 'failed') gl.deleteProgram(e.p);
}
// The scene program for one combination of approach and equation: its key in the cache and how to write its source.
function sceneWant(a, eq, z0, n2, klein) {
  if (klein) return { key: 'klein', src: () => GL_HEAD + GL_COLOUR + GL_KLEIN + GL_TAIL };
  const fc = compileFormula(eq, true, n2), zc = compileFormula(z0, false, n2);
  return { key: [a.id, fc, zc].join('|'), src: () => GL_HEAD + GL_COLOUR + a.glsl + GL_ORBIT.split('__F__').join(fc).split('__Z0__').join(zc) + GL_TAIL };
}
function sceneNow() {   // what the current settings need; remembered, because the drawing loop asks every frame
  const klein = S.mode === 'k', n2 = Math.abs(S.n - 2) < 1e-9, sig = klein ? 'k' : [S.approach, n2, S.eq, S.z0].join('\n');
  if (R.sig !== sig) {
    R.sig = sig; R.want = null;
    try { R.want = sceneWant(ap(), S.eq, S.z0, n2, klein); } catch (err) { console.error('The formula could not be read: ' + err.message); }
  }
  return R.want;
}
function sceneEntry(w, start) {   // look a program up; with `start`, begin compiling it if it is new
  let e = progs.get(w.key);
  if (e) { progs.delete(w.key); progs.set(w.key, e); }
  else if (start) {
    e = progStart(w.src()); progs.set(w.key, e);
    for (const [k, old] of progs) { if (progs.size <= 40) break; progFree(old); progs.delete(k); }
  }
  return e || null;
}
// The program to draw with: an entry that is ready, 'wait' while it is being prepared, or 'formula' / 'shader'
// (the reason) when it cannot be built.
function sceneAcquire() {
  const w = sceneNow();
  if (!w) return 'formula';
  let e = sceneEntry(w, !!R.par);
  if (!e) {   // this driver compiles on the page's time: let the busy label reach the screen first
    if (R.holdKey !== w.key) { R.holdKey = w.key; R.hold = 0; }
    if (R.hold++ < 2) return 'wait';
    R.holdKey = '';
    e = sceneEntry(w, true);
  }
  if (e.state === 'pending') {
    if (!progSettled(e)) return 'wait';
    if (progFinish(e).state === 'pending') return 'wait';
  }
  if (e.state === 'failed') {
    if (!e.told) { e.told = true; console.error('Shader failed for ' + w.key + ': ' + e.log); }
    return 'shader';
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
  R.par = gl.getExtension('KHR_parallel_shader_compile');
  R.tq = gl.getExtension('EXT_disjoint_timer_query_webgl2'); R.q = null;
  progs.clear(); acc = prev = null; R.shown = null; R.painted = false; R.warming = null; R.holdKey = '';
  blitP = progFinish(progStart(BLIT));   // a few lines of shader: waiting for it is fine
  if (blitP.state !== 'ready') throw new Error('The display shader failed: ' + blitP.log);
  pickT = f32 ? makeTarget(1, 1, true) : null;
  if (pickT && !pickT.ok) pickT = null;
}
function initGL() {
  gl = canvas.getContext('webgl2', { antialias: false, alpha: false, powerPreference: 'high-performance' });
  if (!gl) { $('glfail').hidden = false; return; }
  if (!R.bar) {
    const bar = document.createElement('div');
    bar.id = 'drawProgress'; bar.className = 'draw-progress'; bar.hidden = true;
    bar.setAttribute('aria-hidden', 'true');   // the status line under the stage says the same in words
    bar.appendChild(document.createElement('span'));
    stage.appendChild(bar); R.bar = bar;
  }
  const setup = () => {
    try { setupGL(); return true; } catch (err) { console.error(err.message); gl = null; $('glfail').hidden = false; return false; }
  };
  if (!setup()) return;
  canvas.addEventListener('webglcontextlost', e => {
    e.preventDefault(); lost = true; R.pend = null; R.prog = null;
    stageProgress(null);
    if (R.busy) { R.busy = false; setBusy('compile', null); }
  });
  canvas.addEventListener('webglcontextrestored', () => { lost = false; if (setup()) touch(); });
}
function ensureTargets() {
  const dpr = Math.min(window.devicePixelRatio || 1, 2);
  let w = stage.clientWidth * dpr * S.q.res, h = stage.clientHeight * dpr * S.q.res;
  const cap = Math.min(1, 3200 / Math.max(w, h));
  w = Math.max(2, Math.round(w * cap)); h = Math.max(2, Math.round(h * cap));
  if (canvas.width !== w || canvas.height !== h) {
    canvas.width = w; canvas.height = h;
    // resizing empties the canvas: put the last picture straight back, stretched, until the new size has been drawn
    if (acc && R.shown) blit(R.shown === 'acc');
  }
  if (!acc || acc.w !== w || acc.h !== h) {
    freeTarget(acc); freeTarget(prev);
    acc = makeTarget(w, h, false); prev = makeTarget(w, h, false);
    if (!acc.ok && floatOK) { floatOK = false; freeTarget(acc); freeTarget(prev); acc = makeTarget(w, h, false); prev = makeTarget(w, h, false); }
    R.shown = null;
  }
}
// How the distance is estimated, as the shader's uNT: 3, 1 or 0 neighbouring orbits.
function sceneDe() { const d = S.q.de === undefined ? 3 : +S.q.de; return d >= 3 ? 3 : d >= 1 ? 1 : 0; }
function setScene(P, o) {
  gl.useProgram(P.p);
  const b = basis(), L = P.l, el = S.lightEl * PI / 180, az = S.lightAz * PI / 180, k = S.k, v = S.view, v2 = S.v2;
  gl.uniform2f(L('uRes'), o.w, o.h); gl.uniform2f(L('uOff'), o.off[0], o.off[1]);
  gl.uniform3fv(L('uCamPos'), b.pos); gl.uniformMatrix3fv(L('uCam'), false, [...b.right, ...b.up, ...b.f]);
  gl.uniform1f(L('uFov'), v.fov); gl.uniform1f(L('uBound'), v.bound);
  gl.uniform1f(L('uPow'), S.n); gl.uniform4fv(L('uA'), apVec());
  gl.uniform1f(L('uJulia'), S.mode === 'j' ? 1 : 0); gl.uniform3fv(L('uC'), S.c);
  gl.uniform1f(L('uMosaic'), S.mosaic && S.mode === 'm' ? S.mosaicCell : 0);
  gl.uniform3fv(L('uAbs'), S.abs); gl.uniform3f(L('uSgn'), 1, S.flip[0] ? -1 : 1, S.flip[1] ? -1 : 1);
  gl.uniform1f(L('uBail'), 64); gl.uniform1i(L('uIter'), S.mode === 'k' ? k.iter : S.iter);
  gl.uniform1f(L('uCut'), S.cutOn ? S.cut : 1e9);
  gl.uniform1f(L('uFlat'), S.flat ? 1 : 0); gl.uniform2f(L('uFlatC'), v2.x, v2.y); gl.uniform1f(L('uFlatH'), v2.h); gl.uniform1f(L('uSliceZ'), S.cut);
  gl.uniform1i(L('uSteps'), o.steps); gl.uniform1i(L('uNT'), o.nt);
  gl.uniform1f(L('uDetail'), S.q.detail); gl.uniform1f(L('uStepK'), S.q.stepk); gl.uniform1f(L('uNormEps'), o.normEps);
  gl.uniform1f(L('uAO'), o.ao ? 1 : 0); gl.uniform1f(L('uShadow'), o.shadow ? 1 : 0); gl.uniform1i(L('uShSteps'), 28);
  // the exact slope needs all three neighbouring orbits
  gl.uniform1f(L('uAnalytic'), o.sharp && o.nt === 3 && S.mode !== 'k' ? 1 : 0); gl.uniform1f(L('uPick'), o.pick ? 1 : 0);
  gl.uniform1f(L('uPx'), o.px);
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
  R.shown = useAcc ? 'acc' : 'prev'; R.painted = true;
}
// Before the first picture exists the canvas would show black: paint the stage colour the display shader gives the background.
function stageClear() {
  const c = lin(theme.stage || [0, 0, 0]).map(x => Math.pow(clamp(x / (1 + 0.12 * x) * 1.12, 0, 1), 0.4545));
  gl.bindFramebuffer(gl.FRAMEBUFFER, null); gl.disable(gl.SCISSOR_TEST);
  gl.clearColor(c[0], c[1], c[2], 1); gl.clear(gl.COLOR_BUFFER_BIT);
}
// The thin bar along the bottom of the stage. f: share of the full-quality drawing done, or null to hide it.
function stageProgress(f) {
  const el = R.bar;
  if (!el) return;
  if (f === null) { if (!el.hidden) el.hidden = true; return; }
  el.firstChild.style.transform = `scaleX(${clamp(f, 0, 1).toFixed(4)})`;
  if (el.hidden) el.hidden = false;
}
function sceneFail(why) {   // why: 'formula', 'shader', or '' when all is well
  if (R.failed === why) return;
  R.failed = why;
  const el = $('glfail');
  el.hidden = !why;
  if (why) {
    el.textContent = why === 'formula'
      ? 'This equation could not be turned into a picture. Check the two formulas in the Equation section.'
      : 'The shader for this setting did not compile on this device. Try another approach or equation.';
    say('Nothing drawn: this setting did not compile');
    stageProgress(null);
  }
}

// ---------- drawing schedule. A quick preview while anything moves; at rest, a full-size picture
// drawn in bands so the page never stalls, then refined by adding jittered passes.
let uiDirty = false;
const halton = (i, b) => { let f = 1, r = 0; while (i > 0) { f /= b; r += f * (i % b); i = Math.floor(i / b); } return r; };
function kick() { // next animation frame, or a timer if the page is in the background and frames are paused
  if (R.raf) return;
  R.raf = requestAnimationFrame(() => kicked(false, true)); R.tmr = setTimeout(() => kicked(true, true), 300);
  // With a GPU timer the bands are sized by their real cost, so a finished band need not wait for the next frame:
  // it is looked for between frames and the next one follows at once, which keeps the GPU busy.
  if (R.tq && R.pend && R.pend.kind === 'band') R.fast = setTimeout(bandPoll, 3);
}
function kicked(bg, frame) { cancelAnimationFrame(R.raf); clearTimeout(R.tmr); clearTimeout(R.fast); R.raf = 0; R.bg = bg; loop(frame); }
function bandPoll() {
  if (!R.raf || !R.pend || !gl || lost) return;
  if (gl.clientWaitSync(R.pend.sync, 0, 0) === gl.TIMEOUT_EXPIRED) R.fast = setTimeout(bandPoll, 3);
  else kicked(R.bg, false);
}
function touch() { R.wantPrev = true; R.restart = true; R.prog = null; R.lastTouch = performance.now(); uiDirty = true; kick(); }
// Timing one preview or band. The wall clock counts more than the drawing: the wait for the next animation frame,
// and for whatever else is using the GPU. Where the driver has a timer, its own count of the drawing is used, so a
// busy GPU or a slow frame rate cannot talk the schedule into ever smaller bands.
function jobBegin() {
  if (!R.tq) return;
  if (R.q) { gl.endQuery(R.tq.TIME_ELAPSED_EXT); gl.deleteQuery(R.q); }   // left open by a drawing call that threw
  R.q = gl.createQuery(); gl.beginQuery(R.tq.TIME_ELAPSED_EXT, R.q);
}
function fence(job) {
  if (R.q) { gl.endQuery(R.tq.TIME_ELAPSED_EXT); job.q = R.q; R.q = null; }
  job.sync = gl.fenceSync(gl.SYNC_GPU_COMMANDS_COMPLETE, 0); job.t0 = performance.now(); R.pend = job; gl.flush();
}
function jobCost(job) {   // -> { ms, exact }: exact when ms is the GPU's own count
  const wall = Math.max(4, performance.now() - job.t0), c = { ms: wall, exact: false };
  if (job.q) {
    if (!gl.getParameter(R.tq.GPU_DISJOINT_EXT) && gl.getQueryParameter(job.q, gl.QUERY_RESULT_AVAILABLE)) {
      const t = gl.getQueryParameter(job.q, gl.QUERY_RESULT) / 1e6;
      if (t > 0.05 && t < wall + 1) { c.ms = t; c.exact = true; }
    }
    gl.deleteQuery(job.q);
  }
  return c;
}
// How long one job should take. Counted by the GPU: most of a frame, leaving room for the page's own drawing.
// Timed by the clock, which is read once per frame: grow while a job is back by the next frame, shrink when it takes two.
// The 2D preview is allowed twice as long: there a sharp picture at half the frame rate beats a soft one.
const bandTarget = exact => (exact ? clamp(0.7 * R.dt, 8, 24) : 1.8 * R.dt);
const prevTarget = (exact, flat) => (exact ? clamp(0.7 * R.dt, 10, 24) : 1.56 * R.dt) * (flat ? 2 : 1);
function say(t) { const el = $('status'); if (el.textContent !== t) el.textContent = t; }
// true once nothing more will be drawn for the current settings: the finished picture is up (or its shader failed)
function renderIdle() { return !R.restart && !R.prog && !R.pend && !R.wantPrev; }
// the view moved but the scene itself need not be redrawn: refresh overlays on the next frame
function viewChanged() { uiDirty = true; kick(); }
function loop(frame) {
  const t = performance.now(); R.where = 'start'; loopIn(frame);
  const d = performance.now() - t; if (d > (R.loopMax || 0)) { R.loopMax = d; R.loopWhere = R.where; }
}
function loopIn(frame) {
  R.raf = 0;
  if (frame) {
    const now = performance.now();
    if (!R.bg && now - R.lastLoop < 100) R.dt = clamp(R.dt + (now - R.lastLoop - R.dt) * 0.1, 4, 50);
    R.lastLoop = now;
  }
  if (uiDirty) { uiDirty = false; hooks.view.forEach(f => f()); }
  if (!gl || lost) return;
  if (R.pend) {
    if (gl.clientWaitSync(R.pend.sync, 0, 0) === gl.TIMEOUT_EXPIRED) return kick();
    gl.deleteSync(R.pend.sync);
    const dbgWall = performance.now() - R.pend.t0;
    const job = R.pend, c = jobCost(job), ms = c.ms;
    (R.log = R.log || []).push([job.kind, job.rows || 0, +dbgWall.toFixed(1), +c.ms.toFixed(2), c.exact ? 1 : 0, +R.dt.toFixed(1)]);
    R.pend = null;
    if (job.kind === 'prev') {
      blit(false);
      if (!R.bg) {
        // a full-size row costs about this much; in the ray-marched view shadows, crevice shading and extra steps roughly triple it
        R.rowMs = ms / R.ph * (canvas.width / R.pw) * (job.flat ? 1 : 3); R.rowExact = c.exact;
        const k = Math.sqrt(prevTarget(c.exact, job.flat) / ms);
        if (job.flat) R.ps2 = clamp(R.ps2 * clamp(k, 0.4, 1.25), 0.2, 1);
        else R.ps = clamp(R.ps * clamp(k, 0.4, 1.12), 0.12, 0.8);
      }
    } else {
      // by the clock a band can look slow for reasons a smaller band would not cure, so there it keeps a least size
      if (!R.bg) R.rows = clamp(R.rows * clamp(bandTarget(c.exact) / ms, 0.2, 1.6), c.exact ? 2 : Math.max(2, canvas.height / 32), 4096);
      if (!R.wantPrev) { blit(true); stageProgress(R.prog ? job.frac : null); }
      if (!R.prog && !R.wantPrev) {
        say(`Done: ${R.total} ${R.total === 1 ? 'pass' : 'passes'} at ${canvas.width} × ${canvas.height}`);
        if (R.warmOn && R.par) { clearTimeout(R.warmT); R.warmT = setTimeout(sceneWarm, 500); }
      }
    }
  }
  R.where = 'acquire'; const P = sceneAcquire(); R.where = 'after acquire';
  if (P === 'wait') {   // the last picture stays up while the driver prepares the new program
    if (!R.busy) { R.busy = true; setBusy('compile', 'Preparing the formula'); say('Preparing the formula'); stageProgress(null); }
    if (!R.painted) stageClear();
    return kick();
  }
  if (R.busy) { R.busy = false; setBusy('compile', null); }
  if (typeof P === 'string') { sceneFail(P); R.wantPrev = R.restart = false; R.prog = null; return; }
  sceneFail('');
  ensureTargets();
  if (R.wantPrev) { R.wantPrev = false; stageProgress(null); R.where = 'preview'; preview(P); return kick(); }
  if (R.prog) { R.where = 'band'; band(P); return kick(); }
  if (R.restart) {
    if (performance.now() - R.lastTouch > 170) {
      R.restart = false;
      R.total = floatOK ? Math.max(1, Math.round(S.q.aa)) : 1; R.prog = { s: 0, y: 0 };
      if (R.bg) R.rows = Math.max(R.rows, canvas.height / 6);
      else if (R.rowMs > 0) R.rows = clamp(bandTarget(R.rowExact) / R.rowMs, 2, canvas.height);
      gl.bindFramebuffer(gl.FRAMEBUFFER, acc.fbo); gl.disable(gl.SCISSOR_TEST); gl.clearColor(0, 0, 0, 0); gl.clear(gl.COLOR_BUFFER_BIT);
      stageProgress(0);
      band(P);
    }
    return kick();
  }
}
function preview(P) {
  // the 2D view has no ray march, so its preview starts at full size and shrinks only if the device cannot keep up
  const flat = !!S.flat, ps = flat ? R.ps2 : R.ps;
  const w = Math.max(2, Math.round(canvas.width * ps)), h = Math.max(2, Math.round(canvas.height * ps));
  R.pw = w; R.ph = h;
  gl.bindFramebuffer(gl.FRAMEBUFFER, prev.fbo); gl.viewport(0, 0, w, h); gl.disable(gl.SCISSOR_TEST); gl.disable(gl.BLEND);
  jobBegin();
  setScene(P, { w, h, off: [0, 0], px: w / Math.max(1, stage.clientWidth), nt: sceneDe(), steps: Math.min(S.q.steps, 120), normEps: 1.5, ao: false, shadow: false, sharp: S.q.normals === 'sharp' });
  gl.drawArrays(gl.TRIANGLES, 0, 3);
  fence({ kind: 'prev', flat });
  say('Preview while moving');
}
function band(P) {
  const g = R.prog, W = canvas.width, H = canvas.height, rows = Math.min(Math.max(2, Math.round(R.rows)), H - g.y);
  gl.bindFramebuffer(gl.FRAMEBUFFER, acc.fbo); gl.viewport(0, 0, W, H);
  gl.enable(gl.SCISSOR_TEST); gl.scissor(0, g.y, W, rows);
  gl.enable(gl.BLEND); gl.blendFunc(gl.ONE, gl.ONE);
  const off = g.s === 0 ? [0, 0] : [halton(g.s, 2) - 0.5, halton(g.s, 3) - 0.5];
  jobBegin();
  setScene(P, { w: W, h: H, off, px: W / Math.max(1, stage.clientWidth), nt: sceneDe(), steps: S.q.steps, normEps: S.q.smooth, ao: S.q.ao, shadow: S.q.shadow, sharp: S.q.normals === 'sharp' });
  gl.drawArrays(gl.TRIANGLES, 0, 3);
  gl.disable(gl.SCISSOR_TEST); gl.disable(gl.BLEND);
  fence({ kind: 'band', rows, frac: (g.s * H + g.y + rows) / (R.total * H) });
  say(g.s === 0 ? 'Drawing at full size' : `Refining: pass ${g.s + 1} of ${R.total}`);
  g.y += rows;
  if (g.y >= H) { g.y = 0; g.s++; if (g.s >= R.total) R.prog = null; }
}
// Once a picture is finished, prepare the programs the next click is most likely to need (the other approaches,
// the other form of the power, the Kleinian view, the equation presets), one at a time on the driver's own
// thread, so that those switches draw at once instead of waiting for a compile.
function sceneWarm() {
  clearTimeout(R.warmT); R.warmT = 0;
  if (!gl || lost || !R.par || !R.warmOn || !renderIdle()) return;
  if (R.warming) {
    if (R.warming.state === 'pending' && !progSettled(R.warming)) { R.warmT = setTimeout(sceneWarm, 100); return; }
    progFinish(R.warming); R.warming = null;
  }
  const n2 = Math.abs(S.n - 2) < 1e-9, a = ap(), list = [];
  const want = (...args) => { try { list.push(sceneWant(...args)); } catch (err) { /* a formula that does not compile is not warmed */ } };
  APPROACHES.forEach(x => want(x, S.eq, S.z0, n2, false));
  want(a, S.eq, S.z0, !n2, false);
  want(a, '', '', false, true);
  PRESETS.forEach(p => want(a, p.eq, p.z0, n2, false));
  const w = list.find(x => !progs.has(x.key));
  if (w) { R.warming = sceneEntry(w, true); R.warmT = setTimeout(sceneWarm, 100); }
}
// The scene point under a stage position (CSS pixels from the stage's top left corner), or null where there is none.
function pick(px, py) {
  const w = stage.clientWidth, h = stage.clientHeight;
  if (S.flat) {   // the 2D view maps the stage straight onto the slice, so no drawing is needed
    const s = S.v2.h / Math.max(1, h);
    return [S.v2.x + (px - w / 2) * s, S.v2.y + (h / 2 - py) * s, S.cut];
  }
  if (!gl || lost || !pickT) return null;
  const want = sceneNow(), P = want && progs.get(want.key);
  if (!P || P.state !== 'ready') return null;
  const out = new Float32Array(4);
  gl.bindFramebuffer(gl.FRAMEBUFFER, pickT.fbo); gl.viewport(0, 0, 1, 1); gl.disable(gl.SCISSOR_TEST); gl.disable(gl.BLEND);
  setScene(P, { w, h, off: [px - 0.5, h - py - 0.5], px: 1, nt: sceneDe(), steps: 300, normEps: 1, ao: false, shadow: false, sharp: false, pick: true });
  gl.drawArrays(gl.TRIANGLES, 0, 3);
  gl.readPixels(0, 0, 1, 1, gl.RGBA, gl.FLOAT, out);
  gl.bindFramebuffer(gl.FRAMEBUFFER, null);
  return out[3] > 0.5 ? [out[0], out[1], out[2]] : null;
}

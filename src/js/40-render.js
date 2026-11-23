// Rendering: WebGL set-up, scene programs, the progressive drawing loop, snapshots and background drawing.
const canvas = $('view'), stage = $('stage');
let gl = null, lost = false, floatOK = false, acc = null, prev = null, pickT = null, blitP = null;
const progs = new Map();   // scene programs by key, least recently used first
// Renderer state. Outside this file only 45-export.js reads it (R.gen); other files ask renderIdle().
const R = {
  pend: null,                // the preview or band the GPU is working on: { kind, sync, t0, q, flat | rows, frac, ... }
  pend2: null,               // a second band, queued on the GPU behind the first
  pipe: false,               // bands are cheap and timed by the GPU: two may be in flight
  quick: false,              // the first pass is short: it replaces the preview in one go, not band by band
  gain: 3, rowPrev: 0,       // cost of a full-size row over a preview row, learnt from each first pass; the preview row's cost
  p0: null,                  // the first pass under way: { ms, rows, row } GPU time and rows so far, and the preview row cost at its start
  wantPrev: false,           // a preview is due
  restart: false,            // a full-quality drawing is due once things have stopped moving
  prog: null,                // the full-quality drawing under way: { s: pass, y: next row }
  lastTouch: 0, raf: 0, tmr: 0, fast: 0,   // when touch() was last called; the loop's frame request and timers
  bg: false,                 // animation frames are paused (a background tab): the loop runs from its timer
  ps: 0.35, ps2: 1,          // preview size as a share of the full picture: ray-marched view, 2D view
  rows: 32,                  // rows in the next band
  rowMs: 0, rowExact: false, // cost of one full-size row, judged from the last preview; whether the GPU counted it
  pw: 2, ph: 2, total: 1,    // size of the last preview; passes in the full-quality drawing
  tq: null, q: null,         // EXT_disjoint_timer_query_webgl2 or null; the query now running
  dt: 16.7, lastLoop: 0,     // time between animation frames, smoothed; when a frame last ran the loop
  par: null,                 // KHR_parallel_shader_compile, or null
  shown: null,               // the target on screen: 'prev' the preview, 'acc' the full-size picture, or null
  painted: false,            // the canvas has shown a picture since the context was made
  sig: '', want: null,       // the settings the wanted program was worked out from; its key and source
  hold: 0, holdKey: '',      // frames waited before a compile that blocks (a driver without parallel compile)
  busy: false, busyP: null,  // the busy label is up for a compile; the program it waits to see a first picture from
  failed: '',                // why nothing can be drawn ('formula' | 'shader'), or ''
  bar: null,                 // the progress bar element
  warming: null, warmT: 0,   // preparing likely programs ahead of time: the one in hand, its timer
  gen: 0, f32: false,        // times the GL context has been set up; whether float pictures can be drawn and read back
  lostMid: false,            // the graphics went away while a picture was being drawn or was due (see renderIdle)
};

// Programs are compiled and linked without waiting. With KHR_parallel_shader_compile the driver works on another
// thread and COMPLETION_STATUS_KHR tells when it is done; any other question about the program makes the page wait.
function progStart(fsSrc) {
  const p = gl.createProgram(), vs = gl.createShader(gl.VERTEX_SHADER), fs = gl.createShader(gl.FRAGMENT_SHADER);
  gl.shaderSource(vs, VERT); gl.compileShader(vs);
  gl.shaderSource(fs, fsSrc); gl.compileShader(fs);
  gl.attachShader(p, vs); gl.attachShader(p, fs); gl.linkProgram(p);
  const cache = {};
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
// The scene program for one combination of approach, equation and colour needs: its cache key and how to write its
// source. A program holds only the colour code its settings use (see colProgramNeeds), and that is part of the key.
function sceneWant(a, eq, z0, n2, klein, needs = colProgramNeeds()) {
  const defs = glNeeds(needs, klein), tag = glNeedsKey(needs), keyOf = k => (tag ? k + '|' + tag : k);
  if (klein === 'balls') return { key: keyOf('balls'), src: () => GL_HEAD + defs + GL_COLOUR + GL_BALLS + GL_TAIL };
  if (klein === 'ballsSmall') return { key: keyOf('ballsSmall'), src: () => GL_HEAD + defs + GL_COLOUR + GL_BALLS_RHO + GL_TAIL };
  if (klein === 'ballsFree') return { key: keyOf('ballsFree'), src: () => GL_HEAD + defs + GL_COLOUR + GL_BALLS_FREE + GL_TAIL };
  if (klein) return { key: keyOf('klein'), src: () => GL_HEAD + defs + GL_COLOUR + GL_KLEIN + GL_TAIL };
  // An approach whose shader text changes (the custom one) says which text it is now with glslKey, and one that
  // writes the whole step of the orbit itself (whole) takes the place of the equation.
  const glsl = a.glsl, fc = a.whole || compileFormula(eq, true, n2), zc = compileFormula(z0, false, n2);
  return { key: keyOf([a.glslKey ? a.id + '#' + a.glslKey() : a.id, fc, zc].join('|')), src: () => GL_HEAD + defs + GL_COLOUR + glsl + GL_ORBIT.split('__F__').join(fc).split('__Z0__').join(zc) + GL_TAIL };
}
// Which Kleinian program the state asks for: false (not the Kleinian view), true (the first group), or for Balls on
// balls 'balls' (two equal spheres), 'ballsSmall' (a smaller second sphere) or 'ballsFree' (any other pair): see ballsKind.
const sceneKlein = () => (S.mode !== 'k' ? false : S.k.group === 1 ? ballsKind() : true);
const sceneBalls = kl => kl === 'balls' || kl === 'ballsSmall' || kl === 'ballsFree';
function sceneNow() {   // what the current settings need; remembered, because the drawing loop asks every frame
  const klein = sceneKlein(), n2 = Math.abs(S.n - 2) < 1e-9, needs = colProgramNeeds();
  const sig = (klein ? (klein === true ? 'k' : 'k-' + klein) : [S.approach, ap().glslKey ? ap().glslKey() : '', n2, S.eq, S.z0].join('\n')) + '\n' + glNeedsKey(needs);
  if (R.sig !== sig) {
    R.sig = sig; R.want = null;
    try { R.want = sceneWant(ap(), S.eq, S.z0, n2, klein, needs); } catch (err) { console.error('The formula could not be read: ' + err.message); }
  }
  return R.want;
}
function sceneEntry(w, start) {   // look a program up; with `start`, begin compiling it if it is new
  let e = progs.get(w.key);
  if (e) { progs.delete(w.key); progs.set(w.key, e); }
  else if (start) {
    e = progStart(w.src()); progs.set(w.key, e);
    // a program a snapshot draws from (pins > 0) stays, however long ago the screen last used it
    for (const [k, old] of progs) { if (progs.size <= 40) break; if (old.pins > 0) continue; progFree(old); progs.delete(k); }
  }
  return e || null;
}
// The program to draw with: a ready entry, 'wait' while it is being prepared, or why it cannot be built ('formula' / 'shader').
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
function makeTarget(w, h, f32, bytes) {   // bytes: 8 bits a channel whatever the device can do (a picture to be read back)
  const tex = gl.createTexture();
  gl.bindTexture(gl.TEXTURE_2D, tex);
  if (f32) gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA32F, w, h, 0, gl.RGBA, gl.FLOAT, null);
  else if (floatOK && !bytes) gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA16F, w, h, 0, gl.RGBA, gl.HALF_FLOAT, null);
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
  R.gen++; R.f32 = f32; BG.pbo = null; BG.pboSize = 0; BG.vol = null;   // what the old context held went with it
  progs.clear(); acc = prev = null; R.shown = null; R.painted = false; R.warming = null; R.holdKey = '';
  blitP = progFinish(progStart(BLIT));   // a few lines of shader: waiting for it is fine
  if (blitP.state !== 'ready') throw new Error('The display shader failed: ' + blitP.log);
  pickT = f32 ? makeTarget(1, 1, true) : null;
  if (pickT && !pickT.ok) pickT = null;
}
// The status line while the WebGL context is lost. touch() replaces the text when the context is restored.
const LOST_WORDS = 'The graphics of this page were interrupted. The picture comes back by itself.';
function initGL() {
  gl = canvas.getContext('webgl2', { antialias: false, alpha: false, powerPreference: 'high-performance' });
  if (!gl) { $('glfail').hidden = false; return; }
  const bar = document.createElement('div');
  bar.id = 'drawProgress'; bar.className = 'draw-progress'; bar.hidden = true;
  bar.setAttribute('aria-hidden', 'true');   // the status line under the stage says the same in words
  bar.appendChild(document.createElement('span'));
  stage.appendChild(bar); R.bar = bar;
  const setup = () => {
    try { setupGL(); return true; } catch (err) { console.error(err.message); gl = null; $('glfail').hidden = false; return false; }
  };
  if (!setup()) return;
  canvas.addEventListener('webglcontextlost', e => {
    e.preventDefault();
    R.lostMid = !renderIdle();   // asked before the drawing under way is dropped below
    lost = true; R.pend = R.pend2 = null; R.prog = null;
    stageProgress(null); bgPump();   // background pieces end here: their jobs are told the picture cannot be read
    busyOff();
    say(LOST_WORDS);
  });
  canvas.addEventListener('webglcontextrestored', () => { lost = false; R.lostMid = false; if (setup()) touch(); });
}
function stagePixels() {
  const dpr = Math.min(window.devicePixelRatio || 1, 2);
  const w = stage.clientWidth * dpr * S.q.res, h = stage.clientHeight * dpr * S.q.res, cap = Math.min(1, 3200 / Math.max(w, h));
  return [Math.max(2, Math.round(w * cap)), Math.max(2, Math.round(h * cap))];
}
function ensureTargets() {
  const [w, h] = stagePixels();
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
// An entry may cap the estimate (deMax): for some rules the finer estimates draw things that are not there.
function sceneDeCap() { return ap().deMax ?? 3; }
function sceneDe(q = S.q) { const d = Math.min(+q.de, sceneDeCap()); return d >= 3 ? 3 : d >= 1 ? 1 : 0; }
// Sets every uniform of the scene program. For a snapshot (see takeSnapshot) its frozen state and theme colours
// are put into S and theme for the length of the call, because the colour code and apVec() read S themselves.
function setScene(P, o, snap) {
  if (!snap) { sceneUniforms(P, o, basis()); return; }
  const liveS = snapSwap(S, snap.S), liveTheme = snapSwap(theme, snap.theme);
  try { sceneUniforms(P, o, snap.basis); } finally { snapSwap(S, liveS); snapSwap(theme, liveTheme); }
}
// o.slice { x, y, h, z } draws that flat slice whatever the state says (volume sampling); o.raw asks the shader for
// colour and distance instead of a picture.
function sceneUniforms(P, o, b) {
  gl.useProgram(P.p);
  const L = P.l, el = S.lightEl * PI / 180, az = S.lightAz * PI / 180, k = S.k, v = S.view, v2 = o.slice || { x: S.v2.x, y: S.v2.y, h: S.v2.h, z: S.cut };
  gl.uniform2f(L('uRes'), o.w, o.h); gl.uniform2f(L('uOff'), o.off[0], o.off[1]);
  gl.uniform3fv(L('uCamPos'), b.pos); gl.uniformMatrix3fv(L('uCam'), false, [...b.right, ...b.up, ...b.f]);
  gl.uniform1f(L('uFov'), v.fov); gl.uniform1f(L('uBound'), v.bound);
  gl.uniform1f(L('uPow'), S.n); gl.uniform4fv(L('uA'), apVec());
  if (ap().uniforms) ap().uniforms(gl, L);
  gl.uniform1f(L('uJulia'), S.mode === 'j' ? 1 : 0); gl.uniform3fv(L('uC'), S.c);
  gl.uniform1f(L('uMosaic'), S.mosaic && S.mode === 'm' ? S.mosaicCell : 0);
  gl.uniform3fv(L('uAbs'), S.abs); gl.uniform3f(L('uSgn'), 1, S.flip[0] ? -1 : 1, S.flip[1] ? -1 : 1);
  const kl = sceneKlein(), balls = sceneBalls(kl);   // Balls on balls: its own depth, and its two numbers (uBT, uBGrid)
  gl.uniform1f(L('uBail'), 64); gl.uniform1i(L('uIter'), balls ? k.bit : S.mode === 'k' ? k.iter : S.iter);
  // uBT is t as ballsTOf hands it over. Only 'ballsSmall' and 'ballsFree' have uBRho.
  if (balls) { gl.uniform1f(L('uBT'), ballsTOf(kl)); gl.uniform1i(L('uBGrid'), k.bgrid | 0); if (kl !== 'balls') gl.uniform1f(L('uBRho'), ballsRho()); }
  gl.uniform1f(L('uCut'), S.cutOn ? S.cut : 1e9);
  gl.uniform1f(L('uFlat'), S.flat || o.slice ? 1 : 0); gl.uniform2f(L('uFlatC'), v2.x, v2.y); gl.uniform1f(L('uFlatH'), v2.h); gl.uniform1f(L('uSliceZ'), v2.z);
  gl.uniform1f(L('uRaw'), o.raw ? 1 : 0);
  gl.uniform1f(L('uGrid'), S.view.grid && !o.raw && !o.pick && !o.slice ? 1 : 0);
  // Balls on balls: twice the steps, because its estimate is in places half the true distance.
  gl.uniform1i(L('uSteps'), balls && !o.raw ? 2 * o.steps : o.steps); gl.uniform1i(L('uNT'), o.nt);
  // The Kleinian distance estimate runs large away from a pearl, so its rays take at most half of it: at 0.8 small
  // pearls come out hollow or are skipped. The Balls on balls estimate is never longer than the true distance, so
  // its rays may take up to nine tenths of it.
  gl.uniform1f(L('uDetail'), S.q.detail); gl.uniform1f(L('uStepK'), balls ? Math.min(S.q.stepk, 0.9) : S.mode === 'k' ? Math.min(S.q.stepk, 0.5) : S.q.stepk); gl.uniform1f(L('uNormEps'), o.normEps);
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
// Before the first picture the canvas would show black: paint the stage colour as the display shader shows it.
function stageClear() {
  const c = lin(theme.stage).map(x => Math.pow(clamp(x / (1 + 0.12 * x) * 1.12, 0, 1), 0.4545));
  gl.bindFramebuffer(gl.FRAMEBUFFER, null); gl.disable(gl.SCISSOR_TEST);
  gl.clearColor(c[0], c[1], c[2], 1); gl.clear(gl.COLOR_BUFFER_BIT);
}
// The thin bar along the bottom of the stage. f: share of the full-quality drawing done, or null to hide it.
function stageProgress(f) {
  const el = R.bar;
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
      : 'This combination of approach and equation could not be prepared on this device. Try another approach or equation.';
    say('Nothing drawn: these settings could not be prepared');
    stageProgress(null);
  }
}

// Drawing schedule: a quick preview while anything moves; at rest a full-size picture drawn in bands, so the page
// never stalls, then refined by adding jittered passes.
let uiDirty = false;
const halton = (i, b) => { let f = 1, r = 0; while (i > 0) { f /= b; r += f * (i % b); i = Math.floor(i / b); } return r; };
function kick() { // next animation frame, or a timer if the page is in the background and frames are paused
  if (R.raf) return;
  R.raf = requestAnimationFrame(() => kicked(false, true)); R.tmr = setTimeout(() => kicked(true, true), 300);
  // A finished preview or band is looked for between frames, so that it is shown, and the next one started, at once.
  if (R.pend) R.fast = setTimeout(bandPoll, 3);
}
function kicked(bg, frame) { cancelAnimationFrame(R.raf); clearTimeout(R.tmr); clearTimeout(R.fast); R.raf = 0; R.bg = bg; loop(frame); }
function bandPoll() {
  if (!R.raf || !R.pend || !gl || lost) return;
  // a band may also be handed over while the one before it is being drawn
  if (gl.clientWaitSync(R.pend.sync, 0, 0) === gl.TIMEOUT_EXPIRED && !(R.pipe && R.prog && !R.pend2 && !R.wantPrev)) R.fast = setTimeout(bandPoll, 3);
  else kicked(R.bg, false);
}
function touch() {
  // The Learn tab draws its own picture on the stage. When it is left, it clears S.learn and calls touch().
  if (S.learn) { learnTouch(); return; }
  R.wantPrev = true; R.restart = true; R.prog = null; R.lastTouch = performance.now(); uiDirty = true; kick(); }
// Timing one preview or band. The wall clock also counts the wait for the next look and for whatever else uses
// the GPU. Where the driver has a timer its own count is used, so a busy GPU cannot shrink the bands without end.
function jobBegin() {
  if (!R.tq) return;
  if (R.q) { gl.endQuery(R.tq.TIME_ELAPSED_EXT); gl.deleteQuery(R.q); }   // left open by a drawing call that threw
  R.q = gl.createQuery(); gl.beginQuery(R.tq.TIME_ELAPSED_EXT, R.q);
}
function fence(job) {
  if (R.q) { gl.endQuery(R.tq.TIME_ELAPSED_EXT); job.q = R.q; R.q = null; }
  job.sync = gl.fenceSync(gl.SYNC_GPU_COMMANDS_COMPLETE, 0); job.t0 = performance.now(); gl.flush();
  if (R.pend) { job.behind = true; R.pend2 = job; } else R.pend = job;
}
function jobCost(job) {   // returns { ms, exact }: exact when ms is the GPU's own count
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
// How long one job should take, in milliseconds. A preview must be drawn and on the canvas within one frame. A
// band takes about half a frame: counted by the GPU two are kept in flight, timed by the clock one at a time.
const bandTarget = exact => (exact ? clamp(0.5 * R.dt, 6, 20) : 0.7 * R.dt + 4);
const prevTarget = exact => (exact ? clamp(0.55 * R.dt, 8, 20) : 0.55 * R.dt + 4);
// The fewest rows a band may have: a pass is never more than 32 bands. Below this the hand-over between bands
// costs more than the drawing, and a GPU left idle slows its clock, which makes the next band look slower.
const bandFloor = () => Math.max(2, canvas.height / 32);
function say(t) { const el = $('status'); if (el.textContent !== t) el.textContent = t; }
// true once nothing more will be drawn for the current settings: the finished picture is up, or its shader failed.
// false while the graphics are away in the middle of a picture: it is drawn again when they come back.
function renderIdle() { return !(lost && R.lostMid) && !R.restart && !R.prog && !R.pend && !R.wantPrev; }
// the view moved but the scene itself need not be redrawn: refresh overlays on the next frame
function viewChanged() { uiDirty = true; kick(); }
function busyOff() { if (R.busy) { R.busy = false; setBusy('compile', null); } }
function warmSoon(ms) { if (R.par) { clearTimeout(R.warmT); R.warmT = setTimeout(sceneWarm, ms); } }
function drawDone() {
  say(`Done: ${R.total} ${R.total === 1 ? 'pass' : 'passes'} at ${canvas.width} × ${canvas.height}`);
  stageProgress(null); warmSoon(500);
}
function jobDone(job, c) {
  const ms = c.ms;
  if (job.P === R.busyP) busyOff();   // a newly prepared program has drawn its first picture: until then the label stays up
  if (job.kind === 'prev') {
    blit(false);
    if (!R.bg) {
      // What a full-size row costs with the preview's settings, then with the finished picture's (R.gain times as much).
      R.rowPrev = ms / R.ph * (canvas.width / R.pw); R.rowMs = R.rowPrev * (job.flat ? 1 : R.gain); R.rowExact = c.exact;
      const k = Math.sqrt(prevTarget(c.exact) / ms);
      if (job.flat) R.ps2 = clamp(R.ps2 * clamp(k, 0.4, 1.25), 0.2, 1);
      else R.ps = clamp(R.ps * clamp(k, 0.4, 1.12), 0.12, 0.8);
    }
    return;
  }
  if (!R.bg && (c.exact || !job.behind)) {   // by the clock, a band that waited behind another was not timed
    R.rows = clamp(R.rows * clamp(bandTarget(c.exact) / ms, 0.6, 1.6), bandFloor(), 4096);
    R.pipe = c.exact && ms < 1.5 * bandTarget(true);
  }
  const p0 = R.p0;
  if (job.p0 && p0 && c.exact && !R.bg) {
    p0.ms += ms; p0.rows += job.rows;
    if (p0.rows >= canvas.height && p0.row > 0) { R.gain = clamp(R.gain + (p0.ms / p0.rows / p0.row - R.gain) * 0.6, 0.5, 12); R.p0 = null; }
  }
  if (R.wantPrev) return;   // the drawing this band belonged to has been dropped
  if (job.show) blit(true);
  if (R.prog || R.pend) stageProgress(job.frac);
  else drawDone();
  if (job.p0 && job.last) warmSoon(500);   // the first pass is up
}
function loop(frame) {
  R.raf = 0;
  if (frame) {
    const now = performance.now();
    if (!R.bg && now - R.lastLoop < 100) R.dt = clamp(R.dt + (now - R.lastLoop - R.dt) * 0.1, 4, 50);
    R.lastLoop = now;
  }
  if (uiDirty) { uiDirty = false; hooks.view.forEach(f => f()); }
  if (!gl || lost) return;
  if (R.pend && gl.clientWaitSync(R.pend.sync, 0, 0) !== gl.TIMEOUT_EXPIRED) {
    const job = R.pend;
    gl.deleteSync(job.sync); R.pend = R.pend2; R.pend2 = null;
    jobDone(job, jobCost(job));
  }
  const P = sceneAcquire();
  if (P === 'wait') {   // the last picture stays up while the driver prepares the new program
    const label = 'Preparing the formula';
    R.busyP = null;
    if (!R.busy) { R.busy = true; setBusy('compile', label); say(label); stageProgress(null); }
    else {
      // the corner label shows whichever task was raised last: keep this one in front while the picture waits for it
      const el = $('busy'), tx = el && el.querySelector('.busy-text');
      if (tx && tx.textContent !== label) { setBusy('compile', null); setBusy('compile', label); }
    }
    if (!R.painted) stageClear();
    return kick();
  }
  if (typeof P === 'string') { busyOff(); sceneFail(P); R.wantPrev = R.restart = false; R.prog = null; return; }
  sceneFail('');
  if (R.busy && !R.busyP) R.busyP = P;
  if (R.wantPrev) {
    if (R.pend) return kick();   // what is in flight finishes first
    ensureTargets();
    R.wantPrev = false; stageProgress(null); preview(P); return kick();
  }
  if (R.prog) {
    if (!R.pend || (R.pipe && !R.pend2)) band(P);
    return kick();
  }
  if (R.pend) return kick();   // the last bands of the picture are in flight
  if (R.restart) {
    ensureTargets();
    const W = canvas.width, H = canvas.height, first = R.rowMs * H;   // what the first pass will cost, judged from the preview
    // A picture that is quick to draw starts after two frames without a change. A slow one waits about as long as
    // its first pass takes, so that a pause in a drag does not start a drawing that is dropped again.
    const rest = clamp(first, Math.max(30, 2.2 * R.dt), 170) - (performance.now() - R.lastTouch);
    if (rest <= 0) {
      R.restart = false;
      R.total = floatOK ? Math.max(1, Math.round(S.q.aa)) : 1; R.prog = { s: 0, y: 0 };
      R.quick = first < 250; R.pipe = false;
      R.p0 = { ms: 0, rows: 0, row: R.rowExact && !S.flat ? R.rowPrev : 0 };
      if (R.bg) R.rows = Math.max(R.rows, H / 6);
      else if (R.rowMs > 0) R.rows = clamp(bandTarget(R.rowExact) / R.rowMs, bandFloor(), H);
      stageProgress(0);
      gl.disable(gl.SCISSOR_TEST);
      if (S.flat && R.shown === 'prev' && R.pw === W && R.ph === H) {
        // the 2D preview on screen is already full size and drawn with the final settings: it is the first pass
        gl.bindFramebuffer(gl.READ_FRAMEBUFFER, prev.fbo); gl.bindFramebuffer(gl.DRAW_FRAMEBUFFER, acc.fbo);
        gl.blitFramebuffer(0, 0, W, H, 0, 0, W, H, gl.COLOR_BUFFER_BIT, gl.NEAREST);
        gl.bindFramebuffer(gl.FRAMEBUFFER, null);
        R.prog.s = 1; R.p0 = null;
        blit(true);
        if (R.total === 1) { R.prog = null; busyOff(); drawDone(); return; }
        stageProgress(1 / R.total);
      } else {
        gl.bindFramebuffer(gl.FRAMEBUFFER, acc.fbo); gl.clearColor(0, 0, 0, 0); gl.clear(gl.COLOR_BUFFER_BIT);
      }
      band(P);
      return kick();
    }
    kick(); clearTimeout(R.fast);
    R.fast = setTimeout(() => { if (R.raf) kicked(R.bg, false); }, rest + 1);   // look again when the wait is over, not a frame later
    return;
  }
  busyOff();
}
function preview(P) {
  // the 2D view has no ray march, so its preview starts at full size and shrinks only if the device cannot keep up
  const flat = !!S.flat, ps = flat ? R.ps2 : R.ps;
  const w = Math.max(2, Math.round(canvas.width * ps)), h = Math.max(2, Math.round(canvas.height * ps));
  R.pw = w; R.ph = h;
  gl.bindFramebuffer(gl.FRAMEBUFFER, prev.fbo); gl.viewport(0, 0, w, h); gl.disable(gl.SCISSOR_TEST); gl.disable(gl.BLEND);
  jobBegin();
  const o = { w, h, off: [0, 0], px: w / Math.max(1, stage.clientWidth), nt: sceneDe(), sharp: S.q.normals === 'sharp' };
  // the 2D preview is drawn exactly like a first pass, so at full size it can be kept as one
  setScene(P, flat ? Object.assign(o, { steps: S.q.steps, normEps: S.q.smooth, ao: S.q.ao, shadow: S.q.shadow })
    // the ray-marched preview is lit like the finished picture, so the two do not differ in brightness
    : Object.assign(o, { steps: Math.min(S.q.steps, 120), normEps: 1.5, ao: S.q.ao, shadow: S.q.shadow }));
  gl.drawArrays(gl.TRIANGLES, 0, 3);
  fence({ kind: 'prev', flat, P });
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
  const p0 = g.s === 0, last = g.y + rows >= H;
  // a quick first pass is shown when it is whole, so the preview is not replaced strip by strip
  fence({ kind: 'band', P, rows, p0, last, show: !p0 || last || !R.quick, frac: (g.s * H + g.y + rows) / (R.total * H) });
  say(g.s === 0 ? 'Drawing at full size' : `Refining: pass ${g.s + 1} of ${R.total}`);
  g.y += rows;
  if (g.y >= H) { g.y = 0; g.s++; if (g.s >= R.total) R.prog = null; }
}
// Prepares the programs the next click is most likely to need, one at a time on the driver's own thread. It stands
// back while the picture moves and while a background job runs: a compile takes the GPU away from the job's pieces.
const bgJobBusy = () => !!BG.fly || BG.queue.length > 0 || exportBusy() || meshBusy();
function sceneWarm() {
  clearTimeout(R.warmT); R.warmT = 0;
  if (!gl || lost || !R.par || R.failed) return;
  if (bgJobBusy()) { R.warmT = setTimeout(sceneWarm, 500); return; }
  if (R.busy || R.wantPrev || (R.pend && R.pend.kind === 'prev') || (R.restart && !R.prog)) { R.warmT = setTimeout(sceneWarm, 500); return; }
  if (R.warming) {
    if (R.warming.state === 'pending' && !progSettled(R.warming)) { R.warmT = setTimeout(sceneWarm, 100); return; }
    progFinish(R.warming); R.warming = null;
  }
  const n2 = Math.abs(S.n - 2) < 1e-9, a = ap(), list = [];
  const want = (...args) => { try { list.push(sceneWant(...args)); } catch (err) { /* a formula that does not compile is not warmed */ } };
  // Balls on balls on show: its other two programs come first, so that moving a dial does not stop to prepare one.
  const kl = sceneKlein();
  if (sceneBalls(kl)) for (const other of ['ballsFree', 'ballsSmall', 'balls']) if (other !== kl) want(a, '', '', false, other);
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

// Snapshots and background drawing. A snapshot freezes everything a picture depends on, so that a background job
// draws the picture as it was. Its pieces share the screen's GL context, one at a time, and give way to the live picture.
const BG = {
  queue: [], fly: null,      // pieces waiting for their turn; the piece the GPU is working on
  next: 0,                   // while the live picture is busy: the earliest moment the next piece may start
  chan: null, armed: false,  // what wakes the queue: a message channel (a hidden tab does not slow it down) or a timer; one wake-up is on its way
  pbo: null, pboSize: 0,     // finished pixels are copied into this buffer on the GPU's side, so reading them never waits
  vol: null,                 // the float target that slices of a volume are drawn into
  late: [], lateT: 0, lateAt: 0,   // GPU timings to come in: { q, fn, t, gen }; the timer that looks for them; when they were last looked for
};
const SNAP_NONE = {};        // stands for "this key was not there" while values are swapped
function snapCopy(v) {
  if (Array.isArray(v)) return v.map(snapCopy);
  if (ArrayBuffer.isView(v)) return v.slice();
  if (v && typeof v === 'object') { const o = {}; for (const k of Object.keys(v)) o[k] = snapCopy(v[k]); return o; }
  return v;
}
// Put `vals` into `obj`, key by key, and return what was there, in a form that the same call puts back.
function snapSwap(obj, vals) {
  const was = {};
  for (const k of Object.keys(vals)) {
    was[k] = k in obj ? obj[k] : SNAP_NONE;
    if (vals[k] === SNAP_NONE) delete obj[k]; else obj[k] = vals[k];
  }
  return was;
}
// The picture as it is now: a deep copy of the state, the camera, the theme colours, the height on screen and the
// scene program, which is kept alive until releaseSnapshot. 45-export.js and 46-mesh.js read S, basis and stage,
// and 45-export.js adjusts its S for the size and quality of the picture. The other fields belong to this file.
function takeSnapshot() {
  const b = basis(), ph = stagePixels()[1];
  const snap = {
    S: snapCopy(S), theme: snapCopy(theme),
    basis: { pos: [...b.pos], right: [...b.right], up: [...b.up], f: [...b.f] },
    stage: { h: stage.clientHeight, ph },   // the picture on screen: its height in CSS pixels and in picture pixels
    want: null, P: null, gen: -1, live: true, vol: null,
    wantRaw: null, PR: null, genR: -1,   // the program volume samples are drawn with (see snapProg), made when first asked for
    pxMs: 0, pxGpu: 0, pxLast: 4096,   // sampling: what a point costs by the clock and by the GPU's count; the points in the last piece
  };
  try {
    const n2 = Math.abs(S.n - 2) < 1e-9, klein = sceneKlein();
    snap.want = sceneWant(ap(), S.eq, S.z0, n2, klein);
    snap.wantRaw = sceneWant(ap(), S.eq, S.z0, n2, klein, { ...colProgramNeeds(), raw: true });
  } catch (err) { /* the formula cannot be read: there is no picture, and sampling this snapshot gives null */ }
  snapProg(snap);
  return snap;
}
function releaseSnapshot(snap) {
  if (!snap || !snap.live) return;
  snap.live = false;
  if (snap.P && snap.gen === R.gen && snap.P.pins > 0) snap.P.pins--;
  if (snap.PR && snap.genR === R.gen && snap.PR.pins > 0) snap.PR.pins--;
  snap.P = snap.PR = null;
}
// The snapshot's program: an entry that is ready, 'wait' while the driver prepares it, or null when it cannot be had.
// raw: the program volume samples are drawn with (built with RAW_FIT, see glNeeds), started when first asked for.
function snapProg(snap, raw) {
  const w = raw ? 'wantRaw' : 'want', p = raw ? 'PR' : 'P', g = raw ? 'genR' : 'gen';
  if (!snap || !snap.live || !snap[w] || !gl || lost) return null;
  if (snap[g] !== R.gen) {   // first use, or the context was lost and made again: the old program went with it
    snap[p] = sceneEntry(snap[w], true); snap[p].pins = (snap[p].pins || 0) + 1; snap[g] = R.gen;
  }
  const e = snap[p];
  if (e.state === 'pending' && progSettled(e)) progFinish(e);
  return e.state === 'ready' ? e : e.state === 'pending' ? 'wait' : null;
}
async function snapReady(snap, raw) {
  for (;;) {
    const P = snapProg(snap, raw);
    if (P !== 'wait') return P;
    await new Promise(r => setTimeout(r, 30));
  }
}
const bgLiveBusy = () => !document.hidden && (!renderIdle() || performance.now() - R.lastTouch < 300);
// What one background piece should cost, in milliseconds: short, because a drag's first preview waits behind it.
const bgTarget = () => (bgLiveBusy() ? 5 : 12);
// One piece of background drawing. draw() issues the GL calls when the piece's turn has come. `read`, if given, is
// { x, y, w, h, into }: that rectangle of the framebuffer draw() leaves bound is copied into the typed array `into`
// (a Float32Array reads floats, anything else bytes). Resolves { ms }, or null when the context went away or draw()
// failed. ms is by the clock and includes waiting, so a job must not answer a slow piece with ever smaller pieces.
// The GPU's own count is the measure to size pieces by: it arrives a little later (on some devices never) in late(ms).
function bgPiece(draw, read, late) {
  return new Promise(done => { BG.queue.push({ draw, read, late, done, gen: R.gen }); bgPump(); });
}
function bgLate(now) {
  if (!BG.late.length || now - BG.lateAt < 6) return;
  BG.lateAt = now;
  if (!gl || lost) { BG.late.length = 0; return; }
  const torn = gl.getParameter(R.tq.GPU_DISJOINT_EXT);   // the GPU's clock was disturbed: what is pending cannot be trusted
  BG.late = BG.late.filter(e => {
    if (e.gen !== R.gen) return false;
    const ready = !torn && gl.getQueryParameter(e.q, gl.QUERY_RESULT_AVAILABLE);
    if (!ready && !torn && now - e.t < 2000) return true;
    const t = ready ? gl.getQueryParameter(e.q, gl.QUERY_RESULT) / 1e6 : 0;
    gl.deleteQuery(e.q);
    if (t > 0) e.fn(t);
    return false;
  });
  // after the last piece of a job nothing else comes by to collect what is pending
  if (BG.late.length && !BG.lateT) BG.lateT = setTimeout(() => { BG.lateT = 0; bgLate(performance.now()); }, 250);
}
// Look at the queue again in `ms` milliseconds. Only one wake-up is ever on its way.
function bgWake(ms) {
  if (BG.armed) return;
  BG.armed = true;
  if (ms > 0 && !document.hidden) { setTimeout(bgWoken, ms); return; }
  if (!BG.chan) { BG.chan = new MessageChannel(); BG.chan.port1.onmessage = bgWoken; }
  BG.chan.port2.postMessage(0);
}
function bgWoken() { BG.armed = false; bgPump(); }
function bgPump() {
  const now = performance.now(), dead = !gl || lost;
  let j = BG.fly;
  bgLate(now);
  if (j) {
    let c = null;
    if (!dead && j.gen === R.gen) {
      // Asked again at once for the first few milliseconds (most pieces are that short, and a timer would add four
      // more to each), then every two. A hidden tab slows timers to one a second, so there it is always at once.
      if (gl.clientWaitSync(j.sync, 0, 0) === gl.TIMEOUT_EXPIRED) { bgWake(now - j.t0 < 4 ? 0 : 2); return; }
      gl.deleteSync(j.sync);
      c = { ms: Math.max(0.1, now - j.t0) };
      if (j.q) BG.late.push({ q: j.q, fn: j.late, t: now, gen: j.gen });
      if (j.read) {
        gl.bindBuffer(gl.PIXEL_PACK_BUFFER, BG.pbo);
        gl.getBufferSubData(gl.PIXEL_PACK_BUFFER, 0, j.read.into);
        gl.bindBuffer(gl.PIXEL_PACK_BUFFER, null);
      }
      BG.next = now + 3 * c.ms;   // the live picture gets three times as long before the next piece
    }
    BG.fly = null; j.done(c);
  }
  while (BG.queue.length) {
    if (dead) { BG.queue.splice(0).forEach(x => x.done(null)); return; }
    if (bgLiveBusy() && BG.next - now > 0.5) { bgWake(BG.next - now); return; }
    j = BG.queue.shift();
    if (j.gen !== R.gen) { j.done(null); continue; }   // queued for a context that is gone
    let ok = true, q = null;
    if (j.late && R.tq && !R.q) { q = gl.createQuery(); gl.beginQuery(R.tq.TIME_ELAPSED_EXT, q); }
    try {
      j.draw();
      if (j.read) {
        const r = j.read, bytes = r.into.byteLength;
        gl.bindBuffer(gl.PIXEL_PACK_BUFFER, BG.pbo || (BG.pbo = gl.createBuffer()));
        if (BG.pboSize < bytes) { gl.bufferData(gl.PIXEL_PACK_BUFFER, bytes, gl.STREAM_READ); BG.pboSize = bytes; }
        gl.readPixels(r.x, r.y, r.w, r.h, gl.RGBA, r.into instanceof Float32Array ? gl.FLOAT : gl.UNSIGNED_BYTE, 0);
      }
    } catch (err) { ok = false; console.error('A background piece of drawing failed: ' + (err && err.stack || err)); }
    gl.bindBuffer(gl.PIXEL_PACK_BUFFER, null); gl.bindFramebuffer(gl.FRAMEBUFFER, null);
    gl.disable(gl.SCISSOR_TEST); gl.disable(gl.BLEND);
    if (q) gl.endQuery(R.tq.TIME_ELAPSED_EXT);
    if (!ok) { if (q) gl.deleteQuery(q); j.done(null); continue; }
    j.q = q; j.sync = gl.fenceSync(gl.SYNC_GPU_COMMANDS_COMPLETE, 0); j.t0 = performance.now(); gl.flush();
    BG.fly = j;
    bgWake(0);
    return;
  }
}
// Colour and distance over one level slice of the snapshot's scene: 4 * N * N numbers for the square of side
// `side` centred on (cx, cy) at height z, rows from the lowest y upward: r, g, b the surface colour (linear),
// a the signed distance estimate. null when the picture cannot be sampled.
async function sampleSlice(snap, cx, cy, side, z, N) {
  N = Math.round(N);
  if (!snap || !(N >= 1 && N <= 4096) || !isFinite(cx + cy + side + z)) return null;
  const out = new Float32Array(4 * N * N), slice = { x: cx, y: cy, h: side, z };
  // a volume is sampled as the 3D picture, whichever view the snapshot was taken in
  const frame = snap.vol || (snap.vol = { S: { ...snap.S, flat: false }, theme: snap.theme, basis: snap.basis });
  let y = 0;
  while (y < N) {
    const P = await snapReady(snap, true);
    if (!P || !R.f32) return null;
    // A piece is sized by what a point costs: by the GPU's count, else by the clock, which may not push a piece below
    // 16384 points (see bgPiece). It holds at most four times the points of the piece before; the first is small.
    const per = snap.pxGpu || snap.pxMs;
    const px = per > 0 ? Math.min(Math.max(bgTarget() / per, snap.pxGpu ? 1024 : 16384), 4 * snap.pxLast) : snap.pxLast;
    const rows = Math.min(N - y, Math.max(1, Math.round(px / N))), y0 = y;
    const c = await bgPiece(() => {
      if (!BG.vol || BG.vol.w < N) { freeTarget(BG.vol); BG.vol = makeTarget(Math.max(N, 256), Math.max(N, 256), true); }
      if (!BG.vol.ok) throw new Error('no float target');
      gl.bindFramebuffer(gl.FRAMEBUFFER, BG.vol.fbo); gl.viewport(0, 0, N, N);
      gl.enable(gl.SCISSOR_TEST); gl.scissor(0, y0, N, rows); gl.disable(gl.BLEND);
      // px: for a volume sample the shader wants the height of the snapshot's picture in page pixels, so that a
      // trap colour reads as many orbit steps as it does in that picture (see pagePix in main())
      setScene(P, { w: N, h: N, off: [0, 0], px: Math.max(1, snap.stage.h), nt: 3, steps: 1, normEps: 1, ao: false, shadow: false, sharp: false, raw: true, slice }, frame);
      gl.drawArrays(gl.TRIANGLES, 0, 3);
    }, { x: 0, y: y0, w: N, h: rows, into: out.subarray(4 * N * y0, 4 * N * (y0 + rows)) },
    ms => { const e = ms / (rows * N); snap.pxGpu = snap.pxGpu > 0 ? 0.5 * (snap.pxGpu + e) : e; });
    if (!c || !snap.live) return null;
    const each = c.ms / (rows * N);
    snap.pxMs = snap.pxMs > 0 ? 0.5 * (snap.pxMs + each) : each;
    snap.pxLast = Math.max(1024, rows * N); y += rows;
  }
  return out;
}

function kick() { // next animation frame, or a timer if the page is in the background and frames are paused
  if (R.raf) return;
  R.raf = requestAnimationFrame(() => kicked(false, true)); R.tmr = setTimeout(() => kicked(true, true), 300);
  // A finished preview or band need not wait for the next frame: it is looked for between frames, so a preview is on
  // the canvas in time for the next frame and the next band follows at once, which keeps the GPU busy.
  if (R.pend) R.fast = setTimeout(bandPoll, 3);
}
function kicked(bg, frame) { cancelAnimationFrame(R.raf); clearTimeout(R.tmr); clearTimeout(R.fast); R.raf = 0; R.bg = bg; loop(frame); }
function bandPoll() {
  if (!R.raf || !R.pend || !gl || lost) return;
  // a band may also be handed over while the one before it is still being drawn
  if (gl.clientWaitSync(R.pend.sync, 0, 0) === gl.TIMEOUT_EXPIRED && !(R.pipe && R.prog && !R.pend2 && !R.wantPrev)) R.fast = setTimeout(bandPoll, 3);
  else kicked(R.bg, false);
}
function touch() { R.wantPrev = true; R.restart = true; R.prog = null; R.lastTouch = performance.now(); uiDirty = true; kick(); }
// Timing one preview or band. The wall clock counts more than the drawing: the wait for the next look,
// and for whatever else is using the GPU. Where the driver has a timer, its own count of the drawing is used, so a
// busy GPU or a slow frame rate cannot talk the schedule into ever smaller bands.
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
// How long one job should take. A preview has to be drawn, noticed and put on the canvas within one frame, so that
// every frame of a drag shows a new picture. Bands take about half a frame each: counted by the GPU, two are kept in
// flight, so the GPU always has work and the page's own drawing waits for one band at most. Timed by the clock (which
// also counts the wait until the page looks again, a few milliseconds) there is one band at a time.
const bandTarget = exact => (exact ? clamp(0.5 * R.dt, 6, 20) : 0.7 * R.dt + 4);
const prevTarget = exact => (exact ? clamp(0.55 * R.dt, 8, 20) : 0.55 * R.dt + 4);
// The fewest rows a band may have. A band that looks slow must not be answered with ever smaller bands: below this the
// hand-over between bands costs more than the drawing, and a GPU that is left idle most of the time slows its clock
// down, which makes the next band look slower still. With this floor a pass is never more than 32 bands.
const bandFloor = () => Math.max(2, canvas.height / 32);
function say(t) { const el = $('status'); if (el.textContent !== t) el.textContent = t; }
// true once nothing more will be drawn for the current settings: the finished picture is up (or its shader failed)
function renderIdle() { return !R.restart && !R.prog && !R.pend && !R.wantPrev; }
// the view moved but the scene itself need not be redrawn: refresh overlays on the next frame
function viewChanged() { uiDirty = true; kick(); }
function busyOff() { if (R.busy) { R.busy = false; setBusy('compile', null); } }
function warmSoon(ms) { if (R.warmOn && R.par) { clearTimeout(R.warmT); R.warmT = setTimeout(sceneWarm, ms); } }
function drawDone() {
  say(`Done: ${R.total} ${R.total === 1 ? 'pass' : 'passes'} at ${canvas.width} × ${canvas.height}`);
  stageProgress(null); warmSoon(500);
}
// A preview or a band has come back from the GPU.
function jobDone(job, c) {
  const ms = c.ms;
  busyOff();   // a newly prepared program has now drawn its first picture: until then the label stays up
  if (job.kind === 'prev') {
    blit(false);
    if (!R.bg) {
      // What a full-size row costs with the preview's settings. Shadows, crevice shading and extra steps make a row of
      // the finished picture dearer by a factor that is learnt from each first pass (the 2D view draws the same thing).
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
  if (job.p0 && job.last) warmSoon(500);   // the first pass is up: start preparing the programs a next click may need
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
  if (R.wantPrev) {
    if (R.pend) return kick();   // what is in flight finishes first
    ensureTargets();
    R.wantPrev = false; stageProgress(null); preview(P); return kick();
  }
  if (R.prog) {
    if (!R.pend || (R.pipe && !R.pend2)) band(P);
    return kick();
  }
  if (R.pend) return kick();   // the last bands of the picture are still being drawn
  if (R.restart) {
    ensureTargets();
    const W = canvas.width, H = canvas.height, first = R.rowMs * H;   // what the first pass will cost, judged from the preview
    // A picture that is quick to draw starts almost at once. A slow one waits until things have been still for about
    // as long as its first pass takes, so that a pause in a drag does not start a drawing that is dropped again.
    if (performance.now() - R.lastTouch > clamp(first, 30, 170)) {
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
    }
    return kick();
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
    : Object.assign(o, { steps: Math.min(S.q.steps, 120), normEps: 1.5, ao: false, shadow: false }));
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
  const p0 = g.s === 0, last = g.y + rows >= H;
  // a quick first pass is shown when it is whole, so the preview is not replaced strip by strip
  fence({ kind: 'band', rows, p0, last, show: !p0 || last || !R.quick, frac: (g.s * H + g.y + rows) / (R.total * H) });
  say(g.s === 0 ? 'Drawing at full size' : `Refining: pass ${g.s + 1} of ${R.total}`);
  g.y += rows;
  if (g.y >= H) { g.y = 0; g.s++; if (g.s >= R.total) R.prog = null; }
}
// Prepare the programs the next click is most likely to need (the other approaches, the other form of the power,
// the Kleinian view, the equation presets), one at a time on the driver's own thread, so that those switches draw
// at once instead of waiting for a compile. It starts once the first pass of a picture is up and goes on while the
// picture is refined; it stands back while the picture is moving or its own program is still being prepared.
function sceneWarm() {
  clearTimeout(R.warmT); R.warmT = 0;
  if (!gl || lost || !R.par || !R.warmOn || R.failed) return;
  if (R.busy || R.wantPrev || (R.pend && R.pend.kind === 'prev') || (R.restart && !R.prog)) { R.warmT = setTimeout(sceneWarm, 500); return; }
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

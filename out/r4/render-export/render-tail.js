
// ---------- snapshots and background drawing
// A snapshot freezes everything a picture depends on, so that a background job (a picture to save, a 3D model) can
// go on drawing the picture as it was while the page moves on. Its drawing goes through the same GL context as the
// screen, in pieces: one at a time, each short, and no more than a quarter of the time while the live picture is busy.
const BG = {
  queue: [], fly: null,      // pieces waiting for their turn; the piece the GPU is working on
  next: 0,                   // while the live picture is busy: the earliest moment the next piece may start
  chan: null, armed: false,  // what wakes the queue: a message channel (a hidden tab does not slow it down) or a timer; one wake-up is on its way
  pbo: null, pboSize: 0,     // finished pixels are copied into this buffer on the GPU's side, so reading them never waits for the GPU
  vol: null,                 // the float target that slices of a volume are drawn into
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
// The picture as it is now: a deep copy of the state, the camera, the theme colours, the size on screen and the
// scene program (compiled if it is not yet, and kept alive until releaseSnapshot). Nothing the page does afterwards
// changes it. Treat it as opaque outside this file and 45-export.js.
function takeSnapshot() {
  const b = basis();
  const snap = {
    S: snapCopy(S), theme: snapCopy(theme),
    basis: { pos: [...b.pos], right: [...b.right], up: [...b.up], f: [...b.f] },
    stage: { w: stage.clientWidth, h: stage.clientHeight, pw: canvas.width, ph: canvas.height },   // CSS pixels; picture pixels
    want: null, P: null, gen: -1, live: true, vol: null, pxMs: 0,
  };
  try { snap.want = sceneWant(ap(), S.eq, S.z0, Math.abs(S.n - 2) < 1e-9, S.mode === 'k'); }
  catch (err) { /* the formula cannot be read: there is no picture, and sampling this snapshot gives null */ }
  snapProg(snap);
  return snap;
}
function releaseSnapshot(snap) {
  if (!snap || !snap.live) return;
  snap.live = false;
  if (snap.P && snap.gen === R.gen && snap.P.pins > 0) snap.P.pins--;
  snap.P = null;
}
// The snapshot's program: an entry that is ready, 'wait' while the driver prepares it, or null when it cannot be had.
function snapProg(snap) {
  if (!snap || !snap.live || !snap.want || !gl || lost) return null;
  if (snap.gen !== R.gen) {   // first use, or the context was lost and made again: the old program went with it
    snap.P = sceneEntry(snap.want, true); snap.P.pins = (snap.P.pins || 0) + 1; snap.gen = R.gen;
  }
  const e = snap.P;
  if (e.state === 'pending' && progSettled(e)) progFinish(e);
  return e.state === 'ready' ? e : e.state === 'pending' ? 'wait' : null;
}
async function snapReady(snap) {
  for (;;) {
    const P = snapProg(snap);
    if (P !== 'wait') return P;
    await new Promise(r => setTimeout(r, 30));
  }
}
// The live picture needs the GPU: something is moving, or its drawing is not finished. A hidden tab shows no picture.
const bgLiveBusy = () => !document.hidden && (!renderIdle() || performance.now() - R.lastTouch < 300);
// What one background piece should cost, in milliseconds. Short while the live picture is busy, so that its frames
// keep coming; never long, because a drag may begin at any moment and its first preview waits behind the piece.
const bgTarget = exact => (bgLiveBusy() ? (exact ? 4 : 10) : (exact ? 12 : 16));
// One piece of background drawing. draw() issues the GL calls when the piece's turn has come. `read`, if given, is
// { x, y, w, h, into }: that rectangle of the framebuffer draw() leaves bound is copied into the typed array `into`
// (a Float32Array reads floats, anything else bytes) once the GPU has finished. Resolves { ms, exact }, what the
// piece cost, or null when the GL context went away or draw() failed.
function bgPiece(draw, read) {
  return new Promise(done => { BG.queue.push({ draw, read, done, gen: R.gen }); bgPump(); });
}
// Look at the queue again in `ms` milliseconds. Only one wake-up is ever on its way, so that two jobs running side
// by side do not each keep a chain of them going.
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
  if (j) {
    let c = null;
    if (!dead && j.gen === R.gen) {
      if (gl.clientWaitSync(j.sync, 0, 0) === gl.TIMEOUT_EXPIRED) {
        // In a hidden tab no frame is waiting, so the page may as well block until the GPU is done as ask again and again.
        if (document.hidden && !j.blocked && now - j.t0 > 4) { j.blocked = true; gl.finish(); }
        bgWake(now - j.t0 < 4 ? 0 : 2);
        return;
      }
      gl.deleteSync(j.sync);
      c = { ms: Math.max(1, now - j.t0), exact: false };
      if (j.q) {
        if (!gl.getParameter(R.tq.GPU_DISJOINT_EXT) && gl.getQueryParameter(j.q, gl.QUERY_RESULT_AVAILABLE)) {
          const t = gl.getQueryParameter(j.q, gl.QUERY_RESULT) / 1e6;
          if (t > 0.02 && t < c.ms + 1) { c.ms = t; c.exact = true; }
        }
        gl.deleteQuery(j.q);
      }
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
    let q = null, ok = true;
    if (R.tq && !R.q) { q = gl.createQuery(); gl.beginQuery(R.tq.TIME_ELAPSED_EXT, q); }
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
// Colour and distance over one level slice of the snapshot's scene (see docs/CONTRACT4.md): 4 * N * N numbers for
// the square of side `side` centred on (cx, cy) at height z, rows from the lowest y upward: r, g, b the surface
// colour (linear), a the signed distance estimate. null when the picture cannot be sampled.
async function sampleSlice(snap, cx, cy, side, z, N) {
  N = Math.round(N);
  if (!snap || !(N >= 1 && N <= 4096) || !isFinite(cx + cy + side + z)) return null;
  const out = new Float32Array(4 * N * N), slice = { x: cx, y: cy, h: side, z };
  // a volume is sampled as the 3D picture, whichever view the snapshot was taken in
  const frame = snap.vol || (snap.vol = { S: { ...snap.S, flat: false }, theme: snap.theme, basis: snap.basis });
  let y = 0, last = 4096;   // pixels in the piece before this one: the first is small, to learn what a pixel costs
  while (y < N) {
    const P = await snapReady(snap);
    if (!P || !R.f32) return null;
    const px = snap.pxMs > 0 ? Math.min(bgTarget(!!R.tq) / snap.pxMs, 4 * last) : last;
    const rows = Math.min(N - y, Math.max(1, Math.round(px / N))), y0 = y;
    const c = await bgPiece(() => {
      if (!BG.vol || BG.vol.w < N) { freeTarget(BG.vol); BG.vol = makeTarget(Math.max(N, 256), Math.max(N, 256), true); }
      if (!BG.vol.ok) throw new Error('no float target');
      gl.bindFramebuffer(gl.FRAMEBUFFER, BG.vol.fbo); gl.viewport(0, 0, N, N);
      gl.enable(gl.SCISSOR_TEST); gl.scissor(0, y0, N, rows); gl.disable(gl.BLEND);
      setScene(P, { w: N, h: N, off: [0, 0], px: 1, nt: 3, steps: 1, normEps: 1, ao: false, shadow: false, sharp: false, raw: true, slice }, frame);
      gl.drawArrays(gl.TRIANGLES, 0, 3);
    }, { x: 0, y: y0, w: N, h: rows, into: out.subarray(4 * N * y0, 4 * N * (y0 + rows)) });
    if (!c || !snap.live) return null;
    const each = c.ms / (rows * N);
    snap.pxMs = snap.pxMs > 0 ? 0.5 * (snap.pxMs + each) : each;
    last = rows * N; y += rows;
  }
  return out;
}

import io
p='src/js/40-render.js'
s=io.open(p,encoding='utf-8').read()
def rep(a,b):
    global s
    assert s.count(a)==1,(a,s.count(a))
    s=s.replace(a,b)
rep("""  vol: null,                 // the float target that slices of a volume are drawn into
};""","""  vol: null,                 // the float target that slices of a volume are drawn into
  late: [], lateT: 0, lateAt: 0,   // GPU timings still to come in: { q, fn, t, gen }; the timer that looks for them; when they were last looked for
};""")
rep("""// (a Float32Array reads floats, anything else bytes) once the GPU has finished. Resolves { ms }, or null when the GL
// context went away or draw() failed. ms is the time from handing the piece over until it was seen to be done. The
// GPU's own count would be better, but it only arrives with the next frame, which is too late to size the next piece
// by and never comes in a hidden tab. The clock errs on the long side (it also counts waiting behind the live
// picture's drawing), so pieces sized by it come out too short when in doubt, never too long.
function bgPiece(draw, read) {
  return new Promise(done => { BG.queue.push({ draw, read, done, gen: R.gen }); bgPump(); });
}""","""// (a Float32Array reads floats, anything else bytes) once the GPU has finished. Resolves { ms }, or null when the GL
// context went away or draw() failed. ms is the time by the clock from handing the piece over until it was seen to
// be done. That counts more than the drawing: waiting behind the live picture, and behind whatever else is using
// the GPU, which can be several milliseconds for a piece of any size. So a job must not answer a slow piece with
// ever smaller pieces. The GPU's own count is the measure to size pieces by; it arrives a little after the piece
// (and not at all on some devices), and is then handed to late(ms).
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
  // after the last piece of a job nothing else comes by to collect what is still pending
  if (BG.late.length && !BG.lateT) BG.lateT = setTimeout(() => { BG.lateT = 0; bgLate(performance.now()); }, 250);
}""")
rep("""function bgPump() {
  const now = performance.now(), dead = !gl || lost;
  let j = BG.fly;""","""function bgPump() {
  const now = performance.now(), dead = !gl || lost;
  let j = BG.fly;
  bgLate(now);""")
rep("""      c = { ms: Math.max(0.1, now - j.t0) };
      R.bgN++; R.bgMs += c.ms;
""","""      c = { ms: Math.max(0.1, now - j.t0) };
      R.bgN++; R.bgMs += c.ms;
      if (j.q) BG.late.push({ q: j.q, fn: j.late, t: now, gen: j.gen });
""")
rep("""    let ok = true;
    try {""","""    let ok = true, q = null;
    if (j.late && R.tq && !R.q) { q = gl.createQuery(); gl.beginQuery(R.tq.TIME_ELAPSED_EXT, q); }
    try {""")
rep("""    if (!ok) { j.done(null); continue; }
    j.sync = gl.fenceSync""","""    if (q) gl.endQuery(R.tq.TIME_ELAPSED_EXT);
    if (!ok) { if (q) gl.deleteQuery(q); j.done(null); continue; }
    j.q = q; j.sync = gl.fenceSync""")
rep("""    pxMs: 0, pxLast: 4096,   // sampling: what a point costs, and the points in the last piece (the first is small, to learn the cost)""",
"""    pxMs: 0, pxGpu: 0, pxLast: 4096,   // sampling: what a point costs by the clock and by the GPU's count; the points in the last piece""")
rep("""    // a piece may hold four times the points of the one before, in case the points have become dearer
    const px = snap.pxMs > 0 ? Math.min(bgTarget() / snap.pxMs, 4 * snap.pxLast) : snap.pxLast;""","""    // A piece is sized by what a point costs: by the GPU's count where there is one, else by the clock, which is
    // not allowed to push a piece below 16384 points (see bgPiece). It may hold four times the points of the piece
    // before, in case the points have become dearer. The very first is small, to learn the cost.
    const per = snap.pxGpu || snap.pxMs;
    const px = per > 0 ? Math.min(Math.max(bgTarget() / per, snap.pxGpu ? 1024 : 16384), 4 * snap.pxLast) : snap.pxLast;""")
rep("""    }, { x: 0, y: y0, w: N, h: rows, into: out.subarray(4 * N * y0, 4 * N * (y0 + rows)) });""","""    }, { x: 0, y: y0, w: N, h: rows, into: out.subarray(4 * N * y0, 4 * N * (y0 + rows)) },
    ms => { const e = ms / (rows * N); snap.pxGpu = snap.pxGpu > 0 ? 0.5 * (snap.pxGpu + e) : e; });""")
io.open(p,'w',encoding='utf-8',newline='\n').write(s)

p='src/js/45-export.js'
s=io.open(p,encoding='utf-8').read()
i0=s.index("        // What one pixel of this tile costs is not known until it has been drawn once")
i1=s.index("        // the finished tile: the same tone curve as the screen")
new = """        // What a pixel of this tile costs is not known until it has been drawn once, and it can be a hundred times
        // what the tile before cost. So the first pass feels its way: a few rows, then at most four times as many
        // as the piece before. The cost is taken from the GPU's own count where it arrives (the dearest piece counts
        // for a part of the tile, the average for whole passes), else from the clock, which is not allowed to push a
        // piece below a sixteenth of the tile (see bgPiece in 40-render.js).
        const est = { wall: 0, gMax: 0, gMs: 0, gPx: 0 };
        let s = 0, y = 0, rowsWas = Math.max(1, Math.round(4096 / tw)), clear = true;
        while (s < passes) {
          const target = bgTarget(), first = clear, part = est.gMax || est.wall;
          const fit = part > 0 ? target / (part * tw) : rowsWas;   // rows that fit the target
          let rows = th - y, many = 1;
          if (s === 0) rows = Math.min(rows, clamp(Math.round(fit), Math.min(8, rowsWas), 4 * rowsWas));
          else {
            const whole = est.gPx >= tw * th ? target / (est.gMs / est.gPx * tw * th) : fit / th;   // passes that fit
            if (y === 0 && whole >= 1) many = clamp(Math.floor(whole), 1, Math.min(passes - s, 16));
            else rows = Math.min(rows, Math.max(Math.round(fit), est.gMax ? 1 : Math.ceil(th / 16)));
          }
          const s0 = s, ya = y, px = rows * tw * many;
          const c = check(await bgPiece(() => {
            if (R.gen !== gen) throw new Error('the GL context changed');
            gl.bindFramebuffer(gl.FRAMEBUFFER, acc.fbo); gl.viewport(0, 0, tw, th);
            gl.disable(gl.SCISSOR_TEST); gl.disable(gl.BLEND);
            if (first) { gl.clearColor(0, 0, 0, 0); gl.clear(gl.COLOR_BUFFER_BIT); }
            gl.enable(gl.SCISSOR_TEST); gl.scissor(0, ya, tw, rows);
            gl.enable(gl.BLEND); gl.blendFunc(gl.ONE, gl.ONE);
            for (let i = 0; i < many; i++) {
              const p = s0 + i, jx = p === 0 ? 0 : halton(p, 2) - 0.5, jy = p === 0 ? 0 : halton(p, 3) - 0.5;
              if (i === 0) setScene(P, Object.assign(o, { off: [x0 + jx, y0 + jy] }), snap);
              else gl.uniform2f(P.l('uOff'), x0 + jx, y0 + jy);
              gl.drawArrays(gl.TRIANGLES, 0, 3);
            }
          }, null, ms => { est.gMax = Math.max(est.gMax, ms / px); est.gMs += ms; est.gPx += px; }));
          clear = false;
          est.wall = est.wall > 0 ? 0.5 * (est.wall + c.ms / px) : c.ms / px;
          if (s === 0) rowsWas = rows;
          went(px);
          y += rows;
          if (y >= th) { y = 0; s += many; }
        }
"""
s=s[:i0]+new+s[i1:]
io.open(p,'w',encoding='utf-8',newline='\n').write(s)
print('ok')

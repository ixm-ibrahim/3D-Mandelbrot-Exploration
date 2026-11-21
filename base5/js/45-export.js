// ---------- "Save a picture": a background job that draws the picture as it was when Start was pressed, at a
// chosen size and quality, and hands it over as a file.
// The job works from its own snapshot (takeSnapshot in 40-render.js), so nothing done on the page afterwards
// changes it. The picture is drawn tile by tile through the renderer's background queue (bgPiece), which keeps the
// pieces short and gives way to the live picture. Finished tiles go straight into a 2D canvas, so the size of the
// picture is not held to what one GL target can be, and that canvas is what gets written as PNG, JPG or WebP.
const EXPORT_TILE = 512;      // tiles are this many pixels square
const EXPORT_MAX = 1e8;       // pixels in all: three times an 8K picture. Beyond it a browser may run out of memory instead of saying no.
const EXPORT_SIZES = [
  ['screen', 'As on screen'], ['x2', 'Twice the size on screen'], ['x4', 'Four times the size on screen'],
  ['1920x1080', '1920 × 1080 (Full HD)'], ['2560x1440', '2560 × 1440'], ['3840x2160', '3840 × 2160 (4K)'], ['7680x4320', '7680 × 4320 (8K)'],
  ['2048x2048', 'Square, 2048 × 2048'], ['4096x4096', 'Square, 4096 × 4096'], ['typed', 'Typed width and height'],
];
// What "Fine" and "Extra fine" put in place of the quality settings on screen. Fine is the page's own Fine preset.
const EXPORT_QUALITY = {
  fine: { aa: 32, steps: 450, detail: 0.7, stepk: 0.8, smooth: 1, shadow: true, ao: true, de: 3, normals: 'sharp' },
  extra: { aa: 64, steps: 900, detail: 0.5, stepk: 0.8, smooth: 1, shadow: true, ao: true, de: 3, normals: 'sharp' },
};
const EXPORT_KINDS = { png: ['image/png', 'PNG'], jpg: ['image/jpeg', 'JPG'], webp: ['image/webp', 'WebP'] };
const EXPORT_NAMES = { m: 'mandelbrot', j: 'julia', k: 'kleinian' };
const EXPORT_WORDS = {
  cancel: 'The picture was cancelled.',
  none: 'A picture cannot be drawn just now, because the graphics of this page are not running.',
  formula: 'These settings cannot be drawn, so there is no picture to save.',
  lost: 'The graphics of this page were interrupted, so the picture could not be finished. Start it again.',
  encode: 'The finished picture could not be written as a file. Try another file type or a smaller size.',
  failed: 'The picture could not be made. Try again, or choose a smaller size.',
};
const EXPORT = {
  opt: { size: 'x2', w: 1920, h: 1080, quality: 'fine', kind: 'png' },
  job: null,                  // the job that is running
  result: null,               // the finished picture: { name, blob, facts, note }
  ui: null,
};
function exportBusy() { return !!EXPORT.job; }
function exportStop(code) { const e = new Error(code); e.exportCode = code; return e; }
function exportBytes(n) { return n >= 1048576 ? (n / 1048576).toFixed(n >= 10485760 ? 0 : 1) + ' MB' : Math.max(1, Math.round(n / 1024)) + ' kB'; }
function exportTime(ms) { const s = ms / 1000; return s < 1.5 ? 'about a second' : s < 90 ? Math.round(s) + ' seconds' : s < 5400 ? Math.round(s / 60) + ' minutes' : (s / 3600).toFixed(1) + ' hours'; }
// The size in pixels a choice of size stands for. st: the picture on screen, { pw, ph } in pixels.
function exportDims(o, st) {
  const fit = v => clamp(Math.round(v) || 0, 16, 16384);
  if (o.size === 'typed') return [fit(o.w), fit(o.h)];
  const m = /^(\d+)x(\d+)$/.exec(o.size);
  if (m) return [+m[1], +m[2]];
  const k = o.size === 'x4' ? 4 : o.size === 'x2' ? 2 : 1;
  return [fit(st.pw * k), fit(st.ph * k)];
}
// A 2D canvas of that size, or null where the browser cannot make one. A canvas that is too large does not fail
// loudly: it just stays empty, so one pixel in the far corner is drawn and read back.
function exportCanvas(W, H) {
  try {
    const cv = document.createElement('canvas');
    cv.width = W; cv.height = H;
    // kept in ordinary memory: it is filled tile by tile and read once, and a picture this large need not sit on the GPU as well
    const ctx = cv.getContext('2d', { willReadFrequently: true });
    if (!ctx || cv.width !== W || cv.height !== H) return null;
    ctx.fillStyle = '#fff'; ctx.fillRect(W - 1, H - 1, 1, 1);
    if (ctx.getImageData(W - 1, H - 1, 1, 1).data[3] !== 255) return null;
    ctx.clearRect(W - 1, H - 1, 1, 1);
    return { cv, ctx };
  } catch (err) { return null; }
}

// ---------- the job
async function exportRun(job) {
  const { snap, W, H } = job, T = EXPORT_TILE, q = snap.S.q;
  const check = c => { if (job.cancel) throw exportStop('cancel'); if (c === null) throw exportStop('lost'); return c; };
  job.step = 'Preparing the formula'; exportPaint();
  const P = await snapReady(snap);
  check();
  if (!P) throw exportStop(!gl || lost ? 'lost' : 'formula');
  const gen = R.gen, passes = floatOK ? Math.max(1, Math.round(q.aa)) : 1;
  // The hatching of a cut face repeats every 8 * uPx pixels, counted from each tile's own corner. A period that
  // divides the tile keeps the lines unbroken from tile to tile (it changes their spacing by a few percent at most).
  const px = T / (8 * Math.max(1, Math.round(T / (8 * Math.max(H / Math.max(1, snap.stage.h), 1e-3)))));
  const o = { w: W, h: H, off: [0, 0], px, nt: sceneDe(q), steps: q.steps, normEps: q.smooth, ao: q.ao, shadow: q.shadow, sharp: q.normals === 'sharp' };
  const acc = makeTarget(T, T, false), out = makeTarget(T, T, false, true);
  const bytes = new Uint8Array(4 * T * T), total = W * H * passes;
  let done = 0;
  const went = (n, c) => {   // n pixel-passes have been drawn
    done += n; job.frac = 0.97 * done / total;
    const el = performance.now() - job.t0;
    if (done > 0.02 * total || el > 3000) job.left = el * (total - done) / done;
    exportPaint();
    return c;
  };
  job.step = 'Drawing the picture';
  try {
    if (!acc.ok || !out.ok) throw exportStop('failed');
    for (let y0 = (Math.ceil(H / T) - 1) * T; y0 >= 0; y0 -= T) {   // rows of tiles from the top of the picture down
      for (let x0 = 0; x0 < W; x0 += T) {
        const tw = Math.min(T, W - x0), th = Math.min(T, H - y0);
        // What a pixel of this tile costs is not known until it has been drawn once, and it can be a hundred times
        // what the tile before cost. So the first pass feels its way: a few rows, then at most four times as many
        // as the piece before. The cost is taken from the GPU's own count where it arrives (for a part of the tile
        // the dearest piece of the first pass counts, for whole passes the average), else from the clock. Neither is
        // allowed to push a piece below a sixteenth of the tile: one slow reading, with the GPU busy elsewhere, must
        // not turn the rest of the tile into single rows (see bgPiece in 40-render.js).
        const est = { wall: 0, g0: 0, gMs: 0, gPx: 0 };
        let s = 0, y = 0, rowsWas = Math.max(1, Math.round(4096 / tw)), clear = true;
        while (s < passes) {
          const target = bgTarget(), first = clear, part = est.g0 || est.wall;
          const fit = part > 0 ? target / (part * tw) : rowsWas;   // rows that fit the target
          let rows = th - y, many = 1;
          if (s === 0) rows = Math.min(rows, clamp(Math.round(fit), Math.min(8, rowsWas), 4 * rowsWas));
          else {
            const whole = est.gPx >= tw * th ? target / (est.gMs / est.gPx * tw * th) : fit / th;   // passes that fit
            if (y === 0 && whole >= 1) many = clamp(Math.floor(whole), 1, Math.min(passes - s, 16));
            else rows = Math.min(rows, Math.max(Math.round(fit), Math.ceil(th / 16)));
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
          }, null, ms => { if (s0 === 0) est.g0 = Math.max(est.g0, ms / px); est.gMs += ms; est.gPx += px; }));
          clear = false;
          est.wall = est.wall > 0 ? 0.5 * (est.wall + c.ms / px) : c.ms / px;
          if (s === 0) rowsWas = rows;
          went(px);
          y += rows;
          if (y >= th) { y = 0; s += many; }
        }
        // the finished tile: the same tone curve as the screen (the display shader), then into the 2D canvas
        const part = bytes.subarray(0, 4 * tw * th);
        check(await bgPiece(() => {
          if (R.gen !== gen) throw new Error('the GL context changed');
          gl.bindFramebuffer(gl.FRAMEBUFFER, out.fbo); gl.viewport(0, 0, tw, th);
          gl.disable(gl.SCISSOR_TEST); gl.disable(gl.BLEND);
          gl.useProgram(blitP.p);
          gl.activeTexture(gl.TEXTURE0); gl.bindTexture(gl.TEXTURE_2D, acc.tex);
          gl.uniform1i(blitP.l('uAcc'), 0); gl.uniform1i(blitP.l('uPrev'), 0);
          gl.uniform2f(blitP.l('uSize'), T, T);
          gl.uniform2f(blitP.l('uPrevScale'), 1, 1); gl.uniform2f(blitP.l('uPrevMax'), 1, 1);
          gl.uniform1f(blitP.l('uUseAcc'), 1);
          gl.drawArrays(gl.TRIANGLES, 0, 3);
        }, { x: 0, y: 0, w: tw, h: th, into: part }));
        const img = job.big.ctx.createImageData(tw, th);
        for (let r = 0; r < th; r++) img.data.set(part.subarray(4 * tw * (th - 1 - r), 4 * tw * (th - r)), 4 * tw * r);   // GL rows run upward
        job.big.ctx.putImageData(img, x0, H - y0 - th);
      }
    }
  } finally {
    if (gl && !lost && R.gen === gen) { freeTarget(acc); freeTarget(out); }
  }
  const [mime, word] = EXPORT_KINDS[job.o.kind] || EXPORT_KINDS.png;
  job.step = `Writing the ${word} file`; job.frac = 0.97; job.left = 0; exportPaint();
  const blob = await new Promise(res => { try { job.big.cv.toBlob(res, mime, 0.93); } catch (err) { res(null); } });
  check();
  if (!blob) throw exportStop('encode');
  // a browser that cannot write the chosen type hands back a PNG instead
  const got = Object.keys(EXPORT_KINDS).find(k => EXPORT_KINDS[k][0] === blob.type) || 'png';
  const u = EXPORT.ui, k = Math.min(1, 480 / W, 360 / H);
  u.preview.width = Math.max(1, Math.round(W * k)); u.preview.height = Math.max(1, Math.round(H * k));
  const pc = u.preview.getContext('2d');
  pc.imageSmoothingQuality = 'high';
  pc.drawImage(job.big.cv, 0, 0, u.preview.width, u.preview.height);
  job.big.cv.width = job.big.cv.height = 0;   // the large canvas has done its work: let its memory go
  const name = `squaring-lab-${EXPORT_NAMES[snap.S.mode] || 'picture'}-${W}x${H}.${got}`;
  return {
    name, blob,
    facts: [['Size', `${W} × ${H} pixels`], ['File', name], ['File size', exportBytes(blob.size)], ['Time taken', exportTime(performance.now() - job.t0)]],
    note: got !== job.o.kind ? `This browser cannot write ${word} files, so the picture is a ${EXPORT_KINDS[got][1]} file.` : '',
  };
}
async function exportStart() {
  if (EXPORT.job || EXPORT.result) return;
  if (!gl || lost) { exportSay(EXPORT_WORDS.none); return; }
  const o = { ...EXPORT.opt }, [pw, ph] = stagePixels(), [W, H] = exportDims(o, { pw, ph });
  const big = W * H <= EXPORT_MAX ? exportCanvas(W, H) : null;
  if (!big) {
    exportSay(`This browser cannot hold a picture of ${W} × ${H} pixels. Choose a smaller size.`);
    return;
  }
  const snap = takeSnapshot();
  // The job's quality settings stand in for the ones on screen, in its own copy of the state. "As on screen now"
  // also keeps the surface exactly where the screen has it: the surface threshold is counted in pixels, so it is
  // scaled with the picture, and the result is the same picture, only larger. Fine and Extra fine count it in the
  // new picture's own pixels, which brings out finer detail at larger sizes.
  const scale = H / Math.max(1, snap.stage.ph);
  if (EXPORT_QUALITY[o.quality]) Object.assign(snap.S.q, EXPORT_QUALITY[o.quality]);
  else snap.S.q.detail *= scale;
  // the outline of the 2D view and the glow beside it are widths in pixels: they keep their weight in the larger picture
  for (const key of ['edge', 'edgeGlow']) if (typeof snap.S.colour[key] === 'number') snap.S.colour[key] *= scale;
  const job = EXPORT.job = { o, snap, W, H, big, cancel: false, step: 'Starting', frac: 0, left: 0, t0: performance.now(), painted: 0 };
  exportSay(''); exportShow(true);
  try {
    EXPORT.result = await exportRun(job);
    exportSay(EXPORT.result.note || 'The picture is ready.');
  } catch (err) {
    if (!err || !err.exportCode) console.error('The picture could not be made: ' + (err && err.stack || err));
    big.cv.width = big.cv.height = 0;
    exportSay(EXPORT_WORDS[err && err.exportCode] || EXPORT_WORDS.failed);
  } finally {
    releaseSnapshot(snap);
    EXPORT.job = null;
    exportShow(true);
  }
}
async function exportSave() {
  const r = EXPORT.result;
  if (!r || r.saving) return;
  r.saving = true;
  const out = await saveFile(r.name, r.blob);
  r.saving = false;
  if (EXPORT.result === r) exportSay(out.ok ? `Saved as ${r.name}. You can save it again, or discard it to make another picture.` : `${out.message} The picture is still here, so you can try again.`);
}

// ---------- the panel
function exportSay(text) { const u = EXPORT.ui; if (u && u.msg.textContent !== text) u.msg.textContent = text; }
function exportPaint(force) {   // the progress of the running job; the words change a few times a second at most
  const u = EXPORT.ui, job = EXPORT.job, now = performance.now();
  if (!u || !job || (!force && now - job.painted < 120 && job.stepShown === job.step)) return;
  job.painted = now; job.stepShown = job.step;
  const pc = Math.floor(100 * clamp(job.frac, 0, 1)), s = job.left / 1000;
  u.fill.style.transform = `scaleX(${(pc / 100).toFixed(2)})`;
  u.bar.setAttribute('aria-valuenow', pc);
  const left = s < 3 ? '' : s < 90 ? ` About ${Math.round(s)} seconds left.` : s < 5400 ? ` About ${Math.round(s / 60)} minutes left.` : ` About ${(s / 3600).toFixed(1)} hours left.`;
  const text = `${job.step}, ${job.W} × ${job.H} pixels. ${pc}%.${left}`;
  if (u.step.textContent !== text) u.step.textContent = text;
}
// The line under the size choice: how large the picture will be, and what a different shape does to the view.
function exportSizeNote() {
  const u = EXPORT.ui;
  if (!u) return;
  const [pw, ph] = stagePixels(), st = { pw, ph }, [W, H] = exportDims(EXPORT.opt, st);
  const shape = W / H / (st.pw / Math.max(1, st.ph));
  const text = `The picture will be ${W} × ${H} pixels.` + (shape > 1.02 ? ' It is wider than the picture on screen, so it shows more at the sides.' : shape < 0.98 ? ' It is narrower than the picture on screen, so it shows less at the sides.' : '');
  if (u.sizeNote.textContent !== text) u.sizeNote.textContent = text;
  const typed = EXPORT.opt.size === 'typed';
  if (u.typed.hidden === typed) u.typed.hidden = !typed;
  u.w.el.hidden = u.h.el.hidden = !typed;
}
// Show the block that fits the state: the start button, the running job, or the finished picture. With `move`,
// the keyboard focus follows when the button it was on has just gone.
function exportShow(move) {
  const u = EXPORT.ui, job = EXPORT.job, res = EXPORT.result;
  if (!u) return;
  const lostFocus = move && [u.start, u.cancel, u.save, u.discard].includes(document.activeElement);
  u.idle.hidden = !!job || !!res; u.run.hidden = !job; u.done.hidden = !!job || !res;
  if (job) exportPaint(true);
  if (res && !job) {
    u.facts.textContent = '';
    res.facts.forEach(([k, v]) => { u.facts.appendChild(Object.assign(document.createElement('dt'), { textContent: k })); u.facts.appendChild(Object.assign(document.createElement('dd'), { textContent: v })); });
  }
  if (lostFocus) (job ? u.cancel : res ? u.save : u.start).focus();
}
function buildExportPanel(host) {
  host = typeof host === 'string' ? $(host) : host;
  if (!host || EXPORT.ui) return;
  const O = EXPORT.opt, grp = { group: 'export' };
  const make = (parent, tag, cls, text) => { const e = document.createElement(tag); if (cls) e.className = cls; if (text) e.textContent = text; parent.appendChild(e); return e; };
  const button = (parent, id, text, act) => { const b = make(parent, 'button', 'btn', text); b.type = 'button'; b.id = id; b.addEventListener('click', act); return b; };
  host.classList.add('export-panel');
  make(host, 'p', 'note', 'Draws the picture again at the size and quality you choose and gives it to you as a file. It is the picture as it is when you press Start: you can go on exploring while it is drawn, and what you change afterwards does not affect it.');
  const u = EXPORT.ui = {};
  addSelect(host, 'exportSize', 'Size', EXPORT_SIZES, () => O.size, v => { O.size = v; exportSizeNote(); }, { ...grp, def: 'x2' });
  u.typed = make(host, 'div', 'export-typed');
  u.w = addDial(u.typed, 'exportW', 'Width, pixels', 16, 8192, 1, () => O.w, v => { O.w = v; exportSizeNote(); }, { ...grp, def: 1920, int: true, slider: false, xhi: 16384 });
  u.h = addDial(u.typed, 'exportH', 'Height, pixels', 16, 8192, 1, () => O.h, v => { O.h = v; exportSizeNote(); }, { ...grp, def: 1080, int: true, slider: false, xhi: 16384 });
  u.sizeNote = make(host, 'p', 'note export-size'); u.sizeNote.id = 'exportSizeNote';
  addSelect(host, 'exportQuality', 'Quality', [['screen', 'As on screen now'], ['fine', 'Fine'], ['extra', 'Extra fine (slowest)']], () => O.quality, v => { O.quality = v; },
    { ...grp, def: 'fine', help: 'As on screen now uses the settings under Quality and speed as they are. Fine and Extra fine use more passes, more ray steps and a finer surface, whatever is set there. Large sizes at Extra fine can take many minutes.' });
  addSelect(host, 'exportKind', 'File type', [['png', 'PNG (every pixel exact, largest file)'], ['jpg', 'JPG (small file)'], ['webp', 'WebP (smallest file)']], () => O.kind, v => { O.kind = v; }, { ...grp, def: 'png' });
  u.idle = make(host, 'div', 'row-btns'); u.run = make(host, 'div', 'export-run'); u.bar = make(u.run, 'div', 'export-bar');
  u.fill = make(u.bar, 'span'); u.step = make(u.run, 'p', 'export-step');
  u.bar.id = 'exportBar'; u.bar.setAttribute('role', 'progressbar'); u.bar.setAttribute('aria-label', 'Progress of the picture');
  u.bar.setAttribute('aria-valuemin', 0); u.bar.setAttribute('aria-valuemax', 100);
  u.step.id = 'exportStep';
  u.start = button(u.idle, 'exportStart', 'Start the picture', exportStart);
  u.cancel = button(make(u.run, 'div', 'row-btns'), 'exportCancel', 'Cancel', () => { if (EXPORT.job) EXPORT.job.cancel = true; });
  u.done = make(host, 'div', 'export-done');
  u.preview = make(u.done, 'canvas', 'export-preview'); u.preview.id = 'exportPreview';
  u.preview.setAttribute('role', 'img'); u.preview.setAttribute('aria-label', 'The finished picture, small');
  u.facts = make(u.done, 'dl', 'export-facts'); u.facts.id = 'exportFacts';
  const row = make(u.done, 'div', 'row-btns');
  u.save = button(row, 'exportSave', 'Save the file', exportSave);
  u.discard = button(row, 'exportDiscard', 'Discard', () => { EXPORT.result = null; exportSay(''); exportShow(true); });
  u.msg = make(host, 'p', 'note export-msg'); u.msg.id = 'exportMsg'; u.msg.setAttribute('role', 'status');
  addReset(host, 'export', { after: exportSizeNote });
  hooks.view.push(exportSizeNote);   // the stage may have changed size
  exportSizeNote(); exportShow(false);
}

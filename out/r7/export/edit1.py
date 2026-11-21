"""First edit of src/js/45-export.js: the cost of every tile is measured before the tiles are drawn (export-1),
and the save button's words and state after a failure (export-2, export-3)."""
import io, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
p = os.path.join(ROOT, 'src', 'js', '45-export.js')
s = io.open(p, encoding='utf-8').read()


def rep(a, b, count=1):
    global s
    if s.count(a) != count:
        sys.exit('expected %d of: %r, found %d' % (count, a[:70], s.count(a)))
    s = s.replace(a, b)


# ---- constants
rep("""const EXPORT_MAX = 1e8;       // pixels in all: three times an 8K picture. Beyond it a browser may run out of memory instead of saying no.
""", """const EXPORT_MAX = 1e8;       // pixels in all: three times an 8K picture. Beyond it a browser may run out of memory instead of saying no.
// Before the tiles are drawn every tile is felt: one small patch (EXPORT_FEEL[1] pixels square) in the middle of
// each square of EXPORT_FEEL[0] pixels is drawn once and timed. That is 1/64 of one pass, and it is what the bar
// and the time left are worked out from (see exportProgress).
const EXPORT_FEEL = [64, 8];
""")

# ---- the job: tiles as a list, the feeling pass, and progress by cost
rep("""  const bytes = new Uint8Array(4 * T * T), total = W * H * passes;
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
""", """  const bytes = new Uint8Array(4 * T * T);
  // The tiles, rows from the top of the picture down. For each: N pixel-passes in all and n of them drawn; ms, the
  // time by the clock it has had; gpu and clock, what its patches cost when they were felt (see exportFeel).
  const tiles = job.tiles = [];
  for (let y0 = (Math.ceil(H / T) - 1) * T; y0 >= 0; y0 -= T) {
    for (let x0 = 0; x0 < W; x0 += T) {
      const tw = Math.min(T, W - x0), th = Math.min(T, H - y0);
      tiles.push({ x0, y0, tw, th, N: tw * th * passes, n: 0, ms: 0, fin: false, gpu: 0, clock: -1, felt: 0, w: 0 });
    }
  }
  try {
    if (!acc.ok || !out.ok) throw exportStop('failed');
    job.step = 'Working out how long it will take'; exportPaint();
    await exportFeel(job, tile => (rects, late) => bgPiece(() => {
      if (R.gen !== gen) throw new Error('the GL context changed');
      gl.bindFramebuffer(gl.FRAMEBUFFER, acc.fbo); gl.viewport(0, 0, tile.tw, tile.th);
      gl.disable(gl.BLEND); gl.enable(gl.SCISSOR_TEST);
      setScene(P, Object.assign(o, { off: [tile.x0, tile.y0] }), snap);
      for (const r of rects) { gl.scissor(r[0], r[1], r[2], r[3]); gl.drawArrays(gl.TRIANGLES, 0, 3); }
    }, null, late), check);
    job.step = 'Drawing the picture'; exportPaint(true);
    for (const tile of tiles) {
      {
        const { x0, y0, tw, th } = tile, tile0 = performance.now();
        const went = n => {   // n pixel-passes of this tile have been drawn
          tile.n += n; tile.ms = performance.now() - tile0;
          exportProgress(job); exportPaint();
        };
""")
rep("""        job.big.ctx.putImageData(img, x0, H - y0 - th);
      }
    }
  } finally {""", """        job.big.ctx.putImageData(img, x0, H - y0 - th);
        tile.n = tile.N; tile.ms = performance.now() - tile0; tile.fin = true;
        exportProgress(job, true); exportPaint();
      }
    }
  } finally {""")
rep("""  job.step = `Writing the ${word} file`; job.frac = 0.97; job.left = 0; exportPaint();""",
    """  job.step = `Writing the ${word} file`; job.frac = 0.97; job.left = -1; exportPaint();
  if (typeof window.squaringLabExportTest === 'function') window.squaringLabExportTest(tiles.map(t => ({ x0: t.x0, y0: t.y0, gpu: t.gpu, clock: t.clock, felt: t.felt, w: t.w, ms: t.ms })));""")

# ---- the two new functions, before exportStart
rep("""async function exportStart() {""", """// What every tile will cost, before any of it is drawn. A pixel on the solid can cost a hundred times a pixel of
// the empty background, so the share of the pixels drawn says little about the share of the time gone. Each tile's
// patches (EXPORT_FEEL) are drawn as one piece, twice over, and the cheaper reading counts: other programs using
// the GPU can only make a reading longer. A tile whose two readings disagree is asked a third time.
// piece(tile) gives a function (rects, late) that draws those rectangles of the tile as one background piece.
// The GPU's own count is taken where it arrives; the clock otherwise, less what a piece that draws nothing takes.
async function exportFeel(job, piece, check) {
  const [cell, side] = EXPORT_FEEL, tiles = job.tiles;
  const rects = t => {
    const list = [];
    for (let y = 0; y < t.th; y += cell) for (let x = 0; x < t.tw; x += cell) {
      const cw = Math.min(cell, t.tw - x), ch = Math.min(cell, t.th - y), w = Math.min(side, cw), h = Math.min(side, ch);
      list.push([x + ((cw - w) >> 2 << 1), y + ((ch - h) >> 2 << 1), w, h]);   // on even pixels: the GPU shades in blocks of 2 x 2
    }
    return list;
  };
  let none = Infinity;   // what a piece costs by the clock when it draws next to nothing
  for (let i = 0; i < 3; i++) none = Math.min(none, check(await piece(tiles[0])([[0, 0, 2, 2]], null)).ms);
  const feel = async t => {
    const list = rects(t);
    const c = check(await piece(t)(list, ms => { t.gpu = t.gpu > 0 ? Math.min(t.gpu, ms) : ms; }));
    const net = Math.max(c.ms - none, 0);
    t.felt = list.reduce((a, r) => a + r[2] * r[3], 0);
    t.clock = t.clock < 0 ? net : Math.min(t.clock, net);
    return net;
  };
  const first = [];
  for (const t of tiles) first.push(await feel(t));
  for (let i = 0; i < tiles.length; i++) {
    const a = first[i], b = await feel(tiles[i]);
    if (Math.max(a, b) > 1.5 * Math.min(a, b) + 0.5) await feel(tiles[i]);
  }
}
// A tile's cost as it was felt, in milliseconds for the whole tile with all its passes.
function exportCost(t) { return Math.max(t.gpu > 0 ? t.gpu : t.clock, 0.004) / Math.max(1, t.felt) * t.N; }
// The bar and the time left. The bar is the share of the felt cost that has been drawn. The time left needs one
// more number, how long the clock takes over one unit of felt cost; it is taken from the tiles drawn so far, as the
// middle value when each counts by the time it took (a tile whose feeling was disturbed then has no say). Tiles
// with next to nothing in them are left out of that and counted by what such a tile takes as a whole. No time is
// given before two seconds have gone into tiles that matter, and once given it does not go up again: when the
// job is slowed, by the live picture or by another program, the number waits.
function exportProgress(job, force) {
  const now = performance.now(), tiles = job.tiles;
  if (!tiles || (!force && now - (job.told || 0) < 200)) return;
  job.told = now;
  let total = 0, done = 0;
  for (const t of tiles) { t.w = exportCost(t); total += t.w; done += t.w * t.n / t.N; }
  job.frac = Math.max(job.frac, 0.97 * done / total);
  const dear = 0.25 * total / tiles.length;
  const cheap = tiles.filter(t => t.fin && t.w < dear).map(t => t.ms).sort((a, b) => a - b), each = cheap.length ? cheap[cheap.length >> 1] : 0;
  const rates = tiles.filter(t => t.n > 0 && t.ms > 0 && t.w >= dear).map(t => [t.ms / (t.w * t.n / t.N), t.ms]).sort((a, b) => a[0] - b[0]);
  const seen = rates.reduce((a, r) => a + r[1], 0);
  if (seen < 2000) return;
  let rate = 0, half = 0;
  for (const r of rates) { half += r[1]; if (half >= seen / 2) { rate = r[0]; break; } }
  let left = 0;
  for (const t of tiles) if (!t.fin) left += t.w < dear && !t.n ? Math.max(each, rate * t.w) : rate * t.w * (1 - t.n / t.N);
  job.left = job.left >= 0 ? Math.min(job.left, left) : left;
}
async function exportStart() {""")
rep("""cancel: false, step: 'Starting', frac: 0, left: 0, t0: performance.now(), painted: 0 };""",
    """cancel: false, step: 'Starting', frac: 0, left: -1, t0: performance.now(), painted: 0 };   // left: milliseconds, -1 while it cannot be said""")

# ---- the words for the time left
rep("""  const left = s < 3 ? '' : s < 90 ? ` About ${Math.round(s)} seconds left.` : s < 5400 ? ` About ${Math.round(s / 60)} minutes left.` : ` About ${(s / 3600).toFixed(1)} hours left.`;
""", """  const left = exportLeftWords(s);
""")
rep("""// ---------- the panel
""", """// ---------- the panel
// The time left in words, no finer than it is known: whole seconds at the end, fives and tens before that, half
// minutes up to five minutes. Nothing under three seconds, and nothing while it cannot be said (s below 0).
function exportLeftWords(s) {
  if (!(s >= 3)) return '';
  if (s < 100) return ` About ${s < 20 ? Math.round(s) : s < 60 ? 5 * Math.round(s / 5) : 10 * Math.round(s / 10)} seconds left.`;
  if (s < 330) { const h = Math.round(s / 30); return ` About ${(h >> 1) + (h & 1 ? '½' : '')} minutes left.`; }
  return s < 5400 ? ` About ${Math.round(s / 60)} minutes left.` : ` About ${(s / 3600).toFixed(1)} hours left.`;
}
""")

# ---- saving
rep("""  r.saving = true;
  const out = await saveFile(r.name, r.blob);
  r.saving = false;
  if (EXPORT.result === r) exportSay(out.ok ? `Saved as ${r.name}. You can save it again, or discard it to make another picture.` : `${out.message} The picture is still here, so you can try again.`);
}""", """  r.saving = true;
  let out = null;
  // saveFile promises not to throw. Should it do so all the same, the button must not stay dead for this picture.
  try { out = await saveFile(r.name, r.blob); }
  catch (err) { console.error('Saving the picture failed: ' + (err && err.stack || err)); }
  finally { r.saving = false; }
  if (EXPORT.result === r) exportSay(exportSaveWords(out || { ok: false, code: 'failed', again: true }, r));
}
// What to say after a press of "Save the file". Another try is offered only where it can help (out.again).
function exportSaveWords(out, r) {
  if (out.ok) return `Saved as ${r.name}. You can save it again, or discard it to make another picture.`;
  const msg = out.message || 'The file could not be saved.';
  const again = out.again !== undefined ? out.again : ['declined', 'rate_limited', 'failed'].includes(out.code);
  if (again) return /try again/i.test(msg) ? `${msg} The picture is still here.` : `${msg} The picture is still here, so you can try again.`;
  if (out.code === 'too_large' && /\\.png$/.test(r.name)) return `${msg} A JPG or WebP file of the same picture is much smaller.`;
  if (out.code === 'rejected_extension' || out.code === 'extension_not_enabled') return `${msg} Discard the picture and choose another file type.`;
  return msg;
}""")
io.open(p, 'w', encoding='utf-8', newline='\n').write(s)
print('edited', p)

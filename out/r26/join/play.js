// Play for real: press Play at step 0 and record, in the page, the time between every two frames
// (requestAnimationFrame) until the steps stop at 16. Speed as the page opens (Normal).
// Beside that, per frame: the time the page's own redraw took (LEARN.shape.state().ms.frame; for a flat picture
// that is all there is), and, in the second half of this list, what the graphics card needed for each 3D picture:
// one pixel is read back in the task after the module's drawArrays, and the time from the draw to that answer is
// taken. (In this headless Chrome requestAnimationFrame keeps its beat while the card is busy, so the times
// between frames alone would hide a slow 3D picture. The read-back changes the pace a little, which is why the
// times between frames are taken in runs without it.)
//@
await shapeOn({ kind: 'm', space: 2, pos: 0 });
window.__probe = () => {
  const gl = document.querySelector('canvas.learn-shape-gl');
  if (!gl || window.__probed) return;
  window.__probed = true; window.__gpu = [];
  const ctx = gl.getContext('webgl2'), orig = ctx.drawArrays.bind(ctx), px = new Uint8Array(4);
  let waiting = false;
  ctx.drawArrays = (...a) => {
    orig(...a);
    if (waiting || !window.__probing) return;
    waiting = true;
    const t = performance.now(), size = gl.width + 'x' + gl.height;
    setTimeout(() => { waiting = false; if (ctx.isContextLost()) return; ctx.bindFramebuffer(ctx.FRAMEBUFFER, null); ctx.readPixels(0, 0, 1, 1, ctx.RGBA, ctx.UNSIGNED_BYTE, px); window.__gpu.push([performance.now() - t, size]); }, 0);
  };
};
window.__play = async (kind, space, c, ap, probe) => {
  if (ap) await approach(ap);
  const t00 = performance.now();
  L.shape.set({ kind, space, c: c || [-0.1226, 0.7449, 0], pos: 0 });
  const firstMs = performance.now() - t00;
  await sleep(700);
  if (space === 3) window.__probe();
  window.__probing = !!probe; window.__gpu = [];
  const gaps = [], own = [], sentences = new Set(), notes = new Set(), asked = new Set();
  let last = 0, stop = false;
  // (state() is asked only while the steps play: then it reads and draws nothing; at rest it would draw the fine picture early)
  const tick = now => { if (stop) return; if (last) gaps.push(now - last); last = now; if ($('learnShapePlay').textContent === 'Pause') { const s = L.shape.state(); own.push(s.ms.frame); if (s.three && space === 3) asked.add(s.three.quality); } requestAnimationFrame(tick); };
  $('learnShapePlay').click();
  requestAnimationFrame(tick);
  const t0 = performance.now();
  for (let i = 0; i < 1500; i++) {
    await sleep(40);
    sentences.add($('learnShapeSay').textContent);
    notes.add($('learnShapeNote').hidden ? '' : $('learnShapeNote').textContent);
    if ($('learnShapePlay').textContent === 'Play') break;
  }
  stop = true;
  const secs = (performance.now() - t0) / 1000, gpuPlay = window.__gpu.slice();
  await sleep(600);
  const s = L.shape.state();
  if (s.pos !== 16 || s.playing) fail(kind + ' ' + space + 'D did not play to the end: ' + s.pos);
  const q = (a, f) => { const b = a.slice().sort((x, y) => x - y); return b.length ? r1(b[Math.min(b.length - 1, Math.floor(f * b.length))]) : null; };
  const out = { what: (kind === 'm' ? 'Mandelbrot shape' : kind === 'j' ? 'Julia shape' : 'Both') + ', ' + space + 'D' + (ap ? ', ' + LAB.APPROACHES[S.approach].name : ''),
    seconds: r1(secs), frames: gaps.length,
    betweenFramesMs: { median: q(gaps, 0.5), p95: q(gaps, 0.95), p99: q(gaps, 0.99), slowest: r1(Math.max(...gaps)), over20: gaps.filter(g => g > 20).length, over34: gaps.filter(g => g > 34).length, over50: gaps.filter(g => g > 50).length },
    pageRedrawMs: { median: q(own, 0.5), p99: q(own, 0.99), slowest: r1(Math.max(...own)) },
    sentencesSeen: sentences.size, note: [...notes].filter(Boolean).join(' / '), askedWhilePlaying: [...asked].join(' '), atRest: s.quality, last: s.sentence };
  if (probe) {
    const ms = gpuPlay.map(x => x[0]), rest = window.__gpu.slice(gpuPlay.length);
    out.cardMsPerPicture = { pictures: ms.length, median: q(ms, 0.5), p95: q(ms, 0.95), slowest: r1(Math.max(...ms)), buffers: [...new Set(gpuPlay.map(x => x[1]))].join(' '),
      theRestingPictureAfterwards: rest.map(x => r1(x[0]) + ' ms at ' + x[1]).join(', ') };
  }
  window.__probing = false;
  return out;
};
return 'ready, ' + LAB.APPROACHES[S.approach].name + ', speed ' + $('learnShapeSpeed').value;
//@
return await window.__play('m', 2);
//@
return await window.__play('j', 2);
//@
return await window.__play('both', 2);
//@ sleep=0.3 shot=out/r26/join/NAME-both-2d-end.png
//@
return await window.__play('m', 3);
//@ sleep=0.5 shot=out/r26/join/NAME-m-3d-end.png
//@
return await window.__play('j', 3);
//@
return await window.__play('both', 3);
//@ sleep=0.5 shot=out/r26/join/NAME-both-3d-end.png
//@
return await window.__play('both', 3, [-1, 0, 0], 'fold');
//@
return await window.__play('both', 3, [-1, 0, 0], 'pillow');
//@ sleep=0.5 shot=out/r26/join/NAME-both-3d-pillow-end.png
//@
// the same in 3D with every picture waited for: what the graphics card needed
return await window.__play('m', 3, null, 'mercator', true);
//@
return await window.__play('j', 3, null, null, true);
//@
return await window.__play('both', 3, null, null, true);
//@
return await window.__play('both', 3, [-1, 0, 0], 'fold', true);
//@
return await window.__play('both', 3, [-1, 0, 0], 'pillow', true);
//@
return await approach('mercator');

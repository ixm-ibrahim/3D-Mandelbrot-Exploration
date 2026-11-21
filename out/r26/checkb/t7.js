// Feel. (1) From pressing Play to the first movement. (2) Does the slider follow the hand. (3) Is 3D smooth while
// it plays. Times are taken inside the page. For 3D the graphics card's own time per picture is taken too: one
// pixel is read back in the task after the module's draw (the joiner's probe; in this headless Chrome the beat of
// requestAnimationFrame alone does not show a busy card).
//@
await openLearn(); await pickShape(); L.shape.pause(); $('learnShapeAgain').click(); await sleep(300);
window.__q = (a, f) => { const b = a.slice().sort((x, y) => x - y); return b.length ? r1(b[Math.min(b.length - 1, Math.floor(f * b.length))]) : null; };
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
    setTimeout(() => { waiting = false; if (ctx.isContextLost()) return; ctx.bindFramebuffer(ctx.FRAMEBUFFER, null); ctx.readPixels(0, 0, 1, 1, ctx.RGBA, ctx.UNSIGNED_BYTE, px); window.__gpu.push([performance.now() - t, size, t]); }, 0);
  };
};
// a hash of the flat picture's canvas (a coarse grid of its pixels), to see when the picture itself first changes
window.__hash = () => { const cv = $('learnShapeCanvas'), g = cv.getContext('2d'), w = cv.width, h = cv.height; let s = 0; for (let j = 1; j < 24; j++) { const d = g.getImageData(0, Math.floor(h * j / 24), w, 1).data; for (let i = 0; i < d.length; i += 28) s = (s * 31 + d[i] + 3 * d[i + 1] + 7 * d[i + 2]) >>> 0; } return s; };
// press Play by its own button and time what happens first
window.__first = async (kind, space) => {
  kindBar(kind); spaceBar(space); await sleep(space === 3 ? 900 : 300); $('learnShapeAgain').click(); await sleep(space === 3 ? 700 : 300);
  if (space === 3) { window.__probe(); window.__probing = true; window.__gpu = []; }
  const h0 = space === 2 ? window.__hash() : 0, say0 = $('learnShapeSay').textContent;
  const out = { what: kind + ' ' + space + 'D' };
  const t0 = performance.now();
  $('learnShapePlay').click();
  out.buttonSaysPauseMs = $('learnShapePlay').textContent === 'Pause' ? r1(performance.now() - t0) : null;
  for (let i = 0; i < 240; i++) {
    await frame();
    const t = r1(performance.now() - t0);
    if (out.sliderMovedMs === undefined && +$('learnShapePos').value > 0) out.sliderMovedMs = t;
    if (out.sentenceChangedMs === undefined && $('learnShapeSay').textContent !== say0) out.sentenceChangedMs = t;
    if (space === 2 && out.pictureChangedMs === undefined && window.__hash() !== h0) out.pictureChangedMs = t;
    if (space === 3 && out.firstPictureOffTheCardMs === undefined && window.__gpu.length) out.firstPictureOffTheCardMs = r1(window.__gpu[0][2] + window.__gpu[0][0] - t0);
    if (t > 2600) break;
  }
  out.sliderAfter = +$('learnShapePos').value;
  L.shape.pause(); window.__probing = false;
  return out;
};
// the hand on the slider: its value changed once a frame, as a drag would, from 0 to 16 and back in n frames each way
window.__sweep = async (kind, space, n, ap) => {
  if (ap) await approach(ap);
  kindBar(kind); spaceBar(space); await sleep(space === 3 ? 900 : 300); $('learnShapeAgain').click(); await sleep(500);
  if (space === 3) { window.__probe(); window.__probing = true; window.__gpu = []; }
  const el = $('learnShapePos'), gaps = [], own = [], handler = [], lag = [];
  let last = performance.now();
  for (let i = 1; i <= 2 * n; i++) {
    const v = i <= n ? 16 * i / n : 16 * (2 * n - i) / n;
    el.value = v;
    const t = performance.now(); el.dispatchEvent(new Event('input', { bubbles: true })); handler.push(performance.now() - t);
    lag.push(Math.abs(+el.value - L.shape.state().pos) > 0.03 ? 1 : 0);
    await frame(); const now = performance.now(); gaps.push(now - last); last = now;
  }
  const gpu = (window.__gpu || []).map(x => x[0]), sizes = [...new Set((window.__gpu || []).map(x => x[1]))];
  window.__probing = false; await sleep(400);
  const q = window.__q;
  return { what: kind + ' ' + space + 'D' + (ap ? ' ' + ap : ''), frames: gaps.length, betweenFramesMs: { median: q(gaps, 0.5), p95: q(gaps, 0.95), slowest: r1(Math.max(...gaps)) },
    theInputHandlerMs: { median: q(handler, 0.5), p95: q(handler, 0.95), slowest: r1(Math.max(...handler)) }, timesTheSliderAndThePictureDisagreed: lag.reduce((a, b) => a + b, 0),
    cardMsPerPicture: space === 3 ? { pictures: gpu.length, median: q(gpu, 0.5), p95: q(gpu, 0.95), slowest: gpu.length ? r1(Math.max(...gpu)) : null, buffers: sizes.join(' ') } : undefined };
};
// play to the end, timing every frame; probe: also the card's time per picture
window.__play = async (kind, space, ap, probe) => {
  if (ap) await approach(ap);
  kindBar(kind); spaceBar(space); await sleep(space === 3 ? 900 : 300); $('learnShapeAgain').click(); await sleep(700);
  if (space === 3) window.__probe();
  window.__probing = !!probe; window.__gpu = [];
  const gaps = [], own = [];
  let last = 0, stop = false;
  const tick = now => { if (stop) return; if (last) gaps.push(now - last); last = now; if ($('learnShapePlay').textContent === 'Pause') own.push(L.shape.state().ms.frame); requestAnimationFrame(tick); };
  $('learnShapePlay').click(); requestAnimationFrame(tick);
  const t0 = performance.now();
  for (let i = 0; i < 1500; i++) { await sleep(40); if ($('learnShapePlay').textContent === 'Play') break; }
  stop = true;
  const secs = (performance.now() - t0) / 1000, gpu = window.__gpu.map(x => x[0]), sizes = [...new Set(window.__gpu.map(x => x[1]))];
  window.__probing = false; await sleep(600);
  const q = window.__q;
  return { what: kind + ' ' + space + 'D' + (ap ? ', ' + LAB.APPROACHES[S.approach].name : ''), seconds: r1(secs), frames: gaps.length,
    betweenFramesMs: { median: q(gaps, 0.5), p95: q(gaps, 0.95), p99: q(gaps, 0.99), slowest: r1(Math.max(...gaps)), over20: gaps.filter(g => g > 20).length, over34: gaps.filter(g => g > 34).length, over50: gaps.filter(g => g > 50).length },
    pageRedrawMs: { median: q(own, 0.5), p99: q(own, 0.99), slowest: r1(Math.max(...own)) },
    cardMsPerPicture: probe ? { pictures: gpu.length, median: q(gpu, 0.5), p95: q(gpu, 0.95), slowest: gpu.length ? r1(Math.max(...gpu)) : null, over34: gpu.filter(g => g > 34).length, over50: gpu.filter(g => g > 50).length, buffers: sizes.join(' ') } : undefined, endAt: +$('learnShapePos').value };
};
return 'ready, ' + LAB.APPROACHES[S.approach].name + ', ' + innerWidth + 'x' + innerHeight + ', stage ' + box('stage').slice(2).join('x');
//@
return [await window.__first('m', 2), await window.__first('j', 2), await window.__first('both', 2)];
//@
return [await window.__first('m', 3), await window.__first('j', 3), await window.__first('both', 3)];
//@
return [await window.__sweep('m', 2, 90), await window.__sweep('both', 2, 90)];
//@
return [await window.__sweep('m', 3, 90, 'mercator'), await window.__sweep('both', 3, 90, 'mercator')];
//@
return [await window.__sweep('both', 3, 90, 'fold'), await window.__sweep('m', 3, 90, 'bulb')];
//@
return await window.__play('m', 2, 'mercator', false);
//@
return await window.__play('m', 3, 'mercator', false);
//@
return await window.__play('m', 3, 'mercator', true);
//@
return await window.__play('both', 3, 'fold', true);
//@
return await window.__play('m', 3, 'turnalong', true);
//@
return await window.__play('m', 3, 'lathe', true);
//@
return await window.__play('both', 3, 'bulb', true);

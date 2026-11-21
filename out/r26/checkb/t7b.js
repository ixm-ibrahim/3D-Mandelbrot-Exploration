// The 3D part of t7 again, short, to run at another moment (other work on this machine shares the graphics card):
// the slider swept by hand and one play, opening approach, with the card's time per picture.
//@
await openLearn(); await pickShape(); L.shape.pause(); $('learnShapeAgain').click(); await sleep(300);
const q = (a, f) => { const b = a.slice().sort((x, y) => x - y); return b.length ? r1(b[Math.min(b.length - 1, Math.floor(f * b.length))]) : null; };
window.__q = q;
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
return 'ready';
//@
// the card's time for one and the same resting picture, ten times over (a yardstick for how busy the card is now)
kindBar('m'); spaceBar(3); await sleep(900); $('learnShapeTicks').children[3].click(); await sleep(900);
window.__probe(); window.__probing = true; window.__gpu = [];
const cv = $('learnShapeCanvas');
for (let i = 0; i < 10; i++) { ptr(cv, 'pointerdown', 400, 250); ptr(cv, 'pointermove', 400 + (i % 2 ? -3 : 3), 250); await frame(); await frame(); ptr(cv, 'pointerup', 400, 250); await sleep(450); }
window.__probing = false;
const mv = window.__gpu.filter(x => x[1] === '862x511').map(x => x[0]), st = window.__gpu.filter(x => x[1] !== '862x511');
return { yardstick: 'step 3, opening approach', moveMs: { n: mv.length, median: window.__q(mv, 0.5), slowest: mv.length ? r1(Math.max(...mv)) : null }, stillMs: st.map(x => r1(x[0]) + ' at ' + x[1]) };
//@
// the slider swept as a hand would: one value a frame, 0 to 16 and back, 90 frames each way
$('learnShapeAgain').click(); await sleep(600);
window.__probing = true; window.__gpu = [];
const el = $('learnShapePos'), gaps = [], n = 90; let last = performance.now();
for (let i = 1; i <= 2 * n; i++) { el.value = i <= n ? 16 * i / n : 16 * (2 * n - i) / n; el.dispatchEvent(new Event('input', { bubbles: true })); await frame(); const now = performance.now(); gaps.push(now - last); last = now; }
const gpu = window.__gpu.map(x => x[0]); window.__probing = false; await sleep(500);
return { sweep: 'm 3D, opening approach', betweenFramesMs: { median: window.__q(gaps, 0.5), p95: window.__q(gaps, 0.95), slowest: r1(Math.max(...gaps)) }, cardMsPerPicture: { pictures: gpu.length, median: window.__q(gpu, 0.5), p95: window.__q(gpu, 0.95), slowest: r1(Math.max(...gpu)) } };
//@
// one play, Normal speed
$('learnShapeAgain').click(); await sleep(700);
window.__probing = true; window.__gpu = [];
const gaps = []; let last = 0, stop = false;
const tick = now => { if (stop) return; if (last) gaps.push(now - last); last = now; requestAnimationFrame(tick); };
$('learnShapePlay').click(); requestAnimationFrame(tick);
const t0 = performance.now();
for (let i = 0; i < 1500; i++) { await sleep(40); if ($('learnShapePlay').textContent === 'Play') break; }
stop = true; const secs = (performance.now() - t0) / 1000, gpu = window.__gpu.map(x => x[0]); window.__probing = false; await sleep(500);
const q = window.__q;
return { play: 'm 3D, opening approach', seconds: r1(secs), frames: gaps.length, betweenFramesMs: { median: q(gaps, 0.5), p95: q(gaps, 0.95), slowest: r1(Math.max(...gaps)), over34: gaps.filter(g => g > 34).length, over50: gaps.filter(g => g > 50).length },
  cardMsPerPicture: { pictures: gpu.length, median: q(gpu, 0.5), p95: q(gpu, 0.95), slowest: r1(Math.max(...gpu)), over34: gpu.filter(g => g > 34).length, over50: gpu.filter(g => g > 50).length } };

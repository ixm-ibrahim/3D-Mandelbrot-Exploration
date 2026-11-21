// Does the page hang when a zoomed-in 3D picture comes to rest? In the page, as a hand would do it: the wheel
// zooms in notch by notch, then nothing is touched; then the picture is turned and let go; then a tick of the
// slider is clicked; then another approach is chosen, still zoomed in.
// What is measured: every picture the 3D module draws is waited for (one pixel is read back in the task after its
// drawArrays, so outside the module's own timing), and the time from the draw to that answer is what the graphics
// card needed for the picture, give or take a few ms. In this headless Chrome the times between
// requestAnimationFrame calls do NOT show a busy card, so they are no use here.
// Run on the joined page and, for comparison, on the page as the two builders left it (--page r26-core-three).
//@
await shapeOn({ kind: 'j', space: 3, pos: 12, c: [-1, 0, 0] });
await sleep(400);
const gl = document.querySelector('canvas.learn-shape-gl'), ctx = gl.getContext('webgl2'), orig = ctx.drawArrays.bind(ctx), px = new Uint8Array(4);
window.__log = [];
let waiting = false;
ctx.drawArrays = (...a) => {
  orig(...a);
  if (waiting) return;
  waiting = true;
  const t = performance.now(), size = gl.width + 'x' + gl.height;
  setTimeout(() => { waiting = false; if (ctx.isContextLost()) return; ctx.bindFramebuffer(ctx.FRAMEBUFFER, null); ctx.readPixels(0, 0, 1, 1, ctx.RGBA, ctx.UNSIGNED_BYTE, px); window.__log.push([performance.now() - t, size]); }, 0);
};
window.__take = () => { const l = window.__log; window.__log = []; if (!l.length) return 'no picture drawn'; const ms = l.map(x => x[0]); return { pictures: l.length, longestMs: r1(Math.max(...ms)), medianMs: r1(med(ms)), buffers: [...new Set(l.map(x => x[1]))].join(' '), longestWas: l[ms.indexOf(Math.max(...ms))][1] }; };
window.__try = async (id, notches) => {
  await approach(id);
  L.shape.set({ kind: 'j', space: 3, pos: 12, c: [-1, 0, 0] });
  if (shown('learnShapeViewReset')) $('learnShapeViewReset').click();
  await sleep(900);
  window.__take();
  const st = $('stage'), cv = $('learnShapeCanvas'), r = st.getBoundingClientRect(), out = { approach: LAB.APPROACHES[S.approach].name };
  for (let i = 0; i < notches; i++) { st.dispatchEvent(new WheelEvent('wheel', { bubbles: true, cancelable: true, deltaY: -100, clientX: r.left + 430, clientY: r.top + 255 })); await frame(); await frame(); }
  out.whileZooming = window.__take();
  await sleep(1200);
  out.whenTheZoomRests = window.__take();
  out.zoom = +L.shape.state().view3.zoom.toFixed(2);      // (nothing is waiting to be drawn by now, so this draws nothing)
  ptr(cv, 'pointerdown', 300, 200);
  for (let i = 1; i <= 14; i++) { ptr(cv, 'pointermove', 300 + 8 * i, 200 + 3 * i); await frame(); await frame(); }
  out.whileTurning = window.__take();
  ptr(cv, 'pointerup', 412, 242);
  await sleep(1200);
  out.afterLettingGo = window.__take();
  $('learnShapeTicks').children[9].click();
  await sleep(1200);
  out.afterATickOfTheSlider = window.__take();
  return out;
};
return 'ready';
//@
return await window.__try('mercator', 6);
//@
return await window.__try('mercator', 14);
//@
return await window.__try('fold', 14);
//@
return await window.__try('pillow', 6);
//@
return await window.__try('pillow', 14);
//@ sleep=0.3 shot=out/r26/join/NAME-pillow-zoomed.png clip=#stage
//@
// another approach chosen while zoomed in: a picture nothing led up to
window.__take();
await approach('softfold');
await sleep(1500);
const a = window.__take();
await approach('pillow');
await sleep(1500);
return { 'to Blended planes, zoomed in': a, 'back to Pillow, zoomed in': window.__take() };
//@
// zoom out again and rest: the fine picture comes back
$('learnShapeViewReset').click();
const gl = document.querySelector('canvas.learn-shape-gl'), seen = [];
for (let i = 0; i < 4; i++) { await sleep(600); L.shape.set({ pos: 9 + (i % 2) }); await sleep(600); seen.push(gl.width + 'x' + gl.height); }
await approach('mercator');
await sleep(600); L.shape.set({ pos: 3 }); await sleep(700);
return { buffersAtRestAtZoom1Again: seen, withTheOpeningApproach: gl.width + 'x' + gl.height, pictures: window.__take() };

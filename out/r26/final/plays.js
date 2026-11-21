// The final look: whole plays from step 0, pressed with the page's own Play button, watched frame by frame.
// A 2D play of the Mandelbrot shape, then 3D plays of the Mandelbrot shape, the Julia shape and Both.
//@
await openShape();
// one watcher for every play of this list
window.__watch = async (label) => {
  const frame = () => new Promise(r => requestAnimationFrame(() => r()));
  const t0 = performance.now(), gaps = [], card = [], says = [], rests = {};
  let last = null, prevT = t0, prevPos = -1, restStart = null, restAt = null, firstMove = null, hidden = 0;
  $('learnShapePlay').click();
  for (;;) {
    await frame();
    const now = performance.now(), s = L.shape.state(), say = $('learnShapeSay').textContent;
    gaps.push(now - prevT); prevT = now;
    if (firstMove === null && s.pos > 0) firstMove = Math.round(now - t0);
    if (say !== last) { says.push(say); last = say; }
    if (s.space === 3) { if (s.three && s.three.ok) card.push(s.ms.three); const c = document.querySelector('canvas.learn-shape-gl'); if (!c || c.hidden) hidden++; }
    if (Number.isInteger(s.pos) && s.pos === prevPos) { if (restStart === null) { restStart = now; restAt = s.pos; } }
    else if (restStart !== null) { rests[restAt] = Math.round(now - restStart); restStart = null; }
    prevPos = s.pos;
    if (!s.playing && s.pos >= 16) break;
    if (now - t0 > 90000) throw new Error(label + ': the play did not end in 90 s (pos ' + s.pos + ')');
  }
  const q = (a, f) => { const b = a.slice().sort((x, y) => x - y); return b.length ? +b[Math.min(b.length - 1, Math.floor(b.length * f))].toFixed(1) : null; };
  const mid = Object.entries(rests).filter(([k]) => +k > 0 && +k < 16).map(([, v]) => v);
  return { play: label, seconds: +((performance.now() - t0) / 1000).toFixed(1), firstMoveAtMs: firstMove, sentences: says.length, says,
    restsOnWholeSteps: mid.length, shortestRestMs: mid.length ? Math.min(...mid) : null, longestRestMs: mid.length ? Math.max(...mid) : null,
    frames: gaps.length, gapMedian: q(gaps, 0.5), gap95: q(gaps, 0.95), gapMax: q(gaps, 1), gapsOver34ms: gaps.filter(x => x > 34).length, gapsOver100ms: gaps.filter(x => x > 100).length,
    cardMsMedian: q(card, 0.5), cardMs95: q(card, 0.95), cardMsMax: q(card, 1), framesWithThe3dPictureHidden: hidden, end: { where: $('learnShapeWhere').textContent, say: $('learnShapeSay').textContent } };
};
return 'ready';
//@ sleep=0.4 shot=out/r26/final/NAME-2d-m-end.png
kindBar('m'); spaceBar(2); await sleep(300); $('learnShapeAgain').click(); await sleep(200);
return await window.__watch('2D, Mandelbrot shape');
//@ sleep=0.6 shot=out/r26/final/NAME-3d-m-end.png
spaceBar(3); await sleep(1200); $('learnShapeAgain').click(); await rest(300);
return await window.__watch('3D, Mandelbrot shape');
//@ sleep=0.6 shot=out/r26/final/NAME-3d-j-end.png
kindBar('j'); await sleep(600); $('learnShapeAgain').click(); await rest(300);
return await window.__watch('3D, Julia shape');
//@ sleep=0.6 shot=out/r26/final/NAME-3d-both-end.png
kindBar('both'); await sleep(600); $('learnShapeAgain').click(); await rest(300);
return await window.__watch('3D, Both');
//@ sleep=0.4 shot=out/r26/final/NAME-2d-both-end.png
spaceBar(2); await sleep(500); $('learnShapeAgain').click(); await sleep(200);
return await window.__watch('2D, Both');
//@ sleep=0.4 shot=out/r26/final/NAME-2d-j-end.png
kindBar('j'); await sleep(300); $('learnShapeAgain').click(); await sleep(200);
return await window.__watch('2D, Julia shape');

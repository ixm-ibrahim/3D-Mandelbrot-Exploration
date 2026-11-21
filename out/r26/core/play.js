// "Done" for cut 1: Mandelbrot shape, Julia shape and Both, in 2D and in 3D, play from step 0 to 16 without console
// errors. Run in both themes and at both sizes (the runner's --theme and --size). Speed: Fast, to keep the run short.
//@
await shapeOn({ kind: 'm', space: 2, pos: 0 });
const sp = $('learnShapeSpeed'); sp.value = 'fast'; sp.dispatchEvent(new Event('change', { bubbles: true }));
window.__play = async (kind, space) => {
  L.shape.set({ kind, space, c: [-0.1226, 0.7449, 0], pos: 0 });
  await sleep(150);
  const t0 = performance.now(); let frames = 0, worst = 0, last = t0, sentences = new Set(), notes = new Set(), q = new Set(), stop = false;
  const tick = now => { if (stop) return; frames++; worst = Math.max(worst, now - last); last = now; requestAnimationFrame(tick); };
  requestAnimationFrame(tick);
  $('learnShapePlay').click();
  for (let i = 0; i < 600; i++) {
    await sleep(50);
    const Sh = L.shape, pos = +$('learnShapePos').value;
    sentences.add($('learnShapeSay').textContent); notes.add($('learnShapeNote').hidden ? '' : $('learnShapeNote').textContent);
    if ($('learnShapePlay').textContent === 'Play') break;
  }
  stop = true;
  const secs = (performance.now() - t0) / 1000, s = L.shape.state();
  if (s.pos !== 16 || s.playing) throw new Error(kind + ' ' + space + 'D did not play to the end: ' + s.pos);
  return { what: (kind === 'm' ? 'Mandelbrot shape' : kind === 'j' ? 'Julia shape' : 'Both') + ', ' + space + 'D', seconds: +secs.toFixed(1), framesASecond: +(frames / secs).toFixed(0), longestFrameMs: +worst.toFixed(0),
    sentencesSeen: sentences.size, note: [...notes].filter(Boolean).join(' / '), endQuality: s.quality, endMs: s.ms, threeOk: s.threeOk, last: s.sentence };
};
return 'ready';
//@
return await window.__play('m', 2);
//@ sleep=0.3 shot=out/r26/core/NAME-m-2d-end.png clip=.bench-main
//@
return await window.__play('j', 2);
//@
return await window.__play('both', 2);
//@ sleep=0.3 shot=out/r26/core/NAME-both-2d-end.png clip=.bench-main
//@
return await window.__play('m', 3);
//@ sleep=0.5 shot=out/r26/core/NAME-m-3d-end.png clip=.bench-main
//@
return await window.__play('j', 3);
//@ sleep=0.5 shot=out/r26/core/NAME-j-3d-end.png clip=.bench-main
//@
return await window.__play('both', 3);
//@ sleep=0.5 shot=out/r26/core/NAME-both-3d-end.png clip=.bench-main

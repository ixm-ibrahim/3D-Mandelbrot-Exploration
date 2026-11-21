// Check 5: a phone-sized window (run with --size 390x800) and both themes: nothing overlaps, nothing is wider than
// the window, and the transport is in reach under the picture. The same list also serves the wide window.
//@
window.__boxes = () => {
  // every control of the transport, and the parts of the stage that could collide
  const els = [...document.querySelectorAll('#learnShapeBar .learn-where, #learnShapeBar .learn-speed, #learnShapeSay, #learnShapePos, #learnShapeTicks, #learnShapeBar .learn-btns .btn, #learnShapeBar .learn-shape-seg')].filter(e => e.getBoundingClientRect().width > 0);
  const R = els.map(e => { const r = e.getBoundingClientRect(); return { id: e.id || e.className, l: r.left, t: r.top, r: r.right, b: r.bottom }; });
  const hits = [];
  for (let i = 0; i < R.length; i++) for (let j = i + 1; j < R.length; j++) {
    const a = R[i], b = R[j], ox = Math.min(a.r, b.r) - Math.max(a.l, b.l), oy = Math.min(a.b, b.b) - Math.max(a.t, b.t);
    if (ox > 1 && oy > 1) hits.push([a.id, b.id, Math.round(ox), Math.round(oy)]);
  }
  // the ticks among themselves (their numbers must not run into each other)
  const ticks = [...$('learnShapeTicks').children].map(b => { const sp = document.createRange(); sp.selectNodeContents(b); return sp.getBoundingClientRect(); });
  let tickGap = 1e9; for (let i = 1; i < ticks.length; i++) tickGap = Math.min(tickGap, ticks[i].left - ticks[i - 1].right);
  const st = $('stage').getBoundingClientRect(), bar = $('learnShapeBar').getBoundingClientRect(), pin = $('pinToggle') && $('pinToggle').getBoundingClientRect().width ? $('pinToggle').getBoundingClientRect() : null;
  const say = $('learnShapeSay');
  return {
    window: [innerWidth, innerHeight], pageWidth: document.documentElement.scrollWidth, stage: [Math.round(st.width), Math.round(st.height)], bar: [Math.round(bar.width), Math.round(bar.height)],
    stagePlusTransport: Math.round(bar.bottom - st.top), shareOfWindow: +((bar.bottom - st.top) / innerHeight).toFixed(3),
    overlaps: hits, tickGapPx: +tickGap.toFixed(1), widerThanWindow: els.filter(e => e.getBoundingClientRect().right > innerWidth + 0.5).map(e => e.id || e.className),
    sentenceFits: say.scrollHeight <= say.clientHeight + 1, sentenceLines: Math.round(say.scrollHeight / parseFloat(getComputedStyle(say).lineHeight)),
    pinButton: pin ? [Math.round(pin.left - st.left), Math.round(pin.top - st.top), Math.round(pin.width), Math.round(pin.height)] : null,
    pin: LAB.pin ? LAB.pin.state() : null,
  };
};
const s = await shapeOn({ kind: 'm', space: 2, pos: 5 });
$('stage').scrollIntoView({ block: 'start' }); await sleep(300);
return { state: brief(s), boxes: window.__boxes() };
//@ sleep=0.3 shot=out/r26/core/NAME-1-m-05.png
//@
const s = L.shape.set({ kind: 'both', c: [-0.1226, 0.7449, 0], pos: 4.3 }); await sleep(200);
return { state: brief(s), panes: s.panes, side: s.side, boxes: window.__boxes() };
//@ sleep=0.3 shot=out/r26/core/NAME-2-both-4.3.png
//@
const s = L.shape.set({ kind: 'both', pos: 0 }); await sleep(200);
const b0 = window.__boxes();
const e = L.shape.set({ pos: 16 }); await sleep(200);
return { longestSentences: [s.sentence.length, e.sentence.length], at0: { fits: b0.sentenceFits, lines: b0.sentenceLines }, at16: { fits: window.__boxes().sentenceFits, lines: window.__boxes().sentenceLines } };
//@ sleep=0.3 shot=out/r26/core/NAME-3-both-16.png
//@
const s = L.shape.set({ kind: 'j', c: [-1, 0, 0], pos: 8 }); await sleep(200);
return { state: brief(s), boxes: window.__boxes() };
//@ sleep=0.3 shot=out/r26/core/NAME-4-j-08.png
//@
const s = L.shape.set({ kind: 'both', space: 3, pos: 6 }); await sleep(300);
return { state: brief(s), boxes: window.__boxes() };
//@ sleep=0.4 shot=out/r26/core/NAME-5-3d-both-06.png
//@
// the panel, scrolled to: the choices, the dials for c, the named values
L.shape.set({ kind: 'j', space: 2, pos: 8 }); await sleep(200);
$('learnPanel').scrollIntoView({ block: 'start' }); await sleep(400);
const wide = [...document.querySelectorAll('#learnPanel *')].filter(e => e.getBoundingClientRect().width > 0 && e.getBoundingClientRect().right > innerWidth + 0.5).map(e => e.id || e.className).slice(0, 8);
return { pageWidth: document.documentElement.scrollWidth, widerThanWindow: wide };
//@ sleep=0.3 shot=out/r26/core/NAME-6-panel.png
//@
$('learnShapeNotice').scrollIntoView({ block: 'end' }); await sleep(400);
return 'the lower part of the panel';
//@ sleep=0.3 shot=out/r26/core/NAME-7-panel-lower.png

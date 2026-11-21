// The final look at phone size (390 x 800): M5, M6, M7, the layout, the sentences, a pinch, and a whole play.
//@ sleep=0.4 shot=out/r26/final/NAME-1-2d-m-05.png
await openShape(); tick(5); await sleep(400);
const de = document.documentElement, st = box('stage'), bar = box('learnShapeBar');
return { window: [innerWidth, innerHeight], pageScrollWidth: de.scrollWidth, stage: st, transport: bar, stagePlusTransport: st[3] + bar[3], shareOfWindow: r2((st[3] + bar[3]) / innerHeight),
  transportBottom: bar[1] + bar[3], ...page() };
//@
// M5: the word before the row of shapes, and where that row stands against the lab's own tabs. M7: the sizes of the targets.
const cap = document.querySelector('.learn-shape-cap'), kinds = $('learnShapeKindBar'), tabs = $('mode-m').closest('fieldset, .seg-row, .modes, div');
const segs = [...document.querySelectorAll('#learnShapeSpaceBar .seg, #learnShapeKindBar .seg')].map(n => [n.textContent.trim(), ...box(n).slice(2)]);
const ticks = [...$('learnShapeTicks').children].map(n => box(n).slice(2)), sp = box('learnShapeSpeed');
return { capText: cap ? cap.textContent : null, capShown: !!cap && cap.offsetParent !== null, capBox: cap ? box(cap) : null, kindRow: box(kinds), labTabs: tabs ? box(tabs) : null,
  gapBetweenRowAndTabs: tabs ? box(tabs)[1] - (box(kinds)[1] + box(kinds)[3]) : null,
  segsWidthHeight: segs, tickBoxes: [ticks[0], ticks[8], ticks[16]], speedSelect: sp.slice(2), playButton: box('learnShapePlay').slice(2), stepButtons: [box('learnShapeBack').slice(2), box('learnShapeFwd').slice(2)],
  coarsePointer: matchMedia('(pointer: coarse)').matches };
//@ sleep=0.4 shot=out/r26/final/NAME-2-2d-both-05.png
// M6: Both on the phone: the labels against the big circle, and the buttons the stage carries
kindBar('both'); await sleep(300); tick(5); await sleep(400);
const s = L.shape.state(), btns = [...document.querySelectorAll('#stage button')].filter(b => b.offsetParent !== null).map(b => [b.textContent.trim(), ...box(b)]);
const stg = box('stage');
return { side: s.side, panes: s.panes, stageButtons: btns, stage: stg, circles: s.panes.map(P => ({ kind: P.kind, top: Math.round(stg[1] + P.y + P.h / 2 - 2 * 0.19 * Math.min(P.w, P.h)), right: Math.round(stg[0] + P.x + P.w / 2 + 2 * 0.19 * Math.min(P.w, P.h)) })), ...page() };
//@ sleep=0.4 shot=out/r26/final/NAME-3-2d-both-00.png
tick(0); await sleep(300); return page();
//@ sleep=0.6 shot=out/r26/final/NAME-4-3d-both-05.png
spaceBar(3); await sleep(1200); tick(5); const s = await rest(600);
const btns = [...document.querySelectorAll('#stage button')].filter(b => b.offsetParent !== null).map(b => [b.textContent.trim(), ...box(b)]);
return { side: s.side, panes: s.panes, stageButtons: btns, ...page(), hint: $('learnHint').textContent };
//@ sleep=0.6 shot=out/r26/final/NAME-5-3d-m-05.png
kindBar('m'); await sleep(500); tick(5); await rest(600); return page();
//@ sleep=0.6 shot=out/r26/final/NAME-6-3d-j-basilica-05.png
L.shape.set({ kind: 'j', c: [-1, 0, 0] }); await sleep(500); tick(5); await rest(600); return page();
//@
// every sentence of the six pictures at steps 0, 0.5, 1, 1.5, 5, 5.5, 12.5, 16: how many lines does it take on the phone?
const e = $('learnShapeSay'), lh = parseFloat(getComputedStyle(e).lineHeight) || 20, rows = [];
let most = 0, longest = '';
for (const sp of [2, 3]) { spaceBar(sp); await sleep(sp === 3 ? 900 : 300);
  for (const kd of ['m', 'j', 'both']) { kindBar(kd); await sleep(250);
    for (const p of [0, 0.5, 1, 1.5, 5, 5.5, 12.5, 16]) { await slider(p); await sleep(80); const rg = document.createRange(); rg.selectNodeContents(e); const tops = new Set([...rg.getClientRects()].map(r => Math.round(r.top))); const n = tops.size; rows.push([sp + 'D', kd, p, n, e.textContent.length]); if (n > most || (n === most && e.textContent.length > longest.length)) { most = n; longest = e.textContent; } } } }
const boxH = box(e)[3];
return { sentences: rows.length, mostLines: most, over3Lines: rows.filter(r => r[3] > 3), longest, sayBoxHeight: boxH, lineHeight: lh, sayOverflows: e.scrollHeight > e.clientHeight + 1 };
//@ sleep=0.4 shot=out/r26/final/NAME-7-2d-j-rabbit-pinched.png
// a scripted two-finger pinch on a flat picture zooms it (2D, Julia shape of the rabbit, step 6)
spaceBar(2); await sleep(300); L.shape.set({ kind: 'j', c: [-0.1226, 0.7449, 0] }); tick(6); await sleep(300);
const cv = $('learnShapeCanvas'), b = cv.getBoundingClientRect(), z0 = L.shape.state().view2.j.zoom;
const ev = (type, id, x, y) => cv.dispatchEvent(new PointerEvent(type, { bubbles: true, cancelable: true, pointerId: id, pointerType: 'touch', isPrimary: id === 11, button: 0, buttons: type === 'pointerup' ? 0 : 1, clientX: b.left + x, clientY: b.top + y }));
const mx = b.width / 2, my = b.height / 2;
ev('pointerdown', 11, mx - 30, my); ev('pointerdown', 12, mx + 30, my);
for (let i = 1; i <= 8; i++) { ev('pointermove', 11, mx - 30 - i * 8, my); ev('pointermove', 12, mx + 30 + i * 8, my); await frame(); }
ev('pointerup', 11, mx - 94, my); ev('pointerup', 12, mx + 94, my); await sleep(400);
const s = L.shape.state();
return { zoomBefore: z0, zoomAfter: r2(s.view2.j.zoom), resetShown: !$('learnShapeViewReset').hidden, ...page() };
//@ sleep=0.4 shot=out/r26/final/NAME-8-panel-top.png
// the panel under the transport (scrolled to): the choice Follow, the note, Which shape
$('learnShapeViewReset').click(); await sleep(200); kindBar('both'); await sleep(200);
$('learnFollow').scrollIntoView({ block: 'start' }); await sleep(300);
return { followBox: box('learnFollow'), scrollY: Math.round(scrollY) };
//@ sleep=0.4 shot=out/r26/final/NAME-9-panel-lower.png
$('learnShapeC').scrollIntoView({ block: 'start' }); await sleep(300);
return { named: [...document.querySelectorAll('#learnShapeCs button')].map(b => [b.textContent.trim(), ...box(b).slice(2)]), pageScrollWidth: document.documentElement.scrollWidth };
//@ sleep=0.5 shot=out/r26/final/NAME-10-play-end-3d-both.png
// a whole play on the phone, 3D, Both, from step 0, with the Play button
scrollTo(0, 0); spaceBar(3); await sleep(1200); $('learnShapeAgain').click(); await rest(300);
const t0 = performance.now(), says = []; let last = null, n = 0, gapsOver34 = 0, prev = t0;
$('learnShapePlay').click();
for (;;) { await frame(); const now = performance.now(); if (now - prev > 34) gapsOver34++; prev = now; n++; const s = L.shape.state(), say = $('learnShapeSay').textContent; if (say !== last) { says.push(say); last = say; } if (!s.playing && s.pos >= 16) break; if (now - t0 > 90000) fail('the play did not end'); }
return { seconds: r2((performance.now() - t0) / 1000), frames: n, gapsOver34, says, pageScrollWidth: document.documentElement.scrollWidth };

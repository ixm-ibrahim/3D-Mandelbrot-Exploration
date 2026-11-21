// The phone's defects (M5, M6, M7), at --size 390x800, on the page as joined (--page r26-fix-before --log before-phone)
// and on the mended page (--log after-phone). Also: does every sentence fit its three lines?
//@ sleep=0.5 shot=out/r26/fix/NAME-M5-after-the-tap.png
// M5: where the reader stands after tapping "A whole shape": the transport's row of shapes above the lab's own tabs
// (the reader has scrolled down to the choice "Follow" to tap it; the picture is pinned by then)
await openLearn(); $('learnFollowShape').closest('fieldset').scrollIntoView({ block: 'center' }); await sleep(400); await pickShape(); await sleep(100);
const row = document.querySelector('#learnShapeKindBar').getBoundingClientRect(), tabs = document.querySelector('fieldset.mode').getBoundingClientRect(), bar = $('learnShapeBar').getBoundingClientRect();
const cap = document.querySelector('.learn-shape-cap');
return { ...said(), scrollY: Math.round(scrollY), rowOfShapes: [Math.round(row.top), Math.round(row.bottom)], labTabs: [Math.round(tabs.top), Math.round(tabs.bottom)], gap: Math.round(tabs.top - row.bottom), transportBottom: Math.round(bar.bottom), wordBeforeTheRow: cap ? cap.textContent + ' ' + JSON.stringify(box(cap)) : null };
//@
// M7: the sizes of the small targets, and where everything stands
L.shape.pause(); $('learnShapeAgain').click(); scrollTo(0, 0); await sleep(400);
const sp =[...document.querySelectorAll('#learnShapeSpaceBar .seg span')].map(e => box(e)), kd = [...document.querySelectorAll('#learnShapeKindBar .seg span')].map(e => box(e));
const st = box('stage'), bar = box('learnShapeBar');
return { space2D3D: sp, kinds: kd, tick: box($('learnShapeTicks').children[3]), speed: box('learnShapeSpeed'), stage: st, transport: bar, together: st[3] + bar[3], shareOfWindow: +((bar[1] + bar[3] - st[1]) / innerHeight).toFixed(3), pageWidth: document.documentElement.scrollWidth, coarse: matchMedia('(pointer: coarse)').matches };
//@ sleep=0.4 shot=out/r26/fix/NAME-M6-2d-both-00.png clip=#stage
// M6: Both on the phone: the labels, the top of the big circle and its number 2
kindBar('both'); await sleep(200); return { ...said(), panes: L.shape.state().panes };
//@ sleep=0.4 shot=out/r26/fix/NAME-M6-2d-both-16.png clip=#stage
tick(16); await sleep(300); return said();
//@ sleep=0.4 shot=out/r26/fix/NAME-M6-3d-both-05-zoomed.png clip=#stage
spaceBar(3); await sleep(900); tick(5); await sleep(300);
const cv = $('learnShapeCanvas'); ptr(cv, 'pointerdown', 90, 120); ptr(cv, 'pointermove', 120, 150); await frame(); ptr(cv, 'pointerup', 120, 150);
for (let i = 0; i < 3; i++) { wheel($('stage'), 90, 120, -200); await sleep(120); }
const s = await rest(700); return { ...said(), view: s.view3 };
//@ sleep=0.4 shot=out/r26/fix/NAME-3d-m-05.png
// the 3D picture as it opens, on the phone
$('learnShapeViewReset').click(); kindBar('m'); await sleep(300); const s = await rest(600); return { ...said(), view: s.view3 };
//@
// every sentence against its box: three lines high, nothing cut off (2D and 3D, the three kinds, the first steps, a late one, the end)
const e = $('learnShapeSay'), rows = [], long = [];
const look = (tag) => { const t = e.textContent; rows.push(t.length); if (e.scrollHeight > e.clientHeight + 1) long.push(tag + ': ' + e.scrollHeight + ' of ' + e.clientHeight + ' px: ' + t); };
for (const sp of [2, 3]) { spaceBar(sp); await sleep(sp === 3 ? 900 : 200); for (const kd of ['m', 'j', 'both']) { kindBar(kd); await sleep(250); for (const p of [0, 0.5, 1, 1.5, 2, 9, 12.5, 13, 16]) { await slider(p); await sleep(sp === 3 ? 260 : 30); look(sp + 'D ' + kd + ' ' + p); } } }
spaceBar(2); kindBar('m'); await slider(0);
return { sentences: rows.length, longest: Math.max(...rows), boxHeight: e.clientHeight, tooLong: long };
//@ sleep=0.3 shot=out/r26/fix/NAME-play-end.png
// one play on the phone, Fast, with every sentence it shows
$('learnShapeSpeed').value = 'fast'; $('learnShapeSpeed').dispatchEvent(new Event('change', { bubbles: true }));
const t0 = performance.now(), seen = []; let last = null; $('learnShapePlay').click();
for (let i = 0; i < 900; i++) { const s = said(); if (s.say !== last) { seen.push([Math.round(performance.now() - t0), +s.slider.toFixed(2), s.say]); last = s.say; } if (s.play === 'Play' && s.slider >= 16) break; await sleep(30); }
return { seconds: +((performance.now() - t0) / 1000).toFixed(1), seen };

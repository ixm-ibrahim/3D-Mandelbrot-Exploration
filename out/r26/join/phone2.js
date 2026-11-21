// Things the builders left untried, at phone size (run with --size 390x800): do the longest sentences fit their
// box, does anything stand wider than the window, and does a pinch with two (scripted) fingers zoom a flat picture.
//@
await shapeOn({ kind: 'both', space: 2, pos: 16, c: [-0.1226, 0.7449, 0] });
const say = $('learnShapeSay'), rows = [];
const fits = label => { const s = L.shape.state(); rows.push({ what: label, letters: s.sentence.length, fits: say.scrollHeight <= say.clientHeight + 1, boxPx: say.clientHeight, textPx: say.scrollHeight, sentence: s.sentence }); };
fits('power 2, both, 2D, step 16');
S.n = 3; go(); await sleep(200); L.shape.set({ pos: 16 }); fits('power 3, both, 2D, step 16 (the longest of all)');
S.n = 2; go(); await sleep(200);
L.shape.set({ pos: 0 }); fits('both, step 0');
L.shape.set({ pos: 0.5 }); fits('both, step 1 under way');
L.shape.set({ pos: 1 }); fits('both, step 1');
L.shape.set({ space: 3, pos: 0 }); fits('both, 3D, step 0');
L.shape.set({ pos: 4.5 }); fits('both, 3D, between steps');
S.n = -2; go(); await sleep(200);
L.shape.set({ space: 2, kind: 'm', pos: 1.5 }); await sleep(200); fits('power -2, Mandelbrot shape, between 1 and 2 (new sentence)');
L.shape.set({ kind: 'both', pos: 16 }); await sleep(200); fits('power -2, both, step 16 (new sentence)');
S.n = 2; go(); await sleep(200);
L.shape.set({ kind: 'both', space: 2, pos: 8 });
const wide = document.documentElement.scrollWidth, tooLong = rows.filter(r => !r.fits);
return { window: innerWidth + 'x' + innerHeight, pageWidth: wide, nothingWiderThanTheWindow: wide <= innerWidth, sentencesThatDoNotFit: tooLong.length, rows };
//@
// pinch on the flat Mandelbrot picture: two fingers 60 px apart moving to 150 px apart
L.shape.set({ kind: 'm', space: 2, pos: 8 });
await sleep(200);
const cv = $('learnShapeCanvas'), z0 = L.shape.state().view2.m.zoom;
const t = (type, id, x, y) => ptr(cv, type, x, y, { pointerId: id, pointerType: 'touch' });
t('pointerdown', 21, 150, 120); t('pointerdown', 22, 210, 120);
for (let i = 1; i <= 9; i++) { t('pointermove', 21, 150 - 5 * i, 120); t('pointermove', 22, 210 + 5 * i, 120); await frame(); await frame(); }
t('pointerup', 21, 105, 120); t('pointerup', 22, 255, 120);
await sleep(400);
const s = L.shape.state(), z1 = s.view2.m.zoom;
if (!(Math.abs(z1 / z0 - 2.5) < 0.15)) fail('a pinch to two and a half times the spread should zoom by as much: ' + z0 + ' -> ' + z1);
// one finger now moves the zoomed picture
const x0 = s.view2.m.x;
t('pointerdown', 23, 180, 120); t('pointermove', 23, 150, 120); await frame(); await frame(); t('pointerup', 23, 150, 120);
await sleep(300);
const x1 = L.shape.state().view2.m.x;
return { zoomBefore: z0, zoomAfterThePinch: +z1.toFixed(2), middleBefore: +x0.toFixed(3), middleAfterOneFingerMoved: +x1.toFixed(3), moved: x1 !== x0, resetShown: shown('learnShapeViewReset') };
//@ sleep=0.3 shot=out/r26/join/NAME-pinched.png
//@
$('learnShapeViewReset').click(); await sleep(300);
return brief(L.shape.state());

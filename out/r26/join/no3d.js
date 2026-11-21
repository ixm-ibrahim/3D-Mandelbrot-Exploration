// The page without the 3D module (dist/r26-join-no3d.html: the frozen copy plus 66, 67 and the style sheet, no 68):
// the 2D pictures must work fully and 3D must show the plain sentence, with the joiner's changes in 67 as well.
//@
const s = await shapeOn({ kind: 'both', space: 2, pos: 8, c: [-0.1226, 0.7449, 0] });
if (LAB.learnShape3d) fail('this page should have no 3D module');
return brief(s);
//@ sleep=0.3 shot=out/r26/join/NAME-2d-both-08.png clip=.bench-main
//@
const s = L.shape.set({ space: 3 });
await sleep(300);
const note = $('learnShapeNote');
if (note.hidden || !/missing from this copy/.test(note.textContent)) fail('3D should show the sentence: ' + note.textContent);
S.n = -2; go(); await sleep(200);
const neg = [L.shape.set({ kind: 'm', pos: 1 }).sentence, L.shape.set({ kind: 'both', pos: 3 }).sentence];
S.n = 2; go(); await sleep(200);
L.shape.set({ kind: 'm', pos: 0 }); $('learnShapePlay').click(); await sleep(1200); $('learnShapePlay').click(); await sleep(300);
const t = L.shape.state();
return { note: note.textContent, threeOk: t.threeOk, sentencesWithPowerMinus2: neg, playedTo: +t.pos.toFixed(2), canvases: document.querySelectorAll('canvas.learn-shape-gl').length };
//@ sleep=0.3 shot=out/r26/join/NAME-3d-note.png clip=.bench-main
//@
return brief(L.shape.set({ space: 2, pos: 5 }));

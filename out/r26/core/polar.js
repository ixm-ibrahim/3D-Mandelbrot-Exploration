// A power that is not a whole number (2.5: the polar form): the coarse picture while the diamond is held (half a
// sample to a pixel each way) must lie where the fine one lies. Also power 3 and the modifiers, for the eye.
//@
await shapeOn({ kind: 'both', space: 2, pos: 5, c: [-0.4, 0.3, 0] });
S.n = 2.5; go(); await sleep(300);
const cv = $('learnShapeCanvas'), s0 = L.shape.state(), d0 = s0.diamonds[1];
ptr(cv, 'pointerdown', d0[0], d0[1]);
for (let i = 1; i <= 6; i++) { ptr(cv, 'pointermove', d0[0] + 5 * i, d0[1] - 3 * i); await frame(); await frame(); }
const held = L.shape.state();
window.__d = [d0[0] + 30, d0[1] - 18];
return { quality: held.quality, ms: held.ms, c: held.c };
//@ shot=out/r26/core/polar-1-held.png clip=#stage
//@
const cv = $('learnShapeCanvas');
ptr(cv, 'pointerup', window.__d[0], window.__d[1]); await sleep(400);
const s = L.shape.state();
return { quality: s.quality, ms: s.ms, c: s.c, sentence: L.shape.goto(16).sentence };
//@ sleep=0.3 shot=out/r26/core/polar-2-rest-16.png clip=.bench-main
//@
S.n = 3; go(); await sleep(300);
return brief(L.shape.set({ kind: 'both', c: [0.2, 0.6, 0], pos: 16 }));
//@ sleep=0.3 shot=out/r26/core/polar-3-power3-16.png clip=.bench-main
//@
S.n = 2; S.abs = [1, 1, 0]; go(); await sleep(300);
return brief(L.shape.set({ kind: 'both', c: [-0.5, -0.5, 0], pos: 16 }));
//@ sleep=0.3 shot=out/r26/core/polar-4-absxy-16.png clip=.bench-main
//@
S.abs = [0, 0, 0]; S.n = -2; go(); await sleep(300);
const a = L.shape.set({ kind: 'both', c: [0.3, 0.2, 0], pos: 1 });
return { at1: a.sentence, at0to1: L.shape.set({ pos: 0.5 }).sentence, end: L.shape.set({ pos: 16 }).sentence };
//@ sleep=0.3 shot=out/r26/core/polar-5-power-minus2-16.png clip=.bench-main
//@
S.n = 2; go(); await sleep(200);
return 'power back to 2';

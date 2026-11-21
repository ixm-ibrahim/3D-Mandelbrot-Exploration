// A first look at the joined page: the whole window, "A whole shape" on. NAME in a path is the log's name.
//@
const s = await shapeOn({ kind: 'm', space: 2, pos: 0 });
return { opening: LAB.APPROACHES[S.approach].name, state: brief(s) };
//@ sleep=0.4 shot=out/r26/join/NAME-2d-m-00.png
//@
return brief(L.shape.goto(2));
//@ sleep=0.4 shot=out/r26/join/NAME-2d-m-02.png
//@
return brief(L.shape.goto(5));
//@ sleep=0.4 shot=out/r26/join/NAME-2d-m-05.png
//@
return brief(L.shape.goto(16));
//@ sleep=0.4 shot=out/r26/join/NAME-2d-m-16.png
//@
return brief(L.shape.set({ kind: 'both', c: [-0.1226, 0.7449, 0], pos: 8 }));
//@ sleep=0.4 shot=out/r26/join/NAME-2d-both-rabbit-08.png
//@
const s = L.shape.set({ kind: 'm', space: 3, pos: 0 });
if (!s.threeOk || s.note) fail('3D should draw: ' + s.note);
return brief(s);
//@ sleep=0.8 shot=out/r26/join/NAME-3d-m-00.png
//@
return brief(L.shape.goto(1));
//@ sleep=0.8 shot=out/r26/join/NAME-3d-m-01.png
//@
return brief(L.shape.goto(3));
//@ sleep=0.8 shot=out/r26/join/NAME-3d-m-03.png
//@
return brief(L.shape.goto(16));
//@ sleep=0.8 shot=out/r26/join/NAME-3d-m-16.png
//@
const name = await approach('fold');
const s = L.shape.set({ kind: 'j', c: [-1, 0, 0], pos: 8 });
return { approach: name, state: brief(s), rule: $('learnShapeRule').textContent, notice: $('learnShapeNotice').textContent };
//@ sleep=0.8 shot=out/r26/join/NAME-3d-j-basilica-fold-08.png
//@
const name = await approach('mercator');
const s = L.shape.set({ kind: 'both', c: [-0.1226, 0.7449, 0], pos: 5 });
return { approach: name, state: brief(s), panes: s.panes, diamonds: s.diamonds };
//@ sleep=0.8 shot=out/r26/join/NAME-3d-both-rabbit-05.png
//@
return brief(L.shape.set({ pos: 2.35 }));
//@ sleep=0.8 shot=out/r26/join/NAME-3d-both-rabbit-02.35.png

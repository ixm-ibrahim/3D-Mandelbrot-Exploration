// Check 2: the flat pictures. Mandelbrot shape, Julia shape for c = -1 and for the rabbit, at steps 0 1 2 3 5 8 16;
// Both; and pictures caught between two steps.
//@
const s = await shapeOn({ kind: 'm', space: 2, pos: 0 }); return brief(s);
//@ sleep=0.3 shot=out/r26/core/flat-m-00.png clip=.bench-main
//@
return brief(L.shape.goto(1));
//@ sleep=0.3 shot=out/r26/core/flat-m-01.png clip=.bench-main
//@
return brief(L.shape.goto(2));
//@ sleep=0.3 shot=out/r26/core/flat-m-02.png clip=.bench-main
//@
return brief(L.shape.goto(3));
//@ sleep=0.3 shot=out/r26/core/flat-m-03.png clip=.bench-main
//@
return brief(L.shape.goto(5));
//@ sleep=0.3 shot=out/r26/core/flat-m-05.png clip=.bench-main
//@
return brief(L.shape.goto(8));
//@ sleep=0.3 shot=out/r26/core/flat-m-08.png clip=.bench-main
//@
return brief(L.shape.goto(16));
//@ sleep=0.3 shot=out/r26/core/flat-m-16.png clip=.bench-main
//@
return brief(L.shape.set({ kind: 'j', c: [-1, 0, 0], pos: 0 }));
//@ sleep=0.3 shot=out/r26/core/flat-j-basilica-00.png clip=.bench-main
//@
return brief(L.shape.goto(1));
//@ sleep=0.3 shot=out/r26/core/flat-j-basilica-01.png clip=.bench-main
//@
return brief(L.shape.goto(2));
//@ sleep=0.3 shot=out/r26/core/flat-j-basilica-02.png clip=.bench-main
//@
return brief(L.shape.goto(3));
//@ sleep=0.3 shot=out/r26/core/flat-j-basilica-03.png clip=.bench-main
//@
return brief(L.shape.goto(5));
//@ sleep=0.3 shot=out/r26/core/flat-j-basilica-05.png clip=.bench-main
//@
return brief(L.shape.goto(8));
//@ sleep=0.3 shot=out/r26/core/flat-j-basilica-08.png clip=.bench-main
//@
return brief(L.shape.goto(16));
//@ sleep=0.3 shot=out/r26/core/flat-j-basilica-16.png clip=.bench-main
//@
return brief(L.shape.set({ kind: 'j', c: [-0.1226, 0.7449, 0], pos: 0 }));
//@ sleep=0.3 shot=out/r26/core/flat-j-rabbit-00.png clip=.bench-main
//@
return brief(L.shape.goto(1));
//@ sleep=0.3 shot=out/r26/core/flat-j-rabbit-01.png clip=.bench-main
//@
return brief(L.shape.goto(2));
//@ sleep=0.3 shot=out/r26/core/flat-j-rabbit-02.png clip=.bench-main
//@
return brief(L.shape.goto(3));
//@ sleep=0.3 shot=out/r26/core/flat-j-rabbit-03.png clip=.bench-main
//@
return brief(L.shape.goto(5));
//@ sleep=0.3 shot=out/r26/core/flat-j-rabbit-05.png clip=.bench-main
//@
return brief(L.shape.goto(8));
//@ sleep=0.3 shot=out/r26/core/flat-j-rabbit-08.png clip=.bench-main
//@
return brief(L.shape.goto(16));
//@ sleep=0.3 shot=out/r26/core/flat-j-rabbit-16.png clip=.bench-main
//@
return brief(L.shape.set({ kind: 'both', c: [-0.1226, 0.7449, 0], pos: 0 }));
//@ sleep=0.3 shot=out/r26/core/flat-both-00.png clip=.bench-main
//@
return brief(L.shape.goto(6));
//@ sleep=0.3 shot=out/r26/core/flat-both-06.png clip=.bench-main
//@
return brief(L.shape.goto(16));
//@ sleep=0.3 shot=out/r26/core/flat-both-16.png clip=.bench-main
//@
return brief(L.shape.set({ kind: 'm', pos: 2.3 }));
//@ sleep=0.3 shot=out/r26/core/flat-between-m-2.30.png clip=.bench-main
//@
return brief(L.shape.set({ kind: 'm', pos: 2.75 }));
//@ sleep=0.3 shot=out/r26/core/flat-between-m-2.75.png clip=.bench-main
//@
return brief(L.shape.set({ kind: 'j', c: [-1, 0, 0], pos: 1.35 }));
//@ sleep=0.3 shot=out/r26/core/flat-between-j-1.35.png clip=.bench-main
//@
return brief(L.shape.set({ kind: 'both', c: [-0.1226, 0.7449, 0], pos: 4.3 }));
//@ sleep=0.3 shot=out/r26/core/flat-between-both-4.30.png clip=.bench-main
//@
// the other named values: are the names true of the pictures?
return brief(L.shape.set({ kind: 'j', c: [0, 1, 0], pos: 16 }));
//@ sleep=0.3 shot=out/r26/core/flat-j-dendrite-16.png clip=.bench-main
//@
return brief(L.shape.set({ kind: 'j', c: [0, 0, 0], pos: 16 }));
//@ sleep=0.3 shot=out/r26/core/flat-j-disc-16.png clip=.bench-main

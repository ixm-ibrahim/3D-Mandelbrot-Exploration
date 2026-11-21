// M2, a trial: deep steps of the rougher approaches with the near side of a skin more solid (the module's o.look),
// to see whether the form then reads. Four settings of how see-through the near side is, face on:
// 0.13 (as built), 0.35, 0.6, 0.85. Approaches: Turning plane along, two planes, Lathe, Mandelbulb, one plane.
//@
await openShape(); kindBar('m'); spaceBar(3); await sleep(900); window.__ids = ['turnalong', 'fold', 'lathe', 'bulb', 'mercator']; window.__fr = [0.13, 0.35, 0.6, 0.85];
return 'ready';
//@ repeat=20 sleep=0.2 shot=out/r26/fix/trylook-NAME-##.png clip=#stage
const i = __I__, id = window.__ids[Math.floor(i / 4)], fr = window.__fr[i % 4];
await approach(id); L.shape.glass.look = fr === 0.13 ? null : { front: [fr, 0.95], back: [0.12 * (1 - fr), 0.52 * (1 - fr)], glow: 0.55 * (1 - fr) };
L.shape.set({ pos: 16 }); const s = await rest(700); return { id, front: fr };
//@ repeat=10 sleep=0.2 shot=out/r26/fix/trylook-NAME-s12-##.png clip=#stage
const i = __I__, id = window.__ids[Math.floor(i / 2)], fr = [0.13, 0.6][i % 2];
await approach(id); L.shape.glass.look = fr === 0.13 ? null : { front: [fr, 0.95], back: [0.12 * (1 - fr), 0.52 * (1 - fr)], glow: 0.55 * (1 - fr) };
L.shape.set({ pos: 10 }); const s = await rest(700); return { id, front: fr, step: 10 };

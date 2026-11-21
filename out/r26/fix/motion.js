// E2, looked at closely: a 3D step under way, place by place (the slider by hand, each picture at rest and fine).
// Step 3, step 8 and step 12 of the Mandelbrot shape with the opening approach; then step 8 of "Turning plane, along".
//@
await openShape(); kindBar('m'); spaceBar(3); await sleep(900);
window.__at = [2, 2.05, 2.1, 2.15, 2.25, 2.4, 2.6, 2.8, 3, 7, 7.05, 7.1, 7.15, 7.25, 7.4, 7.6, 7.8, 8, 11, 11.1, 11.25, 11.4, 11.7, 12];
return 'ready';
//@ repeat=24 sleep=0.15 shot=out/r26/fix/motion-NAME-##.png clip=#stage
const p = window.__at[__I__]; await slider(p); const s = await rest(350); return { pos: p, asked: s.three.levels.map(l => l.k + ':a' + l.alpha.toFixed(2) + ':t' + (l.tint || 0).toFixed(2) + ':s' + (l.solid || 0).toFixed(2)).join(' ') };
//@
await approach('turnalong'); await sleep(300); window.__at2 = [7, 7.1, 7.25, 7.5, 8, 12]; return 'turnalong';
//@ repeat=6 sleep=0.15 shot=out/r26/fix/motion-NAME-turnalong-##.png clip=#stage
const p = window.__at2[__I__]; await slider(p); const s = await rest(500); return { pos: p };

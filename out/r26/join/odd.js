// Other settings in the joined page, 3D: powers 3, 2.5 and -2, the modifiers, and every approach once.
// For each: does the picture draw, what the sentence says, and how much of the pane is not background
// (read from the 3D module's own canvas through a 2D copy, so an empty picture shows as 0).
//@
await shapeOn({ kind: 'm', space: 3, pos: 0 });
window.__cover = () => {
  const gl = document.querySelector('canvas.learn-shape-gl');
  if (!gl || gl.hidden) return -1;
  const t = document.createElement('canvas'); t.width = 160; t.height = Math.round(160 * gl.height / gl.width);
  const g = t.getContext('2d'); g.drawImage(gl, 0, 0, t.width, t.height);
  const d = g.getImageData(0, 0, t.width, t.height).data, bg = [d[0], d[1], d[2]];
  let n = 0; for (let i = 0; i < d.length; i += 4) if (Math.abs(d[i] - bg[0]) + Math.abs(d[i + 1] - bg[1]) + Math.abs(d[i + 2] - bg[2]) > 12) n++;
  return +(100 * n / (t.width * t.height)).toFixed(1);
};
window.__row = async (label, pos) => { const s = L.shape.goto(pos); await sleep(250); return { what: label, pos, covered: window.__cover() + ' %', sentence: s.sentence, note: s.note, where: $('learnShapeWhere').textContent, levels: s.three ? s.three.levels.map(l => l.k + ':' + l.alpha.toFixed(2)).join(' ') : '' }; };
return 'ready';
//@
// power 3
S.n = 3; go(); await sleep(300);
L.shape.set({ kind: 'both', c: [-0.3, 0.4, 0] });
return [await window.__row('power 3, both', 0), await window.__row('power 3, both', 1), await window.__row('power 3, both', 4), await window.__row('power 3, both', 16)];
//@ sleep=0.3 shot=out/r26/join/NAME-power3-both-16.png clip=#stage
//@
S.n = 2.5; go(); await sleep(300);
return [await window.__row('power 2.5, both', 1), await window.__row('power 2.5, both', 4), await window.__row('power 2.5, both', 4.4), await window.__row('power 2.5, both', 16)];
//@ sleep=0.3 shot=out/r26/join/NAME-power2_5-both-16.png clip=#stage
//@
// a negative power: the Mandelbrot shape loses everything at the first step (its dot starts at 0)
S.n = -2; go(); await sleep(300);
const rows = [];
L.shape.set({ kind: 'm' });
rows.push(await window.__row('power -2, Mandelbrot shape', 0), await window.__row('power -2, Mandelbrot shape', 0.5), await window.__row('power -2, Mandelbrot shape', 1), await window.__row('power -2, Mandelbrot shape', 2), await window.__row('power -2, Mandelbrot shape', 16));
L.shape.set({ kind: 'both' });
rows.push(await window.__row('power -2, both', 1), await window.__row('power -2, both', 3));
L.shape.set({ kind: 'j' });
rows.push(await window.__row('power -2, Julia shape', 1), await window.__row('power -2, Julia shape', 3));
return rows;
//@ sleep=0.3 shot=out/r26/join/NAME-power-2-j-03.png clip=#stage
//@
// the same on the 2D page, for comparison of the words
S.n = -2; go();
L.shape.set({ kind: 'm', space: 2 });
const a = [await (async () => { const s = L.shape.goto(1); return s.sentence; })(), await (async () => { const s = L.shape.goto(0.5); return s.sentence; })()];
L.shape.set({ space: 3 });
return a;
//@
// modifiers at power 2
S.n = 2; S.abs = [1, 1, 0]; S.flip = [1, 0]; go(); await sleep(300);
L.shape.set({ kind: 'both', c: [-0.1226, 0.7449, 0] });
const rows = [await window.__row('|x| |y| flip y, both', 3), await window.__row('|x| |y| flip y, both', 8)];
S.abs = [0, 0, 0]; S.flip = [0, 0]; go(); await sleep(200);
return rows;
//@ sleep=0.3 shot=out/r26/join/NAME-modifiers-both-08.png clip=#stage
//@
// every approach once: Both, the rabbit c, steps 0, 3, 9
const rows = [];
for (const a of LAB.APPROACHES) {
  await approach(a.id);
  L.shape.set({ kind: 'both', c: [-0.1226, 0.7449, 0] });
  const r0 = await window.__row(a.id, 0), r3 = await window.__row(a.id, 3), r9 = await window.__row(a.id, 9), s = L.shape.state();
  rows.push(a.id + ': ' + (s.threeOk && !s.note ? 'draws' : 'DOES NOT DRAW (' + s.note + ')') + ', covered at 0 / 3 / 9: ' + [r0, r3, r9].map(r => r.covered).join(' / ') + ', cut sentence ' + ($('learnShapeNotice').textContent.includes('cutting the 3D shape') ? 'shown' : 'not shown'));
}
await approach('mercator');
return rows;

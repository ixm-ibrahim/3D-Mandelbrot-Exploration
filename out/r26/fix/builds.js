// The 3D module's program text changed (one more way to use its loop, columns(), and a skin's `solid`). Does a
// program still build as fast, and does a picture cost the card the same? A view of its own, nine approaches:
// the time the module itself notes for building each program, and the time of fifteen 'move' and fifteen 'still'
// pictures of step 8 (600 x 450 box, the card waited for after each): the middle one of fifteen, and the quickest.
// Run on the page as joined (--page r26-fix-before --log builds-before) and on the mended page (--log builds-after).
//@
await openLearn();
const T = LAB.learnShape3d.make(); document.body.appendChild(T.canvas); T.canvas.style.cssText = 'position:fixed;left:0;top:0;width:600px;height:450px;z-index:99;';
const o = q => ({ panes: [{ kind: 'm', rect: [0, 0, 600, 450] }], c: [0, 0, 0], levels: [{ k: 8, alpha: 1, tint: 0 }, { k: 7, alpha: 0.22, tint: 0, ghost: 0.55 }], yaw: -0.62, pitch: 0.4, zoom: 1, quality: q, lod: q === 'move' ? 1 : 0, colours: { bg: [0.03, 0.04, 0.06], body: [0.85, 0.68, 0.36], warn: [0.9, 0.4, 0.35], ink: [0.9, 0.9, 0.9] } });
const rows = {};
for (const id of ['mercator', 'fold', 'turnalong', 'lathe', 'bulb', 'pillow', 'alongonce', 'pulledplane', 'quat4']) {
  await approach(id); await sleep(400);
  T.draw(o('move'));
  const mv = T.time(o('move'), 15), st = T.time(o('still'), 15);
  rows[id] = { moveMs: +med(mv).toFixed(1), moveLeast: +Math.min(...mv).toFixed(1), stillMs: +med(st).toFixed(1), stillLeast: +Math.min(...st).toFixed(1) };
}
const b = T.stats().builds; for (const k in b) { const id = k.split('|')[0]; if (rows[id]) rows[id].buildMs = Math.round(b[k]); }
T.dispose(); await approach('mercator');
return rows;

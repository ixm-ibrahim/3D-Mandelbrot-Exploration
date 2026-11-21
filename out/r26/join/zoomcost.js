// What a picture costs the graphics card when it is zoomed in, on a stage of the page's size (862 x 511):
// the module's own time() (draw, then wait for the card), median of 5, for 'still' at each of its three
// finenesses and for 'move' at its finest. One pane, the Julia shape of c = -1, the shape and its ghost.
//@
await shapeOn({ kind: 'm', space: 2, pos: 0 });
const v = LAB.learnShape3d.make();
v.canvas.style.cssText = 'position:fixed;left:0;top:0;width:862px;height:511px;z-index:99999;';
document.body.appendChild(v.canvas);
window.__v = v;
const css = getComputedStyle(document.documentElement), hex = h => { h = h.trim().replace('#', ''); return [0, 2, 4].map(i => parseInt(h.slice(i, i + 2), 16) / 255); };
window.__cols = { bg: hex(css.getPropertyValue('--stage')), body: hex(css.getPropertyValue('--brass')), warn: hex(css.getPropertyValue('--bad')), ink: hex(css.getPropertyValue('--ink')) };
window.__cost = async (id, steps, zooms) => {
  await approach(id);
  const rows = [];
  for (const k of steps) for (const zoom of zooms) {
    const o = q => Object.assign({ panes: [{ kind: 'j', rect: [0, 0, 862, 511] }], c: [-1, 0, 0], levels: [{ k, alpha: 1, tint: 0 }, { k: k - 1, alpha: 0.22, tint: 0, ghost: 0.55 }], yaw: -0.62, pitch: 0.4, zoom, colours: window.__cols }, q);
    const t = q => r1(med(v.time(o(q), 5)));
    rows.push(id + ', step ' + k + ', zoom ' + zoom + ': still ' + [0, 1, 2].map(l => t({ quality: 'still', lod: l })).join(' / ') + ' ms; move (finest) ' + t({ quality: 'move', lod: 0 }) + ' ms');
    await sleep(30);
  }
  return rows;
};
return 'ready';
//@
return await window.__cost('mercator', [3, 8, 12], [1, 2, 4, 6]);
//@
return await window.__cost('fold', [3, 8, 12], [1, 2, 4, 6]);
//@
return await window.__cost('pillow', [3, 8, 12], [1, 2, 4, 6]);
//@
window.__v.dispose();
return await approach('mercator');

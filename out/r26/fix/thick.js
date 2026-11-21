// M1: how thick is the bite of each step, in pixels of the picture, and from which step does the page call it
// "too fine to see"? Read from the page's own tallies (LEARN.shape.state().thick, .above, .thin).
//@
await openShape(); const out = {}, f = a => (a ? a.map(v => (v === null ? 'inf' : (+v).toFixed(2))).join(' ') : null);
const st = L.shape.state(); out.stage = [st.panes[0].w, st.panes[0].h];
out['2D m'] = { px: f(st.thick[0]), thin: st.thin };
kindBar('j'); await sleep(200); let s = L.shape.state(); out['2D j, c as it opens'] = { px: f(s.thick[0]), thin: s.thin };
L.shape.set({ c: [-1, 0, 0] }); await sleep(200); s = L.shape.state(); out['2D j, c = -1'] = { px: f(s.thick[0]), thin: s.thin };
L.shape.set({ c: [-0.4, 0.3, 0] }); kindBar('both'); await sleep(200); s = L.shape.state(); out['2D both'] = { px: s.thick.map(f), thin: s.thin };
// zoomed in three times on the left picture: the same steps
wheel($('stage'), 150, 255, -730); await sleep(400); s = L.shape.state(); out['2D both, left picture zoomed ' + s.view2.m.zoom.toFixed(1)] = { px: s.thick.map(f), thin: s.thin };
$('learnShapeViewReset').click(); kindBar('m'); spaceBar(3); await sleep(1000); s = await rest();
const unit = 0.2 * Math.min(s.panes[0].w, s.panes[0].h);
out['3D m, one plane'] = { px: f(s.above[0].thick.map(t => t * unit)), thin: s.thin, columnsMs: s.above[0].ms, left: s.above[0].left.join(' ') };
for (const id of ['fold', 'turnalong', 'lathe', 'bulb', 'pillow']) { await approach(id); s = await rest(900); const a = s.above.find(x => x.kind === 'm'); out['3D m, ' + id] = { px: f(a.thick.map(t => t * unit)), thin: s.thin, columnsMs: a.ms }; }
await approach('mercator'); spaceBar(2);
return out;

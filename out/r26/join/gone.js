// The words when nothing is left of a picture (the joiner's change in 67-learn-shape.js), and that the ordinary
// sentences are what they were. 2D: asked of the picture itself. 3D: only the one certain case, a Mandelbrot shape
// whose every point the first step throws out (a negative power).
//@
await shapeOn({ kind: 'm', space: 2, pos: 0, c: [-0.1226, 0.7449, 0] });
window.__say = async (o, at) => { L.shape.set(o); const rows = []; for (const p of at) { L.shape.set({ pos: p }); await sleep(120); rows.push(p + ': ' + L.shape.state().sentence); } return rows; };
return 'ready';
//@
// the plain power 2: nothing changes
const out = {};
for (const space of [2, 3]) for (const kind of ['m', 'j', 'both']) out[kind + ' ' + space + 'D'] = await window.__say({ kind, space }, [0, 0.5, 1, 4.5, 7, 16]);
const all = Object.values(out).flat().join(' ');
if (/nothing is left|nothing left/.test(all)) fail('with the power 2 and the rabbit c something is always left: ' + all);
return out;
//@
// power -2 on the 2D page: the Mandelbrot shape loses everything at step 1, the Julia shape does not
S.n = -2; go(); await sleep(200);
const out = {};
out['m 2D'] = await window.__say({ kind: 'm', space: 2 }, [0, 0.5, 1, 1.5, 2, 16]);
out['both 2D'] = await window.__say({ kind: 'both', space: 2 }, [0.5, 1, 1.5, 16]);
out['j 2D'] = await window.__say({ kind: 'j', space: 2 }, [1, 16]);
if (!out['m 2D'][2].startsWith('1: After 1 step nothing is left to see')) fail('2D, power -2, step 1: ' + out['m 2D'][2]);
if (!out['m 2D'][3].includes('nothing left to take it')) fail('2D, power -2, between 1 and 2: ' + out['m 2D'][3]);
if (!out['both 2D'][1].includes('Left: nothing is left to see') || !out['both 2D'][1].includes('Right: what is left')) fail('2D both, power -2: ' + out['both 2D'][1]);
return out;
//@ sleep=0.2 shot=out/r26/join/NAME-2d-power-2-j-16.png clip=.bench-main
//@
// the same in 3D, for the opening approach and four others
const out = {};
for (const id of ['mercator', 'fold', 'lathe', 'alongonce', 'pulledplane']) {
  await approach(id);
  out[id + ' m 3D'] = await window.__say({ kind: 'm', space: 3 }, [0, 0.5, 1, 1.5, 16]);
  out[id + ' both 3D'] = await window.__say({ kind: 'both', space: 3 }, [1, 3]);
  out[id + ' j 3D'] = await window.__say({ kind: 'j', space: 3 }, [1, 3]);
  if (!out[id + ' m 3D'][2].startsWith('1: After 1 step nothing is left to see')) fail(id + ', 3D, power -2, step 1: ' + out[id + ' m 3D'][2]);
  if (!out[id + ' both 3D'][0].includes('Left: nothing is left to see')) fail(id + ', 3D both: ' + out[id + ' both 3D'][0]);
  if (/nothing/.test(out[id + ' j 3D'].join(' '))) fail(id + ': nothing is claimed about a 3D Julia shape: ' + out[id + ' j 3D']);
}
await approach('mercator');
L.shape.set({ kind: 'm', space: 3, pos: 1 });
return out;
//@ sleep=0.4 shot=out/r26/join/NAME-3d-power-2-m-01.png clip=.bench-main
//@
// back to the power 2. A c far outside the big circle: the Julia shape loses everything at once, the Mandelbrot shape does not
S.n = 2; go(); await sleep(200);
const out = {};
out['both 2D, c = 7'] = await window.__say({ kind: 'both', space: 2, c: [7, 0, 0] }, [1, 2, 16]);
out['j 2D, c = 7'] = await window.__say({ kind: 'j', space: 2 }, [0.5, 1, 1.5]);
out['j 3D, c = 7'] = await window.__say({ kind: 'j', space: 3 }, [1]);
if (!out['both 2D, c = 7'][1].includes('Right: nothing is left to see') || !out['both 2D, c = 7'][1].includes('Left: what is left for every c')) fail('both, c = 7: ' + out['both 2D, c = 7'][1]);
// zoomed in on an empty corner: nothing may be claimed
L.shape.set({ kind: 'm', space: 2, pos: 8, c: [-0.1226, 0.7449, 0] });
const st = $('stage'), r = st.getBoundingClientRect();
for (let i = 0; i < 5; i++) st.dispatchEvent(new WheelEvent('wheel', { deltaY: -400, bubbles: true, cancelable: true, clientX: r.left + 80, clientY: r.top + 80 }));
await sleep(400);
out['zoomed in on an empty corner'] = L.shape.state().sentence;
if (/nothing/.test(out['zoomed in on an empty corner'])) fail('a zoomed picture must not say that nothing is left');
$('learnShapeViewReset').click(); await sleep(200);
// the words the round forbids, in everything this part puts on the page
const text = [...document.querySelectorAll('#learnPanel, #learnShapeBar, #learnShapeNote, #learnHint')].map(e => e.innerText).join(' ') + ' ' + Object.values(out).flat().join(' ');
const banned = ['iterate', 'iteration', 'escape', 'bailout', 'radius of escape', 'preimage', 'level set', 'orbit count', 'potential', 'membership', 'sample', 'voxel', 'shader', 'mesh', 'render'];
out.forbiddenWordsFound = banned.filter(w => new RegExp('\\b' + w, 'i').test(text));
if (out.forbiddenWordsFound.length) fail('forbidden words: ' + out.forbiddenWordsFound);
return out;

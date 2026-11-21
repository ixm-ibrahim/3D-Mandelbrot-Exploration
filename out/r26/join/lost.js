// The browser takes the 3D picture's graphics away and gives them back (asked for through WEBGL_lose_context):
// while they are gone the stage shows the module's sentence; when they are back the picture must stand there again
// without anybody touching the page. Then: the 'still' fineness comes back after a dear, zoomed-in picture.
//@
const s = await shapeOn({ kind: 'j', space: 3, pos: 4, c: [-1, 0, 0] });
await sleep(400);
const gl = document.querySelector('canvas.learn-shape-gl');
window.__gl = gl; window.__ext = gl.getContext('webgl2').getExtension('WEBGL_lose_context');
window.__cover = () => {
  if (gl.hidden) return -1;
  const t = document.createElement('canvas'); t.width = 160; t.height = Math.round(160 * gl.height / gl.width);
  const g = t.getContext('2d'); g.drawImage(gl, 0, 0, t.width, t.height);
  const d = g.getImageData(0, 0, t.width, t.height).data, bg = [d[0], d[1], d[2]];
  let n = 0; for (let i = 0; i < d.length; i += 4) if (Math.abs(d[i] - bg[0]) + Math.abs(d[i + 1] - bg[1]) + Math.abs(d[i + 2] - bg[2]) > 12) n++;
  return +(100 * n / (t.width * t.height)).toFixed(1);
};
const before = window.__cover();
if (!(before > 2)) fail('there should be a picture to begin with: ' + before);
window.__ext.loseContext();
await sleep(400);
const noteEl = $('learnShapeNote');
window.__during = { noteShown: !noteEl.hidden, note: noteEl.textContent, canvasHidden: gl.hidden, hintHidden: $('learnHint').hidden };
if (!window.__during.noteShown || !gl.hidden) fail('while the graphics are gone the sentence should stand in the picture\'s place: ' + JSON.stringify(window.__during));
return { coveredBefore: before + ' %', whileGone: window.__during };
//@ shot=out/r26/join/NAME-1-gone.png clip=#stage
//@
// (a later task than the one that lost it: this Chrome gives a context back only then)
window.__ext.restoreContext();
await sleep(700);
const noteEl = $('learnShapeNote'), gl = window.__gl, cover = window.__cover();
if (!noteEl.hidden || gl.hidden || !(cover > 2)) fail('the picture should be back by itself: note shown ' + !noteEl.hidden + ', canvas hidden ' + gl.hidden + ', covered ' + cover);
const s = L.shape.state();
return { back: true, coveredAfter: cover + ' %', note: s.note, threeOk: s.threeOk, asked: s.three && s.three.quality };
//@ sleep=0.3 shot=out/r26/join/NAME-2-back.png clip=#stage
//@
// 'still' after a dear picture: zoom far into a deep step of the dearest approach, rest, zoom out, rest twice
await approach('pillow');
L.shape.set({ kind: 'j', c: [-1, 0, 0], pos: 12 });
await sleep(500);
const buf = () => window.__gl.width + 'x' + window.__gl.height, st = $('stage'), r = st.getBoundingClientRect(), seen = [];
seen.push(['at zoom 1', buf()]);
for (let i = 0; i < 14; i++) { st.dispatchEvent(new WheelEvent('wheel', { bubbles: true, cancelable: true, deltaY: -100, clientX: r.left + 430, clientY: r.top + 255 })); await frame(); }
for (let i = 0; i < 4; i++) { await sleep(450); L.shape.set({ pos: 12 + (i % 2) * 0.001 }); await sleep(450); seen.push(['zoomed in, rest ' + (i + 1), buf(), r1(L.shape.state().three.ms) + ' ms']); }
$('learnShapeViewReset').click();
for (let i = 0; i < 5; i++) { await sleep(450); L.shape.set({ pos: 12 + (i % 2) * 0.001 }); await sleep(450); seen.push(['zoom 1 again, rest ' + (i + 1), buf(), r1(L.shape.state().three.ms) + ' ms']); }
await approach('mercator');
return seen;

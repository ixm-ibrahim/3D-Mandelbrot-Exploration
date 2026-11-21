// The 3D picture inside the page, by hand: turning, zooming (wheel, pinch, keys), 'move' while something moves
// and 'still' when it rests, the slider, Reset view. What the module really drew is read from its own canvas
// (the buffer it fitted) as well as from what the page says it asked for.
//@
const s = await shapeOn({ kind: 'm', space: 3, pos: 3 });
if (!s.threeOk || s.note) fail('3D should draw: ' + s.note);
const gl = document.querySelector('canvas.learn-shape-gl'), cv = $('learnShapeCanvas'), st = $('stage');
window.__buf = () => gl.width + 'x' + gl.height;
window.__box = () => { const r = gl.getBoundingClientRect(), q = cv.getBoundingClientRect(), t = st.getBoundingClientRect(); return { gl: [r.left - t.left, r.top - t.top, r.width, r.height].map(Math.round), over: [q.left - t.left, q.top - t.top, q.width, q.height].map(Math.round), stage: [Math.round(t.width), Math.round(t.height)] }; };
await sleep(400);
return { state: brief(L.shape.state()), buffer: window.__buf(), boxes: window.__box(), glHidden: gl.hidden, zOrder: [...st.children].map(e => e.tagName + (e.id ? '#' + e.id : '') + (e.className ? '.' + String(e.className).split(' ').join('.') : '') + (e.hidden ? ' (hidden)' : '')) };
//@
// turn by dragging: 12 moves, a frame apart
const cv = $('learnShapeCanvas'), before = L.shape.state().view3, seen = [];
ptr(cv, 'pointerdown', 300, 200);
for (let i = 1; i <= 12; i++) { ptr(cv, 'pointermove', 300 + 15 * i, 200 + 5 * i); await frame(); await frame(); seen.push(window.__buf()); }
window.__held = { buffers: [...new Set(seen)], before };
return window.__held;
//@ sleep=0.05 shot=out/r26/join/NAME-1-turn-held.png clip=#stage
//@
const cv = $('learnShapeCanvas');
// what the page asked for while the pointer is still down (state() would draw the fine picture, so read the raw note)
const heldAsk = L.shape.state().three;
ptr(cv, 'pointerup', 480, 260);
await sleep(400);
const s = L.shape.state();
if (Math.abs(s.view3.yaw - window.__held.before.yaw) < 0.5) fail('dragging should turn the picture');
if (s.quality !== 'still' || s.three.quality !== 'still') fail('at rest the picture should be the fine one: ' + s.quality + ' / ' + s.three.quality);
if (heldAsk.quality !== 'move') fail('while the picture is held it should be asked for as move: ' + heldAsk.quality);
return { yawBefore: window.__held.before.yaw, yawAfter: r1(s.view3.yaw), pitchAfter: r1(s.view3.pitch), askedWhileHeld: heldAsk.quality, buffersWhileHeld: window.__held.buffers, bufferAtRest: window.__buf(), atRest: s.three, resetShown: shown('learnShapeViewReset') };
//@ sleep=0.3 shot=out/r26/join/NAME-2-turn-rest.png clip=#stage
//@
// the wheel over the stage: zoom in, 8 notches
const st = $('stage'), r = st.getBoundingClientRect(), z0 = L.shape.state().view3.zoom, bufs = [];
for (let i = 0; i < 8; i++) { st.dispatchEvent(new WheelEvent('wheel', { bubbles: true, cancelable: true, deltaY: -100, clientX: r.left + 430, clientY: r.top + 250 })); await frame(); bufs.push(window.__buf()); }
const mid = { buffers: [...new Set(bufs)] };
await sleep(450);
const s = L.shape.state();
if (!(s.view3.zoom > z0 * 1.5)) fail('the wheel should zoom in: ' + z0 + ' -> ' + s.view3.zoom);
if (s.three.quality !== 'still') fail('still expected at rest after the wheel');
return { zoomBefore: z0, zoomAfter: +s.view3.zoom.toFixed(3), buffersWhileWheeling: mid.buffers, bufferAtRest: window.__buf(), solidCameraUntouched: JSON.stringify(LAB.cam).length > 0 };
//@ sleep=0.3 shot=out/r26/join/NAME-3-zoomed.png clip=#stage
//@
// pinch with two scripted touch pointers: fingers 100 px apart moving to 200 px apart
$('learnShapeViewReset').click(); await sleep(300);
const cv = $('learnShapeCanvas'), z0 = L.shape.state().view3.zoom, bufs = [];
const t = (type, id, x, y) => ptr(cv, type, x, y, { pointerId: id, pointerType: 'touch' });
t('pointerdown', 11, 380, 250); t('pointerdown', 12, 480, 250);
for (let i = 1; i <= 10; i++) { t('pointermove', 11, 380 - 5 * i, 250); t('pointermove', 12, 480 + 5 * i, 250); await frame(); await frame(); bufs.push(window.__buf()); }
t('pointerup', 11, 330, 250); t('pointerup', 12, 530, 250);
await sleep(450);
const s = L.shape.state();
if (!(Math.abs(s.view3.zoom / z0 - 2) < 0.1)) fail('pinching to twice the spread should double the zoom: ' + z0 + ' -> ' + s.view3.zoom);
return { zoomBefore: +z0.toFixed(3), zoomAfter: +s.view3.zoom.toFixed(3), buffersWhilePinching: [...new Set(bufs)], bufferAtRest: window.__buf(), quality: s.three.quality };
//@
// one finger after a pinch must turn, not jump
const cv = $('learnShapeCanvas'), a0 = L.shape.state().view3;
const t = (type, id, x, y) => ptr(cv, type, x, y, { pointerId: id, pointerType: 'touch' });
t('pointerdown', 13, 400, 250); t('pointermove', 13, 410, 250); await frame(); await frame(); t('pointermove', 13, 430, 250); await frame(); await frame(); t('pointerup', 13, 430, 250);
await sleep(350);
const a = L.shape.state().view3;
if (Math.abs(a.zoom - a0.zoom) > 1e-9 || Math.abs((a.yaw - a0.yaw) + 0.3) > 0.02) fail('one finger should turn by 0.3 and leave the zoom: ' + JSON.stringify([a0, a]));
// then the keys; then Reset view
cv.focus();
for (const k of ['ArrowLeft', 'ArrowLeft', 'ArrowUp', '-']) cv.dispatchEvent(new KeyboardEvent('keydown', { key: k, bubbles: true, cancelable: true }));
await sleep(350);
const b = L.shape.state().view3;
if (Math.abs(b.yaw - a.yaw) < 0.15 || Math.abs(b.pitch - a.pitch) < 0.05 || !(b.zoom < a.zoom)) fail('the keys should turn and zoom: ' + JSON.stringify([a, b]));
$('learnShapeViewReset').click(); await sleep(350);
const s = L.shape.state();
if (Math.abs(s.view3.yaw + 0.62) > 1e-9 || Math.abs(s.view3.zoom - 1) > 1e-9 || shown('learnShapeViewReset')) fail('Reset view should put the view back and go away: ' + JSON.stringify(s.view3));
return { afterKeys: b, afterReset: s.view3, quality: s.three.quality, buffer: window.__buf() };
//@
// the slider by hand: input events as a hand would send them, a frame apart
const pos = $('learnShapePos'), bufs = [], qs = [];
for (let v = 3; v <= 6.001; v += 0.05) { pos.value = v.toFixed(2); pos.dispatchEvent(new Event('input', { bubbles: true })); await frame(); bufs.push(window.__buf()); }
const during = [...new Set(bufs)];
await sleep(450);
const s = L.shape.state();
if (s.pos !== 6) fail('the slider should stand on 6: ' + s.pos);
if (s.three.quality !== 'still') fail('still expected once the slider rests');
return { buffersWhileSliding: during, bufferAtRest: window.__buf(), asked: s.three };
//@ sleep=0.3 shot=out/r26/join/NAME-4-slider-06.png clip=#stage
//@
// Both: one drag turns both pictures; the diamond stands in both
const s0 = L.shape.set({ kind: 'both', c: [-0.1226, 0.7449, 0.5], pos: 4 });
const cv = $('learnShapeCanvas');
ptr(cv, 'pointerdown', 650, 250);
for (let i = 1; i <= 8; i++) { ptr(cv, 'pointermove', 650 - 12 * i, 250 - 6 * i); await frame(); await frame(); }
ptr(cv, 'pointerup', 554, 202);
await sleep(400);
const s = L.shape.state();
return { panes: s.panes, diamonds: s.diamonds.map(d => d && d.map(Math.round)), view3: s.view3, asked: s.three, buffer: window.__buf() };
//@ sleep=0.3 shot=out/r26/join/NAME-5-both-turned.png clip=#stage
//@
// Play from 4: a picture taken while it plays (the 'move' picture), and what was asked
L.shape.set({ kind: 'j', c: [-0.1226, 0.7449, 0], pos: 4 });
$('learnShapeViewReset').click(); await sleep(300);
$('learnShapePlay').click();
await sleep(700);
window.__mid = { buffer: window.__buf(), playing: $('learnShapePlay').textContent === 'Pause', pos: +$('learnShapePos').value };
return window.__mid;
//@ shot=out/r26/join/NAME-6-playing.png clip=#stage
//@
$('learnShapePlay').click(); await sleep(450);
const s = L.shape.state();
return { paused: !s.playing, pos: +s.pos.toFixed(2), bufferAtRest: window.__buf(), asked: s.three, sentence: s.sentence };
//@ sleep=0.3 shot=out/r26/join/NAME-7-paused.png clip=#stage
//@
// back to 2D and to 3D again: the 3D canvas goes and comes back; One point and back
L.shape.set({ space: 2 }); await sleep(300);
const gl = document.querySelector('canvas.learn-shape-gl'), hid2 = gl.hidden;
L.shape.set({ space: 3 }); await sleep(300);
const hid3 = gl.hidden;
$('learnFollowPoint').click(); await sleep(300);
const hidP = gl.hidden, pointCanvasShown = shown('learnCanvas');
$('learnFollowShape').click(); await sleep(400);
const s = L.shape.state();
if (!hid2 || hid3 || !hidP || gl.hidden) fail('the 3D canvas should be hidden in 2D and with One point: ' + [hid2, hid3, hidP, gl.hidden]);
return { hiddenIn2D: hid2, hiddenIn3D: hid3, hiddenWithOnePoint: hidP, backAgain: brief(s) };

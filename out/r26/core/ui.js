// The controls of "A whole shape", used the way a reader uses them: the choice Follow (and the picture playing by
// itself the first time), the transport, the two small choices, the panel, the wheel, the keys, and the two resets.
//@
// 1. Follow: the first switch plays by itself from step 0; the 1D line goes away
$('mode-l').click(); await sleep(400);
$('learnSpace1').click(); await sleep(300);
if (L.space !== 1) fail('the 1D line should be on before the switch');
if (!shown('learnFollow') || !$('learnFollowPoint').checked) fail('the choice Follow should stand at the top of the panel, on One point');
const first = document.querySelector('#learnPanel .sec-body').firstElementChild.id;
$('learnFollowShape').click(); await sleep(350);
const a = L.shape.state();
if (!a.on || a.space !== 2) fail('A whole shape should come on, in 2D: ' + JSON.stringify([a.on, a.space]));
if (!a.playing) fail('the first switch should play by itself');
if (shown(document.querySelector('.learn-space-1'))) fail('the 1D choice should be put away');
for (const id of ['learnBar', 'learnCanvas', 'learnDials', 'learnChecks', 'learnMoves', 'learnZero', 'learnNotice']) if (shown(id)) fail('#' + id + ' belongs to One point and should be put away');
for (const id of ['learnShapeBar', 'learnShapeCanvas', 'learnShapeIntro', 'learnShapeKind', 'learnShapeNotice', 'learnSpace', 'learnReset']) if (!shown(id)) fail('#' + id + ' should be on show');
if (shown('learnShapeC')) fail('the c dials mean nothing for the Mandelbrot shape alone');
await sleep(2600);
const b = L.shape.state();
if (!(b.pos > 1.2) || !b.playing) fail('it should be playing on: ' + b.pos);
return { firstInPanel: first, playingAt: [+a.pos.toFixed(2), +b.pos.toFixed(2)], sentence: b.sentence, summary: document.querySelector('#learnPanel summary').textContent, where: $('learnShapeWhere').textContent };
//@ shot=out/r26/core/ui-1-playing.png
//@
// 2. Pause, Play, the Speed, the end of the steps
$('learnShapePlay').click(); await sleep(150);
const a = L.shape.state();
if (a.playing || $('learnShapePlay').textContent !== 'Play') fail('Pause should stop it');
const sp = $('learnShapeSpeed'); sp.value = 'fast'; sp.dispatchEvent(new Event('change', { bubbles: true }));
if (L.speed !== 'fast' || $('learnSpeed').value !== 'fast') fail('the Speed is one setting for both parts');
L.shape.goto(13);
$('learnShapePlay').click(); await sleep(200);
if ($('learnShapePlay').textContent !== 'Pause' || $('learnShapePlay').getAttribute('aria-pressed') !== 'true') fail('Play should show Pause while it plays');
for (let i = 0; i < 100 && L.shape.state().playing; i++) await sleep(100);
const e = L.shape.state();
if (e.pos !== 16 || e.playing) fail('it should stop at step 16: ' + e.pos);
if (!$('learnShapeFwd').disabled || $('learnShapeBack').disabled) fail('at the end only Back is open');
// Play at the end starts again from 0
$('learnShapePlay').click(); await sleep(300);
const r = L.shape.state();
if (!(r.pos < 1) || !r.playing) fail('Play at the end should start again from the start: ' + r.pos);
L.shape.pause();
sp.value = 'normal'; sp.dispatchEvent(new Event('change', { bubbles: true }));
return { end: e.sentence, tickOn: [...$('learnShapeTicks').children].filter(b => b.classList.contains('is-on')).map(b => b.textContent), restartedAt: +r.pos.toFixed(2) };
//@
// 3. Start again, one step forward (plays to the next whole step), one step back, the ticks, the slider, its keys
$('learnShapeAgain').click(); await sleep(100);
if (L.shape.state().pos !== 0 || !$('learnShapeBack').disabled || !$('learnShapeAgain').disabled) fail('Start again should go to step 0');
$('learnShapeFwd').click(); await sleep(250);
const mid = L.shape.state();
if (!mid.playing || !(mid.pos > 0 && mid.pos < 1)) fail('Forward should play the next step: ' + mid.pos);
for (let i = 0; i < 60 && L.shape.state().playing; i++) await sleep(100);
if (L.shape.state().pos !== 1) fail('Forward should stop at the next whole step: ' + L.shape.state().pos);
$('learnShapeFwd').click(); for (let i = 0; i < 60 && (L.shape.state().playing || i < 2); i++) await sleep(100);
if (L.shape.state().pos !== 2) fail('Forward again: ' + L.shape.state().pos);
L.shape.set({ pos: 2.6 });
$('learnShapeBack').click(); if (L.shape.state().pos !== 2) fail('Back from 2.6 should go to 2');
$('learnShapeBack').click(); if (L.shape.state().pos !== 1) fail('Back from 2 should go to 1');
$('learnShapeTicks').children[7].click(); if (L.shape.state().pos !== 7) fail('a tick should go to its step');
const pos = $('learnShapePos'); pos.value = 4.35; pos.dispatchEvent(new Event('input', { bubbles: true }));
const s435 = L.shape.state();
if (Math.abs(s435.pos - 4.35) > 1e-9) fail('the slider should stand between two steps: ' + s435.pos);
pos.value = 5.01; pos.dispatchEvent(new Event('input', { bubbles: true }));
if (L.shape.state().pos !== 5) fail('close to a whole step is the whole step: ' + L.shape.state().pos);
const key = k => pos.dispatchEvent(new KeyboardEvent('keydown', { key: k, bubbles: true, cancelable: true }));
key('ArrowRight'); const k1 = L.shape.state().pos; key('ArrowLeft'); key('ArrowLeft'); const k2 = L.shape.state().pos;
if (k1 !== 6 || k2 !== 4) fail('the arrow keys on the slider go by whole steps: ' + [k1, k2]);
return { between: s435.sentence, where: $('learnShapeWhere').textContent, valuetext: pos.getAttribute('aria-valuetext') };
//@
// 4. the two small choices under the picture, and the same choices in the panel
const pick = (name, value) => { const r = document.querySelector('input[name=' + name + '][value="' + value + '"]'); r.click(); };
pick('learnShapeKindBar', 'j'); await sleep(150);
let s = L.shape.state();
if (s.kind !== 'j' || !document.querySelector('input[name=learnShapeKind][value=j]').checked) fail('Julia under the picture should tick Julia shape in the panel too');
if (!shown('learnShapeC') || !shown('learnShape-cx') || shown('learnShape-cz')) fail('the c dials: x and y on the 2D page');
pick('learnShapeKind', 'both'); await sleep(150);
s = L.shape.state();
if (s.kind !== 'both' || s.panes.length !== 2 || !document.querySelector('input[name=learnShapeKindBar][value=both]').checked) fail('Both in the panel should show two pictures and tick Both under the picture');
pick('learnShapeSpaceBar', '3'); await sleep(200);
s = L.shape.state();
if (s.space !== 3 || !$('learnSpace3').checked || !shown('learnShape-cz') || !shown('learnShapeRule')) fail('3D under the picture: the panel follows, the dial for z and the line about the approach come up');
const rule = $('learnShapeRule').textContent, notice3 = $('learnShapeNotice').textContent, note3 = s.note, sentence3 = s.sentence;
$('learnSpace2').click(); await sleep(200);
s = L.shape.state();
if (s.space !== 2 || !document.querySelector('input[name=learnShapeSpaceBar][value="2"]').checked) fail('2D page in the panel should tick 2D under the picture');
pick('learnShapeKindBar', 'm'); await sleep(100);
return { rule, notice3, note3, sentence3, notice2: $('learnShapeNotice').textContent, threeOk: s.threeOk };
//@
// 5. the c of the Julia shape: the dials, the named values, the c of the Julia tab
L.shape.set({ kind: 'j', pos: 16 });
const names = [...document.querySelectorAll('#learnShapeCs .btn')].map(b => b.innerText.replace(/\s+/g, ' ').trim());
const btn = t => [...document.querySelectorAll('#learnShapeCs .btn')].find(b => b.textContent.includes(t));
btn('c = −1').click(); await sleep(100); const c1 = L.shape.state().c.slice();
btn('0.7449').click(); await sleep(100); const c2 = L.shape.state().c.slice();
btn('c = i').click(); await sleep(100); const c3 = L.shape.state().c.slice();
btn('c = 0').click(); await sleep(100); const c4 = L.shape.state().c.slice();
S.c = [0.28, 0.01, 0]; btn('Julia tab').click(); await sleep(100); const c5 = L.shape.state().c.slice(); S.c = [-1, 0, 0];
const dial = $('learnShape-cxNum'); dial.value = '-0.75'; dial.dispatchEvent(new Event('input', { bubbles: true })); dial.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', bubbles: true })); dial.dispatchEvent(new Event('change', { bubbles: true })); await sleep(100);
const c6 = L.shape.state().c.slice();
if (JSON.stringify([c1, c2, c3, c4, c5]) !== JSON.stringify([[-1, 0, 0], [-0.1226, 0.7449, 0], [0, 1, 0], [0, 0, 0], [0.28, 0.01, 0]])) fail('the buttons for c: ' + JSON.stringify([c1, c2, c3, c4, c5]));
if (c6[0] !== -0.75) fail('the dial should set c: ' + c6);
// at another power the names are not true, so only the values are shown
S.n = 3; go(); await sleep(150);
const namesAt3 = [...document.querySelectorAll('#learnShapeCs .btn')].map(b => b.innerText.replace(/\s+/g, ' ').trim());
const end3 = L.shape.state().sentence;
S.n = 2.5; go(); await sleep(150); const end25 = L.shape.state().sentence;
S.n = 2; go(); await sleep(150);
return { names, namesAt3, c6, endPower3: end3, endPower2_5: end25 };
//@
// 6. the wheel zooms the flat picture about the pointer, "Reset view" comes up, a drag then moves the picture
L.shape.set({ kind: 'm', pos: 8 });
const st = $('stage'), r = st.getBoundingClientRect(), cv = $('learnShapeCanvas');
if (shown('learnShapeViewReset')) fail('no Reset view before anything is zoomed');
for (let i = 0; i < 4; i++) st.dispatchEvent(new WheelEvent('wheel', { deltaY: -300, bubbles: true, cancelable: true, clientX: r.left + 250, clientY: r.top + 250 }));
await sleep(350);
const z = L.shape.state();
if (!(z.view2.m.zoom > 3) || !shown('learnShapeViewReset') || shown('learnViewReset')) fail('the wheel should zoom, and its own Reset view should come up: ' + JSON.stringify(z.view2));
const camBefore = JSON.stringify(LAB.cam);
ptr(cv, 'pointerdown', 400, 250); for (let i = 1; i <= 5; i++) { ptr(cv, 'pointermove', 400 + 12 * i, 250 + 4 * i); await frame(); } ptr(cv, 'pointerup', 460, 270); await sleep(300);
const p = L.shape.state();
if (p.view2.m.x === z.view2.m.x) fail('a drag should move a zoomed picture');
if (JSON.stringify(LAB.cam) !== camBefore) fail('the solid\'s camera must not hear the wheel or the drag');
return { zoomed: z.view2.m, moved: p.view2.m, ms: p.ms };
//@ sleep=0.3 shot=out/r26/core/ui-6-zoomed.png clip=.bench-main
//@
$('learnShapeViewReset').click(); await sleep(200);
const s = L.shape.state();
if (s.view2.m.zoom !== 1 || s.view2.m.x !== 0 || shown('learnShapeViewReset')) fail('Reset view should put the picture back');
// the keys on the picture: space plays and pauses, plus zooms, the arrows move c
const cv = $('learnShapeCanvas'), key = (k, o) => cv.dispatchEvent(new KeyboardEvent('keydown', Object.assign({ key: k, bubbles: true, cancelable: true }, o || {})));
L.shape.set({ kind: 'j', c: [0, 0, 0], pos: 3 });
key(' '); await sleep(150); const playing = L.shape.state().playing; key(' '); await sleep(100); const paused = !L.shape.state().playing;
key('ArrowRight'); key('ArrowUp'); key('ArrowUp', { shiftKey: true });
const c = L.shape.state().c;
key('+'); const zoom = L.shape.state().view2.j.zoom; key('-');
if (!playing || !paused || c[0] !== 0.05 || c[1] !== 0.06 || !(zoom > 1.1)) fail('the keys on the picture: ' + JSON.stringify([playing, paused, c, zoom]));
return { playing, paused, c, zoom };
//@
// 7. leaving Learn and coming back keeps the whole shape; the second switch does not play by itself
L.shape.set({ kind: 'both', pos: 4.5, c: [-1, 0, 0] });
$('mode-j').click(); await sleep(500);
if (document.body.classList.contains('is-learn') || document.body.classList.contains('is-learn-shape') || shown('learnShapeBar') || shown('learnShapeCanvas')) fail('leaving Learn should put the whole shape away');
if (!shown('view')) fail('the solid should be back');
$('mode-l').click(); await sleep(400);
const s = L.shape.state();
if (!s.on || s.kind !== 'both' || s.pos !== 4.5 || s.playing) fail('coming back should find the whole shape as it was left: ' + JSON.stringify(brief(s)));
$('learnFollowPoint').click(); await sleep(200); $('learnFollowShape').click(); await sleep(300);
if (L.shape.state().playing) fail('only the first switch of a visit plays by itself');
return brief(L.shape.state());
//@
// 8. the panel's own reset: Follow = One point; inside it the Mandelbrot shape, 2D, step 0, c as Learn opens
L.shape.set({ kind: 'both', space: 3, pos: 7, c: [0.3, 0.3, 0.3] });
document.querySelector('#learnReset button').click(); await sleep(300);
const a = L.shape.state();
if (L.follow !== 'point' || a.on || !$('learnFollowPoint').checked || !shown('learnBar') || shown('learnShapeBar')) fail('the panel\'s reset should go back to One point');
if (a.kind !== 'm' || a.space !== 2 || a.pos !== 0 || JSON.stringify(a.c) !== '[-0.4,0.3,0]') fail('and put the whole shape back as it opens: ' + JSON.stringify(brief(a)));
if (document.querySelector('#learnPanel summary').textContent !== 'Learn: one step, move by move') fail('the heading of the panel should be the old one again');
// Reset everything, from inside the whole shape
await shapeOn({ kind: 'j', space: 3, pos: 9, c: [1, 1, 1] });
$('resetAll').click(); await sleep(500);
const b = L.shape.state();
if (L.on || L.follow !== 'point' || b.kind !== 'm' || b.space !== 2 || b.pos !== 0 || JSON.stringify(b.c) !== '[-0.4,0.3,0]') fail('Reset everything: ' + JSON.stringify([L.on, L.follow, brief(b)]));
if (document.body.classList.contains('is-learn-shape') || shown('learnShapeBar') || shown('learnShapeCanvas') || shown('learnShapeNote')) fail('Reset everything should leave nothing of the whole shape on show');
$('mode-l').click(); await sleep(400);
const c = L.state();
if (!L.on || L.follow !== 'point' || !shown('learnBar') || !shown('learnCanvas') || shown('learnShapeBar')) fail('Learn should open on One point again');
return { afterPanelReset: brief(a), afterResetAll: brief(b), learnOpensOn: L.follow, sentence: c.sentence };
//@ sleep=0.3 shot=out/r26/core/ui-8-after-resets.png
//@
// 9. a reader who asked for reduced motion: the first switch does not play by itself (a fresh visit is needed for
// "first", so this is asked of the rule itself: the flag is put back and the media query answered by hand)
const mm = window.matchMedia.bind(window);
window.matchMedia = q => (String(q).includes('prefers-reduced-motion') ? { matches: true, media: q, addEventListener() {}, removeEventListener() {} } : mm(q));
$('resetAll').click(); await sleep(400); $('mode-l').click(); await sleep(400);
// (LEARN_SHAPE is not reachable from here; a new page would be: see ui-calm in the notes. Here: forward one step must jump, not play.)
$('learnFollowShape').click(); await sleep(300);
const a = L.shape.state();
$('learnShapeFwd').click(); await sleep(100);
const b = L.shape.state();
window.matchMedia = mm;
if (b.pos !== 1 || b.playing) fail('with reduced motion Forward should jump to the next step: ' + JSON.stringify([b.pos, b.playing]));
return { playingAfterSwitch: a.playing, forwardJumpedTo: b.pos };

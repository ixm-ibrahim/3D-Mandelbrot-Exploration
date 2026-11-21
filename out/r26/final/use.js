// The final look: using the page the way a reader would, things nobody's list of defects names.
//@
// (1) The first switch to "A whole shape" plays by itself; the second one in the same visit does not.
await openLearn(); $('learnFollowShape').click(); await sleep(400);
const first = { playing: L.shape.state().playing, play: page().play };
$('learnShapePlay').click(); await sleep(100);     // Pause
$('learnFollowPoint').click(); await sleep(250); $('learnFollowShape').click(); await sleep(400);
const second = { playing: L.shape.state().playing, play: page().play, pos: L.shape.state().pos };
return { first, second };
//@ sleep=0.3 shot=out/r26/final/NAME-1-space-bar-paused.png clip=#stage
// (2) Keys with the picture in focus: the space bar plays and pauses; plus zooms; arrows move c on the 2D page
const cv = $('learnShapeCanvas'); cv.focus();
const key = (k, o) => cv.dispatchEvent(new KeyboardEvent('keydown', Object.assign({ key: k, bubbles: true, cancelable: true }, o || {})));
$('learnShapeAgain').click(); await sleep(150);
key(' '); await sleep(2300); const a = L.shape.state(); key(' '); await sleep(150); const b = L.shape.state();
kindBar('j'); await sleep(200); const c0 = L.shape.state().c; key('ArrowRight'); key('ArrowUp'); await sleep(150); const c1 = L.shape.state().c;
key('+'); key('+'); await sleep(200); const z = L.shape.state().view2.j.zoom; $('learnShapeViewReset').click(); await sleep(150);
return { afterSpace: { playing: a.playing, pos: r2(a.pos) }, afterSecondSpace: { playing: b.playing, pos: r2(b.pos) }, cBefore: c0, cAfterRightAndUp: c1, zoomAfterTwoPlus: r2(z) };
//@ sleep=0.4 shot=out/r26/final/NAME-2-diamond-dragged-2d-both.png clip=#stage
// (3) Both in 2D at step 6: the diamond dragged by a scripted mouse from where it stands to the point (0.3, 0.5):
// does c follow, and does the right picture change while the button is still down?
kindBar('both'); await sleep(200); tick(6); await sleep(300);
const cv = $('learnShapeCanvas'), b = cv.getBoundingClientRect(), s0 = L.shape.state(), d = s0.diamonds[0], P = s0.panes[0];
const ev = (type, x, y) => cv.dispatchEvent(new PointerEvent(type, { bubbles: true, cancelable: true, pointerId: 5, pointerType: 'mouse', isPrimary: true, button: 0, buttons: type === 'pointerup' ? 0 : 1, clientX: b.left + x, clientY: b.top + y }));
const sc = 0.21 * Math.min(P.w, P.h), tx = P.x + P.w / 2 + 0.3 * sc, ty = P.y + P.h / 2 - 0.5 * sc;
const sum = () => { const m = L.shape.mask2('j', 65, 2, 6); let n = 0; for (const v of m) if (v > 6) n++; return n; };
const before = sum();
ev('pointerdown', d[0], d[1]);
for (let i = 1; i <= 10; i++) { ev('pointermove', d[0] + (tx - d[0]) * i / 10, d[1] + (ty - d[1]) * i / 10); await frame(); }
const mid = { c: L.shape.state().c, julia6: sum(), quality: L.shape.state().quality };
ev('pointerup', tx, ty); await sleep(400);
const s1 = L.shape.state();
return { cBefore: s0.c, cWhileHeld: mid.c, cAfter: s1.c, pointsOfJuliaShape6: { before, whileHeld: mid.julia6 }, qualityWhileHeld: mid.quality, qualityAfter: s1.quality, ...page() };
//@ sleep=0.6 shot=out/r26/final/NAME-3-3d-turned.png clip=#stage
// (4) 3D: a drag turns both pictures; the wheel zooms; Reset view puts it back
spaceBar(3); await sleep(1200); await rest(300);
const cv = $('learnShapeCanvas'), b = cv.getBoundingClientRect(), v0 = L.shape.state().view3;
const ev = (type, x, y) => cv.dispatchEvent(new PointerEvent(type, { bubbles: true, cancelable: true, pointerId: 6, pointerType: 'mouse', isPrimary: true, button: 0, buttons: type === 'pointerup' ? 0 : 1, clientX: b.left + x, clientY: b.top + y }));
ev('pointerdown', 200, 250); let moving = null;
for (let i = 1; i <= 12; i++) { ev('pointermove', 200 + i * 10, 250 - i * 4); await frame(); if (i === 8) moving = L.shape.state().quality; }
ev('pointerup', 320, 202); const s1 = await rest(500);
return { viewBefore: v0, viewAfter: { yaw: r3(s1.view3.yaw), pitch: r3(s1.view3.pitch), zoom: s1.view3.zoom }, qualityWhileDragging: moving, qualityAtRest: s1.quality, resetShown: !$('learnShapeViewReset').hidden };
//@ sleep=0.5 shot=out/r26/final/NAME-4-other-tab-and-back.png
// (5) Play in 3D, leave for the Julia tab while it plays, come back to Learn: nothing breaks, the play has stopped
$('learnShapeViewReset').click(); await sleep(200); $('learnShapeAgain').click(); await sleep(200); $('learnShapePlay').click(); await sleep(3200);
const during = L.shape.state();
$('mode-j').click(); await sleep(1500);
const away = { learnOn: L.on, shapeOn: L.shape.state().on, barHidden: $('learnShapeBar').hidden, glHidden: (document.querySelector('canvas.learn-shape-gl') || {}).hidden, bodyClass: document.body.className };
$('mode-l').click(); await sleep(900); const back = await rest(300);
return { during: { playing: during.playing, pos: r2(during.pos) }, away, back: { on: back.on, follow: back.follow, playing: back.playing, pos: r2(back.pos), kind: back.kind, space: back.space, note: back.note }, ...page() };
//@ sleep=0.5 shot=out/r26/final/NAME-5-theme-switched.png
// (6) the theme switched by hand (data-theme on <html>) while a 3D picture is on show: both canvases follow
const html = document.documentElement, was = html.getAttribute('data-theme'), want = '__THEME__' === 'dark' ? 'light' : 'dark';
tick(4); await rest(300);
html.setAttribute('data-theme', want); const s = await rest(700);
const bg = getComputedStyle($('stage')).backgroundColor;
window.__themeWas = was;
return { themeNow: want, stageBackground: bg, coloursOk: s.three && s.three.ok };
//@
const html = document.documentElement; if (window.__themeWas === null) html.removeAttribute('data-theme'); else html.setAttribute('data-theme', window.__themeWas); await rest(500);
return { themeBack: html.getAttribute('data-theme') };
//@ sleep=0.4 shot=out/r26/final/NAME-6-after-reset-everything.png
// (7) "Reset everything": Follow = One point; and inside the whole shape: Mandelbrot shape, 2D, step 0, c as Learn opens
L.shape.set({ kind: 'j', space: 3, c: [0.3, -0.6, 0.4], pos: 7 }); await rest(300);
const btn = [...document.querySelectorAll('button')].find(b => b.textContent.trim().toLowerCase() === 'reset everything');
if (!btn) fail('no Reset everything button');
btn.click(); await sleep(900);
const a = { learnOn: L.on, follow: L.follow, bodyShape: document.body.classList.contains('is-learn-shape') };
await openLearn(); await sleep(300);
const b = { follow: L.follow, pointChecked: $('learnFollowPoint').checked, space: L.state().space, where: $('learnWhere').textContent };
$('learnFollowShape').click(); await sleep(300); L.shape.pause();
const s = L.shape.state();
return { rightAfter: a, learnAgain: b, wholeShape: { kind: s.kind, space: s.space, pos: s.pos, c: s.c, view2: s.view2, view3: s.view3, playsByItselfAgain: s.playing } };
//@ sleep=0.4 shot=out/r26/final/NAME-7-after-learn-reset.png
// (8) the Learn panel's own reset, from inside the whole shape
L.shape.set({ kind: 'both', space: 3, c: [0.3, -0.6, 0.4], pos: 7 }); await rest(300);
$('learnReset').click(); await sleep(600);
const s = L.shape.state();
return { learnOn: L.on, follow: L.follow, pointChecked: $('learnFollowPoint').checked, wholeShapeInside: { kind: s.kind, space: s.space, pos: s.pos, c: s.c } };
//@ sleep=0.4 shot=out/r26/final/NAME-8-from-1d.png
// (9) from the 1D line into the whole shape: the space becomes 2D and the 1D choice is put away
$('learnSpace1').click(); await sleep(300); const before = L.state().space;
$('learnFollowShape').click(); await sleep(300); L.shape.pause();
const one = $('learnSpace1').closest('.seg');
return { spaceBefore: before, spaceInShape: L.shape.state().space, oneDChoiceShown: one.offsetParent !== null, panelSpaceChoices: [...document.querySelectorAll('#learnSpace .seg')].filter(n => n.offsetParent !== null).map(n => n.textContent.trim()) };
//@ sleep=0.6 shot=out/r26/final/NAME-9-resized-3d.png
// (10) the window made narrower and wider again with a 3D picture on show (the stage's box changes): the picture
// follows and stays sharp (its buffer is fitted to the box)
spaceBar(3); await sleep(1200); kindBar('both'); tick(4); await rest(400);
const gl = document.querySelector('canvas.learn-shape-gl'), box0 = [gl.clientWidth, gl.clientHeight, gl.width, gl.height];
$('stage').style.width = '520px'; await sleep(500); const s1 = await rest(400); const box1 = [gl.clientWidth, gl.clientHeight, gl.width, gl.height, s1.side];
$('stage').style.width = ''; await sleep(500); const s2 = await rest(400); const box2 = [gl.clientWidth, gl.clientHeight, gl.width, gl.height, s2.side];
return { boxAndBuffer: box0, narrow: box1, wideAgain: box2 };
//@
// (11) "Use the c of the Julia tab": the Julia shape takes the lab's c
kindBar('j'); spaceBar(2); await sleep(300);
const labC = S.c.slice(); $('learnShapeJuliaC').click(); await sleep(300);
return { labC, shapeC: L.shape.state().c };
//@
// (12) the dials of the lab change the picture: Power to 3 (2D, Mandelbrot shape, step 6): the note says so, the
// names of the named values go, and the closing sentence stays true
kindBar('m'); tick(6); await sleep(200);
const count = () => { const m = L.shape.mask2('m', 129, 2, 6); let n = 0; for (const v of m) if (v > 6) n++; return n; };
const n2 = count(), pw = $('pow'); pw.value = 3; pw.dispatchEvent(new Event('input', { bubbles: true })); pw.dispatchEvent(new Event('change', { bubbles: true })); await sleep(400);
const out = { power: S.n, pointsInShape6: { power2: n2, power3: count() }, note: $('learnShapeIntro').textContent.slice(-120) };
kindBar('j'); await sleep(200); out.named = [...document.querySelectorAll('#learnShapeCs button')].map(b => b.innerText.trim()); tick(16); await sleep(200); out.end = page().say;
pw.value = 2; pw.dispatchEvent(new Event('input', { bubbles: true })); pw.dispatchEvent(new Event('change', { bubbles: true })); await sleep(300); kindBar('m'); tick(0);
return out;

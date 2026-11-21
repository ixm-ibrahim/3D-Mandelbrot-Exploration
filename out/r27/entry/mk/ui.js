// Steps 3 and 4: the state, the choice, the dials, the note, framing, the row in the Approach list, resets, and every
// thing that works in the Kleinian view, tried with Balls on balls. Each line of the result is one thing that was checked.
const out = [], ok = t => out.push(t);
const shown = id => { const e = $(id); return !!e && e.getBoundingClientRect().width > 0; };
const sig = () => { const w = $('stage').clientWidth, h = $('stage').clientHeight; let s = '', sum = 0; for (let i = 0; i < 15; i++) for (let j = 0; j < 11; j++) { const p = L.pick(w * (i + 0.5) / 15, h * (j + 0.5) / 11); s += p ? '1' : '0'; if (p) sum += p[0] + 2 * p[1] + 3 * p[2]; } return s + ' ' + sum.toFixed(3); };
const hits = s => (s.split(' ')[0].match(/1/g) || []).length;
const type = (id, v) => { const e = $(id); if (!e) fail('no control ' + id); e.value = String(v); e.dispatchEvent(new Event('input', { bubbles: true })); e.dispatchEvent(new Event('change', { bubbles: true })); };

// 1. the list
if (L.APPROACHES.length !== 21) fail('APPROACHES should still have 21 entries: ' + L.APPROACHES.length);
if (L.APPROACHES.some(a => /ball/i.test(a.id))) fail('Balls on balls must not be an element of APPROACHES');
if (document.querySelectorAll('#rules .rule').length !== 21 || document.querySelectorAll('#rules input[type=radio]').length !== 21) fail('the list should still hold 21 approach rows');
$('apMenuBtn').click(); await sleep(150);
const row = $('apBallsRow'), head = $('apgh-cousin');
if (!row || !shown('ap-balls')) fail('the row is not on show in the open list');
if (head.textContent !== 'A cousin, not a rule') fail('heading: ' + head.textContent);
if (!/Balls on balls/.test(row.textContent) || !row.textContent.includes('a cousin of the flat picture: no c, no power')) fail('row text: ' + row.textContent);
if (row.querySelector('.cousin-tag').getBoundingClientRect().height < 8) fail('the label of the row is not visible');
if (row.compareDocumentPosition(document.querySelectorAll('#rules .rule')[20]) & Node.DOCUMENT_POSITION_FOLLOWING) fail('the row should stand after the last approach');
if ($('rules').contains(row) || !$('apPop').contains(row)) fail('the row should stand in the open menu, under the list');
{ const pop = $('apPop').getBoundingClientRect(), rr = row.getBoundingClientRect(); if (pop.bottom > innerHeight + 0.5 || rr.bottom > pop.bottom + 0.5 || rr.top < pop.top) fail('the open menu or the row does not fit the window'); }
ok('list: 21 approaches as before; the row "' + row.textContent.trim() + '" stands last, under "' + head.textContent + '"');

// 2. one click
const before = { approach: S.approach, mode: S.mode };
$('ap-balls').click(); await sleep(100);
if (S.mode !== 'k' || S.k.group !== 1) fail('the row did not choose Balls on balls');
if (!$('apPop').hidden) fail('the list stayed open');
if (S.approach !== before.approach) fail('the approach changed');
await settle();
if ($('apMenuName').textContent !== 'Balls on balls') fail('menu name: ' + $('apMenuName').textContent);
if (!shown('ballsNote') || shown('kleinNote') || shown('kleinPreset') || shown('kleinFrame')) fail('the panel does not show the right part');
if (!$('kleinGroup1').checked || $('kleinGroup0').checked) fail('the choice at the top of the panel is not on Balls on balls');
if (!shown('secApproach') || shown('secEq') || shown('secMod') || shown('apPanels') || shown('apAboutBtn')) fail('Approach section: menu should stay, equation and dials go');
if ($('ballsNote').textContent !== L.BALLS.note) fail('note text');
const sentences = L.BALLS.note.split(/(?<=[.])\s+/).length;
if (sentences > 3) fail('the note has ' + sentences + ' sentences');
for (const w of ['slides by whole numbers', 'sphere inversions', 'exact ball', 'cousin of the flat picture', 'chain of circles', 'no c and no power']) if (!L.BALLS.note.includes(w)) fail('the note does not say: ' + w);
for (const id of ['ballsSize', 'ballsGrid', 'ballsDepth', 'ballsFrame']) if (!shown(id)) fail('control not on show: ' + id);
if (L.kleinTrouble() !== '' || L.kleinSwallowed() || shown('kleinWarn')) fail('a warning of the first group fired');
const s0 = sig(), g0 = grid();
if (g0[0] < 20 || g0[1] > 0) fail('start view: ' + g0[0] + ' probes hit, ' + g0[1] + ' on the outer ring');
ok('one click: Kleinian, Balls on balls, framed (' + g0[0] + ' of 165 probes hit, none on the outer ring); menu reads "Balls on balls"; note has ' + sentences + ' sentences; no warning of the first group');
if (S.k.bt !== 1.4 || S.k.bgrid !== 0 || S.k.bit !== L.BALLS.rounds) fail('defaults: ' + JSON.stringify(S.k));
if (Math.abs(+$('ballsSize').value - 55.56) > 0.06) fail('size dial shows ' + $('ballsSize').value);
ok('defaults: t = 1.4 (dial shows ' + $('ballsSize').value + ' %), square grid, depth ' + S.k.bit);

// 3. the dials
type('ballsSize', 100); await settle();
if (S.k.bt !== 1) fail('size 100 should be t = 1: ' + S.k.bt);
if (!shown('ballsWarn') || !/Drawing radius/.test($('ballsWarn').textContent)) fail('no note about the endless chain at 100');
const s100 = sig();
type('ballsSize', 25); await settle();
if (Math.abs(S.k.bt - 2.5) > 1e-9) fail('size 25 should be t = 2.5: ' + S.k.bt);
if (shown('ballsWarn')) fail('the note stayed');
const s25 = sig();
if (s100 === s0 || s25 === s0 || s25 === s100) fail('the size dial did not change the picture');
type('ballsSize', 55.6); await settle();
if (S.k.bt !== 1.4) fail('back at 55.6 t is ' + S.k.bt);
if (sig() !== s0) fail('back at the start value the picture is not the first picture');
ok('size dial: 100 gives t = 1 (and the note "' + 'The chain of balls runs out past the Drawing radius…"), 25 gives t = 2.5, 55.6 gives t = 1.4 exactly and the first picture again');
const gs = [];
for (const g of [1, 2, 0]) { $('ballsGrid').value = String(g); $('ballsGrid').dispatchEvent(new Event('change', { bubbles: true })); await settle(); if (S.k.bgrid !== g) fail('grid select: ' + S.k.bgrid); gs.push(sig()); }
if (gs[0] === gs[1] || gs[0] === gs[2] || gs[1] === gs[2] || gs[2] !== s0) fail('the grids should give three different pictures, and the square grid the first one');
ok('whole numbers: three grids, three pictures (' + gs.map(hits).join(', ') + ' probes hit: honeycomb, line, square)');
type('ballsDepth', 3); await settle(); const s3 = sig();
type('ballsDepth', 40); await settle(); const s40 = sig();
if (s3 === s0) fail('depth 3 should swell the balls');
type('ballsDepth', L.BALLS.rounds); await settle();
ok('depth: 3 rounds changes the picture (' + hits(s3) + ' probes hit against ' + hits(s0) + '), 40 rounds ' + (s40 === s0 ? 'gives the same probes as the default' : 'differs from the default in the probes'));

// 4. camera: Frame it, Reset view
L.cam.dist *= 3; L.cam.yaw += 1; L.touch(); await settle();
$('ballsFrame').click(); await settle();
if (sig() !== s0) fail('Frame it did not bring the start view back');
L.cam.dist *= 0.3; L.touch(); await settle(); $('reset').click(); await settle();
if (sig() !== s0) fail('Reset view did not bring the start view back');
S.view.zmax = 2; L.syncControls(); $('ballsFrame').click(); await settle();
if (!(S.view.zmax >= L.cam.dist) || sig() !== s0) fail('Frame it should move a zoom limit that is in the way');
L.resetZoomLimits(); go(); await settle();
ok('Frame it and Reset view bring the start view back (Frame it also moves a zoom limit that is in the way)');

// 5. the section's reset
S.k.bt = 2; S.k.bgrid = 1; S.k.bit = 9; go(); await settle();
[...$('ballsReset').querySelectorAll('button')].forEach(b => b.click()); await settle();
if (S.k.bt !== 1.4 || S.k.bgrid !== 0 || S.k.bit !== L.BALLS.rounds || S.k.group !== 1) fail('the reset of the section: ' + JSON.stringify(S.k));
ok('"Reset this section" under the dials: t, grid and depth back, the group stays');

// 6. the 2D view and its cut slider
$('flat').click(); await sleep(200); await settle();
const w = $('stage').clientWidth, h = $('stage').clientHeight, pc = L.pick(w / 2, h / 2);
if (!S.flat || !pc || Math.abs(pc[2]) > 1e-9) fail('the 2D view is not the cut at z = 0');
let flatBad = 0, flatIn = 0;
for (let i = 0; i < 2000; i++) { const p = L.pick(w * Math.random(), h * Math.random()); if (L.ballsInside(p[0], p[1], 0)) flatIn++; }
type('cut', 0.3); await settle();
if (S.cut !== 0.3) fail('the cut slider did not move the slice');
const pz = L.pick(w / 2, h / 2); if (Math.abs(pz[2] - 0.3) > 1e-9) fail('slice height');
type('cut', 0); await settle();
$('flat').click(); await sleep(200);
S.cutOn = false; go(); await settle();
ok('2D view: the cut at z = 0 (' + flatIn + ' of 2000 random points of the frame inside); the height dial moves the slice');

// 7. colours, outside and inside; traps; trap solids; the cut plane
const tryIt = async (what, f, least) => { f(); go(); await settle(); const g = grid(); if (g[0] < least) fail(what + ': ' + g[0] + ' probes hit'); out.push('   ' + what + ': ' + g[0] + ' probes hit'); };
const C = S.colour, c0 = JSON.stringify(C);
for (const m of [2, 3, 4, 5, 6, 7, 0]) await tryIt('colour by ' + m, () => { C.mode = m; }, 20);
for (const tr of [0, 1, 2, 3, 4, 6, 7, 5]) await tryIt('trap shape ' + tr, () => { C.trap = tr; }, 20);
for (const by of [0, 1, 2, 3, 5, 4]) await tryIt('trap colours by ' + by, () => { C.by = by; }, 20);
// trap solids are switched off for this group: the choice shows one plain sentence and the picture stays the plain one
for (const so of [2, 1]) {
  C.solid = so; go(); await settle();
  const notes = [...document.querySelectorAll('#colDials .note')].filter(e => e.getBoundingClientRect().width > 0).map(e => e.textContent);
  if (!notes.includes('Balls on balls has no trap solid: in this view the trap only colours the balls.')) fail('no sentence about the trap solid: ' + notes.join(' / ').slice(0, 300));
  if (shown('col-thick') || shown('col-skip')) fail('the dials of a trap solid should be put away');
  if (sig() !== s0) fail('with the trap solid choice at ' + so + ' the picture should be the plain one');
}
out.push('   trap solid choices 1 and 2: the sentence "Balls on balls has no trap solid: in this view the trap only colours the balls." shows, the picture is the plain one');
C.solid = 0;
await tryIt('cut open at z = 0, cut face painted', () => { S.cutOn = true; S.cut = 0; C.cutFace = true; C.inMode = 3; }, 20);
S.cutOn = false; C.cutFace = false; C.inMode = 0;
S.flat = true;
for (const im of [1, 2, 3, 4, 0]) { C.inMode = im; go(); await settle(); out.push('   2D view, inside coloured by ' + im + ': drawn'); }
S.flat = false; Object.assign(C, JSON.parse(c0)); go(); await settle();
if (sig() !== s0) fail('with the colours back the picture is not the first picture');
ok('colours (7 ways), 8 trap shapes, 6 "colours by", the cut with a painted face, 5 inside colourings: all draw, no program fails; trap solids are switched off with one sentence');

// 8. the examples list belongs to the first group
if (L.exampleAt() !== -1) fail('an example is marked while Balls on balls is on show');
L.applyExample(L.EXAMPLES[6]); await settle();
if (S.k.group !== 0 || S.mode !== 'k' || L.exampleAt() !== 6) fail('a Kleinian example should show the first group');
if (!shown('kleinNote') || shown('ballsNote') || shown('secApproach')) fail('after the example the panel is not the first group\'s');
ok('Examples: a Kleinian example goes to the first group (its panel, no Approach menu)');
$('kleinGroup1').click(); await sleep(100); await settle();
if (S.k.group !== 1 || !shown('ballsNote')) fail('the choice at the top of the panel did not choose Balls on balls');
Object.assign(C, JSON.parse(c0)); go(); await settle();
if (sig() !== s0) fail('the choice in the panel should give the start view of Balls on balls');
ok('the choice at the top of the panel: Balls on balls, at its start view');

// 9. picture export and 3D model
let saved = null; window.squaringLabSaveHook = (name, blob) => { saved = { name, size: blob.size }; };
if ($('exportStart')) {
  S.k.bit = 12; L.syncControls();
  $('exportSize').value = '0'; $('exportSize').dispatchEvent(new Event('change', { bubbles: true }));
  $('exportStart').click(); await sleep(300);
  for (let i = 0; i < 3000 && L.exportBusy(); i++) await sleep(50);
  if (L.exportBusy()) fail('the picture job never ended');
  if (shown('exportSave')) { $('exportSave').click(); await sleep(400); }
  ok('picture export: ' + (saved ? 'file ' + saved.name + ', ' + saved.size + ' bytes' : 'ended; message: ' + ($('exportMsg') ? $('exportMsg').textContent.slice(0, 120) : '')));
  S.k.bit = L.BALLS.rounds; L.syncControls();
}
if ($('meshStart')) {
  window.squaringLabMeshTest = { cells: 48 };
  $('meshStart').click(); await sleep(300);
  for (let i = 0; i < 6000 && L.meshBusy(); i++) await sleep(50);
  if (L.meshBusy()) fail('the model job never ended');
  const msg = $('meshMsg') ? $('meshMsg').textContent : '';
  if (!shown('meshSave')) fail('the model job did not end with a file to save: ' + msg);
  delete window.squaringLabMeshTest;
  ok('3D model (48 cells): ended with a file to save. ' + msg.slice(0, 160));
}
delete window.squaringLabSaveHook;

// 10. the scorecard and Learn: as in the Kleinian view today
if ($('card') && /undefined|NaN/.test($('card').innerText)) fail('the card shows a stray mark');
if ($('mode-l')) {
  $('mode-l').click(); await sleep(500);
  const on = document.body.classList.contains('is-learn');
  if (!on) fail('Learn did not open from Balls on balls');
  // under Learn the menu is the approach's, as it is with the first group behind it
  if ($('apMenuName').textContent === 'Balls on balls' || !shown('secApproach') || !shown('apPanels') || document.querySelectorAll('#rules input[type=radio]:checked').length !== 1) fail('under Learn the Approach menu should show the approach');
  const o2 = L.APPROACHES[(S.approach + 5) % 21]; $('ap-' + o2.id).click(); await sleep(300);
  if (S.mode !== 'k' || apId() !== o2.id || !document.body.classList.contains('is-learn')) fail('choosing an approach under Learn should stay in Learn with the Kleinian picture behind: ' + S.mode);
  if (L.learn && L.learn.cache && L.learn.cache.fault) fail('Learn reports: ' + L.learn.cache.fault);
  $('mode-k').click(); await sleep(400);
  if (document.body.classList.contains('is-learn') || S.mode !== 'k' || S.k.group !== 1) fail('coming back from Learn lost Balls on balls');
  await settle();
  if ($('apMenuName').textContent !== 'Balls on balls' || shown('apPanels')) fail('back from Learn the menu should read Balls on balls again');
  // the row, chosen under Learn, leaves Learn
  $('mode-j').click(); await sleep(200); $('mode-l').click(); await sleep(400);
  $('ap-balls').click(); await sleep(400); await settle();
  if (document.body.classList.contains('is-learn') || !(S.mode === 'k' && S.k.group === 1) || $('apMenuName').textContent !== 'Balls on balls') fail('the row chosen under Learn should leave Learn and show Balls on balls');
  $('mode-m').click(); await sleep(200); $('ap-balls').click(); await sleep(300); await settle();
  ok('Learn: opens from Balls on balls as from the first group, with the approach in the menu; an approach chosen there stays in Learn; the Kleinian button brings Balls on balls back; the row chosen under Learn leaves Learn');
}

// 11. choosing a real approach afterwards
const other = L.APPROACHES[(S.approach + 3) % L.APPROACHES.length];
$('ap-' + other.id).click(); await sleep(200);
if (S.mode !== 'm' || apId() !== other.id) fail('choosing an approach should leave the Kleinian view for where the row was chosen from (Mandelbrot): ' + S.mode + ' ' + apId());
if (!shown('secEq') || !shown('apPanels') || shown('kleinPanel') || $('apMenuName').textContent === 'Balls on balls') fail('the Approach section did not come back whole');
await settle();
const camM = JSON.stringify(L.cam);
$('mode-k').click(); await sleep(100); $('mode-m').click(); await sleep(100);
if (JSON.stringify(L.cam) !== camM) fail('the camera after choosing an approach is not the one the Mandelbrot button gives');
ok('choosing the approach "' + other.name.replace(/<[^>]*>/g, '') + '" from Balls on balls: back in the Mandelbrot view with that approach and the Mandelbrot start view');
$('mode-j').click(); await sleep(150); await settle();
$('ap-balls').click(); await sleep(150); await settle();
$('apNext').click(); await sleep(200);
if (S.mode !== 'j' || S.approach !== 0) fail('Next from the row should be the first approach, in the Julia view: ' + S.mode + ' ' + S.approach);
$('ap-balls').click(); await sleep(150); $('apPrev').click(); await sleep(200);
if (S.mode !== 'j' || apId() !== L.APPROACHES[20].id && S.approach === 0) fail('Previous from the row should be the last approach of the list');
ok('from the Julia view: the row, then the step buttons: next is the first approach, previous the last of the list (' + apId() + '), both in the Julia view');
// with the first group on show an approach's radio does what it did: the Kleinian view stays
$('mode-k').click(); await sleep(100); $('kleinGroup0').click(); await sleep(150);
$('ap-' + other.id).click(); await sleep(150);
if (S.mode !== 'k' || apId() !== other.id) fail('with the first group the radio of an approach should not leave the Kleinian view');
ok('with the first group on show, an approach chosen from a script stays in the Kleinian view, as before');

// 12. Reset everything
$('kleinGroup1').click(); await sleep(100); S.k.bt = 2; S.k.bgrid = 2; S.k.bit = 7; go();
$('resetAll').click(); await sleep(400); await settle();
if (S.mode !== 'm' || S.approach !== 0 || S.k.group !== 0 || S.k.bt !== 1.4 || S.k.bgrid !== 0 || S.k.bit !== L.BALLS.rounds) fail('Reset everything: ' + S.mode + ' ' + JSON.stringify(S.k));
$('mode-k').click(); await sleep(200);
if (!shown('kleinNote') || shown('ballsNote') || !$('kleinGroup0').checked) fail('after Reset everything the Kleinian view should hold the first group');
$('mode-m').click(); await sleep(200); await settle();
ok('Reset everything: Mandelbrot, first approach, the Kleinian view back on its first group, the three dials at their start');
return out.join('\n');

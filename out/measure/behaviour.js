// Cancelling, streams of calls, the cache, the waiting look, and the step figure's redraw guard.
const L = window.squaringLab, T = L.T, S = L.S, R = T.cardRun;
const frame = () => new Promise(r => requestAnimationFrame(r)), sleep = ms => new Promise(r => setTimeout(r, ms));
const settle = async () => { while (!T.cardIdle()) await frame(); };
const cell = id => document.getElementById(id), out = [];
const check = (name, ok, detail) => out.push(`${ok ? 'PASS' : 'FAIL'}  ${name}${detail === undefined ? '' : '  [' + detail + ']'}`);
const fresh = async (approach, n) => { S.approach = approach; S.n = n; R.cache.clear(); await sleep(320); };

// 1. a newer call cancels an older one
await fresh(0, 2);
T.updateCard(); await frame(); await frame();            // the first measurement is under way
const mid = R.slices;
S.n = 3; T.updateCard();
check('second call leaves a measurement pending', !T.cardIdle());
await settle();
const want = L.measure(v => T.MATH[T.ap().id](v, 3, { ...T.apP() }), 3);
check('the first measurement had started before it was cancelled', mid >= 1, mid + ' slices');
check('the result shown belongs to the newer call (n = 3)', Object.keys(want).every(k => Object.is(want[k], R.result[k])));
check('only the newer state is cached', R.cache.size === 1, [...R.cache.keys()].join(' | '));
check('busy label cleared', !T.busyTasks.has('measure'));
check('aria-busy removed', !cell('card').hasAttribute('aria-busy'));

// 2. a stream of calls (a dial being dragged or animated): nothing is measured until it pauses
await fresh(0, 2);
let sliced = 0, busyDuring = 0;
for (let i = 0; i < 40; i++) { S.n = 2 + i * 0.01; R.slices = 0; T.updateCard(); await frame(); sliced += R.slices; busyDuring += T.busyTasks.has('measure') ? 1 : 0; }
check('at most one slice of work during a 40-frame stream of calls', sliced <= 1, sliced + ' slices, busy label up in ' + busyDuring + ' of 40 frames');
check('measured cells are dimmed while the stream runs', cell('s-round').style.opacity === '0.45' && cell('b-round').style.opacity === '0.45');
check('plane column follows the stream at once', cell('p-round').textContent.includes('2.39×'), cell('p-round').textContent);
const t0 = performance.now(); await settle();
check('the card settles after the stream stops', R.result && cell('s-round').style.opacity === '', (performance.now() - t0).toFixed(0) + ' ms after the last call');
check('settled on the last state of the stream', R.cache.has(T.ap().id + ' ' + S.n + ' ' + JSON.stringify(T.apP())));

// 3. the cache: the same state again is shown at once, with no measuring
const before = R.result; T.updateCard();
check('a state measured before is shown without measuring again', T.cardIdle() && R.result === before && !T.busyTasks.has('measure'));

// 4. the waiting look: another approach's numbers are not left on show
await fresh(1, 2);
T.updateCard();
check('switching approach blanks the measured cells', cell('s-len').textContent === 'Measuring…' && cell('b-len').style.display === 'none', cell('s-len').textContent);
check('cells that need no measuring are filled at once', cell('s-crush').textContent.length > 10 && cell('b-crush').textContent === 'fails' || cell('b-crush').textContent.length > 0, cell('b-crush').textContent + ': ' + cell('s-crush').textContent);
check('header names the approach at once', cell('ruleHead').textContent === T.ap().name, cell('ruleHead').textContent);
await settle();
check('pills come back with the numbers', cell('b-len').style.display === '' && cell('b-len').textContent === 'holds' && cell('s-len').textContent.startsWith('|v'), cell('s-len').textContent);

// 5. same approach, new n: the old numbers stay up, dimmed, until the new ones arrive
await sleep(320); S.n = 4; const old = cell('s-round').textContent; T.updateCard();
check('same approach keeps the old numbers up, dimmed', cell('s-round').textContent === old && cell('s-round').style.opacity === '0.45');
await settle();
check('then replaces them', cell('s-round').textContent !== old && cell('s-round').style.opacity === '', cell('s-round').textContent);

// 6. the step figure is registered once by buildCard and skips redraws when nothing it shows has changed
const mine = T.hooks.view.filter(f => f === T.drawStep3d).length; T.buildCard(); T.updateCard(); await settle();
check('buildCard does not register drawStep3d a second time', T.hooks.view.filter(f => f === T.drawStep3d).length === mine, mine + ' registered (the baseline boot adds one of its own)');
let clears = 0; const proto = CanvasRenderingContext2D.prototype, orig = proto.clearRect;
proto.clearRect = function (...a) { if (this.canvas.id === 'step3d') clears++; return orig.apply(this, a); };
T.drawStep3d(); T.drawStep3d(); T.drawStep3d();
const idleClears = clears;
L.cam.yaw += 0.2; T.drawStep3d(); const afterTurn = clears - idleClears;
T.buildStep3d(); T.drawStep3d(); const afterBuild = clears - idleClears - afterTurn;
proto.clearRect = orig; L.cam.yaw -= 0.2;
check('drawStep3d skips when nothing changed, redraws after a turn and after a rebuild', idleClears === 0 && afterTurn === 1 && afterBuild === 1, `${idleClears} / ${afterTurn} / ${afterBuild}`);

S.approach = 0; S.n = 2; L.syncControls(); L.refresh(false);
return out.join('\n');

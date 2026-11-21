// Round 22, entrycheck second pass: attempts to break the two entries on the repaired page, with weight on what the
// second pass changed (the card's watch on c, the Learn tab's orbit). HEAD of drv.py, then this common part, per step.
const RAB = [-0.122561, 0.744862, 0];
const cardText = () => txt('card');
const cardDone = async () => { await sleep(350); for (let i = 0; i < 800 && !L.cardIdle(); i++) await sleep(25); await sleep(150); };
const pick = async (id, c) => { $('mode-j').click(); await sleep(150); $('ap-' + id).click(); await sleep(250); if (apId() !== id) fail('could not choose ' + id); S.eq = 'z^n + c'; S.z0 = '0'; S.n = 2; S.iter = 30; S.c = (c || [-1, 0, 0]).slice(); S.flat = false; S.cutOn = false; S.mosaic = false; S.abs = [0, 0, 0]; S.flip = [0, 0]; if (S.param.pulledplane) Object.assign(S.param.pulledplane, { hold: 0.05, ease: 0.7, cpull: 16 }); L.resetCam(); go(); await settle(); await cardDone(); };
const choose = async (selId, re) => { const sel = $(selId); const opt = [...sel.options].find(o => re.test(o.textContent)); if (!opt) fail('no option ' + re); sel.value = opt.value; sel.dispatchEvent(new Event('change', { bubbles: true })); await sleep(100); };
const fresh = async () => { go(); await settle(); await cardDone(); return cardText(); };
const type = (id, v) => { const e = $(id); if (!e) fail('no control ' + id); e.value = String(v); e.dispatchEvent(new Event('input', { bubbles: true })); e.dispatchEvent(new Event('change', { bubbles: true })); e.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', bubbles: true })); };
const sig = () => { const w = $('stage').clientWidth, h = $('stage').clientHeight; let s = '', sum = 0; for (let i = 0; i < 15; i++) for (let j = 0; j < 11; j++) { const p = L.pick(w * (i + 0.5) / 15, h * (j + 0.5) / 11); s += p ? '1' : '0'; if (p) sum += p[0] + 2 * p[1] + 3 * p[2]; } return s + ' ' + sum.toFixed(4); };
const own = (id, z0, c, steps, q, n, ab) => { const R = L.CARRY[id]; let st = R.start(q), z = z0.slice(); const tr = [z.slice()]; for (let k = 0; k < steps; k++) { const m = ab ? z.map((x, i) => (ab[i] ? Math.abs(x) : x)) : z; st = R.step(st, m, c, q); const w = R.pw(st, m, n); z = [w[0] + c[0], w[1] + c[1], w[2] + c[2]]; tr.push(z.slice()); } return tr; };
const far = (a, b) => (a.length !== b.length ? NaN : Math.max(...a.map((v, i) => Math.hypot(v[0] - b[i][0], v[1] - b[i][1], v[2] - b[i][2]))));
const bad = t => /undefined|NaN|\[object/.test(t);
const O = window.__o || (window.__o = {});
//@@STEP
// ---- 5. the card under stress
const o = O.card = [];
// a. two powers in one step, then a jump from the list
await pick('pulledplane'); S.eq = 'z^2 + z^3 + c'; go(); await settle(); await cardDone(); const a0 = cardText();
await choose('juliaPreset', /rabbit/i); await settle(); await cardDone(); const a1 = cardText(); const a2 = await fresh();
o.push('a. z^2 + z^3 + c, jump to the rabbit: card changed ' + (a0 !== a1) + ', same as a fresh one ' + (a1 === a2) + ', stray words ' + bad(a1) + ', power note: ' + (txt('cardPowNote') || '').slice(0, 90));
// b. Mandelbrot from c^2
S.eq = 'z^n + c'; S.z0 = 'c^2'; $('mode-m').click(); await sleep(250); await settle(); await cardDone(); const b1 = cardText(); const b2 = await fresh();
o.push('b. Mandelbrot from c^2: card same as a fresh one ' + (b1 === b2) + ', stray words ' + bad(b1)); S.z0 = '0';
// c. the entry changed while a measurement is under way
await pick('pulledplane'); S.c[1] = 0.33; L.touch(); await sleep(30); $('ap-turnalong').click(); await sleep(250); await settle(); await cardDone();
const c1 = cardText(), c2 = await fresh(); $('ap-pulledplane').click(); await sleep(250); await settle(); await cardDone(); const c3 = cardText(), c4 = await fresh();
o.push('c. entry changed during a measurement: turnalong card same as fresh ' + (c1 === c2) + ' (head: ' + (txt('ruleHead') || '') + '); back to pulledplane at c ' + JSON.stringify(S.c) + ': same as fresh ' + (c3 === c4));
// d. the Kleinian view, c moved there, and back
await pick('pulledplane'); const d0 = cardText(); $('mode-k').click(); await sleep(300); await settle(); S.c = RAB.slice(); L.touch(); await settle(); await cardDone();
$('mode-j').click(); await sleep(300); await settle(); await cardDone(); const d1 = cardText(), d2 = await fresh();
o.push('d. Kleinian view, hidden c moved to the rabbit, back to Julia: card changed ' + (d0 !== d1) + ', same as fresh ' + (d1 === d2));
$('mode-j').click(); await sleep(200); S.n = 2; S.c = [-1, 0, 0]; go(); await settle();
return JSON.stringify(o);
//@@STEP
const o = [];
for (const id of ['alongonce']) for (const n of [1, -2]) {
  await pick(id); S.n = n; go(); await settle(); await cardDone(); const j = cardText();
  S.c = [-0.2, 0.5, 0.3]; L.touch(); await settle(); await cardDone(); const j2 = cardText(), j3 = await fresh();
  $('mode-m').click(); await sleep(250); await settle(); await cardDone(); const m = cardText();
  o.push('e. ' + id + ' power ' + n + ': Julia card stray ' + bad(j) + ', after c moved by touch only same as fresh ' + (j2 === j3) + (id === 'pulledplane' ? ', changed ' + (j !== j2) : ', unchanged ' + (j === j2)) + '; Mandelbrot card stray ' + bad(m));
}
S.n = 2; $('mode-j').click(); await sleep(200); S.c = [-1, 0, 0]; go(); await settle();
return JSON.stringify(o);
//@@STEP
const o = [];
for (const id of ['alongonce']) for (const n of [2.5, 3]) {
  await pick(id); S.n = n; go(); await settle(); await cardDone(); const j = cardText();
  S.c = [-0.2, 0.5, 0.3]; L.touch(); await settle(); await cardDone(); const j2 = cardText(), j3 = await fresh();
  $('mode-m').click(); await sleep(250); await settle(); await cardDone(); const m = cardText();
  o.push('e. ' + id + ' power ' + n + ': Julia card stray ' + bad(j) + ', after c moved by touch only same as fresh ' + (j2 === j3) + (id === 'pulledplane' ? ', changed ' + (j !== j2) : ', unchanged ' + (j === j2)) + '; Mandelbrot card stray ' + bad(m));
}
S.n = 2; $('mode-j').click(); await sleep(200); S.c = [-1, 0, 0]; go(); await settle();
return JSON.stringify(o);
//@@STEP
const o = [];
for (const id of ['pulledplane']) for (const n of [1, -2]) {
  await pick(id); S.n = n; go(); await settle(); await cardDone(); const j = cardText();
  S.c = [-0.2, 0.5, 0.3]; L.touch(); await settle(); await cardDone(); const j2 = cardText(), j3 = await fresh();
  $('mode-m').click(); await sleep(250); await settle(); await cardDone(); const m = cardText();
  o.push('e. ' + id + ' power ' + n + ': Julia card stray ' + bad(j) + ', after c moved by touch only same as fresh ' + (j2 === j3) + (id === 'pulledplane' ? ', changed ' + (j !== j2) : ', unchanged ' + (j === j2)) + '; Mandelbrot card stray ' + bad(m));
}
S.n = 2; $('mode-j').click(); await sleep(200); S.c = [-1, 0, 0]; go(); await settle();
return JSON.stringify(o);
//@@STEP
const o = [];
for (const id of ['pulledplane']) for (const n of [2.5, 3]) {
  await pick(id); S.n = n; go(); await settle(); await cardDone(); const j = cardText();
  S.c = [-0.2, 0.5, 0.3]; L.touch(); await settle(); await cardDone(); const j2 = cardText(), j3 = await fresh();
  $('mode-m').click(); await sleep(250); await settle(); await cardDone(); const m = cardText();
  o.push('e. ' + id + ' power ' + n + ': Julia card stray ' + bad(j) + ', after c moved by touch only same as fresh ' + (j2 === j3) + (id === 'pulledplane' ? ', changed ' + (j !== j2) : ', unchanged ' + (j === j2)) + '; Mandelbrot card stray ' + bad(m));
}
S.n = 2; $('mode-j').click(); await sleep(200); S.c = [-1, 0, 0]; go(); await settle();
return JSON.stringify(o);
//@@STEP
const o = [];
// f. a c out of the flat plane: what the slice line of each card says, and is it so (flat points, first squaring, against the complex square)
for (const id of ['alongonce', 'pulledplane']) {
  await pick(id, [-0.5, 0.2, 0.4]); const t = cardText(); const line = (t.match(/Contains the flat set.*$/) || [''])[0].slice(0, 260);
  let worst = 0; for (let k = 1; k <= 500; k++) { const v = [Math.sin(k * 1.3), Math.sin(k * 2.1), 0], w = L.MATH[id](v, 2, S.param[id] || {}, S.c.slice()); worst = Math.max(worst, Math.hypot(w[0] - (v[0] * v[0] - v[1] * v[1]), w[1] - 2 * v[0] * v[1], w[2])); }
  o.push('f. ' + id + ', c = (-0.5, 0.2, 0.4): ' + line + ' || first squaring of flat points is off the complex square by at most ' + worst.toExponential(1));
}
S.n = 2; $('mode-j').click(); await sleep(200); S.c = [-1, 0, 0]; go(); await settle();
return JSON.stringify(o);
//@@STEP
// Learn at power 0 (my first run set the power wrongly for this case)
const o = [];
for (const id of ['alongonce', 'pulledplane']) {
  $('mode-j').click(); await sleep(200); $('ap-' + id).click(); await sleep(250); S.n = 0; S.eq = 'z^n + c'; S.abs = [0, 0, 0]; S.flip = [0, 0]; go(); await sleep(120);
  $('mode-l').click(); await sleep(400); $('learnSpace3').click(); await sleep(250); L.learn.set({ z: [0.5, -0.4, 0.3], c: [-0.8, 0.1, 0.2] });
  for (let i = 0; i < 3; i++) { $('learnNext').click(); await sleep(110); }
  const st = L.learn.state();
  o.push(id + ' power ' + S.n + ': ' + (st.orbit.length - 1) + ' steps, off own ' + far(st.orbit, own(id, [0.5, -0.4, 0.3], [-0.8, 0.1, 0.2], st.orbit.length - 1, S.param[id] || {}, 0)).toExponential(1) + ', fault "' + (L.learn.cache.fault || '') + '", stray words ' + bad(L.learn.cache.say.join(' ') + st.note) + ', says: ' + L.learn.cache.say.join(' | ').slice(0, 300));
  $('learnAgain').click(); await sleep(150);
}
$('mode-j').click(); await sleep(300); S.n = 2; S.c = [-1, 0, 0]; go(); await settle();
return JSON.stringify(o);
//@@STEP shot: out/r22/entrycheck2/break/ao-rabbit10.png
await pick('alongonce', [-0.122561, 0.7335, 0.1293]); S.iter = 40; go(); await settle();
return 'alongonce, rabbit c turned 10 degrees, Iterations 40: ' + grid()[0] + ' of 165 probes stop';
//@@STEP shot: out/r22/entrycheck2/break/ao-m1z03.png
await pick('alongonce', [-1, 0, 0.3]); S.iter = 40; go(); await settle();
return 'alongonce, c = (-1, 0, 0.3), Iterations 40: ' + grid()[0] + ' of 165 probes stop';
//@@STEP shot: out/r22/entrycheck2/break/pp-rabbit10.png
await pick('pulledplane', [-0.122561, 0.7335, 0.1293]); S.iter = 40; go(); await settle();
return 'pulledplane, rabbit c turned 10 degrees, Iterations 40: ' + grid()[0] + ' of 165 probes stop';
//@@STEP shot: out/r22/entrycheck2/break/pp-m1z03.png
await pick('pulledplane', [-1, 0, 0.3]); S.iter = 40; go(); await settle();
return 'pulledplane, c = (-1, 0, 0.3), Iterations 40: ' + grid()[0] + ' of 165 probes stop';
//@@STEP shot: out/r22/entrycheck2/break/pp-mosaic.png
await pick('pulledplane'); S.mode = 'm'; S.mosaic = true; S.iter = 20; go(); await settle();
return 'pulledplane mosaic: ' + grid()[0] + ' probes';
//@@STEP shot: out/r22/entrycheck2/break/ao-pow-2.png
await pick('alongonce', [0.3, 0.2, 0.1]); S.mosaic = false; S.n = -2; go(); await settle();
return 'alongonce power -2: ' + grid()[0] + ' probes';
//@@STEP
S.n = 2; S.mode = 'j'; S.mosaic = false; S.c = [-1, 0, 0]; go(); await settle();
return 'done';

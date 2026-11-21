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
// ---- 1. drawing: powers 1, 3, -2, 2.5, the inside-out equation, two powers in one step, mosaic, the 2D cut, the cut plane
const o = O.drawA = [];
const scenes = [
  ['power 1, Julia c = -1', () => { S.n = 1; }],
  ['power 1, Mandelbrot', () => { S.n = 1; S.mode = 'm'; }],
  ['power 3, Julia c = (0.3, 0.2, 0)', () => { S.n = 3; S.c = [0.3, 0.2, 0]; }],
  ['power 3, Mandelbrot', () => { S.n = 3; S.mode = 'm'; }],
  ['power -2, Julia c = (0.3, 0.2, 0.1)', () => { S.n = -2; S.c = [0.3, 0.2, 0.1]; }],
  ['z^-n + c (inside out), Mandelbrot', () => { S.eq = 'z^-n + c'; S.mode = 'm'; }],
  ['power 2.5, Julia c = -1', () => { S.n = 2.5; }],
  ['z^2 + z^3 + c, Julia c = (-0.2, 0.1, 0)', () => { S.eq = 'z^2 + z^3 + c'; S.c = [-0.2, 0.1, 0]; }],
  ['z^2 + z^3 + c, Mandelbrot', () => { S.eq = 'z^2 + z^3 + c'; S.mode = 'm'; }],
  ['mosaic, Mandelbrot', () => { S.mode = 'm'; S.mosaic = true; }],
  ['mosaic in the 2D view', () => { S.mode = 'm'; S.mosaic = true; S.flat = true; }],
  ['2D cut of the rabbit', () => { S.c = RAB.slice(); S.flat = true; }],
  ['cut plane on, Julia c = -1', () => { S.cutOn = true; }],
  ['|x| and |z| ticked, flip, Julia c = -1', () => { S.abs = [1, 0, 1]; S.flip = [1, 0]; }],
  ['Iterations 1', () => { S.iter = 1; }],
  ['Iterations 200, rabbit', () => { S.iter = 200; S.c = RAB.slice(); }],
];
for (const id of ['alongonce']) for (const [what, f] of scenes) {
  S.mode = 'j'; S.eq = 'z^n + c'; S.z0 = '0'; S.n = 2; S.iter = 30; S.c = [-1, 0, 0]; S.flat = false; S.cutOn = false; S.mosaic = false; S.abs = [0, 0, 0]; S.flip = [0, 0];
  $('mode-j').click(); await sleep(60); $('ap-' + id).click(); await sleep(120);
  try { f(); L.resetCam(); go(); await settle(); await cardDone(); const g = S.flat ? ['2D', 0] : grid(); const ct = cardText();
    o.push(id + ' | ' + what + ': ' + (S.flat ? '2D view drawn' : g[0] + ' of 165 probes') + (L.R.failed ? ' PROGRAM FAILED ' + L.R.failed : '') + (bad(ct) ? ' CARD HAS A STRAY WORD' : '') + (bad($('f-' + id).textContent) ? ' FORMULA LINE HAS A STRAY WORD' : '')); }
  catch (e) { o.push(id + ' | ' + what + ': FAILED ' + e.message); }
}
S.mode = 'j'; S.eq = 'z^n + c'; S.n = 2; S.iter = 30; S.c = [-1, 0, 0]; S.flat = false; S.cutOn = false; S.mosaic = false; S.abs = [0, 0, 0]; S.flip = [0, 0]; go(); await settle();
return JSON.stringify(o);
//@@STEP
// ---- 1. drawing: powers 1, 3, -2, 2.5, the inside-out equation, two powers in one step, mosaic, the 2D cut, the cut plane
const o = O.drawB = [];
const scenes = [
  ['power 1, Julia c = -1', () => { S.n = 1; }],
  ['power 1, Mandelbrot', () => { S.n = 1; S.mode = 'm'; }],
  ['power 3, Julia c = (0.3, 0.2, 0)', () => { S.n = 3; S.c = [0.3, 0.2, 0]; }],
  ['power 3, Mandelbrot', () => { S.n = 3; S.mode = 'm'; }],
  ['power -2, Julia c = (0.3, 0.2, 0.1)', () => { S.n = -2; S.c = [0.3, 0.2, 0.1]; }],
  ['z^-n + c (inside out), Mandelbrot', () => { S.eq = 'z^-n + c'; S.mode = 'm'; }],
  ['power 2.5, Julia c = -1', () => { S.n = 2.5; }],
  ['z^2 + z^3 + c, Julia c = (-0.2, 0.1, 0)', () => { S.eq = 'z^2 + z^3 + c'; S.c = [-0.2, 0.1, 0]; }],
  ['z^2 + z^3 + c, Mandelbrot', () => { S.eq = 'z^2 + z^3 + c'; S.mode = 'm'; }],
  ['mosaic, Mandelbrot', () => { S.mode = 'm'; S.mosaic = true; }],
  ['mosaic in the 2D view', () => { S.mode = 'm'; S.mosaic = true; S.flat = true; }],
  ['2D cut of the rabbit', () => { S.c = RAB.slice(); S.flat = true; }],
  ['cut plane on, Julia c = -1', () => { S.cutOn = true; }],
  ['|x| and |z| ticked, flip, Julia c = -1', () => { S.abs = [1, 0, 1]; S.flip = [1, 0]; }],
  ['Iterations 1', () => { S.iter = 1; }],
  ['Iterations 200, rabbit', () => { S.iter = 200; S.c = RAB.slice(); }],
];
for (const id of ['pulledplane']) for (const [what, f] of scenes) {
  S.mode = 'j'; S.eq = 'z^n + c'; S.z0 = '0'; S.n = 2; S.iter = 30; S.c = [-1, 0, 0]; S.flat = false; S.cutOn = false; S.mosaic = false; S.abs = [0, 0, 0]; S.flip = [0, 0];
  $('mode-j').click(); await sleep(60); $('ap-' + id).click(); await sleep(120);
  try { f(); L.resetCam(); go(); await settle(); await cardDone(); const g = S.flat ? ['2D', 0] : grid(); const ct = cardText();
    o.push(id + ' | ' + what + ': ' + (S.flat ? '2D view drawn' : g[0] + ' of 165 probes') + (L.R.failed ? ' PROGRAM FAILED ' + L.R.failed : '') + (bad(ct) ? ' CARD HAS A STRAY WORD' : '') + (bad($('f-' + id).textContent) ? ' FORMULA LINE HAS A STRAY WORD' : '')); }
  catch (e) { o.push(id + ' | ' + what + ': FAILED ' + e.message); }
}
S.mode = 'j'; S.eq = 'z^n + c'; S.n = 2; S.iter = 30; S.c = [-1, 0, 0]; S.flat = false; S.cutOn = false; S.mosaic = false; S.abs = [0, 0, 0]; S.flip = [0, 0]; go(); await settle();
return JSON.stringify(o);
//@@STEP
// ---- 2. switching back and forth: each entry draws the same picture, and shows the same card, each time it is chosen
const o = O.sw = {};
const seq = ['alongonce', 'pulledplane', 'turnalong', 'alongonce', 'mercator', 'pulledplane', 'windsq', 'alongonce', 'lathe', 'pulledplane', 'alongonce', 'pulledplane'];
for (const [tag, set] of [['rabbit', () => { S.mode = 'j'; S.c = RAB.slice(); S.iter = 26; }], ['mandel', () => { S.mode = 'm'; S.iter = 20; }]]) {
  const seen = {}, cards = {}; let diff = 0, cdiff = 0;
  await pick('mercator'); set(); go(); await settle();
  for (const id of seq) {
    $('ap-' + id).click(); await sleep(200); await settle(); await cardDone();
    const s = sig(), c = cardText();
    if (seen[id] !== undefined && seen[id] !== s) diff++; seen[id] = s;
    if (cards[id] !== undefined && cards[id] !== c) cdiff++; cards[id] = c;
  }
  o[tag] = 'pictures that differ from the first time: ' + diff + ', cards that differ: ' + cdiff + ' (' + seq.length + ' choices); probes ' + Object.entries(seen).map(([k, v]) => k + ' ' + (v.split(' ')[0].match(/1/g) || []).length).join(', ');
}
$('mode-j').click(); await sleep(200);
return JSON.stringify(o);
//@@STEP
// ---- 3. a power in the start value: the shader against the page's own rule, started the way the note says
const o = O.z0 = [];
const NB = 96, box = [-0.4, 0, 2.6], zs = 0.12, iter = 22;
const flatP = v => L.CARRY.alongonce.pw(0, v, 2);   // count 0: the one-plane square (what the note says the start value is taken by)
for (const id of ['alongonce', 'pulledplane']) {
  await pick(id); S.mode = 'm'; S.z0 = 'c^2'; S.iter = iter; go(); await settle();
  const snap = L.takeSnapshot(); const a = await L.sampleSlice(snap, box[0], box[1], box[2], zs, NB); L.releaseSnapshot(snap);
  const R = L.CARRY[id], q = S.param[id] || {}; let differ = 0, inside = 0, amb = 0;
  for (let j = 0; j < NB; j++) for (let i = 0; i < NB; i++) {
    const c = [box[0] + box[2] * ((i + 0.5) / NB - 0.5), box[1] + box[2] * ((j + 0.5) / NB - 0.5), zs];
    let st = R.start(q), z = flatP(c), k = 0;
    for (; k < iter; k++) { st = R.step(st, z, c, q); const w = R.pw(st, z, 2); z = [w[0] + c[0], w[1] + c[1], w[2] + c[2]]; if (!(z[0] * z[0] + z[1] * z[1] + z[2] * z[2] < 4096)) break; }
    const d = a[4 * (j * NB + i) + 3], lab = d < 0, js = k >= iter;
    if (!(d < 0) && !(d > 0)) amb++; else if (lab !== js) differ++; if (lab) inside++;
  }
  // the other reading (the start value's power taken as a FIRST squaring, and counted) for contrast
  let other = 0;
  for (let j = 0; j < NB; j++) for (let i = 0; i < NB; i++) {
    const c = [box[0] + box[2] * ((i + 0.5) / NB - 0.5), box[1] + box[2] * ((j + 0.5) / NB - 0.5), zs];
    let st = R.step(R.start(q), c, c, q), z = R.pw(st, c, 2), k = 0;
    for (; k < iter; k++) { st = R.step(st, z, c, q); const w = R.pw(st, z, 2); z = [w[0] + c[0], w[1] + c[1], w[2] + c[2]]; if (!(z[0] * z[0] + z[1] * z[1] + z[2] * z[2] < 4096)) break; }
    const d = a[4 * (j * NB + i) + 3]; if ((d < 0) !== (k >= iter)) other++;
  }
  o.push(id + ', Mandelbrot from c^2, slice z = ' + zs + ', ' + NB * NB + ' points: inside ' + inside + '; shader against "start value by the flat one-plane square, not counted": ' + differ + ' differ (' + amb + ' unclear); against "counted as a first squaring": ' + other + ' differ');
}
S.z0 = '0'; $('mode-j').click(); await sleep(200); go(); await settle();
return JSON.stringify(o);
//@@STEP
// ---- 4. Learn under stress
const o = O.learn = [];
const enter = async (id, z0, c, n) => { $('mode-j').click(); await sleep(200); $('ap-' + id).click(); await sleep(250); S.n = n || 2; S.eq = 'z^n + c'; S.abs = [0, 0, 0]; S.flip = [0, 0]; Object.assign(S.param.pulledplane, { hold: 0.05, ease: 0.7, cpull: 16 }); go(); await sleep(120); $('mode-l').click(); await sleep(400); $('learnSpace3').click(); await sleep(250); L.learn.set({ z: z0, c }); };
const next = async k => { for (let i = 0; i < k; i++) { $('learnNext').click(); await sleep(110); } return L.learn.state(); };
const Z = [0.5, -0.4, 0.3], C = [-0.8, 0.1, 0.2];
// a. an orbit that leaves: Next step many times
await enter('alongonce', [0.9, 0.8, 0.7], [0.5, 0.5, 0.5]); let st = await next(10);
o.push('a. Along once, an orbit that leaves: Next step x10 -> ' + (st.orbit.length - 1) + ' steps on show, fault "' + (L.learn.cache.fault || '') + '", away ' + L.learn.cache.away + ', stray words ' + bad(L.learn.cache.say.join(' ')));
// b. change the entry while at step 3
await enter('pulledplane', Z, C); st = await next(3); const before = st.orbit.map(v => v.slice());
$('ap-turnalong').click(); await sleep(300); const t1 = L.learn.state();
$('ap-alongonce').click(); await sleep(300); const t2 = L.learn.state();
$('ap-pulledplane').click(); await sleep(300); const t3 = L.learn.state();
o.push('b. entry changed at step 3 (approach list on show: ' + ($('ap-turnalong').getBoundingClientRect().width > 0) + '): turnalong ' + (t1.orbit.length - 1) + ' steps; alongonce off its own orbit ' + far(t2.orbit, own('alongonce', Z, C, t2.orbit.length - 1, {}, 2)).toExponential(1) + '; back to pulledplane off its own ' + far(t3.orbit, own('pulledplane', Z, C, t3.orbit.length - 1, S.param.pulledplane, 2)).toExponential(1) + ', same as before the change ' + (far(t3.orbit, before) < 1e-12));
// c. a dial of Pulled plane moved at step 3
type('par-pulledplane-holdNum', 0.3); await sleep(400); const t4 = L.learn.state();
o.push('c. first dial typed 0.3 at step 3 (' + JSON.stringify(S.param.pulledplane) + '): ' + (t4.orbit.length - 1) + ' steps, off the own orbit with that dial ' + far(t4.orbit, own('pulledplane', Z, C, t4.orbit.length - 1, S.param.pulledplane, 2)).toExponential(1) + ', orbit changed ' + !(far(t4.orbit, before) < 1e-9));
Object.assign(S.param.pulledplane, { hold: 0.05, ease: 0.7, cpull: 16 }); L.syncControls(); L.touch(); await sleep(300);
// d. the power changed at step 3
S.n = 3; L.syncControls(); L.touch(); await sleep(400); const t5 = L.learn.state();
o.push('d. power set to 3 at step 3: ' + (t5.orbit.length - 1) + ' steps, off the own orbit ' + far(t5.orbit, own('pulledplane', Z, C, t5.orbit.length - 1, S.param.pulledplane, 3)).toExponential(1));
S.n = 2; L.syncControls(); L.touch(); await sleep(300);
// e. |y| ticked at step 3
S.abs = [0, 1, 0]; L.syncControls(); L.touch(); await sleep(400); const t6 = L.learn.state();
o.push('e. |y| ticked: ' + (t6.orbit.length - 1) + ' steps, off the own orbit ' + far(t6.orbit, own('pulledplane', Z, C, t6.orbit.length - 1, S.param.pulledplane, 2, [0, 1, 0])).toExponential(1) + ', moves ' + L.learn.cache.names.join(' / '));
S.abs = [0, 0, 0]; L.syncControls(); L.touch(); await sleep(300);
// f. the page's Back / Fwd / Play / Again buttons at step 3
const k0 = L.learn.k; let msg = 'f. buttons at step ' + k0 + ':';
for (const b of ['learnBack', 'learnBack', 'learnFwd', 'learnPlay', 'learnAgain']) { const e = $(b); if (!e) { msg += ' no ' + b + ';'; continue; } e.click(); await sleep(350); const s = L.learn.state(); msg += ' ' + b + ' -> step ' + L.learn.k + ', ' + (s.orbit.length - 1) + ' orbit steps, off own ' + far(s.orbit, own('pulledplane', Z, C, s.orbit.length - 1, S.param.pulledplane, 2)).toExponential(0) + ';'; }
o.push(msg);
// g. companions: at the first step each companion is a fresh orbit of its own (exact); at a later step they take the main orbit's page
for (const id of ['pulledplane', 'alongonce']) for (const show of ['circle', 'all']) {
  await enter(id, Z, C); L.learn.set({ show }); await sleep(250);
  const K = L.learn.cache, q = S.param[id] || {}, first = K.comp[0], last = K.comp[K.comp.length - 1];
  const want0 = first.map(v => own(id, v, C, 1, q, 2)[1]); const d0 = far(last, want0), fin0 = last.every(v => v.every(isFinite));
  const s2 = await next(2); const K2 = L.learn.cache, f2 = K2.comp[0], l2 = K2.comp[K2.comp.length - 1];
  // what a companion would do if it were an orbit of its own at this step is not defined (it has no history); what the page does: the main orbit's carried state, then this step
  const R = L.CARRY[id]; let stc = R.start(q), z = Z.slice(); for (let k = 0; k < s2.orbit.length - 1; k++) { stc = R.step(stc, z, C, q); const w = R.pw(stc, z, 2); z = [w[0] + C[0], w[1] + C[1], w[2] + C[2]]; }
  const want2 = f2.map(v => { const s3 = R.step(stc, v, C, q), w = R.pw(s3, v, 2); return [w[0] + C[0], w[1] + C[1], w[2] + C[2]]; });
  o.push('g. ' + id + ', companions "' + show + '" (' + first.length + ' points): first step off "each a fresh orbit" ' + d0.toExponential(1) + ', all finite ' + fin0 + '; step ' + (L.learn.k + 1) + ' off "the main orbit\'s carried state, then this step" ' + far(l2, want2).toExponential(1) + ', all finite ' + l2.every(v => v.every(isFinite)));
  L.learn.set({ show: 'none' });
}
// h. start on the x-axis and with the first dial at 0 (nothing holds the page)
await enter('pulledplane', [0.5, 0, 0], [-1, 0, 0]); Object.assign(S.param.pulledplane, { hold: 0 }); L.syncControls(); L.touch(); await sleep(300); st = await next(3);
o.push('h. first dial 0, start on the x-axis, c = -1: ' + (st.orbit.length - 1) + ' steps, last point ' + st.orbit[st.orbit.length - 1].map(x => x.toFixed(4)).join(', ') + ' (flat: 0.5 -> -0.75 -> -0.4375 -> -0.8086), stray words ' + bad(L.learn.cache.say.join(' ')));
L.learn.set({ z: [0.3, 0.2, 0.4], c: [-0.5, 0.1, 0.3] }); st = await next(3);
o.push('h2. first dial 0, a point in space: ' + (st.orbit.length - 1) + ' steps, off the own orbit ' + far(st.orbit, own('pulledplane', [0.3, 0.2, 0.4], [-0.5, 0.1, 0.3], st.orbit.length - 1, S.param.pulledplane, 2)).toExponential(1) + ', stray words ' + bad(L.learn.cache.say.join(' ')));
Object.assign(S.param.pulledplane, { hold: 0.05, ease: 0.7, cpull: 16 }); L.syncControls(); L.touch(); await sleep(200);
// i. "use the Julia c" button, and powers 0 and 1
S.c = [-0.3, 0.4, 0.5]; const jc = $('learnJuliaC'); if (jc) { jc.click(); await sleep(300); st = await next(2); o.push('i. "Julia c" button: Learn c ' + JSON.stringify(L.learn.pts[3].c) + ', off the own orbit ' + far(st.orbit, own('pulledplane', L.learn.pts[3].z, L.learn.pts[3].c, st.orbit.length - 1, S.param.pulledplane, 2)).toExponential(1)); } else o.push('i. no learnJuliaC button');
for (const id of ['alongonce', 'pulledplane']) for (const n of [1, 0, 0.5]) { await enter(id, Z, C, n); st = await next(3); o.push('j. ' + id + ' power ' + n + ': ' + (st.orbit.length - 1) + ' steps, off own ' + far(st.orbit, own(id, Z, C, st.orbit.length - 1, S.param[id] || {}, n)).toExponential(1) + ', fault "' + (L.learn.cache.fault || '') + '", stray words ' + bad(L.learn.cache.say.join(' ') + st.note)); }
$('learnAgain').click(); await sleep(150); $('mode-j').click(); await sleep(300); S.n = 2; S.c = [-1, 0, 0]; go(); await settle();
return JSON.stringify(o);
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
// e. powers 1, 0, -2, 2.5, 3 in both views, both entries: no stray words, card up to date after a jump
for (const id of ['alongonce', 'pulledplane']) for (const n of [1, 0, -2, 2.5, 3]) {
  await pick(id); S.n = n; go(); await settle(); await cardDone(); const j = cardText();
  S.c = [-0.2, 0.5, 0.3]; L.touch(); await settle(); await cardDone(); const j2 = cardText(), j3 = await fresh();
  $('mode-m').click(); await sleep(250); await settle(); await cardDone(); const m = cardText();
  o.push('e. ' + id + ' power ' + n + ': Julia card stray ' + bad(j) + ', after c moved by touch only same as fresh ' + (j2 === j3) + (id === 'pulledplane' ? ', changed ' + (j !== j2) : ', unchanged ' + (j === j2)) + '; Mandelbrot card stray ' + bad(m));
}
// f. a c out of the flat plane: what the slice line of each card says, and is it so (flat points, first squaring, against the complex square)
for (const id of ['alongonce', 'pulledplane']) {
  await pick(id, [-0.5, 0.2, 0.4]); const t = cardText(); const line = (t.match(/Contains the flat set.*$/) || [''])[0].slice(0, 260);
  let worst = 0; for (let k = 1; k <= 500; k++) { const v = [Math.sin(k * 1.3), Math.sin(k * 2.1), 0], w = L.MATH[id](v, 2, S.param[id] || {}, S.c.slice()); worst = Math.max(worst, Math.hypot(w[0] - (v[0] * v[0] - v[1] * v[1]), w[1] - 2 * v[0] * v[1], w[2])); }
  o.push('f. ' + id + ', c = (-0.5, 0.2, 0.4): ' + line + ' || first squaring of flat points is off the complex square by at most ' + worst.toExponential(1));
}
S.n = 2; $('mode-j').click(); await sleep(200); S.c = [-1, 0, 0]; go(); await settle();
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

// Round 22, entrycheck second pass: each of the seven earlier defects, tried again on the repaired page, through the
// page's own controls where there is one. (HEAD of drv.py is in front of every step, then this common part.)
const RAB = [-0.122561, 0.744862, 0];
const cardText = () => txt('card');
const cardDone = async () => { await sleep(350); for (let i = 0; i < 800 && !L.cardIdle(); i++) await sleep(25); await sleep(150); };
const pick = async (id, c) => { $('mode-j').click(); await sleep(150); $('ap-' + id).click(); await sleep(250); if (apId() !== id) fail('could not choose ' + id); S.eq = 'z^n + c'; S.z0 = '0'; S.n = 2; S.iter = 30; S.c = (c || [-1, 0, 0]).slice(); S.flat = false; S.cutOn = false; S.mosaic = false; S.abs = [0, 0, 0]; S.flip = [0, 0]; L.resetCam(); go(); await settle(); await cardDone(); };
const choose = async (selId, re) => { const sel = $(selId); if (!sel) fail('no list ' + selId); const opt = [...sel.options].find(o => re.test(o.textContent)); if (!opt) fail('no option ' + re + ' in ' + selId + ': ' + [...sel.options].map(o => o.textContent).join(' / ')); sel.value = opt.value; sel.dispatchEvent(new Event('change', { bubbles: true })); await sleep(100); return opt.textContent; };
const fresh = async () => { go(); await settle(); await cardDone(); return cardText(); };
const key = t => { const m = t.match(/Roundness[^%]*%/), w = t.match(/(HOLDS|FAILS)[^.]*(never reverses|mirror-reversed)/g); return (m ? m[0] : '?') + ' | ' + (w ? w.join(' ; ').slice(0, 160) : '?'); };
const type = (id, v) => { const e = $(id); if (!e) fail('no control ' + id); e.value = String(v); e.dispatchEvent(new Event('input', { bubbles: true })); e.dispatchEvent(new Event('change', { bubbles: true })); e.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', bubbles: true })); };
const vis = id => { const e = $(id); if (!e) return false; const r = e.getBoundingClientRect(); return r.width > 0 && r.height > 0; };
const O = window.__o || (window.__o = {});
//@@STEP
// ---- defect 1: the card of Pulled plane after "Jump to a point", a saved point, in the 2D view
const o = O.d1 = {};
await pick('pulledplane');
const full1 = cardText(); o.atMinus1 = key(full1);
o.chosen = await choose('juliaPreset', /rabbit/i); await settle(); await cardDone();
const m1 = cardText(); o.cAfterMenu = S.c.slice(); o.afterMenu = key(m1);
const f1 = await fresh(); o.menu_cardChanged = m1 !== full1; o.menu_sameAsFresh = m1 === f1;
// a real saved point: go to c = (-1, 0, 0) by the menu ("Basilica"), move c along y by its dial, save, jump away, jump back
S.c = [-1, 0, 0]; go(); await settle(); await cardDone();
type('cyNum', 0.3); await settle(); await cardDone();
const atSaved = cardText(); o.cTyped = S.c.slice(); o.typed_sameAsFresh = atSaved === await fresh();
$('juliaName').value = 'ec2 point'; $('juliaSave').click(); await sleep(400);
o.saveNote = txt('juliaSaveNote'); o.listHead = [...$('juliaPreset').options].map(x => x.textContent).slice(0, 4);
await choose('juliaPreset', /rabbit/i); await settle(); await cardDone(); const r2 = cardText();
o.rabbitAgain_same = r2 === m1;
await choose('juliaPreset', /ec2 point/); await settle(); await cardDone();
const sv = cardText(); o.cSaved = S.c.slice(); o.afterSaved = key(sv); o.saved_isCardOfThatC = sv === atSaved; o.saved_differsFromRabbit = sv !== r2; o.saved_sameAsFresh = sv === await fresh();
const del = $('juliaDelete'); if (del && !del.hidden) { del.click(); await sleep(400); o.deleted = ![...$('juliaPreset').options].some(x => /ec2 point/.test(x.textContent)); } else o.deleted = 'no delete button on show';
// the 2D view
S.c = [-1, 0, 0]; S.flat = true; go(); await settle(); await cardDone(); const a2 = cardText();
await choose('juliaPreset', /rabbit/i); await settle(); await cardDone(); const b2 = cardText(); const c2 = await fresh();
o.flatView = { changed: a2 !== b2, sameAsFresh: b2 === c2, sameAs3D: b2 === m1 };
S.flat = false; S.c = [-1, 0, 0]; go(); await settle(); await cardDone();
return JSON.stringify(o);
//@@STEP
// ---- defect 1, more ways c can move: the Examples list, the Learn tab on show, a quick sweep, the mosaic
const o = O.d1b = {};
await pick('pulledplane');
const at1 = cardText();
const ex = $('trapExamples');
o.examples = ex ? [...ex.options].map(x => x.textContent).slice(0, 12) : 'no Examples list';
if (ex) {
  const cs = [];
  for (const opt of [...ex.options].slice(1)) {
    ex.value = opt.value; ex.dispatchEvent(new Event('change', { bubbles: true })); await sleep(150); await settle(); await cardDone();
    const t = cardText(), f = await fresh();
    cs.push(opt.textContent + ': mode ' + S.mode + ', c ' + JSON.stringify(S.c.map(x => +x.toFixed(3))) + ', entry ' + apId() + ', card ' + (t === f ? 'up to date' : 'STALE'));
    if (cs.length >= 6) break;
  }
  o.exampleRuns = cs;
}
$('resetAll') && 0;
await pick('pulledplane');
// a quick sweep of c: 25 values, one per frame, by the dial's own setter path (S.c in place + touch)
for (let i = 0; i < 25; i++) { S.c[1] = 0.02 * i; L.touch(); await sleep(16); }
await settle(); await cardDone(); const sw = cardText(); o.sweep_sameAsFresh = sw === await fresh(); o.sweep_c = S.c.slice();
o.cacheKeysWithC = [...L.cardRun.cache.keys()].filter(k => k.includes(' c=')).length; o.cacheSize = L.cardRun.cache.size;
// the Learn tab on show: are the Julia list and the card on show there, and does the card follow?
S.c = [-1, 0, 0]; go(); await settle(); await cardDone();
$('mode-l').click(); await sleep(500);
o.learn = { on: document.body.classList.contains('is-learn'), cardOnShow: vis('card'), juliaListOnShow: vis('juliaPreset'), approachListOnShow: vis('secApproach'), cDialOnShow: vis('cyNum') };
if (o.learn.juliaListOnShow) { const b = cardText(); await choose('juliaPreset', /rabbit/i); await sleep(900); await cardDone(); o.learn.cardAfterJump = cardText() === b ? 'unchanged (c is ' + JSON.stringify(S.c) + ')' : 'changed'; }
$('mode-j').click(); await sleep(400); await settle(); await cardDone();
const back = cardText(); o.learn.backInJulia_c = S.c.slice(); o.learn.backInJulia_sameAsFresh = back === await fresh();
return JSON.stringify(o);
//@@STEP
// ---- defects 5 and 7b: the card in the Mandelbrot view and the hidden Julia c; what is remembered
const o = O.d5 = {};
await pick('pulledplane');
const jul1 = cardText();
$('mode-m').click(); await sleep(250); await settle(); await cardDone(); const mA = cardText();
S.c = RAB.slice(); go(); await settle(); await cardDone(); const mB = cardText();
S.c = [-0.5, 0.3, 0.4]; L.touch(); await settle(); await cardDone(); const mC = cardText();
o.mandel = key(mA); o.mandel_sameForThreeHiddenC = mA === mB && mB === mC; o.mandel_differsFromJulia = mA !== jul1;
o.mandelSlice = (mA.match(/Slice[^|]{0,400}/) || [''])[0].slice(0, 300);
// is "c = the point" what the page's own orbit rule does in a Mandelbrot orbit? first counted squaring of the orbit of 0 for c = v
{ const R = L.CARRY.pulledplane, q = S.param.pulledplane; let worst = 0;
  for (let k = 1; k <= 2000; k++) { const v = [Math.sin(k * 1.7) * 1.3, Math.sin(k * 2.9) * 1.1, Math.sin(k * 4.3) * 1.1];
    let st = R.start(q); st = R.step(st, [0, 0, 0], v, q); const w0 = R.pw(st, [0, 0, 0], 2); const z1 = [w0[0] + v[0], w0[1] + v[1], w0[2] + v[2]];
    st = R.step(st, z1, v, q); const w = R.pw(st, z1, 2), m = L.MATH.pulledplane(v, 2, q, v);
    worst = Math.max(worst, Math.hypot(w[0] - m[0], w[1] - m[1], w[2] - m[2])); }
  o.mandelRule_vs_orbit = worst; }
// back to Julia by the mode button: the card must be the card of the Julia c now in S.c
$('mode-j').click(); await sleep(250); await settle(); await cardDone(); const j2 = cardText();
o.backToJulia_c = S.c.slice(); o.backToJulia_sameAsFresh = j2 === await fresh(); o.backToJulia_sliceLine = (j2.match(/The plane z = 0[^.]*\./) || ['?'])[0];
// the Julia card against the same thing asked of the rule directly: card at c = RAB reached by typing the dials
S.c = [-1, 0, 0]; go(); await settle(); await cardDone();
type('cxNum', RAB[0]); type('cyNum', RAB[1]); await settle(); await cardDone(); const tj = cardText();
o.typedRabbit = key(tj); o.typedRabbit_c = S.c.slice();
// remembered measurements
o.cache = { withC: [...L.cardRun.cache.keys()].filter(k => k.includes(' c=')), size: L.cardRun.cache.size };
await pick('alongonce'); const a0 = cardText(), n0 = L.cardRun.cache.size;
type('cyNum', 0.37); await settle(); await cardDone(); type('czNum', 0.21); await settle(); await cardDone();
o.alongonce = { cardSame: cardText() === a0, cache: n0 + ' -> ' + L.cardRun.cache.size, keys: [...L.cardRun.cache.keys()].filter(k => k.startsWith('alongonce')) };
// along once in the Mandelbrot view: the same card as in Julia?
$('mode-m').click(); await sleep(250); await settle(); await cardDone(); o.alongonce.mandelSameAsJulia = cardText() === a0;
$('mode-j').click(); await sleep(250); S.c = [-1, 0, 0]; go(); await settle();
return JSON.stringify(o);
//@@STEP
// ---- defect 3: the Stretch sentences, every plan
const o = O.d3 = {};
const ids = L.APPROACHES.map(a => a.id);
const seen = {};
for (const id of ids) for (const n of [2, 3, 4, 7, 2.5, -2, 1, 0.5]) for (const len of [0.8, 1.5, 1, 3]) {
  try {
    const plan = L.learnPlan({ space: 3, id, params: S.param[id], n, c: [-1, 0, 0], abs: [0, 0, 0], flip: [0, 0] });
    let p = [0.48 * len, 0.6 * len, 0.64 * len];
    for (const m of plan.moves) { const b = m.at(p, 1); if (/Stretch/.test(m.name || '')) { const s = String(m.say(p, b)); const tpl = s.replace(/−?\d[\d,.]*(e[+-]?\d+)?/g, '#'); (seen[tpl] = seen[tpl] || []).push(id + ' n=' + n + ' len=' + len + ': ' + s); } p = b; }
  } catch (e) { (seen['FAILED ' + e.message] = seen['FAILED ' + e.message] || []).push(id + ' n=' + n + ' len=' + len); }
}
o.templates = Object.fromEntries(Object.entries(seen).map(([k, v]) => [k, { count: v.length, first: v[0], ids: [...new Set(v.map(s => s.split(' ')[0]))].join(' ') }]));
// spaces 2 and 1 (the flat moves) at power 2
for (const sp of [2, 1]) { const plan = L.learnPlan({ space: sp, id: 'pulledplane', params: S.param.pulledplane, n: 2, c: [-1, 0, 0] }); let p = [0.6, sp > 1 ? 0.5 : 0, 0]; const says = []; for (const m of plan.moves) { const b = m.at(p, 1); says.push((m.name || '?') + ': ' + m.say(p, b)); p = b; } o['space' + sp] = says; }
return JSON.stringify(o);
//@@STEP
// ---- defect 4: Learn, "Next step": the orbit on show against the entry's own (page's CARRY here; the library in python)
const o = O.d4 = {};
const own = (id, z0, c, steps, q, n, ab) => { const R = L.CARRY[id]; let st = R.start(q), z = z0.slice(); const tr = [z.slice()]; for (let k = 0; k < steps; k++) { const m = ab ? z.map(Math.abs) : z; st = R.step(st, m, c, q); const w = R.pw(st, m, n); z = [w[0] + c[0], w[1] + c[1], w[2] + c[2]]; tr.push(z.slice()); } return tr; };
const far = (a, b) => Math.max(...a.map((v, i) => Math.hypot(v[0] - b[i][0], v[1] - b[i][1], v[2] - b[i][2])));
const runs = [
  ['alongonce', [0.5, -0.4, 0.3], [-0.8, 0.1, 0.2], 2, null, 0],
  ['pulledplane', [0.5, -0.4, 0.3], [-0.8, 0.1, 0.2], 2, null, 0],
  ['alongonce', [0, 0, 0], [-0.9, 0.2, 0.15], 2, null, 0],
  ['pulledplane', [0, 0, 0], [-0.9, 0.2, 0.15], 2, null, 0],
  ['pulledplane', [0.3, 0.5, -0.2], [-1, 0, 0], 2, { hold: 0.6, ease: 0.1, cpull: 40 }, 0],
  ['pulledplane', [0.3, 0.5, -0.2], [-0.2, 0.3, 0.3], 3, null, 0],
  ['alongonce', [0.3, 0.5, -0.2], [-0.2, 0.3, 0.3], 3, null, 0],
  ['alongonce', [0.9, 0.5, -0.6], [0.1, 0.2, 0.3], -2, null, 0],
  ['pulledplane', [0.9, 0.5, -0.6], [0.1, 0.2, 0.3], -2, null, 0],
];
o.runs = [];
for (const [id, z0, c, n, dials, ab] of runs) {
  $('mode-j').click(); await sleep(200); $('ap-' + id).click(); await sleep(250); S.n = n; S.eq = 'z^n + c'; S.abs = [0, 0, 0]; S.flip = [0, 0];
  if (id === 'pulledplane') Object.assign(S.param.pulledplane, dials || { hold: 0.05, ease: 0.7, cpull: 16 });
  go(); await sleep(120);
  $('mode-l').click(); await sleep(400); $('learnSpace3').click(); await sleep(250);
  L.learn.set({ z: z0, c });
  const names0 = L.learn.cache.names.slice(), say0 = L.learn.cache.say.slice();
  for (let k = 0; k < 6; k++) { $('learnNext').click(); await sleep(110); }
  const st = L.learn.state(), want = own(id, z0, c, st.orbit.length - 1, S.param[id], n, ab);
  const end = st.end, nxt = own(id, z0, c, st.orbit.length, S.param[id], n, ab).pop();
  // step back by the page's own control, then forward again: the same orbit?
  let backOk = 'no learnBack';
  o.runs.push({ id, z0, c, n, dials, steps: st.orbit.length - 1, k: L.learn.k, offOwn: far(st.orbit, want), endOffNext: Math.hypot(end[0] - nxt[0], end[1] - nxt[1], end[2] - nxt[2]), orbit: st.orbit, fault: L.learn.cache.fault || '', names0, say0, sayLast: L.learn.cache.say.slice(), bad: /undefined|NaN/.test(L.learn.cache.say.join(' ') + st.note) });
  $('learnAgain').click(); await sleep(150);
}
o.note = L.learn.state().note;
// spaces 2 and 1 for both entries: the flat rule, at every step
o.flat = [];
for (const id of ['alongonce', 'pulledplane']) for (const sp of [2, 1]) {
  $('mode-j').click(); await sleep(200); $('ap-' + id).click(); await sleep(250); S.n = 2; if (id === 'pulledplane') Object.assign(S.param.pulledplane, { hold: 0.05, ease: 0.7, cpull: 16 }); go(); await sleep(120);
  $('mode-l').click(); await sleep(400); $('learnSpace' + sp).click(); await sleep(250);
  const z0 = sp === 2 ? [0.3, 0.4, 0] : [0.5, 0, 0], c = sp === 2 ? [-0.5, 0.3, 0] : [-0.9, 0, 0];
  L.learn.set({ z: z0, c });
  for (let k = 0; k < 4; k++) { $('learnNext').click(); await sleep(110); }
  const st = L.learn.state(); let z = z0.slice(), worst = 0;
  for (let k = 1; k < st.orbit.length; k++) { z = [z[0] * z[0] - z[1] * z[1] + c[0], 2 * z[0] * z[1] + c[1], 0]; worst = Math.max(worst, Math.hypot(st.orbit[k][0] - z[0], st.orbit[k][1] - z[1], st.orbit[k][2])); }
  o.flat.push(id + ' space ' + sp + ': ' + (st.orbit.length - 1) + ' steps, off the flat orbit by ' + worst.toExponential(1));
  $('learnAgain').click(); await sleep(150);
}
$('learnSpace3').click(); await sleep(200); $('mode-j').click(); await sleep(300); S.n = 2; go(); await settle();
return JSON.stringify(o);
//@@STEP
// ---- defects 2, 6, 7a, 7c: every sentence of the two entries as the page shows it
const o = O.texts = {};
for (const id of ['alongonce', 'pulledplane']) {
  await pick(id);
  const a = L.APPROACHES[S.approach], q = S.param[a.id], box = $('apAbout'), btn = $('apAboutBtn');
  if (box.hidden) { btn.click(); await sleep(200); }
  const t = o[id] = { name: a.name, tag: a.tag, aboutBox: box.innerText, section: $('secApproach').innerText, card: cardText() };
  for (const n of [2, 3, 2.5, -2]) t['power ' + n] = { formula: a.formula(q, n), round: a.roundNote(q, n), crush: a.crush(q, n), smooth: a.smooth(q, n), sliceYes: a.slice(true, q, n), sliceNo: a.slice(false, q, n) };
  t.dials = (a.params || []).filter(p => p.type === 'dial').map(p => ({ key: p.key, label: p.label, help: p.help }));
  t.labelsOnPage = [...document.querySelectorAll('#pd-' + id + ' label, #pd-' + id + ' .dial-label, #pd-' + id + ' legend')].map(e => e.textContent.trim()).filter(Boolean).slice(0, 12);
  btn.click(); await sleep(100);
}
const P = S.param.pulledplane, ap2 = L.APPROACHES.find(a => a.id === 'pulledplane');
o.smooth = {};
for (const [h, n] of [[0.05, 2], [0.05, 3], [0.2, 2], [0, 2], [0.05, 2.5], [0.0500001, 2]]) o.smooth['hold ' + h + ' n ' + n] = ap2.smooth({ ...P, hold: h }, n)[1];
const all = document.body.innerText;
o.coined = ['Ease of a pull', 'easing', 'sheet lag', 'psi', 'ψ', 'evc', 'c_wake', 'wake'].map(w => w + ': ' + (all.includes(w) ? 'ON THE PAGE' : 'not on the page'));
o.newLabel = all.includes('How little a thing near the page turns it');
return JSON.stringify(o);

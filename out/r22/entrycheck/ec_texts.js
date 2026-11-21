// Round 22, entrycheck: every sentence a user sees for the two entries, the card after c changes, and the Learn tab.
// (HEAD of drive.py is in front.)
const out = { texts: {}, card: {}, learn: {}, stretch: {} };
const RAB = [-0.122561, 0.744862, 0];
const cardText = () => ($('card') ? $('card').innerText.replace(/\s+/g, ' ').trim() : '(no card)');
const pick = async id => { $('mode-j').click(); await sleep(150); $('ap-' + id).click(); await sleep(250); if (apId() !== id) fail('could not choose ' + id); S.eq = 'z^n + c'; S.z0 = '0'; S.n = 2; S.iter = 30; S.c = [-1, 0, 0]; S.flat = false; S.cutOn = false; S.mosaic = false; L.resetCam(); go(); await settle(); };
for (const id of ['alongonce', 'pulledplane']) {
  await pick(id);
  const a = L.APPROACHES[S.approach], q = S.param[a.id], box = $('apAbout'), btn = $('apAboutBtn');
  if (box.hidden) { btn.click(); await sleep(200); }
  const t = out.texts[id] = { name: a.name, menu: $('apMenuName').textContent, aboutBox: box.innerText, section: $('secApproach').innerText, card: cardText() };
  for (const n of [2, 3, 2.5, -2, 1, 0]) t['power ' + n] = { formula: a.formula(q, n), round: a.roundNote(q, n), crush: a.crush(q, n), smooth: a.smooth(q, n), sliceYes: a.slice(true, q, n), sliceNo: a.slice(false, q, n) };
  t.dials = (a.params || []).filter(p => p.type === 'dial').map(p => ({ key: p.key, label: p.label, min: p.min, max: p.max, def: p.def, help: p.help }));
  btn.click(); await sleep(100);
}
// ----- the card of Pulled plane when c changes by other ways than the c dials
await pick('pulledplane');
out.card.atMinus1 = cardText();
const rab = L.JULIA_PRESETS.find(p => p.c && Math.abs(p.c[0] + 0.122561) < 1e-3 && Math.abs(p.c[1] - 0.744862) < 1e-3) || L.JULIA_PRESETS.find(p => p.c && Math.abs(p.c[1]) > 0.3);
out.card.preset = rab ? rab.name + ' ' + JSON.stringify(rab.c) : null;
if (rab) {
  L.applyJuliaPreset(rab); await settle(); await sleep(600);
  out.card.afterPreset = cardText();
  go(); await settle(); await sleep(600);
  out.card.afterPresetAndRefresh = cardText();
}
// the same through the menu itself
S.c = [-1, 0, 0]; go(); await settle(); await sleep(400);
const sel = $('juliaPreset');
out.card.select = sel ? [...sel.options].map(o => o.value + '=' + o.textContent).slice(0, 12) : null;
if (sel) {
  const opt = [...sel.options].find(o => /abbit/.test(o.textContent));
  if (opt) { sel.value = opt.value; sel.dispatchEvent(new Event('change', { bubbles: true })); await settle(); await sleep(600);
    out.card.afterMenu = cardText(); out.card.cAfterMenu = S.c.slice();
    go(); await settle(); await sleep(600); out.card.afterMenuAndRefresh = cardText(); }
}
// a c dial (the builder's fix)
S.c = [-1, 0, 0]; go(); await settle(); await sleep(400);
out.card.backAtMinus1 = cardText();
// Mandelbrot view: which c does the card use?
$('mode-m').click(); await sleep(200); await settle(); await sleep(400);
out.card.mandel = cardText();
S.c = RAB.slice(); go(); await settle(); await sleep(400);
out.card.mandelOtherHiddenC = cardText();
$('mode-j').click(); await sleep(200); S.c = [-1, 0, 0]; go(); await settle();
// ----- Learn: the words, and where "Next step" puts the point against the entry's own orbit
for (const id of ['alongonce', 'pulledplane', 'turnalong', 'mercator']) {
  await pick(id);
  $('mode-l').click(); await sleep(400);
  if (!document.body.classList.contains('is-learn')) fail('Learn did not switch on');
  $('learnSpace3').click(); await sleep(400);
  const o = out.learn[id] = {};
  o.note = $('learnNote') ? $('learnNote').innerText : null;
  o.panel = [...document.querySelectorAll('#learnPanel')].map(e => e.innerText).join(' ').replace(/\s+/g, ' ').slice(0, 1500);
  $('learnFwd').click(); await sleep(200);
  const K0 = L.learn.cache; o.names = K0 && K0.names; o.say0 = K0 && K0.say;
  o.z0 = L.learn.pts ? L.learn.pts[3].z.slice() : null; o.c = L.learn.pts ? L.learn.pts[3].c.slice() : null;
  $('learnNext').click(); await sleep(400);
  const K1 = L.learn.cache; o.k = L.learn.k; o.say1 = K1 && K1.say;
  o.keys = K1 ? Object.keys(K1) : null;
  o.orbit = K1 && K1.orbit ? K1.orbit : null;
  o.pts1 = K1 && K1.pts ? K1.pts : null;
  $('learnNext').click(); await sleep(400);
  const K2 = L.learn.cache; o.pts2 = K2 && K2.pts ? K2.pts : null; o.orbit2 = K2 && K2.orbit ? K2.orbit : null;
  // the entry's own orbit from the same start, by the page's rule
  if (L.CARRY[id] && o.z0 && o.c) {
    const R = L.CARRY[id], q = S.param[id] || {}; let st = R.start(q), z = o.z0.slice(); const tr = [z.slice()];
    for (let k = 0; k < 3; k++) { st = R.step(st, z, o.c, q); const w = R.pw(st, z, 2); z = [w[0] + o.c[0], w[1] + o.c[1], w[2] + o.c[2]]; tr.push(z.slice()); }
    o.own = tr;
  }
  $('learnAgain').click(); await sleep(200);
  $('mode-j').click(); await sleep(300);
}
// ----- the Stretch sentence at a few powers, for an entry with the generic moves
if (typeof L.learnPlan === 'function') {
  for (const id of ['turnalong', 'windsq', 'alongonce', 'pulledplane', 'mercator', 'lathe', 'pillow']) {
    if (!L.APPROACHES.find(a => a.id === id)) continue;
    for (const n of [2, 3, 5, 2.5, -2, 1]) for (const len of [0.8, 1.5, 2, 1]) {
      try {
        const plan = L.learnPlan({ space: 3, id, params: S.param[id], n, c: [-1, 0, 0], abs: [0, 0, 0], flip: [0, 0] });
        let p = [0.48 * len, 0.6 * len, 0.64 * len]; const says = [];
        for (const m of plan.moves) { const b = m.at(p, 1); says.push((m.name || '?') + ': ' + m.say(p, b)); p = b; }
        out.stretch[id + ' n=' + n + ' len=' + len] = says.filter(s => /^Stretch/.test(s)).join(' | ') || says.join(' | ');
        if (n === 2 && len === 0.8) out.stretch[id + ' note'] = plan.note;
      } catch (e) { out.stretch[id + ' n=' + n + ' len=' + len] = 'FAILED: ' + e.message; }
    }
  }
}
return JSON.stringify(out);

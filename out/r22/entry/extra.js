// Round 22, entry, second pass: the changed Learn code off the beaten track. (HEAD of run.py is in front of this.)
//   python out/r22/entry/run.py js out/r22/entry/extra.js extra.log
// 1. Learn's orbit against the entry's own orbit at the powers 3 and -2, and for Pulled plane with its dials moved.
// 2. Learn on a page and on a line (space 2, 1) for the two entries: the flat rule, no fault, Next step works.
// 3. The card in the Kleinian view and back; entries switched in the Mandelbrot view.
const far = (a, b) => Math.max(...a.map((v, i) => Math.hypot(v[0] - b[i][0], v[1] - b[i][1], v[2] - b[i][2])));
const own = (id, z0, c, steps, q, n) => { const R = L.CARRY[id]; let st = R.start(q), z = z0.slice(); const o = [z.slice()]; for (let k = 0; k < steps; k++) { st = R.step(st, z, c, q); const w = R.pw(st, z, n); z = [w[0] + c[0], w[1] + c[1], w[2] + c[2]]; o.push(z.slice()); } return o; };
const out = [];
const learnOn = async sp => { $('mode-l').click(); await sleep(400); if (!document.body.classList.contains('is-learn')) fail('Learn did not switch on'); $('learnSpace' + sp).click(); await sleep(300); };
const learnOff = async () => { $('learnAgain').click(); await sleep(150); $('mode-j').click(); await sleep(250); };
for (const [id, n, q] of [['alongonce', 3, null], ['alongonce', -2, null], ['pulledplane', 3, null], ['pulledplane', 2, { hold: 0.2, ease: 0.4, cpull: 5 }], ['pulledplane', 2, { hold: 0, ease: 1, cpull: 0 }]]) {
  $('mode-j').click(); await sleep(200); $('ap-' + id).click(); await sleep(250);
  S.eq = 'z^n + c'; S.z0 = '0'; S.n = n; S.abs = [0, 0, 0]; S.flip = [0, 0];
  const keep = q ? { ...S.param[id] } : null; if (q) Object.assign(S.param[id], q);
  go(); await sleep(150); await learnOn(3);
  const Z0 = [0.5, 0.35, -0.3], C = [-0.2, 0.15, 0.1];
  L.learn.set({ z: Z0, c: C });
  for (let k = 0; k < 3; k++) { $('learnNext').click(); await sleep(120); }
  const st = L.learn.state(), want = own(id, Z0, C, st.orbit.length - 1, S.param[id], n), d = far(st.orbit, want);
  if (st.orbit.length < 2) fail(id + ' power ' + n + ': Next step did not go on');
  if (!(d < 1e-9)) fail(id + ' power ' + n + ' ' + JSON.stringify(q) + ': Learn is ' + d.toExponential(2) + ' off the own orbit');
  if (L.learn.cache.fault || /undefined|NaN/.test(L.learn.cache.say.join(' ') + st.note + st.sentence)) fail(id + ' power ' + n + ': ' + L.learn.cache.fault + ' ' + L.learn.cache.say.join(' '));
  out.push(id + ' power ' + n + (q ? ' dials ' + JSON.stringify(q) : '') + ': ' + (st.orbit.length - 1) + ' steps, off by ' + d.toExponential(1) + ', Stretch: ' + (L.learn.cache.say.find(s => /ength/.test(s)) || '').slice(0, 110));
  await learnOff();
  if (keep) Object.assign(S.param[id], keep);
  S.n = 2; go(); await sleep(100);
}
// 2. a page and a line
for (const id of ['alongonce', 'pulledplane']) for (const sp of [2, 1]) {
  $('mode-j').click(); await sleep(200); $('ap-' + id).click(); await sleep(250); S.n = 2; go(); await sleep(100); await learnOn(sp);
  L.learn.set({ z: [0.5, 0.4, 0], c: [-0.3, 0.2, 0] });
  for (let k = 0; k < 3; k++) { $('learnNext').click(); await sleep(120); }
  const st = L.learn.state();
  let z = sp === 1 ? [0.5, 0, 0] : [0.5, 0.4, 0]; const c = sp === 1 ? [-0.3, 0, 0] : [-0.3, 0.2, 0], o = [z.slice()];
  for (let k = 0; k < st.orbit.length - 1; k++) { z = [z[0] * z[0] - z[1] * z[1] + c[0], 2 * z[0] * z[1] + c[1], 0]; o.push(z.slice()); }
  const d = far(st.orbit, o);
  if (st.orbit.length < 3 || !(d < 1e-9) || L.learn.cache.fault) fail(id + ' in space ' + sp + ': ' + st.orbit.length + ' points, off the flat rule by ' + d + ' ' + L.learn.cache.fault);
  out.push(id + ' on a ' + (sp === 2 ? 'page' : 'line') + ': ' + (st.orbit.length - 1) + ' steps of the flat rule, off by ' + d.toExponential(1));
  await learnOff();
}
// 3. the card through the Kleinian view and back, and entries switched in the Mandelbrot view
const cardText = () => $('card').innerText.replace(/\s+/g, ' ');
const cardIdle = async () => { await settle(); await sleep(500); for (let i = 0; i < 600 && ($('card').getAttribute('aria-busy') || !L.idle()); i++) await sleep(20); if ($('card').getAttribute('aria-busy')) fail('the card never finished'); };
$('mode-j').click(); await sleep(200); $('ap-pulledplane').click(); await sleep(250); S.c = [-1, 0, 0]; go(); await cardIdle();
const j1 = cardText();
$('mode-k').click(); await sleep(300); await settle(); $('mode-j').click(); await sleep(300); await cardIdle();
if (cardText() !== j1) fail('the card changed through the Kleinian view');
$('mode-m').click(); await sleep(300); await cardIdle(); const m1 = cardText();
$('ap-mercator').click(); await sleep(250); await cardIdle(); const mm = cardText();
$('ap-pulledplane').click(); await sleep(250); await cardIdle();
if (cardText() !== m1 || mm === m1) fail('the Mandelbrot card of Pulled plane is not the same after another entry was chosen and left');
$('mode-j').click(); await sleep(300); await cardIdle();
if (cardText() !== j1) fail('back in the Julia view the card is not the Julia card');
out.push('card: the same through the Kleinian view and back, and after another entry in the Mandelbrot view');
$('resetAll').click(); await sleep(300);
return out.join('; ');

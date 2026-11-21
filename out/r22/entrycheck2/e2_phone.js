// Round 22, entrycheck second pass: a phone-sized window (390 x 844).
const cardDone = async () => { await sleep(350); for (let i = 0; i < 800 && !L.cardIdle(); i++) await sleep(25); await sleep(150); };
const wide = () => { const W = document.documentElement.clientWidth; const over = [...document.querySelectorAll('body *')].filter(e => { const r = e.getBoundingClientRect(); return r.width > 0 && r.right > W + 1 && getComputedStyle(e).position !== 'fixed'; }).slice(0, 5).map(e => e.tagName + '#' + e.id + '.' + String(e.className).slice(0, 30) + ' right ' + Math.round(e.getBoundingClientRect().right)); return 'window ' + W + ', page scroll width ' + document.documentElement.scrollWidth + ', wider than the window: ' + (over.length ? over.join(' ; ') : 'nothing'); };
//@@STEP
const o = [];
for (const id of ['alongonce', 'pulledplane']) {
  $('mode-j').click(); await sleep(150); $('ap-' + id).click(); await sleep(250); if (apId() !== id) fail('could not choose ' + id);
  S.eq = 'z^n + c'; S.z0 = '0'; S.n = 2; S.iter = 30; S.c = [-1, 0, 0]; L.resetCam(); go(); await settle(); await cardDone();
  o.push(id + ': ' + grid()[0] + ' probes; ' + wide());
  if (id === 'pulledplane') {
    const labs = [...document.querySelectorAll('#pd-pulledplane label')].map(e => { const r = e.getBoundingClientRect(); return e.textContent.trim().slice(0, 44) + ' [' + Math.round(r.width) + ' x ' + Math.round(r.height) + ']'; });
    o.push('dial labels: ' + labs.join(' | '));
    const sel = $('juliaPreset'), opt = [...sel.options].find(x => /rabbit/i.test(x.textContent)); const before = $('card').innerText;
    sel.value = opt.value; sel.dispatchEvent(new Event('change', { bubbles: true })); await settle(); await cardDone();
    o.push('jump to the rabbit: card changed ' + ($('card').innerText !== before));
    S.c = [-1, 0, 0]; go(); await settle();
  }
  $('mode-l').click(); await sleep(500); $('learnSpace3').click(); await sleep(300);
  L.learn.set({ z: [0.6, 0.3, 0.4], c: [-0.3, 0.2, 0.1] });
  for (let k = 0; k < 2; k++) { $('learnNext').click(); await sleep(150); }
  const st = L.learn.state();
  o.push(id + ' Learn: ' + (st.orbit.length - 1) + ' steps, second point ' + st.orbit[2].map(x => x.toFixed(2)).join(', ') + ', fault "' + (L.learn.cache.fault || '') + '"; ' + wide());
  $('learnAgain').click(); await sleep(150); $('mode-j').click(); await sleep(300); await settle();
}
$('ap-pulledplane').click(); await sleep(250); go(); await settle();
const d = $('pd-pulledplane'); if (d) d.scrollIntoView({ block: 'start' }); await sleep(300);
return JSON.stringify(o);

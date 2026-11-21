// Round 12, tried rules: each new entry under every equation preset, at other powers, in the Kleinian view and
// with the Julia mosaic. Follows tests/approaches-page.json. Low quality: this is a compile-and-draw check.
const L = window.squaringLab, S = L.S, sleep = ms => new Promise(r => setTimeout(r, ms)), $ = id => document.getElementById(id);
const ids = ['softfold', 'axisbulb', 'pillow'];
const settle = async () => { await sleep(80); for (let i = 0; i < 1200 && !L.idle(); i++) await sleep(50); return L.idle(); };
L.R.warmOn = false; S.q.aa = 1; S.q.res = 0.25; S.q.shadow = false; S.q.ao = false;
window.__t = { done: false, text: '' };
(async () => {
  const sel = $('eqPreset'), bad = [], seen = [];
  let count = 0;
  const ok = async label => { const fine = await settle(); count++; if (!fine || !$('glfail').hidden || !$('eqErr').hidden || L.R.failed) bad.push(label + (L.R.failed ? ' (' + L.R.failed + ')' : '')); };
  for (const id of ids) {
    $('mode-m').click(); $('ap-' + id).click();
    for (let i = 0; i < sel.options.length; i++) {
      if (+sel.options[i].value < 0) continue;
      sel.value = sel.options[i].value; sel.dispatchEvent(new Event('change'));
      await ok(id + ' / ' + sel.options[i].text);
      if (id === ids[0]) seen.push(sel.options[i].text);
    }
    sel.value = sel.options[[...sel.options].findIndex(o => +o.value >= 0)].value; sel.dispatchEvent(new Event('change')); await settle();
    for (const n of [3, 8, -1, 2.5]) { S.n = n; L.syncControls(); L.refresh(false); L.touch(); await ok(id + ' / power ' + n); }
    S.n = 2; L.syncControls(); L.refresh(false); L.touch(); await settle();
    $('mode-j').click(); await ok(id + ' / Julia');
    $('mode-k').click(); await ok(id + ' / Kleinian');
    $('mode-m').click(); await settle();
    S.flat = true; L.syncControls(); L.refresh(false); L.touch(); await ok(id + ' / 2D view');
    S.flat = false; L.syncControls(); L.refresh(false); L.touch(); await settle();
  }
  window.__t.text = count + ' drawings, ' + bad.length + ' failed' + (bad.length ? ': ' + bad.join('; ') : '') + '. Equation presets: ' + seen.join(' | ');
  window.__t.done = true;
})();
return 'drawing';

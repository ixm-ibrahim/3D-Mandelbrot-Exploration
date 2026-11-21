// Round 16, entry: the words of the two entries at several powers (no exception, no "undefined"), and what the
// page's own scorecard shows for them at power 2 and 3.
const L = window.squaringLab, S = L.S, $ = id => document.getElementById(id);
const sleep = ms => new Promise(r => setTimeout(r, ms));
const idle = async () => { const t0 = performance.now(); await sleep(200); while (!L.idle() && performance.now() - t0 < 240000) await sleep(150); return L.idle(); };
const out = [];
for (const id of ['turnaway', 'turnalong']) {
  const a = L.APPROACHES.find(x => x.id === id);
  out.push('===== ' + id + ' | ' + a.name + ' | group ' + a.group + ' | place in the list ' + L.APPROACHES.indexOf(a) + ' of ' + L.APPROACHES.length);
  out.push('tag: ' + a.tag);
  out.push('note: ' + a.params[0].text);
  out.push('about: ' + a.about);
  for (const n of [2, 3, 4, 2.5, 1, 0, -1, -2]) {
    const parts = [a.formula({}, n), a.slice(true, {}, n), a.slice(false, {}, n), a.crush({}, n).join(' | '), a.smooth({}, n).join(' | '), a.roundNote({}, n)];
    const bad = parts.filter(t => typeof t !== 'string' || /undefined|NaN|TEXT PENDING|—/.test(t)).length;
    out.push('--- n = ' + n + (bad ? '   BAD PARTS: ' + bad : '') + '\nformula: ' + parts[0] + '\nslice (ok): ' + parts[1] + '\ncrush: ' + parts[3] + '\nsmooth: ' + parts[4]);
  }
  $('ap-' + id).click(); await sleep(200); $('mode-m').click();
  for (const n of [2, 3]) {
    S.n = n; S.flat = false; L.syncControls(); L.refresh(false); L.touch(); await idle(); await sleep(300); await idle();
    out.push('--- the page\'s scorecard at n = ' + n + '\n' + $('card').innerText.replace(/\n{2,}/g, '\n'));
  }
  S.n = 2; L.syncControls(); L.refresh(false); L.touch(); await idle();
}
return out.join('\n');

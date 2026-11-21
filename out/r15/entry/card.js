// Round 15, entry: what the page's own scorecard measures for the Square pillow, at the powers 2 to 5.
const L = window.squaringLab, S = L.S, $ = id => document.getElementById(id);
const sleep = ms => new Promise(r => setTimeout(r, ms));
const idle = async () => { const t0 = performance.now(); await sleep(200); while (!L.idle() && performance.now() - t0 < 240000) await sleep(150); return L.idle(); };
const out = [];
$('ap-sqpillow').click(); await sleep(200); $('mode-m').click();
for (const n of [2, 3, 4, 5]) {
  S.n = n; S.flat = false; L.syncControls(); L.refresh(false); L.touch(); await idle(); await sleep(300); await idle();
  out.push('--- n = ' + n + '\n' + $('card').innerText.replace(/\n{2,}/g, '\n'));
}
S.n = 2;
return out.join('\n');

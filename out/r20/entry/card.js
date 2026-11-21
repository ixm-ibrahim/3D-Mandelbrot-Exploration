// Round 20, entry: the words of the entry at several powers (no exception, no "undefined"), the page's own
// scorecard for it in JULIA mode at power 2 and 3, and what the menu shows. No Mandelbrot picture is drawn.
const L = window.squaringLab, S = L.S, $ = id => document.getElementById(id);
const sleep = ms => new Promise(r => setTimeout(r, ms));
const idle = async () => { const t0 = performance.now(); await sleep(200); while (!L.idle() && performance.now() - t0 < 240000) await sleep(150); return L.idle(); };
const out = [];
const id = 'windsq', a = L.APPROACHES.find(x => x.id === id);
out.push('===== ' + id + ' | ' + a.name + ' | group ' + a.group + ' | place in the list ' + L.APPROACHES.indexOf(a) + ' of ' + L.APPROACHES.length + ' | deMax ' + a.deMax + ' | dials ' + a.params.filter(p => p.type === 'dial').length);
out.push('tag: ' + a.tag);
out.push('note: ' + a.params[0].text);
out.push('about: ' + a.about);
let badAll = 0;
for (const n of [2, 3, 4, 5, 2.5, 1, 0.7, 0, -1, -2, -3]) {
  const parts = [a.formula({}, n), a.slice(true, {}, n), a.slice(false, {}, n), a.crush({}, n).join(' | '), a.smooth({}, n).join(' | '), a.roundNote({}, n)];
  const bad = parts.filter(t => typeof t !== 'string' || /undefined|NaN|TEXT PENDING|WS_|—/.test(t)).length; badAll += bad;
  out.push('--- n = ' + n + (bad ? '   BAD PARTS: ' + bad : '') + '\nformula: ' + parts[0] + '\nslice (ok): ' + parts[1] + '\ncrush: ' + parts[3] + '\nsmooth: ' + parts[4] + '\nround: ' + parts[5]);
}
for (const t of [a.tag, a.params[0].text, a.about]) if (/undefined|NaN|TEXT PENDING|WS_|—/.test(t)) badAll++;
out.push('BAD PARTS IN ALL: ' + badAll);
$('mode-j').click(); await sleep(150);
$('ap-' + id).click(); await sleep(250);
S.c = [-1, 0, 0]; S.iter = 40;
for (const n of [2, 3]) {
  S.n = n; S.flat = false; L.syncControls(); L.refresh(false); L.touch(); await idle(); await sleep(300); await idle();
  out.push('--- the page\'s scorecard at n = ' + n + ' (Julia mode, c = -1)\n' + $('card').innerText.replace(/\n{2,}/g, '\n'));
}
S.n = 2; L.syncControls(); L.refresh(false); L.touch(); await idle();
out.push('--- under the menu: ' + ($('apMenuName') ? $('apMenuName').textContent : '?'));
const heads = [...document.querySelectorAll('#rules .rule')].map(r => r.getAttribute('data-ap'));
out.push('--- order of the list: ' + heads.join(' '));
$('ap-mercator').click(); await sleep(250); S.iter = 14; L.syncControls(); L.refresh(false); L.touch(); await idle();
return out.join('\n');

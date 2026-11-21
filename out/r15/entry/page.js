// Round 15, entry: the new entry on the page itself. Texts for many powers (no exception, no leftover word, no long
// dash), the formula line and the scorecard as shown, the place in the menu, and that the old entries kept their places.
const L = window.squaringLab, S = L.S, $ = id => document.getElementById(id);
const sleep = ms => new Promise(r => setTimeout(r, ms));
const idle = async () => { const t0 = performance.now(); await sleep(150); while (!L.idle() && performance.now() - t0 < 240000) await sleep(150); return L.idle(); };
const out = { groups: L.APPROACH_GROUPS.map(g => g.id + ': ' + g.title), order: L.APPROACHES.map(a => a.id).join(' '), problems: [] };
const id = 'sqpillow', a = L.APPROACHES.find(x => x.id === id), row = { id, name: a.name, group: a.group, index: L.APPROACHES.indexOf(a) };
let texts = 0; const all = [];
const seen = t => { texts++; all.push(t); if (typeof t !== 'string' || !t || /to come|PROVISIONAL|undefined|NaN|\u2014|\u2013/.test(t)) out.problems.push('bad text: ' + String(t).slice(0, 120)); };
[a.name, a.tag, a.about].forEach(seen);
(a.params || []).forEach(s => { if (s.text !== undefined) seen(s.text); });
row.byPower = {};
for (const n of [2, 3, 4, 5, 6, 8, 1, 0, -1, -2, -3, 2.5, 0.5, -1.5]) {
  try {
    const f = a.formula({}, n), r = a.roundNote({}, n), c = a.crush({}, n), s = a.smooth({}, n), y = a.slice(true, {}, n), x = a.slice(false, {}, n);
    [f, r, c[1], s[1], y, x].forEach(seen);
    if (!['ok', 'part', 'no'].includes(c[0]) || !['ok', 'part', 'no'].includes(s[0])) out.problems.push('bad pill at ' + n);
    const v = L.MATH[id]([0.3, -0.4, 0.5], n, {}), z = L.MATH[id]([0, 0, 0], n, {}), p = L.MATH[id]([0.3, -0.4, 0], n, {});
    if (!v.every(Number.isFinite) || !z.every(Number.isFinite)) out.problems.push('not finite at n = ' + n);
    row.byPower[n] = { formula: f, slice: y, zOfAPlanePoint: p[2] };
  } catch (e) { out.problems.push('n ' + n + ': ' + e.message); }
}
row.textsRead = texts;
row.tag = a.tag; row.note = a.params[0].text; row.about = a.about;
$('ap-' + id).click(); await sleep(200); $('mode-m').click(); S.n = 2; S.flat = false; L.syncControls(); L.refresh(false); L.touch();
row.drawn = await idle(); row.failed = String(L.R.failed);
row.card = $('card').innerText.replace(/\n{2,}/g, '\n');
// the menu: headings in order, and the entries under each
row.menu = [...document.querySelectorAll('.rule-group')].map(b => { const h = b.querySelector('.rule-group-head'); return (h ? h.textContent : '(no heading)') + ': ' + [...b.querySelectorAll('[id^="ap-"]')].map(e => e.id.slice(3)).filter(x => L.APPROACHES.some(q => q.id === x)).join(', '); });
for (const n of [2.5, 7, -2, 3]) { S.n = n; L.syncControls(); L.refresh(false); L.touch(); await idle(); await sleep(250); await idle(); row['sliceCellAt' + n] = [...$('card').innerText.split('\n')].slice(-1)[0]; }
S.n = 2; L.syncControls(); L.refresh(false); L.touch(); await idle();
out.row = row;
return JSON.stringify(out, null, 1);

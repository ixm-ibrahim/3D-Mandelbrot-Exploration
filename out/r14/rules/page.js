// Round 14, rules: every new entry on the page itself. Texts for many powers and dial settings (no exception, no
// leftover word, no long dash), the formula line and the scorecard as shown, and the Learn tab opening under it.
const L = window.squaringLab, S = L.S, $ = id => document.getElementById(id);
const sleep = ms => new Promise(r => setTimeout(r, ms));
const idle = async () => { const t0 = performance.now(); await sleep(150); while (!L.idle() && performance.now() - t0 < 240000) await sleep(150); return L.idle(); };
const out = { entries: [], groups: L.APPROACH_GROUPS.map(g => g.id + ': ' + g.title), order: L.APPROACHES.map(a => a.id).join(' '), problems: [] };
const VAR = { quat4: [{ w: 0, tilt: 0, cw: 0 }, { w: 0.3, tilt: 0, cw: 0 }, { w: 0, tilt: 40, cw: 0.2 }], rotor: [{ lon: 0, lat: 90 }, { lon: 0, lat: 0 }, { lon: 40, lat: 0 }, { lon: 180, lat: 0 }, { lon: 20, lat: 35 }], rotorframe: [{}], kleinsq: [{}], kleinsq2: [{}] };
for (const id of ['quat4', 'rotor', 'rotorframe', 'kleinsq', 'kleinsq2']) {
  const a = L.APPROACHES.find(x => x.id === id), row = { id, name: a.name, group: a.group };
  if (!a) { out.problems.push('missing ' + id); continue; }
  let texts = 0;
  const seen = t => { texts++; if (typeof t !== 'string' || !t || /PROVISIONAL|undefined|NaN|\u2014|\u2013/.test(t)) out.problems.push(id + ': bad text: ' + String(t).slice(0, 120)); };
  [a.name, a.tag, a.about].forEach(seen);
  (a.params || []).forEach(s => { if (s.text !== undefined) seen(s.text); if (s.label !== undefined) seen(s.label); if (s.help !== undefined) seen(s.help); });
  for (const q of VAR[id]) for (const n of [2, 3, 4, 8, 1, 0, -1, -2, 2.5, 0.5, -1.5]) {
    try {
      seen(a.formula(q, n)); seen(typeof a.roundNote === 'function' ? a.roundNote(q, n) : a.roundNote);
      const c = a.crush(q, n), s = a.smooth(q, n); seen(c[1]); seen(s[1]);
      if (!['ok', 'part', 'no'].includes(c[0]) || !['ok', 'part', 'no'].includes(s[0])) out.problems.push(id + ': bad pill');
      seen(a.slice(true, q, n)); seen(a.slice(false, q, n));
      const v = L.MATH[id]([0.3, -0.4, 0.5], n, q), z = L.MATH[id]([0, 0, 0], n, q), ax = a.axis(q);
      if (!v.every(Number.isFinite) || !z.every(Number.isFinite) || !ax.every(Number.isFinite)) out.problems.push(id + ': not finite at n = ' + n);
    } catch (e) { out.problems.push(id + ' n ' + n + ' ' + JSON.stringify(q) + ': ' + e.message); }
  }
  row.textsRead = texts;
  // on the page
  $('ap-' + id).click(); await sleep(200); $('mode-m').click(); S.n = 2; S.flat = false; L.syncControls(); L.refresh(false); L.touch();
  row.drawn = await idle(); row.failed = String(L.R.failed);
  row.formulaShown = ($('f-' + id) || {}).textContent || '(none)';
  row.dials = [...document.querySelectorAll('#pd-' + id + ' [id^="par-' + id + '-"]')].map(e => e.id).filter(x => !/Help|Play|Num|Val/.test(x)).slice(0, 8);
  row.card = ['crush', 'smooth', 'slice'].map(k => { const e = $('r-' + k) || $('s-' + k); return e ? e.textContent.slice(0, 90) : '(cell not found)'; });
  try {
    const st = L.learn.setOn(true); await sleep(400);
    const st2 = L.learn.state();
    row.learn = { on: st2.on, moves: st2.moves, note: (st2.note || '').slice(0, 700), sentence: (st2.sentence || '').slice(0, 100), orbitFinite: st2.orbit.every(v => v.every(Number.isFinite)) };
    const plan = L.learnPlan({ space: 3, id, params: S.param[id], n: 2, c: [-0.4, 0.2, 0.1] });
    row.learnPlanCheck = plan.check([0.3, -0.4, 0.5]);
    L.learn.setOn(false); await sleep(200);
  } catch (e) { out.problems.push(id + ': Learn tab: ' + e.message); }
  out.entries.push(row);
}
$('ap-mercator').click(); await sleep(200);
out.idleAtEnd = await idle(); out.failedAtEnd = String(L.R.failed);
return JSON.stringify(out, null, 1);

// Round 22, entry: does the card of Pulled plane follow the c of the Julia dials, and does no other card change with c?
// (HEAD of run.py is in front of this.)
const type = (id, v) => { const e = $(id); if (!e) fail('no control ' + id); e.value = v; e.dispatchEvent(new Event('input', { bubbles: true })); e.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', bubbles: true })); };
const cardIdle = async () => { await sleep(400); for (let i = 0; i < 3000 && !L.idle(); i++) await sleep(20); if (!L.idle()) fail('the card never finished'); };
const sliceCell = () => { const e = $('s-slice') || $('p-slice'); return e ? e.textContent : $('card').innerText; };
const out = {};
$('mode-j').click(); await sleep(150);
for (const id of ['pulledplane', 'alongonce', 'turnalong']) {
  $('ap-' + id).click(); await sleep(250); S.n = 2; S.c = [-1, 0, 0]; go(); await cardIdle();
  const a = $('card').innerText;
  type('cz', '0.3'); await cardIdle();
  if (Math.abs(S.c[2] - 0.3) > 1e-9) fail('the c dial did not take: ' + S.c);
  const b = $('card').innerText;
  type('cz', '0'); await cardIdle();
  const c = $('card').innerText;
  out[id] = { changedWithC: a !== b, backAgain: a === c, flat: /follows complex arithmetic exactly/.test(a), off: /does not follow complex arithmetic/.test(b), first: L.MATH[id]([0.3, 0.4, 0.5], 2, S.param[id], [-1, 0, 0.3]).map(x => +x.toFixed(6)), firstFlat: L.MATH[id]([0.3, 0.4, 0.5], 2, S.param[id], [-1, 0, 0]).map(x => +x.toFixed(6)) };
}
if (!out.pulledplane.changedWithC || !out.pulledplane.backAgain) fail('the card of Pulled plane does not follow c: ' + JSON.stringify(out.pulledplane));
if (!out.pulledplane.flat || !out.pulledplane.off) fail('the slice line of Pulled plane is not what it should be: ' + JSON.stringify(out.pulledplane));
if (out.alongonce.changedWithC || out.turnalong.changedWithC) fail('a card that should not depend on c changed with c');
$('resetAll').click(); await sleep(300);
return JSON.stringify(out);

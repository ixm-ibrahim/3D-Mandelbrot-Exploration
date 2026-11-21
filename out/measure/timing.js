// Times updateCard() and checks that the frame-sliced measurement ends on the same numbers as measure().
const L = window.squaringLab, T = L.T, S = L.S;
const frame = () => new Promise(r => requestAnimationFrame(r));
const rows = [];
for (const [idx, n] of [[0, 2], [1, 3], [2, -2], [3, 8], [4, 2.5], [0, -3], [1, 0.5], [2, 8]]) {
  const id = T.APPROACHES[idx].id;
  S.approach = idx; S.n = n;
  T.cardRun.cache.clear();
  await new Promise(r => setTimeout(r, 320));   // long enough that the call does not count as part of a stream
  let gap = 0, last = 0, busySeen = false, on = true;
  const tick = () => { const t = performance.now(); if (last) gap = Math.max(gap, t - last); last = t; busySeen = busySeen || T.busyTasks.has('measure'); if (on) requestAnimationFrame(tick); };
  requestAnimationFrame(tick);
  await frame(); await frame();
  gap = 0;
  const t0 = performance.now();
  T.updateCard();
  const call = performance.now() - t0, pendingAfterCall = !T.cardIdle(), ariaBusy = document.getElementById('card').getAttribute('aria-busy');
  while (!T.cardIdle()) await frame();
  const wall = performance.now() - t0;
  on = false;
  const a = T.cardRun.result, p = { ...S.param[id] };
  const t1 = performance.now(), b = L.measure(v => T.MATH[id](v, n, p), n), sync = performance.now() - t1;
  const same = Object.keys(b).length === Object.keys(a).length && Object.keys(b).every(k => Object.is(a[k], b[k]));
  rows.push(`${id} n=${n}: call ${call.toFixed(2)} ms, ${T.cardRun.slices} slices, longest slice ${T.cardRun.longest.toFixed(2)} ms, longest frame gap ${gap.toFixed(1)} ms, done after ${wall.toFixed(0)} ms (one blocking measure(): ${sync.toFixed(0)} ms), ` +
    `pending after call ${pendingAfterCall}, aria-busy ${ariaBusy}, busy label seen ${busySeen}, busy cleared ${!T.busyTasks.has('measure')}, same numbers as measure() ${same}, used ${a.used}`);
}
S.approach = 0; S.n = 2; L.refresh(false);
return rows;

// Warming: after the first picture, the renderer prepares the programs the next click is likely to need.
// Reports how long that takes, whether it disturbs the page's frames, and how switches behave afterwards.
const L = window.squaringLab, $ = id => document.getElementById(id);
const sleep = ms => new Promise(r => setTimeout(r, ms));
const frame = () => new Promise(r => requestAnimationFrame(r));
const idle = async () => { while (!L.idle()) await sleep(8); };
let gaps = [], busy = 0, last = performance.now(), on = true;
(function tick() {
  const t = performance.now(); gaps.push(t - last); last = t;
  const b = $('busy'); if (b && !b.hidden) busy++;
  if (on) requestAnimationFrame(tick);
})();
const out = [];
await idle();
gaps = []; last = performance.now();
const t0 = performance.now(), c0 = L.R.compiles;
await sleep(700);
while (L.R.warming || L.R.warmT) await sleep(50);
out.push(`warming: ${L.R.compiles - c0} programs in ${Math.round(performance.now() - t0)} ms, longest frame gap meanwhile ${Math.max(...gaps).toFixed(1)} ms`);
const run = async (name, fn) => {
  await idle(); await sleep(150);
  gaps = []; busy = 0; last = performance.now();
  const t0 = performance.now(), c = L.R.compiles; fn();
  let first = 0;
  while (!first) { await frame(); if ($('status').textContent !== 'Preparing the formula' && L.R.shown) first = performance.now() - t0; if (performance.now() - t0 > 20000) break; }
  await idle();
  return `${name}: new compiles ${L.R.compiles - c}, busy label on ${busy} frames, longest frame gap ${Math.max(...gaps).toFixed(1)} ms, finished after ${Math.round(performance.now() - t0)} ms`;
};
L.R.warmOn = false;   // so the switches below do not start further warming and blur the count
const idx = id => +$('ap-' + id).value;
out.push(await run('approach -> classic', () => { L.S.approach = idx('classic'); L.touch(); }));
out.push(await run('approach -> lathe', () => { L.S.approach = idx('lathe'); L.touch(); }));
out.push(await run('approach -> first, equation -> lambda', () => { L.S.approach = 0; L.S.eq = 'c*z*(1 - z)'; L.S.z0 = '0.5'; L.touch(); }));
out.push(await run('equation -> Mandelbrot, power 2 -> 3', () => { L.S.eq = 'z^n + c'; L.S.z0 = '0'; L.S.n = 3; L.touch(); }));
out.push(await run('mode -> Kleinian', () => { L.S.mode = 'k'; L.touch(); }));
on = false;
return out;

// Longest gap between animation frames around switches that need a new shader program.
// "state only" switches change S and call touch(), so only the renderer is timed; "click" switches go
// through the page's own handlers (which in the baseline also run the scorecard measurement).
const L = window.squaringLab, $ = id => document.getElementById(id);
L.R.warmOn = false;                         // time real compiles, not programs prepared in advance
const sleep = ms => new Promise(r => setTimeout(r, ms));
const frame = () => new Promise(r => requestAnimationFrame(r));
const idle = async () => { while (!L.idle()) await sleep(8); };
let gaps = [], busy = 0, labels = {}, bar = 0, barMax = 0, last = performance.now(), on = true;
(function tick() {
  const t = performance.now(); gaps.push(t - last); last = t;
  const b = $('busy'); if (b && !b.hidden) { busy++; labels[b.textContent] = 1; }
  const p = $('drawProgress');
  if (p && !p.hidden) { bar++; barMax = Math.max(barMax, parseFloat(p.firstChild.style.transform.replace('scaleX(', '')) || 0); }
  if (on) requestAnimationFrame(tick);
})();
const run = async (name, fn) => {
  await idle(); await sleep(250);
  gaps = []; busy = 0; labels = {}; bar = 0; barMax = 0; last = performance.now();
  const t0 = performance.now(); fn(); const handler = performance.now() - t0;
  await frame(); await frame(); await idle();
  const total = performance.now() - t0;
  await sleep(60);
  return `${name}: handler ${handler.toFixed(1)} ms, longest frame gap ${Math.max(...gaps).toFixed(1)} ms, finished after ${Math.round(total)} ms, busy label on ${busy} frames [${Object.keys(labels).join(' / ')}], progress bar on ${bar} frames (max ${barMax.toFixed(2)})`;
};
const idx = id => +$('ap-' + id).value, out = [];
await idle();
out.push(await run('state only: approach -> classic', () => { L.S.approach = idx('classic'); L.touch(); }));
out.push(await run('state only: equation -> lambda', () => { L.S.eq = 'c*z*(1 - z)'; L.S.z0 = '0.5'; L.touch(); }));
out.push(await run('state only: power 2 -> 3', () => { L.S.eq = 'z^n + c'; L.S.z0 = '0'; L.S.n = 3; L.touch(); }));
out.push(await run('state only: mode -> Kleinian', () => { L.S.mode = 'k'; L.touch(); }));
out.push(await run('state only: back to the first program (cached)', () => { L.S.mode = 'm'; L.S.n = 2; L.S.approach = 0; L.touch(); }));
out.push(await run('click: approach -> lathe', () => $('ap-lathe').click()));
out.push(await run('click: preset -> cubic', () => { const s = $('eqPreset'); s.value = '4'; s.dispatchEvent(new Event('change', { bubbles: true })); }));
out.push(await run('camera move only (no new program)', () => { L.cam.yaw += 0.3; L.touch(); }));
on = false;
return out;

const L = window.squaringLab, $ = id => document.getElementById(id);
L.R.warmOn = false;
const sleep = ms => new Promise(r => setTimeout(r, ms));
const frame = () => new Promise(r => requestAnimationFrame(r));
const idle = async () => { while (!L.idle()) await sleep(8); };
await idle();
const out = [];
const run = async (name, fn) => {
  await idle(); await sleep(200);
  const t0 = performance.now(); fn();
  const log = []; let n = 0;
  await frame();
  while (!L.idle() && performance.now() - t0 < 60000) {
    await frame(); n++;
    if (n % 30 === 0 || n < 12) log.push(`${Math.round(performance.now() - t0)}ms rows=${L.R.rows.toFixed(1)} ps=${L.R.ps.toFixed(2)} rowMs=${L.R.rowMs.toFixed(3)} ${$('status').textContent} y=${L.R.prog ? L.R.prog.y : '-'}`);
  }
  out.push(name + ' finished after ' + Math.round(performance.now() - t0) + ' ms, frames ' + n); out.push(...log.slice(0, 40));
};
await run('lambda first use', () => { L.S.eq = 'c*z*(1 - z)'; L.S.z0 = '0.5'; L.touch(); });
await run('lambda again (camera nudge)', () => { L.cam.yaw += 0.01; L.touch(); });
return out;

const L = window.squaringLab, $ = id => document.getElementById(id);
L.R.warmOn = false;
const sleep = ms => new Promise(r => setTimeout(r, ms));
const idle = async () => { while (!L.idle()) await sleep(8); };
await idle(); await sleep(200);
const out = [];
for (let k = 0; k < 3; k++) {
  L.R.log = [];
  const t0 = performance.now();
  L.cam.yaw += 0.02; L.touch();
  await sleep(50); await idle();
  const log = L.R.log, bands = log.filter(x => x[0] === 'band');
  const sum = i => bands.reduce((a, x) => a + x[i], 0);
  out.push(`run ${k}: finished after ${Math.round(performance.now() - t0)} ms; ${bands.length} bands, exact on ${bands.filter(x => x[4]).length}; wall sum ${Math.round(sum(2))} ms, counted sum ${Math.round(sum(3))} ms; dt ${log[log.length - 1][5]}`);
  out.push(log.slice(0, 14).map(x => x.join(',')).join(' | '));
}
return out;

//// wait=done
const L = window.squaringLab; L.R.warmOn = false; return 'ready';
//// 
// The same picture drawn three ways: sized by the GPU timer; by the clock (no timer extension); by the clock at 30 frames a second.
const L = window.squaringLab, sleep = ms => new Promise(r => setTimeout(r, ms)), out = [];
const run = async name => {
  let gaps = [], last = performance.now(), on = true;
  (function tick() { const t = performance.now(); gaps.push(t - last); last = t; if (on) requestAnimationFrame(tick); })();
  L.R.log = []; L.cam.yaw += 0.001; L.touch(); const t0 = performance.now(); await sleep(80); while (!L.idle()) await sleep(10);
  on = false;
  const bands = L.R.log.filter(x => x[0] === 'band'), rows = bands.map(x => x[1]).sort((a, b) => a - b);
  out.push(`${name}: finished in ${Math.round(performance.now() - t0)} ms, ${bands.length} bands, rows per band min ${rows[0]} median ${rows[rows.length >> 1]} max ${rows[rows.length - 1]}, exact timings ${bands.filter(x => x[4]).length}, frame interval ${L.R.dt.toFixed(1)} ms, longest frame gap ${Math.max(...gaps).toFixed(1)} ms`);
};
await run('GPU timer');
await run('GPU timer');
const tq = L.R.tq; L.R.tq = null;
await run('clock only');
await run('clock only');
// halve the frame rate: every other animation frame is skipped
const raf = window.requestAnimationFrame;
window.requestAnimationFrame = f => raf(() => raf(f));
await run('clock only, 30 frames a second');
await run('clock only, 30 frames a second');
L.R.tq = tq;
await run('GPU timer, 30 frames a second');
window.requestAnimationFrame = raf;
return out;

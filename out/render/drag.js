//// wait=done
const L = window.squaringLab; L.R.warmOn = false; return 'ready';
//// 
const L = window.squaringLab, sleep = ms => new Promise(r => setTimeout(r, ms)), frame = () => new Promise(r => requestAnimationFrame(r));
const out = [];
const drag = async (name, setup) => {
  setup(); L.touch(); await sleep(80); while (!L.idle()) await sleep(10);
  L.R.log = []; L.R.loopMax = 0;
  let gaps = [], last = performance.now(), n = 0;
  const t0 = performance.now();
  while (performance.now() - t0 < 2000) {   // two seconds of turning, one camera change per frame
    await frame(); const t = performance.now(); gaps.push(t - last); last = t; n++;
    if (L.S.flat) L.S.v2.x += 0.002; else L.cam.yaw += 0.01;
    L.touch();
  }
  const prevs = L.R.log.filter(x => x[0] === 'prev');
  const tEnd = performance.now();
  while (document.getElementById('drawProgress').hidden && performance.now() - tEnd < 3000) await frame();
  const startDelay = performance.now() - tEnd;
  while (!L.idle()) await sleep(10);
  out.push(`${name}: ${n} frames in 2 s (longest gap ${Math.max(...gaps).toFixed(1)} ms), ${prevs.length} previews drawn at ${L.R.pw}x${L.R.ph} of ${document.getElementById('view').width}x${document.getElementById('view').height}, preview GPU time median ${prevs.map(x => x[3]).sort((a, b) => a - b)[prevs.length >> 1]} ms, full drawing began ${Math.round(startDelay)} ms after the last move, finished ${Math.round(performance.now() - tEnd)} ms after it, longest loop() ${L.R.loopMax.toFixed(2)} ms`);
};
await drag('3D, balanced', () => {});
await drag('3D, distance estimate with no neighbours', () => { L.S.q.de = 0; });
await drag('3D mosaic', () => { L.S.q.de = 3; L.S.mosaic = true; });
await drag('2D view', () => { L.S.mosaic = false; L.S.flat = true; });
await drag('2D view, 200 iterations', () => { L.S.iter = 200; });
return out;

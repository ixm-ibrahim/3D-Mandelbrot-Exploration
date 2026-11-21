//// wait=done
const L = window.squaringLab; L.R.warmOn = false; return 'ready';
//// 
// GPU time of the default picture, per pass, as counted by the GPU timer
const L = window.squaringLab, sleep = ms => new Promise(r => setTimeout(r, ms)), out = [];
for (let k = 0; k < 3; k++) {
  L.R.log = []; L.cam.yaw += 0.001; L.touch(); await sleep(80); while (!L.idle()) await sleep(10);
  const bands = L.R.log.filter(x => x[0] === 'band'), gpu = bands.reduce((a, x) => a + x[3], 0), wall = bands.reduce((a, x) => a + x[2], 0);
  out.push(`${bands.length} bands, GPU ${Math.round(gpu)} ms for 12 passes (${Math.round(gpu / 12)} ms a pass), clock ${Math.round(wall)} ms, GPU busy ${Math.round(100 * gpu / wall)}%`);
}
return out;

//// wait=done
const L = window.squaringLab; L.R.warmOn = false; return 'ready';
//// 
const L = window.squaringLab, $ = id => document.getElementById(id), sleep = ms => new Promise(r => setTimeout(r, ms));
const idle = async () => { while (!L.idle()) await sleep(8); };
const out = [];
let gaps = [], last = performance.now(), on = true;
(function tick() { const t = performance.now(); gaps.push([t - last, Math.round(t)]); last = t; if (on) requestAnimationFrame(tick); })();
const run = async (name, fn) => {
  await idle(); await sleep(250);
  L.R.log = []; L.R.loopMax = 0; gaps = []; last = performance.now();
  const t0 = performance.now(); fn(); await sleep(60); await idle();
  const big = gaps.filter(g => g[0] > 40).map(g => `${g[0].toFixed(0)} ms ending at +${Math.round(g[1] - t0)}`);
  const prevs = L.R.log.filter(x => x[0] === 'prev').map(x => `wall ${x[2]} gpu ${x[3]}`);
  const bands = L.R.log.filter(x => x[0] === 'band');
  out.push(`${name}: gaps over 40 ms [${big.join('; ')}], longest loop() ${L.R.loopMax.toFixed(1)} ms in ${L.R.loopWhere}, previews [${prevs.join('; ')}], largest band gpu ${Math.max(...bands.map(x => x[3]))} wall ${Math.max(...bands.map(x => x[2]))}, compile wait ${Math.round((L.R.log[0] ? 0 : 0))}`);
};
const idx = id => +$('ap-' + id).value;
await run('approach -> classic', () => { L.S.approach = idx('classic'); L.touch(); });
await run('equation -> lambda', () => { L.S.eq = 'c*z*(1 - z)'; L.S.z0 = '0.5'; L.touch(); });
await run('power 2 -> 3', () => { L.S.eq = 'z^n + c'; L.S.z0 = '0'; L.S.n = 3; L.touch(); });
await run('mode -> Kleinian', () => { L.S.mode = 'k'; L.touch(); });
await run('back to the first program', () => { L.S.mode = 'm'; L.S.n = 2; L.S.approach = 0; L.touch(); });
await run('camera move', () => { L.cam.yaw += 0.3; L.touch(); });
on = false;
return out;

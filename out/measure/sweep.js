// Drives the real page (refresh -> updateCard -> figures) through every approach, a grid of powers and some
// offsets, and reads the finished card and captions back from the page.
const L = window.squaringLab, T = L.T, S = L.S, R = T.cardRun;
const frame = () => new Promise(r => requestAnimationFrame(r)), sleep = ms => new Promise(r => setTimeout(r, ms));
const NS = [-8, -3, -2, -1, -0.5, -0.1, 0, 0.1, 0.5, 1, 1.5, 2, 2.5, 3, 8, 10];
const extra = { mercator: [{ planes: 1 }, { planes: 1, turn: 30 }, { planes: 1, lift: 0.5 }, { planes: 8 }], lathe: [{ spin: -3 }], bulb: [{ lat: 20 }, { lon: 45 }], classic: [{ theta: -90 }, { phi: 45 }], split: [] };
const problems = [], seen = new Set();
// Frame gaps are kept apart for the first case after an approach switch: there the baseline renderer compiles a
// new shader on the main thread, which is its stall, not the scorecard's.
let cases = 0, worstCall = 0, worstSlice = 0, gapSame = 0, gapSwitch = 0, switching = false, last = 0, on = true;
const tick = () => { const t = performance.now(); if (last) { if (switching) gapSwitch = Math.max(gapSwitch, t - last); else gapSame = Math.max(gapSame, t - last); } last = t; if (on) requestAnimationFrame(tick); };
requestAnimationFrame(tick);
for (let i = 0; i < T.APPROACHES.length; i++) {
  const a = T.APPROACHES[i], defs = T.specDefaults(a.params || []);
  let first = true;
  for (const v of [{}, ...(extra[a.id] || [])]) for (const n of NS) {
    switching = first; first = false;
    S.approach = i; S.n = n; Object.assign(S.param[a.id], defs, v);
    const t0 = performance.now();
    // window.SWEEP_DIRECT: call only this module's own functions, leaving the 3D picture (and its shader compiles) alone
    if (window.SWEEP_DIRECT) { T.buildStep3d(); T.drawStep2d(); T.updateCard(); T.drawStep3d(); } else L.refresh(false);
    worstCall = Math.max(worstCall, performance.now() - t0);
    while (!T.cardIdle()) await frame();
    worstSlice = Math.max(worstSlice, R.slices ? R.longest : 0);
    cases++;
    const where = `${a.id} ${JSON.stringify(v)} n=${n}`;
    const texts = [...document.querySelectorAll('#card .cell span:not(.k), #cap2d, #cap3d')].map(e => e.textContent);
    for (const t of texts) {
      seen.add(t);
      if (/NaN|undefined|Infinity|null|\[object|−0[^.]|-\d|  |\.\.|,\./.test(t) || !t.trim()) problems.push(`${where}: "${t}"`);
    }
    for (const b of document.querySelectorAll('#card .pill')) if (b.style.display === 'none' || !/^(holds|partly|fails)$/.test(b.textContent) || b.style.opacity) problems.push(`${where}: pill ${b.id} "${b.textContent}"`);
    if (document.getElementById('card').hasAttribute('aria-busy') || T.busyTasks.has('measure')) problems.push(`${where}: still marked busy`);
  }
  Object.assign(S.param[a.id], defs);
}
on = false;
S.approach = 0; S.n = 2; L.syncControls(); L.refresh(false);
return [`${cases} cases, ${seen.size} different sentences, ${problems.length} problems`,
  `longest ${window.SWEEP_DIRECT ? 'buildStep3d + drawStep2d + updateCard + drawStep3d' : 'refresh()'} call ${worstCall.toFixed(1)} ms, longest measuring slice ${worstSlice.toFixed(1)} ms, longest gap between frames ${gapSame.toFixed(1)} ms (and ${gapSwitch.toFixed(0)} ms in the frames where the baseline renderer compiles the next approach's shader)`, ...problems.slice(0, 40)].join('\n');

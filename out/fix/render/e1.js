// perf-3: pictures per second while dragging, per quality preset; 2D view when ARG.flat.
// Also reports how long the finished picture takes after the drag stops (perf-1, perf-2).
const L = window.squaringLab, T = window.__t, R = L.R, $ = id => document.getElementById(id);
R.warmOn = false;
if (ARG && ARG.setup) { new Function(ARG.setup)(); await T.idle(60000); }
if (ARG && ARG.flat && !L.S.flat) $('flat').click();
const out = [];
for (const q of (ARG && ARG.presets) || ['qUltra', 'qFast', 'qBal']) {
  $(q).click(); await T.idle((ARG && ARG.cap) || 15000); await T.sleep(300);
  await T.drag(600, !!L.S.flat);            // let the preview size settle
  T.start(); const d = await T.drag(2000, !!L.S.flat); const ev = T.stop();
  const fin = await T.idle((ARG && ARG.cap) || 15000);
  const pv = ev.filter(e => e[1] === 'blit' && e[2] === 'prev').map(e => e[0]), gaps = pv.slice(1).map((x, i) => x - pv[i]);
  const jobs = T.sum(ev).filter(j => j.seen !== null), seen = jobs.map(j => j.seen).sort((a, b) => a - b), gpu = jobs.map(j => j.gpu).filter(x => x !== null).sort((a, b) => a - b);
  out.push({ q, picsPerSec: pv.length / 2, gapAvg: Math.round(gaps.reduce((a, b) => a + b, 0) / gaps.length * 10) / 10, gapMax: Math.round(Math.max(...gaps) * 10) / 10, frames: d.frames, worstRaf: d.worstGap,
    prev: R.pw + 'x' + R.ph, canvas: $('view').width + 'x' + $('view').height, seenMed: seen[seen.length >> 1], gpuMed: gpu[gpu.length >> 1], pollsAvg: Math.round(jobs.reduce((a, j) => a + j.polls, 0) / jobs.length * 10) / 10, finalMs: fin && Math.round(fin), frac: T.frac(), status: $('status').textContent });
}
return out;

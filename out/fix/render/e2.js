// perf-1 / perf-2: from rest, one small move, then the full-quality drawing traced job by job.
// ARG: { setup: 'js', preset: 'qFast', reps: 3, cap: 12000, drag: ms (0 = single move), dump: true }
const L = window.squaringLab, T = window.__t, R = L.R, $ = id => document.getElementById(id);
R.warmOn = false;
if (ARG && ARG.setup) { new Function(ARG.setup)(); await T.idle(90000); }
$((ARG && ARG.preset) || 'qFast').click(); await T.idle(60000); await T.sleep(300);
const out = [], cap = (ARG && ARG.cap) || 12000;
for (let rep = 0; rep < ((ARG && ARG.reps) || 3); rep++) {
  T.start();
  let tEnd;
  if (ARG && ARG.drag) { const d = await T.drag(ARG.drag, !!L.S.flat); tEnd = d.end; }
  else { if (L.S.flat) L.S.v2.x += L.S.v2.h * 0.01; else L.cam.yaw += 0.02; L.touch(); tEnd = performance.now(); }
  const fin = await T.idle(cap); const frac = T.frac(), status = $('status').textContent;
  const ev = T.stop(), off = tEnd - T.t0;
  const jobs = T.sum(ev), bands = jobs.filter(j => j.rows > 0 && j.t >= off), seen = bands.filter(j => j.seen !== null);
  const rows = bands.map(j => j.rows).sort((a, b) => a - b), gpu = seen.map(j => j.gpu).filter(x => x !== null);
  const firstAcc = ev.find(e => e[1] === 'blit' && e[2] === 'acc' && e[0] >= off);
  const o = { final: fin && Math.round(fin - 0), afterStop: fin === null ? null : Math.round(performance.now() - 0) && Math.round(fin), frac, status, bands: bands.length,
    rowsMin: rows[0], rowsMed: rows[rows.length >> 1], rowsMax: rows[rows.length - 1], gpuSum: Math.round(gpu.reduce((a, b) => a + b, 0)), gpuMed: gpu.slice().sort((a, b) => a - b)[gpu.length >> 1],
    seenMed: seen.map(j => j.seen).sort((a, b) => a - b)[seen.length >> 1], firstBandAt: bands.length ? Math.round(bands[0].t - off) : null, firstAccAt: firstAcc ? Math.round(firstAcc[0] - off) : null,
    lastBandSeenAt: seen.length ? Math.round(seen[seen.length - 1].t + seen[seen.length - 1].seen - off) : null, canvas: $('view').width + 'x' + $('view').height, total: R.total, dt: Math.round(R.dt * 10) / 10 };
  if (ARG && ARG.dump) o.jobs = jobs.filter(j => j.t >= off - 50).slice(0, ARG.dump === true ? 60 : ARG.dump).map(j => [Math.round(j.t - off), j.kind, j.rows, j.vp, j.seen, j.gpu, j.polls]);
  out.push(o);
  if (fin === null) await T.idle(60000);
  await T.sleep(200);
}
return out;

// Other paths: the busy label around a switch (perf-4, p1-1), the clock-only path (no GPU timer), the failure text.
const L = window.squaringLab, T = window.__t, R = L.R, $ = id => document.getElementById(id);
R.warmOn = false;
const out = {};
// 1. a switch to an approach not shown yet: label texts frame by frame until the picture is finished
{
  const seen = []; let last = null, worst = 0, prevT = performance.now(), bare = 0, firstPrevAt = null, labelOffAt = null; const t0 = performance.now();
  T.start();
  $('ap-classic').click();
  await new Promise(res => { const f = () => { const now = performance.now(); worst = Math.max(worst, now - prevT);
    const b = $('busy'), tx = b && !b.hidden ? b.textContent : '', bar = !$('drawProgress').hidden;
    if (tx !== last) { seen.push([Math.round(now - t0), tx]); last = tx; }
    if (!tx && labelOffAt === null && seen.length > 1) labelOffAt = Math.round(now - t0);
    if (!tx && !bar && !L.idle()) bare += now - prevT;
    prevT = now;
    if (L.idle() && now - t0 > 300) res(); else if (now - t0 > 60000) res(); else T.oraf(f); }; T.oraf(f); });
  const ev = T.stop(), fp = ev.find(e => e[1] === 'blit' && e[2] === 'prev');
  out.switch = { labels: seen, worstRafGap: Math.round(worst), firstPreviewOnCanvasAt: fp ? Math.round(fp[0]) : null, labelOffAt, msWithNoIndicator: Math.round(bare), status: $('status').textContent };
}
// 2. no GPU timer: sizes come from the clock
R.tq = null;
$('qBal').click(); await T.idle(60000);
{ T.start(); const d = await T.drag(1500, false); const ev = T.stop(); const fin = await T.idle(60000);
  const pv = ev.filter(e => e[1] === 'blit' && e[2] === 'prev').length;
  out.clock = { picsPerSec: pv / 1.5, worstRaf: d.worstGap, finalMs: fin && Math.round(fin), prev: R.pw + 'x' + R.ph, rows: Math.round(R.rows), status: $('status').textContent }; }
// 3. animation frames paused (a background tab): the timer finishes the picture
{ const raf = window.requestAnimationFrame; window.requestAnimationFrame = () => 0;
  L.cam.yaw += 0.1; L.touch(); const t0 = performance.now();
  await new Promise(res => { const iv = setInterval(() => { if (L.renderIdle() || performance.now() - t0 > 60000) { clearInterval(iv); res(); } }, 100); });
  window.requestAnimationFrame = raf;
  out.background = { finalMs: Math.round(performance.now() - t0), status: $('status').textContent, idle: L.renderIdle() }; }
return out;

// perf-5: programs are prepared ahead while the default picture is still being refined; a later switch then needs no compile.
const L = window.squaringLab, T = window.__t, R = L.R, $ = id => document.getElementById(id);
const out = { compilesAtStart: R.compiles };
$('qFine').click();                       // a long drawing: 32 passes
L.cam.yaw += 0.3; L.touch();
let worst = 0, prevT = performance.now(), during = 0; const t0 = prevT;
await new Promise(res => { const f = () => { const now = performance.now(); worst = Math.max(worst, now - prevT); prevT = now;
  if (!L.renderIdle()) during = R.compiles; if (now - t0 > 9000) res(); else T.oraf(f); }; T.oraf(f); });
out.compilesWhileStillDrawing = during; out.stillDrawingAt9s = !L.renderIdle(); out.worstRafGap = Math.round(worst); out.status = $('status').textContent;
$('qFast').click(); await T.idle(60000);
// wait until everything has been prepared, then switch approach and count compiles and the busy label
for (let i = 0; i < 200 && (R.warming || R.warmT); i++) await T.sleep(300);
out.compilesAfterWarming = R.compiles;
const c0 = R.compiles; let label = false;
$('ap-lathe').click();
await new Promise(res => { const t1 = performance.now(); const f = () => { const b = $('busy'); if (b && !b.hidden && /Preparing/.test(b.textContent)) label = true; if ((L.idle() && performance.now() - t1 > 200) || performance.now() - t1 > 30000) res(); else T.oraf(f); }; T.oraf(f); });
out.switchCompiles = R.compiles - c0; out.switchShowedPreparing = label; out.final = $('status').textContent;
return out;

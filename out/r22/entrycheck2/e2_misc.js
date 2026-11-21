// Round 22, entrycheck second pass: small things. (HEAD of drv.py in front.)
const cardDone = async () => { await sleep(350); for (let i = 0; i < 800 && !L.cardIdle(); i++) await sleep(25); await sleep(150); };
const pick = async (id, c) => { $('mode-j').click(); await sleep(150); $('ap-' + id).click(); await sleep(250); if (apId() !== id) fail('could not choose ' + id); S.eq = 'z^n + c'; S.z0 = '0'; S.n = 2; S.iter = 30; S.c = (c || [-1, 0, 0]).slice(); S.flat = false; S.cutOn = false; S.mosaic = false; S.abs = [0, 0, 0]; S.flip = [0, 0]; L.resetCam(); go(); await settle(); await cardDone(); };
//@@STEP
const o = [];
// 1. what a sweep of a c dial costs per frame for Pulled plane against Turning plane, along: frames in 2 s while c moves every frame
for (const id of ['pulledplane', 'turnalong', 'pulledplane', 'turnalong']) {
  await pick(id); S.iter = 16; go(); await settle();
  let frames = 0, t0 = performance.now(), worst = 0, last = t0;
  await new Promise(res => { const tick = () => { const now = performance.now(); worst = Math.max(worst, now - last); last = now; frames++; S.c[1] = 0.3 * Math.sin(frames / 20); L.touch(); if (now - t0 < 2000) requestAnimationFrame(tick); else res(); }; requestAnimationFrame(tick); });
  await settle(); await cardDone();
  o.push('sweep of c for 2 s, ' + id + ': ' + frames + ' frames, longest gap ' + Math.round(worst) + ' ms');
}
// 2. the notes of the flat Learn spaces: are the new entries named as exceptions?
for (const sp of [2, 1]) { const p = L.learnPlan({ space: sp, id: 'pulledplane', params: S.param.pulledplane, n: 2, c: [-0.5, 0.3, 0.4] }); o.push('Learn note, space ' + sp + ' (c given with a z part): ' + p.note); }
// 3. "Reset everything" with Pulled plane chosen and c moved
await pick('pulledplane', [-0.3, 0.5, 0.2]); const before = $('card').innerText;
const ra = $('resetAll'); if (ra) { ra.click(); await sleep(600); await settle(); await cardDone(); const t = $('card').innerText; go(); await settle(); await cardDone(); o.push('Reset everything: entry ' + apId() + ', mode ' + S.mode + ', c ' + JSON.stringify(S.c) + ', card same as a fresh one ' + (t === $('card').innerText)); } else o.push('no resetAll button');
// 4. after the reset choose Pulled plane again in the Mandelbrot view the page starts with: card same as fresh
$('ap-pulledplane').click(); await sleep(300); await settle(); await cardDone(); const t2 = $('card').innerText; go(); await settle(); await cardDone();
o.push('Pulled plane chosen right after the reset (mode ' + S.mode + '): card same as a fresh one ' + (t2 === $('card').innerText) + '; remembered measurements with a c: ' + [...L.cardRun.cache.keys()].filter(k => k.includes(' c=')).join(' ;; '));
return JSON.stringify(o);

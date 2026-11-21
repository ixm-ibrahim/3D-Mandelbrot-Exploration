// How long does each step of Play take, and each rest on a whole step? The slider's value is read at every frame.
// At Normal a step should take 1.1 s and each rest 0.35 s: 16 steps and 15 rests, 22.85 s in all.
//@
await shapeOn({ kind: 'm', space: 2, pos: 0 });
window.__pace = async (kind, space, c, ap) => {
  if (ap) await approach(ap);
  L.shape.set({ kind, space, c: c || [-0.1226, 0.7449, 0], pos: 0 });
  await sleep(700);
  const log = [];
  let stop = false;
  const tick = now => { if (stop) return; log.push([now, +$('learnShapePos').value]); requestAnimationFrame(tick); };
  $('learnShapePlay').click();
  requestAnimationFrame(tick);
  for (let i = 0; i < 1500; i++) { await sleep(40); if ($('learnShapePlay').textContent === 'Play') break; }
  stop = true;
  // for each whole step k: when the slider first stood on it, and when it first left it
  const moves = [], rests = [];
  let arrive = log[0][0], leave = log[0][0];
  for (let k = 1; k <= 16; k++) {
    const a = log.find(x => x[1] >= k - 1e-6), b = log.find(x => x[1] > k + 1e-6);
    if (!a) break;
    moves.push(Math.round(a[0] - leave));
    if (b) { rests.push(Math.round(b[0] - a[0])); leave = b[0]; }
  }
  return { what: kind + ' ' + space + 'D' + (ap ? ' ' + ap : ''), totalSeconds: r1((log[log.length - 1][0] - log[0][0]) / 1000), stepMs: moves.join(' '), restMs: rests.join(' ') };
};
return 'ready';
//@
return await window.__pace('m', 2);
//@
return await window.__pace('m', 2);
//@
return await window.__pace('both', 3);
//@
return await window.__pace('both', 3, [-1, 0, 0], 'fold');
//@
const sp = $('learnShapeSpeed'); sp.value = 'fast'; sp.dispatchEvent(new Event('change', { bubbles: true }));
return [await window.__pace('j', 2), await window.__pace('j', 3), await window.__pace('both', 2)];
//@
const sp = $('learnShapeSpeed'); sp.value = 'slow'; sp.dispatchEvent(new Event('change', { bubbles: true }));
const a = await window.__pace('m', 2);
sp.value = 'normal'; sp.dispatchEvent(new Event('change', { bubbles: true }));
await approach('mercator');
return a;

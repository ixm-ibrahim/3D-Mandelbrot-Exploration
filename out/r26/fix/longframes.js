// Where in a 3D play do the long frames fall? Three plays at Normal: the time between frames is noted with the time
// since Play was pressed, and every gap over 20 ms is listed. Also what the look from above (columns) took.
// Run on the mended page and on the page as joined (--page r26-fix-before --log longframes-before).
//@
await openShape(); kindBar('m'); spaceBar(3); await sleep(1200);
window.__one = async (kind, ap) => {
  if (ap) await approach(ap);
  kindBar(kind); await sleep(1200); $('learnShapeAgain').click(); await sleep(800);
  const gaps = []; let last = 0, stop = false, t0 = 0;
  const tick = now => { if (stop) return; if (last) gaps.push([Math.round(now - t0), +(now - last).toFixed(1)]); last = now; requestAnimationFrame(tick); };
  t0 = performance.now(); $('learnShapePlay').click(); requestAnimationFrame(tick);
  for (let i = 0; i < 1500; i++) { await sleep(40); if ($('learnShapePlay').textContent === 'Play') break; }
  stop = true; const s = L.shape.state();
  return { what: kind + ' 3D ' + AP().id, seconds: +((performance.now() - t0) / 1000).toFixed(1), frames: gaps.length, over20: gaps.filter(g => g[1] > 20).map(g => g[1] + ' ms at ' + (g[0] / 1000).toFixed(2) + ' s'), lookFromAboveMs: s.above ? s.above.map(a => a.kind + ' ' + a.ms) : null };
};
return 'ready';
//@
return await window.__one('m');
//@
return await window.__one('both', 'fold');
//@
return await window.__one('both');
//@
return await window.__one('both', 'pillow');
//@
return await window.__one('m', 'mercator');

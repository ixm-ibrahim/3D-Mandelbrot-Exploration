// Trying how see-through the glass should be: the same scenes drawn by the 3D module with different `look`
// numbers (an extra of the module, made for this), side by side on one sheet. Nothing of the page is changed.
//@
await shapeOn({ kind: 'm', space: 3, pos: 0 });
await sleep(300);
const T3 = LAB.learnShape3d;
const css = getComputedStyle(document.documentElement), tok = n => css.getPropertyValue(n).trim();
const hex = h => { h = h.replace('#', ''); if (h.length === 3) h = h.split('').map(c => c + c).join(''); return [0, 2, 4].map(i => parseInt(h.slice(i, i + 2), 16) / 255); };
window.__cols = () => { const c = getComputedStyle(document.documentElement), t = n => c.getPropertyValue(n).trim(); return { bg: hex(t('--stage')), body: hex(t('--brass')), warn: hex(t('--bad')), ink: hex(t('--ink')) }; };
window.__LOOKS = [
  ['A as built', {}],
  ['B glow .2', { glow: 0.2 }],
  ['C thin: front .10/.9 back .06/.45 glow .12 fog .08', { front: [0.10, 0.9], back: [0.06, 0.45], glow: 0.12, fog: 0.08, rim: 2.4 }],
  ['D tinted: front .10/.9 back .08/.4 glow .1 fog .22', { front: [0.10, 0.9], back: [0.08, 0.4], glow: 0.1, fog: 0.22, rim: 2.4 }],
  ['E tinted more: front .12/.95 back .06/.4 glow .05 fog .4', { front: [0.12, 0.95], back: [0.06, 0.4], glow: 0.05, fog: 0.4, rim: 2.2 }],
  ['F bubble: front .06/.85 back .04/.35 glow 0 fog .1', { front: [0.06, 0.85], back: [0.04, 0.35], glow: 0, fog: 0.1, rim: 2 }],
];
const host = document.createElement('div');
host.id = 'looksHost';
host.style.cssText = 'position:fixed;inset:0;z-index:99999;display:grid;grid-template-columns:repeat(3,1fr);grid-template-rows:repeat(2,1fr);gap:4px;background:' + tok('--panel') + ';padding:4px;';
document.body.appendChild(host);
window.__views = window.__LOOKS.map(([name]) => {
  const cell = document.createElement('div'); cell.style.cssText = 'position:relative;min-width:0;min-height:0;';
  const v = T3.make(); v.canvas.style.cssText = 'position:absolute;inset:0;width:100%;height:100%;';
  const cap = document.createElement('div'); cap.textContent = name; cap.style.cssText = 'position:absolute;left:6px;top:4px;font:12px monospace;color:' + tok('--ink') + ';';
  cell.appendChild(v.canvas); cell.appendChild(cap); host.appendChild(cell);
  return v;
});
window.__scene = async (ap, kind, c, levels, view) => {
  if (ap) await approach(ap);
  const out = [];
  window.__views.forEach((v, i) => {
    const w = v.canvas.clientWidth, h = v.canvas.clientHeight;
    const r = v.draw(Object.assign({ panes: [{ kind, rect: [0, 0, w, h] }], c, levels, yaw: -0.62, pitch: 0.4, zoom: 1.25, quality: 'still', colours: window.__cols(), look: window.__LOOKS[i][1] }, view || {}));
    out.push(r.ok);
  });
  await sleep(500);
  return out.every(Boolean) ? 'drawn' : 'NOT drawn: ' + out;
};
return 'ready';
//@
return await window.__scene('mercator', 'm', [0, 0, 0], [{ k: 0, alpha: 1, tint: 0 }]);
//@ sleep=0.3 shot=out/r26/join/NAME-1-ball.png
//@
return await window.__scene('mercator', 'm', [0, 0, 0], [{ k: 3, alpha: 1, tint: 0 }, { k: 2, alpha: 0.22, tint: 0, ghost: 0.55 }]);
//@ sleep=0.3 shot=out/r26/join/NAME-2-m3.png
//@
return await window.__scene('mercator', 'j', [-0.1226, 0.7449, 0], [{ k: 5, alpha: 1, tint: 0 }, { k: 4, alpha: 0.22, tint: 0, ghost: 0.55 }]);
//@ sleep=0.3 shot=out/r26/join/NAME-3-jrab5.png
//@
return await window.__scene('mercator', 'j', [-0.1226, 0.7449, 0], [{ k: 3, alpha: 0.23, tint: 0 }, { k: 2, alpha: 0.99, tint: 1, ghost: 0 }, { k: 1, alpha: 0.08, tint: 0, ghost: 0.55 }]);
//@ sleep=0.3 shot=out/r26/join/NAME-4-jrab-2.35.png
//@
return await window.__scene('mercator', 'j', [-0.1226, 0.7449, 0], [{ k: 5, alpha: 0.8, tint: 0 }, { k: 4, alpha: 0.61, tint: 0.96, ghost: 0.02 }, { k: 3, alpha: 0.01, tint: 0, ghost: 0.55 }]);
//@ sleep=0.3 shot=out/r26/join/NAME-5-jrab-4.65.png
//@
return await window.__scene('fold', 'j', [-1, 0, 0], [{ k: 8, alpha: 1, tint: 0 }, { k: 7, alpha: 0.22, tint: 0, ghost: 0.55 }], { zoom: 1.8 });
//@ sleep=0.3 shot=out/r26/join/NAME-6-fold-j8.png
//@
return await window.__scene('mercator', 'm', [0, 0, 0], [{ k: 16, alpha: 1, tint: 0 }, { k: 15, alpha: 0.22, tint: 0, ghost: 0.55 }], { zoom: 1.8 });
//@ sleep=0.3 shot=out/r26/join/NAME-7-m16.png
//@
return await window.__scene('fold', 'm', [0, 0, 0], [{ k: 3, alpha: 1, tint: 0 }, { k: 2, alpha: 0.22, tint: 0, ghost: 0.55 }]);
//@ sleep=0.3 shot=out/r26/join/NAME-8-fold-m3.png

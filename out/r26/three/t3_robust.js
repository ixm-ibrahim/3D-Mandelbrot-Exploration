// Odds and ends of the contract: sizes, sharp screens, the camera helper, the JavaScript twin on points whose answer
// is known, 'move' finding its own fineness, a lost graphics context, dispose, and calls with things left out.
const T = window.T3, L = T.L, M = T.M, V = T.view, S = L.S;
const res = {};
const gl = V.canvas.getContext('webgl2');
res.waits = [];
// a wait that gives up after a while and says so, so that a missing event cannot hang the whole run
const within = (p, ms, tag) => Promise.race([p, new Promise(f => setTimeout(() => { res.waits.push('GAVE UP waiting for ' + tag); f(); }, ms))]);
const frame = () => within(new Promise(f => requestAnimationFrame(f)), 1000, 'an animation frame');
const grab = () => { const w = V.canvas.width, h = V.canvas.height, px = new Uint8Array(w * h * 4); gl.readPixels(0, 0, w, h, gl.RGBA, gl.UNSIGNED_BYTE, px); return { w, h, px }; };
const notBg = (g, x, y) => { const i = 4 * ((g.h - 1 - y) * g.w + x); return Math.abs(g.px[i] - g.px[0]) + Math.abs(g.px[i + 1] - g.px[1]) + Math.abs(g.px[i + 2] - g.px[2]) > 4; };
T.setAp('mercator'); S.n = 2;

// 1. the twin on points whose answer can be worked out by hand
res.out = {
  centre_m: M.out([0, 0, 0], 'm', [0, 0, 0], 16),            // c = 0 stays at 0: 17
  outside: M.out([3, 0, 0], 'm', [0, 0, 0], 16),             // starts outside the ball: 0
  c1: M.out([1, 0, 0], 'm', [0, 0, 0], 16),                  // 0, 1, 2, 5: thrown out at step 3
  c_minus2: M.out([-2, 0, 0], 'm', [0, 0, 0], 16),           // 0, -2, 2, 2, ...: on the edge, stays in by the rule (not > 2)
  julia_centre: M.out([0, 0, 0], 'j', [-1, 0, 0], 16),       // 0, -1, 0, -1: 17
  julia_far: M.out([1.9, 0, 0], 'j', [-1, 0, 0], 16),        // 1.9, 2.61: thrown out at step 1
  maxK3: M.out([0, 0, 0], 'm', [0, 0, 0], 3),                // still in after 3 steps: 4
};

// 2. the size of the buffer: an ordinary screen, a sharp one, a phone-sized box
const sizes = {};
for (const [name, w, h, dpr] of [['600x450@1', 600, 450, 1], ['600x450@2', 600, 450, 2], ['390x300@3', 390, 300, 3], ['1100x700@1', 1100, 700, 1], ['1100x700@2', 1100, 700, 2]]) {
  Object.defineProperty(window, 'devicePixelRatio', { value: dpr, configurable: true });
  T.size(w, h);
  V.draw(T.one('m', [0, 0, 0], T.levelsAt(3), { quality: 'still', lod: 0 })); const a = V.stats().last;
  V.draw(T.one('m', [0, 0, 0], T.levelsAt(3), { quality: 'move', lod: 1 })); const b = V.stats().last;
  V.draw(T.one('m', [0, 0, 0], T.levelsAt(3), { quality: 'move', lod: 2 })); const c = V.stats().last;
  sizes[name] = 'still ' + a.bw + 'x' + a.bh + ', move (start) ' + b.bw + 'x' + b.bh + ', move (half) ' + c.bw + 'x' + c.bh;
}
Object.defineProperty(window, 'devicePixelRatio', { value: 1, configurable: true });
res.sizes = sizes;

// 3. the camera helper against the picture: the ball's left and right edge on the middle row, and its top
T.size(600, 450);
const o1 = T.one('m', [0, 0, 0], [{ k: 0, alpha: 1, tint: 0 }], { quality: 'still', res: 0.5, zoom: 1.3, yaw: 0.9, pitch: -0.3 });   // res 0.5: one buffer pixel per CSS pixel
V.draw(o1);
{
  const g = grab(), P = M.proj(o1, [0, 0, 600, 450]), row = Math.round(P.cy);
  let x0 = -1, x1 = -1, y0 = -1;
  for (let x = 0; x < g.w; x++) if (notBg(g, x, row)) { if (x0 < 0) x0 = x; x1 = x; }
  for (let y = 0; y < g.h; y++) if (notBg(g, Math.round(P.cx), y)) { y0 = y; break; }
  res.proj = { buffer: g.w + 'x' + g.h, picture: { left: x0, right: x1, top: y0 }, helper: { left: +(P.cx - 2 * P.s).toFixed(1), right: +(P.cx + 2 * P.s).toFixed(1), top: +(P.cy - 2 * P.s).toFixed(1) }, pxPerUnit: P.s };
  // a point of space and its picture: the Julia shape after 1 step for c = (-1, 0, 0) touches the ball where p*p - 1 has length 2, e.g. p = (0, 1, 0) (i*i - 1 = -2)
  const q = P.to([0, 1, 0]); res.proj.pointOnScreen = q.map(v => +v.toFixed(2));
}

// 4. 'move' finds its own fineness (this machine is quick, so it should end at the finest entry)
{
  const lods = [];
  for (let i = 0; i < 40; i++) { V.draw(T.one('j', [-1, 0, 0], T.levelsAt(8), { quality: 'move' })); await frame(); if (i % 5 === 4) lods.push(V.stats().lod.move); }
  res.moveLod = lods.join(' ') + '  gpu ms ' + JSON.stringify(V.stats().gpuMs);
}

// 5. calls with things left out
{
  const tries = {};
  const t = (name, f) => { try { const r = f(); tries[name] = r && typeof r === 'object' && 'ok' in r ? 'ok ' + r.ok + (r.note ? ' note: ' + r.note : '') : String(r && r.length !== undefined ? 'array ' + r.length : r); } catch (err) { tries[name] = 'THREW ' + err.message; } };
  t('draw()', () => V.draw());
  t('draw({})', () => V.draw({}));
  t('no levels', () => V.draw({ panes: [{ kind: 'm', rect: [0, 0, 600, 450] }] }));
  t('no colours', () => V.draw({ panes: [{ kind: 'j', rect: [0, 0, 600, 450] }], levels: [{ k: 2, alpha: 1 }] }));
  t('four levels', () => V.draw({ panes: [{ kind: 'j', rect: [0, 0, 600, 450] }], levels: [{ k: 2, alpha: 1 }, { k: 1, alpha: 0.5, tint: 1 }, { k: 3, alpha: 0.5 }, { k: 4, alpha: 0.5 }], c: [-1, 0, 0] }));
  t('alpha 0', () => V.draw({ panes: [{ kind: 'j', rect: [0, 0, 600, 450] }], levels: [{ k: 2, alpha: 0 }] }));
  t('slice()', () => V.slice('m', [0, 0, 0]));
  t('slice size 5', () => V.slice('j', [-1, 0, 0], { size: 5, half: 2, z: 0, maxK: 4 }).join(','));
  t('slice centres', () => V.slice('j', [-1, 0, 0], { size: 4, half: 2, z: 0, maxK: 4, centres: true }).join(','));
  t('out no maxK', () => M.out([0, 0, 0], 'j', [-1, 0, 0]));
  res.tries = tries;
}

// 6. the graphics context is taken away and given back
{
  const lose = gl.getExtension('WEBGL_lose_context');
  const o = T.one('j', [-1, 0, 0], T.levelsAt(5));
  V.draw(o);
  const lost = new Promise(f => V.canvas.addEventListener('webglcontextlost', f, { once: true }));
  lose.loseContext(); await within(lost, 4000, 'the context to be lost');
  // the browser only allows the context back once the "lost" event has been fully handed out: ask in a later task
  await new Promise(f => setTimeout(f, 60));
  const during = V.draw(o);
  const back = new Promise(f => V.canvas.addEventListener('webglcontextrestored', f, { once: true }));
  lose.restoreContext(); await within(back, 4000, 'the context to come back'); await frame();
  const g = grab();
  let n = 0; for (let y = 0; y < g.h; y += 4) for (let x = 0; x < g.w; x += 4) if (notBg(g, x, y)) n++;
  res.lost = { during: 'ok ' + during.ok + ' note: ' + during.note, afterBack: 'drawn again by itself, ' + n + ' of ' + Math.ceil(g.h / 4) * Math.ceil(g.w / 4) + ' probed pixels are not background', okNow: M.ok() };
}

// 7. a second view beside the first, then dispose
{
  const v2 = M.make(), box2 = document.createElement('div');
  box2.style.cssText = 'position:fixed;left:620px;top:0;width:300px;height:225px;z-index:99999';
  document.body.appendChild(box2); v2.canvas.style.cssText = 'width:100%;height:100%;display:block'; box2.appendChild(v2.canvas);
  const r = v2.draw({ panes: [{ kind: 'm', rect: [0, 0, 300, 225] }], levels: T.levelsAt(4), colours: T.cols() });
  v2.dispose();
  const after = v2.draw({ panes: [{ kind: 'm', rect: [0, 0, 300, 225] }], levels: T.levelsAt(4) });
  res.second = { drew: r.ok, canvasStillInPage: !!v2.canvas.parentNode, drawAfterDispose: 'ok ' + after.ok + ' note: ' + after.note, sliceAfterDispose: String(v2.slice('m', [0, 0, 0], { size: 8 })) };
  box2.remove();
  // the first view still works
  res.second.firstStillDraws = V.draw(T.one('m', [0, 0, 0], T.levelsAt(4))).ok;
}
return res;

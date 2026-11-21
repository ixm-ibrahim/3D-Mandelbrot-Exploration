// Tracing hooks for the renderer's schedule. Installed once per page as window.__t.
// Every job (a preview or a band) is logged at its fence: start time, rows wanted, kind (from the status line),
// then the polls of its fence, the GPU's own count of its cost when one is read, and every picture put on the canvas.
if (!window.__t) window.__t = (() => {
  const L = window.squaringLab, R = L.R, gl = document.getElementById('view').getContext('webgl2');
  const T = { on: false, ev: [], oraf: window.requestAnimationFrame.bind(window) };
  const log = (k, a, b, c) => { if (T.on) T.ev.push([performance.now(), k, a, b, c]); };
  const of = gl.fenceSync.bind(gl), oq = gl.getQueryParameter.bind(gl), ow = gl.clientWaitSync.bind(gl), od = gl.drawArrays.bind(gl), ov = gl.viewport.bind(gl), os = gl.scissor.bind(gl);
  let vp = [0, 0], sc = 0, fb = null;
  const obf = gl.bindFramebuffer.bind(gl);
  gl.bindFramebuffer = (t, f) => { fb = f; return obf(t, f); };
  gl.viewport = (x, y, w, h) => { vp = [w, h]; return ov(x, y, w, h); };
  gl.scissor = (x, y, w, h) => { sc = h; return os(x, y, w, h); };
  gl.fenceSync = (...a) => { log('job', document.getElementById('status').textContent.slice(0, 7), sc, vp.join('x')); return of(...a); };
  gl.getQueryParameter = (q, p) => { const v = oq(q, p); if (p === gl.QUERY_RESULT) log('gpu', v / 1e6); return v; };
  gl.clientWaitSync = (...a) => { const r = ow(...a); log('poll', r === gl.TIMEOUT_EXPIRED ? 0 : 1); return r; };
  gl.drawArrays = (...a) => { od(...a); if (T.on && fb === null) { const e = [performance.now(), 'blit', '', 0, 0]; T.ev.push(e); Promise.resolve().then(() => { e[2] = R.shown; }); } };
  T.start = () => { T.ev = []; T.on = true; T.t0 = performance.now(); };
  T.stop = () => { T.on = false; return T.ev.map(e => [Math.round((e[0] - T.t0) * 10) / 10, e[1], typeof e[2] === 'number' ? Math.round(e[2] * 100) / 100 : e[2], e[3], e[4]]); };
  T.frames = n => new Promise(res => { const f = () => (--n > 0 ? T.oraf(f) : res()); T.oraf(f); });
  T.sleep = ms => new Promise(res => setTimeout(res, ms));
  T.idle = cap => new Promise(res => { const t0 = performance.now(); const f = () => { if (L.renderIdle()) res(performance.now() - t0); else if (performance.now() - t0 > cap) res(null); else T.oraf(f); }; T.oraf(f); });
  // a simulated drag: every animation frame the camera turns (or the 2D picture slides) and touch() is called
  T.drag = (ms, flat) => new Promise(res => { const t0 = performance.now(); let n = 0, last = t0, worst = 0;
    const f = () => { const now = performance.now(); worst = Math.max(worst, now - last); last = now; n++;
      if (now - t0 < ms) { if (flat) L.S.v2.x += L.S.v2.h * 0.004 * Math.cos((now - t0) / 300); else L.cam.yaw += 0.01; L.touch(); T.oraf(f); } else res({ frames: n, worstGap: Math.round(worst * 10) / 10, end: now }); };
    T.oraf(f); });
  T.frac = () => { const b = document.getElementById('drawProgress'); if (!b || b.hidden) return -1; const m = /scaleX\(([0-9.]+)\)/.exec(b.firstChild.style.transform || ''); return m ? +m[1] : 0; };
  // summary of a trace: per job the wait between its fence and the poll that saw it finished, and its GPU cost
  T.sum = ev => { const jobs = []; let cur = null;
    for (const e of ev) { if (e[1] === 'job') { cur = { t: e[0], kind: e[2], rows: e[3], vp: e[4], polls: 0, seen: null, gpu: null }; jobs.push(cur); }
      else if (e[1] === 'poll' && cur && cur.seen === null) { cur.polls++; if (e[2] === 1) cur.seen = Math.round((e[0] - cur.t) * 10) / 10; }
      else if (e[1] === 'gpu' && cur) { const j = jobs.filter(x => x.seen !== null && x.gpu === null).pop(); if (j) j.gpu = e[2]; } }
    return jobs; };
  return T;
})();
return 'trace ready';

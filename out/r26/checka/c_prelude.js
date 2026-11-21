// Checker "arithmetic": helpers put in front of every piece of JavaScript I run in the page (see clab.py).
const LAB = window.squaringLab, L = LAB.learn, S = LAB.S, $ = id => document.getElementById(id);
const sleep = ms => new Promise(r => setTimeout(r, ms));
const frame = () => new Promise(r => requestAnimationFrame(() => r()));
const fail = m => { throw new Error(m); };
const b64 = u => { let s = ''; for (let i = 0; i < u.length; i += 8192) s += String.fromCharCode.apply(null, u.subarray(i, i + 8192)); return btoa(s); };
const go = () => { LAB.syncControls(); LAB.refresh(false); LAB.touch(); };
const AP = () => LAB.APPROACHES[S.approach];
const pickAp = async id => { if (AP().id !== id) { $('ap-' + id).click(); await sleep(200); } if (AP().id !== id) fail('could not choose ' + id); return AP().name; };
const learnOn = async () => { if (!L.on) { $('mode-l').click(); await sleep(250); } };
const shapeOn = async o => { await learnOn(); return L.shape.set(Object.assign({ on: true }, o || {})); };
const setRule = (n, abs, flip) => { if (n !== undefined) S.n = n; if (abs) S.abs = abs.slice(); if (flip) S.flip = flip.slice(); go(); };
const dials = (id, o) => { Object.assign(S.param[id], o); go(); };
const dialsBack = id => { const a = LAB.APPROACHES.find(x => x.id === id); for (const s of a.params || []) if (s.key !== undefined) S.param[id][s.key] = s.def; go(); };
const ptr = (el, type, x, y, o) => { const r = el.getBoundingClientRect(); el.dispatchEvent(new PointerEvent(type, Object.assign({ bubbles: true, cancelable: true, pointerId: 7, pointerType: 'mouse', button: 0, buttons: type === 'pointerup' ? 0 : 1, clientX: r.left + x, clientY: r.top + y }, o || {}))); };
// a hash of a canvas's pixels as the browser holds them (for "did the picture change")
const hashOf = cv => { const u = cv.toDataURL('image/png'); let h = 2166136261; for (let i = 0; i < u.length; i++) { h ^= u.charCodeAt(i); h = Math.imul(h, 16777619); } return (h >>> 0).toString(16) + ':' + u.length; };

// ---------- my own orbit in space, written from the lab's shader text (GL_ORBIT, orbitDE and f) and driven with
// the lab's MATH and CARRY. Nothing of 68-learn-shape3d.js is used here.
//   a Julia orbit starts at zmap(p, c) (only "Quaternions, 4D" has a zmap), a Mandelbrot orbit at 0;
//   the constant is cmap(c) or cmap(p) (only "two planes" and "Quaternions, 4D" have a cmap that does anything);
//   a step: the modifiers (|x| |y| |z| first, then the flips of y and z), what the orbit carries is stepped once,
//   the power, plus c.
// The fold, from the shader's aprFold (not from the lab's foldk):
const ckFold = (v, k) => {
  k = Math.max(k, 2);
  const rho = Math.hypot(v[1], v[2]);
  if (rho < 1e-20) return v.slice();
  const w = Math.PI / k, psi = Math.atan2(v[2], v[1]), s = psi < 0 ? -1 : 1, a = Math.abs(psi);
  const j = Math.floor(a / w + 0.5), d = a - j * w;
  const fm = (x, y) => x - y * Math.floor(x / y);
  let a2;
  if (2 * j < k - 0.5 || (Math.abs(2 * j - k) < 0.5 && d < 0)) a2 = fm(j, 2) < 0.5 ? d : -d;
  else a2 = Math.PI + (fm(k - j, 2) < 0.5 ? d : -d);
  a2 *= s;
  return [v[0], rho * Math.cos(a2), rho * Math.sin(a2)];
};
// "Quaternions, 4D", from the shader's q4E, q4C, cmap and zmap. uA = (w, tilt in degrees, cw).
const ckQ4 = (() => {
  const cs = deg => { const a = deg * Math.PI / 180, c = Math.cos(a), s = Math.sin(a); return [Math.abs(c) < 1e-6 ? 0 : c, Math.abs(s) < 1e-6 ? 0 : s]; };
  const E = (P, A) => { const t = cs(A[1]); return [P[0] * t[0] - A[0] * t[1], P[1], P[2], P[0] * t[1] + A[0] * t[0]]; };
  const C = (c, A, jul) => (jul ? [c[0], c[1], c[2], A[2]] : E(c, A));
  const dir = (y, z) => { const l = Math.hypot(y, z); return l > 1e-12 ? [y / l, z / l] : [1, 0]; };
  return {
    cmap(c, A, jul) { const k = C(c, A, jul); if (k[3] === 0) return [k[0], k[1], k[2]]; const d = dir(k[1], k[2]), m = Math.hypot(k[1], k[2], k[3]); return [k[0], m * d[0], m * d[1]]; },
    zmap(P, c, A) {
      const e = E(P, A), k = C(c, A, true);
      if (k[3] === 0 && A[0] === 0 && A[1] === 0) return [e[0], e[1], e[2]];
      const m = Math.hypot(k[1], k[2], k[3]), u = m > 1e-12 ? [k[1] / m, k[2] / m, k[3] / m] : [1, 0, 0], d = dir(k[1], k[2]);
      const b = e[1] * u[0] + e[2] * u[1] + e[3] * u[2], mu = Math.hypot(e[1] - b * u[0], e[2] - b * u[1], e[3] - b * u[2]);
      return [e[0], b * d[0] - mu * d[1], b * d[1] + mu * d[0]];
    },
  };
})();
// The step at which p is thrown out (0: starts outside the big ball; K + 1: still in after K steps).
const ckOut3 = (p, kind, c, K) => {
  const a = AP(), id = a.id, q = S.param[id], n = S.n, jul = kind === 'j', A = LAB.S ? (() => { const v = [0, 0, 0, 0]; (a.params || []).filter(s => s.key !== undefined).forEach((s, i) => { if (i < 4) v[i] = +q[s.key]; }); return v; })() : null;
  const far = v => !(Math.sqrt(v[0] * v[0] + v[1] * v[1] + v[2] * v[2]) <= 2);
  if (far(p)) return 0;
  let z = [0, 0, 0], cc;
  if (jul) {
    z = id === 'quat4' ? ckQ4.zmap(p, c, A) : p.slice();
    cc = id === 'fold' ? ckFold(c, A[0]) : id === 'quat4' ? ckQ4.cmap(c, A, true) : c.slice();
    if (far(z)) return 0;
  } else cc = id === 'fold' ? ckFold(p, A[0]) : id === 'quat4' ? ckQ4.cmap(p, A, false) : p.slice();
  const car = LAB.CARRY && LAB.CARRY[id] ? LAB.CARRY[id] : null;
  let st = car ? car.start(q) : null;
  for (let k = 1; k <= K; k++) {
    const v = [S.abs[0] ? Math.abs(z[0]) : z[0], (S.abs[1] ? Math.abs(z[1]) : z[1]) * (S.flip[0] ? -1 : 1), (S.abs[2] ? Math.abs(z[2]) : z[2]) * (S.flip[1] ? -1 : 1)];
    let w;
    if (car) { st = car.step(st, v, cc, q); w = car.pw(st, v, n); } else w = LAB.MATH[id](v, n, q, cc);
    z = [w[0] + cc[0], w[1] + cc[1], w[2] + cc[2]];
    if (far(z)) return k;
  }
  return K + 1;
};
// the point slice() asks about for a row and a column (outer points ON the edge of the square, row 0 at y = +half),
// worked out here, not taken from the module's slicePoint
const ckPoint = (row, col, size, half, z) => { const d = 2 * half / (size - 1); return [col * d - half, half - row * d, z]; };
// my view of the 3D module, made once
const ckView = () => (window.__ckv || (window.__ckv = LAB.learnShape3d.make()));

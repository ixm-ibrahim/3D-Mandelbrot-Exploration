// ---------- measuring an approach's power rule against the flat case
const powerF = () => { const a = ap(), q = apP(), n = S.n; return v => MATH[a.id](v, n, q); };
function fib(i, N) {
  const z = 1 - (2 * i + 1) / N, r = Math.sqrt(Math.max(0, 1 - z * z)), a = i * PI * (3 - Math.sqrt(5));
  return [r * Math.cos(a), r * Math.sin(a), z];
}
function tangent(d) {
  const e1 = norm(cross(d, Math.abs(d[0]) < 0.8 ? [1, 0, 0] : [0, 1, 0]));
  return [e1, cross(d, e1)];
}
function symEig3(a11, a12, a13, a22, a23, a33) { // eigenvalues of a symmetric 3x3, largest first
  const p1 = a12 * a12 + a13 * a13 + a23 * a23, q = (a11 + a22 + a33) / 3;
  const p2 = (a11 - q) ** 2 + (a22 - q) ** 2 + (a33 - q) ** 2 + 2 * p1, p = Math.sqrt(p2 / 6);
  if (p < 1e-14) return [q, q, q];
  const b11 = (a11 - q) / p, b22 = (a22 - q) / p, b33 = (a33 - q) / p, b12 = a12 / p, b13 = a13 / p, b23 = a23 / p;
  const det = b11 * (b22 * b33 - b23 * b23) - b12 * (b12 * b33 - b23 * b13) + b13 * (b12 * b23 - b22 * b13);
  const phi = Math.acos(clamp(det / 2, -1, 1)) / 3;
  const e1 = q + 2 * p * Math.cos(phi), e3 = q + 2 * p * Math.cos(phi + 2 * PI / 3);
  return [e1, 3 * q - e1 - e3, e3];
}
function measure(F, n) {
  const g = v => norm(F(v));
  const N = 6000, h = 1e-4, tear = 400 * Math.max(1, Math.abs(n));
  let lmin = Infinity, lmax = 0, smin = Infinity, smax = 0, round = 0, rev = 0, deg = 0, sheets = 0, used = 0;
  for (let i = 0; i < N; i++) {
    const d = fib(i, N), L = len(F(d));
    lmin = Math.min(lmin, L); lmax = Math.max(lmax, L);
    // central differences at two step sizes; if they disagree the sample straddles a jump and is skipped
    const diff = (f, e, hh) => scl(sub(f(add(d, scl(e, hh))), f(sub(d, scl(e, hh)))), 0.5 / hh);
    const slope = (f, e) => { const a = diff(f, e, h), b = diff(f, e, h / 8); return len(sub(a, b)) > 0.25 * (len(b) + 0.05) ? null : a; };
    const J = [[1, 0, 0], [0, 1, 0], [0, 0, 1]].map(e => slope(F, e));
    const [e1, e2] = tangent(d);
    const g1 = slope(g, e1), g2 = slope(g, e2);
    if (J.includes(null) || !g1 || !g2 || len(J[0]) > tear || len(J[1]) > tear || len(J[2]) > tear) continue;
    used++;
    if (dot(J[0], cross(J[1], J[2])) < 0) rev++;
    const ev = symEig3(dot(J[0], J[0]), dot(J[0], J[1]), dot(J[0], J[2]), dot(J[1], J[1]), dot(J[1], J[2]), dot(J[2], J[2]));
    const s1 = Math.sqrt(Math.max(ev[0], 0)), s3 = Math.sqrt(Math.max(ev[2], 0));
    smin = Math.min(smin, s3); smax = Math.max(smax, s1);
    round += s1 > 0 ? s3 / s1 : 0;
    const w = dot(g(d), cross(g1, g2)); // signed area scale of the direction map
    deg += w; sheets += Math.abs(w);
  }
  used = Math.max(used, 1);
  let planeErr = 0; // does the plane z = 0 follow complex z^n?
  for (let i = 0; i < 48; i++) {
    const a = 0.37 + i * 2.39996, r = 0.25 + 1.2 * ((i * 0.618034) % 1), x = r * Math.cos(a), y = r * Math.sin(a);
    const out = F([x, y, 0]), R = Math.pow(r, n), th = Math.atan2(y, x) * n;
    planeErr = Math.max(planeErr, len(sub(out, [R * Math.cos(th), R * Math.sin(th), 0])) / (1 + R));
  }
  return { lmin, lmax, smin, smax, round: round / used, rev: rev / used, deg: deg / used, sheets: sheets / used, plane: planeErr < 1e-9 };
}
const fmtN = n => (Math.abs(n - Math.round(n)) < 1e-9 ? String(Math.round(n)) : String(+n.toFixed(2)));
const tidy = x => { const r = Math.round(x); return Math.abs(x - r) < 0.07 ? String(r) : x.toFixed(1); };
const PROPS = [['len', 'Length goes to its nth power'], ['round', 'Keeps shapes'], ['wrap', 'Wraps without folding'], ['crush', 'Crushes only the origin'], ['smooth', 'One smooth formula'], ['slice', 'Contains the flat set']];
const PILL = { ok: 'holds', part: 'partly', no: 'fails' };
function buildCard() {
  $('card').innerHTML = '<div class="row head label"><div>Property</div><div>In the plane</div><div id="ruleHead">In space</div></div>' +
    PROPS.map(([id, title]) => `<div class="row"><div class="prop">${title}</div>` +
      `<div class="cell"><span class="k label">In the plane</span><span id="p-${id}"></span></div>` +
      `<div class="cell"><span class="k label k3">In space</span><span class="pill" id="b-${id}"></span><span id="s-${id}"></span></div></div>`).join('');
}
function setCell(id, st, text) {
  const b = $('b-' + id);
  b.className = 'pill ' + st; b.textContent = PILL[st];
  $('s-' + id).textContent = text;
}
function updateCard() {
  const a = ap(), q = apP(), n = S.n, N = fmtN(n), m = measure(powerF(), n);
  $('ruleHead').textContent = a.name;
  document.querySelectorAll('.k3').forEach(el => { el.textContent = a.name; });
  $('p-len').textContent = '|zⁿ| = |z|ⁿ for every z.';
  $('p-round').textContent = `Roundness 100%. A tiny circle lands as a circle, stretched ${N}× in every direction at |z| = 1.`;
  $('p-wrap').textContent = `Wraps the circle of directions ${N} times and never reverses it.`;
  $('p-crush').textContent = 'Only the origin is crushed. That one critical point is why the orbit of 0 decides everything.';
  $('p-smooth').textContent = 'A polynomial. For n = 2: (x² − y², 2xy).';
  $('p-slice').textContent = 'It is the flat set.';
  const lenOk = Math.abs(m.lmin - 1) < 1e-6 && Math.abs(m.lmax - 1) < 1e-6;
  setCell('len', lenOk ? 'ok' : 'no', lenOk ? '|vⁿ| = |v|ⁿ for every v.' : `For |v| = 1 the result has length anywhere from ${m.lmin.toFixed(2)} to ${m.lmax.toFixed(2)}.`);
  const dec = x => (Math.abs(x - Math.round(x)) < 0.02 ? String(Math.round(x)) : x.toFixed(1));
  const lo = m.smin < 0.03 * n ? '0' : dec(m.smin), hi = m.smax > 30 * n ? 'no upper limit' : dec(m.smax) + '×';
  setCell('round', m.round > 0.999 ? 'ok' : 'no', `Roundness ${Math.round(m.round * 100)}%. At |v| = 1 the stretch runs from ${lo}× to ${hi}, where the plane gives ${N}× throughout. ${a.roundNote}`);
  const wrapOk = m.rev < 0.005 && Math.abs(m.deg - m.sheets) < 0.05;
  setCell('wrap', wrapOk ? 'ok' : 'no', wrapOk
    ? `Wraps the sphere of directions ${tidy(m.sheets)} times and never reverses it.`
    : `Covers the sphere of directions ${tidy(m.sheets)} times over, but ${Math.round(m.rev * 100)}% of directions land mirror-reversed. Counted with sign, the net wrap is ${tidy(Math.abs(m.deg) < 0.05 ? 0 : m.deg)}.`);
  setCell('crush', ...a.crush(q));
  setCell('smooth', ...a.smooth(q));
  setCell('slice', m.plane ? 'ok' : 'no', a.slice(m.plane, q));
}

// ---------- the step figures
function prep(cv) {
  const dpr = Math.min(window.devicePixelRatio || 1, 2), w = cv.clientWidth, h = cv.clientHeight;
  if (cv.width !== Math.round(w * dpr) || cv.height !== Math.round(h * dpr)) { cv.width = Math.round(w * dpr); cv.height = Math.round(h * dpr); }
  const ctx = cv.getContext('2d');
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0); ctx.clearRect(0, 0, w, h);
  ctx.lineJoin = 'round'; ctx.lineCap = 'round';
  return { ctx, w, h };
}
const hueCol = hue => `hsl(${hue.toFixed(0)} 62% ${theme.dark ? 64 : 40}%)`;
function arrow(ctx, w, h) {
  ctx.strokeStyle = theme.ink2; ctx.globalAlpha = 1; ctx.lineWidth = 1.25; ctx.setLineDash([]);
  ctx.beginPath(); ctx.moveTo(w / 2 - 9, h / 2); ctx.lineTo(w / 2 + 9, h / 2);
  ctx.moveTo(w / 2 + 4, h / 2 - 4); ctx.lineTo(w / 2 + 9, h / 2); ctx.lineTo(w / 2 + 4, h / 2 + 4); ctx.stroke();
}
function drawStep2d() {
  const { ctx, w, h } = prep($('step2d')), n = S.n, K = 7, rho = Math.min(0.16, 0.34 / Math.max(1, Math.abs(n))), M = 48;
  const R = Math.min(w / 4, h / 2) / 1.5, cy = h / 2;
  [w * 0.25, w * 0.75].forEach((cx, side) => {
    ctx.setLineDash([]); ctx.globalAlpha = 1; ctx.lineWidth = 1; ctx.strokeStyle = theme.line;
    ctx.beginPath(); ctx.arc(cx, cy, R, 0, 2 * PI); ctx.moveTo(cx, cy); ctx.lineTo(cx + R, cy); ctx.stroke();
    ctx.lineWidth = 1.6;
    for (let k = 0; k < K; k++) {
      const th = 0.45 + 2 * PI * k / K;
      ctx.strokeStyle = hueCol(th * 180 / PI);
      ctx.beginPath();
      for (let j = 0; j <= M; j++) {
        const t = 2 * PI * j / M, re = Math.cos(th) + rho * Math.cos(t), im = Math.sin(th) + rho * Math.sin(t);
        let X = re, Y = im;
        if (side === 1) { // z^n, with the angle unwrapped around the circle's own centre so it stays continuous
          const r = Math.pow(Math.hypot(re, im), n), a = (th + Math.atan2(im * Math.cos(th) - re * Math.sin(th), re * Math.cos(th) + im * Math.sin(th))) * n;
          X = r * Math.cos(a); Y = r * Math.sin(a);
        }
        if (j === 0) ctx.moveTo(cx + R * X, cy - R * Y); else ctx.lineTo(cx + R * X, cy - R * Y);
      }
      ctx.stroke();
    }
  });
  arrow(ctx, w, h);
}
let stepCurves = [];
function ringAround(c, ang, M) {
  const [e1, e2] = tangent(c), pts = [];
  for (let j = 0; j <= M; j++) {
    const t = 2 * PI * j / M;
    pts.push(norm(add(scl(c, Math.cos(ang)), scl(add(scl(e1, Math.cos(t)), scl(e2, Math.sin(t))), Math.sin(ang)))));
  }
  return pts;
}
function buildStep3d() {
  const P = powerF(), F = v => norm(P(v));
  const N = 34, rho = Math.min(0.11, 0.24 / Math.max(1, Math.abs(S.n))), h = 1e-4;
  stepCurves = [];
  for (let i = 0; i < N; i++) {
    const c = fib(i, N), [e1, e2] = tangent(c), before = ringAround(c, rho, 44);
    const g1 = sub(F(add(c, scl(e1, h))), F(sub(c, scl(e1, h)))), g2 = sub(F(add(c, scl(e2, h))), F(sub(c, scl(e2, h))));
    stepCurves.push({ hue: (Math.atan2(c[1], c[0]) * 180 / PI + 360) % 360, before, after: before.map(F), flipped: dot(F(c), cross(g1, g2)) < 0 });
  }
}
function drawStep3d() {
  const { ctx, w, h } = prep($('step3d')), b = basis(), axis = ap().axis(apP());
  const R = Math.min(w / 4, h / 2) / 1.2, cy = h / 2;
  const P = (cx, p) => [cx + R * dot(p, b.right), cy - R * dot(p, b.up), -dot(p, b.f)];
  const poly = (cx, pts, color, width, dash) => {
    ctx.strokeStyle = color; ctx.lineWidth = width; ctx.setLineDash(dash || []);
    for (const front of [false, true]) {
      ctx.globalAlpha = front ? 1 : 0.2;
      ctx.beginPath();
      for (let j = 0; j + 1 < pts.length; j++) {
        if (len(sub(pts[j], pts[j + 1])) > 0.8) continue; // do not draw across a tear
        const a = P(cx, pts[j]), c = P(cx, pts[j + 1]);
        if ((a[2] + c[2] >= 0) !== front) continue;
        ctx.moveTo(a[0], a[1]); ctx.lineTo(c[0], c[1]);
      }
      ctx.stroke();
    }
  };
  const great = k => { const pts = []; for (let j = 0; j <= 64; j++) { const t = 2 * PI * j / 64, p = [0, 0, 0]; p[k] = Math.cos(t); p[(k + 1) % 3] = Math.sin(t); pts.push(p); } return pts; };
  [w * 0.25, w * 0.75].forEach((cx, side) => {
    ctx.globalAlpha = 1; ctx.setLineDash([]); ctx.lineWidth = 1; ctx.strokeStyle = theme.line;
    ctx.beginPath(); ctx.arc(cx, cy, R, 0, 2 * PI); ctx.stroke();
    for (let k = 0; k < 3; k++) poly(cx, great(k), theme.line, 1);
    for (const s of [1, -1]) { // the axis this approach singles out
      const a = P(cx, scl(axis, s)), c = P(cx, scl(axis, s * 1.16));
      ctx.globalAlpha = a[2] >= 0 ? 1 : 0.35; ctx.strokeStyle = theme.brass; ctx.lineWidth = 2; ctx.setLineDash([]);
      ctx.beginPath(); ctx.moveTo(a[0], a[1]); ctx.lineTo(c[0], c[1]); ctx.stroke();
    }
    for (const cv of stepCurves) poly(cx, side ? cv.after : cv.before, hueCol(cv.hue), 1.6, side && cv.flipped ? [4, 3] : null);
  });
  arrow(ctx, w, h);
}

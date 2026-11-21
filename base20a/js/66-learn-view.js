// ---------- Learn: one step of z -> z^n + c, played move by move on the stage (round 13, the view).
// The moves themselves come from 65-learn-steps.js (learnPlan, learnRun). This file draws them: a second canvas
// on the stage (Canvas 2D, no WebGL), a transport under the stage, and a panel in the controls column.
// Learn is a fourth choice under Show. S.mode keeps its value; S.learn = true stands beside it, and while it is
// set touch() calls learnTouch() and leaves the solid alone (see 40-render.js).
// The two points each space opens with (unused coordinates stay 0). On the line and on the page they are chosen
// so that Next step can be pressed many times: the point wanders and then settles, it does not run away.
const LEARN_V_START = {
  1: { z: [-1.2, 0, 0], c: [-0.6, 0, 0] },
  2: { z: [0.7, 0.4, 0], c: [-0.4, 0.3, 0] },
  3: { z: [0.6, 0.3, 0.4], c: [-0.3, 0.2, 0.1] },
};
const LEARN_V_VIEWS = {            // one view per kind of picture: flat line, flat page, tipped line, tipped page, space
  f1: { zoom: 1 }, f2: { zoom: 1 },
  h1: { yaw: -0.42, pitch: 0.82, zoom: 1 }, h2: { yaw: -0.5, pitch: 0.55, zoom: 1 }, s3: { yaw: -0.62, pitch: 0.4, zoom: 1 },
};
const LEARN_V_SECONDS = { slow: 3.6, normal: 2, fast: 1 };   // how long one move plays
const LEARN_V_NOTICE = {
  1: 'On a line a number leans one of two ways from the positive side: 0° or 180°. Doubling 180° gives 360°, which is 0° again. That is why a negative number times itself is positive. To get there the point swings through a direction the line does not have.',
  2: 'On a page every lean from 0° to 360° exists, and the swing fits inside the page. The hinge of the turn is the one line the page does not have, the z-axis. Going from a line to a page is the big step: two leans become all of them, and the picture goes from a plain stretch of the line (from −2 to ¼) to the Mandelbrot set.',
  3: 'In space a point still leans away from the x-axis by one angle. What is new is the direction it leans in, a second angle. A turn of space needs three numbers (two to aim its hinge, one for how far), and a point supplies only two. Each approach fills in the missing one in its own way, which is why there are several approaches and no single right one. Watch the hinge: under “Quaternion square (Lathe)” it is a different line for every point, and it is the z-axis exactly when the point lies in the flat plane.',
};
const LEARN_V_HIDDEN = {
  '1on': 'The line is seen at a slant, lying in the faint sheet the number swings through. The line itself does not have that direction. The dashed line standing on the sheet is the hinge of the swing.',
  '1off': 'This is all the line can show: the number slides to 0 and comes out on the other side. Tick the box to see the swing that does it.',
  '2on': 'The page is seen at a slant. The dashed line standing on it is the z-axis, the hinge of the turn. Drag the picture to look from another side.',
  '2off': 'The turn stays inside the page. Its hinge is the z-axis, which comes straight out of the page at the centre. Tick the box to see it standing there.',
  '3': 'In space no direction is hidden: the hinge of a turn is a line you can see. The ladder still goes on one rung. A swing on a line turns about a point. So does a turn of a page, and seen from space that point is a line, the z-axis. A turn of space is about a line, and seen from 4D that line is a whole sheet: the hinge line together with the fourth direction. So the fourth direction alone does not say how to turn. The line that goes with it has to be chosen, and each approach chooses it in its own way.',
};
const LEARN = {
  on: false,
  follow: 'point',               // 'point': one point, move by move (this file) | 'shape': a whole shape, step by step (67-learn-shape.js draws and paints)
  space: 2,                      // 1 a line, 2 a page, 3 space
  pts: null,                     // pts[space] = { z, c }: where the first step starts, and the point c
  show: 'circle',                // 'point' | 'circle' | 'all': the companions
  hidden: { 1: true, 2: false }, // "Show the hidden direction", for the line and for the page
  k: 0,                          // whole steps already taken: the step on show starts at orbit[k]
  pos: 0,                        // where in the step: 0 .. number of moves (2.5 = half way through the third move)
  endSide: false,                // at a whole pos: stand at the end of the move before it, not at the start of the next
  playing: false, until: null, dwell: 0, last: 0, raf: 0,
  speed: 'normal',
  view: null,                    // view[kind] = { yaw, pitch, zoom }
  stale: true,                   // the plan has to be worked out again
  frame: null,                   // what the picture is framed on: { tight, roomy }, each { ctr, hx, hy, rr, reach }
  fit: 1, fitHold: false,        // the radius of the roomy frame; the frame is held still while a point is dragged
  cache: null, col: null, proj: null, w: 0, h: 0,
  ptr: new Map(), drag: null, pinch: null,
  el: {}, dials: null, sig: '',
};
const learnVCopy = o => JSON.parse(JSON.stringify(o));
const learnVFinite = v => !!v && v.length === 3 && v.every(x => typeof x === 'number' && isFinite(x));
const learnVNum = (x, d = 2) => { const t = (+x).toFixed(d); return (/^-0\.?0*$/.test(t) ? t.slice(1) : t).replace('-', '−'); };
const learnVDeg = a => learnVNum(a * 180 / PI, 0) + '°';
const learnVXyz = (v, sp = LEARN.space) => (sp === 1 ? learnVNum(v[0]) : '(' + v.slice(0, sp).map(x => learnVNum(x)).join(', ') + ')');
const learnVKey = () => (LEARN.space === 3 ? 's3' : (LEARN.hidden[LEARN.space] ? 'h' : 'f') + LEARN.space);
const learnVIsCam = () => { const k = learnVKey(); return k !== 'f1' && k !== 'f2'; };

// What a move turns the point a about, and the flat sheet the point travels in: the hinge (or null), the sheet as
// the move gives it (or null), two directions at right angles that span it, its centre (on the hinge) and how far
// the point is from that centre.
function learnVSheet(m, a) {
  let hinge = null, sheet = null, fr = null;
  try { hinge = m.hinge ? m.hinge(a) : null; sheet = m.sheet ? m.sheet(a) : null; } catch (e) { hinge = sheet = null; }
  if (hinge && !(learnVFinite(hinge) && len(hinge) > 1e-9)) hinge = null;
  if (sheet && !(sheet.length === 2 && learnVFinite(sheet[0]) && learnVFinite(sheet[1]))) sheet = null;
  if (sheet) { const u = norm(sheet[0]), w0 = sub(sheet[1], scl(u, dot(u, sheet[1]))); if (len(w0) > 1e-9) fr = [u, norm(w0)]; }
  if (!fr && hinge) {
    const hn = norm(hinge); let r0 = sub([1, 0, 0], scl(hn, hn[0]));
    if (len(r0) < 1e-6) r0 = sub([0, 1, 0], scl(hn, hn[1]));
    r0 = norm(r0); fr = [r0, cross(hn, r0)];
  }
  let ctr = [0, 0, 0], rs = len(a);
  if (fr) { const iu = dot(a, fr[0]), iw = dot(a, fr[1]); ctr = sub(a, add(scl(fr[0], iu), scl(fr[1], iw))); rs = Math.hypot(iu, iw); }
  return { hinge: hinge ? norm(hinge) : null, sheet, fr, ctr, rs };
}
// ---------- the plan: the moves of the step on show, and everything the picture needs from them
function learnVBuild() {
  const L = LEARN, sp = L.space, P = L.pts[sp], id = ap().id;
  L.stale = false;
  let plan = null, fault = '';
  // carry: what the orbit carries when the step begins, for an entry whose orbit carries something (round 22, see
  // learnPlan); left out for the first step and for every other entry.
  const planFor = carry => learnPlan({ space: sp, id, params: S.param[id], n: S.n, c: P.c.slice(), abs: S.abs.slice(), flip: S.flip.slice(), carry });
  if (typeof learnPlan !== 'function') fault = 'The moves are missing from this copy of the page.';
  else {
    try { plan = planFor(undefined); }
    catch (e) { fault = 'The moves could not be worked out for these settings.'; console.warn('learnPlan failed', e); }
  }
  let moves = plan && Array.isArray(plan.moves) ? plan.moves : [];
  const at = (m, v, t) => { try { const p = m.at(v, t); return learnVFinite(p) ? p : v.slice(); } catch (e) { return v.slice(); } };
  const run = v => { const out = [v.slice()]; for (const m of moves) out.push(at(m, out[out.length - 1], 1)); return out; };
  // the steps taken so far, worked out again from the first point (the approach, the power or c may have changed)
  const orbit = [P.z.slice()];
  while (orbit.length <= L.k && moves.length) {
    const a = orbit[orbit.length - 1], r = run(a), e = r[r.length - 1];
    if (len(e) > 8) break;
    orbit.push(e);
    // An entry whose orbit carries something: the step after this one gets moves of its own, made with what the
    // orbit carries once this step is done. (Every other entry has one plan for every step, as before.)
    if (plan.carry) {
      try { plan = planFor(plan.carry(a)); moves = Array.isArray(plan.moves) ? plan.moves : []; }
      catch (err) { fault = 'The moves could not be worked out for these settings.'; console.warn('learnPlan failed', err); moves = []; }
    }
  }
  L.k = orbit.length - 1;
  const pts = run(orbit[L.k]), N = 48;
  const paths = moves.map((m, j) => { const a = pts[j], out = []; for (let i = 0; i <= N; i++) out.push(at(m, a, i / N)); return out; });
  const say = moves.map((m, j) => { try { return String(m.say(pts[j], pts[j + 1])); } catch (e) { return m.name || ''; } });
  // companions: points that are pushed through the same moves
  const z = orbit[L.k], base = [], follow = [];
  if (L.show === 'circle') {
    if (sp === 1) for (let i = -3; i <= 3; i++) base.push([z[0] + i * 0.05, 0, 0]);
    else {
      const r = len(z), rad = 0.16 * Math.max(0.6, Math.min(r, 2));
      let u = [1, 0, 0], w = [0, 1, 0];
      if (sp === 3 && r > 1e-9) { const d = scl(z, 1 / r); u = norm(cross(Math.abs(d[2]) < 0.9 ? [0, 0, 1] : [1, 0, 0], d)); w = cross(d, u); }
      for (let i = 0; i < 32; i++) { const a = i / 32 * 2 * PI; base.push(add(z, add(scl(u, rad * Math.cos(a)), scl(w, rad * Math.sin(a))))); }
    }
  } else if (L.show === 'all') {
    if (sp === 1) { for (let i = -10; i <= 10; i++) base.push([i * 0.2, 0, 0]); follow.push(2, 6, 14, 18); }
    else if (sp === 2) { for (let i = 0; i < 72; i++) { const a = (i + 0.5) / 72 * 2 * PI; base.push([Math.cos(a), Math.sin(a), 0]); } follow.push(3, 14, 27, 44); }
    else {
      const M = 300, ga = PI * (3 - Math.sqrt(5));
      for (let i = 0; i < M; i++) { const zz = 1 - (i + 0.5) * 2 / M, rr = Math.sqrt(1 - zz * zz); base.push([rr * Math.cos(i * ga), rr * Math.sin(i * ga), zz]); }
      follow.push(40, 110, 190, 260);
    }
  }
  const comp = [base];
  moves.forEach((m, j) => comp.push(comp[j].map(v => at(m, v, 1))));
  // What the picture has to hold: the centre, both points, the whole path and the companions. The picture is
  // framed on these and not on the centre, so that on a small stage the step itself is as large as it can be.
  // The frame moves in steps (a quarter of a unit), so that it stands still while a dial is moved a little.
  const sheets = moves.map((m, j) => learnVSheet(m, pts[j]));
  if (!L.fitHold) {
    const key = [[0, 0, 0]];
    const see = (v, most) => { const l = len(v); key.push(l > most ? scl(v, most / l) : v); };
    pts.forEach(v => see(v, 9)); paths.forEach(p => p.forEach(v => see(v, 9))); orbit.forEach(v => see(v, 9)); see(P.c, 9);
    comp[0].forEach(v => see(v, 4)); comp[comp.length - 1].forEach(v => see(v, 4));
    const frame = list => {
      const lo = [0, 0, 0], hi = [0, 0, 0];
      list.forEach(v => { for (let i = 0; i < 3; i++) { lo[i] = Math.min(lo[i], v[i]); hi[i] = Math.max(hi[i], v[i]); } });
      const ctr = lo.map((x, i) => Math.round((x + hi[i]) / 2 * 4) / 4 + 0);
      let hx = 0.55, hy = 0.55, rr = 0.75, reach = 1;
      list.forEach(v => { hx = Math.max(hx, Math.abs(v[0] - ctr[0])); hy = Math.max(hy, Math.abs(v[1] - ctr[1])); rr = Math.max(rr, len(sub(v, ctr))); reach = Math.max(reach, Math.abs(v[0]), Math.abs(v[1]), Math.abs(v[2])); });
      return { ctr, hx, hy, rr, reach: Math.max(1, Math.ceil(reach - 0.2)) };
    };
    // A stage with room also holds what stands around the step: the unit circle or sphere and the whole of every
    // sheet. A small stage (a phone) keeps to the step itself, and lets those run off the edge.
    const wide = key.slice();
    for (let i = 0; i < sp; i++) for (const s of [-1, 1]) { const v = [0, 0, 0]; v[i] = s; wide.push(v); }
    sheets.forEach((q, j) => { if (!q.fr || !q.sheet || !(q.rs > 1e-6) || len(sub(pts[j + 1], pts[j])) < 1e-9) return; const r = Math.min(q.rs, 4); for (let i = 0; i < 12; i++) { const an = i / 12 * 2 * PI; see(add(q.ctr, add(scl(q.fr[0], r * Math.cos(an)), scl(q.fr[1], r * Math.sin(an)))), 9); wide.push(key.pop()); } });
    L.frame = { tight: frame(key), roomy: frame(wide) };
    L.fit = L.frame.roomy.rr;
  }
  // In space, a sheet seen edge on or a hinge seen end on is hard to read. Until the view is turned by hand, it
  // is turned for the reader: the nearest direction to the usual one from which every hinge of this step shows.
  if (sp === 3 && !L.view.s3.user && !L.fitHold) {
    const V = L.view.s3, cp = Math.cos(V.pitch), sn = Math.sin(V.pitch), turning = sheets.filter((q, j) => q.fr && len(sub(pts[j + 1], pts[j])) > 1e-6).map(q => cross(q.fr[0], q.fr[1]));
    const score = yaw => { let worst = 1; for (const nm of turning) { const d = Math.abs(dot([Math.sin(yaw) * cp, -Math.cos(yaw) * cp, sn], nm)); worst = Math.min(worst, d < 0.5 ? d / 0.5 : (1 - d) / 0.5); } return worst; };
    if (turning.length && score(V.yaw) < 0.4) {
      let best = V.yaw, bs = score(V.yaw);
      for (let i = 0; i < 36 && bs < 0.62; i++) { const y = LEARN_V_VIEWS.s3.yaw + (i % 2 ? 1 : -1) * Math.ceil(i / 2) * PI / 18, sc = score(y); if (sc > bs + 1e-9) { bs = sc; best = y; } }
      V.yaw = best;
    }
  }
  const end = pts[pts.length - 1], away = len(end) > 8 || !learnVFinite(end);
  L.cache = {
    moves, pts, paths, say, orbit, comp, follow, at, fault, away, end, sheets,
    note: fault || (plan && plan.note) || '',
    names: moves.map(m => m.name || m.key || 'Move'),
    doneText: moves.length ? `Step ${L.k + 1} is done: z went from ${learnVXyz(z)} to ${learnVXyz(end)}.` +
      (away ? ' The point has run away: it is now more than 8 from the centre. Press Start again, or pick another point.' : ' Press Next step to go on from there.') : fault,
  };
  L.pos = clamp(L.pos, 0, moves.length);
}
// Which move the position stands in, and how far through it.
function learnVAt() {
  const L = LEARN, n = L.cache ? L.cache.moves.length : 0;
  if (!n) return { j: 0, t: 0, done: true, n: 0 };
  const pos = clamp(L.pos, 0, n);
  if (pos >= n - 1e-9) return { j: n - 1, t: 1, done: true, n };
  let j = Math.floor(pos + 1e-9), t = clamp(pos - j, 0, 1);
  if (t < 1e-9 && j > 0 && L.endSide) { j -= 1; t = 1; }
  return { j, t, done: false, n };
}
// The moving point now.
function learnVPoint() {
  const K = LEARN.cache, a = learnVAt();
  if (!K || !a.n) return LEARN.pts[LEARN.space].z.slice();
  return a.t >= 1 ? K.pts[a.j + 1].slice() : a.t <= 0 ? K.pts[a.j].slice() : K.at(K.moves[a.j], K.pts[a.j], a.t);
}

// ---------- drawing
function learnVTheme() {
  const cs = getComputedStyle(document.documentElement), g = k => cs.getPropertyValue(k).trim();
  LEARN.col = { stage: g('--stage'), panel: g('--panel'), ink: g('--ink'), ink2: g('--ink-2'), line: g('--line'), brass: g('--brass'), ok: g('--ok'), bad: g('--bad'), warn: g('--warn'), mono: g('--f-mono') || 'monospace' };
}
// From a point of the picture's space to a place on the canvas: flat views drop what they cannot show, the
// tipped views and space look from a camera that turns about the upright z-axis.
function learnVProj() {
  const L = LEARN, w = L.w, h = L.h, vk = learnVKey(), V = L.view[vk], F = vk === 'f1' || Math.min(w, h) < 300 ? L.frame.tight : L.frame.roomy, f = F.ctr;
  // the scale moves in steps too (15% apart), for the same reason as the frame
  const grid = s => Math.pow(1.15, Math.floor(Math.log(Math.max(s, 1)) / Math.log(1.15) + 1e-9));
  const cx = w / 2, cy = vk === 'f1' ? h * 0.58 : h / 2 + 5;
  if (vk === 'f1' || vk === 'f2') {
    const s = grid(vk === 'f1' ? (w / 2 - 30) / F.hx : Math.min((w / 2 - 22) / F.hx, (h / 2 - 24) / F.hy)) * V.zoom;
    const to = v => [cx + (v[0] - f[0]) * s, cy - (vk === 'f1' ? 0 : v[1] - f[1]) * s, 0];
    return { cam: false, s, cx, cy, reach: F.reach, o: to([0, 0, 0]), to, from: (x, y) => [f[0] + (x - cx) / s, vk === 'f1' ? 0 : f[1] + (cy - y) / s, 0] };
  }
  const cyaw = Math.cos(V.yaw), syaw = Math.sin(V.yaw), cp = Math.cos(V.pitch), sp = Math.sin(V.pitch);
  const R = [cyaw, syaw, 0], H = [-syaw, cyaw, 0], U = [H[0] * sp, H[1] * sp, cp], D = [-H[0] * cp, -H[1] * cp, sp];
  // a sheet seen at a slant is wide and low, so it may use the width; the ball of space needs the height
  const s = grid(vk === 's3' ? (Math.min(w, h) / 2 - 16) / F.rr : Math.min((w / 2 - 22) / F.rr, (h / 2 - 14) / (F.rr * 0.8))) * V.zoom;
  const fr = dot(f, R), fu = dot(f, U), to = v => [cx + (dot(v, R) - fr) * s, cy - (dot(v, U) - fu) * s, dot(v, D)];
  return { cam: true, s, cx, cy, R, U, D, reach: F.reach, o: to([0, 0, 0]), to };
}
function learnVDraw() {
  const L = LEARN, cv = L.el.canvas, K = L.cache;
  if (L.follow === 'shape') { if (typeof learnShapeDraw === 'function') learnShapeDraw(); return; }   // the whole shape has the stage
  if (!L.on || !cv || !K) return;
  const w = stage.clientWidth, h = stage.clientHeight;
  if (!w || !h) return;
  const dpr = clamp(window.devicePixelRatio || 1, 1, 3), bw = Math.round(w * dpr), bh = Math.round(h * dpr);
  if (cv.width !== bw || cv.height !== bh) { cv.width = bw; cv.height = bh; }
  L.w = w; L.h = h;
  if (!L.col) learnVTheme();
  const g = cv.getContext('2d'), C = L.col, P = L.proj = learnVProj(), sp = L.space, vk = learnVKey(), small = w < 480;
  g.setTransform(dpr, 0, 0, dpr, 0, 0);
  g.clearRect(0, 0, w, h);
  g.lineJoin = g.lineCap = 'round';
  // small drawing kit
  const trace = (pts, close) => { g.beginPath(); pts.forEach((p, i) => { const q = P.to(p); if (i) g.lineTo(q[0], q[1]); else g.moveTo(q[0], q[1]); }); if (close) g.closePath(); };
  const stroke = (col, wd, al, dash) => { g.strokeStyle = col; g.lineWidth = wd; g.globalAlpha = al === undefined ? 1 : al; g.setLineDash(dash || []); g.stroke(); g.setLineDash([]); g.globalAlpha = 1; };
  const fill = (col, al) => { g.fillStyle = col; g.globalAlpha = al === undefined ? 1 : al; g.fill(); g.globalAlpha = 1; };
  const seg = (a, b, col, wd, al, dash) => { trace([a, b]); stroke(col, wd, al, dash); };
  const disc = (v, r, col, al) => { const q = P.to(v); g.beginPath(); g.arc(q[0], q[1], r, 0, 2 * PI); fill(col, al); };
  const ring = (v, r, col, wd, al, dash) => { const q = P.to(v); g.beginPath(); g.arc(q[0], q[1], r, 0, 2 * PI); stroke(col, wd, al, dash); };
  const label = (txt, x, y, col, align, px, weight) => {
    g.font = `${weight || 500} ${px || (small ? 11 : 12.5)}px ${C.mono}`; g.textAlign = align || 'left'; g.textBaseline = 'middle';
    // a label never leaves the picture: it stops at the edge
    const tw = g.measureText(txt).width, l = align === 'right' ? tw : align === 'center' ? tw / 2 : 0;
    x = clamp(x, 5 + l, Math.max(5 + l, w - 5 - (tw - l))); y = clamp(y, 9, h - 9);
    g.lineWidth = 4; g.strokeStyle = C.stage; g.globalAlpha = 0.92; g.strokeText(txt, x, y); g.globalAlpha = 1; g.fillStyle = col; g.fillText(txt, x, y);
  };
  const tag = (v, txt, col, dx, dy, align, px, weight) => { const q = P.to(v); label(txt, q[0] + (dx === undefined ? 10 : dx), q[1] + (dy === undefined ? -10 : dy), col, align, px, weight); };
  const O = [0, 0, 0], ex = [1, 0, 0], ey = [0, 1, 0], ez = [0, 0, 1];
  const circle = (u, v, r, n = 72) => { const out = []; for (let i = 0; i < n; i++) { const a = i / n * 2 * PI; out.push(add(scl(u, r * Math.cos(a)), scl(v, r * Math.sin(a)))); } return out; };
  const E = P.reach;   // how far the grid and the axes reach in the tipped views and in space
  const at = learnVAt(), m = K.moves[at.j], a = m ? K.pts[at.j] : O, p = learnVPoint(), start = K.orbit[L.k], c = L.pts[sp].c;

  // ----- the ground: grid, axes, the unit circle or sphere
  const axisTags = [];
  if (vk === 'f2') {
    const A = P.from(0, h), B = P.from(w, 0), step = B[0] - A[0] > 14 ? 2 : 1;   // the corners of what is in view
    for (let i = Math.ceil(A[0]); i <= Math.floor(B[0]); i++) if (i && i % step === 0) seg([i, A[1], 0], [i, B[1], 0], C.line, 1, 0.6);
    for (let i = Math.ceil(A[1]); i <= Math.floor(B[1]); i++) if (i && i % step === 0) seg([A[0], i, 0], [B[0], i, 0], C.line, 1, 0.6);
    seg([A[0], 0, 0], [B[0], 0, 0], C.ink2, 1.25, 0.9); seg([0, A[1], 0], [0, B[1], 0], C.ink2, 1.25, 0.9);
    trace(circle(ex, ey, 1), true); stroke(C.ink2, 1.25, 0.55, [3, 4]);
    for (let i = Math.ceil(A[0]); i <= Math.floor(B[0]); i++) if (i && i % step === 0) tag([i, 0, 0], learnVNum(i, 0), C.ink2, 0, 11, 'center', small ? 10 : 11);
    for (let i = Math.ceil(A[1]); i <= Math.floor(B[1]); i++) if (i && i % step === 0) tag([0, i, 0], learnVNum(i, 0), C.ink2, -7, 0, 'right', small ? 10 : 11);
    label('x', w - 12, P.o[1] - 10, C.ink2, 'center'); label('y', P.o[0] + 10, 10, C.ink2, 'center');
  } else if (vk === 'f1') {
    const A = P.from(0, 0), B = P.from(w, 0), step = B[0] - A[0] > 14 ? 2 : 1;
    seg([A[0], 0, 0], [B[0], 0, 0], C.ink, 2, 0.9);
    for (let i = Math.ceil(A[0]); i <= Math.floor(B[0]); i++) {
      const q = P.to([i, 0, 0]);
      g.beginPath(); g.moveTo(q[0], q[1] - (i ? 5 : 9)); g.lineTo(q[0], q[1] + (i ? 5 : 9)); stroke(C.ink, i ? 1.25 : 2, 0.9);
      if (i % step === 0) label(learnVNum(i, 0), q[0], q[1] + 20, C.ink2, 'center', small ? 10.5 : 12);
    }
    label('the line', w - 10, P.cy - 14, C.ink2, 'right');
  } else {
    const G = vk === 's3' ? E : E + 0.3, sheet3 = [[-G, -G, 0], [G, -G, 0], [G, G, 0], [-G, G, 0]];   // the sheet reaches a little past its grid
    if (vk !== 's3') { trace(sheet3, true); fill(C.panel, 0.75); trace(sheet3, true); stroke(C.line, 1, 1); }
    for (let i = -E; i <= E; i++) { seg([i, -E, 0], [i, E, 0], C.line, 1, vk === 's3' ? 0.45 : 0.7); seg([-E, i, 0], [E, i, 0], C.line, 1, vk === 's3' ? 0.45 : 0.7); }
    if (vk === 's3') {
      g.beginPath(); g.arc(P.o[0], P.o[1], P.s, 0, 2 * PI); stroke(C.ink2, 1.25, 0.5);
      trace(circle(ex, ey, 1), true); stroke(C.ink2, 1, 0.42, [3, 4]);
      trace(circle(ex, ez, 1), true); stroke(C.ink2, 1, 0.2); trace(circle(ey, ez, 1), true); stroke(C.ink2, 1, 0.2);
    } else if (vk === 'h2') { trace(circle(ex, ey, 1), true); stroke(C.ink2, 1.25, 0.55, [3, 4]); }
    // the axes the space has are solid; a direction it does not have is dashed
    seg([-E, 0, 0], [E, 0, 0], vk === 'h1' ? C.ink : C.ink2, vk === 'h1' ? 2.25 : 1.25, 0.95);
    tag([E, 0, 0], vk === 'h1' ? 'the line' : 'x', C.ink2, 8, 0);
    seg([0, -E, 0], [0, E, 0], C.ink2, 1.25, vk === 'h1' ? 0.6 : 0.95, vk === 'h1' ? [5, 5] : null);
    tag([0, E, 0], vk === 'h1' ? 'hidden direction' : 'y', C.ink2, 8, 0);
    if (vk === 's3') { seg([0, 0, -E], [0, 0, E], C.ink2, 1.25, 0.95); tag([0, 0, E], 'z', C.ink2, 8, -4); }
    // the page does not have the z-axis: it stands on it dashed, and is the hinge whenever the page turns
    if (vk === 'h2') { seg([0, 0, -E * 0.85], [0, 0, E * 0.85], C.ink2, 1.25, 0.6, [5, 5]); if (!(m && K.sheets[at.j].hinge)) tag([0, 0, E * 0.85], 'z, the hidden direction', C.ink2, 8, 2); }
    if (vk === 'h1') for (let i = -E; i <= E; i++) if (i) { tag([i, 0, 0], learnVNum(i, 0), C.ink2, 0, 13, 'center', small ? 10 : 11); disc([i, 0, 0], 2, C.ink); }
    // where the names of the axes stand (inside the picture), so that the word "hinge" can keep clear of them
    for (const v of [[E, 0, 0], [0, E, 0], [0, 0, vk === 'h2' ? E * 0.85 : E]]) { const q = P.to(v); axisTags.push([clamp(q[0] + 8, 5, w - 5), clamp(q[1], 9, h - 9)]); }
  }

  // ----- what the move turns about, and the sheet it moves in
  // (the flat sheet the point travels in goes through the point, with its centre on the hinge: see learnVSheet)
  const Q = m ? K.sheets[at.j] : { hinge: null, sheet: null, fr: null, ctr: O, rs: 0 }, hinge = Q.hinge, sheet = Q.sheet, fr = Q.fr, ctr = Q.ctr, rs = Q.rs;
  const round = (r, n) => circle(fr[0], fr[1], r, n).map(v => add(ctr, v));
  if (sheet && fr && vk !== 'f1' && rs > 1e-6) {
    trace(round(rs), true); fill(C.ok, 0.1);
    trace(round(rs), true); stroke(C.ok, 1.25, 0.55);
    seg(ctr, add(ctr, scl(fr[0], rs)), C.ink2, 1, 0.7, [4, 4]);
  }
  if (hinge) {
    const hn = hinge, reach = vk === 's3' ? E * 1.05 : E * 0.85, q0 = P.to(scl(hn, -reach)), q1 = P.to(scl(hn, reach));
    if (Math.hypot(q1[0] - q0[0], q1[1] - q0[1]) < 16) {
      ring(O, 8, C.ok, 2); disc(O, 2.5, C.ok);
      label(vk === 'f1' ? 'hinge (hidden)' : 'hinge, seen end on', P.o[0] + 13, P.o[1] + (vk === 'f1' ? -24 : 16), C.ok, 'left', 0, 600);
    } else {
      seg(scl(hn, -reach), scl(hn, reach), C.ok, 2.25, 1, [8, 5]);
      // the word stands by the upper end of the line, or by the highest part of it that is in the picture
      const up = q1[1] < q0[1] ? 1 : -1; let at1 = up > 0 ? q1 : q0;
      for (let i = 20; i >= 4; i--) { const q = P.to(scl(hn, up * reach * i / 20)); at1 = q; if (q[0] > 12 && q[0] < w - 60 && q[1] > 16 && q[1] < h - 16 && axisTags.every(t => Math.abs(t[1] - q[1]) > 15 || t[0] < q[0] - 24 || t[0] > q[0] + 64)) break; }
      label('hinge', at1[0] + 9, at1[1] + 2, C.ok, 'left', small ? 12.5 : 14, 600);
    }
  }

  // ----- the steps taken before this one
  for (let i = 0; i < L.k; i++) { seg(K.orbit[i], K.orbit[i + 1], C.ink2, 1.25, 0.55); disc(K.orbit[i], 2.75, C.ink2, 0.9); tag(K.orbit[i], String(i), C.ink2, 6, 9, 'left', 10); }

  // ----- companions: a small circle round the point, or every direction at once
  if (K.comp[0].length) {
    const now = at.t >= 1 ? K.comp[at.j + 1] : at.t <= 0 ? K.comp[at.j] : K.comp[at.j].map(v => K.at(m, v, at.t));
    const lift = vk === 'f1' ? -9 : 0;   // on a flat line the companions ride just above it
    if (L.show === 'circle') {
      if (vk !== 'f1') {
        trace(K.comp[0], true); stroke(C.ink2, 1, 0.5, [2, 3]);
        trace(now, true); fill(C.brass, 0.14); trace(now, true); stroke(C.ink, 1.25, 0.85);
      }
      now.forEach(v => { const q = P.to(v); g.beginPath(); g.arc(q[0], q[1] + lift, vk === 'f1' ? 2.25 : 1.6, 0, 2 * PI); fill(C.ink, 0.9); });
    } else {
      const hues = [C.ok, C.bad, C.ink, C.warn];
      now.forEach((v, i) => {
        if (K.follow.includes(i)) return;
        const q = P.to(v); g.beginPath(); g.arc(q[0], q[1] + lift, sp === 3 ? 1.9 : 2.3, 0, 2 * PI); fill(C.ink2, P.cam && q[2] < 0 ? 0.3 : 0.7);
      });
      K.follow.forEach((i, n) => {
        const q = P.to(now[i]), q0 = P.to(K.comp[0][i]);
        g.beginPath(); g.arc(q0[0], q0[1] + lift, 6, 0, 2 * PI); stroke(hues[n % 4], 1.5, 0.75);
        g.beginPath(); g.arc(q[0], q[1] + lift, 6.5, 0, 2 * PI); fill(C.stage); g.beginPath(); g.arc(q[0], q[1] + lift, 5, 0, 2 * PI); fill(hues[n % 4]);
      });
    }
  }

  // ----- the path of the point: swept so far, and still to come
  const N = 48, so = K.paths[at.j] ? K.paths[at.j].slice(0, Math.floor(at.t * N + 1e-9) + 1).concat([p]) : [];
  if (vk === 'f1') {
    // on a flat line every move is drawn as a bow from where it starts to where the point is now
    K.moves.forEach((mv, j) => {
      const from = P.to(K.pts[j]), to = P.to(j < at.j ? K.pts[j + 1] : j === at.j ? p : K.pts[j + 1]), up = 22 + 9 * j, later = j > at.j;
      if (Math.abs(to[0] - from[0]) < 1) return;
      g.beginPath(); g.moveTo(from[0], from[1] - 9); g.quadraticCurveTo((from[0] + to[0]) / 2, from[1] - 9 - up * 1.6, to[0], to[1] - 9);
      stroke(later ? C.ink2 : C.brass, later ? 1.25 : 2, later ? 0.5 : 0.95, later ? [2, 4] : null);
    });
  } else {
    if ((hinge || sheet) && so.length > 2) { trace([ctr].concat(so), true); fill(C.brass, 0.2); }
    K.paths.forEach((path, j) => {
      if (j < at.j) { trace(path); stroke(C.brass, 2, 0.8); }
      else if (j > at.j) { trace(path); stroke(C.ink2, 1.25, 0.42, [1.5, 5]); }
    });
    if (K.paths[at.j]) { trace(K.paths[at.j].slice(Math.floor(at.t * N + 1e-9))); stroke(C.ink2, 1.25, 0.42, [1.5, 5]); }
    if (so.length > 1) { trace(so); stroke(C.brass, 2.75, 1); }
  }

  // ----- the number that is changing: an angle (with its arc at the centre) or a length
  let read = '';
  const unwrap = list => {             // the angle in the frame along a path, without jumps of a whole turn
    let prev = null, sum = 0; const out = [];
    for (const v of list) { const an = Math.atan2(dot(v, fr[1]), dot(v, fr[0])); if (prev === null) sum = an; else { let d = an - prev; d -= 2 * PI * Math.round(d / (2 * PI)); sum += d; } prev = an; out.push(sum); }
    return out;
  };
  const inFrame = v => Math.hypot(dot(v, fr[0]), dot(v, fr[1]));
  if (m && fr && inFrame(a) > 1e-6 && K.paths[at.j].every(v => inFrame(v) > 1e-9)) {
    const all = unwrap(K.paths[at.j]), cur = unwrap(so), a0 = all[0], a1 = all[all.length - 1], an = cur[cur.length - 1];
    if (Math.abs(a1 - a0) > 1e-4) {
      read = `${learnVDeg(a0)} → ${learnVDeg(an)}`;
      if (vk !== 'f1') {
        const rw = Math.min(34 / P.s, 0.5 * rs), arc = [], steps = Math.max(8, Math.ceil(Math.abs(an) / 0.08));
        for (let i = 0; i <= steps; i++) { const q = an * i / steps; arc.push(add(ctr, add(scl(fr[0], rw * Math.cos(q)), scl(fr[1], rw * Math.sin(q))))); }
        trace(arc); stroke(C.brass, 1.75, 1);
        const mid = an / 2, out = rw + 17 / P.s;
        tag(add(ctr, add(scl(fr[0], out * Math.cos(mid)), scl(fr[1], out * Math.sin(mid)))), learnVDeg(an), C.brass, 0, 0, 'center', small ? 11.5 : 13, 600);
      }
    }
  }
  if (m && !read) {
    const l0 = len(a), l1 = len(K.pts[at.j + 1]), radial = l0 > 1e-9 && len(sub(scl(a, l1 / l0), K.pts[at.j + 1])) < 1e-6 * Math.max(1, l1);
    if (m.key === 'stretch' || (radial && Math.abs(l1 - l0) > 1e-9)) read = `length ${learnVNum(l0)} → ${learnVNum(len(p))}`;
    else if (len(sub(K.pts[at.j + 1], a)) > 1e-9) read = `${learnVXyz(a)} → ${learnVXyz(p)}`;
    else read = 'the point stays where it is';
  }
  // adding c: the arm of c, carried to the point
  if (m && m.key === 'shift' && vk !== 'f1') { seg(a, add(a, c), C.ink, 1.25, 0.8, [5, 4]); }

  // ----- arms and points
  if (vk !== 'f1') {
    seg(O, c, C.ink2, 1.25, 0.6, [2, 4]);
    if (len(sub(p, start)) > 1e-9) seg(O, start, C.ink2, 1.25, 0.7, [5, 4]);
    seg(O, p, C.brass, 2.25, 1);
    if (vk === 's3') for (const [v, col] of [[p, C.brass], [c, C.ink2]]) { seg(v, [v[0], v[1], 0], col, 1, 0.55, [2, 3]); disc([v[0], v[1], 0], 1.75, col, 0.7); }
  }
  disc(O, 2.75, C.ink);
  // the point c: a diamond
  { const q = P.to(c), r = 7; g.beginPath(); g.moveTo(q[0], q[1] - r); g.lineTo(q[0] + r, q[1]); g.lineTo(q[0], q[1] + r); g.lineTo(q[0] - r, q[1]); g.closePath(); fill(C.stage, 0.9); stroke(C.ink, 2, 1); label('c', q[0] + 11, q[1] + (vk === 'f1' ? 22 : 9), C.ink, 'left', small ? 12 : 13.5, 600); }
  // where the step started: a ring (in the flat views it is the handle that moves z)
  const qs = P.to(start), qp = P.to(p), apart = Math.hypot(qs[0] - qp[0], qs[1] - qp[1]);
  ring(start, 8, C.ink, 1.75, 1, P.cam ? null : [3, 2.5]);
  // labels stand clear of the arm: the point's outwards from the centre, the start's to the side the turn leaves behind
  const away = (q, gap, side) => { let dx = q[0] - P.o[0], dy = q[1] - P.o[1]; const d = Math.hypot(dx, dy); if (d < 2) { dx = 0.7; dy = -0.7; } else { dx /= d; dy /= d; } if (side) [dx, dy] = [-dy, dx]; return [q[0] + dx * gap, q[1] + dy * gap, dx > 0.35 ? 'left' : dx < -0.35 ? 'right' : 'center']; };
  if (apart > 26) { if (vk === 'f1') label('start', qs[0], qs[1] + 36, C.ink2, 'center'); else { const t = away(qs, 19, true); label('start', t[0], t[1], C.ink2, t[2]); } }
  // the moving point (hollow while it is off a flat line, out in the direction the line does not have)
  const off = vk === 'f1' && Math.hypot(p[1], p[2]) > 1e-3 * Math.max(1, len(p));
  disc(p, 8.5, C.stage); disc(p, 6.5, C.brass, off ? 0.35 : 1); if (off) ring(p, 6.5, C.brass, 1.75);
  { const t = vk === 'f1' ? [qp[0], qp[1] - 22, 'center'] : away(qp, 18, false); label(at.done ? 'new z' : 'z', t[0], t[1], C.brass, t[2], small ? 13.5 : 15.5, 600); }
  if (off) label('z is off the line, out in the hidden direction', P.cx, Math.min(h - 12, P.cy + 62), C.ink2, 'center');

  // ----- the read-out in the corner
  if (m) {
    label(`${m.name}`, 10, 15, C.ink, 'left', small ? 12.5 : 14, 600);
    label(read, 10, small ? 32 : 35, C.brass, 'left', small ? 12.5 : 14, 600);
  }
}

// ---------- the words and marks on the page
function learnVPaint() {
  const L = LEARN, K = L.cache, el = L.el;
  if (L.follow === 'shape') { if (typeof learnShapePaint === 'function') learnShapePaint(); return; }   // and its own words and transport
  if (!L.on || !K) return;
  const at = learnVAt(), n = at.n, put = (node, text, html) => { if (node.dataset.t !== text) { node.dataset.t = text; if (html) node.innerHTML = text; else node.textContent = text; } };
  put(el.where, !n ? 'No moves' : at.done ? `Step ${L.k + 1}: <b>done</b>` : `Step ${L.k + 1}, move ${at.j + 1} of ${n}: <b>${K.names[at.j]}</b>`, true);
  put(el.say, !n ? K.fault : at.done ? K.doneText : K.say[at.j]);
  const sig = K.names.join('|');
  if (L.sig !== sig) {
    L.sig = sig;
    el.ticks.textContent = ''; el.moves.textContent = '';
    K.names.forEach((name, j) => {
      const tick = document.createElement('button');
      tick.type = 'button'; tick.tabIndex = -1; tick.textContent = name; tick.title = `Play move ${j + 1}: ${name}`;
      tick.addEventListener('click', () => learnVPlayMove(j));
      el.ticks.appendChild(tick);
      const b = document.createElement('button');
      b.type = 'button'; b.className = 'btn'; b.innerHTML = `<span class="learn-no">${j + 1}</span><span></span>`;
      b.lastChild.textContent = name;
      b.addEventListener('click', () => { learnVPlayMove(j); learnVShowStage(); });
      el.moves.appendChild(b);
    });
  }
  [...el.ticks.children].forEach((b, j) => { b.classList.toggle('is-on', !at.done && j === at.j); b.classList.toggle('is-past', at.done || j < at.j); });
  [...el.moves.children].forEach((b, j) => { const on = !at.done && j === at.j; b.classList.toggle('is-on', on); b.setAttribute('aria-pressed', String(on)); });
  if (+el.pos.max !== Math.max(1, n)) el.pos.max = Math.max(1, n);
  if (Math.abs(+el.pos.value - L.pos) > 1e-6) el.pos.value = L.pos;
  el.pos.setAttribute('aria-valuetext', !n ? '' : at.done ? 'The step is done' : `Move ${at.j + 1} of ${n}, ${K.names[at.j]}, ${Math.round(at.t * 100)} percent`);
  put(el.play, L.playing ? 'Pause' : 'Play');
  el.play.setAttribute('aria-pressed', String(L.playing));
  el.back.disabled = L.pos <= 1e-9; el.fwd.disabled = at.done; el.next.disabled = !n || K.away; el.again.disabled = L.k === 0 && L.pos <= 1e-9;
  put(el.note, K.note); el.note.hidden = !K.note;
  put(el.notice, LEARN_V_NOTICE[L.space]);
  put(el.hiddenNote, LEARN_V_HIDDEN[L.space === 3 ? '3' : L.space + (L.hidden[L.space] ? 'on' : 'off')]);
  el.eqNote.hidden = S.eq === 'z^n + c';
  const cam = learnVIsCam(), V = L.view[learnVKey()], D = LEARN_V_VIEWS[learnVKey()];
  put(el.hint, cam ? 'Drag to turn the picture. Scroll or pinch to zoom.' : 'Drag the ring to move z, and the diamond to move c. Scroll to zoom.');
  el.viewReset.hidden = !(Math.abs(V.zoom - 1) > 1e-6 || (cam && (V.user || V.pitch !== D.pitch)));
  for (const r of el.spaces) r.checked = +r.value === L.space;
}
// ---------- the clock: one frame redoes what is stale, moves a playing step on, and draws
function learnVQueue() { if (!LEARN.raf && LEARN.on) LEARN.raf = requestAnimationFrame(learnVFrame); }
function learnVFrame(now) {
  const L = LEARN;
  L.raf = 0;
  if (!L.on) return;
  if (L.stale) learnVBuild();
  if (L.playing) {
    const n = L.cache.moves.length, dt = clamp(now - L.last, 0, 80), stop = L.until === null ? n : Math.min(n, L.until);
    L.last = now;
    if (L.dwell > 0) { L.dwell -= dt; if (L.dwell <= 0) L.endSide = false; }
    else {
      const edge = Math.floor(L.pos + 1e-9) + 1;
      let pos = L.pos + dt / (LEARN_V_SECONDS[L.speed] * 1000);
      L.endSide = false;
      if (pos >= edge) { pos = edge; L.endSide = true; if (edge < stop) L.dwell = 420; }
      if (pos >= stop - 1e-9) { pos = stop; L.playing = false; L.until = null; L.endSide = true; }
      L.pos = pos;
    }
  }
  learnVPaint(); learnVDraw();
  if (L.playing) learnVQueue();
}
// Everything now, without waiting for a frame (the test methods and the controls use it, so that what they
// read back is already true).
function learnVNow() {
  const L = LEARN;
  if (!L.on) { if (L.stale && L.pts) learnVBuild(); return; }
  if (L.stale) learnVBuild();
  learnVPaint(); learnVDraw();
}
function learnVChanged() { LEARN.stale = true; learnVNow(); }
// touch() calls this while Learn is on: a dial of the approach, the power or a modifier has changed.
function learnTouch() { if (!LEARN.on) return; LEARN.stale = true; learnVQueue(); }
function learnVStop() { LEARN.playing = false; LEARN.until = null; LEARN.dwell = 0; }
function learnVPlay(until) {
  const L = LEARN, n = L.cache ? L.cache.moves.length : 0;
  if (!n) return;
  if (L.pos >= n - 1e-9) L.pos = 0;                   // at the end: play the step again from its start
  L.until = until === undefined ? null : until;
  L.playing = true; L.dwell = 0; L.endSide = false; L.last = performance.now();
  learnVPaint(); learnVQueue();
}
function learnVPlayMove(j) { LEARN.pos = j; learnVPlay(j + 1); }
function learnVGoto(pos, endSide) { learnVStop(); LEARN.pos = pos; LEARN.endSide = !!endSide; learnVNow(); }
function learnVNextStep(play) {
  const L = LEARN;
  if (L.stale) learnVBuild();
  if (!L.cache.moves.length || L.cache.away) return false;
  learnVStop(); L.k += 1; L.pos = 0; L.endSide = false;
  learnVChanged();
  if (play && !matchMedia('(prefers-reduced-motion: reduce)').matches) learnVPlay();
  return true;
}
function learnVAgain() { learnVStop(); LEARN.k = 0; LEARN.pos = 0; LEARN.endSide = false; learnVChanged(); }
function learnVShowStage() {
  // on a narrow page the list of moves is far below the picture: bring the picture back into view
  const r = stage.getBoundingClientRect();
  if (r.bottom < 80 || r.top > innerHeight - 80) stage.scrollIntoView({ block: 'nearest', behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth' });
}
// The settings of Learn back to how it opens (the approach, the power and the modifiers are not Learn's).
function learnVDefaults() {
  const L = LEARN;
  learnVStop();
  L.space = 2; L.pts = learnVCopy(LEARN_V_START); L.show = 'circle'; L.hidden = { 1: true, 2: false };
  L.view = learnVCopy(LEARN_V_VIEWS); L.speed = 'normal'; L.k = 0; L.pos = 0; L.endSide = false; L.stale = true;
  if (L.el.speed) L.el.speed.value = 'normal';
  if (typeof learnShapeDefaults === 'function') learnShapeDefaults();   // Follow = One point, and the whole shape as it opens
  if (L.dials) { L.dials.sync(); L.checks.sync(); }
}
// "Reset everything": Learn goes back to its starting state, which is off, with its own settings as they open.
function learnReset() { learnVDefaults(); learnVSetOn(false, true); }
// Learn on or off. `quiet`: the caller draws the solid itself (a click on another choice under Show does).
function learnVSetOn(on, quiet) {
  const L = LEARN, el = L.el;
  on = !!on;
  if (L.on === on && !!S.learn === on) return;
  learnVStop();
  L.on = on; S.learn = on;
  document.body.classList.toggle('is-learn', on);
  for (const node of [el.panel, el.bar, el.canvas, el.over]) node.hidden = !on;
  if (typeof learnShapeSync === 'function') learnShapeSync();   // with Follow = A whole shape, its transport and canvas stand in
  if (on) {
    el.radio.checked = true; el.panel.open = true;
    learnVTheme(); learnVChanged();
    if (typeof uiCollapsePaint === 'function') uiCollapsePaint();
  } else if (!quiet) refresh(false);   // re-ticks the choice the picture belongs to and draws the solid again
}
function learnVRefresh() {             // the end of every refresh()
  if (!LEARN.on) return;
  LEARN.el.radio.checked = true;
  learnVChanged();
}

// ---------- hands on the picture
function learnVBind(cv) {
  const L = LEARN, at = e => { const r = cv.getBoundingClientRect(); return [e.clientX - r.left, e.clientY - r.top]; };
  const grab = (x, y, reach) => {
    const P = L.proj, K = L.cache;
    if (!P || !K || P.cam) return null;
    const qz = P.to(K.orbit[L.k]), qc = P.to(L.pts[L.space].c), dz = Math.hypot(x - qz[0], y - qz[1]), dc = Math.hypot(x - qc[0], y - qc[1]);
    if (Math.min(dz, dc) > reach) return null;
    return dz <= dc ? { kind: 'z', dx: qz[0] - x, dy: qz[1] - y } : { kind: 'c', dx: qc[0] - x, dy: qc[1] - y };
  };
  const zoomBy = f => { const V = L.view[learnVKey()]; V.zoom = clamp(V.zoom * f, 0.35, 6); };
  const spread = () => { const [p, q] = [...L.ptr.values()]; return Math.hypot(p[0] - q[0], p[1] - q[1]); };
  cv.addEventListener('pointerdown', e => {
    if (!L.on || (e.pointerType === 'mouse' && e.button !== 0)) return;
    try { cv.setPointerCapture(e.pointerId); } catch (err) { /* a scripted press has no real pointer */ }
    const [x, y] = at(e);
    L.ptr.set(e.pointerId, [x, y]);
    if (L.ptr.size === 2) { L.pinch = { d: Math.max(1, spread()), zoom: L.view[learnVKey()].zoom }; L.drag = null; return; }
    if (learnVIsCam()) L.drag = { kind: 'turn', x, y };
    else { L.drag = grab(x, y, e.pointerType === 'mouse' ? 16 : 26); if (L.drag) L.fitHold = true; }
    if (L.drag) e.preventDefault();
  });
  cv.addEventListener('pointermove', e => {
    if (!L.on) return;
    const [x, y] = at(e);
    if (!L.ptr.has(e.pointerId)) { if (!learnVIsCam()) cv.style.cursor = grab(x, y, 16) ? 'move' : 'default'; else cv.style.cursor = ''; return; }
    L.ptr.set(e.pointerId, [x, y]);
    if (L.pinch && L.ptr.size === 2) { L.view[learnVKey()].zoom = clamp(L.pinch.zoom * spread() / L.pinch.d, 0.35, 6); learnVNow(); return; }
    const d = L.drag;
    if (!d) return;
    if (d.kind === 'turn') {
      const V = L.view[learnVKey()];
      V.yaw -= (x - d.x) * 0.01; V.pitch = clamp(V.pitch + (y - d.y) * 0.01, -1.5, 1.5); V.user = true; d.x = x; d.y = y;
      learnVNow(); return;
    }
    const P = L.proj, r2 = v => clamp(Math.round(v * 100) / 100, -8, 8) + 0, pt = L.pts[L.space];
    const at2 = P.from(x + d.dx, y + d.dy), v = [r2(at2[0]), L.space > 1 ? r2(at2[1]) : 0, 0];
    if (d.kind === 'z') { pt.z = v; L.k = 0; } else pt.c = v;
    L.dials.sync(); learnVChanged();
  });
  const up = e => {
    L.ptr.delete(e.pointerId);
    if (L.ptr.size < 2) L.pinch = null;
    if (!L.ptr.size) { const held = L.fitHold; L.drag = null; L.fitHold = false; if (held) learnVChanged(); }
  };
  cv.addEventListener('pointerup', up); cv.addEventListener('pointercancel', up);
  // The stage has a wheel listener of the camera's (50-camera.js), which would zoom the solid behind this picture.
  // While Learn is on the wheel is taken here, on the stage and in the capture phase, before that one hears it.
  stage.addEventListener('wheel', e => {
    if (!L.on) return;
    e.preventDefault(); e.stopImmediatePropagation();
    if (L.follow === 'shape') { if (typeof learnShapeWheel === 'function') learnShapeWheel(e); return; }
    zoomBy(Math.exp(-e.deltaY * (e.deltaMode === 1 ? 0.05 : 0.0015))); learnVNow();
  }, { capture: true, passive: false });
  cv.addEventListener('keydown', e => {
    if (!L.on || e.ctrlKey || e.metaKey || e.altKey) return;
    const dir = { ArrowLeft: [-1, 0], ArrowRight: [1, 0], ArrowUp: [0, 1], ArrowDown: [0, -1] }[e.key];
    if (e.key === '+' || e.key === '=') zoomBy(1.15);
    else if (e.key === '-') zoomBy(1 / 1.15);
    else if (e.key === ' ') { if (L.playing) learnVStop(); else learnVPlay(); }
    else if (dir && learnVIsCam()) { const V = L.view[learnVKey()]; V.yaw -= dir[0] * 0.1; V.pitch = clamp(V.pitch + dir[1] * 0.1, -1.5, 1.5); V.user = true; }
    else if (dir) { const pt = L.pts[L.space], st = e.shiftKey ? 0.01 : 0.05; pt.z = [clamp(+(pt.z[0] + dir[0] * st).toFixed(2), -8, 8), L.space > 1 ? clamp(+(pt.z[1] + dir[1] * st).toFixed(2), -8, 8) : 0, 0]; L.k = 0; L.dials.sync(); L.stale = true; }
    else return;
    e.preventDefault(); learnVNow();
  });
}

// ---------- building it (called once, after boot())
function learnInit() {
  const L = LEARN, el = L.el, make = (tag, cls, html) => { const n = document.createElement(tag); if (cls) n.className = cls; if (html) n.innerHTML = html; return n; };
  if (el.panel) return;
  L.pts = learnVCopy(LEARN_V_START); L.view = learnVCopy(LEARN_V_VIEWS);

  // the fourth choice under Show
  const modes = document.querySelector('fieldset.mode'), seg = make('label', 'seg', '<input type="radio" name="mode" id="mode-l" value="l"><span>Learn</span>');
  modes.appendChild(seg);
  el.radio = seg.querySelector('input');
  // In the capture phase, so that S.learn is right before the page's own handlers run. Going back to the choice
  // the picture already belongs to must not count as choosing it anew (that would put the camera back).
  modes.addEventListener('change', e => {
    const t = e.target;
    if (!t || t.name !== 'mode') return;
    if (t === el.radio) { learnVSetOn(true); return; }
    if (!L.on) return;
    learnVSetOn(false, true);
    if (t.value === S.mode) { e.stopPropagation(); refresh(false); }
  }, true);
  document.addEventListener('click', e => { if (e.target && e.target.closest && e.target.closest('#resetAll')) learnReset(); }, true);

  // the stage: the drawing, a hint and the button that puts the view back
  el.canvas = make('canvas', 'learn-canvas');
  el.canvas.id = 'learnCanvas'; el.canvas.tabIndex = 0; el.canvas.hidden = true;
  el.canvas.setAttribute('role', 'img');
  el.canvas.setAttribute('aria-label', 'Drawing of one step: the point z, the point c, and the move being played. The sentence under the picture says the same in words. With the picture in focus, the arrow keys turn a tipped view or move z in a flat one, plus and minus zoom, and the space bar plays or pauses.');
  el.over = make('div', 'learn-over', '<p class="learn-hint" id="learnHint"></p><button class="btn" id="learnViewReset" type="button" hidden>Reset view</button>');
  el.over.hidden = true;
  stage.append(el.canvas, el.over);
  el.hint = el.over.querySelector('#learnHint'); el.viewReset = el.over.querySelector('#learnViewReset');
  el.viewReset.addEventListener('click', () => { L.view[learnVKey()] = learnVCopy(LEARN_V_VIEWS[learnVKey()]); learnVChanged(); });
  learnVBind(el.canvas);

  // the transport, directly under the stage
  el.bar = make('div', 'learn-bar',
    '<div class="learn-head"><span class="label learn-where" id="learnWhere"></span>' +
    '<label class="learn-speed"><span class="label">Speed</span><select id="learnSpeed"><option value="slow">Slow</option><option value="normal" selected>Normal</option><option value="fast">Fast</option></select></label></div>' +
    '<p class="learn-say" id="learnSay" aria-live="polite"></p>' +
    '<div class="learn-track"><input class="learn-pos" id="learnPos" type="range" min="0" max="3" step="0.005" value="0" aria-label="Where in the step. Drag to take a move forwards and backwards by hand.">' +
    '<div class="learn-ticks" id="learnTicks"></div></div>' +
    '<div class="learn-btns" role="group" aria-label="Play the step">' +
    '<button class="btn learn-step" id="learnBack" type="button" aria-label="Back one move" title="Back one move">◀</button>' +
    '<button class="btn learn-play" id="learnPlay" type="button" aria-pressed="false">Play</button>' +
    '<button class="btn learn-step" id="learnFwd" type="button" aria-label="Forward one move" title="Forward one move">▶</button>' +
    '<button class="btn" id="learnNext" type="button" title="Go on from the new point">Next step</button>' +
    '<button class="btn" id="learnAgain" type="button" title="Back to the first point">Start again</button></div>');
  el.bar.id = 'learnBar'; el.bar.hidden = true;
  stage.after(el.bar);
  for (const [key, id] of [['where', 'learnWhere'], ['say', 'learnSay'], ['pos', 'learnPos'], ['ticks', 'learnTicks'], ['back', 'learnBack'], ['play', 'learnPlay'], ['fwd', 'learnFwd'], ['next', 'learnNext'], ['again', 'learnAgain'], ['speed', 'learnSpeed']]) el[key] = el.bar.querySelector('#' + id);
  el.pos.addEventListener('input', () => learnVGoto(+el.pos.value, +el.pos.value >= +el.pos.max));
  el.play.addEventListener('click', () => { if (L.playing) { learnVStop(); learnVNow(); } else learnVPlay(); });
  el.back.addEventListener('click', () => { const a = learnVAt(); learnVGoto(a.done ? a.n - 1 : a.t > 0.02 && a.t < 1 ? a.j : Math.max(0, (a.t >= 1 ? a.j + 1 : a.j) - 1)); });
  el.fwd.addEventListener('click', () => {
    const a = learnVAt(), j = a.t >= 1 ? a.j + 1 : a.j;
    if (a.done) return;
    if (matchMedia('(prefers-reduced-motion: reduce)').matches) learnVGoto(j + 1, true);
    else { if (a.t >= 1) L.pos = j; learnVPlay(j + 1); }
  });
  el.next.addEventListener('click', () => learnVNextStep(true));
  el.again.addEventListener('click', learnVAgain);
  el.speed.addEventListener('change', () => { L.speed = LEARN_V_SECONDS[el.speed.value] ? el.speed.value : 'normal'; });

  // the panel, first among the sections
  el.panel = make('details', 'sec',
    '<summary class="label">Learn: one step, move by move</summary><div class="sec-body">' +
    '<p class="note">One step of the lab is z → zⁿ + c. Here that step is taken apart into simple moves, and each one is played on its own. Press Play under the picture, or drag the slider there to take a move forwards and backwards by hand. The power n and the approach are in the section Approach and equation.</p>' +
    '<p class="note warn-note" id="learnEqNote" hidden>The equation is not zⁿ + c just now. Learn shows the plain rule zⁿ + c.</p>' +
    '<fieldset class="learn-space" id="learnSpace"><legend class="label">Space</legend>' +
    '<label class="seg"><input type="radio" name="learnSpace" id="learnSpace1" value="1"><span>1D line</span></label>' +
    '<label class="seg"><input type="radio" name="learnSpace" id="learnSpace2" value="2" checked><span>2D page</span></label>' +
    '<label class="seg"><input type="radio" name="learnSpace" id="learnSpace3" value="3"><span>3D space</span></label></fieldset>' +
    '<div id="learnChecks" class="sec-inner"></div><p class="note" id="learnHiddenNote"></p>' +
    '<div id="learnDials" class="sec-inner"></div>' +
    '<div class="learn-btncol"><button class="btn" id="learnZero" type="button">Start at 0, like the Mandelbrot set</button>' +
    '<button class="btn" id="learnJuliaC" type="button">Use the c of the Julia tab</button></div>' +
    '<p class="label" id="learnMovesHead">The moves of this step</p><div class="learn-moves" id="learnMoves" role="group" aria-labelledby="learnMovesHead"></div>' +
    '<p class="note" id="learnNote"></p>' +
    '<p class="label">What to notice</p><p class="learn-notice" id="learnNotice"></p>' +
    '<div id="learnReset"></div></div>');
  el.panel.id = 'learnPanel'; el.panel.open = true; el.panel.hidden = true;
  $('sections').prepend(el.panel);
  for (const [key, id] of [['moves', 'learnMoves'], ['note', 'learnNote'], ['notice', 'learnNotice'], ['hiddenNote', 'learnHiddenNote'], ['eqNote', 'learnEqNote']]) el[key] = el.panel.querySelector('#' + id);
  el.spaces = [...el.panel.querySelectorAll('input[name=learnSpace]')];
  el.panel.querySelector('#learnSpace').addEventListener('change', e => { if (e.target.name === 'learnSpace') L.set({ space: +e.target.value }); });
  el.panel.addEventListener('toggle', () => { if (typeof uiCollapsePaint === 'function') uiCollapsePaint(); });
  // The dials read and write the points of the space on show. A new first point starts the steps afresh.
  const store = {}, bind = (key, get, set) => Object.defineProperty(store, key, { get, set, enumerable: true });
  ['x', 'y', 'z'].forEach((axis, i) => {
    bind('z' + axis, () => L.pts[L.space].z[i], v => { L.pts[L.space].z[i] = v; L.k = 0; });
    bind('c' + axis, () => L.pts[L.space].c[i], v => { L.pts[L.space].c[i] = v; });
  });
  bind('show', () => L.show, v => { L.show = v; });
  bind('hid', () => !!L.hidden[L.space], v => { if (L.space < 3) L.hidden[L.space] = !!v; });
  const changed = () => { learnVStop(); learnVChanged(); };
  L.checks = buildControls('learnChecks', [{ type: 'check', key: 'hid', label: 'Show the hidden direction', def: false, when: () => L.space < 3 }], store, changed, { idPrefix: 'learn-', group: 'learn' });
  const pd = (key, label, when) => ({ type: 'dial', key, label, min: -2, max: 2, step: 0.01, lo: -8, hi: 8, when });
  L.dials = buildControls('learnDials', [
    // (the labels are upper case, which would print the points z and c as capitals: class asis keeps them as typed)
    pd('zx', 'The point <span class="asis">z</span>, along x'), pd('zy', 'The point <span class="asis">z</span>, along y', () => L.space >= 2), pd('zz', 'The point <span class="asis">z</span>, along z', () => L.space === 3),
    pd('cx', 'The point <span class="asis">c</span>, along x'), pd('cy', 'The point <span class="asis">c</span>, along y', () => L.space >= 2), pd('cz', 'The point <span class="asis">c</span>, along z', () => L.space === 3),
    { type: 'select', key: 'show', label: 'Show', def: 'circle', options: [['point', 'The point alone'], ['circle', 'A small circle round the point'], ['all', 'All directions at once']],
      help: 'The companions take the same moves as the point, each by its own amount, so they show what a move does to everything near the point and not only to the point. On a line the circle is a short row of dots, and all directions is a row of dots along the line.' },
  ], store, () => learnVChanged(), { idPrefix: 'learn-', group: 'learn' });
  el.panel.querySelector('#learnZero').addEventListener('click', () => { L.set({ z: [0, 0, 0] }); learnVShowStage(); });
  el.panel.querySelector('#learnJuliaC').addEventListener('click', () => { L.set({ c: S.c.slice() }); learnVShowStage(); });
  // the kit puts its own controls back first; the points and the rest follow
  addReset('learnReset', 'learn', { after: () => { learnVDefaults(); learnVChanged(); } });

  if (!hooks.refresh.includes(learnVRefresh)) hooks.refresh.push(learnVRefresh);
  const retheme = () => { learnVTheme(); if (L.on) learnVNow(); };
  matchMedia('(prefers-color-scheme: dark)').addEventListener('change', retheme);
  new MutationObserver(retheme).observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] });
  new ResizeObserver(() => { if (L.on) learnVNow(); }).observe(stage);
  learnVTheme();
  if (typeof learnShapeInit === 'function') learnShapeInit();   // the choice "Follow" and the whole shape (67-learn-shape.js)
}

// ---------- for tests and the console: no pixels needed
// set({ space, z, c, show, hidden }): any of them. z and c are 3-vectors; what the space does not have is dropped.
LEARN.set = o => {
  const L = LEARN, vec = v => [0, 1, 2].map(i => (i < L.space && isFinite(+v[i]) ? clamp(+v[i], -8, 8) + 0 : 0));
  learnVStop();
  if (o.space !== undefined && [1, 2, 3].includes(+o.space) && +o.space !== L.space) { L.space = +o.space; L.k = 0; L.pos = 0; L.endSide = false; }
  if (o.z) { L.pts[L.space].z = vec(o.z); L.k = 0; }
  if (o.c) L.pts[L.space].c = vec(o.c);
  if (o.show !== undefined && ['point', 'circle', 'all'].includes(o.show)) L.show = o.show;
  if (o.hidden !== undefined && L.space < 3) L.hidden[L.space] = !!o.hidden;
  if (L.dials) { L.dials.sync(); L.checks.sync(); }
  learnVChanged();
  return L.state();
};
// goto(move, t): stand at the fraction t (0 to 1) of the move with that number, counted from 0.
LEARN.goto = (move, t = 0) => { const L = LEARN; if (L.stale) learnVBuild(); const n = L.cache.moves.length, j = clamp(Math.round(+move) || 0, 0, Math.max(0, n - 1)), f = clamp(+t || 0, 0, 1); learnVGoto(j + f, f >= 1); return L.state(); };
// next(): go on from the new point (false when the point has run away).
LEARN.next = () => learnVNextStep(false);
LEARN.again = () => { learnVAgain(); return LEARN.state(); };
LEARN.play = until => learnVPlay(until);
LEARN.setOn = on => { learnVSetOn(on); return LEARN.state(); };
LEARN.reset = () => learnReset();
LEARN.state = () => {
  const L = LEARN;
  if (L.stale || !L.cache) learnVBuild();
  const K = L.cache, a = learnVAt();
  return {
    on: L.on, space: L.space, z: K.orbit[L.k].slice(), z0: L.pts[L.space].z.slice(), c: L.pts[L.space].c.slice(), show: L.show,
    hidden: L.space < 3 ? !!L.hidden[L.space] : false, step: L.k, move: a.j, t: a.t, done: a.done, playing: L.playing,
    moves: K.names.slice(), sentence: !a.n ? K.fault : a.done ? K.doneText : K.say[a.j], note: K.note,
    point: learnVPoint(), end: K.end.slice(), away: K.away, orbit: K.orbit.map(v => v.slice()), fit: L.fit,
  };
};

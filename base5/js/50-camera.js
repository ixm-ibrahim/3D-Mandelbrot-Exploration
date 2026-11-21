// ---------- camera: one description of the view, and all the input that moves it.
// `cam` is an arcball: the eye sits `dist` away from `target`, in the direction given by yaw and pitch.
// Fly mode keeps the same four numbers and changes only what input does to them: looking around turns
// about the eye (the target is carried along, `dist` ahead of it) and the keys move eye and target together.
// So basis() never needs to know the mode, and switching modes cannot move the picture.
// The 2D view has its own three numbers, S.v2 { x, y, h }: the centre of the picture and its visible height.
const cam = { yaw: -1.0, pitch: 0.55, dist: 5.2, target: [-0.6, 0, 0] };

const CAM_DEF = { zmin: 0.005, zmax: 60, hmin: 0.0005, hmax: 40 };   // default zoom limits: camera distance, and height of the 2D view
const CAM_LIM = {                                                    // the hard range each limit, and the fly speed, is held to
  zmin: [1e-5, 500], zmax: [0.002, 1000], hmin: [1e-5, 500], hmax: [0.002, 2000], speed: [0.001, 100],
};
const CAM_EASE = 0.07;                     // seconds: a zoom covers 92% of the way to its goal in 180 ms, and no frame takes more than a fifth of what is left
const CAM_NOTCH = Math.log(1.12) / 100;    // one notch of a mouse wheel (100 px of scroll) changes the zoom by 12%
const CAM_STEP = 0.8;                      // one press of a zoom button, or of the plus and minus keys
const CAM_SHARP = 0.0005;                  // 2D view: closer than this the shader's numbers run out of digits and the picture turns blocky
const CAM_FOV0 = 0.32, CAM_FIT0 = CAM_FOV0 / Math.hypot(1, CAM_FOV0);   // the field of view the start framings were chosen at, and the sine of its half angle
const CAM_KEYS = {                         // movement keys by position on the keyboard: [axis, direction, also works outside fly mode]
  KeyW: [1, 1], KeyS: [1, -1], KeyA: [0, -1], KeyD: [0, 1], KeyE: [2, 1], KeyQ: [2, -1], Space: [2, 1], ShiftLeft: [2, -1], ShiftRight: [2, -1],
  ArrowUp: [1, 1, true], ArrowDown: [1, -1, true], ArrowLeft: [0, -1, true], ArrowRight: [0, 1, true],
};
const CAM_TEXT = {
  arc: { hint: 'Drag to turn. Scroll to zoom. Shift-drag to slide. Double-click a spot to move in on it.',
         touch: 'Drag to turn. Pinch to zoom. Drag with two fingers to slide. Double-tap a spot to move in on it.',
         view: 'The set for the chosen approach. Drag or use the arrow keys to turn it, plus and minus to zoom, F for the fly camera.',
         ends: ['near', 'far'], word: 'Distance', rail: 'Zoom: distance from the point the camera turns around',
         lims: ['Nearest distance the zoom may reach. At most half the farthest.', 'Farthest distance the zoom may reach. At least twice the nearest.'],
         names: ['nearest limit', 'farthest limit'],
         stop: ['This is the nearest the zoom may go. The box at the top of the slider sets that limit.',
                'This is the farthest the zoom may go. The box at the bottom of the slider sets that limit.'] },
  fly: { hint: 'Drag to look around. W A S D or the arrow keys move, Q and E go down and up. Scroll changes the speed.',
         touch: 'Drag to look around. Pinch to move forward or back. Drag with two fingers to move sideways. The slider sets the speed.',
         view: 'The set for the chosen approach, seen from a camera that flies. Drag to look around, W A S D or the arrow keys to move, Q and E to go down and up, F for the arcball camera.',
         ends: ['fast', 'slow'], word: 'Speed', rail: 'Fly speed, in scene units per second', lims: ['', ''] },
  flat: { hint: 'Drag to slide the picture. Scroll to zoom. Double-click a spot to centre it.',
          touch: 'Drag to slide the picture. Pinch to zoom. Double-tap a spot to centre it.',
          view: 'A flat slice of the set for the chosen approach. Drag or use the arrow keys to slide it, plus and minus to zoom.',
          // "span", never "height": on this page height is the z of the slice
          ends: ['in', 'out'], word: 'Span', rail: 'Zoom: how tall a piece of the slice fits in the picture',
          lims: ['Closest zoom: the smallest piece that may fill the picture. At most half the largest. Below ' + CAM_SHARP + ' the picture loses sharpness.',
                 'Widest zoom: the largest piece that may fill the picture. At least twice the smallest.'],
          names: ['closest zoom', 'widest zoom'],
          stop: ['This is the closest the zoom may go. The box at the top of the slider sets that limit. Below ' + CAM_SHARP + ' the picture loses sharpness.',
                 'This is the widest the zoom may go. The box at the bottom of the slider sets that limit.'],
          soft: 'Closer than ' + CAM_SHARP + ' the picture loses sharpness: the numbers behind it run out of digits.' },
};
const CV = {            // private bookkeeping
  init: false, bound: false, ui: null,
  ptr: new Map(),       // pointers that are down: id -> { x, y, el, x0, y0, t0 }
  tap: null, dblT: 0,   // the last quick tap of a finger, and when a double-click or double-tap was last acted on
  keys: new Set(),      // movement keys being held, by KeyboardEvent.code
  vel: [0, 0, 0],       // eased key motion along sideways, forward, up; each between -1 and 1
  velKind: '',          // the mode that motion belongs to
  goal: null,           // what the view is easing toward: { kind, and any of dist, target, h, at: { u, p }, centre }
  raf: 0, tmr: 0, last: 0, railPtr: null, speedTmr: 0, noteTmr: 0,
};

function camInit() {
  if (CV.init) return;
  CV.init = true;
  S.view.zmin = CAM_DEF.zmin; S.view.zmax = CAM_DEF.zmax;   // the camera's own defaults replace the ones the state starts with
  S.v2.hmin = S.v2.hmin ?? CAM_DEF.hmin; S.v2.hmax = S.v2.hmax ?? CAM_DEF.hmax;
}
const camKind = () => (S.flat ? 'flat' : S.view.fly ? 'fly' : 'arc');
const camOff = () => { const cp = Math.cos(cam.pitch); return [cp * Math.cos(cam.yaw), cp * Math.sin(cam.yaw), Math.sin(cam.pitch)]; };
function basis() {
  const off = camOff(), f = scl(off, -1), right = norm(cross(f, [0, 0, 1])), up = cross(right, f);
  return { pos: add(cam.target, scl(off, cam.dist)), right, up, f };
}
const clampDist = d => clamp(d, S.view.zmin, S.view.zmax);

// The sine of half the field of view: a ball of radius r just fits the picture's height from r / camFit() away.
const camFit = () => S.view.fov / Math.hypot(1, S.view.fov);
// The entry of the Julia or Kleinian list that the dials stand on, if it carries a camera chosen for it.
// The lists belong to the page (75-presets.js), so every name is asked for, never assumed. The user's own
// saved points are left out: their cameras are wherever the user happened to be.
function camListed() {
  let p = null;
  try {
    if (S.mode === 'j' && typeof juliaPresetAt === 'function' && S.eq === 'z^n + c' && Math.abs(S.n - 2) < 1e-9) p = juliaPresetAt();
    else if (S.mode === 'k' && typeof kleinPresetAt === 'function' && typeof KLEIN_PRESETS !== 'undefined') p = KLEIN_PRESETS[kleinPresetAt()];
  } catch (err) { p = null; }
  return p && p.cam && p.cam.dist > 0 && p.source !== 'saved' ? p : null;
}
// The start framing for what is on show: { yaw, pitch, dist, target, h }, where h is the matching span of the 2D view.
// `preset` may carry hints: an equation preset { target, dist } (meant for its Mandelbrot set), or anything with
// cam: { yaw, pitch, dist, target }, which is used exactly as given. Without one, the list entry the dials stand
// on is used, then the equation preset in use. Those and the built-in distances were chosen at a field of view
// of 0.32, so they are scaled to fit the solid the same way at the current one.
function camHome(preset) {
  const jul = S.mode === 'j', kl = S.mode === 'k', wide = !jul && !kl && Math.abs(S.n - 2) < 0.5;
  const v = { yaw: jul ? -1.25 : kl ? 0.35 : -1.0, pitch: jul ? 1.0 : kl ? 0.35 : 0.55, dist: kl ? 7 : wide ? 5.2 : 4.8, target: wide ? [-0.6, 0, 0] : [0, 0, 0] };
  // A negative power turns the solid inside out, and it then reaches further from the centre the nearer n is
  // to 0: about 1.3 + 1/|n|, measured on the pictures for n from -8 to -1.
  if (!kl && S.n < 0) v.dist = 3.8 * (1.3 + 1 / Math.max(1, -S.n));
  const listed = preset ? null : camListed(), p = preset || listed || PRESETS.find(q => q.eq === S.eq);
  let asGiven = false;
  if (p) {
    const c = p.cam || p, eqHint = c === p && p.eq !== undefined;
    if (!(eqHint && kl)) {
      if (Number.isFinite(c.yaw)) v.yaw = c.yaw;
      if (Number.isFinite(c.pitch)) v.pitch = clamp(c.pitch, -1.5, 1.5);
      if (c.dist > 0) { v.dist = c.dist; asGiven = !eqHint && !listed; }
      if (Array.isArray(c.target) && !(eqHint && jul)) v.target = c.target.slice(0, 3);
    }
  }
  // the 2D view shows what that camera sees of the plane through its target
  if (asGiven) v.h = 2 * v.dist * S.view.fov;
  else {
    v.h = 2 * CAM_FOV0 * v.dist;
    if (listed) {
      // list cameras were chosen on a wide stage: back off on a tall, narrow one. Every Julia entry fits a span of 3.6.
      v.dist *= Math.max(1, 1.2 * stage.clientHeight / Math.max(1, stage.clientWidth));
      if (jul) v.h = Math.max(v.h, 3.6);
    }
    v.dist *= CAM_FIT0 / camFit();
  }
  return v;
}
// Put the view back to the start for what is on show (see camHome for `preset`). `only` limits it to the
// '3d' camera or to the '2d' view; without it both are put back, as a change of mode or equation wants.
// The zoom limits the user set are kept: the start distance is held to them.
function resetCam(preset, only) {
  camInit();
  const v = camHome(preset);
  if (only !== '2d') {
    cam.yaw = v.yaw; cam.pitch = v.pitch; cam.dist = clampDist(v.dist); cam.target = v.target;
    if (S.view.fly) camFitSpeed();
  }
  if (only !== '3d') { S.v2.x = v.target[0]; S.v2.y = v.target[1]; S.v2.h = clamp(v.h, S.v2.hmin, S.v2.hmax); }
  CV.goal = null; CV.vel = [0, 0, 0];
}
// The Reset view button, and what a "frame it" control should call: a fresh framing of the view that is on
// screen. The other view (the 3D camera while the 2D view is up, and the other way round) is left as it is.
function resetView() { resetCam(undefined, S.flat ? '2d' : '3d'); touch(); }
// Hold the 3D distance to the zoom limits at once, without easing. A flying camera keeps its eye where it
// is: the pivot ahead of it moves instead.
function camHoldDist() {
  const d = clampDist(cam.dist);
  if (d === cam.dist) return;
  if (S.view.fly) cam.target = sub(basis().pos, scl(camOff(), d));
  cam.dist = d;
}
// Put the zoom limits (3D and 2D) back to their defaults, pulling both views inside them if need be.
function resetZoomLimits() {
  camInit();
  S.view.zmin = CAM_DEF.zmin; S.view.zmax = CAM_DEF.zmax; S.v2.hmin = CAM_DEF.hmin; S.v2.hmax = CAM_DEF.hmax;
  // the view on screen eases back inside (camIntoLimits); the one out of sight is simply held
  if (camKind() !== 'arc') camHoldDist();
  if (!S.flat) S.v2.h = clamp(S.v2.h, S.v2.hmin, S.v2.hmax);
  camIntoLimits();
}

function drawTriad() {
  // the 2D view looks straight down the z-axis, so z points at the viewer
  const b = S.flat ? { right: [1, 0, 0], up: [0, 1, 0], f: [0, 0, -1] } : basis();
  [[1, 0, 0], [0, 1, 0], [0, 0, 1]].forEach((v, i) => {
    const x = dot(v, b.right), y = dot(v, b.up), front = -dot(v, b.f) >= -0.05;
    const ln = $('ax' + i), tx = $('at' + i);
    if (!ln || !tx) return;
    // an axis seen end-on has no length to label, so its letter steps off the hub
    const lx = Math.hypot(x, y) < 0.2 ? -0.3 : x, ly = Math.hypot(x, y) < 0.2 ? -0.3 : y;
    ln.setAttribute('x2', (36 + 23 * x).toFixed(1)); ln.setAttribute('y2', (36 - 23 * y).toFixed(1));
    tx.setAttribute('x', (36 + 31 * lx).toFixed(1)); tx.setAttribute('y', (36 - 31 * ly).toFixed(1));
    ln.style.opacity = tx.style.opacity = front ? 1 : 0.4;
  });
}

// ---------- the zoom channel: the one quantity the wheel, a pinch and the stage slider change in the current mode
function camChan() {
  if (S.flat) return { key: 'h', v: S.v2.h, lo: S.v2.hmin, hi: S.v2.hmax };
  if (S.view.fly) return { key: 'speed', v: S.view.speed, lo: CAM_LIM.speed[0], hi: CAM_LIM.speed[1] };
  return { key: 'dist', v: cam.dist, lo: S.view.zmin, hi: S.view.zmax };
}
// Position on the slider, 0 at the top and 1 at the bottom, on a log scale. The top is near (zoom) or fast (speed).
function camT(ch, v) {
  const span = Math.log(ch.hi / ch.lo), t = span > 0 ? clamp(Math.log(v / ch.lo) / span, 0, 1) : 0.5;
  return ch.key === 'speed' ? 1 - t : t;
}
const camAtT = (ch, t) => ch.lo * Math.pow(ch.hi / ch.lo, ch.key === 'speed' ? 1 - t : t);
// the easing in progress, if it was set in the current mode (a goal means nothing in another mode)
const camLive = () => (CV.goal && CV.goal.kind === camKind() ? CV.goal : null);
// where the channel is heading: the goal of that easing, else its value now
const camAim = ch => { const g = camLive(); return (g && (ch.key === 'dist' ? g.dist : ch.key === 'h' ? g.h : 0)) || ch.v; };
const camFmt = v => { const a = Math.abs(v); return a > 0 ? String(+v.toFixed(clamp(2 - Math.floor(Math.log10(a)), 0, 6))) : '0'; };
// 2D view: where a stage pixel sits, in units of half the picture height from the centre (the shader's uv)
const camFlatUv = (px, py) => { const r = canvas.getBoundingClientRect(), h = Math.max(1, r.height); return [(2 * px - r.width) / h, (h - 2 * py) / h]; };

// Add to what the view is easing toward.
function camGoal(patch) { CV.goal = Object.assign(camLive() || { kind: camKind() }, patch); camWake(); }
// Ask for a new value of the channel. Zoom eases to it; `at` (2D only) is the stage pixel that must stay put.
function camZoomTo(v, at) {
  const ch = camChan(), asked = v;
  v = clamp(v, ch.lo, ch.hi);
  if (ch.key === 'speed') { S.view.speed = v; camSpeedChanged(); return; }
  // asked to go on past a limit the view already rests on: say why nothing moves
  if (asked !== v && camAim(ch) === v) camNote(CAM_TEXT[camKind()].stop[v === ch.lo ? 0 : 1]);
  if (ch.key === 'dist') { camGoal({ dist: v }); return; }
  if (v < CAM_SHARP && camAim(ch) >= CAM_SHARP) camNote(CAM_TEXT.flat.soft);
  let hold = null;
  if (at) { const u = camFlatUv(at[0], at[1]); hold = { u, p: [S.v2.x + u[0] * S.v2.h / 2, S.v2.y + u[1] * S.v2.h / 2] }; }
  camGoal({ h: v, at: hold, centre: null });
}
// Scroll by a factor: above 1 backs away (or, when flying, slows down), below 1 moves in (or speeds up).
function camZoomBy(f, at) { const ch = camChan(); camZoomTo(ch.key === 'speed' ? ch.v / f : camAim(ch) * f, at); }
// The zoom buttons and the plus and minus keys: one eased step. A flying camera has no zoom, so it moves along its view.
function camStep(f) {
  if (camKind() !== 'fly') { camZoomBy(f); return; }
  const g = camLive();
  camGoal({ target: add(g && g.target ? g.target : cam.target, scl(basis().f, -2 * Math.log(f) * S.view.speed)) });
}
function camIntoLimits() {      // after the limits changed: pull the view, or whatever it is easing toward, back inside them
  const ch = camChan(), aim = camAim(ch), v = clamp(aim, ch.lo, ch.hi);
  if (ch.key !== 'speed' && v !== aim) camZoomTo(v);
  viewChanged();
}
function camSpeedChanged() {
  viewChanged();
  // a fly-speed dial elsewhere on the page follows, once the scrolling pauses
  clearTimeout(CV.speedTmr); CV.speedTmr = setTimeout(syncControls, 150);
}
// A fly speed left over from another scale would cross the view in under a second, or take most of a minute.
// Then start at a quarter of the distance to the pivot per second; the wheel takes it from there.
function camFitSpeed() {
  if (S.view.speed <= cam.dist && S.view.speed >= cam.dist / 40) return;
  S.view.speed = clamp(cam.dist / 4, CAM_LIM.speed[0], CAM_LIM.speed[1]);
  camSpeedChanged();
}
// A short message on the stage (why the zoom stopped, why a typed limit was not taken). It goes away by itself.
function camNote(text) {
  const el = CV.ui && CV.ui.note;
  if (!el) return;
  clearTimeout(CV.noteTmr);
  if (el.textContent !== text) el.textContent = text;
  el.hidden = !text;
  if (text) CV.noteTmr = setTimeout(() => { el.hidden = true; }, 6000);
}

// ---------- easing and held keys: a frame loop that runs only while something is moving
function camWake() {
  touch();   // at once, so the renderer knows a change is under way before the first eased frame
  if (CV.raf) return;
  CV.last = performance.now();
  camNext();
}
function camNext() {   // the next animation frame, or a timer when the page is in the background and frames are paused
  const run = () => { cancelAnimationFrame(CV.raf); clearTimeout(CV.tmr); CV.raf = 0; camTick(); };
  CV.raf = requestAnimationFrame(run); CV.tmr = setTimeout(run, 250);
}
// one eased step of a positive number toward its goal, on a log scale: never past it, and exact once within 0.1%
const camEase = (v, goal, k) => { const l = Math.log(goal / v); return Math.abs(l) < 1e-3 ? goal : v * Math.exp(l * k); };
function camTick() {
  const now = performance.now(), dt = clamp((now - CV.last) / 1000, 0, 0.1), kind = camKind();
  CV.last = now;
  if (CV.velKind !== kind) { CV.velKind = kind; CV.vel = [0, 0, 0]; }
  const g = CV.goal = camLive();
  let live = false;
  if (g) {
    // someone who asked for less motion gets the new view at once
    const k = matchMedia('(prefers-reduced-motion: reduce)').matches ? 1 : 1 - Math.exp(-dt / CAM_EASE);
    let open = 0;
    if (g.dist) { cam.dist = camEase(cam.dist, g.dist, k); if (cam.dist !== g.dist) open++; }
    if (g.target) {
      const d = sub(g.target, cam.target);
      if (len(d) < 1e-3 * cam.dist) cam.target = g.target.slice(); else { cam.target = add(cam.target, scl(d, k)); open++; }
    }
    if (g.h) {
      S.v2.h = camEase(S.v2.h, g.h, k);
      if (g.at) { S.v2.x = g.at.p[0] - g.at.u[0] * S.v2.h / 2; S.v2.y = g.at.p[1] - g.at.u[1] * S.v2.h / 2; }
      if (S.v2.h !== g.h) open++;
    }
    if (g.centre) {
      const dx = g.centre[0] - S.v2.x, dy = g.centre[1] - S.v2.y;
      if (Math.hypot(dx, dy) < 1e-3 * S.v2.h) { S.v2.x = g.centre[0]; S.v2.y = g.centre[1]; } else { S.v2.x += dx * k; S.v2.y += dy * k; open++; }
    }
    if (open) live = true; else CV.goal = null;
  }
  // held keys push a velocity that eases in and out, so starts and stops are soft
  const want = [0, 0, 0], kv = 1 - Math.exp(-dt / 0.07);
  CV.keys.forEach(code => { const m = CAM_KEYS[code]; if (kind === 'fly' || m[2]) want[m[0]] += m[1]; });
  CV.vel = CV.vel.map((v, i) => v + (clamp(want[i], -1, 1) - v) * kv);
  if (CV.keys.size || len(CV.vel) > 0.004) {
    const [vx, vy, vz] = CV.vel;
    if (kind === 'fly') {
      const b = basis(), s = S.view.speed * dt;
      cam.target = add(cam.target, add(add(scl(b.right, vx * s), scl(b.f, vy * s)), [0, 0, vz * s]));
      if (CV.goal) CV.goal.target = null;
    } else if (kind === 'flat') camFlatShift(vx * 0.9 * S.v2.h * dt, vy * 0.9 * S.v2.h * dt);
    else { cam.yaw += vx * 1.4 * dt; cam.pitch = clamp(cam.pitch + vy * 1.4 * dt, -1.5, 1.5); }
    live = true;
  } else CV.vel = [0, 0, 0];
  touch();
  if (live) camNext();
}

// ---------- what a drag, a pinch and a double-click do
function camTurn(dx, dy) {      // drag by (dx, dy) pixels: turn about the target, or about the eye when flying
  if (!S.view.fly) { cam.yaw -= dx * 0.008; cam.pitch = clamp(cam.pitch + dy * 0.008, -1.5, 1.5); return; }
  const eye = basis().pos;
  cam.yaw -= dx * 0.004; cam.pitch = clamp(cam.pitch + dy * 0.004, -1.5, 1.5);
  cam.target = sub(eye, scl(camOff(), cam.dist));
  if (CV.goal) CV.goal.target = null;
}
function camSlide(dx, dy) {     // drag by (dx, dy) pixels: carry the scene sideways with the pointer
  const b = basis(), ref = S.view.fly ? 3 * S.view.speed : cam.dist, s = ref * 2 * S.view.fov / Math.max(1, stage.clientHeight);
  cam.target = add(cam.target, add(scl(b.right, -dx * s), scl(b.up, dy * s)));
  if (CV.goal) CV.goal.target = null;
}
function camFlatShift(dx, dy) {   // 2D view: move the centre by a scene distance, along with whatever a zoom is holding still
  S.v2.x += dx; S.v2.y += dy;
  const g = CV.goal;
  if (g && g.at) { g.at.p[0] += dx; g.at.p[1] += dy; }
  if (g) g.centre = null;
}
function camFlatDrag(dx, dy) { const s = S.v2.h / Math.max(1, canvas.getBoundingClientRect().height); camFlatShift(-dx * s, dy * s); }
function camPinch(f, at) {      // fingers moved apart (f < 1) or together. No easing here: the fingers are the easing.
  const g = CV.goal;
  if (S.flat) {
    const h = clamp(S.v2.h * f, S.v2.hmin, S.v2.hmax), u = camFlatUv(at[0], at[1]), k = (S.v2.h - h) / 2;
    S.v2.x += u[0] * k; S.v2.y += u[1] * k; S.v2.h = h;
    if (g) g.h = g.at = null;
  } else if (S.view.fly) cam.target = add(cam.target, scl(basis().f, -1.5 * Math.log(f) * S.view.speed));
  else { cam.dist = clampDist(cam.dist * f); if (g) g.dist = null; }
}
function camBindDrag(el, main) {   // main: the stage canvas. Otherwise a small figure that shares the camera and only turns it.
  el.addEventListener('pointerdown', e => {
    try { el.setPointerCapture(e.pointerId); } catch (err) { /* a pointer that is already gone cannot be captured; the drag still works while it stays over the element */ }
    CV.ptr.set(e.pointerId, { x: e.clientX, y: e.clientY, el, x0: e.clientX, y0: e.clientY, t0: performance.now() });
  });
  el.addEventListener('pointermove', e => {
    const p = CV.ptr.get(e.pointerId);
    if (!p || p.el !== el) return;
    const dx = e.clientX - p.x, dy = e.clientY - p.y;
    if (!dx && !dy) return;
    if (!main) {
      p.x = e.clientX; p.y = e.clientY;
      camTurn(dx, dy);
      if (S.flat) viewChanged(); else touch();   // the flat picture does not depend on the camera; the small figure does
      return;
    }
    const other = [...CV.ptr.values()].find(q => q.el === el && q !== p);
    if (other) {
      // two fingers: the change in their spread zooms about the point that was between them, then that point
      // follows them (half of this finger's movement). Together the two keep each finger on the spot it touched.
      const d0 = Math.hypot(p.x - other.x, p.y - other.y), r = el.getBoundingClientRect();
      const mid = [(p.x + other.x) / 2 - r.left, (p.y + other.y) / 2 - r.top];
      p.x = e.clientX; p.y = e.clientY;
      const d1 = Math.hypot(p.x - other.x, p.y - other.y);
      if (d0 > 0 && d1 > 0) camPinch(d0 / d1, mid);
      if (S.flat) camFlatDrag(dx / 2, dy / 2); else camSlide(dx / 2, dy / 2);
    } else {
      p.x = e.clientX; p.y = e.clientY;
      if (S.flat) camFlatDrag(dx, dy);
      else if ((e.shiftKey && !S.view.fly) || (e.buttons & 6)) camSlide(dx, dy);   // when flying, Shift is the key for going down
      else camTurn(dx, dy);
    }
    touch();
  });
  const end = e => {
    const p = CV.ptr.get(e.pointerId), now = performance.now();
    CV.ptr.delete(e.pointerId);
    // Two quick taps of a finger count as a double-click: not every touch browser sends that event itself.
    if (!main || !p || e.type !== 'pointerup' || e.pointerType === 'mouse' || CV.ptr.size || now - p.t0 > 300 || Math.hypot(e.clientX - p.x0, e.clientY - p.y0) > 10) return;
    const t = CV.tap;
    CV.tap = { t: now, x: e.clientX, y: e.clientY };
    if (t && now - t.t < 350 && Math.hypot(e.clientX - t.x, e.clientY - t.y) < 30) { CV.tap = null; camDblClick(e); }
  };
  el.addEventListener('pointerup', end); el.addEventListener('pointercancel', end);
}
// The wheel anywhere on the stage, the controls that sit on the picture included: the page must not scroll
// away under a pointer that rests on the plus button or a limit box.
function camWheel(e) {
  const fail = $('glfail');
  if (fail && !fail.hidden) return;   // no picture to zoom, so the wheel scrolls the page as usual
  e.preventDefault();
  // lines and pages become pixels; a pinch on a trackpad arrives as a wheel event with the control key set, in much smaller units
  const px = clamp(e.deltaY * (e.deltaMode === 1 ? 100 / 3 : e.deltaMode === 2 ? 300 : 1) * (e.ctrlKey ? 8 : 1), -300, 300);
  if (!px) return;
  // Over the picture the 2D zoom holds the spot under the pointer. Over a control it is about the middle, as that control's own zoom is.
  const r = canvas.getBoundingClientRect(), onCtl = e.target !== canvas && e.target.closest && e.target.closest('.cam-zoom, .cam-mode, .stage-btns');
  camZoomBy(Math.exp(px * CAM_NOTCH), onCtl ? null : [e.clientX - r.left, e.clientY - r.top]);
}
function camDblClick(e) {       // a double-click, or the second of two taps
  const r = canvas.getBoundingClientRect(), px = e.clientX - r.left, py = e.clientY - r.top, now = performance.now();
  if (now - CV.dblT < 300) return;   // a browser that sends both must not be answered twice
  CV.dblT = now;
  if (S.flat) {
    const u = camFlatUv(px, py);
    camGoal({ centre: [S.v2.x + u[0] * S.v2.h / 2, S.v2.y + u[1] * S.v2.h / 2], at: null });
    return;
  }
  const hit = pick(px, py);
  if (hit) camGoal({ target: hit, dist: clampDist(len(sub(basis().pos, hit)) * 0.55) });
}
function camKeyDown(e) {
  if (e.ctrlKey || e.metaKey || e.altKey) return;
  const kind = camKind(), m = CAM_KEYS[e.code];
  if (m && (kind === 'fly' || m[2])) { if (!CV.keys.has(e.code)) { CV.keys.add(e.code); camWake(); } }
  else if (e.key === '+' || e.key === '=') camStep(CAM_STEP);
  else if (e.key === '-' || e.key === '_') camStep(1 / CAM_STEP);
  else if (e.code === 'KeyF' && kind !== 'flat' && !e.repeat) setCamMode(!S.view.fly);
  else return;
  e.preventDefault();
}

// Switch between the arcball (false) and the fly camera (true). The eye and the view direction stay as they are.
function setCamMode(fly) {
  fly = !!fly;
  if (S.view.fly === fly) return;
  CV.goal = null; CV.vel = [0, 0, 0];
  if (!fly) {
    // turn around the spot in the middle of the picture if there is one, else around a point `dist` ahead
    const b = basis(), hit = S.flat ? null : pick(stage.clientWidth / 2, stage.clientHeight / 2);
    cam.dist = clampDist(hit ? len(sub(hit, b.pos)) : cam.dist);
    cam.target = add(b.pos, scl(b.f, cam.dist));
  } else camFitSpeed();
  S.view.fly = fly;
  touch();
}

// ---------- overlays on the stage: the camera switch and the zoom slider with its two limit boxes
function camParse(text) {       // a typed number; spaces, a unicode minus and a decimal comma are fine
  const s = String(text).trim().replace(/\u2212/g, '-').replace(',', '.');
  return /^[-+]?(\d+\.?\d*|\.\d+)(e[-+]?\d+)?$/i.test(s) ? parseFloat(s) : NaN;
}
// Set the nearest (end 0) or farthest (end 1) zoom limit of the current view from a typed value.
// -> '' when it was taken exactly as typed, else a sentence for the user saying what happened instead.
// The two limits stay a factor 2 apart. A value on the wrong side of that is refused, not bent into a number
// nobody typed (bending the near limit up to half the far one used to carry the camera far away).
function camSetLimit(end, v) {
  const kind = camKind();
  if (kind === 'fly') return 'The fly camera has no zoom limits.';
  if (!(v > 0) || !isFinite(v)) return 'A zoom limit is a number above zero.';
  const o = S.flat ? S.v2 : S.view, [a, b] = S.flat ? ['hmin', 'hmax'] : ['zmin', 'zmax'], names = CAM_TEXT[kind].names;
  if (end === 0 && v > o[b] / 2) return `The ${names[0]} can be at most half the ${names[1]}, so ${camFmt(o[b] / 2)} or less here. To go above that, raise the ${names[1]} first.`;
  if (end === 1 && v < o[a] * 2) return `The ${names[1]} must be at least twice the ${names[0]}, so ${camFmt(o[a] * 2)} or more here. To go below that, lower the ${names[0]} first.`;
  const key = end ? b : a, [lo, hi] = CAM_LIM[key], w = clamp(v, lo, hi);
  o[key] = w;
  camIntoLimits();
  if (w !== v) return `The ${names[end]} is kept between ${camFmt(lo)} and ${camFmt(hi)}.`;
  if (S.flat && end === 0 && w < CAM_SHARP) camNote(CAM_TEXT.flat.soft);
  return '';
}
function camLimitBox(inp, end) {
  const show = () => { const ch = camChan(); inp.value = camFmt(end ? ch.hi : ch.lo); inp.dataset.dirty = ''; };
  const commit = () => {
    if (!inp.dataset.dirty) return;
    const why = camSetLimit(end, camParse(inp.value));
    show();
    if (why) {
      // the box shows a number that was not typed: flag it for a moment and say why
      inp.setAttribute('aria-invalid', 'true'); setTimeout(() => inp.removeAttribute('aria-invalid'), 900);
      camNote(why);
    }
  };
  inp.addEventListener('input', () => { inp.dataset.dirty = '1'; });
  inp.addEventListener('blur', commit);
  inp.addEventListener('keydown', e => {
    if (e.key === 'Enter') { e.preventDefault(); commit(); inp.select(); }
    else if (e.key === 'Escape') { e.preventDefault(); show(); inp.select(); }
  });
}
function camBuildUi() {
  const mode = document.createElement('div'), zoom = document.createElement('div');
  mode.className = 'cam-mode'; mode.id = 'camMode'; mode.setAttribute('role', 'group'); mode.setAttribute('aria-label', 'Camera');
  mode.innerHTML = '<button type="button" id="camArc" title="Turn the camera around a point (F)">Arcball</button>' +
    '<button type="button" id="camFly" title="Move the camera freely, first person (F)">Fly</button>';
  zoom.className = 'cam-zoom'; zoom.id = 'camZoom';
  zoom.innerHTML = '<span class="cam-end" id="camEndA"></span>' +
    '<input class="cam-lim" id="camNear" type="text" inputmode="decimal" autocomplete="off" spellcheck="false">' +
    '<div class="cam-rail" id="camRail" role="slider" tabindex="0" aria-orientation="vertical" aria-valuemin="0" aria-valuemax="100">' +
    '<span class="cam-ticks" id="camTicks"></span><span class="cam-thumb" id="camThumb"><span class="cam-val" id="camVal"></span></span></div>' +
    '<input class="cam-lim" id="camFar" type="text" inputmode="decimal" autocomplete="off" spellcheck="false">' +
    '<span class="cam-end" id="camEndB"></span>';
  const note = document.createElement('p');
  note.className = 'cam-note'; note.id = 'camNote'; note.hidden = true; note.setAttribute('role', 'status');
  stage.append(mode, zoom, note);
  const ui = CV.ui = { kind: '', ticks: '', top: '', mode, note, hint: stage.querySelector('.hint'), touch: matchMedia('(hover: none) and (pointer: coarse)').matches };
  for (const id of ['camArc', 'camFly', 'camEndA', 'camEndB', 'camNear', 'camFar', 'camRail', 'camTicks', 'camThumb', 'camVal']) ui[id] = $(id);
  const pickMode = fly => e => {
    setCamMode(fly);
    if (e.detail > 0) canvas.focus({ preventScroll: true });   // after a click with a pointer the movement keys should work straight away
  };
  ui.camArc.addEventListener('click', pickMode(false)); ui.camFly.addEventListener('click', pickMode(true));
  camLimitBox(ui.camNear, 0); camLimitBox(ui.camFar, 1);
  const rail = ui.camRail;
  const fromY = y => { const r = rail.getBoundingClientRect(); camZoomTo(camAtT(camChan(), clamp((y - r.top) / Math.max(1, r.height), 0, 1))); };
  rail.addEventListener('pointerdown', e => {
    try { rail.setPointerCapture(e.pointerId); } catch (err) { /* see camBindDrag */ }
    CV.railPtr = e.pointerId; fromY(e.clientY);
  });
  rail.addEventListener('pointermove', e => { if (CV.railPtr === e.pointerId) fromY(e.clientY); });
  const railEnd = e => { if (CV.railPtr === e.pointerId) CV.railPtr = null; };
  rail.addEventListener('pointerup', railEnd); rail.addEventListener('pointercancel', railEnd);
  rail.addEventListener('keydown', e => {
    const ch = camChan(), t = camT(ch, camAim(ch)), step = { ArrowUp: -0.02, ArrowDown: 0.02, PageUp: -0.1, PageDown: 0.1, End: -1, Home: 1 }[e.key];
    if (step === undefined || e.ctrlKey || e.metaKey || e.altKey) return;
    e.preventDefault(); camZoomTo(camAtT(ch, clamp(t + step, 0, 1)));
  });
}
// Make the overlays show the current mode, value and limits. Runs after every change of the view.
function camSync() {
  const ui = CV.ui;
  if (!ui) return;
  const kind = camKind(), ch = camChan(), tx = CAM_TEXT[kind];
  if (ui.kind !== kind) {
    ui.kind = kind; stage.dataset.cam = kind;
    camNote('');   // a message about the other view's zoom means nothing here
    ui.top = ''; ui.camVal.textContent = '';   // so the slider's position and wording are written afresh below
    if (ui.hint) ui.hint.textContent = ui.touch ? tx.touch : tx.hint;
    canvas.setAttribute('aria-label', tx.view);
    ui.mode.hidden = kind === 'flat';
    ui.camArc.setAttribute('aria-pressed', String(kind === 'arc')); ui.camFly.setAttribute('aria-pressed', String(kind === 'fly'));
    ui.camEndA.textContent = tx.ends[0]; ui.camEndB.textContent = tx.ends[1];
    ui.camNear.hidden = ui.camFar.hidden = kind === 'fly';
    ui.camNear.title = tx.lims[0]; ui.camFar.title = tx.lims[1];
    ui.camNear.setAttribute('aria-label', tx.lims[0]); ui.camFar.setAttribute('aria-label', tx.lims[1]);
    ui.camRail.title = tx.rail; ui.camRail.setAttribute('aria-label', kind === 'fly' ? 'Fly speed' : 'Zoom');
  }
  [[ui.camNear, ch.lo], [ui.camFar, ch.hi]].forEach(([inp, v]) => { const s = camFmt(v); if (!inp.dataset.dirty && inp.value !== s) inp.value = s; });
  const t = camT(ch, ch.v), val = camFmt(ch.v), top = (t * 100).toFixed(2) + '%';
  if (ui.top !== top) {
    ui.top = top; ui.camThumb.style.top = top;
    ui.camRail.setAttribute('aria-valuenow', String(Math.round((1 - t) * 100)));
  }
  if (ui.camVal.textContent !== val) {
    ui.camVal.textContent = val;
    ui.camRail.setAttribute('aria-valuetext', `${tx.word} ${val}${kind === 'fly' ? ' per second' : ''}`);
  }
  // a tick at every power of ten between the limits, a longer one at 1
  const key = kind + ch.lo + '|' + ch.hi;
  if (ui.ticks !== key) {
    ui.ticks = key;
    let html = '';
    for (let p = Math.ceil(Math.log10(ch.lo) + 1e-9); Math.pow(10, p) < ch.hi * (1 - 1e-9); p++) {
      if (Math.pow(10, p) > ch.lo * (1 + 1e-9)) html += `<i class="cam-tick${p === 0 ? ' is-one' : ''}" style="top:${(camT(ch, Math.pow(10, p)) * 100).toFixed(2)}%"></i>`;
    }
    ui.camTicks.innerHTML = html;
  }
}

function bindView() {
  if (CV.bound) return;
  CV.bound = true;
  camInit(); camBuildUi();
  camBindDrag(canvas, true);
  if ($('step3d')) camBindDrag($('step3d'), false);
  canvas.addEventListener('contextmenu', e => e.preventDefault());
  stage.addEventListener('wheel', camWheel, { passive: false });
  canvas.addEventListener('dblclick', camDblClick);
  canvas.addEventListener('keydown', camKeyDown);
  // a key released anywhere, or focus lost, must never leave the camera moving
  window.addEventListener('keyup', e => { CV.keys.delete(e.code); });
  canvas.addEventListener('blur', () => CV.keys.clear());
  window.addEventListener('blur', () => CV.keys.clear());
  // After a click with a pointer the keyboard goes to the picture, as it does after the Arcball and Fly buttons:
  // W A S D must keep flying straight after Reset view, and Space must not press the button a second time.
  const on = (id, fn) => { if ($(id)) $(id).addEventListener('click', e => { fn(); if (e.detail > 0) canvas.focus({ preventScroll: true }); }); };
  on('zoomIn', () => camStep(CAM_STEP)); on('zoomOut', () => camStep(1 / CAM_STEP));
  on('reset', resetView);
  for (const f of [drawTriad, camSync]) if (!hooks.view.includes(f)) hooks.view.push(f);
  camSync();
}

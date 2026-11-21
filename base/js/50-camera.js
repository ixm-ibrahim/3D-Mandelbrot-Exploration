const cam = { yaw: -1.0, pitch: 0.55, dist: 5.2, target: [-0.6, 0, 0] };
function resetCam(preset) {
  const jul = S.mode === 'j', kl = S.mode === 'k', wide = !jul && !kl && S.n < 2.5;
  cam.yaw = jul ? -1.25 : kl ? 0.35 : -1.0; cam.pitch = jul ? 1.0 : kl ? 0.35 : 0.55;
  cam.dist = kl ? 7 : wide ? 5.2 : 4.8; cam.target = wide ? [-0.6, 0, 0] : [0, 0, 0];
  const p = preset || PRESETS.find(q => q.eq === S.eq);
  if (p && !kl) { if (p.target && !jul) cam.target = p.target.slice(); if (p.dist) cam.dist = p.dist; }
}
function basis() {
  const cp = Math.cos(cam.pitch), sp = Math.sin(cam.pitch), cy = Math.cos(cam.yaw), sy = Math.sin(cam.yaw);
  const off = [cp * cy, cp * sy, sp];
  const f = scl(off, -1), right = norm(cross(f, [0, 0, 1])), up = cross(right, f);
  return { pos: add(cam.target, scl(off, cam.dist)), right, up, f };
}
const clampDist = d => clamp(d, S.view.zmin, S.view.zmax);

function drawTriad() {
  const b = basis();
  [[1, 0, 0], [0, 1, 0], [0, 0, 1]].forEach((v, i) => {
    const x = dot(v, b.right), y = dot(v, b.up), front = -dot(v, b.f) >= -0.05;
    const ln = $('ax' + i), tx = $('at' + i);
    ln.setAttribute('x2', (36 + 23 * x).toFixed(1)); ln.setAttribute('y2', (36 - 23 * y).toFixed(1));
    tx.setAttribute('x', (36 + 31 * x).toFixed(1)); tx.setAttribute('y', (36 - 31 * y).toFixed(1));
    ln.style.opacity = tx.style.opacity = front ? 1 : 0.4;
  });
}

// ---------- pointer, wheel and keyboard control
const pointers = new Map();
function orbit(dx, dy) { cam.yaw -= dx * 0.008; cam.pitch = clamp(cam.pitch + dy * 0.008, -1.5, 1.5); }
function pan(dx, dy) {
  const b = basis(), s = cam.dist * 2 * S.view.fov / Math.max(1, stage.clientHeight);
  cam.target = add(cam.target, add(scl(b.right, -dx * s), scl(b.up, dy * s)));
}
function bindDrag(el, allowPan) {
  el.addEventListener('pointerdown', e => { el.setPointerCapture(e.pointerId); pointers.set(e.pointerId, { x: e.clientX, y: e.clientY, el }); });
  el.addEventListener('pointermove', e => {
    const p = pointers.get(e.pointerId);
    if (!p || p.el !== el) return;
    const dx = e.clientX - p.x, dy = e.clientY - p.y;
    const mine = [...pointers.values()].filter(q => q.el === el);
    if (mine.length >= 2 && allowPan) {
      const o = mine.find(q => q !== p), d0 = Math.hypot(p.x - o.x, p.y - o.y);
      p.x = e.clientX; p.y = e.clientY;
      const d1 = Math.hypot(p.x - o.x, p.y - o.y);
      if (d0 > 0 && d1 > 0) cam.dist = clampDist(cam.dist * d0 / d1);
      pan(dx / 2, dy / 2);
    } else {
      p.x = e.clientX; p.y = e.clientY;
      if (allowPan && (e.shiftKey || (e.buttons & 6))) pan(dx, dy); else orbit(dx, dy);
    }
    touch();
  });
  const end = e => { pointers.delete(e.pointerId); };
  el.addEventListener('pointerup', end); el.addEventListener('pointercancel', end);
}
function bindView() {
  bindDrag(canvas, true);
  bindDrag($('step3d'), false);
  canvas.addEventListener('contextmenu', e => e.preventDefault());
  canvas.addEventListener('wheel', e => {
    e.preventDefault();
    cam.dist = clampDist(cam.dist * Math.exp((e.deltaMode === 1 ? e.deltaY * 32 : e.deltaY) * 0.0015));
    touch();
  }, { passive: false });
  canvas.addEventListener('dblclick', e => {
    const r = canvas.getBoundingClientRect(), hit = pick(e.clientX - r.left, e.clientY - r.top);
    if (!hit) return;
    cam.dist = clampDist(len(sub(basis().pos, hit)) * 0.55);
    cam.target = hit;
    touch();
  });
  canvas.addEventListener('keydown', e => {
    const k = e.key;
    if (k === 'ArrowLeft') orbit(12, 0); else if (k === 'ArrowRight') orbit(-12, 0);
    else if (k === 'ArrowUp') orbit(0, 12); else if (k === 'ArrowDown') orbit(0, -12);
    else if (k === '+' || k === '=') cam.dist = clampDist(cam.dist * 0.85);
    else if (k === '-' || k === '_') cam.dist = clampDist(cam.dist / 0.85);
    else return;
    e.preventDefault(); touch();
  });
  $('zoomIn').addEventListener('click', () => { cam.dist = clampDist(cam.dist * 0.8); touch(); });
  $('zoomOut').addEventListener('click', () => { cam.dist = clampDist(cam.dist / 0.8); touch(); });
  $('reset').addEventListener('click', () => { resetCam(); touch(); });
}

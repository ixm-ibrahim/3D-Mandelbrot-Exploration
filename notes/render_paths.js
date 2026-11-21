//// wait=done
// Less-travelled paths of the renderer: 3D picking, a failed formula, a driver without parallel compile,
// paused animation frames, a lost and restored WebGL context, and a resized stage.
// Needs a build whose boot file exposes pick and basis (out/render/90-boot-test.js).
const L = window.squaringLab; L.R.warmOn = false; L.S.q.aa = 2; L.touch(); return 'ready';
//// wait=done
const L = window.squaringLab, st = document.getElementById('stage'), w = st.clientWidth, h = st.clientHeight, out = [];
// a picked point, pushed back through the camera, must land on the pixel it was picked at
const b = L.basis(), fov = L.S.view.fov;
let hits = 0, worst = 0;
for (let j = 1; j < 8; j++) for (let i = 1; i < 10; i++) {
  const px = i * w / 10, py = j * h / 8, p = L.pick(px, py);
  if (!p) continue;
  hits++;
  const d = [p[0] - b.pos[0], p[1] - b.pos[1], p[2] - b.pos[2]], dot = (a, c) => a[0] * c[0] + a[1] * c[1] + a[2] * c[2];
  const ux = dot(d, b.right) / dot(d, b.f) / fov, uy = dot(d, b.up) / dot(d, b.f) / fov;
  worst = Math.max(worst, Math.hypot((ux * h + w) / 2 - px, (h - uy * h) / 2 - py));
}
out.push(`3D pick: ${hits} of 63 grid positions hit the solid, corner (2, 2) gives ${JSON.stringify(L.pick(2, 2))}, worst round trip ${worst.toFixed(3)} px`);
return out;
//// sleep=0.4
const L = window.squaringLab; L.S.eq = 'z^^2 + c'; L.touch(); return 'a formula that cannot be read (one console error is expected)';
//// shot=out/render/paths-1-badformula.png clip=#stage
const L = window.squaringLab, g = document.getElementById('glfail'), b = document.getElementById('busy');
return `bad formula: message shown ${!g.hidden} ("${g.textContent}"), busy label hidden ${!b || b.hidden}, idle ${L.idle()}, status "${document.getElementById('status').textContent}"`;
//// wait=done
const L = window.squaringLab; L.S.eq = 'z^n + c'; L.touch(); return 'formula put right';
//// 
const L = window.squaringLab, $ = id => document.getElementById(id), sleep = ms => new Promise(r => setTimeout(r, ms));
const out = [`recovered: message hidden ${$('glfail').hidden}, status "${$('status').textContent}"`];
// no parallel compile: the label must be on screen for at least one frame before the page blocks
L.R.par = null;
let frames = [], last = performance.now(), on = true, busyBefore = 0, blocked = false;
(function tick() {
  const t = performance.now(), gap = t - last; last = t; frames.push(gap);
  if (gap > 150) blocked = true;
  const b = $('busy'); if (!blocked && b && !b.hidden) busyBefore++;
  if (on) requestAnimationFrame(tick);
})();
await sleep(100); frames = []; blocked = false; busyBefore = 0;
const c0 = L.R.compiles;
L.S.approach = +$('ap-lathe').value; L.touch();
while (!L.idle()) await sleep(10);
on = false;
out.push(`without parallel compile: ${L.R.compiles - c0} compile, busy label shown on ${busyBefore} frames before the longest gap of ${Math.max(...frames).toFixed(0)} ms, label hidden afterwards ${$('busy').hidden}`);
return out;
//// 
const L = window.squaringLab, $ = id => document.getElementById(id), sleep = ms => new Promise(r => setTimeout(r, ms));
// animation frames paused (a background tab): the timer fallback must still finish the picture
const raf = window.requestAnimationFrame;
window.requestAnimationFrame = () => 987654;
await sleep(350);
L.cam.yaw += 0.4; L.touch();
const t0 = performance.now();
while (!L.idle() && performance.now() - t0 < 60000) await sleep(50);
const res = `frames paused: finished ${L.idle()} after ${Math.round(performance.now() - t0)} ms, background flag ${L.R.bg}, status "${$('status').textContent}"`;
window.requestAnimationFrame = raf;
L.touch();
return res;
//// wait=done shot=out/render/paths-2-before-loss.png clip=#stage
return 'picture before the context is lost';
//// 
const L = window.squaringLab, $ = id => document.getElementById(id), sleep = ms => new Promise(r => setTimeout(r, ms));
const gl = $('view').getContext('webgl2'), ext = gl.getExtension('WEBGL_lose_context');
window.__lose = ext;
ext.loseContext();
await sleep(300);
const during = `context lost: gl.isContextLost() ${gl.isContextLost()}, busy hidden ${$('busy').hidden}, bar hidden ${$('drawProgress').hidden}`;
ext.restoreContext();
await sleep(100);
return during;
//// wait=done shot=out/render/paths-3-after-restore.png clip=#stage
const L = window.squaringLab; return 'context restored, compiles so far ' + L.R.compiles;
//// wait=done shot=out/render/paths-4-resized.png clip=#stage
const L = window.squaringLab, st = document.getElementById('stage'), cv = document.getElementById('view');
const before = [cv.width, cv.height];
st.style.height = '420px';
await new Promise(r => setTimeout(r, 120));
return `stage resized: canvas ${before.join('x')} -> ${cv.width}x${cv.height}, something on screen ${L.R.painted}`;
//// wait=done shot=out/render/paths-5-res.png clip=#stage
const L = window.squaringLab, cv = document.getElementById('view');
L.S.q.res = 0.5; L.S.q.de = '1'; L.touch();
await new Promise(r => setTimeout(r, 120));
return `resolution 0.5: canvas ${cv.width}x${cv.height}`;

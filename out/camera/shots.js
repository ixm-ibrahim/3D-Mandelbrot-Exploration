const L = window.squaringLab, S = L.S, cam = L.cam, c = document.getElementById('view');
const $ = id => document.getElementById(id);
const raf = () => new Promise(r => requestAnimationFrame(r));
const sleep = ms => new Promise(r => setTimeout(r, ms));
const settle = async () => { for (let i = 0; i < 300 && (L.CV.goal || L.CV.raf); i++) await raf(); await raf(); await raf(); };
//# wait=done shot=out/camera/10-arcball.png clip=#stage
S.q.aa = 3; document.getElementById('ap-mercator').click(); L.resetCam(); L.touch(); return 'arcball';
//# wait=done shot=out/camera/11-fly.png clip=#stage
$('camFly').click(); c.dispatchEvent(new KeyboardEvent('keydown', { code: 'KeyW', key: 'w', bubbles: true })); await sleep(1500); c.dispatchEvent(new KeyboardEvent('keyup', { code: 'KeyW', key: 'w', bubbles: true }));
const r = c.getBoundingClientRect(); const pe = (t, x, y) => c.dispatchEvent(new PointerEvent(t, { pointerId: 1, buttons: t === 'pointerup' ? 0 : 1, clientX: r.left + x, clientY: r.top + y, bubbles: true }));
pe('pointerdown', 300, 300); pe('pointermove', 240, 330); pe('pointerup', 240, 330);
c.dispatchEvent(new WheelEvent('wheel', { deltaY: -400, clientX: 300, clientY: 400, bubbles: true, cancelable: true }));
await settle(); return 'fly: ' + JSON.stringify(L.basis().pos.map(v => +v.toFixed(3))) + ' speed ' + S.view.speed;
//# wait=done shot=out/camera/12-zoomed-in.png clip=#stage
$('camArc').click(); L.resetCam(); for (let i = 0; i < 12; i++) $('zoomIn').click(); await settle(); $('camRail').focus(); return 'dist ' + cam.dist;
//# wait=done shot=out/camera/13-far.png clip=#stage
const far = $('camFar'); far.focus(); far.value = '400'; far.dispatchEvent(new Event('input')); far.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', bubbles: true }));
S.view.bound = 8; for (let i = 0; i < 60; i++) $('zoomOut').click(); await settle(); far.value = 'abc'; far.dispatchEvent(new Event('input')); far.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', bubbles: true })); return 'dist ' + cam.dist + ' invalid ' + far.getAttribute('aria-invalid');
//# wait=done shot=out/camera/14-flat-overlay.png clip=#stage
L.resetZoomLimits(); L.resetCam(); S.flat = true; L.touch(); await settle(); document.activeElement.blur(); return 'flat (the baseline renderer still draws 3D; only the overlays are judged here)';
//# wait=done
S.flat = false; L.resetCam(); L.touch(); return 'back';

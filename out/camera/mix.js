const L = window.squaringLab, S = L.S, cam = L.cam, c = document.getElementById('view');
const $ = id => document.getElementById(id);
const raf = () => new Promise(r => requestAnimationFrame(r));
const settle = async () => { for (let i = 0; i < 300 && (L.CV.goal || L.CV.raf); i++) await raf(); await raf(); await raf(); };
//# wait=done shot=out/camera/30-mix-3d.png clip=#stage
S.q.aa = 3; L.resetCam(); L.touch(); return 'mix 3d';
//# wait=done shot=out/camera/31-mix-flat.png clip=#stage
S.flat = true; L.resetCam(); L.touch(); return 'flat ' + JSON.stringify(S.v2);
//# wait=done shot=out/camera/32-mix-flat-zoom.png clip=#stage
const r = c.getBoundingClientRect();
// zoom in on the seahorse valley with the wheel, about a fixed screen point
const X = Math.round(r.left + r.width * 0.42), Y = Math.round(r.top + r.height * 0.43);
for (let i = 0; i < 22; i++) { c.dispatchEvent(new WheelEvent('wheel', { deltaY: -100, clientX: X, clientY: Y, bubbles: true, cancelable: true })); await raf(); await raf(); }
await settle(); return 'zoomed ' + JSON.stringify(S.v2);
//# wait=done shot=out/camera/33-mix-flat-pan.png clip=#stage
const r = c.getBoundingClientRect(); const pe = (t, x, y) => c.dispatchEvent(new PointerEvent(t, { pointerId: 1, buttons: t === 'pointerup' ? 0 : 1, clientX: r.left + x, clientY: r.top + y, bubbles: true }));
pe('pointerdown', 400, 300); pe('pointermove', 550, 380); pe('pointerup', 550, 380); return 'panned ' + JSON.stringify(S.v2);
//# wait=done shot=out/camera/34-mix-julia-flat.png clip=#stage
document.getElementById('mode-j').click(); return 'julia flat ' + JSON.stringify(S.v2);
//# wait=done shot=out/camera/35-mix-klein-fly.png clip=#stage
S.flat = false; document.getElementById('mode-k').click(); $('camFly').click(); return 'klein fly';

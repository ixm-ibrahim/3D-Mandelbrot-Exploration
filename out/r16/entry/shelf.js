// Round 16, entry: where in space is the flat "shelf" that the close-up of the touching point shows for Turning plane, along?
const L = window.squaringLab, S = L.S, $ = id => document.getElementById(id), M = L.MATH;
const sleep = ms => new Promise(r => setTimeout(r, ms));
const go = () => { L.syncControls(); L.refresh(false); L.touch(); if (L.viewChanged) L.viewChanged(); };
const idle = async () => { await sleep(300); for (let i = 0; i < 900 && !L.idle(); i++) await sleep(100); };
$('ap-turnalong').click(); await sleep(250); S.n = 2; S.iter = 20;
$('mode-j').click(); await sleep(150); S.flat = false; S.cutOn = false; S.c = [-1, 0, 0]; L.resetCam();
L.cam.pitch = 0.9; L.cam.dist = 0.25; L.cam.target = [-0.618, 0, 0]; go(); await idle();
const w = $('stage').clientWidth, h = $('stage').clientHeight, out = [];
const inside = (p, its) => { let z = p.slice(); for (let s = 0; s < its; s++) { const f = M.turnalong(z, 2, {}); z = [f[0] - 1, f[1], f[2]]; if (!(Math.hypot(...z) <= 64)) return s + 1; } return 0; };
for (const [fx, fy] of [[0.5, 0.5], [0.5, 0.56], [0.5, 0.62], [0.6, 0.58], [0.7, 0.55], [0.4, 0.6], [0.3, 0.3], [0.75, 0.3]]) {
  const p = L.pick(w * fx, h * fy);
  out.push(`pixel (${fx}, ${fy}): ` + (p ? `stops at ${p.map(x => x.toFixed(5)).join(', ')}; that point leaves after ${inside(p, 20)} of 20 steps (0 = never, it is in the solid); nearest point of the solid within 0.004: ` + (() => {
    let best = null; for (let i = -8; i <= 8; i++) for (let j = -8; j <= 8; j++) for (let k = -8; k <= 8; k++) { const q = [p[0] + i * 5e-4, p[1] + j * 5e-4, p[2] + k * 5e-4]; if (!inside(q, 20)) { const d = Math.hypot(i, j, k) * 5e-4; if (best === null || d < best) best = d; } } return best === null ? 'none' : best.toFixed(4); })() : 'nothing'));
}
return out.join('\n');

// How much of the picture each step takes away (from the page's own numbers, mask2): the share of the big circle
// thrown out at each step, and what that is in stage pixels at 1400x950 (and on the phone).
//@
await openLearn(); await pickShape(); L.shape.pause(); $('learnShapeAgain').click(); await sleep(200);
const P = L.shape.state().panes[0], rpx = 2 * 0.21 * Math.min(P.w, P.h), discPx = Math.PI * rpx * rpx;
const count = kind => { const n = 1025, m = L.shape.mask2(kind, n, 2, 16), h = new Array(18).fill(0); for (let i = 0; i < m.length; i++) h[m[i]]++; const disc = m.length - h[0]; return h.map((v, k) => k === 0 ? null : { step: k <= 16 ? k : 'left after 16', sharePct: +(100 * v / disc).toFixed(2), stagePx: Math.round(discPx * v / disc) }).filter(Boolean); };
return { stage: [P.w, P.h], bigCircleRadiusPx: Math.round(rpx), mandelbrot: count('m'), juliaAtOpeningC: count('j') };

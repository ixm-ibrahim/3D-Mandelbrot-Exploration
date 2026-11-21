//// wait=done shot=out/render/pick2d.png clip=#stage
// 2D view: pick() must name the slice point that is drawn under a stage position.
// The second step returns pick() for a grid of positions, with how many steps z^2 + c takes to escape there and how far outside the set it is;
// notes/render_pick2d.py compares that with the colours in the screenshot.
const L = window.squaringLab; L.R.warmOn = false;
L.S.flat = true; L.S.v2 = { x: -0.62, y: 0.21, h: 2.7 }; L.S.cut = 0; L.S.iter = 100; L.S.q.aa = 4; L.touch();
return 'flat view set';
//// 
const L = window.squaringLab, st = document.getElementById('stage'), w = st.clientWidth, h = st.clientHeight, pts = [];
for (let j = 0; j < 40; j++) for (let i = 0; i < 50; i++) {
  const px = (i + 0.5) * w / 50, py = (j + 0.5) * h / 40, c = L.pick(px, py);
  // escape steps, and the usual distance estimate for the flat set, in picture pixels
  let x = 0, y = 0, dx = 0, dy = 0, n = 0;
  while (n < 400 && x * x + y * y < 1e6) {
    const tx = 2 * (x * dx - y * dy) + 1; dy = 2 * (x * dy + y * dx); dx = tx;
    const t = x * x - y * y + c[0]; y = 2 * x * y + c[1]; x = t; n++;
  }
  const r = Math.hypot(x, y), d = n < 400 ? 0.5 * r * Math.log(r) / Math.hypot(dx, dy) / (L.S.v2.h / h) : 0;
  pts.push([Math.round(px + st.clientLeft), Math.round(py + st.clientTop), n, +d.toFixed(2)]);
}
return JSON.stringify({ w, h, centre: L.pick(w / 2, h / 2), topLeft: L.pick(0, 0), v2: L.S.v2, cut: L.S.cut, pts });

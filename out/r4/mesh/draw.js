// A plain picture of a finished mesh, drawn by the test (not by the app): seen from a direction given by two
// angles, lit from the upper left, in the colours of the points. It shows what a 3D program would show.
window.meshT.draw = function (m, az, el, size) {
  size = size || 640;
  const old = document.getElementById('meshView'); if (old) old.remove();
  const cv = document.createElement('canvas'); cv.id = 'meshView'; cv.width = cv.height = size;
  cv.style.cssText = 'position:fixed;left:0;top:0;z-index:99;background:#20262e';
  document.body.appendChild(cv);
  const ctx = cv.getContext('2d'), img = ctx.createImageData(size, size), zb = new Float32Array(size * size).fill(-1e30);
  const ca = Math.cos(az), sa = Math.sin(az), ce = Math.cos(el), se = Math.sin(el), P = m.pos, C = m.col, I = m.idx, nv = P.length / 3;
  const Q = new Float32Array(3 * nv), lo = [1e30, 1e30], hi = [-1e30, -1e30];
  for (let v = 0; v < nv; v++) {
    const x = P[3 * v], y = P[3 * v + 1], z = P[3 * v + 2], rx = ca * x + sa * y, ry = -sa * x + ca * y;   // turn about z, then tip
    Q[3 * v] = rx; Q[3 * v + 1] = ce * z - se * ry; Q[3 * v + 2] = -(se * z + ce * ry);   // screen x, screen y (up), depth toward the eye
    lo[0] = Math.min(lo[0], Q[3 * v]); hi[0] = Math.max(hi[0], Q[3 * v]); lo[1] = Math.min(lo[1], Q[3 * v + 1]); hi[1] = Math.max(hi[1], Q[3 * v + 1]);
  }
  const sc = 0.92 * size / Math.max(hi[0] - lo[0], hi[1] - lo[1]), ox = size / 2 - sc * (lo[0] + hi[0]) / 2, oy = size / 2 + sc * (lo[1] + hi[1]) / 2;
  const lx = -0.45, ly = 0.6, lz = 0.66;
  for (let t = 0; t < I.length; t += 3) {
    const a = I[t], b = I[t + 1], c = I[t + 2];
    const ax = ox + sc * Q[3 * a], ay = oy - sc * Q[3 * a + 1], az2 = Q[3 * a + 2], bx = ox + sc * Q[3 * b], by = oy - sc * Q[3 * b + 1], bz = Q[3 * b + 2];
    const cx = ox + sc * Q[3 * c], cy = oy - sc * Q[3 * c + 1], cz = Q[3 * c + 2];
    const ux = Q[3 * b] - Q[3 * a], uy = Q[3 * b + 1] - Q[3 * a + 1], uz = bz - az2, vx = Q[3 * c] - Q[3 * a], vy = Q[3 * c + 1] - Q[3 * a + 1], vz = cz - az2;
    const nx = uy * vz - uz * vy, ny = uz * vx - ux * vz, nz = ux * vy - uy * vx, nl = Math.hypot(nx, ny, nz) || 1;
    if (nz <= 0) continue;   // turned away from the eye
    const sh = 0.22 + 0.78 * Math.max(0, (nx * lx + ny * ly + nz * lz) / nl);
    const r = (C[3 * a] + C[3 * b] + C[3 * c]) / 3 * sh, g = (C[3 * a + 1] + C[3 * b + 1] + C[3 * c + 1]) / 3 * sh, bl = (C[3 * a + 2] + C[3 * b + 2] + C[3 * c + 2]) / 3 * sh;
    const x0 = Math.max(0, Math.floor(Math.min(ax, bx, cx))), x1 = Math.min(size - 1, Math.ceil(Math.max(ax, bx, cx)));
    const y0 = Math.max(0, Math.floor(Math.min(ay, by, cy))), y1 = Math.min(size - 1, Math.ceil(Math.max(ay, by, cy)));
    const den = (by - cy) * (ax - cx) + (cx - bx) * (ay - cy);
    if (!den) continue;
    for (let y = y0; y <= y1; y++) for (let x = x0; x <= x1; x++) {
      const w0 = ((by - cy) * (x - cx) + (cx - bx) * (y - cy)) / den, w1 = ((cy - ay) * (x - cx) + (ax - cx) * (y - cy)) / den, w2 = 1 - w0 - w1;
      if (w0 < -0.01 || w1 < -0.01 || w2 < -0.01) continue;
      const zz = w0 * az2 + w1 * bz + w2 * cz, o = y * size + x;
      if (zz <= zb[o]) continue;
      zb[o] = zz; img.data[4 * o] = r; img.data[4 * o + 1] = g; img.data[4 * o + 2] = bl; img.data[4 * o + 3] = 255;
    }
  }
  ctx.putImageData(img, 0, 0);
  return 'drawn';
};

// Step 2 checks, the 3D picture. (D) For a grid of probes over the stage: where the page's own ray lands (pick) against a
// slow march in JavaScript that uses the twin's distance with a short stride. A probe the slow march hits and the page
// misses is a hole or a missing ball; a page hit well in front of the slow one is a shell. Lengths in pixels of the page.
// (E) How many rounds the default views need: pixels of the flat default view whose verdict with R rounds differs from
// the verdict with 80 rounds.
S.mode = 'k'; S.k.group = 1; S.flat = false; S.cutOn = false; S.colour.solid = 0;
const out = { D: [], E: [] };
const march = (ro, rd, opts, far) => {
  let t = 0;
  for (let i = 0; i < 4000; i++) {
    const d = L.ballsEstimate(ro[0] + rd[0] * t, ro[1] + rd[1] * t, ro[2] + rd[2] * t, opts);
    if (d < 2e-6 * Math.max(t, 1)) return t;
    t += 0.9 * d;
    if (t > far) return -1;
    const q = [ro[0] + rd[0] * t, ro[1] + rd[1] * t, ro[2] + rd[2] * t];
    if (t > 1 && q[0] * q[0] + q[1] * q[1] + q[2] * q[2] > S.view.bound * S.view.bound && q[0] * rd[0] + q[1] * rd[1] + q[2] * rd[2] > 0) return -1;   // out of the drawing radius, going away
  }
  return t;
};
const views = [['start view', null], ['from the front', { yaw: -1.571, pitch: 0.1 }], ['nearly end-on', { yaw: -0.2, pitch: 0.3 }], ['close in on a kiss', { yaw: -1.3, pitch: 0.7, dist: 0.9, target: [0.525, 0, 0] }], ['close in on buds', { yaw: -1.9, pitch: 0.9, dist: 0.35, target: [0, 0.3, 0.43] }]];
for (const [grid, t] of [[0, 1.4], [1, 1.4], [2, 1.4], [0, 1], [0, 2.5]]) for (const [vname, v] of views) {
  if ((grid !== 0 || t === 1) && v && v.dist) continue;
  S.k.bgrid = grid; S.k.bt = t; S.k.bit = L.BALLS.rounds; L.resetCam();
  if (v) { L.cam.yaw = v.yaw; L.cam.pitch = v.pitch; if (v.dist) { L.cam.dist = v.dist; L.cam.target = v.target.slice(); } }
  go(); await settle();
  const w = $('stage').clientWidth, h = $('stage').clientHeight, b = L.basis(), fov = S.view.fov, opts = { t, grid, rounds: 80 };
  const nx = 64, ny = 48, r = { grid, t, view: vname, probes: nx * ny, bothHit: 0, bothMiss: 0, pageOnly: 0, slowOnly: 0, slowOnlyDeep: 0, thinAir: 0, inFront: 0, behind: 0, maxFront: 0, maxBehind: 0, meanGap: 0 };
  for (let j = 0; j < ny; j++) for (let i = 0; i < nx; i++) {
    const px = w * (i + 0.5) / nx, py = h * (j + 0.5) / ny, p = L.pick(px, py);
    const ux = (2 * px - w) / h * fov, uy = (2 * (h - py) - h) / h * fov;
    let rd = [b.right[0] * ux + b.up[0] * uy + b.f[0], b.right[1] * ux + b.up[1] * uy + b.f[1], b.right[2] * ux + b.up[2] * uy + b.f[2]];
    const n = Math.hypot(rd[0], rd[1], rd[2]); rd = rd.map(x => x / n);
    const ts = march(b.pos, rd, opts, 40), tp = p ? Math.hypot(p[0] - b.pos[0], p[1] - b.pos[1], p[2] - b.pos[2]) : -1;
    if (tp < 0 && ts < 0) r.bothMiss++;
    else if (tp >= 0 && ts < 0) r.pageOnly++;
    else if (tp < 0) {
      // the slow march hit and the page did not: how thick is what was hit, along the ray, in pixels (a grazing ray is not a hole)
      r.slowOnly++;
      const pix = 2 * fov * ts / h; let deep = 0;
      for (let k = 1; k <= 6; k++) if (L.ballsInside(b.pos[0] + rd[0] * (ts + k * pix), b.pos[1] + rd[1] * (ts + k * pix), b.pos[2] + rd[2] * (ts + k * pix), opts)) deep++;
      if (deep >= 4) r.slowOnlyDeep++;
    } else {
      r.bothHit++;
      // how far from a ball did the page stop? (the true distance to the nearest ball its search met, in pixels there)
      { const bf = L.ballsEstimate(p[0], p[1], p[2], { t, grid, rounds: 80, parts: true }), far = bf[0] / (2 * fov * tp / h); if (far > 2) r.thinAir++; r.worstAir = Math.max(r.worstAir || 0, +far.toFixed(1)); }
      const pix = 2 * fov * ts / h, gap = (ts - tp) / pix;   // > 0: the page stops in front of the surface
      r.meanGap += gap;
      if (gap > 4) { r.inFront++; r.maxFront = Math.max(r.maxFront, gap); }
      if (gap < -2) { r.behind++; r.maxBehind = Math.max(r.maxBehind, -gap); }
    }
  }
  r.meanGap = +(r.meanGap / Math.max(1, r.bothHit)).toFixed(2); r.maxFront = +r.maxFront.toFixed(1); r.maxBehind = +r.maxBehind.toFixed(1);
  out.D.push(r);
}
S.k.bgrid = 0; S.k.bt = 1.4; S.k.bit = L.BALLS.rounds; S.flat = false; L.resetCam(); go();
return JSON.stringify(out);

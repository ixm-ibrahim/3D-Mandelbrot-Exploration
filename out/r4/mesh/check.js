// Page-side helpers for the mesh tests (loaded by run_tests.py into the test page; not part of the app).
window.meshT = {
  saved: [],
  // Every edge must be used by exactly two triangles, once each way: then the surface is closed and turned one way.
  closed(m) {
    const idx = m.idx, nv = m.pos.length / 3, n = idx.length, fwd = new Float64Array(n), rev = new Float64Array(n);
    let flat = 0;
    for (let t = 0; t < n; t += 3) for (let e = 0; e < 3; e++) {
      const a = idx[t + e], b = idx[t + (e + 1) % 3];
      fwd[t + e] = a * nv + b; rev[t + e] = b * nv + a;
      if (a === b) flat++;
    }
    fwd.sort(); rev.sort();
    let twice = 0, lone = 0;
    for (let i = 0; i < n; i++) { if (i && fwd[i] === fwd[i - 1]) twice++; if (fwd[i] !== rev[i]) lone++; }
    const used = new Uint8Array(nv); for (let i = 0; i < n; i++) used[idx[i]] = 1;
    let unused = 0; for (let i = 0; i < nv; i++) if (!used[i]) unused++;
    // smallest triangle area, in cells squared
    let small = Infinity; const P = m.pos;
    for (let t = 0; t < n; t += 3) {
      const a = 3 * idx[t], b = 3 * idx[t + 1], c = 3 * idx[t + 2];
      const ux = P[b] - P[a], uy = P[b + 1] - P[a + 1], uz = P[b + 2] - P[a + 2], vx = P[c] - P[a], vy = P[c + 1] - P[a + 1], vz = P[c + 2] - P[a + 2];
      small = Math.min(small, Math.hypot(uy * vz - uz * vy, uz * vx - ux * vz, ux * vy - uy * vx) / 2);
    }
    return { triangles: n / 3, points: nv, edgesUsedTwiceTheSameWay: twice, edgesWithoutPartner: lone, pointsUnused: unused, pointRepeatedInTriangle: flat,
      euler: nv - n / 2 + n / 3, smallestArea: +small.toExponential(2) };
  },
  // How far the points are from the surface a field should give, in cells: dist(x, y, z) is the true distance to it.
  fit(m, dist) {
    let sum = 0, worst = 0; const nv = m.pos.length / 3;
    for (let v = 0; v < nv; v++) {
      const e = dist(m.org[0] + m.pos[3 * v] * m.h, m.org[1] + m.pos[3 * v + 1] * m.h, m.org[2] + m.pos[3 * v + 2] * m.h) / m.h;
      sum += e * e; worst = Math.max(worst, Math.abs(e));
    }
    return { rms: +Math.sqrt(sum / nv).toFixed(4), worst: +worst.toFixed(4) };
  },
  async run(field, cells, opt) {
    const L = window.squaringLab;
    window.squaringLabMeshTest = field ? { field, cells } : { cells };
    Object.assign(L.MESH.opt, { cells: 128, offset: 0.5, mm: 100, largest: true, stl: true, obj: true, ply: true }, opt || {});
    if (!field && cells) L.MESH.opt.cells = cells;
    L.syncControls();
    if (L.MESH.result) document.getElementById('meshDiscard').click();
    const t0 = performance.now();
    let gap = 0, last = t0, on = true;
    const tick = () => { const now = performance.now(); gap = Math.max(gap, now - last); last = now; if (on) setTimeout(tick, 0); };
    tick();
    document.getElementById('meshStart').click();
    while (L.meshBusy()) await new Promise(r => setTimeout(r, 30));
    on = false;
    return { seconds: +((performance.now() - t0) / 1000).toFixed(2), longestPause: Math.round(gap), message: document.getElementById('meshMsg').textContent,
      facts: [...document.querySelectorAll('#meshFacts dt')].map(dt => dt.textContent + ': ' + dt.nextSibling.textContent) };
  },
  async save() {
    const before = this.saved.length;
    document.getElementById('meshSave').click();
    for (let i = 0; i < 200 && this.saved.length === before; i++) await new Promise(r => setTimeout(r, 25));
    const f = this.saved[this.saved.length - 1], bytes = new Uint8Array(await f.blob.arrayBuffer());
    let bin = '';
    for (let i = 0; i < bytes.length; i += 32768) bin += String.fromCharCode.apply(null, bytes.subarray(i, i + 32768));
    return { name: f.name, size: bytes.length, b64: btoa(bin), message: document.getElementById('meshMsg').textContent };
  },
};
window.squaringLabSaveHook = (name, blob) => { window.meshT.saved.push({ name, blob }); };

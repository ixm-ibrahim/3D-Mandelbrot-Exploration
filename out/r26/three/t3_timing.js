// Timings for NOTES.md: one frame of a 600 x 450 picture, the graphics card waited for (view.time: draw, then read one
// pixel back, which does not return before the picture is finished). Median and least of 9.
// window.T3_TIMING_IDS (set by the action before this file) says which approaches.
const T = window.T3, L = T.L, V = T.view, S = L.S;
T.size(600, 450);
const ids = window.T3_TIMING_IDS || ['mercator', 'softfold'];
const med = a => { const s = a.slice().sort((x, y) => x - y); return [+s[Math.floor(s.length / 2)].toFixed(1), +s[0].toFixed(1)]; };
const rows = [];
for (const id of ids) {
  T.setAp(id); S.n = 2;
  for (const kind of ['m', 'j']) for (const step of [2, 8, 16, 8.5]) {
    const row = { id, kind, step };
    for (const [name, extra] of [['still', { quality: 'still', lod: 0 }], ['move0', { quality: 'move', lod: 0 }], ['move1', { quality: 'move', lod: 1 }], ['move2', { quality: 'move', lod: 2 }]]) {
      const o = T.one(kind, [-1, 0, 0], T.levelsAt(step), extra);
      const t = med(V.time(o, 9)), st = V.stats().last;
      row[name] = t[0] + ' (' + t[1] + ') ' + st.bw + 'x' + st.bh + ' n' + st.n;
    }
    rows.push(row);
  }
}
rows.push({ builds: V.stats().builds, gpuMs: V.stats().gpuMs });
T.setAp('mercator');
return rows;

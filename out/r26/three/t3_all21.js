// Every approach: does its program build (power 2 and another power), how long does that take, and does it draw
// both kinds? "drawn" is the share of the 600 x 450 picture that is not the background, for the shape after 3 steps.
const T = window.T3, L = T.L, M = T.M, V = T.view, S = L.S;
T.size(600, 450);
const gl = V.canvas.getContext('webgl2');
const drawn = () => {
  const w = V.canvas.width, h = V.canvas.height, px = new Uint8Array(w * h * 4);
  gl.readPixels(0, 0, w, h, gl.RGBA, gl.UNSIGNED_BYTE, px);
  let n = 0;
  for (let i = 0; i < w * h; i++) if (Math.abs(px[4 * i] - px[0]) + Math.abs(px[4 * i + 1] - px[1]) + Math.abs(px[4 * i + 2] - px[2]) > 6) n++;
  return +(100 * n / (w * h)).toFixed(2);
};
const rows = [];
for (const a of L.APPROACHES) {
  T.setAp(a.id);
  (a.params || []).filter(s => s.key !== undefined).forEach(s => { S.param[a.id][s.key] = s.def; });
  const row = { id: a.id, name: a.name };
  for (const n of [2, 3]) {
    S.n = n;
    const lv = [{ k: 3, alpha: 1, tint: 0 }];
    const t0 = performance.now();
    const r = V.draw(T.one('m', [0, 0, 0], lv));
    const px = new Uint8Array(4); gl.readPixels(0, 0, 1, 1, gl.RGBA, gl.UNSIGNED_BYTE, px);
    const first = performance.now() - t0;
    const key = a.id + (n === 2 ? '|2' : '|n'), st = V.stats();
    row['build' + n] = +(st.builds[key] || 0).toFixed(0);
    row['first' + n] = +first.toFixed(0);
    row['ok' + n] = r.ok && M.ok();
    if (!r.ok) row['note' + n] = M.note();
    row['m' + n] = r.ok ? drawn() : 0;
    const r2 = V.draw(T.one('j', [-1, 0, 0], lv));
    row['j' + n] = r2.ok ? drawn() : 0;
    // and the ball at step 0 has to be the same disc for every approach
    V.draw(T.one('m', [0, 0, 0], [{ k: 0, alpha: 1, tint: 0 }]));
    row['ball' + n] = drawn();
    row['still' + n] = +Math.min(...V.time(T.one('j', [-1, 0, 0], [{ k: 7, alpha: 0.14 }, { k: 8, alpha: 1 }]), 3)).toFixed(1);
  }
  rows.push(row);
}
S.n = 2; T.setAp('mercator');
return rows;

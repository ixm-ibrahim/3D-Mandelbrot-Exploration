
const L = window.squaringLab, M = L.MATH;
const CUTS = [{"tag": "ta-bas-x0-14", "id": "turnaway", "n": 2, "mode": "j", "c": [-1, 0, 0], "o": [0, 0, 0], "u": [0, 1, 0], "w": [0, 0, 1], "W": 2.4, "its": 14}, {"tag": "ta-bas-x0-40", "id": "turnaway", "n": 2, "mode": "j", "c": [-1, 0, 0], "o": [0, 0, 0], "u": [0, 1, 0], "w": [0, 0, 1], "W": 2.4, "its": 40}, {"tag": "ta-bas-diag-14", "id": "turnaway", "n": 2, "mode": "j", "c": [-1, 0, 0], "o": [0, 0, 0], "u": [1, 0, 0], "w": [0, 0.7071067811865476, 0.7071067811865476], "W": 3.6, "its": 14}, {"tag": "ta-bas-x618-14", "id": "turnaway", "n": 2, "mode": "j", "c": [-1, 0, 0], "o": [-0.618034, 0, 0], "u": [0, 1, 0], "w": [0, 0, 1], "W": 1.0, "its": 14}, {"tag": "ta-bas-xm03-14", "id": "turnaway", "n": 2, "mode": "j", "c": [-1, 0, 0], "o": [-0.3, 0, 0], "u": [0, 1, 0], "w": [0, 0, 1], "W": 2.4, "its": 14}, {"tag": "tl-bas-x0-14", "id": "turnalong", "n": 2, "mode": "j", "c": [-1, 0, 0], "o": [0, 0, 0], "u": [0, 1, 0], "w": [0, 0, 1], "W": 2.4, "its": 14}, {"tag": "tl-bas-x0-40", "id": "turnalong", "n": 2, "mode": "j", "c": [-1, 0, 0], "o": [0, 0, 0], "u": [0, 1, 0], "w": [0, 0, 1], "W": 2.4, "its": 40}, {"tag": "tl-bas-diag-14", "id": "turnalong", "n": 2, "mode": "j", "c": [-1, 0, 0], "o": [0, 0, 0], "u": [1, 0, 0], "w": [0, 0.7071067811865476, 0.7071067811865476], "W": 3.6, "its": 14}, {"tag": "tl-bas-x618-14", "id": "turnalong", "n": 2, "mode": "j", "c": [-1, 0, 0], "o": [-0.618034, 0, 0], "u": [0, 1, 0], "w": [0, 0, 1], "W": 1.0, "its": 14}, {"tag": "tl-bas-xm03-14", "id": "turnalong", "n": 2, "mode": "j", "c": [-1, 0, 0], "o": [-0.3, 0, 0], "u": [0, 1, 0], "w": [0, 0, 1], "W": 2.4, "its": 14}, {"tag": "f2-bas-x0-14", "id": "fold", "n": 2, "mode": "j", "c": [-1, 0, 0], "o": [0, 0, 0], "u": [0, 1, 0], "w": [0, 0, 1], "W": 2.4, "its": 14}, {"tag": "f2-bas-x0-40", "id": "fold", "n": 2, "mode": "j", "c": [-1, 0, 0], "o": [0, 0, 0], "u": [0, 1, 0], "w": [0, 0, 1], "W": 2.4, "its": 40}, {"tag": "f2-bas-diag-14", "id": "fold", "n": 2, "mode": "j", "c": [-1, 0, 0], "o": [0, 0, 0], "u": [1, 0, 0], "w": [0, 0.7071067811865476, 0.7071067811865476], "W": 3.6, "its": 14}, {"tag": "f2-bas-x618-14", "id": "fold", "n": 2, "mode": "j", "c": [-1, 0, 0], "o": [-0.618034, 0, 0], "u": [0, 1, 0], "w": [0, 0, 1], "W": 1.0, "its": 14}, {"tag": "f2-bas-xm03-14", "id": "fold", "n": 2, "mode": "j", "c": [-1, 0, 0], "o": [-0.3, 0, 0], "u": [0, 1, 0], "w": [0, 0, 1], "W": 2.4, "its": 14}];
const N = 300, out = [];
for (const q of CUTS) {
  const F = q.id === 'fold' ? (v => M.fold(v, q.n, { planes: 2 })) : (v => M[q.id](v, q.n, {}));
  const g = new Uint8Array(N * N);
  let ins = 0;
  for (let j = 0; j < N; j++) for (let i = 0; i < N; i++) {
    const a = q.W * ((i + 0.5) / N - 0.5), b = -q.W * ((j + 0.5) / N - 0.5);
    const p = [q.o[0] + a * q.u[0] + b * q.w[0], q.o[1] + a * q.u[1] + b * q.w[1], q.o[2] + a * q.u[2] + b * q.w[2]];
    const c = q.mode === 'm' ? p : q.c;
    let z = q.mode === 'm' ? [0, 0, 0] : p, e = 0;
    for (let s = 0; s <= q.its; s++) {
      if (!(Math.hypot(z[0], z[1], z[2]) <= 64)) { e = s; break; }
      if (s === q.its) break;
      const f = F(z); z = [f[0] + c[0], f[1] + c[1], f[2] + c[2]];
    }
    g[j * N + i] = Math.min(e, 255); if (!e) ins++;
  }
  let bin = ''; for (let k = 0; k < g.length; k += 8192) bin += String.fromCharCode(...g.subarray(k, k + 8192));
  out.push({ tag: q.tag, inside: ins / (N * N), rows: btoa(bin) });
}
return JSON.stringify(out);

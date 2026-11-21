// Round 15, entry: brute-force cuts through the solid at the places of the close-ups, with MATH.sqpillow in
// JavaScript's 64-bit numbers (no distance estimate, no shader): an upright plane y = const through the point the
// camera moved in on, in windows 0.8, 0.2 and 0.05 wide, with 14, 20 and 26 steps as in the close-ups.
// Returns for each window a 280 x 280 grid: the step at which the point left (0: never, it is in the solid).
const L = window.squaringLab, M = L.MATH;
const add = (a, b) => [a[0] + b[0], a[1] + b[1], a[2] + b[2]], len = a => Math.hypot(a[0], a[1], a[2]);
const N = 280, out = [];
for (const [tag, c, t] of [['bas-body', [-1, 0, 0], [-0.1152, -0.3371, 0.4736]], ['bas-meet', [-1, 0, 0], [-0.6838, -0.1926, 0.2564]], ['rab-body', [-0.12, 0.74, 0], [0.1126, -0.3388, 0.556]]])
  for (const [k, W, its] of [[1, 0.8, 14], [2, 0.2, 20], [3, 0.05, 26]]) {
    const g = new Uint8Array(N * N);
    let ins = 0;
    for (let j = 0; j < N; j++) for (let i = 0; i < N; i++) {
      let z = [t[0] + W * ((i + 0.5) / N - 0.5), t[1], t[2] - W * ((j + 0.5) / N - 0.5)], e = 0;
      for (let s = 0; s <= its; s++) { if (!(len(z) <= 64)) { e = s; break; } if (s === its) break; z = add(M.sqpillow(z, 2, {}), c); }
      g[j * N + i] = e; if (!e) ins++;
    }
    out.push({ tag, k, W, its, c, t, N, inside: ins / (N * N), rows: btoa(String.fromCharCode(...g)) });
  }
return JSON.stringify(out);

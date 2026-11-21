// Round 15, entry: is there matter round the points where the flat bodies touch? Runs inside the page.
// Brute force with MATH (14 steps, escape radius 64, as the picture): the area of the solid's cut by a plane x = const,
// through the touching point and through the middle of the central body, and how far the solid reaches above and
// below the plane z = 0 on the upright line through each. The same for "Sphere inversions, one plane".
const L = window.squaringLab, M = L.MATH;
const add = (a, b) => [a[0] + b[0], a[1] + b[1], a[2] + b[2]], len = a => Math.hypot(a[0], a[1], a[2]);
const inside = (id, P, c, its) => { let z = P; for (let i = 0; i <= its; i++) { if (!(len(z) <= 64)) return false; if (i === its) break; z = add(M[id](z, 2, {}), c); } return true; };
const out = [];
for (const id of ['sqpillow', 'mercator']) for (const its of [14, 24]) {
  const c = [-1, 0, 0], row = { id, steps: its, c };
  for (const [name, x] of [['touching', -0.6180339887], ['middle', 0]]) {
    const h = 0.005; let n = 0, up = 0, dn = 0, ymax = 0;
    for (let y = -1.6; y <= 1.6; y += h) for (let z = -1.6; z <= 1.6; z += h) if (inside(id, [x, y, z], c, its)) { n++; ymax = Math.max(ymax, Math.abs(y)); }
    for (let z = 0.0005; z <= 1.6; z += 0.0005) { if (inside(id, [x, 0, z], c, its)) up = z; }
    for (let z = 0.0005; z <= 1.6; z += 0.0005) { if (inside(id, [x, 0, -z], c, its)) dn = z; }
    row[name] = { x, area: n * h * h, highestInsideAbove: up, lowestInsideBelow: -dn, widestY: ymax };
  }
  row.ratio = row.touching.area / row.middle.area;
  out.push(row);
}
return JSON.stringify(out);

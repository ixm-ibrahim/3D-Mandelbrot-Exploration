// Round 29, builder: how much of the ball of the Drawing radius is inside (120 directions spread evenly, and the same
// at 0.8 and 0.6 of it), for the states of lump.js. To choose the line for the lump sentence.
$('ap-balls').click(); await settle();
const out = [];
const share = R => { let n = 0; for (let i = 0; i < 120; i++) { const z = 1 - (2 * i + 1) / 120, r = Math.sqrt(1 - z * z), a = 2.399963229728653 * i; if (L.ballsInside(R * r * Math.cos(a), R * r * Math.sin(a), R * z)) n++; } return n; };
for (const [name, p, rho, g] of [['X1', 120, 1, 0], ['X2', 130, 1, 0], ['X3', 150, 1, 2], ['X6', 150, 0.75, 0], ['X7', 300, 0.5, 0], ['X9', 105, 1, 0], ['(110, 100)', 110, 1, 0], ['(125, 85)', 125, 0.85, 0], ['(250, 45)', 250, 0.45, 2], ['(115, 100)', 115, 1, 0]]) {
  S.k.brho = rho; S.k.bt = 0.5 * (100 / p + 1); S.k.bgrid = g; S.k.bit = 16; S.flat = false; go();
  out.push(`${name}: inside, of 120 directions, at radius 9: ${share(9)}, 14: ${share(14)}, 30: ${share(30)}, 180: ${share(180)}`);
}
return JSON.stringify(out, null, 1);

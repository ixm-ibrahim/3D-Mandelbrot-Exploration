// Round 29, builder: the sentence "one lump as large as the Drawing radius" against what the picture holds.
// For each cutting state, as Frame it shows it and with a larger Drawing radius: the sentence, and the share of
// 609 rays of the picture that stop on something.
$('ap-balls').click(); await settle();
const out = [];
const probe = () => { const w = $('stage').clientWidth, h = $('stage').clientHeight; let n = 0; for (let i = 0; i < 29; i++) for (let j = 0; j < 21; j++) if (L.pick(w * (i + 0.5) / 29, h * (j + 0.5) / 21)) n++; return Math.round(100 * n / 609); };
for (const [name, p, rho, g] of [['X1', 120, 1, 0], ['X2', 130, 1, 0], ['X3', 150, 1, 2], ['X4', 150, 1, 1], ['X5', 200, 1, 2], ['X6', 150, 0.75, 0], ['X7', 300, 0.5, 0], ['X8', 400, 1, 0], ['X9', 105, 1, 0], ['(110, 100)', 110, 1, 0], ['(125, 85)', 125, 0.85, 0], ['(250, 45)', 250, 0.45, 2]]) {
  for (const bound of [0, 14, 30]) {
    S.k.brho = rho; S.k.bt = 0.5 * (100 / p + 1); S.k.bgrid = g; S.k.bit = 16; S.flat = false; S.view.bound = 4; go(); await sleep(50); $('ballsFrame').click(); await settle();
    if (bound) { if (bound <= S.view.bound) continue; S.view.bound = bound; go(); await settle(); }
    const w = warn();
    out.push(`${name} size ${p} second ${100 * rho} grid ${g}, Drawing radius ${+S.view.bound.toFixed(2)}, eye ${+L.cam.dist.toFixed(2)} away: ${probe()} % of the rays stop on something; lump sentence ${w.includes('one lump') ? 'SHOWN' : 'not shown'}`);
  }
}
return JSON.stringify(out, null, 1);

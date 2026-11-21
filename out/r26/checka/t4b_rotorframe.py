"""Second look at the one finding of t4_cut: "Rotor square with a frame", power 3, Julia c = -1: the card's slice at
z = 0 differs from the flat shape at 8 of 16,641 points, 2 of them with no flat skin within 1e-4.
For each of the 8: the card's number, the flat rule's (out2), three's JavaScript twin, my MATH orbit; the numbers my
orbit gives within 1e-4 in space; and what it gives when every step is nudged by a part in a million.
Also the out2 answer at the tip c = -2 found by t1_flat.
"""
import json
from clab import Lab, Log

log = Log("t4b_rotorframe")
JS = """
await shapeOn({ kind: 'j', space: 3, pos: 5, c: [-1, 0, 0] });
await pickAp('rotorframe'); setRule(3, [0,0,0], [0,0]);
const c = [-1, 0, 0], K = 16, SIZE = 129, v = ckView(), g = v.slice('j', c, { z: 0, half: 2, size: SIZE, maxK: K }), out = [];
let seed = 99; const rnd = () => { seed = (Math.imul(seed, 1664525) + 1013904223) >>> 0; return seed / 4294967296; };
for (let row = 0; row < SIZE; row++) for (let col = 0; col < SIZE; col++) {
  const p = ckPoint(row, col, SIZE, 2, 0), flat = L.shape.out2([p[0], p[1]], 'j', c, K), card = g[row * SIZE + col];
  if (card === flat) continue;
  const near = {}; for (let i = 0; i < 3000; i++) { const e = 1e-4, o = ckOut3([p[0] + e * (rnd() * 2 - 1), p[1] + e * (rnd() * 2 - 1), e * (rnd() * 2 - 1)], 'j', c, K); near[o] = (near[o] || 0) + 1; }
  const nearFlat = {}; for (let i = 0; i < 3000; i++) { const e = 1e-4, o = L.shape.out2([p[0] + e * (rnd() * 2 - 1), p[1] + e * (rnd() * 2 - 1)], 'j', c, K); nearFlat[o] = (nearFlat[o] || 0) + 1; }
  // my orbit with each step nudged
  const noisy = {};
  for (let i = 0; i < 400; i++) {
    let z = p.slice(), res = K + 1;
    for (let k = 1; k <= K; k++) { const l = Math.hypot(z[0], z[1], z[2]); z = z.map(x => x + 1e-6 * l * (rnd() * 2 - 1)); const w = LAB.MATH.rotorframe(z, 3, {}, c); z = [w[0] + c[0], w[1] + c[1], w[2] + c[2]]; if (!(Math.hypot(z[0], z[1], z[2]) <= 2)) { res = k; break; } }
    noisy[res] = (noisy[res] || 0) + 1;
  }
  out.push({ p, card, flat, three: LAB.learnShape3d.out(p, 'j', c, K), mine: ckOut3(p, 'j', c, K), near, nearFlat, noisy });
}
const tip = { out2: L.shape.out2([-2, 0], 'm', null, 16), mask2: L.shape.mask2('m', 129, 2, 16)[64 * 129 + 0], out2_40: L.shape.out2([-2, 0], 'm', null, 40) };
setRule(2, [0,0,0], [0,0]);
const tip2 = { out2: L.shape.out2([-2, 0], 'm', null, 16), mask2: L.shape.mask2('m', 129, 2, 16)[64 * 129 + 0], out2_40: L.shape.out2([-2, 0], 'm', null, 40), mask2_40: L.shape.mask2('m', 129, 2, 40)[64 * 129 + 0],
  three: LAB.learnShape3d.out([-2, 0, 0], 'm', [0, 0, 0], 16) };
await pickAp('mercator');
return { out, tip, tip2 };
"""
with Lab("r26-checka") as lab:
    r = lab.js(JS)
    for o in r["out"]:
        ok = str(o["card"]) in o["near"] or str(o["card"]) in o["noisy"]
        log("p=%s: card %d, flat rule %d, three's twin %d, my orbit %d" % (o["p"], o["card"], o["flat"], o["three"], o["mine"]))
        log("    my orbit within 1e-4 in space: %s" % json.dumps(o["near"]))
        log("    the flat rule within 1e-4 in the plane: %s" % json.dumps(o["nearFlat"]))
        log("    my orbit with each step nudged by 1e-6: %s   -> %s" % (json.dumps(o["noisy"]), "explained" if ok else "NOT EXPLAINED"))
    log("the tip (-2, 0) of the Mandelbrot shape at power 3: %s" % json.dumps(r["tip"]))
    log("the tip (-2, 0) of the Mandelbrot shape at power 2: %s" % json.dumps(r["tip2"]))
    log.problems(lab)

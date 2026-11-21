"""Check 2, second look: the 15 points of t3_slice where the card's slice differs from MATH / CARRY and none of the
78 points I asked within 1e-4 gave the card's number. For each:
  (a) 4000 random points within 1e-4, 1e-5 and 1e-6 of it: which numbers does my 64-bit orbit give there?
  (b) my orbit again, 400 times, with every orbit point nudged by a part in a million at every step (what 32-bit
      arithmetic does to it): which numbers come out?
  (c) how close the 64-bit orbit comes to the big ball's surface on its way (the least | |z_k| - 2 |).
The card's number is "explained" when (a) or (b) gives it.
"""
import json
from clab import Lab, Log

log = Log("t3b_odd")
ODD = [
    ("tilt", 2, None, "m", [0, 0, 0], [-2, 0, 0]),
    ("tilt", 2, {"tilt": -70}, "m", [0, 0, 0], [-2, 0, 0]),
    ("pillow", 2, None, "j", [-1, 0, 0], [-0.375, 0.0625, 0.5]),
    ("pillow", 2, None, "j", [-1, 0, 0], [-0.375, -0.0625, 0.5]),
    ("windsq", 2, None, "j", [-0.3, 0.2, 0.35], [0, 0.4375, 0]),
    ("windsq", 2, None, "j", [-0.3, 0.2, 0.35], [0, -0.4375, 0]),
    ("softfold", 3, None, "j", [-0.3, 0.2, 0.35], [0.0625, 0.0625, 0]),
    ("turnaway", 2.5, None, "j", [-0.1226, 0.7449, 0], [-0.0625, 0, 0.5]),
    ("turnaway", 2.5, None, "j", [-0.1226, 0.7449, 0], [-1.03125, -0.59375, 0.5]),
    ("turnaway", 2.5, None, "j", [-0.1226, 0.7449, 0], [0.90625, -0.75, 0.5]),
    ("turnaway", 2.5, None, "j", [-0.3, 0.2, 0.35], [-0.78125, 0.03125, 0]),
    ("turnaway", 2.5, None, "j", [-0.3, 0.2, 0.35], [-0.5625, -0.4375, 0.2]),
    ("turnaway", 2.5, None, "j", [-0.3, 0.2, 0.35], [-0.28125, 0.0625, 0.5]),
    ("softfold", 2, {"planes": 3, "blend": 0.1, "curve": 1, "mix": 2}, "m", [0, 0, 0], [-1.40625, -0.21875, 0.2]),
    ("softfold", 2, {"planes": 3, "blend": 0.1, "curve": 1, "mix": 2}, "j", [-0.3, 0.2, 0.35], [0.28125, -0.8125, 0.5]),
]
JS = """
const [id, n, moved, kind, c, p] = %s, K = 16;
await pickAp(id); dialsBack(id); setRule(n, [0,0,0], [0,0]); if (moved) dials(id, moved);
const v = ckView();
// the card's own number for exactly this point: a slice of 3 x 3 points whose middle one is p
const g = v.slice(kind, c, { z: p[2], half: 2, size: 129, maxK: K });
const col = Math.round((p[0] + 2) / (4 / 128)), row = Math.round((2 - p[1]) / (4 / 128)), card = g[row * 129 + col];
const M = ckOut3(p, kind, c, K), T = LAB.learnShape3d.out(p, kind, c, K);
// (a)
let seed = 12345; const rnd = () => { seed = (Math.imul(seed, 1664525) + 1013904223) >>> 0; return seed / 4294967296; };
const near = {};
for (const e of [1e-4, 1e-5, 1e-6]) { const h = {}; for (let i = 0; i < 4000; i++) { let d; do { d = [rnd() * 2 - 1, rnd() * 2 - 1, rnd() * 2 - 1]; } while (d[0] * d[0] + d[1] * d[1] + d[2] * d[2] > 1); const o = ckOut3([p[0] + d[0] * e, p[1] + d[1] * e, p[2] + d[2] * e], kind, c, K); h[o] = (h[o] || 0) + 1; } near[e] = h; }
// (b) the orbit with every point nudged at every step, and (c) the margins
const a = AP(), q = S.param[id], car = LAB.CARRY && LAB.CARRY[id] ? LAB.CARRY[id] : null;
const A = (() => { const u = [0, 0, 0, 0]; (a.params || []).filter(s => s.key !== undefined).forEach((s, i) => { if (i < 4) u[i] = +q[s.key]; }); return u; })();
const run = (noise, trace) => {
  let z = [0, 0, 0], cc;
  if (kind === 'j') { z = id === 'quat4' ? ckQ4.zmap(p, c, A) : p.slice(); cc = id === 'fold' ? ckFold(c, A[0]) : id === 'quat4' ? ckQ4.cmap(c, A, true) : c.slice(); }
  else cc = id === 'fold' ? ckFold(p, A[0]) : id === 'quat4' ? ckQ4.cmap(p, A, false) : p.slice();
  let st = car ? car.start(q) : null;
  for (let k = 1; k <= K; k++) {
    if (noise) { const l = Math.hypot(z[0], z[1], z[2]); z = z.map(x => x + noise * l * (rnd() * 2 - 1)); }   // each coordinate, by that share of the point's length
    let w; if (car) { st = car.step(st, z, cc, q); w = car.pw(st, z, n); } else w = LAB.MATH[id](z, n, q, cc);
    z = [w[0] + cc[0], w[1] + cc[1], w[2] + cc[2]];
    const r = Math.hypot(z[0], z[1], z[2]);
    if (trace) trace.push(+r.toPrecision(9));
    if (!(r <= 2)) return k;
  }
  return K + 1;
};
const lens = []; run(0, lens);
const noisy = {};
for (const e of [3e-7, 1e-6, 1e-5]) { const h = {}; for (let i = 0; i < 400; i++) { const o = run(e); h[o] = (h[o] || 0) + 1; } noisy[e] = h; }
if (moved) dialsBack(id);
return { card, M, T, near, noisy, lens, margin: Math.min(...lens.map(r => Math.abs(r - 2))) };
"""
unexpl = 0
with Lab("r26-checka") as lab:
    lab.js("await shapeOn({ kind: 'm', space: 2, pos: 2 }); return 1;")
    for item in ODD:
        r = lab.js(JS % json.dumps(list(item)))
        card = str(r["card"])
        inNear = [e for e, h in r["near"].items() if card in h]
        inNoisy = [e for e, h in r["noisy"].items() if card in h]
        ok = bool(inNear or inNoisy) or r["margin"] < 1e-6
        if not ok: unexpl += 1
        log("%s, power %s%s, %s c=%s, p=%s: card %s, mine %s, three's %s" % (item[0], item[1], (" " + json.dumps(item[2])) if item[2] else "", item[3], item[4], item[5], r["card"], r["M"], r["T"]))
        log("    (a) numbers my orbit gives within 1e-4 / 1e-5 / 1e-6 of the point: %s" % json.dumps(r["near"]))
        log("    (b) numbers it gives with every step nudged by 3e-7 / 1e-6 / 1e-5: %s" % json.dumps(r["noisy"]))
        log("    (c) lengths of the orbit: %s; closest to the ball's surface: %.3g" % (r["lens"], r["margin"]))
        log("    -> %s" % ("explained: " + ("the orbit runs on the surface of the big ball itself" if r["margin"] < 1e-6 else ("the card's number turns up " + ("near the point" if inNear else "") + (" and " if inNear and inNoisy else "") + ("under 32-bit-sized nudges" if inNoisy else ""))) if ok else "NOT EXPLAINED"))
    lab.js("await pickAp('mercator'); setRule(2, [0,0,0], [0,0]); return 1;")
    log.problems(lab)
log("not explained: %d of %d" % (unexpl, len(ODD)))

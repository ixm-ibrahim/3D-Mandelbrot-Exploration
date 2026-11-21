"""Check 1a: the flat pictures' numbers.
LEARN.shape.mask2 and LEARN.shape.out2 against my Python reference (cref.py), both kinds, the powers 2, 3 and 2.5
(and 1, 0.5, -2, 4, 9, -1.5 for good measure), the modifiers |x|, |y| and flip y, three values of c.
A point where the two differ is looked at again: if the reference gives the page's number within 1e-7 of it, the
point lies within a hair of a skin (or on the cut of a power that is not whole); anything else is a defect.
"""
import json, sys
import numpy as np
from clab import Lab, Log, u8
import cref

log = Log("t1_flat")

# the reference against facts known without any program
one = lambda kind, p, c, n=2, K=16: int(cref.out_points([p[0]], [p[1]], kind, c, n, maxK=K)[0])
facts = [
    (one("m", (0, 0), None), 17, "c = 0 never leaves"),
    (one("m", (1, 0), None), 3, "c = 1: 0, 1, 2, 5: thrown out at step 3"),
    (one("m", (-2, 0), None), 17, "c = -2: 0, -2, 2, 2, ... stays"),
    (one("m", (2, 0), None), 2, "c = 2: 0, 2, 6: thrown out at step 2"),
    (one("m", (2.01, 0), None), 0, "c = 2.01 starts outside"),
    (one("m", (0, 1), None), 17, "c = i: 0, i, -1+i, -i, -1+i ... stays"),
    (one("j", (0, 0), (-1, 0)), 17, "Julia c = -1 from 0: 0, -1, 0 stays"),
    (one("j", (2, 0), (-1, 0)), 1, "Julia c = -1 from 2: 3 at step 1"),
    (one("j", (1.5, 0), (0, 0)), 1, "Julia c = 0 from 1.5: 2.25 at step 1"),
    (one("j", (1.2, 0), (0, 0)), 2, "Julia c = 0 from 1.2: 1.44, 2.0736: thrown out at step 2"),
    (one("m", (-1, 0), None, 3), 3, "power 3, c = -1: 0, -1, -2, -9: thrown out at step 3"),
]
log("reference against hand-worked orbits:")
for i, (got, want, txt) in enumerate(facts):
    log("  %s: reference %d, by hand %d %s" % (txt, got, want, "ok" if got == want else "WRONG"))
    if got != want:
        log("STOP: my own reference is wrong"); sys.exit(1)

CS = [[-1, 0, 0], [-0.1226, 0.7449, 0], [0.28, 0.53, 0]]
MODS = [("none", [0, 0, 0], [0, 0]), ("|x|", [1, 0, 0], [0, 0]), ("flip y", [0, 0, 0], [1, 0]), ("|x| and flip y", [1, 0, 0], [1, 0]), ("|y|", [0, 1, 0], [0, 0]), ("|y| and flip y", [0, 1, 0], [1, 0])]
POWERS = [2, 3, 2.5, 1, 0.5, -2, 4, 9, -1.5]
SIZE, HALF, K = 257, 2.0, 16
rows, defects, total_pts, total_diff, total_unexpl = [], [], 0, 0, 0

with Lab("r26-checka") as lab:
    lab.js("await shapeOn({ kind: 'both', space: 2, pos: 3 }); return 1;")
    for n in POWERS:
        mods = MODS if n in (2, 3, 2.5) else MODS[:3]
        for mname, ab, fl in mods:
            for kind, c in [("m", None)] + [("j", c) for c in CS]:
                code = "setRule(%s, %s, %s); %s return b64(L.shape.mask2('%s', %d, %s, %d));" % (
                    json.dumps(n), json.dumps(ab), json.dumps(fl), ("L.shape.set({ c: %s });" % json.dumps(c)) if c else "", kind, SIZE, HALF, K)
                got = u8(lab.js(code)).reshape(SIZE, SIZE).astype(np.int32)
                ref = cref.mask(kind, c, n, SIZE, HALF, K, absx=bool(ab[0]), absy=bool(ab[1]), flipy=bool(fl[0])).astype(np.int32)
                diff = got != ref
                nd = int(diff.sum()); un = 0
                if nd:
                    px, py = cref.grid(SIZE, HALF)
                    ok = cref.explained(px[diff], py[diff], got[diff], kind, c, n, bool(ab[0]), bool(ab[1]), bool(fl[0]), K)
                    un = int((~ok).sum())
                    if un:
                        bad = np.argwhere(diff)[~ok][:5]
                        defects.append("power %s, %s, %s%s: %d of %d points differ and %d are not within a hair of a skin, e.g. %s" % (
                            n, mname, kind, "" if c is None else " c=%s" % c, nd, SIZE * SIZE, un,
                            [(float(px[r, q]), float(py[r, q]), int(got[r, q]), int(ref[r, q])) for r, q in bad]))
                total_pts += SIZE * SIZE; total_diff += nd; total_unexpl += un
                left = [int((ref > k).sum()) for k in (0, 1, 2, 5, 16)]
                rows.append("power %-4s %-15s %s%-22s differ %3d  unexplained %d   (reference: points left after 0,1,2,5,16 steps: %s)" % (
                    n, mname, kind, "" if c is None else " c=%s" % c[:2], nd, un, left))
                log(rows[-1])
    log("")
    log("mask2 against the reference: %d masks, %d points, %d differ, %d of those not within a hair of a skin" % (len(rows), total_pts, total_diff, total_unexpl))

    # other grids: another size and half-width, and cell centres
    for size, half, opt in [(300, 1.3, None), (128, 2.0, True), (401, 0.4, None)]:
        for kind, c, n in [("m", None, 2), ("j", CS[1], 2), ("j", CS[2], 3)]:
            code = "setRule(%s, [0,0,0], [0,0]); %s return b64(L.shape.mask2('%s', %d, %s, %d%s));" % (
                json.dumps(n), ("L.shape.set({ c: %s });" % json.dumps(c)) if c else "", kind, size, half, K, ", { centres: true }" if opt else "")
            got = u8(lab.js(code)).reshape(size, size).astype(np.int32)
            if opt:
                d = 2.0 * half / size
                i = np.arange(size, dtype=np.float64)
                px, py = np.meshgrid(-(half - d / 2) + i * d, (half - d / 2) - i * d)
            else:
                px, py = cref.grid(size, half)
            ref = cref.out_points(px, py, kind, c, n, maxK=K)
            diff = got != ref; nd = int(diff.sum()); un = 0
            if nd:
                un = int((~cref.explained(px[diff], py[diff], got[diff], kind, c, n, False, False, False, K)).sum())
                if un: defects.append("grid %d, half %s, centres %s, %s, power %s: %d unexplained" % (size, half, bool(opt), kind, n, un))
            log("grid %d x %d, half %s%s, %s%s, power %s: differ %d, unexplained %d" % (size, size, half, ", cell centres" if opt else "", kind, "" if c is None else " c=%s" % c[:2], n, nd, un))

    # out2, point by point: random points in and around the big circle, and points on it
    rng = np.random.default_rng(26)
    P = rng.uniform(-2.2, 2.2, size=(3000, 2))
    ang = rng.uniform(0, 2 * np.pi, 200)
    P = np.vstack([P, np.c_[2 * np.cos(ang), 2 * np.sin(ang)], [[2, 0], [0, 2], [-2, 0], [0, -2], [1.2, 1.6], [0, 0], [-0.75, 0], [0.25, 0]]])
    tot = bad = 0
    for n in (2, 3, 2.5, -2, 0.5):
        for mname, ab, fl in MODS[:4]:
            for kind, c in [("m", None), ("j", CS[1]), ("j", CS[0])]:
                code = "setRule(%s, %s, %s); const P = %s; return P.map(p => L.shape.out2(p, '%s', %s, %d));" % (
                    json.dumps(n), json.dumps(ab), json.dumps(fl), json.dumps(P.tolist()), kind, json.dumps(c), K)
                got = np.array(lab.js(code), dtype=np.int32)
                ref = cref.out_points(P[:, 0], P[:, 1], kind, c, n, bool(ab[0]), bool(ab[1]), bool(fl[0]), K)
                diff = got != ref; nd = int(diff.sum()); tot += len(P)
                if nd:
                    ok = cref.explained(P[diff, 0], P[diff, 1], got[diff], kind, c, n, bool(ab[0]), bool(ab[1]), bool(fl[0]), K)
                    un = int((~ok).sum()); bad += un
                    log("out2 power %s, %s, %s%s: %d of %d differ, %d unexplained: %s" % (n, mname, kind, "" if c is None else " c=%s" % c[:2], nd, len(P), un, [(P[i].tolist(), int(got[i]), int(ref[i])) for i in np.argwhere(diff).ravel()[:4]]))
                    if un: defects.append("out2 power %s %s %s: %d unexplained" % (n, mname, kind, un))
    log("out2 against the reference: %d points asked one by one, %d not within a hair of a skin" % (tot, bad))
    # out2 with another maxK, and mask2 against out2 in the page itself (the contract's own check)
    r = lab.js("""setRule(2, [0,0,0], [0,0]); L.shape.set({ c: [-0.1226, 0.7449, 0] });
      let d = 0, n = 0; for (const kind of ['m', 'j']) { const M = L.shape.mask2(kind, 129, 2, 40); for (let r = 0; r < 129; r++) for (let q = 0; q < 129; q++) { n++; if (M[r * 129 + q] !== L.shape.out2([-2 + q * 4 / 128, 2 - r * 4 / 128], kind, [-0.1226, 0.7449, 0], 40)) d++; } }
      return [d, n];""")
    log("in the page: mask2 against out2 with maxK = 40, both kinds: %d of %d differ" % (r[0], r[1]))
    if r[0]: defects.append("mask2 and out2 differ at %d of %d points with maxK 40" % (r[0], r[1]))
    lab.js("setRule(2, [0,0,0], [0,0]); return 1;")
    log.problems(lab)

log("")
log("DEFECTS: %d" % len(defects))
for d in defects:
    log("  " + d)

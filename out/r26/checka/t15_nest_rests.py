"""(1) Nesting in the arithmetic, where it could fail. "Thrown out, for good" matters only when a point that has
    left can come back: powers below 1 and negative powers. With my reference I count, for such powers, the points
    of the big circle that are OUTSIDE at some step and INSIDE again at a later one. A page that asked only
    "is the dot inside after k steps?" would put those points back into the shape, and shape k + 1 would not lie
    in shape k. The page's mask2 is then compared with both readings.
    The same in space with my MATH / CARRY orbit and the card's slice.
(2) Play: how long the picture rests on each whole step (read every frame in the page), Fast and Normal.
"""
import json, time
import numpy as np
from clab import Lab, Log, u8
import cref

log = Log("t15_nest_rests")
defects = []
SIZE, K = 257, 16


def inside_after(kind, c, n, size, half, K):
    """for every point: bit k set when |z_k| <= 2 (no throwing out: the orbit is simply followed)"""
    px, py = cref.grid(size, half)
    with np.errstate(all="ignore"):
        if kind == "j": x, y, cx, cy = px.copy(), py.copy(), c[0], c[1]
        else: x, y, cx, cy = np.zeros_like(px), np.zeros_like(py), px, py
        start = px * px + py * py <= 4
        ins = [start]
        for k in range(1, K + 1):
            a, b = cref.cpow(x, y, n)
            x, y = a + cx, b + cy
            ins.append(start & (x * x + y * y <= 4))
    return np.array(ins)


with Lab("r26-checka") as lab:
    lab.js("await shapeOn({ kind: 'j', space: 2, pos: 0 }); return 1;")
    for n, kind, c in ((-2, "j", [0.28, 0.53, 0]), (0.5, "j", [1.2, 0.3, 0]), (-1.5, "j", [-0.1226, 0.7449, 0]), (0.5, "m", None), (-2, "j", [-1, 0, 0]), (2, "j", [-0.1226, 0.7449, 0])):
        ins = inside_after(kind, c, n, SIZE, 2.0, K)
        first = cref.mask(kind, c, n, SIZE, 2.0, K).astype(np.int32)
        # points that are outside at some step and inside at a later one
        gone = np.zeros(ins[0].shape, dtype=bool); back = np.zeros(ins[0].shape, dtype=bool)
        for k in range(1, K + 1):
            back |= gone & ins[k]
            gone |= ins[0] & ~ins[k]
        got = u8(lab.js("setRule(%s, [0,0,0], [0,0]); %s return b64(L.shape.mask2('%s', %d, 2, %d));" % (json.dumps(n), ("L.shape.set({ c: %s });" % json.dumps(c)) if c else "", kind, SIZE, K))).reshape(SIZE, SIZE).astype(np.int32)
        # the page's shapes against "thrown out for good" and against "inside after k steps"
        d_first = sum(int(((got > k) != (first > k)).sum()) for k in range(K + 1))
        d_naive = sum(int(((got > k) != ins[k]).sum()) for k in range(K + 1))
        nest_naive = sum(int((ins[k + 1] & ~ins[k]).sum()) for k in range(K))
        nest_page = sum(int(((got > k + 1) & ~(got > k)).sum()) for k in range(K))
        log("power %s, %s%s: %d of %d points of the big circle leave and are inside again later. Summed over the 17 shapes: the page differs from \"thrown out for good\" at %d points, from \"inside after k steps\" at %d; points in shape k + 1 and not in shape k: page %d, the other reading %d" % (
            n, kind, "" if c is None else " c=%s" % c[:2], int(back.sum()), int(ins[0].sum()), d_first, d_naive, nest_page, nest_naive))
        if nest_page: defects.append("power %s %s: the page's shapes do not nest (%d points)" % (n, kind, nest_page))
        if d_first > 40: defects.append("power %s %s: the page's shapes are not \"thrown out for good\": %d" % (n, kind, d_first))
    # in space
    r = lab.js("""
      const rows = [];
      for (const [id, n, kind, c] of [['mercator', -2, 'j', [0.28, 0.53, 0.2]], ['lathe', 0.5, 'j', [1.2, 0.3, 0.2]], ['pulledplane', -2, 'j', [0.28, 0.53, 0.2]], ['alongonce', 0.5, 'm', [0, 0, 0]]]) {
        await pickAp(id); setRule(n, [0,0,0], [0,0]);
        const g = ckView().slice(kind, c, { z: 0.3, half: 2, size: 129, maxK: 16 });
        let back = 0, ball = 0, dFirst = 0, dNaive = 0;
        for (let row = 0; row < 129; row++) for (let col = 0; col < 129; col++) {
          const p = ckPoint(row, col, 129, 2, 0.3); if (Math.hypot(...p) > 2) continue; ball++;
          // the orbit followed without throwing out
          const q = S.param[id], car = LAB.CARRY && LAB.CARRY[id] ? LAB.CARRY[id] : null; let st = car ? car.start(q) : null, z = kind === 'j' ? p.slice() : [0, 0, 0], cc = kind === 'j' ? c : p, was = false, came = false, firstOut = 17; const ins = [true];
          for (let k = 1; k <= 16; k++) { let w; if (car) { st = car.step(st, z, cc, q); w = car.pw(st, z, n); } else w = LAB.MATH[id](z, n, q, cc); z = [w[0] + cc[0], w[1] + cc[1], w[2] + cc[2]]; const inn = Math.hypot(...z) <= 2; ins.push(inn); if (!inn) { was = true; if (firstOut === 17) firstOut = k; } else if (was) came = true; }
          if (came) back++;
          const o = g[row * 129 + col];
          for (let k = 0; k <= 16; k++) { if ((o > k) !== (firstOut > k)) dFirst++; if ((o > k) !== ins[k]) dNaive++; }
        }
        rows.push([id, n, kind, ball, back, dFirst, dNaive]);
      }
      await pickAp('mercator'); setRule(2, [0,0,0], [0,0]); return rows;""")
    for id_, n, kind, ball, back, dF, dN in r:
        log("in space, %s, power %s, %s, slice at z = 0.3: %d of %d points leave and are inside again later; the card's shapes differ from \"thrown out for good\" at %d places (summed over 17 shapes), from \"inside after k steps\" at %d" % (id_, n, kind, back, ball, dF, dN))
        if dF > 60: defects.append("3D %s power %s: the card's shapes are not \"thrown out for good\": %d" % (id_, n, dF))

    # (2) the rests of Play
    for speed, rest_ms in (("fast", 150), ("normal", 350)):
        for space, kind in ((2, "m"), (3, "both")):
            lab.js("""L.shape.set({ kind: %s, space: %d, c: [-0.1226, 0.7449, 0], pos: 0 }); $('learnShapeSpeed').value = %s; $('learnShapeSpeed').dispatchEvent(new Event('change', { bubbles: true })); await sleep(300);
              const W = window.__w = { rest: {}, say: {}, done: false, t0: performance.now(), prev: -1, since: 0, lastSay: '', sayT: 0 };
              const tick = t => { const s = L.shape.state(), pos = s.pos, say = $('learnShapeSay').textContent, playing = s.playing;
                if (Number.isInteger(pos)) { if (W.prev !== pos) { W.prev = pos; W.since = t; } W.rest[pos] = t - W.since; } else W.prev = -1;
                if (say !== W.lastSay) { if (W.lastSay) W.say[W.lastSay] = Math.max(W.say[W.lastSay] || 0, t - W.sayT); W.lastSay = say; W.sayT = t; }
                if (!playing && pos >= 16) { W.done = true; W.took = t - W.t0; return; } requestAnimationFrame(tick); };
              $('learnShapePlay').click(); requestAnimationFrame(tick); return 1;""" % (json.dumps(kind), space, json.dumps(speed)))
            if not lab.wait("window.__w && window.__w.done", 60):
                defects.append("play %s %dD %s did not end" % (speed, space, kind)); continue
            w = lab.js("return window.__w;")
            rests = [w["rest"].get(str(k), 0) for k in range(1, 16)]
            says = sorted(w["say"].values())
            short = [(k + 1, round(x)) for k, x in enumerate(rests) if x < 0.8 * rest_ms]
            log("Play, %s, %dD %s: %.1f s; rests on the steps 1 to 15: shortest %.0f ms, longest %.0f ms (meant: %d); %d sentences each shown for at least %.0f ms; rests shorter than 0.8 of the meant: %s" % (
                speed, space, kind, w["took"] / 1000, min(rests), max(rests), rest_ms, len(says), says[0] if says else 0, short))
            if short: defects.append("Play %s %dD %s: rests cut short: %s" % (speed, space, kind, short))
    n = log.problems(lab)
    if n: defects.append("console: %s" % lab.problems[:3])
log("DEFECTS: %d" % len(defects))
for d in defects: log("  " + d)

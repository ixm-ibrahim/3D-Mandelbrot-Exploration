"""Check 2 and 3, the 3D PICTURE itself: is what the module draws shape k, and do the shapes nest in the picture?
A view of my own (learnShape3d.make()) draws one skin, shape k as solid glass and nothing else, 600 x 450, 'still'.
  (1) The outline against arithmetic. For every fourth pixel each way the straight line of sight through the big
      ball is walked in JavaScript with my own MATH / CARRY orbit (240 stops across the ball), which says how many
      stops lie in shape k. Where the line runs through shape k for 4 stops or more the picture must show something
      (differ from the background); where neither it nor its eight neighbours meet shape k at all the picture must
      show the background.
  (2) Nesting: a pixel that shows something of shape k + 1 must show something of shape k (k = 0 .. 15).
The camera is worked out here (yaw about z, pitch above the flat plane, no perspective, the ball 80 % of the
smaller side at zoom 1), not taken from the module's proj.
"""
import json, sys, time
import numpy as np
from clab import Lab, Log, u8

log = Log("t5_solid")
W, H, STEP, NS, K = 600, 450, 4, 240, 16
BG = [0.03, 0.05, 0.07]
SCENES = [
    ("mercator", 2, None, "m", [0, 0, 0], -0.62, 0.4, 1),
    ("mercator", 2, None, "j", [-0.1226, 0.7449, 0], -0.62, 0.4, 1),
    ("fold", 2, None, "j", [-1, 0, 0], 0.9, 0.25, 1),
    ("alongonce", 2, None, "m", [0, 0, 0], -0.62, 0.4, 1),
    ("pulledplane", 2, None, "j", [-0.3, 0.2, 0.1], -2.0, -0.5, 1),
    ("lathe", 3, None, "m", [0, 0, 0], -0.62, 0.4, 1),
    ("bulb", 2, {"lat": 20, "lon": -35}, "j", [-0.4, 0.3, 0.2], 0.3, 1.2, 1.6),
    ("pillow", 2, None, "j", [-1, 0, 0], -0.62, 0.4, 1),
]
SETUP = """
const [id, n, moved, kind, c, yaw, pitch, zoom] = %s;
await pickAp(id); dialsBack(id); if (moved) Object.assign(S.param[id], moved); setRule(n, [0,0,0], [0,0]);
window.__sc = { id, n, kind, c, yaw, pitch, zoom };
return LAB.learnShape3d.ok();
"""
# the lines of sight, in chunks of rows: for each asked pixel, for k = 0..16, how many stops lie in shape k (capped at 255)
RAYS = """
const [row0, row1, W, H, STEP, NS, K] = %s, sc = window.__sc;
const cy = Math.cos(sc.yaw), sy = Math.sin(sc.yaw), cp = Math.cos(sc.pitch), sp = Math.sin(sc.pitch);
const R = [cy, sy, 0], U = [-sy * sp, cy * sp, cp], D = [sy * cp, -cy * cp, sp], s = 0.2 * Math.min(W, H) * sc.zoom;
const cols = Math.floor((W - 1) / STEP) + 1, out = new Uint8Array((row1 - row0) * cols * (K + 1)), hist = new Uint16Array(K + 2);
for (let r = row0; r < row1; r++) for (let q = 0; q < cols; q++) {
  const x = (q * STEP + 0.5 - W / 2) / s, y = (H / 2 - (r * STEP + 0.5)) / s, d2 = x * x + y * y;
  if (d2 >= 4) continue;
  const h = Math.sqrt(4 - d2), dt = 2 * h / NS;
  hist.fill(0);
  for (let i = 0; i < NS; i++) { const t = -h + (i + 0.5) * dt; hist[ckOut3([x * R[0] + y * U[0] + t * D[0], x * R[1] + y * U[1] + t * D[1], x * R[2] + y * U[2] + t * D[2]], sc.kind, sc.c, K)]++; }
  let more = hist[K + 1]; const o = ((r - row0) * cols + q) * (K + 1);
  for (let k = K; k >= 0; k--) { out[o + k] = Math.min(255, more); more += hist[k]; }
}
return b64(out);
"""
DRAW = """
const [k, W, H, BG] = %s, sc = window.__sc, v = ckView();
const res = v.draw({ panes: [{ kind: sc.kind, rect: [0, 0, W, H] }], c: sc.c, levels: [{ k, alpha: 1, tint: 0 }], yaw: sc.yaw, pitch: sc.pitch, zoom: sc.zoom, quality: 'still', lod: 0,
  colours: { bg: BG, body: [0.86, 0.68, 0.35], warn: [0.94, 0.5, 0.46], ink: [0.89, 0.91, 0.93] } });
if (!res.ok) fail('draw: ' + res.note);
const cv = window.__ck2 || (window.__ck2 = document.createElement('canvas')); cv.width = v.canvas.width; cv.height = v.canvas.height;
const g = cv.getContext('2d', { willReadFrequently: true }); g.drawImage(v.canvas, 0, 0);
const d = g.getImageData(0, 0, cv.width, cv.height).data, bw = cv.width, bh = cv.height, f = bw / W;
// for each CSS pixel: the largest distance from the background colour among its buffer pixels
const m = new Uint8Array(W * H), b = BG.map(x => x * 255);
for (let y = 0; y < bh; y++) for (let x = 0; x < bw; x++) { const o = (y * bw + x) * 4, e = Math.max(Math.abs(d[o] - b[0]), Math.abs(d[o + 1] - b[1]), Math.abs(d[o + 2] - b[2])); const i = Math.floor(y / f) * W + Math.floor(x / f); if (e > m[i]) m[i] = Math.min(255, Math.round(e)); }
return { m: b64(m), bw, bh, stats: v.stats().last };
"""
# A second, much finer walk for the lines of sight where the picture shows something and the first walk found nothing:
# the four lines the picture itself draws through that pixel (it has four buffer pixels to a pixel), 4000 stops each.
FINE = """
const [list, W, H, STEP, K] = %s, sc = window.__sc, NS = 4000;
const cy = Math.cos(sc.yaw), sy = Math.sin(sc.yaw), cp = Math.cos(sc.pitch), sp = Math.sin(sc.pitch);
const R = [cy, sy, 0], U = [-sy * sp, cy * sp, cp], D = [sy * cp, -cy * cp, sp], s = 0.2 * Math.min(W, H) * sc.zoom;
return list.map(([r, q, k]) => {
  let n = 0;
  for (const dx of [0.25, 0.75]) for (const dy of [0.25, 0.75]) {
    const x = (q * STEP + dx - W / 2) / s, y = (H / 2 - (r * STEP + dy)) / s, d2 = x * x + y * y;
    if (d2 >= 4) continue;
    const h = Math.sqrt(4 - d2), dt = 2 * h / NS;
    for (let i = 0; i < NS; i++) { const t = -h + (i + 0.5) * dt; if (ckOut3([x * R[0] + y * U[0] + t * D[0], x * R[1] + y * U[1] + t * D[1], x * R[2] + y * U[2] + t * D[2]], sc.kind, sc.c, K) > k) n++; }
  }
  return n;
});
"""
defects, pics = [], []
t0 = time.time()
with Lab("r26-checka") as lab:
    lab.js("await shapeOn({ kind: 'm', space: 2, pos: 2 }); return 1;")
    for sc in SCENES:
        name = "%s%s power %s, %s%s, yaw %s pitch %s zoom %s" % (sc[0], (" " + json.dumps(sc[2])) if sc[2] else "", sc[1], sc[3], "" if sc[3] == "m" else " c=%s" % sc[4], sc[5], sc[6], sc[7])
        if not lab.js(SETUP % json.dumps(list(sc))):
            defects.append(name + ": no program"); continue
        rows = (H - 1) // STEP + 1; cols = (W - 1) // STEP + 1
        ref = np.zeros((rows, cols, K + 1), dtype=np.uint8)
        t1 = time.time()
        for r0 in range(0, rows, 12):
            r1 = min(rows, r0 + 12)
            ref[r0:r1] = u8(lab.js(RAYS % json.dumps([r0, r1, W, H, STEP, NS, K]))).reshape(r1 - r0, cols, K + 1)
        t_rays = time.time() - t1
        prev = None; nest = 0; lines = []; miss_t = extra_t = 0; flagged = []
        for k in range(0, K + 1):
            r = lab.js(DRAW % json.dumps([k, W, H, BG]))
            m = u8(r["m"]).reshape(H, W).astype(np.int32)
            cover = m > 4                                       # the picture shows something there
            if prev is not None:
                # nesting, with one pixel of grace for the smoothed rim
                grown = prev.copy()
                grown[1:] |= prev[:-1]; grown[:-1] |= prev[1:]; grown[:, 1:] |= prev[:, :-1]; grown[:, :-1] |= prev[:, 1:]
                bad = cover & ~grown
                nest += int(bad.sum())
            prev = cover
            cnt = ref[:, :, k].astype(np.int32)
            pic = m[0::STEP, 0::STEP][:rows, :cols]
            sure_in = cnt >= 4
            pad = np.pad(cnt, 1, mode="edge"); nb = np.zeros_like(cnt)
            for dy in (0, 1, 2):
                for dx in (0, 1, 2):
                    nb = np.maximum(nb, pad[dy:dy + rows, dx:dx + cols])
            sure_out = nb == 0
            miss = int((sure_in & (pic <= 4)).sum()); extra = int((sure_out & (pic > 4)).sum())
            miss_t += miss; extra_t += extra
            flagged += [[int(y), int(x), k] for y, x in zip(*np.nonzero(sure_out & (pic > 4)))]
            lines.append("k=%d: in %d (missing %d), out %d (drawn %d)" % (k, int(sure_in.sum()), miss, int(sure_out.sum()), extra))
            if k in (0, 3, 8, 16):
                img = np.clip(np.stack([m * 3] * 3, -1), 0, 255).astype(np.uint8)
                wrong = np.zeros((H, W), dtype=bool)
                ys, xs = np.nonzero((sure_in & (pic <= 4)) | (sure_out & (pic > 4)))
                for y, x in zip(ys, xs):
                    wrong[y * STEP:y * STEP + 3, x * STEP:x * STEP + 3] = True
                img[wrong] = [255, 0, 255]
                if miss or extra:
                    pics.append(lab.save(img, "out/r26/checka/t5-WRONG-%s-%s-%02d.png" % (sc[0], sc[3], k)))
        log("%s   (rays %.0f s; buffer %s x %s)" % (name, t_rays, r["bw"], r["bh"]))
        log("    outline against arithmetic, lines of sight that run 4 stops or more through shape k / that miss it with all their neighbours:")
        for i in range(0, len(lines), 3):
            log("      " + ";  ".join(lines[i:i + 3]))
        log("    total: %d lines through the shape where the picture shows nothing, %d lines past it where the picture shows something" % (miss_t, extra_t))
        log("    nesting in the picture: %d pixels show something of shape k + 1 and nothing of shape k (k = 0..15, one pixel of grace)" % nest)
        thin = 0; none = 0
        for i in range(0, min(len(flagged), 240), 40):
            for n_in in lab.js(FINE % json.dumps([flagged[i:i + 40], W, H, STEP, K])):
                if n_in: thin += 1
                else: none += 1
        if flagged:
            log("    the %d lines past the shape, walked again with 4 x 4000 stops (the first %d of them): %d do meet shape k (a sliver thinner than my first walk), %d do not" % (len(flagged), min(len(flagged), 240), thin, none))
        if miss_t or none: defects.append("%s: outline: %d lines through the shape with nothing drawn, %d pixels drawn where a fine walk finds nothing of the shape" % (name, miss_t, none))
        if nest: defects.append("%s: nesting: %d pixels" % (name, nest))
        lab.js("dialsBack(AP().id); go(); return 1;")
    lab.js("await pickAp('mercator'); setRule(2, [0,0,0], [0,0]); return 1;")
    log.problems(lab)
log("pictures: " + ", ".join(p.replace("\\", "/").split("/checka/")[-1] for p in pics))
log("DEFECTS: %d   (%.0f s)" % (len(defects), time.time() - t0))
for d in defects: log("  " + d)

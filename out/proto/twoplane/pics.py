"""Standard pictures for the pillow prototype, and the piece counts of the 2D slices.

  python out/proto/twoplane/pics.py [all|speed|count]

Builds a list of steps for tools/shot.py, runs it on dist/proto-twoplane.html and saves the output as text
(pics.txt, speed.txt or count.txt next to this file).
"""
import json, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
OUT = "out/proto/twoplane/"
PRE = "const L = window.squaringLab, S = L.S, cam = L.cam, $ = id => document.getElementById(id); "

# Membership on the picture's own pixel grid, in double precision with the JavaScript mirror of the rule, then
# 8-connected pieces. A piece counts when it holds at least 0.05% of the picture.
PIECES = PRE + """
window.__pieces = (id) => {
  const ai = id ? L.APPROACHES.findIndex(a => a.id === id) : S.approach, a = L.APPROACHES[ai], F = L.MATH[a.id], q = { ...S.param[a.id] };
  const st = $('stage'), W = st.clientWidth, H = st.clientHeight, sc = S.v2.h / H, n = S.n, it = S.iter, jul = S.mode === 'j', cz = S.cut;
  const mask = new Uint8Array(W * H);
  let solid = 0;
  for (let py = 0; py < H; py++) for (let px = 0; px < W; px++) {
    const x = S.v2.x + (px + 0.5 - W / 2) * sc, y = S.v2.y + (H / 2 - py - 0.5) * sc;
    let z = jul ? [x, y, cz] : [0, 0, 0], inside = true;
    const c = jul ? S.c : [x, y, cz];
    for (let k = 0; k <= it; k++) {
      if (!(z[0] * z[0] + z[1] * z[1] + z[2] * z[2] <= 4096)) { inside = false; break; }
      if (k === it) break;
      const w = F(z, n, q); z = [w[0] + c[0], w[1] + c[1], w[2] + c[2]];
    }
    if (inside) { mask[py * W + px] = 1; solid++; }
  }
  const lab = new Int32Array(W * H), sizes = [], stack = new Int32Array(W * H);
  for (let s0 = 0; s0 < W * H; s0++) {
    if (!mask[s0] || lab[s0]) continue;
    const tag = sizes.length + 1; let sp = 0, size = 0; stack[sp++] = s0; lab[s0] = tag;
    while (sp) {
      const p = stack[--sp], x = p % W, y = (p - x) / W; size++;
      for (let dy = -1; dy <= 1; dy++) for (let dx = -1; dx <= 1; dx++) {
        const xx = x + dx, yy = y + dy; if (xx < 0 || yy < 0 || xx >= W || yy >= H) continue;
        const t = yy * W + xx; if (mask[t] && !lab[t]) { lab[t] = tag; stack[sp++] = t; }
      }
    }
    sizes.push(size);
  }
  sizes.sort((p, q) => q - p);
  const min = 0.0005 * W * H, big = sizes.filter(s => s >= min), rest = sizes.slice(big.length).reduce((p, q) => p + q, 0), pc = s => (100 * s / Math.max(solid, 1)).toFixed(2) + '%';
  return `${a.id}${a.id === 'mercator' ? ' planes ' + q.planes : ''} ${jul ? 'Julia c=(' + S.c.join(', ') + ')' : 'Mandelbrot'} n=${n} slice z=${cz}: ${W}x${H} px, solid ${solid} px (${(100 * solid / (W * H)).toFixed(1)}% of the picture); ` +
    `pieces of at least ${Math.ceil(min)} px: ${big.length}; largest piece ${pc(sizes[0] || 0)} of the solid; next largest: ${big.slice(1, 6).map(pc).join(', ') || 'none'}; ` +
    `specks below that size: ${sizes.length - big.length}, holding ${pc(rest)} of the solid`;
};
"""

steps = []


def step(js, shot=None, wait=True, timeout=400):
    s = {"js": PRE + js}
    if wait:
        s["wait"] = "done"; s["timeout"] = timeout
    if shot:
        s["shot"] = OUT + shot; s["clip"] = "#stage"
    steps.append(s)


TOP = "cam.yaw = -Math.PI / 2; cam.pitch = 1.5698; "
ALONG_X = "cam.yaw = 0; cam.pitch = 0; "
ALONG_Y = "cam.yaw = -Math.PI / 2; cam.pitch = 0; "


def flat(on):
    return "if (S.flat !== %s) $('flat').click(); " % ("true" if on else "false")


def pictures():
    steps.append({"js": PIECES + "L.R.warmOn = false; return 'approach ' + L.APPROACHES[S.approach].id + ', stage ' + $('stage').clientWidth + 'x' + $('stage').clientHeight;", "wait": "done", "timeout": 400})
    step("L.touch(); return 'm3d-default';", "m3d-default.png")
    step(TOP + "L.touch(); return 'top';", "m3d-top.png")
    step(ALONG_X + "L.touch(); return 'along x';", "m3d-x.png")
    step(ALONG_Y + "L.touch(); return 'along y';", "m3d-y.png")
    step("S.cutOn = true; S.cut = 0; cam.yaw = -1.25; cam.pitch = 0.873; L.syncControls(); L.touch(); return 'cut 0';", "m3d-cut0.png")
    step("S.cut = 0.2; L.syncControls(); L.touch(); return 'cut 0.2';", "m3d-cut02.png")
    for z, name in [(0, "m2d-z000"), (0.1, "m2d-z010"), (0.25, "m2d-z025"), (0.5, "m2d-z050")]:
        step("S.cutOn = false; " + flat(True) + "S.cut = %s; S.v2.x = -0.75; S.v2.y = 0; S.v2.h = 3.0; L.syncControls(); L.touch(); return window.__pieces();" % z, name + ".png")
    step(flat(False) + "S.cut = 0; $('mode-j').click(); S.c[0] = -1; S.c[1] = 0; S.c[2] = 0; L.resetCam(); L.syncControls(); L.touch(); return 'julia c = ' + S.c + ' cam ' + JSON.stringify(cam);", "j-bas-3d.png")
    step(TOP + "L.touch(); return 'top';", "j-bas-top.png")
    step(ALONG_X + "L.touch(); return 'along x';", "j-bas-x.png")
    step(ALONG_Y + "L.touch(); return 'along y (extra)';", "j-bas-y.png")
    for z, name in [(0, "j-bas-2d-z000"), (0.2, "j-bas-2d-z020")]:
        step(flat(True) + "S.cut = %s; S.v2.x = 0; S.v2.y = 0; S.v2.h = 2.9; L.syncControls(); L.touch(); return window.__pieces();" % z, name + ".png")
    step(flat(False) + "S.cut = 0; S.c[0] = -0.1226; S.c[1] = 0.7449; S.c[2] = 0; L.resetCam(); L.syncControls(); L.touch(); return 'julia c = ' + S.c;", "j-rab-3d.png")
    for n in (3, 8):
        step("if (S.mode !== 'm') $('mode-m').click(); S.n = %d; L.resetCam(); L.syncControls(); L.refresh(false); return 'mandelbrot n = ' + S.n + ' cam ' + JSON.stringify(cam);" % n, "m3d-n%d.png" % n)


def speed():
    # the finished default picture, timed from touch() to idle, each approach twice, turn about
    timer = "const sleep = ms => new Promise(r => setTimeout(r, ms)); const t0 = performance.now(); L.touch(); await sleep(300); while (!L.idle()) await sleep(10); return %s + ' default picture: ' + ((performance.now() - t0) / 1000).toFixed(2) + ' s (' + $('status').textContent + ')';"
    steps.append({"js": PRE + "L.R.warmOn = false; return 'warm: pillow';", "wait": "done", "timeout": 400})
    steps.append({"js": PRE + "$('ap-mercator').click(); return 'warm: mercator, planes ' + S.param.mercator.planes;", "wait": "done", "timeout": 400})
    for _ in range(7):
        steps.append({"js": PRE + "$('ap-pillow').click(); return 'pillow';", "wait": "done", "timeout": 400})
        steps.append({"js": PRE + timer % "'pillow'"})
        steps.append({"js": PRE + "$('ap-mercator').click(); return 'mercator';", "wait": "done", "timeout": 400})
        steps.append({"js": PRE + timer % "'mercator planes ' + S.param.mercator.planes"})


def count():
    # the same piece counts for the sphere-inversion approach (two planes, then one), for comparison; nothing is drawn
    steps.append({"js": PIECES + "L.R.warmOn = false; return 'counting';", "wait": "done", "timeout": 400})
    for planes in (2, 1):
        for z in (0, 0.1, 0.25, 0.5):
            steps.append({"js": PRE + "S.mode = 'm'; S.param.mercator.planes = %d; S.cut = %s; S.v2.x = -0.75; S.v2.y = 0; S.v2.h = 3.0; return window.__pieces('mercator');" % (planes, z)})
        for z in (0, 0.2):
            steps.append({"js": PRE + "S.mode = 'j'; S.c[0] = -1; S.c[1] = 0; S.c[2] = 0; S.param.mercator.planes = %d; S.cut = %s; S.v2.x = 0; S.v2.y = 0; S.v2.h = 2.9; return window.__pieces('mercator');" % (planes, z)})
    steps.append({"js": PRE + "S.mode = 'm'; S.cut = 0; S.param.mercator.planes = 2; return 'done';"})


def extra():
    # Not standard pictures: the creases seen from the B corner direction, and two pictures at the Fine preset
    # to tell speckle that belongs to the solid from speckle the Balanced preset adds.
    steps.append({"js": PRE + "L.R.warmOn = false; return 'extra';", "wait": "done", "timeout": 400})
    step("cam.yaw = 2 * Math.PI / 3; cam.pitch = 0; cam.target = [0, 0, 0]; L.touch(); return 'mandelbrot from the B direction';", "extra/m3d-fromB.png")
    step("$('mode-j').click(); S.c[0] = 0.2; S.c[1] = 0; S.c[2] = 0; L.resetCam(); cam.yaw = 2 * Math.PI / 3; cam.pitch = 0.35; L.syncControls(); L.touch(); return 'julia c = (0.2, 0, 0) from above the B direction';", "extra/j-c02-fromB.png")
    step("cam.yaw = 0; cam.pitch = 0.35; L.touch(); return 'julia c = (0.2, 0, 0) from above the A direction';", "extra/j-c02-fromA.png")
    step("S.c[0] = -1; L.resetCam(); $('qFine').click(); L.syncControls(); L.touch(); return 'basilica, Fine preset: ' + JSON.stringify(S.q);", "extra/j-bas-3d-fine.png", timeout=900)
    step("$('mode-m').click(); L.resetCam(); L.touch(); return 'mandelbrot, Fine preset';", "extra/m3d-default-fine.png", timeout=900)


what = sys.argv[1] if len(sys.argv) > 1 else "all"
{"all": pictures, "speed": speed, "count": count, "extra": extra}[what]()
plan = os.path.join(HERE, "plan-%s.json" % what)
with open(plan, "w", encoding="utf-8") as f:
    json.dump(steps, f, indent=1)
out = OUT + {"all": "pics.txt", "speed": "speed.txt", "count": "count.txt", "extra": "extra.txt"}[what]
url = sys.argv[2] if len(sys.argv) > 2 else "dist/proto-twoplane.html"
sys.exit(subprocess.call([sys.executable, os.path.join(ROOT, "notes", "approaches_run.py"), url, out, "--actions", plan], cwd=ROOT))

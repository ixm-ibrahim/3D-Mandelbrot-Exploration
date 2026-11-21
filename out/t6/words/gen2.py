"""More step files of tester "words": python out/t6/words/gen2.py"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen import step, write

# ---------------------------------------------------------------- Show Figure 4, Back to one plane and the four twin buttons, from seven states
RESET = "L.resetAll(); L.setCamMode(false); await sleep(80);\n"
STATES = {
    'a-fresh': "",
    'b-klein2d': "$('mode-k').click(); pickOpt('kleinPreset', '1/2'); $('flat').click(); $('cutOn').click(); S.cut = 0.3; L.setExtreme(true); S.k.iter = 600; L.syncControls(); L.refresh(false);",
    'c-julia-lathe': "$('mode-j').click(); pickOpt('juliaPreset', 'Douady rabbit'); $('ap-lathe').click(); S.n = 3; S.param.lathe.spin = 3; S.abs = [1, 0, 0]; S.flip = [1, 1]; pickOpt('col-trap', 'Cross'); pickOpt('col-solid', 'Is the solid'); S.cutOn = true; S.cut = 0.2; L.syncControls(); L.refresh(false);",
    'd-mosaic-classic8': "$('ap-classic').click(); S.n = 8; S.param.classic.theta = 40; $('m-mosaic').click(); $('flat').click(); $('eqPreset').selectedIndex = 3; $('eqPreset').dispatchEvent(new Event('change', { bubbles: true })); S.v2.h = 0.2; S.v2.x = 0.3; cam.dist = 0.4; cam.target = [0.3, 0.2, 0.1]; L.syncControls(); L.refresh(false);",
    'e-fly-radius-fov': "L.setCamMode(true); S.view.bound = 1.5; S.view.fov = Math.tan(100 * Math.PI / 360); cam.target = [3, 3, 2]; cam.yaw = 2; cam.pitch = -0.4; L.syncControls(); L.viewChanged(); L.touch();",
    'f-sweeping': "$('mode-j').click(); S.c = [0.2, 0.5, 0.3]; S.param.mercator.lift = 0.6; L.syncControls(); $('par-mercator-turnPlay').click(); $('par-mercator-liftPlay').click(); $('qUltra').click(); S.iter = 40; $('eq').value = 'z^n + c + 0.1'; $('z0').value = 'c'; $('eq').dispatchEvent(new Event('change', { bubbles: true })); pickOpt('col-solid', 'Is added'); L.syncControls(); L.refresh(false);",
    'g-zoomlimit-iter': "S.view.zmax = 3; S.iter = 5; cam.dist = 2; L.syncControls(); L.viewChanged(); L.touch();",
}
REPORT = "await sleep(1300); return JSON.stringify({ st: st(), shown: shown(), probes: probes(), busy: $('busy') && !$('busy').hidden ? $('busy').textContent : '' });"


def press(btn):
    return "$('%s').scrollIntoView({ block: 'center' }); await sleep(120); $('%s').click(); await sleep(60); return 'pressed %s';" % (btn, btn, btn)


def figsteps(tag, names, shots_of_state=True):
    out = []
    for k in names:
        setx = RESET + STATES[k]
        out.append(step(setx + "\nreturn 'state %s';" % k, timeout=400, shot=('%s-%s-0state.png' % (tag, k)) if shots_of_state else None))
        out.append(step("return JSON.stringify({ before: st() });", wait=None))
        out.append(step(press('fig4Show'), timeout=400, shot='%s-%s-1fig4.png' % (tag, k)))
        out.append(step(REPORT, wait=None))
        out.append(step(press('fig4Back'), timeout=400, shot='%s-%s-2oneplane.png' % (tag, k)))
        out.append(step(REPORT, wait=None))
        for btn, short in (('twinMerc', '3twinM'), ('twinLathe', '5twinL'), ('twinBulb', '6twinB')):
            out.append(step(setx + "\nawait sleep(500); return 'state again';", wait=None))
            out.append(step(press(btn), timeout=400, shot='%s-%s-%s.png' % (tag, k, short)))
            out.append(step(REPORT, wait=None))
            if btn != 'twinLathe':
                out.append(step(press('twinOff'), timeout=400, shot=('%s-%s-%soff.png' % (tag, k, short)) if btn == 'twinMerc' else None))
                out.append(step(REPORT, wait=None))
    return out


write('fig', figsteps('fig', list(STATES)))
write('figp', figsteps('figp', ['a-fresh', 'c-julia-lathe'], shots_of_state=False))

# ---------------------------------------------------------------- one plane: slices at five heights, in numbers, in the 2D view and with the cut
COMP = r"""
// pieces of the inside of the slice at height z: 8-connected groups of grid points within 0.7 of a grid step of the solid
const comp = async (z, cx, cy, side, N) => {
  const snap = L.takeSnapshot(); const a = await L.sampleSlice(snap, cx, cy, side, z, N); L.releaseSnapshot(snap);
  if (!a) return null;
  const thr = 0.7 * side / N, m = new Uint8Array(N * N); let inside = 0, strict = 0;
  for (let i = 0; i < N * N; i++) { if (a[4 * i + 3] <= thr) { m[i] = 1; inside++; } if (a[4 * i + 3] <= 0) strict++; }
  const sizes = [], stack = [];
  for (let s = 0; s < N * N; s++) if (m[s] === 1) {
    let n = 0; m[s] = 2; stack.push(s);
    while (stack.length) { const p = stack.pop(), x = p % N, y = (p - x) / N; n++;
      for (let dy = -1; dy <= 1; dy++) for (let dx = -1; dx <= 1; dx++) { const X = x + dx, Y = y + dy; if (X < 0 || Y < 0 || X >= N || Y >= N) continue; const q = Y * N + X; if (m[q] === 1) { m[q] = 2; stack.push(q); } } }
    sizes.push(n);
  }
  sizes.sort((p, q) => q - p);
  return { z: +z.toFixed(3), inside, strict, pieces: sizes.length, big: sizes.slice(0, 5), share: inside ? +(sizes[0] / inside).toFixed(4) : 0 };
};
const top = async (cx, cy, side) => { let t = 0; for (let z = 0.02; z < 2.01; z += 0.02) { const r = await comp(z, cx, cy, side, 96); if (r && r.strict > 0) t = z; else if (z > t + 0.2) break; } return t; };
"""
SOLIDS = [
    ('mandel', "", (-0.5, 0, 3.2)),
    ('basilica', "$('mode-j').click(); pickOpt('juliaPreset', 'Basilica');", (0, 0, 3.8)),
    ('rabbit', "$('mode-j').click(); pickOpt('juliaPreset', 'Douady rabbit');", (0, 0, 3.8)),
    ('crackedbas', "$('mode-j').click(); pickOpt('juliaPreset', 'Cracked Basilica');", (0, 0, 3.8)),
    ('rabbit-2planes', "$('mode-j').click(); pickOpt('juliaPreset', 'Douady rabbit'); S.param.mercator.planes = 2; L.syncControls(); L.refresh(false);", (0, 0, 3.8)),
]
slices = []
for name, setx, (cx, cy, side) in SOLIDS:
    slices.append(step(RESET + setx + "\nreturn 'solid %s, planes ' + S.param.mercator.planes + ', iter ' + S.iter + ', c ' + S.c;" % name, timeout=400, shot='slice-%s-3d.png' % name))
    slices.append(step(COMP + r"""
const t = await top(%g, %g, %g); const hs = [0.12, 0.3, 0.5, 0.7, 0.9].map(f => +(f * t).toFixed(3)); window.__h = hs;
const out = [await comp(0, %g, %g, %g, 400)]; for (const z of hs) out.push(await comp(z, %g, %g, %g, 400));
const neg = await comp(-hs[2], %g, %g, %g, 400);
return JSON.stringify({ solid: '%s', top: +t.toFixed(2), heights: hs, slices: out, mirror: neg });
""" % (cx, cy, side, cx, cy, side, cx, cy, side, cx, cy, side, name), wait=None))
    for k in range(5):
        slices.append(step("$('flat').checked || $('flat').click(); S.cut = window.__h[%d]; L.syncControls(); L.touch(); await sleep(60); return 'flat z ' + S.cut + ' label ' + $('flatZ').textContent;" % k, timeout=300, shot='slice-%s-2d-%d.png' % (name, k)))
    slices.append(step("$('flat').checked && $('flat').click(); cam.pitch = 0.95; L.syncControls(); L.touch(); return 'to 3d';", wait=None))
    for k in range(5):
        slices.append(step("S.cutOn = true; S.cut = window.__h[%d]; L.syncControls(); L.touch(); await sleep(60); return 'cut z ' + S.cut + ' ' + $('cutOn').checked;" % k, timeout=300, shot='slice-%s-cut-%d.png' % (name, k)))
write('slices', slices)

# ---------------------------------------------------------------- N11: the Douady rabbit with the rough distance estimate, four distances, three sides
SIDES = [('top', -1.571, 1.1), ('side', -1.571, 0.12), ('end', 0.25, 0.45)]
DISTS = [9, 4.6, 2.6, 1.6]


def n11(tag, sides, dists, ultra):
    out = [step("$('mode-j').click(); pickOpt('juliaPreset', 'Douady rabbit'); $('juliaFrame').click(); return 'rabbit ' + S.c + ' iter ' + S.iter + ' de ' + S.q.de;", timeout=400)]
    for sname, yaw, pitch in sides:
        for d in dists:
            cam_js = "cam.yaw = %g; cam.pitch = %g; cam.dist = %g; cam.target = [0, 0, 0]; " % (yaw, pitch, d)
            out.append(step(cam_js + "pickOpt('qde', 'Rough'); L.touch(); await sleep(60); return 'rough de ' + S.q.de + ' ' + sel('qde') + ' normals ' + S.q.normals;", timeout=400, shot='%s-%s-%g-rough.png' % (tag, sname, d)))
            out.append(step("pickOpt('qde', 'Exact'); L.touch(); await sleep(60); return 'exact de ' + S.q.de;", timeout=400, shot='%s-%s-%g-exact.png' % (tag, sname, d)))
    if ultra:
        for sname, yaw, pitch in sides:
            out.append(step("$('qUltra').click(); cam.yaw = %g; cam.pitch = %g; cam.dist = 4.6; cam.target = [0, 0, 0]; L.touch(); await sleep(60); return 'ultra ' + JSON.stringify(S.q);" % (yaw, pitch), timeout=400, shot='%s-%s-ultra.png' % (tag, sname)))
        # as it was found (24 iterations), rough, from the top and the side
        for sname, yaw, pitch in sides[:2]:
            out.append(step("$('qBal').click(); S.iter = 24; pickOpt('qde', 'Rough'); cam.yaw = %g; cam.pitch = %g; cam.dist = 4.6; cam.target = [0, 0, 0]; L.syncControls(); L.touch(); await sleep(60); return 'iter 24 rough';" % (yaw, pitch), timeout=400, shot='%s-%s-iter24-rough.png' % (tag, sname)))
    return out


write('n11', n11('n11', SIDES, DISTS, True))
write('n11v5', n11('n11v5', SIDES[:2], [4.6, 1.6], False))

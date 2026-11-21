"""Step files of tester "words", second check. python out/t9/words/gen9.py  writes out/t9/words/steps-*.json
Run each with:  PYTHONIOENCODING=utf-8 python tools/shot.py --url dist/v8.html --actions out/t9/words/steps-<name>.json
(adapted from out/t6/words/gen.py and gen2.py)
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen
from gen import write

MORE = r"""
const VIEW = () => ({ zmin: S.view.zmin, zmax: S.view.zmax, bound: S.view.bound, fov: +(2 * Math.atan(S.view.fov) * 180 / Math.PI).toFixed(1), fly: S.view.fly });
const byLabel = text => { const l = [...document.querySelectorAll('label')].find(x => x.textContent.replace(/\s+/g, ' ').trim().startsWith(text)); if (!l) throw new Error('no label ' + text); return l.htmlFor ? $(l.htmlFor) : l.querySelector('input'); };
const full = () => JSON.parse(JSON.stringify({ S, cam: { yaw: cam.yaw, pitch: cam.pitch, dist: cam.dist, target: cam.target }, eq: $('eq').value, z0: $('z0').value }));
const diff = (a, b, p, out) => { out = out || []; p = p || '';
  if (a && b && typeof a === 'object' && typeof b === 'object') { for (const k of new Set([...Object.keys(a), ...Object.keys(b)])) diff(a[k], b[k], p ? p + '.' + k : k, out); }
  else if (JSON.stringify(a) !== JSON.stringify(b)) out.push(p + ': ' + JSON.stringify(typeof a === 'number' ? +a.toFixed(4) : a) + ' -> ' + JSON.stringify(typeof b === 'number' ? +b.toFixed(4) : b));
  return out; };
const notes = () => [...document.querySelectorAll('p.note, .note')].filter(vis).map(e => e.textContent.trim()).filter(t => t);
"""
gen.PRE = gen.PRE + MORE


def step(js=None, wait='done', timeout=400, shot=None, clip='#stage', sleep=None):
    return gen.step(js, wait, timeout, shot, clip, sleep)


RESET = "L.resetAll(); L.setCamMode(false); await sleep(80);\n"


def press(btn):
    return "$('%s').scrollIntoView({ block: 'center' }); await sleep(120); $('%s').click(); await sleep(60); return 'pressed %s';" % (btn, btn, btn)


# ---------------------------------------------------------------- words-3: Show Figure 4 and the twins with view limits in the way
REP3 = "await sleep(1300); return JSON.stringify({ cam: [cam.yaw, cam.pitch, cam.dist].map(x => +x.toFixed(4)), target: cam.target.map(x => +x.toFixed(3)), view: VIEW(), iter: S.iter, planes: S.param.mercator.planes, mode: S.mode, flip: S.flip, probes: probes() });"
ST3 = {
    'a-zmax3-iter5': "S.view.zmax = 3; S.iter = 5; L.syncControls(); L.viewChanged(); L.touch();",
    'a1-zmax3': "S.view.zmax = 3; L.syncControls(); L.viewChanged(); L.touch();",
    'a2-iter5': "S.iter = 5; L.syncControls(); L.viewChanged(); L.touch();",
    'b-fly-bound-fov': "L.setCamMode(true); S.view.bound = 1.5; S.view.fov = Math.tan(100 * Math.PI / 360); L.syncControls(); L.viewChanged(); L.touch();",
    'b1-bound': "S.view.bound = 1.5; L.syncControls(); L.viewChanged(); L.touch();",
    'b2-fov100': "S.view.fov = Math.tan(100 * Math.PI / 360); L.syncControls(); L.viewChanged(); L.touch();",
    'b3-fly-away': "L.setCamMode(true); cam.target = [3, 3, 2]; cam.yaw = 2; cam.pitch = -0.4; L.syncControls(); L.viewChanged(); L.touch();",
    'n-zmin8': "S.view.zmin = 8; cam.dist = 9; L.syncControls(); L.viewChanged(); L.touch();",
    'f-fresh': "",
}
rc3 = []
for k, js in ST3.items():
    rc3.append(step(RESET + js + "\nawait sleep(300); return 'state %s ' + JSON.stringify(VIEW()) + ' dist ' + cam.dist.toFixed(3);" % k, wait='done'))
    rc3.append(step(press('fig4Show'), shot='rc3-%s-fig4.png' % k))
    rc3.append(step(REP3, wait=None))
    if k in ('a-zmax3-iter5', 'b-fly-bound-fov', 'a1-zmax3', 'b2-fov100'):
        for btn in ('twinMerc', 'twinLathe', 'twinBulb'):
            rc3.append(step(RESET + js + "\nawait sleep(300); return 'state again';", wait=None))
            rc3.append(step(press(btn), shot='rc3-%s-%s.png' % (k, btn)))
            rc3.append(step(REP3, wait=None))
write('rc3', rc3)

# ---------------------------------------------------------------- words-5: Ultra fast, 40 iterations, the one-plane Basilica
CAM5 = "cam.yaw = -1.9; cam.pitch = 0.55; cam.dist = 4.8; cam.target = [0, 0, 0]; "
REP5 = " L.syncControls(); L.touch(); await sleep(80); return JSON.stringify({ c: S.c, planes: S.param.mercator.planes, iter: S.iter, q: S.q, mode: S.colour.mode });"
rc5 = [
    step("$('mode-j').click(); $('qUltra').click(); S.iter = 40; " + CAM5 + REP5, shot='rc5-ultra40.png'),
    step("S.iter = 14;" + REP5, shot='rc5-ultra14.png'),
    step("S.iter = 80;" + REP5, shot='rc5-ultra80.png'),
    step("S.iter = 40; pickOpt('col-mode', 'Plain clay');" + REP5, shot='rc5-ultra40-clay.png'),
    step("pickOpt('col-mode', 'Orbit trap'); $('qFast').click(); S.iter = 40; " + CAM5 + REP5, shot='rc5-fast40.png'),
    step("$('qBal').click(); S.iter = 40; " + CAM5 + REP5, shot='rc5-bal40.png'),
    step("$('qBal').click(); S.iter = 40; pickOpt('col-mode', 'Plain clay'); " + CAM5 + REP5, shot='rc5-bal40-clay.png'),
]
write('rc5', rc5)

# ---------------------------------------------------------------- words-4: the rabbit, rough against exact
rc4 = [step("$('mode-j').click(); pickOpt('juliaPreset', 'Douady rabbit'); $('juliaFrame').click(); return 'rabbit ' + S.c + ' iter ' + S.iter + ' de ' + S.q.de;")]
for sname, yaw, pitch, dists in (('side', -1.571, 0.12, [9, 4.6, 2.6, 1.6]), ('top', -1.571, 1.1, [4.6]), ('end', 0.25, 0.45, [4.6])):
    for d in dists:
        cam_js = "cam.yaw = %g; cam.pitch = %g; cam.dist = %g; cam.target = [0, 0, 0]; " % (yaw, pitch, d)
        rc4.append(step(cam_js + "pickOpt('qde', 'Rough'); L.touch(); await sleep(60); return 'rough de ' + S.q.de + ' ' + sel('qde');", shot='rc4-%s-%g-rough.png' % (sname, d)))
        rc4.append(step("pickOpt('qde', 'Exact'); L.touch(); await sleep(60); return 'exact de ' + S.q.de;", shot='rc4-%s-%g-exact.png' % (sname, d)))
# the Ultra fast preset from the side as well (what a user would press)
rc4.append(step("$('qUltra').click(); cam.yaw = -1.571; cam.pitch = 0.12; cam.dist = 4.6; cam.target = [0, 0, 0]; L.touch(); await sleep(60); return 'ultra ' + JSON.stringify(S.q);", shot='rc4-side-4.6-ultra.png'))
rc4.append(step("$('qBal').click(); cam.yaw = -1.571; cam.pitch = 0.12; cam.dist = 4.6; cam.target = [0, 0, 0]; L.touch(); await sleep(60); return 'balanced ' + JSON.stringify(S.q);", shot='rc4-side-4.6-bal.png'))
write('rc4', rc4)

# ---------------------------------------------------------------- words-1: one plane, slices in numbers and pictures
COMP = r"""
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
    ('mandel', "", (-0.5, 0, 3.2), False),
    ('basilica', "$('mode-j').click(); pickOpt('juliaPreset', 'Basilica');", (0, 0, 3.8), True),
    ('rabbit', "$('mode-j').click(); pickOpt('juliaPreset', 'Douady rabbit');", (0, 0, 3.8), False),
]
rc1 = []
for name, setx, (cx, cy, side), pics in SOLIDS:
    rc1.append(step(RESET + setx + "\nreturn 'solid %s, planes ' + S.param.mercator.planes + ', iter ' + S.iter + ', c ' + S.c;" % name, shot=('rc1-%s-3d.png' % name) if pics else None))
    rc1.append(step(COMP + r"""
const t = await top(%g, %g, %g); const hs = [0.12, 0.3, 0.5, 0.7, 0.9].map(f => +(f * t).toFixed(3)); window.__h = hs;
const out = [await comp(0, %g, %g, %g, 400)]; for (const z of hs) out.push(await comp(z, %g, %g, %g, 400));
return JSON.stringify({ solid: '%s', top: +t.toFixed(2), heights: hs, slices: out });
""" % (cx, cy, side, cx, cy, side, cx, cy, side, name), wait=None))
    if pics:
        for k in range(5):
            rc1.append(step("$('flat').checked || $('flat').click(); S.cut = window.__h[%d]; L.syncControls(); L.touch(); await sleep(60); return 'flat z ' + S.cut;" % k, shot='rc1-%s-2d-%d.png' % (name, k)))
        rc1.append(step("$('flat').checked && $('flat').click(); cam.pitch = 0.95; L.syncControls(); L.touch(); return 'to 3d';", wait=None))
        for k in (1, 2):
            rc1.append(step("S.cutOn = true; S.cut = window.__h[%d]; L.syncControls(); L.touch(); await sleep(60); return 'cut z ' + S.cut + ' ' + $('cutOn').checked;" % k, shot='rc1-%s-cut-%d.png' % (name, k)))
write('rc1', rc1)

# ---------------------------------------------------------------- claims A: Figure 4 and the twins from a changed state: what is switched off, what stays
DIRTY = ("$('mode-j').click(); pickOpt('juliaPreset', 'Douady rabbit'); $('ap-lathe').click(); S.n = 3; S.param.lathe.spin = 3; S.abs = [1, 0, 0]; S.flip = [1, 1]; "
         "pickOpt('col-trap', 'Cross'); pickOpt('col-solid', 'Is the solid'); S.cutOn = true; S.cut = 0.2; S.iter = 20; $('qFast').click(); pickOpt('col-pal', 'Fire'); "
         "S.colour.rev = false; S.colour.glow = 2; S.colour.reach = 6; S.param.mercator.turn = 30; S.param.mercator.lift = 0.4; S.param.bulb.lat = 20; $('flat').click(); L.syncControls(); L.refresh(false); await sleep(200);")
DIRTYM = ("$('ap-classic').click(); S.n = 8; S.param.classic.theta = 40; $('m-mosaic').click(); pickOpt('col-trap', 'Ring'); pickOpt('col-solid', 'Is added'); S.iter = 20; $('qFast').click(); "
          "pickOpt('col-pal', 'Ocean'); S.param.mercator.turn = 30; S.param.mercator.lift = 0.4; S.param.bulb.lat = 20; S.param.lathe.spin = 3; S.cutOn = true; S.cut = 0.1; L.syncControls(); L.refresh(false); await sleep(200);")
cA = []
for tag, dirty in (('j', DIRTY), ('m', DIRTYM)):
    for btn, back in (('fig4Show', 'fig4Back'), ('twinMerc', 'twinOff'), ('twinLathe', None), ('twinBulb', None)):
        cA.append(step(RESET + dirty + "\nwindow.__b = full(); return 'dirty %s';" % tag))
        cA.append(step(press(btn), shot='cA-%s-%s.png' % (tag, btn)))
        cA.append(step("await sleep(900); const a = full(); const d = diff(window.__b, a); window.__b = a; return '%s from %s: ' + d.join(' ; ');" % (btn, tag), wait=None))
        if back:
            cA.append(step(press(back), shot='cA-%s-%s.png' % (tag, back)))
            cA.append(step("await sleep(900); const a = full(); const d = diff(window.__b, a); return '%s: ' + d.join(' ; ');" % back, wait=None))
write('cA', cA)

# ---------------------------------------------------------------- claims B: flip z on a Julia set whose c lies in the plane z = 0: pixel for pixel?
CFG = [
    ('si-basilica', "$('mode-j').click();"),
    ('si-rabbit', "$('mode-j').click(); pickOpt('juliaPreset', 'Douady rabbit');"),
    ('lathe-rabbit', "$('mode-j').click(); pickOpt('juliaPreset', 'Douady rabbit'); $('ap-lathe').click();"),
    ('si-rabbit-lift', "$('mode-j').click(); pickOpt('juliaPreset', 'Douady rabbit'); S.param.mercator.lift = 0.3; L.syncControls(); L.refresh(false);"),
    ('si-rabbit-turn', "$('mode-j').click(); pickOpt('juliaPreset', 'Douady rabbit'); S.param.mercator.turn = 40; L.syncControls(); L.refresh(false);"),
    ('si-rabbit-planes2', "$('mode-j').click(); pickOpt('juliaPreset', 'Douady rabbit'); S.param.mercator.planes = 2; L.syncControls(); L.refresh(false);"),
    ('lathe-rabbit-spin3', "$('mode-j').click(); pickOpt('juliaPreset', 'Douady rabbit'); $('ap-lathe').click(); S.param.lathe.spin = 3; L.syncControls(); L.refresh(false);"),
    ('bulb-rabbit', "$('mode-j').click(); pickOpt('juliaPreset', 'Douady rabbit'); $('ap-bulb').click();"),
]
cB = []
for name, js in CFG:
    cB.append(step(RESET + js + "\nawait sleep(100); return '%s flip ' + S.flip + ' par ' + JSON.stringify(S.param[L.APPROACHES[S.approach].id]) + ' c ' + S.c;" % name, shot='cB-%s-off.png' % name))
    cB.append(step("$('flipz').click(); await sleep(100); return 'flip ' + S.flip;", shot='cB-%s-on.png' % name))
    if name == 'si-basilica':
        cB.append(step("$('flipz').click(); await sleep(100); return 'flip ' + S.flip;", shot='cB-%s-off2.png' % name))
write('cB', cB)

# ---------------------------------------------------------------- claims C: what the twin buttons show, slices of the Sphere inversions twin, the Lathe
cC = [
    step(RESET + press('twinMerc'), shot='cC-twinM-3d.png'),
]
for z in (0, 0.3, 0.6, 1.0, 1.4):
    cC.append(step("$('flat').checked || $('flat').click(); S.cut = %g; L.syncControls(); L.touch(); await sleep(60); return 'twin 2d z ' + S.cut + ' flip ' + S.flip + ' h ' + S.v2.h;" % z, shot='cC-twinM-2d-%g.png' % z))
cC.append(step(press('twinOff'), wait=None))
for z in (0, 0.1, 0.2, 0.3):
    cC.append(step("$('flat').checked || $('flat').click(); S.cut = %g; L.syncControls(); L.touch(); await sleep(60); return 'plain 2d z ' + S.cut + ' flip ' + S.flip;" % z, shot='cC-plainM-2d-%g.png' % z))
cC += [
    step(RESET + press('twinLathe'), shot='cC-twinL-3d.png'),
    step("cam.yaw = -1.571; cam.pitch = 0.02; L.touch(); return 'lathe twin from the side, yaw ' + cam.yaw;", shot='cC-twinL-side.png'),
    step("cam.pitch = 1.5; L.touch(); return 'lathe twin from above';", shot='cC-twinL-top.png'),
    step("$('flat').click(); S.cut = 0; L.syncControls(); L.touch(); return 'lathe twin 2d z 0';", shot='cC-twinL-2d-0.png'),
    step(RESET + press('twinBulb'), shot='cC-twinB-3d.png'),
    step(RESET + "$('mode-j').click(); $('ap-lathe').click(); await sleep(60); return 'lathe julia c ' + S.c + ' spin ' + S.param.lathe.spin;", shot='cC-lathe-basilica.png'),
    step("cam.pitch = 0.15; L.touch(); return 'lathe basilica from the side';", shot='cC-lathe-basilica-side.png'),
    step("$('ap-mercator').click(); await sleep(60); return 'si julia same view';", shot='cC-si-basilica-side.png'),
    step(RESET + "$('ap-lathe').click(); await sleep(60); return 'lathe mandelbrot';", shot='cC-lathe-mandel.png'),
]
write('cC', cC)

# ---------------------------------------------------------------- claims D: a trap that is the solid
SK = "S.colour.skip = %d; L.syncControls(); L.refresh(false); await sleep(80); return 'skip ' + S.colour.skip + ' thick ' + S.colour.thick + ' notes ' + JSON.stringify(notes().filter(t => /solid|trap|cut open/i.test(t)).map(t => t.slice(0, 60)));"
cD = [step(RESET + "const r = { ex3d: vis($('trapExamples')), solidSel: vis($('col-solid')) }; pickOpt('col-solid', 'Is the solid'); await sleep(80); r.exSolid = vis($('trapExamples')); r.skip = S.colour.skip; r.thick = S.colour.thick; r.order = [...document.querySelectorAll('#col-solid, #trapExamples, #col-thick, #col-skip')].map(e => e.id); r.nEx = $('trapExamples').options.length; return JSON.stringify(r);", shot='cD-m-skip1.png')]
for k in (0, 2, 3):
    cD.append(step(SK % k, shot='cD-m-skip%d.png' % k))
cD.append(step(SK % 1, wait='done'))
for q in ('qUltra', 'qFast', 'qFine'):
    cD.append(step("$('%s').click(); await sleep(80); return '%s ' + JSON.stringify(S.q);" % (q, q), shot='cD-m-skip1-%s.png' % q))
cD.append(step("$('qBal').click(); $('mode-j').click(); await sleep(80); return 'julia solid ' + S.colour.solid + ' skip ' + S.colour.skip;", shot='cD-j-skip1.png'))
cD.append(step(SK % 0, shot='cD-j-skip0.png'))
cD.append(step(SK % 2, shot='cD-j-skip2.png'))
cD.append(step("S.colour.skip = 1; L.syncControls(); $('mode-k').click(); await sleep(80); return 'klein solid ' + S.colour.solid + ' k ' + JSON.stringify(S.k) + ' notes ' + JSON.stringify(notes());", shot='cD-k-skip1.png'))
cD.append(step(SK % 0, shot='cD-k-skip0.png'))
cD.append(step(SK % 2, shot='cD-k-skip2.png'))
cD.append(step("S.colour.skip = 1; S.k.mx = 0.15; L.syncControls(); L.refresh(false); await sleep(200); return 'klein leaning mx ' + S.k.mx + ' notes ' + JSON.stringify(notes());", shot='cD-k-lean.png'))
cD.append(step("S.k.mx = 0; S.colour.tx = 0.3; L.syncControls(); L.refresh(false); await sleep(200); return 'klein trap off centre notes ' + JSON.stringify(notes().filter(t => /cut open/.test(t)));", wait=None))
cD.append(step("S.colour.tx = 0; pickOpt('col-solid', 'Colours the surface'); await sleep(200); return 'klein, trap colours the surface, lean notes ' + JSON.stringify(notes().filter(t => /cut open/.test(t))) + ' examples shown ' + vis($('trapExamples'));", wait=None))
write('cD', cD)

# ---------------------------------------------------------------- claims E: the 2D view's own controls, the cut face
VIS2 = "({ edge: vis($('col-edge')), edgeGlow: vis($('col-edgeGlow')), inMode: vis($('col-inMode')), inPal: vis($('col-inPal')), cutFace: (() => { try { return vis(byLabel('Colour the cut face')); } catch (e) { return 'absent'; } })(), reach: vis($('col-reach')), solid: vis($('col-solid')) })"
cE = [
    step(RESET + "const r = { in3d: %s }; $('flat').click(); await sleep(150); r.in2d = %s; r.inModeAt = sel('col-inMode'); return JSON.stringify(r);" % (VIS2, VIS2), shot='cE-m-2d-plain.png'),
    step("pickOpt('col-inMode', 'Orbit trap'); await sleep(100); return 'inside orbit trap, inPal ' + sel('col-inPal') + ' shown ' + vis($('col-inPal'));", shot='cE-m-2d-trap.png'),
    step("pickOpt('col-inMode', 'Where the orbit ends up'); await sleep(100); return 'ends up';", shot='cE-m-2d-ends.png'),
    step("pickOpt('col-inMode', 'How deep inside'); await sleep(100); return 'deep';", shot='cE-m-2d-deep.png'),
    step("pickOpt('col-inMode', 'How quickly'); await sleep(100); return 'settles';", shot='cE-m-2d-settles.png'),
    step("pickOpt('col-inPal', 'Fire'); await sleep(100); return 'settles, palette for the inside Fire';", shot='cE-m-2d-settles-fire.png'),
    step("pickOpt('col-inPal', 'Same as outside'); $('mode-k').click(); pickOpt('col-inMode', 'How deep inside'); await sleep(100); return 'klein 2d deep ' + S.flat + ' ' + S.mode;", shot='cE-k-2d-deep.png'),
    step("pickOpt('col-inMode', 'How quickly'); await sleep(100); return 'klein 2d settles';", shot='cE-k-2d-settles.png'),
    step("pickOpt('col-inMode', 'Where the orbit ends up'); await sleep(100); return 'klein 2d ends up';", shot='cE-k-2d-ends.png'),
    step(RESET + "pickOpt('col-inMode', 'How deep inside'); S.cutOn = true; S.cut = 0; cam.pitch = 0.9; L.syncControls(); L.refresh(false); await sleep(150); return JSON.stringify({ cutOn: S.cutOn, vis: %s, cutFace: S.colour.cutFace });" % VIS2, shot='cE-m-cut-off.png'),
    step("byLabel('Colour the cut face').click(); await sleep(150); return JSON.stringify({ cutFace: S.colour.cutFace, vis: %s });" % VIS2, shot='cE-m-cut-on.png'),
    step("pickOpt('col-inMode', 'Orbit trap'); await sleep(150); return 'cut face, inside by orbit trap';", shot='cE-m-cut-on-trap.png'),
]
write('cE', cE)

# ---------------------------------------------------------------- claims F: "A Glow width of 2 or 3 brings more colour, and so does a Trap radius of 0.7"; the new dial
SETC = "Object.assign(S.colour, %s); L.syncControls(); L.touch(); await sleep(80); return JSON.stringify({ glow: S.colour.glow, radius: S.colour.radius, reach: S.colour.reach, reachDial: $('col-reach').value, reachNum: $('col-reachNum') ? $('col-reachNum').value : null, reachRange: [$('col-reach').min, $('col-reach').max] });"
cF = [
    step(RESET + SETC % "{}", shot='cF-open.png'),
    step(SETC % "{ glow: 2 }", shot='cF-glow2.png'),
    step(SETC % "{ glow: 3 }", shot='cF-glow3.png'),
    step(SETC % "{ glow: 1, radius: 0.7 }", shot='cF-radius07.png'),
    step(SETC % "{ glow: 1, radius: 1, reach: 2 }", shot='cF-reach2.png'),
    step(SETC % "{ reach: 8 }", shot='cF-reach8.png'),
    step(SETC % "{ reach: 12 }", shot='cF-reach12.png'),
    step(SETC % "{ reach: 4 }" + " ", wait='done'),
    step("$('mode-j').click(); await sleep(80); return 'julia open';", shot='cF-j-open.png'),
    step(SETC % "{ glow: 3 }", shot='cF-j-glow3.png'),
    step(SETC % "{ glow: 1 }" + " ", wait='done'),
    step("$('mode-k').click(); await sleep(80); return 'klein open';", shot='cF-k-open.png'),
    step(SETC % "{ glow: 3 }", shot='cF-k-glow3.png'),
]
write('cF', cF)

# ---------------------------------------------------------------- claims G: Extreme ranges
cG = [
    step(RESET + r"""
const dials = () => [...document.querySelectorAll('input[type=range]')].map(e => { const l = document.querySelector('label[for="' + e.id + '"]'); const n = $(e.id + 'Num'); return { id: e.id, min: +e.min, max: +e.max, v: +e.value, title: n ? n.title : '', label: l ? l.textContent.replace(/\s+/g, ' ').trim() : '' }; });
const a = dials(); const box = byLabel('Extreme ranges'); const top0 = Math.round(box.getBoundingClientRect().top), firstDetails = Math.round(document.querySelector('details').getBoundingClientRect().top);
box.click(); await sleep(400);
const b = dials(); const rows = [];
for (const d of a) { const e = b.find(x => x.id === d.id); if (!e) continue; rows.push({ id: d.id, label: d.label, min: d.min, max: d.max, xmin: e.min, xmax: e.max, title0: d.title, title1: e.title, ratio: +((e.max - e.min) / (d.max - d.min)).toFixed(2) }); }
const wide = [...document.querySelectorAll('.wide, [class*=wide]')].map(e => e.className + ':' + e.textContent.trim().slice(0, 20) + ':' + (e.getBoundingClientRect().width > 0));
const wideWord = [...document.querySelectorAll('label, span, small, em, b')].filter(e => e.children.length === 0 && /^\s*wide\s*$/i.test(e.textContent)).length;
window.__rows = rows;
return JSON.stringify({ extreme: L.isExtreme(), boxTop: top0, firstSectionTop: firstDetails, note: $('extremeNote').textContent, n: rows.length, widened: rows.filter(r => r.ratio > 1.01).length, wideWord, wideSample: wide.slice(0, 6), rows });
""", wait='done'),
    step(r"""
// values beyond the usual range, typed; then the switch off
const set = { iterNum: 300, kiterNum: 900, qstepsNum: 3000, qaaNum: 200, powNum: 40 }; const got = {};
for (const k in set) { if ($(k)) { type(k, set[k]); await sleep(60); got[k] = $(k).value; } else got[k] = 'no box'; }
const before = { iter: S.iter, kiter: S.k.iter, steps: S.q.steps, aa: S.q.aa, n: S.n };
byLabel('Extreme ranges').click(); await sleep(400);
const after = { iter: S.iter, kiter: S.k.iter, steps: S.q.steps, aa: S.q.aa, n: S.n };
const wideWord = [...document.querySelectorAll('label, span, small, em, b')].filter(e => e.children.length === 0 && /^\s*wide\s*$/i.test(e.textContent) && e.getBoundingClientRect().width > 0).length;
return JSON.stringify({ typed: got, before, after, extreme: L.isExtreme(), wideWordShownAfterOff: wideWord, note: $('extremeNote').textContent });
""", wait='done', timeout=600),
]
write('cG', cG)

# ---------------------------------------------------------------- claims H: what a list entry changes; Frame it; As it was found; counts; saved points
cH = [
    step(RESET + r"""
$('mode-j').click(); $('ap-lathe').click(); S.iter = 31; $('qFast').click(); cam.yaw = 1.1; cam.pitch = 0.3; cam.dist = 3.3; cam.target = [0.1, 0.2, 0]; S.k.iter = 77; L.syncControls(); L.refresh(false); await sleep(200);
const b0 = full(); pickOpt('juliaPreset', 'Douady rabbit'); await sleep(300); const b1 = full(); const out = { pick: diff(b0, b1), foundShown: !$('juliaFound').hidden, note: $('juliaNote').textContent };
$('juliaFrame').click(); await sleep(300); const b2 = full(); out.frame = diff(b1, b2);
out.foundShown2 = !$('juliaFound').hidden; try { out.foundDiff = JSON.stringify(L.juliaFoundDiff(L.JULIA_PRESETS.find(p => p.name === 'Douady rabbit'))); } catch (e) { out.foundDiff = 'err ' + e.message; }
$('ap-mercator').click(); await sleep(300); out.foundShownSI = !$('juliaFound').hidden; const b3 = full();
if (!$('juliaFound').hidden) { $('juliaFound').click(); await sleep(300); } const b4 = full(); out.found = diff(b3, b4); out.foundShownAfter = !$('juliaFound').hidden;
// groups and counts
out.groups = [...$('juliaPreset').querySelectorAll('optgroup')].map(g => g.label + ': ' + g.children.length); out.loose = [...$('juliaPreset').children].filter(e => e.tagName === 'OPTION').map(o => o.text);
out.twoPlanes = [...$('juliaPreset').querySelectorAll('optgroup')].filter(g => /two planes/.test(g.label)).map(g => [...g.children].map(o => o.text))[0];
out.planes2InData = L.JULIA_PRESETS.filter(p => (p.planes || (p.found && p.found.planes)) === 2).map(p => p.name);
out.sample = JSON.stringify(L.JULIA_PRESETS[0]).slice(0, 300);
return JSON.stringify(out);
""", wait='done'),
    step(r"""
// a saved point goes to the top of the list
S.c = [0.123, 0.456, 0.05]; L.syncControls(); L.refresh(false); await sleep(200); $('juliaName').value = 'My test point'; $('juliaName').dispatchEvent(new Event('input', { bubbles: true })); $('juliaSave').click(); await sleep(300);
const kids = [...$('juliaPreset').children].map(e => e.tagName === 'OPTGROUP' ? '[' + e.label + ': ' + e.children.length + ']' : e.text);
const r = { order: kids, saved: L.juliaSaved().length, selected: sel('juliaPreset'), deleteShown: !$('juliaDelete').hidden, saveNote: $('juliaSaveNote').textContent };
if (!$('juliaDelete').hidden) { $('juliaDelete').click(); await sleep(300); r.afterDelete = L.juliaSaved().length; r.orderAfter = [...$('juliaPreset').children].map(e => e.tagName === 'OPTGROUP' ? '[' + e.label + ']' : e.text); }
return JSON.stringify(r);
""", wait='done'),
    step(RESET + r"""
$('mode-k').click(); await sleep(200); S.iter = 31; $('qFast').click(); cam.yaw = 1.1; cam.pitch = 0.3; cam.dist = 3.3; cam.target = [0.1, 0.2, 0]; S.k.iter = 77; L.syncControls(); L.refresh(false); await sleep(200);
const g = [...$('kleinPreset').querySelectorAll('optgroup')]; const out = { groups: g.map(x => x.label + ': ' + x.children.length), total: $('kleinPreset').querySelectorAll('option').length };
const sph = g.find(x => /Turning-out/.test(x.label)); const first = sph.children[0];
const b0 = full(); $('kleinPreset').value = first.value; $('kleinPreset').dispatchEvent(new Event('change', { bubbles: true })); await sleep(300); const b1 = full(); out.pickName = first.text; out.pick = diff(b0, b1);
$('kleinFrame').click(); await sleep(300); const b2 = full(); out.frame = diff(b1, b2);
// do the 15 keep a group that is already in the list and move only the sphere?
const P = L.KLEIN_PRESETS; out.n = P.length; out.keys = Object.keys(P[0]); out.sample = JSON.stringify(P[0]).slice(0, 400); out.sample20 = JSON.stringify(P[P.length - 1]).slice(0, 400);
return JSON.stringify(out);
""", wait='done'),
]
write('cH', cH)

# ---------------------------------------------------------------- claims I: "Preparing the formula" and "going back is quick"
OBS = r"""
if (!window.__busyLog) { window.__busyLog = []; if (!$('busy')) { L.setBusy('t9', 'x'); L.setBusy('t9', null); } const el = $('busy'); const rec = () => window.__busyLog.push([Math.round(performance.now()), el.hidden ? '' : el.querySelector('.busy-text').textContent]); new MutationObserver(rec).observe(el, { attributes: true, childList: true, subtree: true, characterData: true }); }
const mark = () => { window.__busyLog.length = 0; window.__t0 = Math.round(performance.now()); };
const seen = () => { const out = []; let last = null; for (const [t, s] of window.__busyLog) { if (s !== last) { out.push((t - window.__t0) + 'ms:' + (s || '(hidden)')); last = s; } } return out.join(' | ') + ' || idle after ' + (Math.round(performance.now()) - window.__t0) + 'ms'; };
"""


def timed(name, js):
    return [step(OBS + "mark(); " + js + " return 'did %s';" % name, wait='done'), step(OBS + "return '%s: ' + seen();" % name, wait=None)]


cI = [step("return 'busy element ' + !!$('busy') + ' hidden ' + ($('busy') && $('busy').hidden);", wait='done')]
for name, js in [
    ('to Lathe (first time)', "$('ap-lathe').click();"),
    ('back to Sphere inversions', "$('ap-mercator').click();"),
    ('to Lathe again', "$('ap-lathe').click();"),
    ('back to Sphere inversions again', "$('ap-mercator').click();"),
    ('power 3 (first time)', "S.n = 3; L.syncControls(); L.refresh(false);"),
    ('power 2 again', "S.n = 2; L.syncControls(); L.refresh(false);"),
    ('power 3 again', "S.n = 3; L.syncControls(); L.refresh(false);"),
    ('power 2 once more', "S.n = 2; L.syncControls(); L.refresh(false);"),
    ('another equation (first time)', "$('eq').value = 'z^n + c + 0.1'; $('eq').dispatchEvent(new Event('change', { bubbles: true }));"),
    ('equation back', "$('eq').value = 'z^n + c'; $('eq').dispatchEvent(new Event('change', { bubbles: true }));"),
    ('Kleinian (first time)', "$('mode-k').click();"),
    ('Mandelbrot again', "$('mode-m').click();"),
    ('Kleinian again', "$('mode-k').click();"),
    ('Mandelbrot once more', "$('mode-m').click();"),
    ('trap is the solid (first time)', "pickOpt('col-solid', 'Is the solid');"),
    ('trap colours the surface', "pickOpt('col-solid', 'Colours the surface');"),
    ('trap is the solid again', "pickOpt('col-solid', 'Is the solid');"),
    ('trap colours the surface again', "pickOpt('col-solid', 'Colours the surface');"),
    ('2D view', "$('flat').click();"),
    ('inside colours (first time)', "pickOpt('col-inMode', 'How deep inside');"),
    ('inside plain', "pickOpt('col-inMode', 'Plain');"),
    ('inside colours again', "pickOpt('col-inMode', 'How deep inside');"),
]:
    cI += timed(name, js)
write('cI', cI)

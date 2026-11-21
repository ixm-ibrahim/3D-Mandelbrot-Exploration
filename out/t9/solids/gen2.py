"""More step files of the tester "solids" in the second check: N12 (trap colours), the Examples list, the dial
"Orbit steps the trap reads". Run from the project root: python out/t9/solids/gen2.py
then, one at a time: PYTHONIOENCODING=utf-8 python tools/shot.py --url dist/v8.html --actions out/t9/solids/<name>.json"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen import step, write, J, C1, C2, C3, N

# ---- runs n-<scene>: N12, the colour an orbit trap gives a surface, across presets, threshold, iterations and zoom
RAB = "$('mode-j').click(); await sleep(200); L.applyJuliaPreset(L.JULIA_PRESETS.find(p => /rabbit/i.test(p.name))); L.syncControls(); await sleep(200); "
SCENES = [
 ('r', RAB + "L.cam.dist = L.cam.dist * 0.45; L.touch(); L.viewChanged();"),          # the user's own scene: the rabbit close up
 ('m', ""),                                                                             # the opening Mandelbrot view
 ('b', J(C1)),                                                                          # Julia c = -1
 ('x', "$('ap-bulb').click(); await sleep(300);"),                                      # another approach: the Mandelbulb, Mandelbrot mode
]
SETUPS = [('shell1', "sel('col-trap', 5); type('col-radiusNum', '1');"), ('shell07', "sel('col-trap', 5); type('col-radiusNum', '0.7');"),
          ('cross', "sel('col-trap', 1);"), ('planes', "sel('col-trap', 4);")]
# the zoom a user makes: aim at the surface point in the middle of the picture (what a double-click does), then go closer
ZB = ("if (!window.__z) { const w = $('stage').clientWidth, h = $('stage').clientHeight; let hit = null, at = null; "
      "for (const [dx, dy] of [[0,0],[0.06,0],[-0.06,0],[0,0.06],[0,-0.06],[0.12,0.05],[-0.12,-0.05],[0.2,0.1],[-0.2,-0.1],[0.1,-0.2],[-0.1,0.2]]) { hit = L.pick(w * (0.5 + dx), h * (0.5 + dy)); if (hit) { at = [dx, dy]; break; } } "
      "if (!hit) fail('no surface near the middle'); const b = L.basis(), D0 = Math.hypot(b.pos[0] - hit[0], b.pos[1] - hit[1], b.pos[2] - hit[2]); "
      "window.__z = { hit: [hit[0], hit[1], hit[2]], D0, at, cam0: { target: L.cam.target.slice(), dist: L.cam.dist } }; } "
      "const Z = window.__z; const zoom = f => { L.cam.target = Z.hit.slice(); L.cam.dist = Z.D0 / f; L.touch(); L.viewChanged(); }; ")
ZR = "'zoom ' + JSON.stringify(window.__z) + ' ' + st()"
for sn, sj in SCENES:
    s = []
    for i, (un, uj) in enumerate(SETUPS):
        first = (sj if i == 0 else '') + uj
        p = 'n-%s-%s-' % (sn, un)
        s += [
         step(first + "$('qUltra').click();", p + 'U.png'),
         step("$('qFast').click();", p + 'F.png'),
         step("$('qBal').click();", p + 'B.png'),
         step("$('qFine').click();", p + 'N.png'),
         step("$('qBal').click(); type('qdetailNum', '0.2');", p + 'd02.png'),
         step("type('qdetailNum', '3');", p + 'd3.png'),
         step("type('qdetailNum', '1'); type('iterNum', '24');", p + 'i24.png'),
         step("type('iterNum', '60');", p + 'i60.png'),
         step("type('iterNum', '120');", p + 'i120.png'),
         step("type('iterNum', '14'); " + ZB + "zoom(1);", p + 'zb.png', ret=ZR),
         step(ZB + "zoom(2);", p + 'z2.png', ret=ZR),
         step(ZB + "zoom(8);", p + 'z8.png', ret=ZR),
         step(ZB + "L.cam.target = Z.cam0.target.slice(); L.cam.dist = Z.cam0.dist; L.touch(); L.viewChanged();"),
        ]
    write('n-' + sn, s)

# ---- run ex: the nine entries of the Examples list
EXR = ("JSON.stringify({ at: L.exampleAt(), shown: $('trapExamples').selectedOptions[0] && $('trapExamples').selectedOptions[0].textContent, mode: S.mode, c: S.c, "
       "kfit: L.kleinPresetAt ? L.kleinPresetAt() : null, trap: C.trap, solid: C.solid, thick: C.thick, skip: C.skip, radius: C.radius, t: [C.tx, C.ty, C.tz], "
       "cam: { yaw: L.cam.yaw, pitch: L.cam.pitch, dist: +L.cam.dist.toFixed(3), target: L.cam.target }, iter: S.iter, kiter: S.k.iter, bound: S.view.bound, zmin: S.view.zmin, zmax: S.view.zmax, "
       "approach: S.approach, n: S.n, eq: S.eq, pal: C.pal, by: C.by, julia: $('juliaList') ? ($('juliaList').selectedOptions[0] || {}).textContent : null, notes: notes() })")
ex = [step("", None, ret="JSON.stringify(L.EXAMPLES)")]
for i in range(1, 10):
    ex.append(step("sel('trapExamples', %d);" % i, 'ex-%d.png' % i, ret=EXR))
# the same nine after the user has moved everything the hint says an example sets (and the camera's aim)
MESS = ("$('mode-j').click(); await sleep(150); type('cxNum', '0.25'); type('cyNum', '0.4'); type('czNum', '0.1'); sel('col-trap', 2); sel('col-solid', 2); "
        "type('col-thickNum', '0.3'); type('col-skipNum', '5'); sel('col-trap', 6); type('col-radiusNum', '0.4'); sel('col-solid', 0); "
        "L.cam.target = [0.4, 0.3, 0.2]; L.cam.yaw += 1.3; L.cam.pitch = -0.4; L.cam.dist = 9; L.touch(); L.viewChanged(); await sleep(150); ")
MESSK = "$('mode-k').click(); await sleep(150); L.applyKleinPreset(L.KLEIN_PRESETS[7]); L.syncControls(); await sleep(150); "
for i in range(1, 10):
    ex.append(step((MESSK if i >= 7 else '') + MESS + "sel('trapExamples', %d);" % i, 'ex2-%d.png' % i, ret=EXR))
# the trap centre is not among the things an example sets: what does the list give after the centre was moved?
ex.append(step("type('col-txNum', '0.5'); type('col-tyNum', '0.3'); sel('trapExamples', 4);", 'ex3-4-centre.png', ret=EXR))
ex.append(step("sel('trapExamples', 1);", 'ex3-1-centre.png', ret=EXR))
ex.append(step("sel('trapExamples', 8);", 'ex3-8-centre.png', ret=EXR))
write('ex', ex)

# ---- run reach: the dial "Orbit steps the trap reads"
rc = []
for sn, sj in (('m', "$('mode-m').click(); await sleep(200); sel('col-trap', 5); type('col-radiusNum', '1');"), ('b', J(C1) + "type('col-radiusNum', '0.7');")):
    for k, v in enumerate((1, 2, 3, 4, 6, 9, 16)):
        rc.append(step((sj if k == 0 else '') + "type('col-reachNum', '%d');" % v, 'rc-%s-%d.png' % (sn, v)))
    # zoomed in 8 times: do the finer steps come in?
    rc.append(step("window.__z = null; type('col-reachNum', '4'); " + ZB + "zoom(8);", 'rc-%s-z8-4.png' % sn, ret=ZR))
    for v in (6, 9, 16):
        rc.append(step("type('col-reachNum', '%d');" % v, 'rc-%s-z8-%d.png' % (sn, v)))
    rc.append(step("type('col-reachNum', '2');", 'rc-%s-z8-2.png' % sn))
    rc.append(step(ZB + "L.cam.target = Z.cam0.target.slice(); L.cam.dist = Z.cam0.dist; type('col-reachNum', '4'); L.touch(); L.viewChanged();"))
# where the dial is on show, and what its box takes
SHOWN = "(() => { const e = $('col-reachNum'); const d = e && e.closest('.dial'); return !!(d && !d.hidden && d.getBoundingClientRect().width > 0); })()"
rc.append(step("$('mode-m').click(); await sleep(200); type('col-reachNum', '2.6'); await sleep(100); window.__r = ['typed 2.6 -> ' + C.reach]; type('col-reachNum', '0'); await sleep(100); window.__r.push('typed 0 -> ' + C.reach + ' box ' + $('col-reachNum').value); "
               "type('col-reachNum', '250'); await sleep(100); window.__r.push('typed 250 -> ' + C.reach + ' box ' + $('col-reachNum').value); type('col-reachNum', 'abc'); await sleep(100); window.__r.push('typed abc -> ' + C.reach + ' box ' + $('col-reachNum').value); "
               "type('col-reachNum', '4'); window.__r.push('3D trap: shown ' + " + SHOWN + "); sel('col-solid', 1); await sleep(150); window.__r.push('trap is the solid: shown ' + " + SHOWN + "); sel('col-solid', 2); await sleep(150); window.__r.push('trap added: shown ' + " + SHOWN + "); sel('col-solid', 0); "
               "sel('col-mode', 2); await sleep(150); window.__r.push('escape count: shown ' + " + SHOWN + "); sel('col-mode', 0); await sleep(150); $('flat').click(); await sleep(200); window.__r.push('2D view: shown ' + " + SHOWN + "); $('flat').click(); await sleep(200); "
               "$('mode-k').click(); await sleep(300); window.__r.push('Kleinian: shown ' + " + SHOWN + "); $('mode-m').click(); await sleep(200); window.__r.push('help: ' + ($('col-reachNum').closest('.dial').querySelector('.dial-help, .note') || {}).textContent);",
               None, ret="window.__r.join(' | ')"))
write('reach', rc)

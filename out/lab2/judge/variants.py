"""Judge's own step lists: (1) the picture kinds the pillow2 engineer did not draw, (2) dial settings of softfold
and axisbulb chosen by the judge. Writes out/lab2/judge/<job>/plan.json for tools/shot.py.
   python out/lab2/judge/variants.py"""
import json, os
PRE = "const L = window.squaringLab, S = L.S, cam = L.cam, $ = id => document.getElementById(id); "
def END(tag): return " L.syncControls(); L.touch(); return JSON.stringify({ shot: '%s', approach: L.APPROACHES[S.approach].id, param: S.param[L.APPROACHES[S.approach].id], mode: S.mode, n: S.n, c: S.c, flat: S.flat, cutOn: S.cutOn, cut: S.cut, colour: S.colour.mode, de: S.q.de, steps: S.q.steps, aa: S.q.aa });" % tag
TOP = "cam.yaw = -Math.PI / 2; cam.pitch = 1.5699;"
root = 'out/lab2/judge'

# ---- (1) pillow extras: the seven standard kinds missing from out/lab2/pillow2
EXTRA = [
    ('m3d-y', "S.flat = false; S.cutOn = false; S.cut = 0; $('mode-m').click(); S.n = 2; L.refresh(false); L.resetCam(); cam.yaw = -Math.PI / 2; cam.pitch = 0;"),
    ('m3d-cut0', "L.resetCam(); cam.pitch = 50 * Math.PI / 180; S.cutOn = true; S.cut = 0;"),
    ('m3d-cut02', "S.cut = 0.2;"),
    ('m2d-z050', "L.resetCam(); S.cutOn = false; S.flat = true; S.cut = 0.5; S.v2.x = -0.6; S.v2.y = 0; S.v2.h = 3.2;"),
    ('j-off-3d', "S.flat = false; S.cut = 0; $('mode-j').click(); S.c[0] = -1.0; S.c[1] = 0.045; S.c[2] = 0.026; L.refresh(false); L.resetCam();"),
    ('m3d-n3', "S.c[0] = -1; S.c[1] = 0; S.c[2] = 0; $('mode-m').click(); S.n = 3; L.refresh(false); L.resetCam();"),
    ('m3d-n8', "S.n = 8; L.refresh(false); L.resetCam();"),
]
for apid in ('pillowsmooth', 'pillowboth'):
    out = '%s/extra-%s' % (root, apid)
    os.makedirs(out, exist_ok=True)
    acts = [{"js": PRE + "S.approach = L.APPROACHES.findIndex(a => a.id === '%s'); L.refresh(false); L.R.warmOn = false; return L.APPROACHES[S.approach].id;" % apid}]
    for prefix, mode in (('', 0), ('plain-', 4)):
        acts.append({"js": PRE + "S.colour.mode = %d; L.syncControls(); L.touch(); return 'colour ' + S.colour.mode;" % mode})
        for name, js in EXTRA:
            acts.append({"js": PRE + js + END(prefix + name), "wait": "done", "timeout": 900, "shot": "%s/%s%s.png" % (out, prefix, name), "clip": "#stage"})
    json.dump(acts, open(out + '/plan.json', 'w', encoding='utf-8'), indent=1)
    print(out, sum('shot' in a for a in acts))

# ---- (2) the judge's own dial settings; Depth colours, full Balanced quality
VIEWS = [
    ('m3d-default', "S.flat = false; S.cutOn = false; S.cut = 0; $('mode-m').click(); S.n = 2; L.refresh(false); L.resetCam();"),
    ('m2d-z025', "L.resetCam(); S.cutOn = false; S.flat = true; S.cut = 0.25; S.v2.x = -0.6; S.v2.y = 0; S.v2.h = 3.2;"),
    ('j-bas-3d', "S.flat = false; S.cut = 0; $('mode-j').click(); S.n = 2; S.c[0] = -1; S.c[1] = 0; S.c[2] = 0; L.refresh(false); L.resetCam();"),
    ('j-bas-x', "cam.yaw = 0; cam.pitch = 0;"),
    ('j-bas-2d-z020', "L.resetCam(); S.flat = true; S.cut = 0.2; S.v2.x = 0; S.v2.y = 0; S.v2.h = 3.0;"),
    ('j-rab-3d', "S.flat = false; S.cut = 0; S.c[0] = -0.1226; S.c[1] = 0.7449; S.c[2] = 0; L.resetCam();"),
    ('j-off-3d', "S.c[0] = -1.0; S.c[1] = 0.045; S.c[2] = 0.026; L.resetCam();"),
]
def job(name, apid, variants):
    out = '%s/%s' % (root, name)
    os.makedirs(out, exist_ok=True)
    acts = [{"js": PRE + "S.approach = L.APPROACHES.findIndex(a => a.id === '%s'); L.R.warmOn = false; S.colour.mode = 4; L.refresh(false); return L.APPROACHES[S.approach].id;" % apid}]
    for tag, setter in variants:
        for view, js in VIEWS:
            acts.append({"js": PRE + setter + " " + js + END(view + '--' + tag), "wait": "done", "timeout": 900, "shot": "%s/%s--%s.png" % (out, view, tag), "clip": "#stage"})
    json.dump(acts, open(out + '/plan.json', 'w', encoding='utf-8'), indent=1)
    print(out, sum('shot' in a for a in acts))

def sf(planes, blend, curve=0, mix=0, de=3, steps=260):
    return "Object.assign(S.param.softfold, { planes: %d, blend: %s, curve: %d, mix: %d }); S.q.de = %d; S.q.steps = %d;" % (planes, blend, curve, mix, de, steps)
job('v-softfold', 'softfold', [
    ('p2-a10', sf(2, 0.10)),
    ('p2-a40', sf(2, 0.40)),
    ('p2-a45', sf(2, 0.45)),
    ('p2-a49', sf(2, 0.49)),
    ('p3-a35', sf(3, 0.35)),
    ('p4-a45', sf(4, 0.45)),
    ('p2-a25-de0', sf(2, 0.25, de=0, steps=700)),
    ('p2-a49-de0', sf(2, 0.49, de=0, steps=700)),
])
def ab(k, wob, reach=45, pinch=0, de=3, steps=260):
    return "Object.assign(S.param.axisbulb, { k: %d, wob: %s, reach: %s, pinch: %s }); S.q.de = %d; S.q.steps = %d;" % (k, wob, reach, pinch, de, steps)
job('v-axisbulb', 'axisbulb', [
    ('k1-a040', ab(1, 0.4)),
    ('k1-a100-r90', ab(1, 1.0, reach=90)),
    ('k1-am050', ab(1, -0.5)),
    ('k1-a025-r0', ab(1, 0.25, reach=0)),
    ('k5-a000-de0', ab(5, 0, de=0, steps=700)),
    ('km3-a020-de0', ab(-3, 0.2, de=0, steps=700)),
    ('k1-a020-b050', ab(1, 0.2, pinch=0.5)),
])

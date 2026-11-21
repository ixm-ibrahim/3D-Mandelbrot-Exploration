"""Step lists for the standard pictures of the two baselines (frozen app, approach mercator, planes 1 and 2).
   python out/lab2/judge/pictures.py
then  python tools/shot.py --url dist/lab2-base.html --actions out/lab2/judge/base-inflated/pictures.json   (and base-folded)"""
import json, os
PRE = "const L = window.squaringLab, S = L.S, cam = L.cam, $ = id => document.getElementById(id); "
END = " S.colour.mode = %d; L.syncControls(); L.touch(); const st = $('stage').getBoundingClientRect(); return JSON.stringify({ shot: '%s', approach: L.APPROACHES[S.approach].id, param: S.param.mercator, mode: S.mode, n: S.n, iter: S.iter, c: S.c, flat: S.flat, cutOn: S.cutOn, cut: S.cut, v2: [S.v2.x, S.v2.y, S.v2.h], cam: [cam.yaw, cam.pitch, cam.dist].map(x => +x.toFixed(4)), stage: [st.width, st.height], colour: S.colour.mode, q: S.q });"
TOP = "cam.yaw = -Math.PI / 2; cam.pitch = 1.5699;"
for folder, planes in (('base-inflated', 1), ('base-folded', 2)):
    out = 'out/lab2/judge/' + folder
    SEL = "S.approach = L.APPROACHES.findIndex(a => a.id === 'mercator'); S.param.mercator.planes = %d; L.refresh(false); L.R.warmOn = false; L.resetCam();" % planes
    steps = [
        ('m3d-default', SEL),
        ('m3d-top', TOP),
        ('m3d-x', "cam.yaw = 0; cam.pitch = 0;"),
        ('m3d-y', "cam.yaw = -Math.PI / 2; cam.pitch = 0;"),
        ('m3d-cut0', "L.resetCam(); cam.pitch = 50 * Math.PI / 180; S.cutOn = true; S.cut = 0;"),
        ('m3d-cut02', "S.cut = 0.2;"),
        ('m2d-z000', "L.resetCam(); S.cutOn = false; S.flat = true; S.cut = 0; S.v2.x = -0.6; S.v2.y = 0; S.v2.h = 3.2;"),
        ('m2d-z010', "S.cut = 0.1;"),
        ('m2d-z025', "S.cut = 0.25;"),
        ('m2d-z050', "S.cut = 0.5;"),
        ('j-bas-3d', "S.flat = false; S.cut = 0; $('mode-j').click(); S.c[0] = -1; S.c[1] = 0; S.c[2] = 0; L.resetCam();"),
        ('j-bas-top', TOP),
        ('j-bas-x', "cam.yaw = 0; cam.pitch = 0;"),
        ('j-bas-2d-z000', "L.resetCam(); S.flat = true; S.cut = 0; S.v2.x = 0; S.v2.y = 0; S.v2.h = 3.0;"),
        ('j-bas-2d-z020', "S.cut = 0.2;"),
        ('j-rab-3d', "S.flat = false; S.cut = 0; S.c[0] = -0.1226; S.c[1] = 0.7449; S.c[2] = 0; L.resetCam();"),
        ('j-off-3d', "S.c[0] = -1.0; S.c[1] = 0.045; S.c[2] = 0.026; L.resetCam();"),
        ('m3d-n3', "S.c[0] = -1; S.c[1] = 0; S.c[2] = 0; $('mode-m').click(); S.n = 3; L.refresh(false); L.resetCam();"),
        ('m3d-n8', "S.n = 8; L.refresh(false); L.resetCam();"),
    ]
    acts = []
    for name, js in steps:
        acts.append({"js": PRE + js + END % (0, name), "wait": "done", "timeout": 900, "shot": "%s/%s.png" % (out, name), "clip": "#stage"})
        acts.append({"js": PRE + END % (4, 'plain-' + name), "wait": "done", "timeout": 900, "shot": "%s/plain-%s.png" % (out, name), "clip": "#stage"})
    os.makedirs(out, exist_ok=True)
    json.dump(acts, open(os.path.join(out, 'pictures.json'), 'w', encoding='utf-8'), indent=1)
    print('wrote %s/pictures.json, %d pictures' % (out, len(acts)))

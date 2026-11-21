"""Write the shot.py step list for the standard pictures of one setting of the axisbulb dials.
   python out/lab2/axisbulb/pictures.py <outdir> <all|key> <k> <wobble A> <reach degrees> [approach id] [pinch B]
then  python tools/shot.py --url dist/lab2-axisbulb.html --actions <outdir>/pictures.json
Every picture is taken twice: default colours as <name>.png, colour mode "Depth from the camera" as plain-<name>.png."""
import json, os, sys
out, subset, k, wob, reach = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5]
apid = sys.argv[6] if len(sys.argv) > 6 else 'axisbulb'
pinch = sys.argv[7] if len(sys.argv) > 7 else '0'
PRE = "const L = window.squaringLab, S = L.S, cam = L.cam, $ = id => document.getElementById(id); "
END = " L.syncControls(); L.touch(); const st = $('stage').getBoundingClientRect(); return JSON.stringify({ shot: '%s', approach: L.APPROACHES[S.approach].id, param: S.param[L.APPROACHES[S.approach].id], mode: S.mode, n: S.n, iter: S.iter, c: S.c, flat: S.flat, cutOn: S.cutOn, cut: S.cut, colour: S.colour.mode, v2: [S.v2.x, S.v2.y, S.v2.h], cam: [cam.yaw, cam.pitch, cam.dist].map(x => +x.toFixed(4)), target: cam.target, stage: [st.width, st.height], aa: S.q.aa, res: S.q.res });"
SET = ("$('ap-%s').click(); " % apid) + ("S.param.axisbulb.k = %s; S.param.axisbulb.wob = %s; S.param.axisbulb.reach = %s; S.param.axisbulb.pinch = %s; " % (k, wob, reach, pinch) if apid == 'axisbulb' else '')
TOP = "cam.yaw = -Math.PI / 2; cam.pitch = 1.5699;"
steps = [
    ('m3d-default', "L.R.warmOn = false; " + SET + "L.refresh(false); L.resetCam();"),
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
KEY = {'m3d-default', 'j-bas-3d', 'j-bas-x', 'j-rab-3d', 'm2d-z025'}
acts = []
for name, js in steps:
    keep = subset == 'all' or name in KEY
    a = {"js": PRE + "S.colour.mode = 0; " + js + END % name}
    if keep:
        a.update({"wait": "done", "timeout": 900, "shot": "%s/%s.png" % (out, name), "clip": "#stage"})
    acts.append(a)
    if keep:
        acts.append({"js": PRE + "S.colour.mode = 4;" + END % ('plain-' + name), "wait": "done", "timeout": 900, "shot": "%s/plain-%s.png" % (out, name), "clip": "#stage"})
os.makedirs(out, exist_ok=True)
json.dump(acts, open(os.path.join(out, 'pictures.json'), 'w', encoding='utf-8'), indent=1)
print('wrote %s/pictures.json, %d steps, %d pictures' % (out, len(acts), sum('shot' in a for a in acts)))

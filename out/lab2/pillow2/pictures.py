"""Write the shot.py step lists for the standard pictures of one approach, in the default colours and
again in the colour mode "Depth from the camera" (prefix plain-).
   python out/lab2/pillow2/pictures.py <approach id> [planes]
then  python tools/shot.py --url dist/lab2-pillow2.html --actions out/lab2/pillow2/<folder>/pictures.json
The folder is the approach id (mercator with planes: mercator1 / mercator2)."""
import json, os, sys
apid = sys.argv[1]
planes = sys.argv[2] if len(sys.argv) > 2 else ''
only = sys.argv[3] if len(sys.argv) > 3 else 'both'      # both | plain | default
folder = apid + planes
out = 'out/lab2/pillow2/' + folder
PRE = "const L = window.squaringLab, S = L.S, cam = L.cam, $ = id => document.getElementById(id); "
END = " L.syncControls(); L.touch(); const st = $('stage').getBoundingClientRect(); return JSON.stringify({ shot: '%s', approach: L.APPROACHES[S.approach].id, param: S.param[L.APPROACHES[S.approach].id], colour: S.colour.mode, mode: S.mode, n: S.n, iter: S.iter, c: S.c, flat: S.flat, cutOn: S.cutOn, cut: S.cut, cam: [cam.yaw, cam.pitch, cam.dist].map(x => +x.toFixed(4)), stage: [st.width, st.height], q: S.q });"
TOP = "cam.yaw = -Math.PI / 2; cam.pitch = 1.5699;"
SEL = "S.approach = L.APPROACHES.findIndex(a => a.id === '%s'); %s L.refresh(false); L.R.warmOn = false;" % (
    apid, ("S.param.mercator.planes = %s;" % planes) if planes else "")
steps = [
    ('m3d-default', "S.flat = false; S.cutOn = false; S.cut = 0; $('mode-m').click(); S.n = 2; L.refresh(false); L.resetCam();"),
    ('m3d-top', TOP),
    ('m3d-x', "cam.yaw = 0; cam.pitch = 0;"),
    ('m2d-z000', "L.resetCam(); S.cutOn = false; S.flat = true; S.cut = 0; S.v2.x = -0.6; S.v2.y = 0; S.v2.h = 3.2;"),
    ('m2d-z010', "S.cut = 0.1;"),
    ('m2d-z025', "S.cut = 0.25;"),
    ('j-bas-3d', "S.flat = false; S.cut = 0; $('mode-j').click(); S.c[0] = -1; S.c[1] = 0; S.c[2] = 0; L.resetCam();"),
    ('j-bas-top', TOP),
    ('j-bas-x', "cam.yaw = 0; cam.pitch = 0;"),
    ('j-bas-2d-z000', "L.resetCam(); S.flat = true; S.cut = 0; S.v2.x = 0; S.v2.y = 0; S.v2.h = 3.0;"),
    ('j-bas-2d-z020', "S.cut = 0.2;"),
    ('j-rab-3d', "S.flat = false; S.cut = 0; S.c[0] = -0.1226; S.c[1] = 0.7449; S.c[2] = 0; L.resetCam();"),
]
acts = [{"js": PRE + SEL + " return L.APPROACHES[S.approach].id + ' ' + JSON.stringify(S.param[L.APPROACHES[S.approach].id]);"}]
for prefix, mode in (('', 0), ('plain-', 4)):
    if only == 'plain' and mode == 0: continue
    if only == 'default' and mode == 4: continue
    acts.append({"js": PRE + "S.colour.mode = %d; L.syncControls(); L.touch(); return 'colour mode ' + S.colour.mode;" % mode})
    for name, js in steps:
        acts.append({"js": PRE + js + END % (prefix + name), "wait": "done", "timeout": 900,
                     "shot": "%s/%s%s.png" % (out, prefix, name), "clip": "#stage"})
os.makedirs(out, exist_ok=True)
json.dump(acts, open(os.path.join(out, 'pictures.json'), 'w', encoding='utf-8'), indent=1)
print('wrote %s/pictures.json, %d steps, %d pictures' % (out, len(acts), sum('shot' in a for a in acts)))

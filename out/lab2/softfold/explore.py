"""Exploration pictures: a few key views for each variant of the soft fold, in the plain colour mode
"Depth from the camera", 4 refining passes. Then contact sheets, one per view.
   python out/lab2/softfold/explore.py plan     -> out/lab2/softfold/explore/plan.json
   python tools/shot.py --url dist/lab2-softfold.html --actions out/lab2/softfold/explore/plan.json
   python out/lab2/softfold/explore.py sheets   -> out/lab2/softfold/explore/sheet-<view>.png
"""
import json, os, sys
OUT = 'out/lab2/softfold/explore'
VARIANTS = [  # name, planes, blend, curve, mix
    ('p2-a00', 2, 0.0, 0, 0), ('p2-a15', 2, 0.15, 0, 0), ('p2-a25', 2, 0.25, 0, 0), ('p2-a35', 2, 0.35, 0, 0),
    ('p2-a42', 2, 0.42, 0, 0), ('p2-a48', 2, 0.48, 0, 0), ('p2-a25-smoother', 2, 0.25, 1, 0), ('p2-a25-straight', 2, 0.25, 0, 1),
    ('p2-a00-straight', 2, 0.0, 0, 1), ('p3-a25', 3, 0.25, 0, 0), ('p3-a40', 3, 0.40, 0, 0), ('p1', 1, 0.25, 0, 0),
    ('pinch-p2-a00', 2, 0.0, 0, 2), ('pinch-p2-a25', 2, 0.25, 0, 2), ('pinch-p2-a40', 2, 0.40, 0, 2), ('pinch-p2-a47', 2, 0.47, 0, 2),
    ('pinch-p3-a25', 3, 0.25, 0, 2), ('pinch-p3-a40', 3, 0.40, 0, 2), ('pinch-p2-a40-smoother', 2, 0.40, 1, 2), ('pinch-p4-a40', 4, 0.40, 0, 2),
]
VIEWS = [
    ('j-bas-3d', "S.flat = false; S.cutOn = false; S.cut = 0; S.mode = 'j'; S.n = 2; S.c[0] = -1; S.c[1] = 0; S.c[2] = 0; L.refresh(false); L.resetCam();"),
    ('j-bas-x', "cam.yaw = 0; cam.pitch = 0;"),
    ('j-bas-2d-z020', "L.resetCam(); S.flat = true; S.cut = 0.2; S.v2.x = 0; S.v2.y = 0; S.v2.h = 3.0;"),
    ('j-rab-3d', "S.flat = false; S.cut = 0; S.c[0] = -0.1226; S.c[1] = 0.7449; S.c[2] = 0; L.resetCam();"),
    ('j-off-3d', "S.c[0] = -1.0; S.c[1] = 0.045; S.c[2] = 0.026; L.resetCam();"),
    ('m3d-default', "S.mode = 'm'; L.refresh(false); L.resetCam();"),
    ('m2d-z025', "S.flat = true; S.cut = 0.25; S.v2.x = -0.6; S.v2.y = 0; S.v2.h = 3.2;"),
]
PRE = "const L = window.squaringLab, S = L.S, cam = L.cam, $ = id => document.getElementById(id); "
if sys.argv[1] == 'plan':
    names = sys.argv[2].split(',') if len(sys.argv) > 2 else None
    acts = [{"js": PRE + "L.R.warmOn = false; S.q.aa = 4; S.colour.mode = 4; L.touch(); return 'start';", "wait": "done", "timeout": 600}]
    for name, p, a, cu, mx in VARIANTS:
        if names and name not in names: continue
        setp = "Object.assign(S.param.softfold, { planes: %d, blend: %g, curve: %d, mix: %d }); " % (p, a, cu, mx)
        for view, js in VIEWS:
            acts.append({"js": PRE + setp + js + " L.syncControls(); L.touch(); return '%s %s ' + JSON.stringify(S.param.softfold) + ' mode ' + S.mode + ' c ' + S.c;" % (name, view),
                         "wait": "done", "timeout": 900, "shot": "%s/%s--%s.png" % (OUT, view, name), "clip": "#stage"})
    os.makedirs(OUT, exist_ok=True)
    json.dump(acts, open(os.path.join(OUT, 'plan.json'), 'w', encoding='utf-8'), indent=1)
    print('wrote %s/plan.json, %d pictures' % (OUT, len(acts) - 1))
else:
    from PIL import Image, ImageDraw
    for view, _ in VIEWS:
        tiles = [(n, os.path.join(OUT, '%s--%s.png' % (view, n))) for n, *_ in VARIANTS]
        tiles = [(n, p) for n, p in tiles if os.path.exists(p)]
        if not tiles: continue
        cols, tw = 4, 480
        ims = []
        for n, p in tiles:
            im = Image.open(p).convert('RGB'); W, H = im.size
            im = im.crop((60, 40, W - 130, H - 60)); im = im.resize((tw, int(tw * im.size[1] / im.size[0])), Image.LANCZOS)
            ImageDraw.Draw(im).text((8, 6), n, fill=(255, 255, 255))
            ims.append(im)
        th = ims[0].size[1]; rows = (len(ims) + cols - 1) // cols
        sheet = Image.new('RGB', (cols * tw, rows * th), (0, 0, 0))
        for i, im in enumerate(ims): sheet.paste(im, ((i % cols) * tw, (i // cols) * th))
        sheet.save(os.path.join(OUT, 'sheet-%s.png' % view))
        print('wrote', os.path.join(OUT, 'sheet-%s.png' % view), sheet.size)

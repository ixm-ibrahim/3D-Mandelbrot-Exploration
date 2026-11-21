"""Lab pictures of a rule on a panel of Julia sets. python out/me/panel/shots.py  -> out/me/panel/look.json"""
import json
PANEL = [  # tag, plain name, c, iterations
    ('basilica', 'Basilica, c = -1', [-1, 0, 0], 40),
    ('airplane', 'Airplane, c = -1.7549', [-1.754878, 0, 0], 40),
    ('sanmarco', 'San Marco, c = -0.75', [-0.75, 0, 0], 40),
    ('cauliflower', 'Cauliflower, c = 0.25', [0.25, 0, 0], 40),
    ('rabbit', 'Douady rabbit, c = -0.123 + 0.745i', [-0.122561, 0.744862, 0], 40),
    ('dendrite', 'Dendrite, c = i', [0, 1, 0], 20),
    ('siegel', 'Siegel disc, c = -0.391 - 0.587i', [-0.390541, -0.586788, 0], 40),
    ('rabbit90', 'Rabbit, c turned 90 degrees out of the flat plane', [-0.122561, 0, 0.744862], 40),
    ('rabbit30', 'Rabbit, c turned 30 degrees out of the flat plane', [-0.122561, 0.645069, 0.372431], 40),
]
HEAD = ("\nconst L = window.squaringLab, S = L.S, $ = id => document.getElementById(id);\n"
        "const sleep = ms => new Promise(r => setTimeout(r, ms));\n"
        "const go = () => { L.syncControls(); L.refresh(false); L.touch(); if (L.viewChanged) L.viewChanged(); };\n"
        "const pick = id => { $('ap-' + id).click(); };\n")
TAIL = "return '%s: ' + L.APPROACHES[S.approach].id + ' iter ' + S.iter + ' c ' + JSON.stringify(S.c) + ' failed ' + L.R.failed;"
def v3(name, id_, c, it, cam):
    js = HEAD + "pick('%s'); await sleep(250); S.n = 2; S.iter = %d; $('mode-j').click(); await sleep(150); S.flat = false; S.cutOn = false; S.c = %s; L.resetCam(); %s go(); await sleep(200); " % (id_, it, json.dumps(c), cam)
    return {"js": js + TAIL % name, "timeout": 900, "wait": "done", "shot": "out/me/panel/%s.png" % name, "clip": "#stage canvas"}
def v2(name, id_, c, it):
    js = HEAD + "pick('%s'); await sleep(250); S.n = 2; S.iter = %d; $('mode-j').click(); await sleep(150); S.cutOn = false; S.flat = true; S.cut = 0; S.v2.x = 0; S.v2.y = 0; S.v2.h = 3.6; S.c = %s; go(); await sleep(200); " % (id_, max(it, 40), json.dumps(c))
    return {"js": js + TAIL % name, "timeout": 900, "wait": "done", "shot": "out/me/panel/%s.png" % name, "clip": "#stage canvas"}
ABOVE = "L.cam.yaw = -1.571; L.cam.pitch = 1.1; L.cam.dist = 4.6;"
SIDE = "L.cam.yaw = -1.9; L.cam.pitch = 0.3; L.cam.dist = 4.6;"
if __name__ == '__main__':
    steps = [{"js": "const L = window.squaringLab; L.R.warmOn = false; return 'page up, ' + L.APPROACHES.length + ' entries';", "wait": "done", "timeout": 600}]
    for tag, name, c, it in PANEL:
        steps += [v2(tag + '-flat', 'turnalong', c, it), v3(tag + '-along-above', 'turnalong', c, it, ABOVE), v3(tag + '-along-side', 'turnalong', c, it, SIDE),
                  v3(tag + '-one-side', 'mercator', c, it, SIDE)]
    json.dump(steps, open('out/me/panel/look.json', 'w', encoding='utf-8'), indent=1)
    print(len(steps), 'steps')

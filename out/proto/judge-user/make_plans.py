"""Judge (user lens): build the shot.py plans for the three baselines. Same views as out/proto/sine/pictures.json.

  python out/proto/judge-user/make_plans.py   -> plan-base-inflated.json, plan-base-folded.json, plan-base-bulb.json
"""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
PRE = ("const L = window.squaringLab, S = L.S, cam = L.cam, $ = id => document.getElementById(id); "
       "const type = (id, v) => { const e = $(id); e.value = v; e.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', bubbles: true })); }; "
       "const say = t => t + ' | ' + L.APPROACHES[S.approach].id + ' planes=' + S.param.mercator.planes + ' mode=' + S.mode + ' n=' + S.n + ' it=' + S.iter + ' c=' + S.c.join(',') + ' flat=' + S.flat + ' cutOn=' + S.cutOn + ' cut=' + S.cut; ")

SETUP = {
    "base-inflated": "$('ap-mercator').click(); document.querySelectorAll('details.sec').forEach(d => { d.open = true; }); type('par-mercator-planesNum', '1'); ",
    "base-folded": "$('ap-mercator').click(); document.querySelectorAll('details.sec').forEach(d => { d.open = true; }); type('par-mercator-planesNum', '2'); ",
    "base-bulb": "$('ap-bulb').click(); S.n = 2; ",
}
KEEP = {
    "base-inflated": "if (S.param.mercator.planes !== 1) { S.param.mercator.planes = 1; L.syncControls(); L.refresh(false); } ",
    "base-folded": "if (S.param.mercator.planes !== 2) { S.param.mercator.planes = 2; L.syncControls(); L.refresh(false); } ",
    "base-bulb": "",
}
TOP = "cam.pitch = 1.5607; cam.yaw = -Math.PI / 2; "
AX = "cam.pitch = 0; cam.yaw = 0; "
AY = "cam.pitch = 0; cam.yaw = Math.PI / 2; "

for name in SETUP:
    out = "out/proto/judge-user/%s/" % name
    steps = []

    def step(js, shot, keep=KEEP[name]):
        steps.append({"js": PRE + js.replace("@KEEP@", keep), "wait": "done", "timeout": 900, "shot": out + shot + ".png", "clip": "#stage"})

    step(SETUP[name] + "L.R.warmOn = false; $('qBal').click(); L.resetCam(); L.syncControls(); L.refresh(false); return say('default q=' + JSON.stringify(S.q));", "m3d-default")
    step(TOP + "L.touch(); return say('top');", "m3d-top")
    step(AX + "L.touch(); return say('along x');", "m3d-x")
    step(AY + "L.touch(); return say('along y');", "m3d-y")
    step("L.resetCam(); cam.pitch = 50 * Math.PI / 180; S.cutOn = true; S.cut = 0; L.syncControls(); L.touch(); return say('cut 0');", "m3d-cut0")
    step("S.cut = 0.2; L.syncControls(); L.touch(); return say('cut 0.2');", "m3d-cut02")
    step("S.cutOn = false; S.cut = 0; L.resetCam(); S.flat = true; S.v2.x = -0.5; S.v2.y = 0; S.v2.h = 3.2; L.syncControls(); L.touch(); return say('2D z=0');", "m2d-z000")
    for z, nm in [(0.1, "m2d-z010"), (0.25, "m2d-z025"), (0.5, "m2d-z050")]:
        step("S.cut = %s; L.syncControls(); L.touch(); return say('2D');" % z, nm)
    step("S.flat = false; S.cut = 0; L.syncControls(); $('mode-j').click(); S.c = [-1, 0, 0]; @KEEP@L.resetCam(); L.syncControls(); L.touch(); return say('julia basilica');", "j-bas-3d")
    step(TOP + "L.touch(); return say('julia top');", "j-bas-top")
    step(AX + "L.touch(); return say('julia along x');", "j-bas-x")
    step("L.resetCam(); S.flat = true; S.cut = 0; S.v2.x = 0; S.v2.y = 0; S.v2.h = 3.2; L.syncControls(); L.touch(); return say('julia 2D z=0');", "j-bas-2d-z000")
    step("S.cut = 0.2; L.syncControls(); L.touch(); return say('julia 2D z=0.2');", "j-bas-2d-z020")
    step("S.flat = false; S.cut = 0; S.c = [-0.1226, 0.7449, 0]; @KEEP@L.resetCam(); L.syncControls(); L.touch(); return say('julia rabbit');", "j-rab-3d")
    with open(os.path.join(HERE, "plan-%s.json" % name), "w", encoding="utf-8") as f:
        json.dump(steps, f, indent=1)
    print(name, len(steps), "steps")

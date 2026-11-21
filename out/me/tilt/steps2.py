"""Close-ups of the tilted quaternion square: python out/me/tilt/steps2.py -> out/me/tilt/steps2.json"""
import io, json, os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
HEAD = """
const L = window.squaringLab, $ = id => document.getElementById(id);
const sleep = ms => new Promise(r => setTimeout(r, ms));
const go = () => { L.syncControls(); L.refresh(false); L.touch(); if (L.viewChanged) L.viewChanged(); };
"""
steps = []
def step(js, name):
    steps.append({"js": HEAD + js + " return '" + name + "';", "timeout": 900, "wait": "done",
                  "shot": "out/me/tilt/" + name + ".png", "clip": "#stage canvas"})

step("$('ap-tilt').click(); await sleep(400); $('mode-m').click(); await sleep(200); L.S.param.tilt.tilt = 40; L.resetCam(); L.cam.yaw = -1.0; L.cam.pitch = 0.45; L.cam.dist = 4.2; go(); await sleep(200);", "c-m40-a")
step("L.cam.yaw = 0.6; L.cam.pitch = 0.35; go();", "c-m40-b")
step("L.cam.yaw = 2.2; L.cam.pitch = 0.5; go();", "c-m40-c")
step("L.cam.yaw = -2.4; L.cam.pitch = -0.5; go();", "c-m40-d")
# zoom in on the body
step("L.cam.yaw = -1.0; L.cam.pitch = 0.45; L.cam.dist = 1.6; L.cam.target = [-0.2, -0.5, 0.35]; go();", "c-m40-zoom")
step("L.cam.dist = 0.6; go();", "c-m40-zoom2")
# Julia sets, bigger
step("$('mode-j').click(); await sleep(200); L.S.c = [-1, 0, 0]; L.resetCam(); L.cam.dist = 3.6; go(); await sleep(200);", "c-jbas40")
step("L.S.c = [-0.122561, 0.744862, 0]; L.resetCam(); L.cam.dist = 3.6; go(); await sleep(200);", "c-jrab40")
step("L.S.c = [-0.8, 0.156, 0]; L.resetCam(); L.cam.dist = 3.6; go(); await sleep(200);", "c-jdrag40")
step("L.S.c = [0.285, 0.01, 0]; L.resetCam(); L.cam.dist = 3.6; go(); await sleep(200);", "c-jcaul40")
step("L.S.c = [-0.4, 0.6, 0]; L.resetCam(); L.cam.dist = 3.6; go(); await sleep(200);", "c-jspir40")
step("L.S.c = [-1.754878, 0, 0]; L.resetCam(); L.cam.dist = 4.2; go(); await sleep(200);", "c-jair40")

io.open(os.path.join(ROOT, 'out', 'me', 'tilt', 'steps2.json'), 'w', encoding='utf-8').write(json.dumps(steps, indent=1))
print(len(steps), 'steps')

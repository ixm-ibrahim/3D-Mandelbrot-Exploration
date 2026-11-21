"""Part A: the slice at z = 0 against a flat set computed in Python. Writes a_steps.json and a_cases.json."""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = "out/t6/modes/a"
os.makedirs(os.path.join(HERE, "a"), exist_ok=True)

SETUP = """
const L = window.squaringLab, S = L.S;
L.R.warmOn = false;
const st = document.createElement('style');
st.textContent = '#stage > *:not(canvas){visibility:hidden !important}';
document.head.appendChild(st);
return { approaches: L.APPROACHES.map(a => a.id), iter: S.iter, kiter: S.k.iter, aa: S.q.aa, res: S.q.res };
"""

CASE = """
const L = window.squaringLab, S = L.S;
S.mode = %(mode)s; S.c = %(c)s; S.approach = L.APPROACHES.findIndex(a => a.id === %(ap)s); S.n = %(n)s;
S.flat = true; S.cut = 0; S.cutOn = false; S.flip = [0, %(flip)d]; S.abs = [0, 0, 0]; S.mosaic = false;
S.colour.mode = 7; S.colour.edge = 0; S.colour.edgeGlow = 0; S.colour.inMode = 0;
S.v2.x = %(x)s; S.v2.y = %(y)s; S.v2.h = %(h)s;
L.syncControls(); L.refresh(false);
const stg = document.getElementById('stage'), cv = document.getElementById('view');
return { name: %(name)s, w: stg.clientWidth, h: stg.clientHeight, cw: cv.width, ch: cv.height, v2: [S.v2.x, S.v2.y, S.v2.h],
  iter: S.iter, n: S.n, flipBox: document.getElementById('flipz').checked, flatBox: document.getElementById('flat').checked,
  approach: L.APPROACHES[S.approach].id, mode: S.mode, c: S.c };
"""

scenes = [("m", "'m'", [-1, 0, 0]), ("jb", "'j'", [-1, 0, 0]), ("jr", "'j'", [-0.123, 0.745, 0])]
frames = {  # centre x, y and visible height per (scene kind, power)
    ("m", 2): (-0.5, 0, 3.2), ("m", 3): (0, 0, 3.2), ("m", -2): (0, 0, 4.0),
    ("j", 2): (0, 0, 3.6), ("j", 3): (0, 0, 3.2), ("j", -2): (0, 0, 4.0),
}
steps = [{"js": SETUP}]
cases = []
aps = ["mercator", "lathe", "bulb", "split"]
for ap in aps:
    for sc, mode, c in scenes:
        for n in (2, 3, -2):
            for flip in (0, 1):
                name = "%s-%s-n%s-f%d" % (ap, sc, n, flip)
                x, y, h = frames[(sc[0], n)]
                steps.append({"js": CASE % dict(mode=mode, c=json.dumps(c), ap=json.dumps(ap), n=n, flip=flip, x=x, y=y, h=h, name=json.dumps(name)),
                              "wait": "done", "timeout": 300, "shot": "%s/%s.png" % (OUT, name), "clip": "#view"})
                cases.append(dict(name=name, ap=ap, scene=sc, mode=mode.strip("'"), c=c, n=n, flip=flip, x=x, y=y, h=h))
# the control: the classic Mandelbulb is the one approach that is allowed to differ
for sc, mode, c in scenes[:2]:
    for n in (2, 3):
        name = "classic-%s-n%s-f0" % (sc, n)
        x, y, h = frames[(sc[0], n)]
        steps.append({"js": CASE % dict(mode=mode, c=json.dumps(c), ap=json.dumps("classic"), n=n, flip=0, x=x, y=y, h=h, name=json.dumps(name)),
                      "wait": "done", "timeout": 300, "shot": "%s/%s.png" % (OUT, name), "clip": "#view"})
        cases.append(dict(name=name, ap="classic", scene=sc, mode=mode.strip("'"), c=c, n=n, flip=0, x=x, y=y, h=h))
json.dump(steps, open(os.path.join(HERE, "a_steps.json"), "w"), indent=1)
json.dump(cases, open(os.path.join(HERE, "a_cases.json"), "w"), indent=1)
print(len(steps), "steps")

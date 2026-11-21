"""Round 20, entry: the page's 2D view of the cut at z = 0 for "Wind, then square" against Sphere inversions, one plane
(whose cut is the flat set): same page, same settings, pixel by pixel. JULIA SETS ONLY. Also one 3D look of the
basilica at the 14 iterations the page opens with.
  python out/r20/entry/flatcmp.py -> flat-<set>-<entry>-<estimate>.png, look-bas-14.png, flatcmp.txt"""
import json, os, sys
import numpy as np
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import run
from pics import HEAD, END

SETS = [('basilica', [-1, 0, 0]), ('rabbit', [-0.122561, 0.744862, 0]), ('siegel', [-0.390541, -0.586788, 0]), ('dendrite', [0, 1, 0])]
V2 = HEAD + """
const q = %s;
$('mode-j').click(); await sleep(150);
$('ap-' + q.id).click(); await sleep(250);
S.n = 2; S.iter = 40; S.cutOn = false; S.flat = true; S.cut = 0; S.v2.x = 0; S.v2.y = 0; S.v2.h = 3.6; S.c = q.c; S.q.de = q.de; S.q.stepk = 0.8;
go(); await sleep(250);
return q.name + ': mode ' + S.mode + ', approach ' + L.APPROACHES[S.approach].id + ', flat ' + S.flat + ', c ' + JSON.stringify(S.c) + ', estimate asked ' + S.q.de;
"""
V3 = HEAD + """
$('mode-j').click(); await sleep(150); $('ap-windsq').click(); await sleep(250);
S.n = 2; S.iter = 14; S.flat = false; S.cutOn = false; S.c = [-1, 0, 0]; S.q.de = 3; S.q.stepk = 0.8;
L.resetCam(); L.cam.yaw = -1.9; L.cam.pitch = 0.3; L.cam.dist = 4.6; L.cam.target = [0, 0, 0]; go(); await sleep(250);
return 'basilica at 14 iterations: approach ' + L.APPROACHES[S.approach].id + ', iter ' + S.iter;
"""

if __name__ == '__main__':
    steps = [run.UP]
    for tag, c in SETS:
        for id_, de in (('windsq', 3), ('mercator', 0), ('mercator', 3)):
            name = 'flat-%s-%s-%d' % (tag, id_, de)
            steps.append({'js': V2 % json.dumps(dict(id=id_, c=c, de=de, name=name)), 'wait': 'done', 'timeout': 900, 'shot': run.REL + name + '.png', 'clip': '#stage canvas'})
    steps.append({'js': V3, 'wait': 'done', 'timeout': 900, 'shot': run.REL + 'look-bas-14.png', 'clip': '#stage canvas'})
    steps.append({'js': HEAD + "S.flat = false; S.iter = 14; go(); return 'back to 3D';", 'wait': 'done', 'timeout': 600})
    steps.append(END)
    code, text, vals = run.shot(run.PAGE, steps, 'flatcmp-steps')
    lines = []
    for tag, c in SETS:
        a = np.asarray(Image.open(os.path.join(HERE, 'flat-%s-windsq-3.png' % tag)).convert('RGB')).astype(int)
        for de, nm in ((0, 'Rough'), (3, 'Exact')):
            b = np.asarray(Image.open(os.path.join(HERE, 'flat-%s-mercator-%d.png' % (tag, de))).convert('RGB')).astype(int)
            d = np.abs(a - b).max(axis=2)
            lines.append('%-9s windsq (drawn with Rough, its cap) against Sphere inversions, one plane drawn with %-5s: %d x %d = %d pixels; differ at all: %d, by more than 8 levels: %d' % (
                tag, nm, a.shape[1], a.shape[0], d.size, int((d > 0).sum()), int((d > 8).sum())))
    out = '\n'.join(lines) + '\n'
    run.write('flatcmp.txt', out + '\n' + text)
    print(out); print(text[-600:])
    sys.exit(code)

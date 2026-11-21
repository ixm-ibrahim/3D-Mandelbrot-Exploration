"""Round 20, entry: the lab's own pictures for the two sheets. JULIA SETS ONLY (the page is put in Julia mode before
the new entry is chosen, so no Mandelbrot picture of it is ever drawn).
  python out/r20/entry/pics.py sheet     -> shot-<set>-<entry>-<camera>.png   (7 sets x 3 entries x 2 cameras, 40 iterations)
  python out/r20/entry/pics.py close     -> close-<name>.png                  (basilica and rabbit of windsq close up)
Quality as the page opens (Balanced, 12 refining passes); "Distance estimate" as the page gives it: Rough for
windsq and turnalong (their cap), Exact for mercator."""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import run

PANEL = [  # tag, plain name, c
    ('basilica', 'Basilica, c = -1', [-1, 0, 0]),
    ('sanmarco', 'San Marco, c = -0.75', [-0.75, 0, 0]),
    ('airplane', 'Airplane, c = -1.7549', [-1.754878, 0, 0]),
    ('cauliflower', 'Cauliflower, c = 0.25', [0.25, 0, 0]),
    ('rabbit', 'Douady rabbit, c = -0.123 + 0.745i', [-0.122561, 0.744862, 0]),
    ('dendrite', 'Dendrite, c = i', [0, 1, 0]),
    ('siegel', 'Siegel disc, c = -0.391 - 0.587i', [-0.390541, -0.586788, 0]),
]
ENTRIES = [('windsq', 'Wind, then square (new)'), ('turnalong', 'Turning plane, along'), ('mercator', 'Sphere inversions, one plane')]
CAMS = {'side': dict(yaw=-1.9, pitch=0.3, dist=4.6, target=[0, 0, 0]), 'above': dict(yaw=-1.571, pitch=1.1, dist=4.6, target=[0, 0, 0])}
IT = 40

HEAD = """
const L = window.squaringLab, S = L.S, $ = id => document.getElementById(id);
const sleep = ms => new Promise(r => setTimeout(r, ms));
const go = () => { L.syncControls(); L.refresh(false); L.touch(); if (L.viewChanged) L.viewChanged(); };
"""
SET = HEAD + """
const q = %s;
$('mode-j').click(); await sleep(150);
$('ap-' + q.id).click(); await sleep(250);
S.n = 2; S.iter = q.it; S.flat = false; S.cutOn = false; S.c = q.c; S.q.de = 3; S.q.stepk = q.stepk || 0.8;
L.resetCam(); L.cam.yaw = q.cam.yaw; L.cam.pitch = q.cam.pitch; L.cam.dist = q.cam.dist; L.cam.target = q.cam.target;
go(); await sleep(250);
return q.name + ': mode ' + S.mode + ', approach ' + L.APPROACHES[S.approach].id + ', iter ' + S.iter + ', c ' + JSON.stringify(S.c) + ', estimate asked ' + S.q.de + ', cap ' + L.APPROACHES[S.approach].deMax + ', ray step ' + S.q.stepk + ', passes ' + S.q.aa + ', failed ' + L.R.failed;
"""
END = {'js': HEAD + "$('mode-j').click(); await sleep(100); $('ap-mercator').click(); await sleep(200); S.q.de = 3; S.q.stepk = 0.8; go(); return 'end: failed ' + L.R.failed + ', status ' + document.getElementById('status').textContent;", 'wait': 'done', 'timeout': 600}


def step(name, q):
    return {'js': SET % json.dumps(dict(q, name=name)), 'wait': 'done', 'timeout': 900, 'shot': run.REL + name + '.png', 'clip': '#stage canvas'}


def sheet():
    out = []
    for tag, nm, c in PANEL:
        for id_, _ in ENTRIES:
            for cn, cam in CAMS.items():
                out.append(step('shot-%s-%s-%s' % (tag, id_, cn), dict(id=id_, c=c, it=IT, cam=cam)))
    return out


BAS, RAB = [-1, 0, 0], [-0.122561, 0.744862, 0]
CLOSE = [  # name, caption, c, iterations, camera, ray step
    ('close-bas-side', 'Basilica from the side', BAS, 40, dict(yaw=-1.9, pitch=0.3, dist=3.0, target=[0, 0, 0]), 0.8),
    ('close-bas-alongx', 'Basilica seen along the x-axis: six buds round each body', BAS, 40, dict(yaw=0.0, pitch=0.0, dist=3.4, target=[0, 0, 0]), 0.8),
    ('close-bas-bud', 'The bud at 60 degrees on the middle body, 0.8 away', BAS, 60, dict(yaw=1.5708, pitch=1.0472, dist=0.8, target=[0, 0.3, 0.52]), 0.8),
    ('close-bas-neck', 'Where two bodies touch, 0.3 away', BAS, 60, dict(yaw=-1.9, pitch=0.9, dist=0.3, target=[-0.618, 0, 0]), 0.8),
    ('close-rab-above', 'Rabbit from above', RAB, 40, dict(yaw=-1.571, pitch=1.3, dist=4.2, target=[0, 0, 0]), 0.8),
    ('close-rab-side', 'Rabbit from the side', RAB, 40, dict(yaw=-1.9, pitch=0.3, dist=4.2, target=[0, 0, 0]), 0.8),
    ('close-rab-alongx', 'Rabbit seen along the x-axis', RAB, 40, dict(yaw=0.0, pitch=0.0, dist=4.6, target=[0, 0, 0]), 0.8),
    ('close-rab-pinch', 'Where three bodies of the flat rabbit meet, 0.7 away', RAB, 60, dict(yaw=-1.571, pitch=0.9, dist=0.7, target=[-0.276, 0.48, 0]), 0.8),
    ('close-rab4-above', 'Rabbit from above, ray step 0.4', RAB, 40, dict(yaw=-1.571, pitch=1.3, dist=4.2, target=[0, 0, 0]), 0.4),
    ('close-rab4-side', 'Rabbit from the side, ray step 0.4', RAB, 40, dict(yaw=-1.9, pitch=0.3, dist=4.2, target=[0, 0, 0]), 0.4),
    ('close-rab4-alongx', 'Rabbit along the x-axis, ray step 0.4', RAB, 40, dict(yaw=0.0, pitch=0.0, dist=4.6, target=[0, 0, 0]), 0.4),
    ('close-rab4-pinch', 'Where three bodies meet, ray step 0.4', RAB, 60, dict(yaw=-1.571, pitch=0.9, dist=0.7, target=[-0.276, 0.48, 0]), 0.4),
]


def close():
    return [step(n, dict(id='windsq', c=c, it=it, cam=cam, stepk=k)) for n, _, c, it, cam, k in CLOSE]


if __name__ == '__main__':
    name = sys.argv[1]
    steps = [run.UP] + {'sheet': sheet, 'close': close}[name]() + [END]
    code, text, vals = run.shot(run.PAGE, steps, 'pics-%s-steps' % name)
    run.write('pics-%s.log' % name, text)
    print(text[-2500:])
    sys.exit(code)

"""Round 22, entry: run the distance-estimate test (see detest.js) one picture set per step, so that no step is long.
  python out/r22/entry/detest_run.py [ids ...]   -> detest.log.json (or detest-<ids>.log.json), then run detest.py"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import run
ids = sys.argv[1:] or ['alongonce', 'pulledplane']
SCENES = [['bas', 'j', [-1, 0, 0], 40], ['rab', 'j', [-0.122561, 0.744862, 0], 40], ['man', 'm', [-1, 0, 0], 30], ['sie', 'j', [-0.390541, -0.586788, 0], 40], ['sm', 'j', [-0.75, 0, 0], 40]]
BODY = """
const PX = 48, PY = 36, out = {}, id = %s, [tag, mode, c, iter] = %s;
$('ap-' + id).click(); await sleep(250);
const a = L.APPROACHES[S.approach], cap = a.deMax;
for (const de of [0, 1, 3]) {
  a.deMax = de; S.q.de = de;
  S.mode = mode; S.eq = 'z^n + c'; S.z0 = '0'; S.n = 2; S.c = c.slice(); S.iter = iter; S.flat = false; S.cutOn = false; S.mosaic = false;
  L.resetCam(); if (mode === 'j') { L.cam.yaw = -1.9; L.cam.pitch = 0.3; L.cam.dist = 4.6; }
  go(); const t0 = performance.now(); await settle(); const ms = Math.round(performance.now() - t0);
  const w = $('stage').clientWidth, h = $('stage').clientHeight, b = L.basis(), picks = [];
  for (let j = 0; j < PY; j++) for (let i = 0; i < PX; i++) { const p = L.pick(w * (i + 0.5) / PX, h * (j + 0.5) / PY); picks.push(p ? [p[0], p[1], p[2]] : null); }
  out[id + ' ' + tag + ' ' + de] = { w, h, PX, PY, fov: S.view.fov, pos: [...b.pos], right: [...b.right], up: [...b.up], f: [...b.f], iter, mode, c, picks, ms };
}
a.deMax = cap; S.q.de = 3;
return JSON.stringify(out);
"""
steps = [run.UP] + [{'js': run.HEAD + BODY % (json.dumps(i), json.dumps(s)), 'timeout': 600} for i in ids for s in SCENES]
name = 'detest' if len(sys.argv) < 2 else 'detest-' + '-'.join(ids)
code, text, vals = run.shot(run.PAGE, steps, name + '-steps', '1400x950')
out = {}
for v in vals[1:]:
    out.update(json.loads(v))
json.dump(out, open(os.path.join(HERE, name + '.log.json'), 'w', encoding='utf-8'))
print(text[-400:], 'exit', code, len(out), 'pictures')

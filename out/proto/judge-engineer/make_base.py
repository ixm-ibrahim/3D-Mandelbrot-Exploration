"""Write shot.py step lists for the three baselines (same standard pictures as the prototypes, sine's framing)."""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
PRE = "const L = window.squaringLab, S = L.S, cam = L.cam, $ = id => document.getElementById(id); const type = (id, v) => { const e = $(id); e.value = v; e.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', bubbles: true })); }; "
INFO = " return JSON.stringify({ approach: L.APPROACHES[S.approach].id, par: S.param[L.APPROACHES[S.approach].id], mode: S.mode, n: S.n, iter: S.iter, c: S.c, flat: S.flat, cutOn: S.cutOn, cut: S.cut, cam: [cam.yaw, cam.pitch, cam.dist].map(x => +x.toFixed(3)) });"
SETUP = {
  'base-inflated': "$('ap-mercator').click(); type('par-mercator-planesNum', '1'); if (S.param.mercator.planes !== 1) throw new Error('planes not 1');",
  'base-folded': "$('ap-mercator').click(); if (S.param.mercator.planes !== 2) throw new Error('planes not 2');",
  'base-bulb': "$('ap-bulb').click(); S.n = 2; L.syncControls(); L.refresh(false);",
}
TOP = "cam.pitch = 1.5607; cam.yaw = -Math.PI / 2;"
STEPS = [
  ('m3d-default', "L.R.warmOn = false; $('qBal').click(); %(setup)s"),
  ('m3d-top', TOP),
  ('m3d-x', "cam.pitch = 0; cam.yaw = 0;"),
  ('m3d-y', "cam.pitch = 0; cam.yaw = Math.PI / 2;"),
  ('m3d-cut0', "L.resetCam(); cam.pitch = 50 * Math.PI / 180; S.cutOn = true; S.cut = 0;"),
  ('m3d-cut02', "S.cut = 0.2;"),
  ('m2d-z000', "S.cutOn = false; S.cut = 0; L.resetCam(); S.flat = true; S.v2.x = -0.5; S.v2.y = 0; S.v2.h = 3.2;"),
  ('m2d-z010', "S.cut = 0.1;"),
  ('m2d-z025', "S.cut = 0.25;"),
  ('m2d-z050', "S.cut = 0.5;"),
  ('j-bas-3d', "S.flat = false; S.cut = 0; L.syncControls(); $('mode-j').click(); S.c[0] = -1; S.c[1] = 0; S.c[2] = 0; %(setup_j)s L.resetCam();"),
  ('j-bas-top', TOP),
  ('j-bas-x', "cam.pitch = 0; cam.yaw = 0;"),
  ('j-bas-2d-z000', "L.resetCam(); S.flat = true; S.cut = 0; S.v2.x = 0; S.v2.y = 0; S.v2.h = 3.2;"),
  ('j-bas-2d-z020', "S.cut = 0.2;"),
  ('j-rab-3d', "S.flat = false; S.cut = 0; S.c[0] = -0.1226; S.c[1] = 0.7449; S.c[2] = 0; L.resetCam();"),
  ('m3d-n3', "S.c[0] = -1; S.c[1] = 0; S.c[2] = 0; $('mode-m').click(); S.n = 3; L.resetCam(); L.syncControls(); L.refresh(false);"),
  ('m3d-n8', "S.n = 8; L.syncControls(); L.refresh(false);"),
]
for name, setup in SETUP.items():
    # after switching to Julia mode make sure the approach parameters are still what the baseline says
    setup_j = "if (L.APPROACHES[S.approach].id === 'mercator' && S.param.mercator.planes !== %d) throw new Error('planes changed');" % (1 if name == 'base-inflated' else 2) if name != 'base-bulb' else ""
    acts = []
    for shot, js in STEPS:
        acts.append({"js": PRE + (js % {"setup": setup, "setup_j": setup_j}) + " L.syncControls(); L.touch();" + INFO,
                     "wait": "done", "timeout": 900, "shot": "out/proto/judge-engineer/%s/%s.png" % (name, shot), "clip": "#stage"})
    os.makedirs(os.path.join(HERE, name), exist_ok=True)
    json.dump(acts, open(os.path.join(HERE, name + '.json'), 'w', encoding='utf-8'), indent=1)
    print('wrote', name, len(acts))

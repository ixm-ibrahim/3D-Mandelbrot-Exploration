// Round 22, entry: which "Distance estimate" draws the two entries truthfully? The cap (deMax) is lifted here in the
// page, and the same 48 x 36 probes are taken with Rough (0), One neighbour (1) and Exact (3). detest.py compares the
// stops with the set worked point by point. (HEAD of run.py is in front of this.)
const RAB = [-0.122561, 0.744862, 0], BAS = [-1, 0, 0], PX = 48, PY = 36, out = {};
const SCENES = [['bas', 'j', BAS, 40], ['rab', 'j', RAB, 40], ['man', 'm', BAS, 30], ['sie', 'j', [-0.390541, -0.586788, 0], 40], ['sm', 'j', [-0.75, 0, 0], 40]];
const IDS = (window.detestIds || ['alongonce', 'pulledplane']);
for (const id of IDS) {
  $('ap-' + id).click(); await sleep(250);
  const a = L.APPROACHES[S.approach], cap = a.deMax;
  for (const [tag, mode, c, iter] of SCENES) {
    for (const de of [0, 1, 3]) {
      a.deMax = de; S.q.de = de;
      S.mode = mode; S.eq = 'z^n + c'; S.z0 = '0'; S.n = 2; S.c = c.slice(); S.iter = iter; S.flat = false; S.cutOn = false; S.mosaic = false;
      L.resetCam(); if (mode === 'j') { L.cam.yaw = -1.9; L.cam.pitch = 0.3; L.cam.dist = 4.6; }
      go(); const t0 = performance.now(); await settle(); const ms = Math.round(performance.now() - t0);
      const w = $('stage').clientWidth, h = $('stage').clientHeight, b = L.basis(), picks = [];
      for (let j = 0; j < PY; j++) for (let i = 0; i < PX; i++) { const p = L.pick(w * (i + 0.5) / PX, h * (j + 0.5) / PY); picks.push(p ? [p[0], p[1], p[2]] : null); }
      out[id + ' ' + tag + ' ' + de] = { w, h, PX, PY, fov: S.view.fov, pos: [...b.pos], right: [...b.right], up: [...b.up], f: [...b.f], iter, mode, c, picks, ms };
    }
  }
  a.deMax = cap;
}
S.q.de = 3;
$('resetAll').click(); await sleep(300);
return JSON.stringify(out);

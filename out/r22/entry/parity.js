// Round 22, entry: what the lab's two entries do, for out/r22/entry/parity.py to compare with the library (mem.py).
// (HEAD of run.py is in front of this.)  A: the rule in JavaScript (CARRY), orbit by orbit.  B: the shader, point by
// point, on level slices (sampleSlice: three neighbouring orbits run beside each point).  C: the 3D picture (Rough, no
// neighbours), probe by probe from one camera.
const RAB = [-0.122561, 0.744862, 0], BAS = [-1, 0, 0];
const out = { A: {}, B: {}, C: {} };
// ----- A
const frac = x => x - Math.floor(x), NA = 20000, STEPS = 40;
const pt = k => [3.6 * frac(k * 0.8191725133961645) - 1.8, 2.6 * frac(k * 0.6710436067037893) - 1.3, 2.6 * frac(k * 0.5497004779019703) - 1.3];
const stay = (id, v, c, q, steps, from0) => {
  const R = L.CARRY[id]; let st = R.start(q), z = from0 ? [0, 0, 0] : v, k = 0;
  for (; k < steps + (from0 ? 1 : 0); k++) {
    st = R.step(st, z, c, q); const w = R.pw(st, z, 2); z = [w[0] + c[0], w[1] + c[1], w[2] + c[2]];
    if (!(z[0] * z[0] + z[1] * z[1] + z[2] * z[2] < 36)) break;
  }
  return from0 ? Math.max(0, k - 1) : k;
};
for (const id of ['alongonce', 'pulledplane']) {
  const q = Object.fromEntries((L.APPROACHES.find(a => a.id === id).params || []).filter(s => s.key !== undefined).map(s => [s.key, s.def]));
  const o = out.A[id] = { bas: [], rab: [], man: [], man0: [] };
  for (let k = 1; k <= NA; k++) {
    const v = pt(k);
    o.bas.push(stay(id, v, BAS, q, STEPS)); o.rab.push(stay(id, v, RAB, q, STEPS));
    o.man.push(stay(id, v, v, q, STEPS)); o.man0.push(stay(id, v, v, q, STEPS, true));
  }
}
// ----- B and C
const NB = 200, PX = 48, PY = 36;
const SCENES = [
  ['bas', 'j', BAS, 40, [0, 0, 3.6], [0, 0.2, 0.45]],
  ['rab', 'j', RAB, 40, [0, 0, 3.6], [0, 0.2]],
  ['man', 'm', BAS, 30, [-0.7, 0, 2.8], [0, 0.2]],
];
for (const id of ['alongonce', 'pulledplane', 'mercator', 'turnalong']) {
  $('ap-' + id).click(); await sleep(250);
  if (apId() !== id) fail('could not choose ' + id);
  for (const [tag, mode, c, iter, box, zs] of SCENES) {
    S.mode = mode; S.eq = 'z^n + c'; S.z0 = '0'; S.n = 2; S.c = c.slice(); S.iter = iter; S.flat = false; S.cutOn = false; S.mosaic = false; S.q.de = 0;
    L.resetCam(); if (mode === 'j') { L.cam.yaw = -1.9; L.cam.pitch = 0.3; L.cam.dist = 4.6; }
    go(); await settle();
    if (id === 'alongonce' || id === 'pulledplane') {
      const snap = L.takeSnapshot();
      for (const z of zs) {
        const a = await L.sampleSlice(snap, box[0], box[1], box[2], z, NB);
        if (!a) fail('sampleSlice gave nothing for ' + id + ' ' + tag);
        let s = '';
        for (let i = 0; i < NB * NB; i++) { const d = a[4 * i + 3]; s += d < 0 ? '1' : d > 0 ? '0' : d === 0 ? '2' : '3'; }
        out.B[id + ' ' + tag + ' z=' + z] = { box, z, N: NB, iter, mode, c, mask: s };
      }
      L.releaseSnapshot(snap);
      go(); await settle();
    }
    const w = $('stage').clientWidth, h = $('stage').clientHeight, b = L.basis(), picks = [];
    for (let j = 0; j < PY; j++) for (let i = 0; i < PX; i++) { const p = L.pick(w * (i + 0.5) / PX, h * (j + 0.5) / PY); picks.push(p ? [p[0], p[1], p[2]] : null); }
    out.C[id + ' ' + tag] = { w, h, PX, PY, fov: S.view.fov, bound: S.view.bound, pos: [...b.pos], right: [...b.right], up: [...b.up], f: [...b.f], iter, mode, c, picks };
  }
}
S.q.de = 3;
$('resetAll').click(); await sleep(300);
return JSON.stringify(out);

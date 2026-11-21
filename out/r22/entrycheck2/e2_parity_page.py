"""Round 22, entrycheck second pass: the page part of MY parity test (other points, other c, other slices and other
cameras than the builder's and than the first checker's).
  A  the rule in JavaScript (L.CARRY, iterated here the way the shader's hooks use it) on 10,000 start points
  B  the shader point by point (L.sampleSlice) on level slices of 144 x 144
  C  the 3D picture: 36 x 27 probes (L.pick) per camera
  python out/r22/entrycheck2/e2_parity_page.py   -> parity.log, parity.log.json   (then e2_parity.py compares with the library)
"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import drv

DEFS = drv.HEAD + r"""
const CSET = { bas: [-1, 0, 0], rab: [-0.122561, 0.744862, 0], smk: [-0.75, 0, 0], air: [-1.754878, 0, 0], off: [-0.3, 0.4, -0.25] };
const out = window.__out || (window.__out = { A: {}, B: {}, C: {} });
const frac = x => x - Math.floor(x), NA = 10000;
const pt = k => [3.2 * frac(k * 0.6180339887498949) - 1.6, 2.4 * frac(k * 0.32471795724474603) - 1.2, 2.4 * frac(k * 0.7548776662466927) - 1.2];
const orbit = (id, v, c, q, steps, r2) => {
  const R = L.CARRY[id]; let st = R.start(q), z = v, k = 0;
  for (; k < steps; k++) {
    st = R.step(st, z, c, q);
    const w = R.pw(st, z, 2);
    z = [w[0] + c[0], w[1] + c[1], w[2] + c[2]];
    if (!(z[0] * z[0] + z[1] * z[1] + z[2] * z[2] < r2)) break;
  }
  return k;
};
const defs = id => Object.fromEntries((L.APPROACHES.find(a => a.id === id).params || []).filter(s => s.key !== undefined).map(s => [s.key, s.def]));
const NB = 144;
const mask = a => { let s = ''; for (let i = 0; i < NB * NB; i++) { const d = a[4 * i + 3]; s += d < 0 ? '1' : d > 0 ? '0' : d === 0 ? '2' : '3'; } return s; };
const slice = async (box, z) => { const snap = L.takeSnapshot(); const a = await L.sampleSlice(snap, box[0], box[1], box[2], z, NB); L.releaseSnapshot(snap); if (!a) fail('sampleSlice gave nothing'); return mask(a); };
const setup = async (id, mode, c, iter) => {
  $('ap-' + id).click(); await sleep(250); if (apId() !== id) fail('could not choose ' + id);
  S.mode = mode; S.eq = 'z^n + c'; S.z0 = '0'; S.n = 2; S.c = c.slice(); S.iter = iter; S.flat = false; S.cutOn = false; S.mosaic = false; S.abs = [0, 0, 0]; S.flip = [0, 0];
  if (S.param.pulledplane) Object.assign(S.param.pulledplane, defs('pulledplane'));
  L.resetCam(); go(); await settle();
};
"""
SL = [('rab', 'j', 34, [0, 0, 3.0], [0, -0.18]),
      ('smk', 'j', 34, [0, 0, 3.2], [0, 0.22]),
      ('air', 'j', 34, [0, 0, 4.0], [0, 0.12]),
      ('off', 'j', 34, [0, 0, 3.0], [0.05]),
      ('man', 'm', 26, [-0.5, 0, 2.8], [0, -0.15])]
CS = [('bas', 'j', 34, "L.cam.yaw = 2.4; L.cam.pitch = 0.5; L.cam.dist = 4.6; L.cam.target = [0, 0, 0];"),
      ('rab', 'j', 34, "L.cam.yaw = -0.9; L.cam.pitch = -0.6; L.cam.dist = 4.4; L.cam.target = [0, 0, 0];"),
      ('man', 'm', 26, "L.cam.yaw = 0.5; L.cam.pitch = 0.9; L.cam.dist = 5.0; L.cam.target = [-0.6, 0, 0];")]

steps = [drv.UP]
steps.append({'js': DEFS + """
for (const [id, q] of [['alongonce', {}], ['pulledplane', defs('pulledplane')]]) {
  const o = out.A[id] = { bas: [], rab: [], smk: [], off: [], man: [] };
  for (let k = 1; k <= NA; k++) {
    const v = pt(k);
    for (const t of ['bas', 'rab', 'smk', 'off']) o[t].push(orbit(id, v, CSET[t], q, 50, 36));
    o.man.push(orbit(id, v, v, q, 50, 36));
  }
}
return 'A done';"""})
for id_ in ('alongonce', 'pulledplane'):
    for tag, mode, it, box, zs in SL:
        c = 'CSET.%s' % ('bas' if tag == 'man' else tag)
        steps.append({'js': DEFS + """
await setup('%s', '%s', %s, %d);
for (const z of %s) out.B['%s %s z=' + z] = { id: '%s', box: %s, z, N: NB, iter: %d, mode: '%s', c: %s, mask: await slice(%s, z) };
return 'B %s %s';""" % (id_, mode, c, it, json.dumps(zs), id_, tag, id_, json.dumps(box), it, mode, c, json.dumps(box), id_, tag)})
for id_ in ('alongonce', 'pulledplane'):
    for tag, mode, it, cam in CS:
        c = 'CSET.%s' % ('bas' if tag == 'man' else tag)
        steps.append({'js': DEFS + """
await setup('%s', '%s', %s, %d);
%s go(); await settle();
const PX = 36, PY = 27, w = $('stage').clientWidth, h = $('stage').clientHeight, b = L.basis(), picks = [];
for (let j = 0; j < PY; j++) for (let i = 0; i < PX; i++) { const p = L.pick(w * (i + 0.5) / PX, h * (j + 0.5) / PY); picks.push(p ? [p[0], p[1], p[2]] : null); }
out.C['%s %s'] = { id: '%s', w, h, PX, PY, fov: S.view.fov, pos: [...b.pos], right: [...b.right], up: [...b.up], f: [...b.f], iter: %d, mode: '%s', c: %s, de: S.q && S.q.de, picks };
return 'C %s %s: ' + picks.filter(p => p).length + ' stops';""" % (id_, mode, c, it, cam, id_, tag, id_, it, mode, c, id_, tag),
                      'shot': 'out/r22/entrycheck2/parity-%s-%s.png' % (id_, tag), 'clip': '#stage'})
steps.append({'js': "return JSON.stringify(window.__out);"})
for s in steps[1:]:
    s.setdefault('timeout', 600)
code, text, vals = drv.shot(drv.PAGE, steps, 'parity-steps', '1400x950')
drv.write('parity.log', text + 'exit %d\n' % code)
if vals:
    v = vals[-1]
    drv.write('parity.log.json', v if isinstance(v, str) else json.dumps(v))
print(text[-3000:]); print('exit', code)
sys.exit(code)

"""Round 22, entrycheck: the page part of the parity test, cut into steps (one step of shot.py may not take 120 s).
What each piece does is described in ec_parity.js (the first, one-piece version, which timed out); the pieces are the same.
  python out/r22/entrycheck/ec_parity_page.py -> parity.log, parity.log.json
"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import drive

DEFS = drive.HEAD + r"""
const SIE = [-0.390541, -0.586788, 0], BAS = [-1, 0, 0], OFF = [-0.6, 0.2, 0.15];
const out = window.__out || (window.__out = { A: {}, B: {}, BJ: {}, C: {} });
const frac = x => x - Math.floor(x), NA = 12000;
const pt = k => [3.4 * frac(k * 0.41421356237309515) - 1.7, 2.6 * frac(k * 0.7320508075688772) - 1.3, 2.6 * frac(k * 0.2360679774997898) - 1.3];
// one orbit with the page's rule, the way the shader's hooks use it: one step() before the powers of a step
const orbit = (id, v, c, q, steps, r2, F, abs) => {
  const R = L.CARRY[id]; let st = R.start(q), z = v, k = 0;
  for (; k < steps; k++) {
    if (abs) z = [Math.abs(z[0]), Math.abs(z[1]), Math.abs(z[2])];
    st = R.step(st, z, c, q);
    const w = F ? F(R, st, z) : R.pw(st, z, 2);
    z = [w[0] + c[0], w[1] + c[1], w[2] + c[2]];
    if (!(z[0] * z[0] + z[1] * z[1] + z[2] * z[2] < r2)) break;
  }
  return k;
};
const defs = id => Object.fromEntries((L.APPROACHES.find(a => a.id === id).params || []).filter(s => s.key !== undefined).map(s => [s.key, s.def]));
const MOVED = { hold: 0.2, ease: 0.4, cpull: 5 };
const NB = 160;
const mask = a => { let s = ''; for (let i = 0; i < NB * NB; i++) { const d = a[4 * i + 3]; s += d < 0 ? '1' : d > 0 ? '0' : d === 0 ? '2' : '3'; } return s; };
const slice = async (box, z) => { const snap = L.takeSnapshot(); const a = await L.sampleSlice(snap, box[0], box[1], box[2], z, NB); L.releaseSnapshot(snap); if (!a) fail('sampleSlice gave nothing'); return mask(a); };
const setup = async (id, mode, c, iter, extra) => {
  $('ap-' + id).click(); await sleep(250); if (apId() !== id) fail('could not choose ' + id);
  S.mode = mode; S.eq = 'z^n + c'; S.z0 = '0'; S.n = 2; S.c = c.slice(); S.iter = iter; S.flat = false; S.cutOn = false; S.mosaic = false; S.abs = [0, 0, 0]; S.flip = [0, 0]; S.q.de = 0;
  if (S.param.pulledplane) Object.assign(S.param.pulledplane, defs('pulledplane'));
  if (extra) extra();
  L.resetCam(); go(); await settle();
};
const jsMask = (id, q, c, iter, box, z, F, abs) => {
  let s = '';
  for (let j = 0; j < NB; j++) for (let i = 0; i < NB; i++) {
    const v = [box[0] + box[2] * ((i + 0.5) / NB - 0.5), box[1] + box[2] * ((j + 0.5) / NB - 0.5), z];
    s += orbit(id, v, c, q, iter, 4096, F, abs) >= iter ? '1' : '0';
  }
  return s;
};
const add3 = (a, b) => [a[0] + b[0], a[1] + b[1], a[2] + b[2]];
"""
C = {'sie': 'SIE', 'off': 'OFF', 'bas': 'BAS'}
SL = [('sie', 'j', 'SIE', 36, [0, 0, 3.2], [0, 0.1, -0.27]),
      ('off', 'j', 'OFF', 36, [0, 0, 3.2], [0, 0.33]),
      ('bas', 'j', 'BAS', 36, [0, 0, 3.4], [0, 0.31]),
      ('man', 'm', 'BAS', 28, [-0.6, 0, 2.8], [0, 0.1, -0.33])]
MOVED = [('off', 'j', 'OFF', 36, [0, 0, 3.2], [0.1]), ('bas', 'j', 'BAS', 36, [0, 0, 3.4], [0.31]), ('man', 'm', 'BAS', 28, [-0.6, 0, 2.8], [0.1])]
VAR = [('power 3', '[0.3, 0, 0]', 30, [0, 0, 2.6], 0.17, "S.n = 3;", "(R, st, z) => R.pw(st, z, 3)", 'false'),
       ('power 3 c off', '[0.2, 0.25, 0.1]', 30, [0, 0, 2.6], 0.17, "S.n = 3;", "(R, st, z) => R.pw(st, z, 3)", 'false'),
       ('z^2 + z^3 + c', '[-0.2, 0, 0]', 30, [-0.3, 0, 2.6], 0.17, "S.eq = 'z^2 + z^3 + c';", "(R, st, z) => add3(R.pw(st, z, 2), R.pw(st, z, 3))", 'false'),
       ('z^2 + z^3 + c, c off', '[-0.25, 0.1, 0.12]', 30, [-0.3, 0, 2.6], 0.17, "S.eq = 'z^2 + z^3 + c';", "(R, st, z) => add3(R.pw(st, z, 2), R.pw(st, z, 3))", 'false'),
       ('|x||y||z|', '[-1, 0, 0]', 30, [0, 0, 3.4], 0.2, "S.abs = [1, 1, 1];", "null", 'true')]
CS = [('sie', 'j', 'SIE', 36, "L.cam.yaw = 0.7; L.cam.pitch = -0.4; L.cam.dist = 4.4; L.cam.target = [0, 0, 0];"),
      ('bas', 'j', 'BAS', 36, "L.cam.yaw = 0.7; L.cam.pitch = -0.4; L.cam.dist = 4.8; L.cam.target = [0, 0, 0];"),
      ('off', 'j', 'OFF', 36, "L.cam.yaw = 2.2; L.cam.pitch = 0.6; L.cam.dist = 4.4; L.cam.target = [0, 0, 0];"),
      ('man', 'm', 'BAS', 28, "L.cam.yaw = -1.0; L.cam.pitch = 0.55; L.cam.dist = 5.2; L.cam.target = [-0.6, 0, 0];"),
      ('man2', 'm', 'BAS', 28, "L.cam.yaw = 1.9; L.cam.pitch = -0.35; L.cam.dist = 4.6; L.cam.target = [-0.6, 0, 0];")]

steps = [drive.UP]
steps.append({'js': DEFS + """
for (const [key, id, q] of [['alongonce', 'alongonce', {}], ['pulledplane', 'pulledplane', defs('pulledplane')], ['pulledplane moved', 'pulledplane', MOVED]]) {
  const o = out.A[key] = { bas: [], sie: [], off: [], man: [] };
  for (let k = 1; k <= NA; k++) {
    const v = pt(k);
    o.bas.push(orbit(id, v, BAS, q, 60, 36)); o.sie.push(orbit(id, v, SIE, q, 60, 36)); o.off.push(orbit(id, v, OFF, q, 60, 36)); o.man.push(orbit(id, v, v, q, 60, 36));
  }
}
return 'A done';"""})
for id_ in ('alongonce', 'pulledplane'):
    for tag, mode, c, it, box, zs in SL:
        steps.append({'js': DEFS + """
await setup('%s', '%s', %s, %d);
for (const z of %s) out.B['%s %s z=' + z] = { id: '%s', box: %s, z, N: NB, iter: %d, mode: '%s', c: %s, mask: await slice(%s, z) };
return 'B %s %s';""" % (id_, mode, c, it, json.dumps(zs), id_, tag, id_, json.dumps(box), it, mode, c, json.dumps(box), id_, tag)})
for tag, mode, c, it, box, zs in MOVED:
    steps.append({'js': DEFS + """
await setup('pulledplane', '%s', %s, %d, () => Object.assign(S.param.pulledplane, MOVED));
for (const z of %s) out.B['pulledplane-moved %s z=' + z] = { id: 'pulledplane', box: %s, z, N: NB, iter: %d, mode: '%s', c: %s, mask: await slice(%s, z) };
Object.assign(S.param.pulledplane, defs('pulledplane'));
return 'B moved %s';""" % (mode, c, it, json.dumps(zs), tag, json.dumps(box), it, mode, c, json.dumps(box), tag)})
for id_ in ('alongonce', 'pulledplane'):
    for tag, c, it, box, z, extra, F, ab in VAR:
        steps.append({'js': DEFS + """
await setup('%s', 'j', %s, %d, () => { %s });
out.BJ['%s %s'] = { box: %s, z: %g, N: NB, iter: %d, c: %s, lab: await slice(%s, %g), js: jsMask('%s', %s, %s, %d, %s, %g, %s, %s) };
return 'BJ %s %s';""" % (id_, c, it, extra, id_, tag, json.dumps(box), z, it, c, json.dumps(box), z, id_, "defs('pulledplane')" if id_ == 'pulledplane' else '{}', c, it, json.dumps(box), z, F, ab, id_, tag)})
for id_ in ('alongonce', 'pulledplane', 'mercator'):
    for tag, mode, c, it, cam in CS:
        steps.append({'js': DEFS + """
await setup('%s', '%s', %s, %d);
%s go(); await settle();
const PX = 40, PY = 30, w = $('stage').clientWidth, h = $('stage').clientHeight, b = L.basis(), picks = [];
for (let j = 0; j < PY; j++) for (let i = 0; i < PX; i++) { const p = L.pick(w * (i + 0.5) / PX, h * (j + 0.5) / PY); picks.push(p ? [p[0], p[1], p[2]] : null); }
out.C['%s %s'] = { id: '%s', w, h, PX, PY, fov: S.view.fov, pos: [...b.pos], right: [...b.right], up: [...b.up], f: [...b.f], iter: %d, mode: '%s', c: %s, picks };
return 'C %s %s: ' + picks.filter(p => p).length + ' stops';""" % (id_, mode, c, it, cam, id_, tag, id_, it, mode, c, id_, tag)})
steps.append({'js': "return JSON.stringify(window.__out);"})
for s in steps[1:]:
    s.setdefault('timeout', 600)
code, text, vals = drive.shot(drive.PAGE, steps, 'parity-steps', '1400x950')
drive.write('parity.log', text + 'exit %d\n' % code)
if vals:
    v = vals[-1]
    drive.write('parity.log.json', v if isinstance(v, str) else json.dumps(v))
print(text[-3500:]); print('exit', code)
sys.exit(code)

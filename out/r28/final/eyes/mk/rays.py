"""The eyes, section 1.4 c: the browser half. For each view (mk/views.py) the dials are set by typing, the picture
is drawn and saved, and pick() is asked at every 4th pixel of every 4th row (the pixel centres i + 0.5 with
i = 0, 4, 8, ...: other rays than the builder's and round 27's, which start at 2). What comes back is kept in
rays/<tag>-<view>.json: where every ray stopped (its length from the eye, 0 = stopped nowhere), and for every stop
the page's own distance to the nearest ball its search meets (300 rounds), in pixels. The other half, mk/walk.py,
walks the same rays with my own numpy recipe and compares.

  python out/r28/final/eyes/mk/rays.py <tag> <size> <theme> <view> [view ...]
      -> shots/<tag>-<view>.png, rays/<tag>-<view>.json, logs/rays-<tag>-<first view>.log
(The picks of a view are spread over steps of about 30 s, because tools/shot.py gives one step 120 s.)
"""
import json, os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import eyerun as run
import views

STEP, BANDS, BAND_MS = 4, 20, 30000

SETUP = run.HEAD + """
const NAME = %s, g = %d, P = %s, RHO = %s, rounds = %d, c = %s, flat = %s, STEP = %d;
for (const e of $('stage').children) e.style.visibility = '';
if (!(S.mode === 'k' && S.k.group === 1)) { $('ap-balls').click(); await settle(); }
if (S.flat) { $('flat').click(); await sleep(120); }
// (the button "Reset this section" lies INSIDE the element ballsReset. My first runs clicked the element itself, which
//  does nothing, so there a view began from the dials of the view before it: logs/reset-slip.txt lists what each of
//  those views really showed. The walk always uses the numbers the page held, so those results stand for what was shown.)
document.querySelector('#ballsReset button').click(); await sleep(200);
const afterReset = { bt: S.k.bt, brho: S.k.brho, bgrid: S.k.bgrid, bit: S.k.bit };
if (Math.abs(S.k.bt - 1.4) > 1e-12 || S.k.brho !== 1 || S.k.bgrid !== 0 || S.k.bit !== 16) fail('Reset this section left ' + JSON.stringify(afterReset));
await type('ballsSize', P);
if (RHO !== null) await type('ballsRho', RHO);
{ const sel = $('ballsGrid'); sel.value = String(g); sel.dispatchEvent(new Event('change', { bubbles: true })); await sleep(60); }
await type('ballsDepth', rounds);
if (flat) { $('flat').click(); await sleep(120); }
$('ballsFrame').click(); await sleep(150);
const framed = { cam: [L.cam.yaw, L.cam.pitch, L.cam.dist, L.cam.target.slice()], v2: Object.assign({}, S.v2), bound: S.view.bound, zmax: S.view.zmax };
if (c && !flat) { L.cam.yaw = c[0]; L.cam.pitch = c[1]; L.cam.dist = c[2]; L.cam.target = c[3].slice(); go(); }
if (c && flat) { S.v2.x = c[0]; S.v2.y = c[1]; S.v2.h = c[2]; go(); }
const t0 = performance.now();
await settle();
const drawMs = Math.round(performance.now() - t0);
const boxes = { size: $('ballsSizeNum').value, rho: $('ballsRhoNum').value, depth: $('ballsDepthNum').value, grid: $('ballsGrid').value, flat: $('flat').checked };
const warnText = warn(), status = $('status').textContent;
for (const e of $('stage').children) if (e.id !== 'view') e.style.visibility = 'hidden';
const w = $('stage').clientWidth, h = $('stage').clientHeight, b = L.basis(), fov = S.view.fov, ro = b.pos, pix = 2 * fov / h, bound = S.view.bound;
const t = S.k.bt, rho = S.k.brho, grid = S.k.bgrid;
const nx = Math.ceil(w / STEP), ny = Math.ceil(h / STEP);
const ray = (px, py) => { const ux = (2 * px - w) / h * fov, uy = (2 * (h - py) - h) / h * fov;
  const rd = [0, 1, 2].map(k => b.right[k] * ux + b.up[k] * uy + b.f[k]), n = Math.hypot(rd[0], rd[1], rd[2]); return rd.map(x => x / n); };
const o300 = { t, grid, rounds: 300, rho, parts: true };
const E = window.__E = { name: NAME, row: 0, ny, nx, depth: new Float32Array(nx * ny), met: new Float32Array(nx * ny), offRay: 0, picks: 0, stops: 0, ms: 0,
  meta: { name: NAME, asked: { grid: g, p: P, rho: RHO, depth: rounds, cam: c, flat }, afterReset, framed, boxes, warn: warnText, status, drawMs, w, h, fov, bound, pix, STEP, nx, ny,
    k: { bt: t, brho: rho, bgrid: grid, bit: S.k.bit, group: S.k.group }, flat: S.flat, cut: S.cut, v2: Object.assign({}, S.v2), cam: [L.cam.yaw, L.cam.pitch, L.cam.dist, L.cam.target.slice()],
    ro, right: b.right, up: b.up, f: b.f, sig: String(L.R.sig), canvas: [$('view').width, $('view').height], q: Object.assign({}, S.q), theme: getComputedStyle(document.body).backgroundColor,
    reach: L.ballsReach(), eyeEst300: flat ? null : L.ballsEstimate(ro[0], ro[1], ro[2], { t, grid, rounds: 300, rho }), eyeInside300: flat ? null : L.ballsInside(ro[0], ro[1], ro[2], { t, grid, rounds: 300, rho }) } };
E.band = ms => { const t1 = performance.now();
  if (flat) { E.row = ny; return 'flat: no rays'; }
  while (E.row < ny && performance.now() - t1 < ms) { const py = E.row * STEP + 0.5;
    for (let ii = 0; ii < nx; ii++) { const px = ii * STEP + 0.5, p = L.pick(px, py); E.picks++;
      if (!p) continue;
      E.stops++;
      const v = [p[0] - ro[0], p[1] - ro[1], p[2] - ro[2]], sd = Math.hypot(v[0], v[1], v[2]), one = pix * sd, rd = ray(px, py);
      const along = v[0] * rd[0] + v[1] * rd[1] + v[2] * rd[2], off = Math.sqrt(Math.max(0, sd * sd - along * along)) / one; if (off > E.offRay) E.offRay = off;
      E.depth[E.row * nx + ii] = sd;
      E.met[E.row * nx + ii] = L.ballsEstimate(p[0], p[1], p[2], o300)[0] / one;
    }
    E.row++; }
  E.ms += performance.now() - t1;
  return 'rows ' + E.row + ' of ' + ny; };
E.b64 = a => { const u = new Uint8Array(a.buffer); let s = ''; for (let i = 0; i < u.length; i += 8192) s += String.fromCharCode.apply(null, u.subarray(i, i + 8192)); return btoa(s); };
E.finish = () => { const m = E.meta; m.rowsDone = E.row; m.picks = E.picks; m.stops = E.stops; m.offRayPx = E.offRay; m.pickMs = Math.round(E.ms);
  return JSON.stringify({ meta: m, depth: flat ? '' : E.b64(E.depth), met: flat ? '' : E.b64(E.met) }); };
return 'set ' + NAME + ': ' + status + ' | t ' + t + ' rho ' + rho + ' grid ' + grid + ' depth ' + S.k.bit + ' | boxes ' + JSON.stringify(boxes) + ' | ' + warnText;
"""


def steps_for(names, tag):
    steps = [run.UP]
    for name in names:
        v = views.V[name]
        if v['cam'] is None:
            c = 'null'
        elif v['flat']:
            c = json.dumps(list(v['cam']))
        else:
            c = json.dumps(views.cam_numbers(v))
        js = SETUP % (json.dumps(name), v['grid'], json.dumps(str(v['p'])), 'null' if v['rho'] is None else json.dumps(str(v['rho'])), v['depth'], c, 'true' if v['flat'] else 'false', STEP)
        steps.append({'js': js, 'wait': 'done', 'timeout': 900, 'shot': '%s/shots/%s-%s.png' % (run.OUT, tag, name), 'clip': '#view'})
        if not v['flat']:
            for k in range(BANDS):
                steps.append({'js': "return window.__E.band(%d);" % BAND_MS})
        else:
            steps.append({'js': "return window.__E.band(1);"})
        steps.append({'js': "return window.__E.finish();"})
    return steps


if __name__ == '__main__':
    tag, size, theme = sys.argv[1:4]
    names = sys.argv[4:]
    os.makedirs(os.path.join(run.EYES, 'shots'), exist_ok=True); os.makedirs(os.path.join(run.EYES, 'rays'), exist_ok=True)
    t0 = time.time()
    code, text, vals = run.shot(run.PAGE, steps_for(names, tag), 'rays-%s-%s' % (tag, names[0]), size, theme)
    run.write('rays-%s-%s.log' % (tag, names[0]), text + 'exit %d, %.0f s\n' % (code, time.time() - t0))
    got = 0
    for v in vals:
        if v.startswith('{"meta"'):
            d = json.loads(v)
            with open(os.path.join(run.EYES, 'rays', '%s-%s.json' % (tag, d['meta']['name'])), 'w', encoding='utf-8') as f:
                f.write(v)
            m = d['meta']; got += 1
            print('%s: t %.6f rho %.6f grid %d depth %d | boxes %s | %s | drawn in %d ms | picks %d, stops %d, rows %d of %d, %d ms | eye inside %s | %s'
                  % (m['name'], m['k']['bt'], m['k']['brho'], m['k']['bgrid'], m['k']['bit'], json.dumps(m['boxes']), m['status'], m['drawMs'], m['picks'], m['stops'], m['rowsDone'], m['ny'], m['pickMs'], m['eyeInside300'], m['warn']))
    print('exit %d, %s, %d of %d views back, %.0f s' % (code, 'no console errors' if run.clean(text) else 'SEE THE LOG', got, len(names), time.time() - t0))
    if code != 0:
        print(text[-3000:])

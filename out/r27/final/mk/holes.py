"""Round 27, final: defects A1 (holes with the neighbours at 100 %) and S (stops in the open), on dist/r27-final.html.

For each view: the dials and the camera are set, the picture is drawn and saved, and pick() is asked at every 4th
pixel of every 4th row (the grid moved by two pixels against the fixer's, so these are other rays).
  A ray that stops nowhere is walked with the exact inside test (the recipe of ROUND27.md section 1 written out here,
  300 rounds, inside only when a wall is reached) in quarter-pixel steps out to the Drawing radius (all such rays up
  to 400 a view, chosen at random beyond that). Through a ball for more than 2 pixels = a hole.
  For a ray that stops: the exact distance from the stopping point to the nearest ball the search meets from there
  (first number of ballsEstimate with parts, 300 rounds), in pixels at that depth. Further than 2 px = a stop in the
  open, unless a point within 3 px ahead on the ray is solid only because the page's depth leaves it undecided.
Self-check of my ray geometry: for every stop, how far (in pixels) the stopping point lies from my ray.
(The picks of a view are spread over six steps, because tools/shot.py gives one step 120 s.)

  python out/r27/final/mk/holes.py [view ...]   -> logs/holes.txt (or holes-<view>.txt), shots/holes-<view>.png
"""
import json, os, sys
import numpy as np
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import run

KISS = [0.525, 0, 0]
VIEWS = {                       # grid, t, depth, camera (yaw, pitch, dist, target) or None for the start view
    't1-kiss-r16': (0, 1.0, 16, (-1.25, 0.5, 0.30, KISS)),            # the checker's view of A1
    't1-kiss-r40': (0, 1.0, 40, (-1.25, 0.5, 0.30, KISS)),
    't1-line-kiss-r16': (2, 1.0, 16, (-1.25, 0.5, 0.30, KISS)),
    't1-hex-kiss-r16': (1, 1.0, 16, (-1.25, 0.5, 0.30, KISS)),
    't1-own-eye-r16': (0, 1.0, 16, (1.9, 0.9, 0.30, KISS)),           # my own eye, not tried by anyone before: a ball within about 0.001 of it
    't1-own-eye2-r16': (0, 1.0, 16, (1.3, 1.1, 0.35, KISS)),          # my own second eye: no ball within about 0.02
    't1-inside-a-ball': (0, 1.0, 16, (2.0, -0.3, 0.25, KISS)),        # (my first try: this eye stands INSIDE the middle ball; kept to show what the page does then)
    't1-own-far-r16': (0, 1.0, 16, (0.6, 0.25, 1.2, [0.9, 0, 0])),    # my own, along the bar
    't1003-kiss-r16': (0, 1.003, 16, (-1.25, 0.5, 0.30, KISS)),       # between 99 % and 100 %
    't1-start-r16': (0, 1.0, 16, None),
    't105-kiss-r16': (0, 1.05, 16, (-1.25, 0.5, 0.30, KISS)),
    'kiss-eyeB-r16': (0, 1.4, 16, (1.5708, -0.6, 0.20, KISS)),        # the checker's view of S
    'kiss-own-eye-r16': (0, 1.4, 16, (-1.0, -0.7, 0.35, KISS)),       # my own eye at the starting size
    'inside-a-ball': (0, 1.4, 16, (0.2, 0.1, 0.25, KISS)),            # (my first try: this eye stands INSIDE the neighbour)
    'start-r16': (0, 1.4, 16, None),
    'hex-start-r16': (1, 1.4, 16, None),                              # third pass: the other two grids and small neighbours
    'line-start-r16': (2, 1.4, 16, None),
    'hex-own-eye-r16': (1, 1.4, 16, (-1.0, -0.7, 0.35, KISS)),
    't25-start-r16': (0, 2.5, 16, None),
    't105-hex-kiss-r16': (1, 1.05, 16, (-1.25, 0.5, 0.30, KISS)),     # (with the honeycomb grid this eye, the checker's, stands INSIDE a ball)
    't1-hex-own-eye-r16': (1, 1.0, 16, (1.3, 1.1, 0.35, KISS)),       # fourth pass: honeycomb close-ups with the eye outside every ball
    't1-hex-own-eye2-r16': (1, 1.0, 16, (1.9, 0.9, 0.30, KISS)),
    't105-hex-own-eye-r16': (1, 1.05, 16, (1.5708, 0.6, 0.2, KISS)),
}
DEFAULT = ['t1-kiss-r16', 't1-kiss-r40', 't1-line-kiss-r16', 't1-own-eye-r16', 't1-own-far-r16', 't1003-kiss-r16', 't1-start-r16', 't105-kiss-r16', 'kiss-eyeB-r16', 'kiss-own-eye-r16', 'start-r16']
STEP, RAYS, BANDS = 4, 400, 6

SETUP = run.HEAD + """
const g = %d, t = %r, rounds = %d, c = %s, STEP = %d, RAYS = %d;
for (const e of $('stage').children) e.style.visibility = '';
if (!(S.mode === 'k' && S.k.group === 1)) { $('ap-balls').click(); await settle(); }
S.k.bt = t; S.k.bgrid = g; S.k.bit = rounds; S.flat = false; S.cutOn = false;
L.ballsFrame();
if (c) { L.cam.yaw = c[0]; L.cam.pitch = c[1]; L.cam.dist = c[2]; L.cam.target = c[3].slice(); }
go(); await settle();
for (const e of $('stage').children) if (e.id !== 'view') e.style.visibility = 'hidden';
const S3 = Math.sqrt(3), K2 = 1.05, top = 2 * t;
// the slide: the nearest whole number of the grid
const near = (x, y) => { if (g === 2) return [Math.round(x), 0]; if (g === 0) return [Math.round(x), Math.round(y)];
  let best = null, bd = Infinity; const b0 = Math.round(y / (S3 / 2)), a0 = Math.round(x + b0 / 2);
  for (let db = -1; db <= 1; db++) for (let da = -1; da <= 1; da++) { const b = b0 + db, a = a0 + da, px = a - b / 2, py = b * S3 / 2, d = (x - px) * (x - px) + (y - py) * (y - py); if (d < bd) { bd = d; best = [px, py]; } }
  return best; };
// the recipe: 1 = a wall was reached (inside a ball), 0 = outside, 2 = undecided after 300 rounds
const sure = (x, y, z) => { const ux = y, uy = z, uz = x - K2 / 2; let d = ux * ux + uy * uy + uz * uz; if (!(d > 0)) d = 1e-300;
  let mx = K2 * ux / d, my = K2 * uy / d, mz = 1 + K2 * uz / d;
  for (let i = 0; i < 300; i++) { if (mz < 0 || mz > top) return 1; const n = near(mx, my); mx -= n[0]; my -= n[1];
    const rb = mx * mx + my * my + mz * mz, rt = mx * mx + my * my + (mz - top) * (mz - top);
    if (rb < 1) { mx /= rb; my /= rb; mz /= rb; } else if (rt < 1) { mx /= rt; my /= rt; mz = top + (mz - top) / rt; } else return 0; }
  return 2; };
const w = $('stage').clientWidth, h = $('stage').clientHeight, b = L.basis(), fov = S.view.fov, ro = b.pos, pix = 2 * fov / h, bound = S.view.bound;
const ray = (px, py) => { const ux = (2 * px - w) / h * fov, uy = (2 * (h - py) - h) / h * fov;
  const rd = [0, 1, 2].map(k => b.right[k] * ux + b.up[k] * uy + b.f[k]), n = Math.hypot(rd[0], rd[1], rd[2]); return rd.map(x => x / n); };
const o300 = { t, grid: g, rounds: 300, parts: true }, deep = { t, grid: g, rounds: 3000 }, own = { t, grid: g, rounds };
const A = { miss: [], picks: 0, stops: 0, offRay: 0, over13: 0, over2: 0, byDepth: 0, open: 0, openNearABall: 0, openNothing: 0, worstNothing: 0, worstOpen: 0, worst: 0 };
const eyeIn = sure(ro[0], ro[1], ro[2]), eyeEst = L.ballsEstimate(ro[0], ro[1], ro[2], { t, grid: g, rounds: 300 });
const dirs = []; for (let a = -1; a <= 1; a++) for (let bq = -1; bq <= 1; bq++) for (let cq = -1; cq <= 1; cq++) if (a || bq || cq) { const n = Math.hypot(a, bq, cq); dirs.push([a / n, bq / n, cq / n]); }
const band = (j0, j1) => { for (let j = 2; j < h; j += STEP) { if (j < j0 || j >= j1) continue; for (let i = 2; i < w; i += STEP) {
  A.picks++;
  const px = i + 0.5, py = j + 0.5, p = L.pick(px, py);
  if (!p) { A.miss.push([px, py]); continue; }
  A.stops++;
  const v = [p[0] - ro[0], p[1] - ro[1], p[2] - ro[2]], sd = Math.hypot(v[0], v[1], v[2]), one = pix * sd, rd = ray(px, py);
  const along = v[0] * rd[0] + v[1] * rd[1] + v[2] * rd[2], off = Math.sqrt(Math.max(0, sd * sd - along * along)) / one; if (off > A.offRay) A.offRay = off;
  const met = L.ballsEstimate(p[0], p[1], p[2], o300)[0] / one;
  if (met > A.worst) A.worst = met;
  if (met > 1.3) A.over13++;
  if (!(met > 2)) continue;
  A.over2++;
  let dep = false;
  for (let k = 0; k <= 3 && !dep; k += 0.25) { const q = [p[0] + k * one * rd[0], p[1] + k * one * rd[1], p[2] + k * one * rd[2]]; if (L.ballsInside(q[0], q[1], q[2], own) && !L.ballsInside(q[0], q[1], q[2], deep)) dep = true; }
  if (dep) { A.byDepth++; continue; }
  A.open++; if (met > A.worstOpen) A.worstOpen = met;
  let nearBall = sure(p[0], p[1], p[2]) === 1;
  for (const k of [0.8, 1.6, 2.5]) for (const u of dirs) { if (nearBall) break; if (sure(p[0] + k * one * u[0], p[1] + k * one * u[1], p[2] + k * one * u[2]) === 1) nearBall = true; }
  if (nearBall) A.openNearABall++; else { A.openNothing++; if (met > A.worstNothing) A.worstNothing = met; }
} } return A.picks; };
const finish = name => {
  let seed = 20261120; const rnd = () => { seed = (seed * 1664525 + 1013904223) >>> 0; return seed / 4294967296; };
  const some = (a, n) => { const o = a.slice(); for (let i = o.length - 1; i > 0; i--) { const k = Math.floor(rnd() * (i + 1)); [o[i], o[k]] = [o[k], o[i]]; } return o.slice(0, n); };
  let walked = 0, meet = 0, c2 = 0, c10 = 0, longest = 0, leaveBound = 0;
  for (const [px, py] of some(A.miss, RAYS)) {
    const rd = ray(px, py), bb = rd[0] * ro[0] + rd[1] * ro[1] + rd[2] * ro[2], hh = bb * bb - (ro[0] * ro[0] + ro[1] * ro[1] + ro[2] * ro[2]) + bound * bound;
    if (hh <= 0) { leaveBound++; continue; }
    walked++;
    let s = Math.max(-bb - Math.sqrt(hh), 2e-6), first = -1; const sOut = -bb + Math.sqrt(hh);
    while (s < sOut) { const inb = sure(ro[0] + rd[0] * s, ro[1] + rd[1] * s, ro[2] + rd[2] * s) === 1;
      if (inb && first < 0) first = s; else if (!inb && first >= 0) break;
      s *= 1 + 0.25 * pix; }
    if (first >= 0) { meet++; const chord = (s - first) / (pix * first); if (chord > 2) c2++; if (chord > 10) c10++; if (chord > longest) longest = chord; }
  }
  return JSON.stringify({ view: name, status: $('status').textContent, t: S.k.bt, grid: S.k.bgrid, depth: S.k.bit, picks: A.picks, stops: A.stops, nowhere: A.miss.length, missNeverInDrawingRadius: leaveBound, walked, meetABall: meet, holes: c2, chordOver10: c10, longest: +longest.toFixed(1),
    stopOffMyRayPx: +A.offRay.toFixed(3), over13: A.over13, over2: A.over2, byDepth: A.byDepth, open: A.open, worstOpenPx: +A.worstOpen.toFixed(2), worstPx: +A.worst.toFixed(2), openNearABall: A.openNearABall, openNothing: A.openNothing, worstNothingPx: +A.worstNothing.toFixed(2), eye: ro.map(x => +x.toFixed(4)), eyeInsideABall: eyeIn === 1, eyeUndecided: eyeIn === 2, eyeToNearestBallPx: +(eyeEst / pix).toExponential(2), eyeToNearestBall: +eyeEst.toExponential(2), warn: $('ballsWarn') && $('ballsWarn').getClientRects().length ? $('ballsWarn').textContent : '' });
};
window.__H = { band, finish, h };
"""

if __name__ == '__main__':
    args = sys.argv[1:]; tagname = 'holes'
    if args and args[0].startswith('tag='):
        tagname = args[0][4:]; args = args[1:]
    names = args or DEFAULT
    os.makedirs(os.path.join(run.ENTRY, 'shots'), exist_ok=True)
    steps = [run.UP]
    for name in names:
        g, t, R, c = VIEWS[name]
        steps.append({'js': SETUP % (g, t, R, json.dumps(c) if c else 'null', STEP, RAYS), 'shot': 'out/r27/final/shots/%s-%s.png' % (tagname, name), 'clip': '#view'})
        for k in range(BANDS):
            steps.append({'js': "const H = window.__H; H.band(Math.floor(H.h * %d / %d), %s);" % (k, BANDS, 'H.h + 1' if k == BANDS - 1 else 'Math.floor(H.h * %d / %d)' % (k + 1, BANDS))})
        steps.append({'js': "return window.__H.finish('%s');" % name})
    tag = tagname + ('-' + names[0] if len(names) == 1 else '')
    code, text, vals = run.shot(run.PAGE, steps, tag, '1400x950', 'dark')
    run.write(tag + '.log', text + 'exit %d\n' % code)
    lines = ['page %s, exit %d, %s' % (run.PAGE, code, 'no console errors' if run.clean(text) else 'SEE logs/%s.log' % tag)]
    for v in vals[1:]:
        try:
            d = json.loads(v)
        except ValueError:
            lines.append(str(v)[:300]); continue
        # the saved picture: how many of its pixels are the plain background (in a close-up every ray should stop)
        try:
            im = np.asarray(Image.open(os.path.join(run.ENTRY, 'shots', '%s-%s.png' % (tagname, d['view']))).convert('RGB')).astype(int)
            bg = im[0, 0]; same = int((np.abs(im - bg).max(axis=2) <= 2).sum()); tot = im.shape[0] * im.shape[1]
        except Exception as e:
            same, tot = -1, 0
        lines.append('%-18s t %s grid %s depth %s | picks %d: stop %d, stop nowhere %d (%d walked: meet a ball %d, HOLES (through a ball for more than 2 px) %d, more than 10 px %d, longest %.1f px) | stops further than 1.3 px from every ball the search meets %d, further than 2 px %d (beside a region only the depth calls solid %d, IN THE OPEN by that measure %d, furthest %.1f px; of those a ball stands within 2.5 px by 78 probes: %d, NOTHING within 2.5 px: %d, furthest %.1f px); furthest of all %.1f px | eye %s, inside a ball: %s, nearest ball the search meets from the eye %s away (%s px) | my ray against the stop: at most %.3f px off | picture: %d of %d pixels have the colour of its top left corner%s'
                     % (d['view'], d['t'], d['grid'], d['depth'], d['picks'], d['stops'], d['nowhere'], d['walked'], d['meetABall'], d['holes'], d['chordOver10'], d['longest'],
                        d['over13'], d['over2'], d['byDepth'], d['open'], d['worstOpenPx'], d['openNearABall'], d['openNothing'], d['worstNothingPx'], d['worstPx'], d['eye'], d['eyeInsideABall'], d['eyeToNearestBall'], d['eyeToNearestBallPx'], d['stopOffMyRayPx'], same, tot, ' | ' + d['warn'] if d['warn'] else ''))
    out = '\n'.join(lines) + '\n'
    run.write(tag + '.txt', out); print(out)
    if code != 0:
        print(text[-3000:])

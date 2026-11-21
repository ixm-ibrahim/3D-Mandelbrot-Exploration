"""Round 27, fixer: defect A1 (holes in the 3D picture with the neighbours at 100 %) and S (stray stops), my own quick
measure, used to compare the page before and after a change of the shader.

For each view: set the dials and the camera (the checker's views), wait for the picture, save it, ask pick() at
every STEP-th pixel of every STEP-th row. For up to RAYS of the rays that stop nowhere: walk the ray with the exact
inside test (the recipe, 300 rounds, inside only when a wall is reached) in quarter-pixel steps out to the Drawing
radius; a ray that passes through a ball for more than 2 pixels is a hole.
For up to RAYS of the rays that do stop: is anything solid within 2.5 pixels of the stopping point (26 probes round it
and the point itself, exact inside test)? If not, the stop is a stray.

  python out/r27/fix/mk/a1.py <page> <tag> [view ...]   -> logs/a1-<tag>.txt, shots/a1-<tag>-<view>.png
"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import run

KISS = [0.525, 0, 0]
VIEWS = {
    't1-kiss-r16': (0, 1.0, 16, (-1.25, 0.5, 0.30, KISS)),
    't1-kiss-r40': (0, 1.0, 40, (-1.25, 0.5, 0.30, KISS)),
    't1-side-r16': (0, 1.0, 16, (-1.25, 0.5, 2.0, KISS)),
    't1-start-r16': (0, 1.0, 16, None),
    't1-hex-kiss-r16': (1, 1.0, 16, (-1.25, 0.5, 0.30, KISS)),
    't1-line-kiss-r16': (2, 1.0, 16, (-1.25, 0.5, 0.30, KISS)),
    't101-kiss-r16': (0, 1.01, 16, (-1.25, 0.5, 0.30, KISS)),
    't105-kiss-r16': (0, 1.05, 16, (-1.25, 0.5, 0.30, KISS)),
    't105-start-r16': (0, 1.05, 16, None),
    'kiss-eye1-r16': (0, 1.4, 16, (-1.25, 0.5, 0.30, KISS)),
    'kiss-eyeB-r16': (0, 1.4, 16, (1.5708, -0.6, 0.20, KISS)),
    'start-r16': (0, 1.4, 16, None),
    'hex-kiss-r16': (1, 1.4, 16, (-1.25, 0.5, 0.30, KISS)),
    't25-start-r16': (0, 2.5, 16, None),
}
STEP, RAYS = 4, 300

JS = run.HEAD + """
const g = %d, t = %r, rounds = %d, c = %s, STEP = %d, RAYS = %d;
for (const e of $('stage').children) e.style.visibility = '';
if (!(S.mode === 'k' && S.k.group === 1)) { L.ballsShow(); await settle(); }
S.k.bt = t; S.k.bgrid = g; S.k.bit = rounds; S.flat = false; S.cutOn = false;
L.ballsFrame();
if (c) { L.cam.yaw = c[0]; L.cam.pitch = c[1]; L.cam.dist = c[2]; L.cam.target = c[3].slice(); }
go(); const t0 = performance.now(); await settle(); const drawMs = Math.round(performance.now() - t0);
for (const e of $('stage').children) if (e.id !== 'view') e.style.visibility = 'hidden';
const S3 = Math.sqrt(3), K2 = 1.05, top = 2 * t;
const near = (x, y) => { if (g === 2) return [Math.round(x), 0]; if (g === 0) return [Math.round(x), Math.round(y)];
  const b0 = Math.round(y / (S3 / 2)); let best = null, bd = Infinity;
  for (let j = -1; j <= 1; j++) { const b = b0 + j, a = Math.round(x + b / 2), px = a - b / 2, py = b * S3 / 2, d = (x - px) * (x - px) + (y - py) * (y - py); if (d < bd) { bd = d; best = [px, py]; } }
  return best; };
// the recipe: 1 inside (a wall was reached), 0 outside, 2 undecided after 300 rounds
const sure = (x, y, z) => { const ux = y, uy = z, uz = x - K2 / 2; let d = ux * ux + uy * uy + uz * uz; if (!(d > 0)) d = 1e-300;
  let mx = K2 * ux / d, my = K2 * uy / d, mz = 1 + K2 * uz / d;
  for (let i = 0; i < 300; i++) { if (mz < 0 || mz > top) return 1; const n = near(mx, my); mx -= n[0]; my -= n[1];
    const rb = mx * mx + my * my + mz * mz, rt = mx * mx + my * my + (mz - top) * (mz - top);
    if (rb < 1) { const s = 1 / rb; mx *= s; my *= s; mz *= s; } else if (rt < 1) { const s = 1 / rt; mx *= s; my *= s; mz = top + (mz - top) * s; } else return 0; }
  return 2; };
const w = $('stage').clientWidth, h = $('stage').clientHeight, b = L.basis(), fov = S.view.fov, ro = b.pos, pix = 2 * fov / h, bound = S.view.bound;
const ray = (px, py) => { const ux = (2 * px - w) / h * fov, uy = (2 * (h - py) - h) / h * fov;
  const rd = [0, 1, 2].map(k => b.right[k] * ux + b.up[k] * uy + b.f[k]), n = Math.hypot(rd[0], rd[1], rd[2]); return rd.map(x => x / n); };
const miss = [], hit = []; let picks = 0; const t1 = performance.now();
for (let j = 0; j < h; j += STEP) for (let i = 0; i < w; i += STEP) { picks++; const p = L.pick(i + 0.5, j + 0.5); if (p) hit.push([i + 0.5, j + 0.5, Math.hypot(p[0] - ro[0], p[1] - ro[1], p[2] - ro[2])]); else miss.push([i + 0.5, j + 0.5]); }
const pickMs = Math.round(performance.now() - t1);
let seed = 7; const rnd = () => { seed = (seed * 1664525 + 1013904223) >>> 0; return seed / 4294967296; };
const some = (a, n) => { const o = a.slice(); for (let i = o.length - 1; i > 0; i--) { const k = Math.floor(rnd() * (i + 1)); [o[i], o[k]] = [o[k], o[i]]; } return o.slice(0, n); };
// the rays that stop nowhere
let walked = 0, blocked = 0, c2 = 0, c10 = 0, c50 = 0, worst = 0;
for (const [px, py] of some(miss, RAYS)) {
  const rd = ray(px, py), bb = rd[0] * ro[0] + rd[1] * ro[1] + rd[2] * ro[2], hh = bb * bb - (ro[0] * ro[0] + ro[1] * ro[1] + ro[2] * ro[2]) + bound * bound;
  if (hh <= 0) continue;
  walked++;
  let s = Math.max(-bb - Math.sqrt(hh), 2e-6), first = -1, chord = 0; const sOut = -bb + Math.sqrt(hh);
  while (s < sOut) { const v = sure(ro[0] + rd[0] * s, ro[1] + rd[1] * s, ro[2] + rd[2] * s) === 1;
    if (v && first < 0) first = s; else if (!v && first >= 0) break;
    s *= 1 + 0.25 * pix; }
  if (first >= 0) { blocked++; chord = (s - first) / (pix * first); if (chord > 2) c2++; if (chord > 10) c10++; if (chord > 50) c50++; if (chord > worst) worst = chord; }
}
// the rays that stop: is there anything solid within 2.5 pixels of the stopping point?
const dirs = []; for (let a = -1; a <= 1; a++) for (let bq = -1; bq <= 1; bq++) for (let cq = -1; cq <= 1; cq++) if (a || bq || cq) { const n = Math.hypot(a, bq, cq); dirs.push([a / n, bq / n, cq / n]); }
let seen = 0, stray = 0, strayFar = 0, byDepth = 0, byDepthFar = 0;
for (const [px, py, sd] of some(hit, RAYS * 4)) {
  const rd = ray(px, py), p = [ro[0] + rd[0] * sd, ro[1] + rd[1] * sd, ro[2] + rd[2] * sd], one = pix * sd; seen++;
  const solid = r => { if (sure(p[0], p[1], p[2]) !== 0) return true; for (const k of [0.5, 1]) for (const v of dirs) if (sure(p[0] + k * r * v[0], p[1] + k * r * v[1], p[2] + k * r * v[2]) !== 0) return true; return false; };
  // solid at the page's own depth (a point still undecided after the page's rounds counts as inside) within 2.5 pixels
  const pageSolid = r => { if (L.ballsInside(p[0], p[1], p[2])) return true; for (const k of [0.5, 1]) for (const v of dirs) if (L.ballsInside(p[0] + k * r * v[0], p[1] + k * r * v[1], p[2] + k * r * v[2])) return true; return false; };
  // (a ball smaller than the probes can see still counts: the true distance to the nearest ball the search meets, 300 rounds)
  const met = L.ballsEstimate(p[0], p[1], p[2], { rounds: 300, parts: true })[0] / one;
  // (and a sliver that is solid only by the page's depth can be thinner than the probes are apart: walk on along the ray)
  const ahead = () => { for (let k = 0.25; k <= 3; k += 0.25) { const q = [p[0] + k * one * rd[0], p[1] + k * one * rd[1], p[2] + k * one * rd[2]]; if (L.ballsInside(q[0], q[1], q[2])) return sure(q[0], q[1], q[2]) !== 1; } return false; };
  if (!solid(2.5 * one) && met > 2.5) { const dep = pageSolid(2.5 * one) || ahead(); if (dep) byDepth++; else stray++; if (!solid(5 * one) && met > 5) { if (dep) byDepthFar++; else strayFar++; } }
}
return JSON.stringify({ view: '%s', status: $('status').textContent, drawMs, pickMs, picks, stops: hit.length, nowhere: miss.length, walked, meetABall: blocked, chordOver2px: c2, chordOver10px: c10, chordOver50px: c50, longestChordPx: +worst.toFixed(1),
  stopsLookedAt: seen, nothingSolidWithin2_5px: stray, nothingSolidWithin5px: strayFar, solidOnlyByDepth: byDepth, solidOnlyByDepthFar: byDepthFar, warn: $('ballsWarn') ? $('ballsWarn').textContent : '' });
"""

if __name__ == '__main__':
    page, tag = sys.argv[1], sys.argv[2]
    names = sys.argv[3:] or list(VIEWS)
    steps = [run.UP]
    for name in names:
        g, t, R, c = VIEWS[name]
        steps.append({'js': JS % (g, t, R, json.dumps(c) if c else 'null', STEP, RAYS, name), 'timeout': 1200,
                      'shot': 'out/r27/fix/shots/a1-%s-%s.png' % (tag, name), 'clip': '#view'})
    code, text, vals = run.shot(page, steps, 'a1-' + tag + ('-' + names[0] if len(names) == 1 else ''), '1400x950', 'dark')
    lines = ['page %s, exit %d, %s' % (page, code, 'no console errors' if 'no console errors' in text else 'SEE THE LOG')]
    for v in vals[1:]:
        try:
            d = json.loads(v)
        except ValueError:
            lines.append(str(v)[:300]); continue
        lines.append('%-16s picks %d: stop %d, stop nowhere %d | of %d walked: meet a ball %d, through a ball for more than 2 px %d, 10 px %d, 50 px %d (longest %.1f) | of %d stops: solid only because the depth of the page leaves it undecided %d (nothing truly solid within 5 px: %d); nothing solid at all within 2.5 px %d, within 5 px %d | draw %d ms, picks %d ms%s'
                     % (d['view'], d['picks'], d['stops'], d['nowhere'], d['walked'], d['meetABall'], d['chordOver2px'], d['chordOver10px'], d['chordOver50px'], d['longestChordPx'],
                        d['stopsLookedAt'], d['solidOnlyByDepth'], d['solidOnlyByDepthFar'], d['nothingSolidWithin2_5px'], d['nothingSolidWithin5px'], d['drawMs'], d['pickMs'], ' | ' + d['warn'] if d['warn'] else ''))
    out = '\n'.join(lines) + '\n'
    run.write('a1-%s%s.txt' % (tag, '-' + names[0] if len(names) == 1 else ''), out)
    print(out)
    if code != 0:
        print(text[-3000:])

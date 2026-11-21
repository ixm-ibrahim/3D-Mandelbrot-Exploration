"""Round 27, fixer: is the spindle really empty, and is the estimate of the page still never longer than the true
distance? Double precision, in the page (the twin), one step of the browser for each t so that no step runs long.

Part 1 (the spindle alone, in the object's own coordinates, without the lab's estimate): for each t and grid, random
points m of the middle cell that the recipe calls OUTSIDE at once and that lie inside the spindle (room e = 1/4 + s^2 -
distance from (1/4 - s^2, t) in the (distance from the middle line, z) half-plane, s^2 = t^2 - 1). On the sphere of
radius 0.999 e round m, 400 directions: is any of those points inside a ball (the recipe, 400 rounds, inside only when
a wall is reached)? Then how tight: the smallest of 1.25 e, 1.5 e, 2 e, 3 e at which a direction finds a ball.
Part 2 (the page's estimate as a whole, ballsEstimate, 60 rounds): the same question at random points of the picture
box and at points close to the place where the two big balls kiss (0.5 down to 0.0005 away).

  python out/r27/fix/mk/spindle.py [page]   -> logs/spindle.txt
"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import run

PRE = """
const S3 = Math.sqrt(3), K2 = 1.05;
const near = (g, x, y) => { if (g === 2) return [Math.round(x), 0]; if (g === 0) return [Math.round(x), Math.round(y)];
  const b0 = Math.round(y / (S3 / 2)); let best = null, bd = Infinity;
  for (let j = -1; j <= 1; j++) { const b = b0 + j, a = Math.round(x + b / 2), px = a - b / 2, py = b * S3 / 2, d = (x - px) * (x - px) + (y - py) * (y - py); if (d < bd) { bd = d; best = [px, py]; } }
  return best; };
const sureM = (g, t, mx, my, mz, R) => { const top = 2 * t;
  for (let i = 0; i < R; i++) { if (mz < 0 || mz > top) return 1; const n = near(g, mx, my); mx -= n[0]; my -= n[1];
    const rb = mx * mx + my * my + mz * mz, rt = mx * mx + my * my + (mz - top) * (mz - top);
    if (rb < 1) { const s = 1 / rb; mx *= s; my *= s; mz *= s; } else if (rt < 1) { const s = 1 / rt; mx *= s; my *= s; mz = top + (mz - top) * s; } else return 0; }
  return 2; };
const sureP = (g, t, x, y, z) => { const ux = y, uy = z, uz = x - K2 / 2, d = Math.max(ux * ux + uy * uy + uz * uz, 1e-300); return sureM(g, t, K2 * ux / d, K2 * uy / d, 1 + K2 * uz / d, 400); };
let seed = %d; const rnd = () => { seed = (seed * 1664525 + 1013904223) >>> 0; return seed / 4294967296; };
const dirs = []; for (let i = 0; i < 400; i++) { const u = 2 * rnd() - 1, a = 2 * Math.PI * rnd(), s = Math.sqrt(1 - u * u); dirs.push([s * Math.cos(a), s * Math.sin(a), u]); }
const t = %r, out = [];
"""
ONE = PRE + """
for (const g of [0, 1, 2]) {
  const s2 = t * t - 1, rc = 0.25 - s2, Ra = 0.25 + s2, H = t - Math.sqrt(s2);
  let n = 0, breaks = 0, undec = 0, worst = 0, wins = 0; const hist = [0, 0, 0, 0, 0];
  for (let k = 0; k < 400000 && n < 600; k++) {
    const narrow = k %% 2 === 0, rr = (narrow ? 0.12 : 0.5) * Math.sqrt(rnd()), an = 2 * Math.PI * rnd();
    const m = [rr * Math.cos(an), rr * Math.sin(an), H + (2 * t - 2 * H) * rnd()];
    if (m[0] * m[0] + m[1] * m[1] + m[2] * m[2] < 1 || m[0] * m[0] + m[1] * m[1] + (m[2] - 2 * t) * (m[2] - 2 * t) < 1) continue;
    const e = Ra - Math.hypot(Math.hypot(m[0], m[1]) - rc, m[2] - t);
    if (!(e > 1e-9)) continue;
    n++;
    // is the spindle the larger of the two rooms here? (the other one: the two balls of diameter H, and the layer by the walls)
    { const rest = g === 0 ? H / 2 : g === 1 ? H / 3 : H / 4, hb = m[2], ht = 2 * t - m[2], cb = Math.hypot(m[0], m[1], hb - H / 2) - H / 2, ct = Math.hypot(m[0], m[1], ht - H / 2) - H / 2;
      const lo = g === 2 ? Math.hypot(m[1], hb) : hb, hi = g === 2 ? Math.hypot(m[1], ht) : ht; if (e > Math.max(Math.min(cb, ct, Math.min(lo, hi) - rest), 0)) wins++; }
    let bad = false;
    for (const v of dirs) { const r = sureM(g, t, m[0] + 0.999 * e * v[0], m[1] + 0.999 * e * v[1], m[2] + 0.999 * e * v[2], 400); if (r === 1) { bad = true; break; } if (r === 2) undec++; }
    if (bad) { breaks++; worst = Math.max(worst, e); continue; }
    let at = 4; const fs = [1.25, 1.5, 2, 3];
    for (let f = 0; f < 4 && at === 4; f++) for (const v of dirs) if (sureM(g, t, m[0] + fs[f] * e * v[0], m[1] + fs[f] * e * v[1], m[2] + fs[f] * e * v[2], 400) === 1) { at = f; break; }
    hist[at]++;
  }
  out.push({ part: 1, t, grid: g, points: n, spindleIsTheLargerRoom: wins, breaks, worst, undecidedProbes: undec, within: hist });
}
return JSON.stringify(out);
"""
TWO = PRE + """
for (const g of [0, 1, 2]) for (const where of ['box', 'kiss']) {
  const opts = { t, grid: g, rounds: 60 }, fs = [1.5, 2, 3, 5], hist = [0, 0, 0, 0, 0];
  let n = 0, breaks = 0, worst = 0;
  for (let k = 0; k < 20000 && n < 300; k++) {
    const sc = where === 'box' ? 1 : Math.pow(10, -3 * rnd());
    const p = where === 'box' ? [-1.9 + 3.8 * rnd(), -1.4 + 2.8 * rnd(), -1.4 + 2.8 * rnd()] : [0.525 + sc * (rnd() - 0.5), sc * (rnd() - 0.5), sc * (rnd() - 0.5)];
    const d = L.ballsEstimate(p[0], p[1], p[2], opts);
    if (!(d > 0)) continue;
    n++;
    let bad = false;
    for (const v of dirs) if (sureP(g, t, p[0] + 0.999 * d * v[0], p[1] + 0.999 * d * v[1], p[2] + 0.999 * d * v[2]) === 1) { bad = true; break; }
    if (bad) { breaks++; worst = Math.max(worst, d); continue; }
    let at = 4;
    for (let f = 0; f < 4 && at === 4; f++) for (const v of dirs) if (sureP(g, t, p[0] + fs[f] * d * v[0], p[1] + fs[f] * d * v[1], p[2] + fs[f] * d * v[2]) === 1) { at = f; break; }
    hist[at]++;
  }
  out.push({ part: 2, t, grid: g, where, points: n, breaks, worst, within: hist });
}
return JSON.stringify(out);
"""
T1 = [1, 1.0005, 1.003, 1.02, 1.05, 1.1, 1.118, 1.2, 1.4, 1.7, 1.99]
T2 = [1, 1.003, 1.02, 1.05, 1.1, 1.2, 1.4, 1.99, 2.5]
GRID = ['square', 'honeycomb', 'line']

if __name__ == '__main__':
    page = sys.argv[1] if len(sys.argv) > 1 else run.PAGE
    steps = [run.UP] + [{'js': run.HEAD + ONE % (100 + i, t), 'timeout': 600} for i, t in enumerate(T1)] + [{'js': run.HEAD + TWO % (500 + i, t), 'timeout': 600} for i, t in enumerate(T2)]
    code, text, vals = run.shot(page, steps, 'spindle', '1400x950', 'dark')
    rows = []
    for v in vals[1:]:
        try:
            rows += json.loads(v)
        except ValueError:
            pass
    lines = ['page %s, exit %d, %s' % (page, code, 'no console errors' if 'no console errors' in text else 'SEE THE LOG'),
             'Part 1: the spindle alone. Points inside it (the recipe says OUTSIDE at once), 400 directions each at 0.999 of the room.']
    tot = [0, 0, 0, 0]
    for r in rows:
        if r['part'] != 1:
            continue
        h = r['within']; tot[0] += r['points']; tot[1] += r['breaks']; tot[2] += r['spindleIsTheLargerRoom']
        lines.append('  t = %-6s %-9s points %4d (the spindle is the larger room at %4d): a ball inside the room at %d%s; a ball within 1.25 e: %d, 1.5 e: %d, 2 e: %d, 3 e: %d, none within 3 e: %d; probes undecided after 400 rounds: %d'
                     % (r['t'], GRID[r['grid']], r['points'], r['spindleIsTheLargerRoom'], r['breaks'], ' (largest such room %.3g)' % r['worst'] if r['breaks'] else '', h[0], h[1], h[2], h[3], h[4], r['undecidedProbes']))
    lines.append('  TOTAL part 1: %d points, a ball inside the room at %d; the spindle is the larger of the two rooms at %d' % (tot[0], tot[1], tot[2]))
    lines.append('Part 2: the estimate of the page (ballsEstimate, 60 rounds), 400 directions each at 0.999 of the estimate.')
    tot = [0, 0]
    for r in rows:
        if r['part'] != 2:
            continue
        h = r['within']; tot[0] += r['points']; tot[1] += r['breaks']
        lines.append('  t = %-6s %-9s %-4s outside points %4d: estimate longer than the true distance at %d%s; a ball within 1.5 d: %d, 2 d: %d, 3 d: %d, 5 d: %d, none within 5 d: %d'
                     % (r['t'], GRID[r['grid']], r['where'], r['points'], r['breaks'], ' (largest %.3g)' % r['worst'] if r['breaks'] else '', h[0], h[1], h[2], h[3], h[4]))
    lines.append('  TOTAL part 2: %d outside points, estimate longer than the true distance at %d' % (tot[0], tot[1]))
    out = '\n'.join(lines) + '\n'
    run.write('spindle.txt', out); print(out)
    if code != 0:
        print(text[-2000:])

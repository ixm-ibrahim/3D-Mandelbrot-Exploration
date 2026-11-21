"""Round 28, Track A, the fixer: E2, the pale lozenges on the bare skin of a large neighbour. Whose shadow are they?

  python out/r28/fix/mk/skinray.py     -> out/r28/fix/logs/skinray.txt

The eyes' view p300-r25-neighbour (their own set-up, rays.SETUP). For pixels inside the patch and beside it the page's
pick() gives the point of the skin; from there the light's own ray is walked the way the shadow march walks it
(strides as in the shader), and at every stop the page's ballsEstimate is read with both of its numbers:
"best" (the true distance to the nearest ball the search met) and "free" (the length that is certainly free).
The shadow darkens where 10 x estimate / (length of the ray so far) falls under 1. For each pixel: the smallest value
of that along the ray as the page reads it (estimate = the smaller of the two numbers), the same with "best" alone,
and where along the ray, in the object's own coordinates, the smallest value was read.
"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); FIX = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(FIX, 'eyes', 'mk'))
import eyerun as run
import views, rays

PIX = [(400, 640), (380, 625), (420, 655), (395, 610), (300, 560), (500, 640), (400, 560), (330, 660)]
JS = run.HEAD + """
const K2 = 1.05, o = { parts: true };
// the light as the picture has it (40-render.js: uLight from S.lightAz and S.lightEl, in degrees)
const el = S.lightEl * Math.PI / 180, az = S.lightAz * Math.PI / 180, LIGHT = [Math.cos(el) * Math.cos(az), Math.cos(el) * Math.sin(az), Math.sin(el)];
const out = { light: LIGHT, rows: [] };
for (const [px, py] of %s) {
  const p = L.pick(px, py); if (!p) { out.rows.push({ px, py, miss: true }); continue; }
  const C = [0.525 + 0.525 * 3, 0, 0], n = [p[0] - C[0], p[1] - C[1], p[2] - C[2]], nl = Math.hypot(n[0], n[1], n[2]); n[0] /= nl; n[1] /= nl; n[2] /= nl;
  let ts = 0.004, lowAll = 9, lowBest = 9, at = null, steps = 0;
  const q0 = [p[0] + 0.002 * n[0], p[1] + 0.002 * n[1], p[2] + 0.002 * n[2]];
  while (ts <= 5 && steps < 400) {
    const q = [q0[0] + LIGHT[0] * ts, q0[1] + LIGHT[1] * ts, q0[2] + LIGHT[2] * ts], e = L.ballsEstimate(q[0], q[1], q[2], o), d = Math.min(e[0], e[1]);
    if (10 * d / ts < lowAll) { lowAll = 10 * d / ts; const u = [q[1], q[2], q[0] - K2 / 2], dd = u[0] * u[0] + u[1] * u[1] + u[2] * u[2]; at = { ts, best: e[0], free: e[1], m: [K2 * u[0] / dd, K2 * u[1] / dd, 1 + K2 * u[2] / dd] }; }
    if (10 * e[0] / ts < lowBest) lowBest = 10 * e[0] / ts;
    ts += Math.min(Math.max(d, 0.002), 0.35); steps++;
  }
  out.rows.push({ px, py, p, dotNL: n[0] * LIGHT[0] + n[1] * LIGHT[1] + n[2] * LIGHT[2], lowAll, lowBest, at, steps });
}
return JSON.stringify(out);
"""
if __name__ == '__main__':
    v = views.V['p300-r25-neighbour']
    js0 = rays.SETUP % (json.dumps('p300-r25-neighbour'), v['grid'], json.dumps(str(v['p'])), json.dumps(str(v['rho'])), v['depth'], json.dumps(views.cam_numbers(v)), 'false', rays.STEP)
    steps = [run.UP, {'js': js0, 'wait': 'done', 'timeout': 900}, {'js': JS % json.dumps(PIX)}]
    code, text, vals = run.shot(run.PAGE, steps, 'skinray', '1400x950', 'dark')
    lines = ['page %s, exit %d, %s' % (run.PAGE, code, 'no console errors' if run.clean(text) else 'SEE THE LOG')]
    for x in vals:
        if x.startswith('{"light"'):
            d = json.loads(x)
            for r in d['rows']:
                if r.get('miss'):
                    lines.append('pixel (%d, %d): no stop' % (r['px'], r['py'])); continue
                a = r['at']
                lines.append('pixel (%d, %d): skin point (%.4f, %.4f, %.4f), light on the skin %.3f | smallest 10 x estimate / length along the light\'s ray: %.3f as the page reads it, %.3f from "best" alone | read at length %.3f: best %.4f, free %.4f, in the object\'s own space (%.3f, %.3f, %.3f) | %d stops'
                             % (r['px'], r['py'], *r['p'], r['dotNL'], r['lowAll'], r['lowBest'], a['ts'], a['best'], a['free'], *a['m'], r['steps']))
    open(os.path.join(FIX, 'logs', 'skinray.txt'), 'w', encoding='utf-8', newline='\n').write('\n'.join(lines) + '\n')
    print('\n'.join(lines))

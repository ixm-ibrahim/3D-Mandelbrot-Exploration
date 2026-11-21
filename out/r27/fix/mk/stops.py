"""Round 27, fixer, defect S: how far from a ball does every ray of a view stop?

For every stop of pick() (every 4th pixel of every 4th row): the true distance from the stopping point to the nearest
ball that the search meets from there, in pixels (the first number of ballsEstimate with parts, 300 rounds: each
ball the search meets is a real ball and that number is the exact distance to it, whatever its size, also far below
a pixel). A stop further than 2.5 px from every ball the search meets is then looked at: is it beside a region that
only the page's depth calls solid (walking on along the ray for 3 px), or in the open?
  python out/r27/fix/mk/stops.py <page> <tag> [view ...]   -> logs/stops-<tag>.txt
"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import run
import a1

JS = run.HEAD + """
const g = %d, t = %r, rounds = %d, c = %s;
if (!(S.mode === 'k' && S.k.group === 1)) { L.ballsShow(); await settle(); }
S.k.bt = t; S.k.bgrid = g; S.k.bit = rounds; S.flat = false; S.cutOn = false;
L.ballsFrame();
if (c) { L.cam.yaw = c[0]; L.cam.pitch = c[1]; L.cam.dist = c[2]; L.cam.target = c[3].slice(); }
go(); await settle();
const w = $('stage').clientWidth, h = $('stage').clientHeight, b = L.basis(), fov = S.view.fov, ro = b.pos, pix = 2 * fov / h;
const o300 = { t, grid: g, rounds: 300, parts: true }, hist = [0, 0, 0, 0, 0]; let stops = 0, far = 0, farDepth = 0, farOpen = 0, worst = 0, worstOpen = 0;
for (let j = 0; j < h; j += 4) for (let i = 0; i < w; i += 4) {
  const p = L.pick(i + 0.5, j + 0.5); if (!p) continue;
  stops++;
  const sd = Math.hypot(p[0] - ro[0], p[1] - ro[1], p[2] - ro[2]), one = pix * sd, met = L.ballsEstimate(p[0], p[1], p[2], o300)[0] / one;
  hist[met <= 1 ? 0 : met <= 1.3 ? 1 : met <= 2 ? 2 : met <= 2.5 ? 3 : 4]++;
  if (met > worst) worst = met;
  if (!(met > 2.5)) continue;
  far++;
  const rd = [(p[0] - ro[0]) / sd, (p[1] - ro[1]) / sd, (p[2] - ro[2]) / sd]; let dep = false;
  for (let k = 0; k <= 3 && !dep; k += 0.25) { const q = [p[0] + k * one * rd[0], p[1] + k * one * rd[1], p[2] + k * one * rd[2]]; if (L.ballsInside(q[0], q[1], q[2]) && !L.ballsInside(q[0], q[1], q[2], { t, grid: g, rounds: 3000 })) dep = true; }
  if (dep) farDepth++; else { farOpen++; if (met > worstOpen) worstOpen = met; }
}
return JSON.stringify({ view: '%s', stops, hist, far, farDepth, farOpen, worst: +worst.toFixed(2), worstOpen: +worstOpen.toFixed(2) });
"""

if __name__ == '__main__':
    page, tag = sys.argv[1], sys.argv[2]
    names = sys.argv[3:] or ['kiss-eyeB-r16', 't105-kiss-r16', 't105-start-r16', 't1-kiss-r16', 't1-kiss-r40', 't1-side-r16', 'kiss-eye1-r16', 'start-r16']
    steps = [run.UP] + [{'js': JS % (a1.VIEWS[n][0], a1.VIEWS[n][1], a1.VIEWS[n][2], json.dumps(a1.VIEWS[n][3]) if a1.VIEWS[n][3] else 'null', n), 'timeout': 1200} for n in names]
    code, text, vals = run.shot(page, steps, 'stops-' + tag, '1400x950', 'dark')
    lines = ['page %s, exit %d, %s' % (page, code, 'no console errors' if 'no console errors' in text else 'SEE THE LOG')]
    for v in vals[1:]:
        try:
            d = json.loads(v)
        except ValueError:
            lines.append(str(v)[:300]); continue
        hh = d['hist']
        lines.append('%-16s stops %5d: nearest ball the search meets within 1 px: %d, 1 to 1.3 px: %d, 1.3 to 2 px: %d, 2 to 2.5 px: %d, further: %d (of those beside a region only the depth calls solid: %d; in the open: %d, furthest %.1f px); furthest of all %.1f px'
                     % (d['view'], d['stops'], hh[0], hh[1], hh[2], hh[3], hh[4], d['farDepth'], d['farOpen'], d['worstOpen'], d['worst']))
    out = '\n'.join(lines) + '\n'
    run.write('stops-%s.txt' % tag, out); print(out)
    if code != 0:
        print(text[-2000:])

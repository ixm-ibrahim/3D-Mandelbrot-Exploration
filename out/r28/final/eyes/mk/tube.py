"""The eyes: is there anything solid NEAR a ray of a 3D view (not only on it)? For the given picture pixels the ray
is walked in half-pixel steps and, at each step, 24 points round it are tried (8 each at 0.5, 1 and 2 px from the
ray). Says how close to the ray something solid comes, at the page's depth and for points that reach a wall in 300
rounds. A painted pixel with nothing within 2 px of its ray would be noise.
  python out/r28/final/eyes/mk/tube.py <tag> <view> x,y [x,y ...]"""
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import recipe, walk
tag, name = sys.argv[1:3]
m, dep, met, img = walk.load(tag, name)
top = 2 * m['k']['bt']; rho = m['k']['brho']; grid = m['k']['bgrid']; rounds = m['k']['bit']
ro = np.array(m['ro']); pix = m['pix']; bound = m['bound']; w, h, fov = m['w'], m['h'], m['fov']
R, U, F = (np.array(m[k]) for k in ('right', 'up', 'f'))
out = []
for a in sys.argv[3:]:
    x, y = (int(v) for v in a.split(','))
    px, py = x + 0.5, y + 0.5
    rd = (2 * px - w) / h * fov * R + (2 * (h - py) - h) / h * fov * U + F; rd /= np.linalg.norm(rd)
    e1 = np.cross(rd, [0.0, 0.0, 1.0]); e1 /= np.linalg.norm(e1); e2 = np.cross(rd, e1)
    b = rd @ ro; hh = b * b - ro @ ro + bound * bound
    s0, s1 = max(-b - np.sqrt(hh), 1e-3), -b + np.sqrt(hh)
    s = s0 * (1 + 0.5 * pix) ** np.arange(int(np.log(s1 / s0) / np.log(1 + 0.5 * pix)) + 1)
    res = {}
    for rad in (0.0, 0.5, 1.0, 2.0):
        angs = [0.0] if rad == 0 else np.arange(8) * np.pi / 4
        hit16 = np.zeros(s.size, dtype=bool); hitw = np.zeros(s.size, dtype=bool)
        for an in angs:
            P = ro + rd * s[:, None] + (rad * pix * s)[:, None] * (np.cos(an) * e1 + np.sin(an) * e2)
            v16 = recipe.verdict(P, top, rho, grid, rounds); hit16 |= v16 != 0
            v300 = recipe.verdict(P, top, rho, grid, 300); hitw |= v300 == 1
        res[rad] = (int(hit16.sum()), int(hitw.sum()), float(s[hit16][0]) if hit16.any() else None)
    out.append('%s pixel (%d, %d) painted %s: points tried at each of %d steps; solid at the page\'s depth / reaching a wall in 300 rounds: on the ray %d / %d; at 0.5 px from it %d / %d; at 1 px %d / %d; at 2 px %d / %d%s'
               % (name, x, y, tuple(int(c) for c in img[y, x]), s.size, res[0.0][0], res[0.0][1], res[0.5][0], res[0.5][1], res[1.0][0], res[1.0][1], res[2.0][0], res[2.0][1],
                  '; first at %.4f from the eye' % next((res[r][2] for r in (0.0, 0.5, 1.0, 2.0) if res[r][2]), -1)))
text = '\n'.join(out) + '\n'
open(os.path.join(walk.EYES, 'logs', 'tube-%s.txt' % tag), 'a', encoding='utf-8', newline='\n').write(text)
print(text)

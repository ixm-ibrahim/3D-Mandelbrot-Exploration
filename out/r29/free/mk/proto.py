"""Round 29, Track A, builder: the prototype of the new distance against the reference (numpy alone, no page).

  python -B out/r29/free/mk/proto.py [flat|box|both] [names...] [key=value ...]
     -> out/r29/free/logs/proto-*.txt, out/r29/free/shots/proto-<name>.png

For each state of the new panel: the recipe alone on a fine grid of the flat cut (and of a box in space), the true
distance from it (a distance transform), and the prototype's distance at the same points.
  safe:   the share of outside points where the estimate is longer than the true distance (2 % and one grid step
          allowed), and the largest ratio;
  small:  outside points where the estimate is under one pixel of a 700 pixel high picture although nothing inside is
          within three pixels (those would be drawn as outline where no outline is).
The picture: inside dark, outside light, red where the estimate is under a pixel (the outline the 2D view would draw),
blue where the estimate is longer than the truth allows.
"""
import os, sys, time
import numpy as np
from PIL import Image
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import kit29 as K

OUT = os.path.dirname(HERE)


def view(p):
    """About the 2D start view of the page for a 1.23 : 1 picture: half width, half height."""
    r = max(4.5, K.K2 * (0.5 + 1.5 * p / 100)) if p > 60 else K.K2 * (0.5 + 1.2 * p / 100) + 0.6
    r = min(r, 9.0)
    return r, r / 1.23


def flat(name, p, rs, grid, rounds, parts, nx=900, zoom=1.0, cx=0.0, cy=0.0, tag=''):
    t = K.t_of(p); rho = rs / 100.0
    hw, hh = view(p); hw /= zoom; hh /= zoom
    xs, ys, ins, dist, step, P = K.flat_truth(t, rho, grid, rounds, cx, cy, hw, hh, nx)
    d, best, free, st = K.estimate(P, t, rho, grid, rounds, parts)
    d = d.reshape(ins.shape); st = st.reshape(ins.shape)
    out = ~ins
    px = 2 * hh / 700.0
    line = '%-4s size %7.2f second %6.2f grid %d depth %3d | inside share %.3f' % (name, p, rs, grid, rounds, ins.mean())
    if out.any() and ins.any():
        e = d[out]; tr = dist[out]
        bad = e > tr * 1.02 + step
        ratio = (e / np.maximum(tr, step)).max()
        small = (e < px) & (tr > 3 * px + step)
        line += ' | outside %d: too long %d (%.4f %%), worst ratio %.3f | wrongly under a pixel %d (%.3f %%) | median est/true %.2f' % (
            out.sum(), bad.sum(), 100.0 * bad.mean(), ratio, small.sum(), 100.0 * small.mean(), np.median(e / np.maximum(tr, step)))
    else:
        line += ' | nothing to measure (all inside or all outside)'
    img = np.where(ins, 40, 235).astype(np.uint8)
    rgb = np.stack([img, img, img], 2)
    if out.any() and ins.any():
        red = out & (d < px)
        blue = out & (d > dist * 1.02 + step)
        rgb[red] = (220, 40, 40); rgb[blue] = (40, 80, 230)
    Image.fromarray(rgb).save(os.path.join(OUT, 'shots', 'proto-%s%s.png' % (name, tag)))
    return line


def box(name, p, rs, grid, rounds, parts, centre, half, n=160):
    t = K.t_of(p); rho = rs / 100.0
    P, ins, dist, step = K.box_truth(t, rho, grid, rounds, centre, half, n)
    out = ~ins.ravel()
    line = '%-4s box at %s half %.2f | inside share %.3f' % (name, centre, half, ins.mean())
    if out.any() and ins.any():
        # points whose true nearest inside point may lie outside the box are left out: keep those nearer to an
        # inside point than to the wall of the box
        X = P[out]; tr = dist.ravel()[out]
        wall = half - np.abs(X - np.array(centre)).max(1)
        keep = tr < wall
        d, best, free, st = K.estimate(X[keep], t, rho, grid, rounds, parts)
        tr = tr[keep]
        bad = d > tr * 1.02 + step
        line += ' | outside %d: too long %d (%.4f %%), worst ratio %.3f | median est/true %.2f, under a tenth of the truth %.2f %%' % (
            keep.sum(), bad.sum(), 100.0 * bad.mean(), (d / np.maximum(tr, step)).max(), np.median(d / np.maximum(tr, step)),
            100.0 * (d < 0.1 * tr - step).mean())
    else:
        line += ' | nothing to measure'
    return line


if __name__ == '__main__':
    args = sys.argv[1:]
    what = args[0] if args and args[0] in ('flat', 'box', 'both') else 'flat'
    names = [a for a in args[1:] if '=' not in a]
    parts = dict((a.split('=')[0], int(a.split('=')[1])) for a in args[1:] if '=' in a)
    tag = ''.join('-%s%s' % (k, parts[k] if k == 'depth' else '') for k in sorted(parts))
    lines = []
    depth = parts.pop('depth', None)
    for (name, p, rs, grid, rounds) in K.PANEL_NEW + K.PANEL_OLD:
        if (names and name not in names) or (not names and name[0] == 'O'):
            continue
        rounds = depth or rounds
        t0 = time.time()
        if what in ('flat', 'both'):
            lines.append('flat ' + flat(name, p, rs, grid, rounds, parts, tag=tag)); print(lines[-1], flush=True)
        if what in ('box', 'both'):
            c = (K.K2 / 2 + 0.05, 0.25, 0.2)
            lines.append('box  ' + box(name, p, rs, grid, rounds, parts, c, 0.7)); print(lines[-1], flush=True)
            lines.append('box  ' + box(name, p, rs, grid, rounds, parts, (0.0, 0.62, 0.3), 0.45)); print(lines[-1], flush=True)
    open(os.path.join(OUT, 'logs', 'proto-%s%s.txt' % (what, tag)), 'w', encoding='utf-8', newline='\n').write('\n'.join(lines) + '\n')

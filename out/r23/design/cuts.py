"""Round 23, design: cuts OFF the mirror planes, one picture per rule (rows = shapes, columns = planes).

    python out/r23/design/cuts.py <rule,rule,...> [sets] [steps]      -> out/r23/design/cuts-<rule>.png
    python out/r23/design/cuts.py try <name>=<kw>;...                 quick look at lens settings (see main)

Columns (u to the right, v up; every picture 3.6 wide and 2.7 high unless said):
  A  the flat plane lifted to z = 0.25                      (level cut; no rule here has it as a mirror plane)
  B  upright plane through the x-axis (y = 0)               (a mirror plane of most rules: shown for the outline only)
  C  plane through the x-axis turned 33.75 degrees
  D  plane through the x-axis turned 22.5 degrees
  E  upright plane through the upright axis, 30 degrees from the x-axis
  F  across the x-axis at x = x0 (x0 = 0 for c on the x-axis, else the x of the point where the big bodies meet)
"""
import os, sys, time
import numpy as np
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import rules as R
M = R.M


def plane(o, eu, ev, w, h, hu=1.8, hv=1.35):
    u, v = np.meshgrid(np.linspace(-hu, hu, w), np.linspace(hv, -hv, h))
    return tuple(o[i] + u * eu[i] + v * ev[i] for i in range(3))


def planes(c):
    a1, a2, a3 = np.radians(33.75), np.radians(22.5), np.radians(30.0)
    cc = complex(c[0], c[1]); x0 = 0.0 if abs(c[1]) < 1e-12 else float(((1 - np.sqrt(1 - 4 * cc)) / 2).real)
    return [
        ('level, lifted to z = 0.25', (0, 0, 0.25), (1, 0, 0), (0, 1, 0)),
        ('upright through the x-axis', (0, 0, 0), (1, 0, 0), (0, 0, 1)),
        ('through the x-axis, turned 33.75', (0, 0, 0), (1, 0, 0), (0, np.cos(a1), np.sin(a1))),
        ('through the x-axis, turned 22.5', (0, 0, 0), (1, 0, 0), (0, np.cos(a2), np.sin(a2))),
        ('upright, 30 degrees from the x-axis', (0, 0, 0), (np.cos(a3), np.sin(a3), 0), (0, 0, 1)),
        ('across the x-axis at x = %.2f' % x0, (x0, 0, 0), (0, 1, 0), (0, 0, 1)),
    ]


def cut_row(rule, c, w=240, h=180, steps=60):
    out = []
    for nm, o, eu, ev in planes(c):
        P = plane(o, eu, ev, w, h)
        out.append((nm, M.shade(M.stay(rule, P[0], P[1], P[2], c[0], c[1], c[2], steps), steps)))
    return out


def picture(rule, sets, path, steps=60, w=240, h=180, title=None):
    pad = 8; rows = []
    for s in sets:
        rows.append((R.SETNAME[s], cut_row(rule, R.SETS[s], w, h, steps)))
    W = pad + 6 * (w + pad); H = 40 + len(rows) * (h + 40)
    im = Image.new('RGB', (W, H), (12, 14, 20)); d = ImageDraw.Draw(im)
    d.text((pad, 8), title or '%s: cuts, %d steps (light = stays)' % (rule.name, steps), fill=(240, 240, 245), font=M.font(18))
    for i, (sn, row) in enumerate(rows):
        y = 40 + i * (h + 40)
        for j, (nm, pic) in enumerate(row):
            x = pad + j * (w + pad)
            d.text((x, y), '%s | %s' % (sn, nm), fill=(170, 180, 195), font=M.font(12)); im.paste(Image.fromarray(pic), (x, y + 18))
    im.save(path); return path


if __name__ == '__main__':
    t0 = time.time()
    if sys.argv[1] == 'try':
        # python cuts.py try "A:b=55,rho=1.6,gamma=90,sx=1,ext=0.25;B:..."   -> cuts-try-<A>.png (c = -1 and rabbit)
        for item in sys.argv[2].split(';'):
            tag, kws = item.split(':'); kw = {k: float(v) for k, v in (t.split('=') for t in kws.split(','))}
            r = R.lens('lens-' + tag, **kw)
            picture(r, ['basilica', 'rabbit'], os.path.join(HERE, 'cuts-try-%s.png' % tag), steps=50, title='lens %s %s' % (tag, kw))
            print('try', tag, kw, '%.0f s' % (time.time() - t0)); sys.stdout.flush()
    else:
        sets = sys.argv[2].split(',') if len(sys.argv) > 2 else ['basilica', 'sanmarco', 'rabbit', 'siegel', 'dendrite']
        steps = int(sys.argv[3]) if len(sys.argv) > 3 else 60
        for nm in sys.argv[1].split(','):
            r = R.get(nm)
            picture(r, sets, os.path.join(HERE, 'cuts-%s.png' % nm.replace(':', '-')), steps=steps, title='%s (%s): cuts off the mirror planes, %d steps' % (nm, R.PLAIN.get(nm, nm), steps))
            print('cuts', nm, '%.0f s' % (time.time() - t0)); sys.stdout.flush()

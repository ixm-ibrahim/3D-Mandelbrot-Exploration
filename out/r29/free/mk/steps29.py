"""Round 29, Track A, builder: how many steps does a ray take? (numpy alone; the page's marcher written out roughly)

  python -B out/r29/free/mk/steps29.py <name> <start|second> [key=value ...]   -> prints, and logs/steps-<name>-<view>.txt

The rays of one view kept by rays29.py (logs/rays-data-*.json) are marched here with the prototype of the distance
(kit29.estimate), the way the page marches them: a stride of nine tenths of the distance, the distance never taken
under two ray thresholds (one threshold = one pixel at that depth), a stop when the distance is under a threshold or
the point is inside, at most 520 strides. Reported: strides per ray, and how many strides were taken at the least
stride (the ray creeping). With parts (nodepth=1, noballs=1, ...) the same without that piece of the distance, to see
what each piece costs or saves.
"""
import base64, json, os, sys, time
import numpy as np
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import kit29 as K

name = sys.argv[1]; view = sys.argv[2]
parts = dict((a.split('=')[0], int(a.split('=')[1])) for a in sys.argv[3:] if '=' in a)
st = dict((s[0], s) for s in K.PANEL_NEW + K.PANEL_OLD)[name]
_, p, rs, grid, depth = st
depth = parts.pop('depth', depth)
t = K.t_of(p); rho = rs / 100.0
d = json.load(open(os.path.join(os.path.dirname(HERE), 'logs', 'rays-data-%s-%s.json' % (name, view))))
w, h, fov, nx, ny = d['w'], d['h'], d['fov'], d['nx'], d['ny']
ro = np.array(d['pos']); R = np.array(d['right']); U = np.array(d['up']); F = np.array(d['f'])
PX, PY = np.meshgrid(3 + np.arange(nx) * 8 + 0.5, 3 + np.arange(ny) * 8 + 0.5)
ux = (2 * PX.ravel() - w) / h * fov; uy = (2 * (h - PY.ravel()) - h) / h * fov
rd = ux[:, None] * R + uy[:, None] * U + F; rd /= np.sqrt((rd * rd).sum(1))[:, None]
bound = d['bound']; pix = 2 * fov / h
bb = rd @ ro; hh = bb * bb - (ro @ ro) + bound * bound
ok = hh > 0
s = np.where(ok, np.maximum(-bb - np.sqrt(np.maximum(hh, 0)), 0.0), 0.0); s_out = np.where(ok, -bb + np.sqrt(np.maximum(hh, 0)), 0.0)
steps = np.zeros(len(rd), int); creep = np.zeros(len(rd), int); live = ok.copy(); hit = np.zeros(len(rd), bool)
t0 = time.time()
for it in range(520):
    idx = np.nonzero(live)[0]
    if not len(idx):
        break
    P = ro + rd[idx] * s[idx][:, None]
    dd, best, free, stt = K.estimate(P, t, rho, grid, depth, parts)
    e = pix * s[idx]
    dd = np.where(stt == 2, np.minimum(best, np.maximum(free, 2 * e)), dd)
    dd = np.maximum(dd, np.sqrt((P * P).sum(1)) - bound)                 # the solid ends at the Drawing radius
    stop = dd < e
    hit[idx[stop]] = True; live[idx[stop]] = False
    go = ~stop
    steps[idx[go]] += 1; creep[idx[go]] += dd[go] <= 2.0001 * e[go]
    s[idx[go]] += 0.9 * dd[go]
    live[idx] &= s[idx] < s_out[idx]
line = '%s %s %s: %d rays in the Drawing radius, %d stop; strides a ray: mean %.1f, median %d, nine in ten under %d, most %d; rays still going after 520: %d; strides at the least stride (creeping): %.0f %% of all (%d s)' % (
    name, view, ' '.join('%s=%s' % kv for kv in sorted(parts.items())) or '(the distance as built)', ok.sum(), hit.sum(), steps[ok].mean(), np.median(steps[ok]), np.percentile(steps[ok], 90), steps.max(), live.sum(),
    100.0 * creep.sum() / max(steps.sum(), 1), time.time() - t0)
print(line)
with open(os.path.join(os.path.dirname(HERE), 'logs', 'steps.txt'), 'a', encoding='utf-8', newline='\n') as f:
    f.write(line + '\n')

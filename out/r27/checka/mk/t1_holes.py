"""Round 27, checker A: are the places where the lab's ray does not stop at t = 1 really holes?

For a view of t = 1: take grid points where pick() stopped nowhere. Walk each such ray from the eye with the exact
inside test (the recipe, 300 rounds, "inside" only when a wall is reached), in steps of a quarter of a pixel at the
place the ray has come to, out to the Drawing radius. If the walk finds a ball, the lab's ray has gone through
something: the first ball met, how far, and how many pixels the ray stays inside it (its chord).
  python t1_holes.py <view> [rays]  -> ../logs/t1-holes-<view>.txt
"""
import json, os, sys
import numpy as np
import ballslib as B
import drive as D
import views_ref as VR

name = sys.argv[1]; nrays = int(sys.argv[2]) if len(sys.argv) > 2 else 400
info = json.load(open(os.path.join(VR.VDIR, name + '.json'), encoding='utf-8'))
cam = VR.camera(info); t, g = info['t'], info['grid']; step = info['step']
sd = np.load(os.path.join(VR.VDIR, name + '-picks.npy'))
ys, xs = np.nonzero(sd == 0)
rng = np.random.default_rng(1)
sel = rng.choice(ys.size, min(nrays, ys.size), replace=False)
px = xs[sel] * step + 0.5; py = ys[sel] * step + 0.5
dr = VR.rays(cam, px, py); ro = cam['ro']; pix = cam['pix']
# where each ray is inside the Drawing sphere
b = dr @ ro; h = b * b - (ro @ ro) + info['bound'] ** 2
t_in = np.maximum(-b - np.sqrt(np.maximum(h, 0)), 0); t_out = -b + np.sqrt(np.maximum(h, 0))
s0 = np.maximum(t_in, 2e-6)
first = np.full(sel.size, np.inf); chord = np.zeros(sel.size)
s = s0.copy(); live = np.ones(sel.size, bool); entered = np.zeros(sel.size, bool)
nstep = 0
while live.any() and nstep < 200000:
    idx = np.nonzero(live)[0]
    p = ro + dr[idx] * s[idx, None]
    st = B.recipe_state(p[:, 0], p[:, 1], p[:, 2], t, g, 300) == 1
    new = idx[st & ~entered[idx]]
    first[new] = s[new]; entered[new] = True
    left = idx[~st & entered[idx]]                      # out of its first ball again: the walk of this ray is over
    chord[left] = (s[left] - first[left]) / (pix * first[left]); live[left] = False
    s[live] *= 1 + 0.25 * pix
    gone = live & (s > t_out)
    chord[gone & entered] = (s[gone & entered] - first[gone & entered]) / (pix * first[gone & entered])
    live &= ~gone
    nstep += 1
blocked = np.isfinite(first)
lines = ['%s: grid points where the lab stops nowhere: %d of %d; %d of them walked with the exact inside test (quarter-pixel steps, %d steps at most)' % (name, ys.size, sd.size, sel.size, nstep),
         '   rays that meet a ball on the way: %d of %d; chord of the first ball met: median %.1f px, 90%% under %.1f px, largest %.1f px; with a chord over 2 px: %d, over 10 px: %d, over 50 px: %d'
         % (blocked.sum(), sel.size, np.median(chord[blocked]) if blocked.any() else 0, np.percentile(chord[blocked], 90) if blocked.any() else 0, chord[blocked].max() if blocked.any() else 0,
            (chord > 2).sum(), (chord > 10).sum(), (chord > 50).sum()),
         '   distance from the eye to that first ball: smallest %.2e, median %.2e, largest %.2e' % ((first[blocked].min(), np.median(first[blocked]), first[blocked].max()) if blocked.any() else (0, 0, 0))]
k = np.argsort(-chord)[:8]
for i in k:
    if chord[i] > 0:
        lines.append('      pixel (%d, %d): first ball met %.3e from the eye, the ray stays in it for %.1f px' % (px[i], py[i], first[i], chord[i]))
print('\n'.join(lines))
with open(os.path.join(D.LOGS, 't1-holes-%s.txt' % name), 'w', encoding='utf-8', newline='\n') as f:
    f.write('\n'.join(lines) + '\n')

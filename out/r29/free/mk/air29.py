"""Round 29, Track A, builder: a second look at the "stops in the air" of rays29.py (numpy alone).

  python -B out/r29/free/mk/air29.py <name> <start|second>   -> prints, and appends to logs/air.txt

rays29.py calls a stop "in the air" when neither the stop nor 78 points within 2.5 pixels round it are inside. Here,
for each such stop: 3000 points drawn at random within 4 pixels of it are asked, with the page's depth and with 300
rounds, and the ray itself is walked on from the stop in steps of a twentieth of a pixel for 6 pixels.
  thin:   something inside lies within 4 pixels (a part thinner than the first probe could see: the picture draws
          such parts a little thicker than they are, on purpose, so that threads do not vanish);
  depth:  inside only by the page's depth (undecided when the rounds run out), nothing inside at 300 rounds;
  air:    nothing inside within 4 pixels at all (a stop where nothing is).
"""
import base64, json, os, sys
import numpy as np
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import kit29 as K
import rays29 as R

name, view = sys.argv[1], sys.argv[2]
st = dict((s[0], s) for s in K.PANEL_NEW)[name]
_, p, rs, grid, depth = st
t = float(K.t_of(p)); rho = rs / 100.0
d = json.load(open(os.path.join(os.path.dirname(HERE), 'logs', 'rays-data-%s-%s.json' % (name, view))))
page = np.frombuffer(base64.b64decode(d['dep']), dtype=np.float32).astype(float)
nx, ny = d['nx'], d['ny']
PX, PY = np.meshgrid(3 + np.arange(nx) * R.STEP + 0.5, 3 + np.arange(ny) * R.STEP + 0.5)
ro, rd, pix = R.rays_of(d, np.stack([PX.ravel(), PY.ravel()], 1))
idx = np.nonzero(page > 0)[0]
hit = ro + rd[idx] * page[idx][:, None]; r1 = pix * page[idx]
near = K.recipe(hit, t, rho, grid, depth)
for rad in (0.8, 1.6, 2.5):
    for u in R.DIRS:
        todo = ~near
        near[todo] |= K.recipe(hit[todo] + u * (rad * r1[todo])[:, None], t, rho, grid, depth)
air = idx[~near]
rng = np.random.RandomState(29)
thin = deep = none = 0
for k in air:
    c = ro + rd[k] * page[k]; one = pix * page[k]
    v = rng.normal(size=(3000, 3)); v /= np.sqrt((v * v).sum(1))[:, None]; v *= (4 * one * rng.uniform(0, 1, 3000) ** (1 / 3.0))[:, None]
    s = page[k] + np.arange(1, 121) * 0.05 * one
    Q = np.concatenate([c + v, ro + rd[k] * s[:, None]])
    a16 = K.recipe(Q, t, rho, grid, depth)
    if not a16.any():
        none += 1
    elif K.recipe(Q[a16], t, rho, grid, 300).any():
        thin += 1
    else:
        deep += 1
line = '%s %s: %d stops, %d of them "in the air" by rays29.py; looked at again: something inside within 4 pixels at %d (thin parts), inside only by the depth of %d at %d, nothing at all at %d' % (
    name, view, len(idx), len(air), thin, depth, deep, none)
print(line)
with open(os.path.join(os.path.dirname(HERE), 'logs', 'air.txt'), 'a', encoding='utf-8', newline='\n') as f:
    f.write(line + '\n')

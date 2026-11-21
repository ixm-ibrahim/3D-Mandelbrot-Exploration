"""Round 27, checker A, bullet 2, the page's side: the lab's 3D pictures and where its rays stop.

For each view: set the dials and the camera, wait for the finished picture, save the picture alone (canvas #view,
everything over the stage hidden), then ask the lab's own pick() where the ray through the centre of a pixel stops,
at a list of random pixels (same list for every view). Results in ../views/<name>.png and <name>.json.
  python views_page.py [name ...]
"""
import json, os, sys
import numpy as np
import drive as D

VDIR = os.path.join(D.CHK, 'views')
KISS = [1.05 / 2, 0.0, 0.0]
# name: grid, t, rounds, camera (yaw, pitch, dist, target or None for the start view)
VIEWS = {
    'start-r16':        (0, 1.4, 16, None),
    'start-r40':        (0, 1.4, 40, None),
    'eye2-r16':         (0, 1.4, 16, (0.9, -0.35, 3.765, [0, 0, 0])),
    'eye2-r40':         (0, 1.4, 40, (0.9, -0.35, 3.765, [0, 0, 0])),
    'kiss-eye1-r16':    (0, 1.4, 16, (-1.25, 0.5, 0.30, KISS)),
    'kiss-eye1-r40':    (0, 1.4, 40, (-1.25, 0.5, 0.30, KISS)),
    # (my first second eye for the close-up, yaw -1.9, pitch 0.12, 0.12 away, stood INSIDE the middle ball: the picture
    #  was black, as it should be. Not a finding about the lab. These two take its place; the eye is in the plane that
    #  touches both big balls at their touching point, outside every ball: the page's own estimate there is kept in the json.)
    'kiss-eyeB-r16':    (0, 1.4, 16, (1.5708, -0.6, 0.20, KISS)),
    'kiss-eyeB-r40':    (0, 1.4, 40, (1.5708, -0.6, 0.20, KISS)),
    'hex-start-r16':    (1, 1.4, 16, None),
    'hex-kiss-r16':     (1, 1.4, 16, (-1.25, 0.5, 0.30, KISS)),
    'line-start-r16':   (2, 1.4, 16, None),
    't25-start-r16':    (0, 2.5, 16, None),
    't105-start-r16':   (0, 1.05, 16, None),      # neighbours at 90.9 % of the middle ball: how near the end of the dial do the troubles of t = 1 begin?
    't105-kiss-r16':    (0, 1.05, 16, (-1.25, 0.5, 0.30, KISS)),
    't1-start-r16':     (0, 1.0, 16, None),
    't1-start-r40':     (0, 1.0, 40, None),
    't1-side-r16':      (0, 1.0, 16, (-1.25, 0.5, 2.0, KISS)),
    't1-side-r40':      (0, 1.0, 40, (-1.25, 0.5, 2.0, KISS)),
    't1-kiss-r16':      (0, 1.0, 16, (-1.25, 0.5, 0.30, KISS)),
    't1-kiss-r40':      (0, 1.0, 40, (-1.25, 0.5, 0.30, KISS)),
}
CHUNK = 20000
DENSE = {'start-r16', 'kiss-eye1-r16'}     # a pick at every pixel; the other views at every second pixel of every second row

SET = D.HEAD + """
const g = %d, t = %r, rounds = %d, c = %s;
for (const e of $('stage').children) e.style.visibility = '';
if (!(S.mode === 'k' && S.k.group === 1)) { L.ballsShow(); await settle(); }
S.k.bt = t; S.k.bgrid = g; S.k.bit = rounds; S.flat = false; S.cutOn = false;
L.ballsFrame();
if (c) { L.cam.yaw = c[0]; L.cam.pitch = c[1]; L.cam.dist = c[2]; L.cam.target = c[3].slice(); }
go(); await sleep(300);
"""
INFO = D.HEAD + """
await settle();
for (const e of $('stage').children) if (e.id !== 'view') e.style.visibility = 'hidden';
await sleep(300);
const b = L.basis();
return JSON.stringify({ cam: L.cam, basis: b, fov: S.view.fov, bound: S.view.bound, stage: [$('stage').clientWidth, $('stage').clientHeight], canvas: [$('view').width, $('view').height],
  eyeEstimate: L.ballsEstimate(b.pos[0], b.pos[1], b.pos[2]), eyeInside: L.ballsInside(b.pos[0], b.pos[1], b.pos[2]),
  k: S.k, q: S.q, status: $('status').textContent, colour: S.colour, failed: L.R.failed || '', warn: $('ballsWarn') ? $('ballsWarn').textContent : '' });
"""
PICK = D.HEAD + """
const x0 = %d, n = %d, step = %d, W = %d, H = %d, out = [], t0 = performance.now(), ro = L.basis().pos;
const nx = Math.ceil(W / step);
for (let k = x0; k < x0 + n; k++) {
  const i = (k %% nx) * step, j = Math.floor(k / nx) * step;
  if (j >= H) break;
  const p = L.pick(i + 0.5, j + 0.5);
  out.push(p ? +Math.hypot(p[0] - ro[0], p[1] - ro[1], p[2] - ro[2]).toPrecision(8) : 0);
}
return JSON.stringify({ s: out, ms: Math.round(performance.now() - t0) });
"""

if __name__ == '__main__':
    names = sys.argv[1:] or list(VIEWS)
    os.makedirs(VDIR, exist_ok=True)
    W, H = 862, 701
    for name in names:
        g, t, R, c = VIEWS[name]
        step = 1 if name in DENSE else 2
        nx = -(-W // step); ny = -(-H // step); total = nx * ny
        steps = [D.UP, {'js': SET % (g, t, R, json.dumps(c) if c else 'null'), 'wait': 'done', 'timeout': 300},
                 {'js': INFO, 'shot': 'out/r27/checka/views/%s.png' % name, 'clip': '#view'}]
        for k in range(0, total, CHUNK):
            steps.append({'js': PICK % (k, CHUNK, step, W, H)})
        code, vals, text = D.run(D.PAGE, steps, 'view-' + name)
        if code != 0 or len(vals) < 3:
            print(name, 'RUN FAILED', code, text[-500:]); continue
        info = vals[1]
        if info['stage'] != [W, H]:
            print(name, 'the stage is', info['stage'], 'not', [W, H]); continue
        sd = []; ms = 0
        for v in vals[2:]:
            sd += v['s']; ms += v['ms']
        info.update(name=name, grid=g, t=t, rounds=R, step=step, pick_ms=ms)
        np.save(os.path.join(VDIR, name + '-picks.npy'), np.array(sd, float).reshape(ny, nx))
        with open(os.path.join(VDIR, name + '.json'), 'w', encoding='utf-8') as f:
            json.dump(info, f)
        print('%s: cam dist %.3f, picks every %d px: %d of %d stop, %d ms; %s; warn: %s' % (name, info['cam']['dist'], step, sum(1 for h in sd if h), len(sd), ms, info['status'], info['warn']))
        sys.stdout.flush()

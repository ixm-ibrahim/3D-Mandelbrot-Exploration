"""The eyes, section 1.4 c, a wider net: many views nobody chose. For each of N views a setting past 100 is drawn
(size, second sphere, grid, depth) and an eye (a target near the chain, a direction, a distance from 0.03 to 8; an
eye inside a ball is drawn again, by my own writing of the recipe in JavaScript). The numbers are put straight into
the page's state here (the dials are another checker's job), the picture is drawn, and pick() is asked at 1500
random pixels. The rays are then walked with my numpy recipe exactly as mk/walk.py does:
  HOLE in a ball   the page stops nowhere, the ray runs through solid for 2 px or more, and a point of that stretch
                   reaches a wall in 300 rounds
  SEEN THROUGH a ball   the page stops more than 2 px behind such a stretch
  IN THE OPEN      a stop with nothing solid within 3 px (78 probes, then 3000)

  python out/r28/eyes/mk/fuzz.py browser <seed> <views>    -> fuzz/<seed>.json
  python out/r28/eyes/mk/fuzz.py walk <seed>               -> logs/fuzz-<seed>.txt
"""
import base64, json, math, os, random, sys, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import eyerun as run
import recipe
MINRUN, K, NPICK = 5, 48, 1500

JS = run.HEAD + """
const V = %s, NPICK = %d;
if (!(S.mode === 'k' && S.k.group === 1)) { $('ap-balls').click(); await settle(); }
S.flat = false; S.cutOn = false;
const K2 = 1.05, S3 = Math.sqrt(3);
const near = (g, x, y) => { if (g === 2) return [Math.round(x), 0]; if (g === 0) return [Math.round(x), Math.round(y)];
  let best = null, bd = Infinity; const b0 = Math.round(y / (S3 / 2));
  for (let db = -1; db <= 1; db++) { const b = b0 + db, a = Math.round(x + b / 2), px = a - b / 2, py = b * S3 / 2, d = (x - px) * (x - px) + (y - py) * (y - py); if (d < bd) { bd = d; best = [px, py]; } }
  return best; };
// my own writing of the recipe (docs/ROUND28.md 1.1): true = solid at 300 rounds (a wall reached, or still undecided)
const solid = (g, top, rho, x, y, z) => { const ux = y, uy = z, uz = x - K2 / 2; let d = ux * ux + uy * uy + uz * uz; if (!(d > 0)) d = 1e-300;
  let mx = K2 * ux / d, my = K2 * uy / d, mz = 1 + K2 * uz / d; const r2 = rho * rho;
  for (let i = 0; i < 300; i++) { if (mz < 0 || mz > top) return true; const n = near(g, mx, my); mx -= n[0]; my -= n[1];
    const rb = mx * mx + my * my + mz * mz, rt = mx * mx + my * my + (mz - top) * (mz - top);
    if (rb < 1) { mx /= rb; my /= rb; mz /= rb; } else if (rt < r2) { const s = r2 / rt; mx *= s; my *= s; mz = top + (mz - top) * s; } else return false; }
  return true; };
let seed = V.seed >>> 0; const rnd = () => { seed = (seed * 1664525 + 1013904223) >>> 0; return seed / 4294967296; };
S.k.brho = V.rho; S.k.bt = V.t; S.k.bgrid = V.grid; S.k.bit = V.depth; S.view.bound = 8;
L.ballsFrame();
const top = 2 * V.t, R = 0.525 * V.p / 100;
// the eye: a target near the chain, a direction, a distance; drawn again while the eye, or a point a hair round it, is solid
let tries = 0, eye = null, tgt = null, yaw = 0, pitch = 0, dist = 0;
for (; tries < 200; tries++) {
  const along = (rnd() * 2 - 1) * (0.525 + 2 * R + 0.3), side = (rnd() * 2 - 1) * Math.min(R, 2), up = (rnd() * 2 - 1) * Math.min(R, 2);
  tgt = [along, side * rnd(), up * rnd()];
  yaw = rnd() * 2 * Math.PI - Math.PI; pitch = Math.asin(rnd() * 1.8 - 0.9); dist = Math.exp(Math.log(0.03) + rnd() * Math.log(8 / 0.03));
  const cp = Math.cos(pitch); eye = [tgt[0] + dist * cp * Math.cos(yaw), tgt[1] + dist * cp * Math.sin(yaw), tgt[2] + dist * Math.sin(pitch)];
  if (Math.hypot(eye[0], eye[1], eye[2]) > 0.9 * S.view.bound) continue;
  let bad = solid(V.grid, top, V.rho, eye[0], eye[1], eye[2]);
  for (let k = 0; k < 40 && !bad; k++) { const a = rnd() * 6.283, c = rnd() * 2 - 1, s = Math.sqrt(1 - c * c), r = 0.004 * dist + 1e-4; bad = solid(V.grid, top, V.rho, eye[0] + r * s * Math.cos(a), eye[1] + r * s * Math.sin(a), eye[2] + r * c); }
  if (!bad) break;
}
if (tries >= 200) return JSON.stringify({ meta: { name: V.name, failed: 'no free eye in 200 tries' } });
L.cam.yaw = yaw; L.cam.pitch = pitch; L.cam.dist = dist; L.cam.target = tgt.slice(); go();
await settle();
const w = $('stage').clientWidth, h = $('stage').clientHeight, b = L.basis(), fov = S.view.fov, ro = b.pos, pix = 2 * fov / h;
const o300 = { t: V.t, grid: V.grid, rounds: 300, rho: V.rho, parts: true };
const px = new Float32Array(NPICK), py = new Float32Array(NPICK), dep = new Float32Array(NPICK), met = new Float32Array(NPICK);
for (let i = 0; i < NPICK; i++) { px[i] = Math.floor(rnd() * w) + 0.5; py[i] = Math.floor(rnd() * h) + 0.5; const p = L.pick(px[i], py[i]);
  if (p) { const sd = Math.hypot(p[0] - ro[0], p[1] - ro[1], p[2] - ro[2]); dep[i] = sd; met[i] = L.ballsEstimate(p[0], p[1], p[2], o300)[0] / (pix * sd); } }
const b64 = a => { const u = new Uint8Array(a.buffer); let s = ''; for (let i = 0; i < u.length; i += 8192) s += String.fromCharCode.apply(null, u.subarray(i, i + 8192)); return btoa(s); };
return JSON.stringify({ meta: { name: V.name, p: V.p, k: { bt: S.k.bt, brho: S.k.brho, bgrid: S.k.bgrid, bit: S.k.bit }, w, h, fov, pix, bound: S.view.bound, ro, right: b.right, up: b.up, f: b.f, cam: [yaw, pitch, dist, tgt], tries, status: $('status').textContent, sig: String(L.R.sig).trim() },
  px: b64(px), py: b64(py), dep: b64(dep), met: b64(met) });
"""


def draw(seed, n):
    rng = random.Random(seed)
    out = []
    for i in range(n):
        p = rng.choice([101, 110, 125, 150, 150, 175, 199.9, 200, 250, 300, 300, 400, 550, 800, 1000, 2000])
        kind = rng.random()
        if kind < 0.35:
            rho = max(0.02, min(0.5, 50.0 / p))                      # what the size dial makes it
        elif kind < 0.6:
            rho = min(0.5, 100.0 / p)                               # the two spheres touch
        else:
            rho = round(rng.uniform(0.02, min(0.5, 100.0 / p)), 4)  # anything the second-sphere dial allows
        out.append(dict(name='f%d-%02d' % (seed, i), seed=seed * 1000 + i, p=p, t=0.5 * (100.0 / p + 1), rho=rho, grid=rng.choice([0, 0, 1, 2]), depth=rng.choice([16, 16, 16, 40, 100])))
    return out


def browser(seed, n):
    vs = draw(seed, n)
    steps = [run.UP] + [{'js': JS % (json.dumps(v), NPICK), 'wait': 'done', 'timeout': 600} for v in vs]
    t0 = time.time()
    code, text, vals = run.shot(run.PAGE, steps, 'fuzz-%d' % seed, '1400x950', 'dark')
    run.write('fuzz-%d.log' % seed, text + 'exit %d, %.0f s\n' % (code, time.time() - t0))
    os.makedirs(os.path.join(run.EYES, 'fuzz'), exist_ok=True)
    got = [json.loads(v) for v in vals if v.startswith('{"meta"')]
    json.dump(got, open(os.path.join(run.EYES, 'fuzz', '%d.json' % seed), 'w', encoding='utf-8'))
    print('seed %d: exit %d, %s, %d of %d views back, %.0f s' % (seed, code, 'no console errors' if run.clean(text) else 'SEE THE LOG', len(got), n, time.time() - t0))
    if code != 0:
        print(text[-1500:])


def arr(s):
    return np.frombuffer(base64.b64decode(s), dtype=np.float32).astype(np.float64)


def walk_one(d):
    m = d['meta']
    if m.get('failed'):
        return dict(view=m['name'], failed=m['failed'])
    top = 2 * m['k']['bt']; rho = m['k']['brho']; grid = m['k']['bgrid']; rounds = m['k']['bit']
    ro = np.array(m['ro']); pix = m['pix']; bound = m['bound']; w, h, fov = m['w'], m['h'], m['fov']
    px, py, dep, met = arr(d['px']), arr(d['py']), arr(d['dep']), arr(d['met'])
    ux = (2 * px - w) / h * fov; uy = (2 * (h - py) - h) / h * fov
    R, U, F = (np.array(m[k]) for k in ('right', 'up', 'f'))
    rd = ux[:, None] * R + uy[:, None] * U + F; rd /= np.linalg.norm(rd, axis=1)[:, None]
    n = rd.shape[0]
    sol = lambda P: recipe.solid(P, top, rho, grid, rounds)
    b = rd @ ro; hh = b * b - ro @ ro + bound * bound; inb = hh > 0; sq = np.sqrt(np.where(inb, hh, 0))
    s_in = np.maximum(-b - sq, 0.0); s_out = np.where(inb, -b + sq, -1.0)
    # how far the nearest solid point is from the eye along these rays (steps a fiftieth longer each time)
    s = 1e-5; near = None
    while s < 2 * bound + np.linalg.norm(ro):
        ok = (s >= s_in) & (s <= s_out)
        if ok.any() and sol(ro + rd[ok] * s).any():
            near = s; break
        s *= 1.02
    q = 1 + 0.5 * pix
    s_cur = np.maximum(s_in, 0.5 * near if near else 1e9)
    run_ = np.zeros(n, dtype=np.int32); run_s1 = np.zeros(n); big_s1 = np.zeros(n); big_s2 = np.zeros(n); big_n = np.zeros(n, dtype=np.int32)
    done = ~inb | (s_cur >= s_out); pw = q ** np.arange(K)
    while True:
        act = np.nonzero(~done)[0]
        if act.size == 0:
            break
        sv = s_cur[act, None] * pw[None, :]
        P = ro[None, None, :] + rd[act][:, None, :] * sv[:, :, None]
        inside = sv <= s_out[act, None]
        so = np.zeros(sv.shape, dtype=bool); so[inside] = sol(P[inside])
        r = run_[act]; r1 = run_s1[act]; B1 = big_s1[act]; B2 = big_s2[act]; BN = big_n[act]; fin = np.zeros(act.size, dtype=bool)
        prev = np.where(r > 0, s_cur[act] / q, 0.0)
        for k in range(K):
            sk = so[:, k] & ~fin
            r1 = np.where(sk & (r == 0), sv[:, k], r1)
            bigend = ~so[:, k] & (r >= MINRUN) & ~fin
            B1 = np.where(bigend, r1, B1); B2 = np.where(bigend, prev, B2); BN = np.where(bigend, r, BN)
            fin |= bigend
            r = np.where(sk, r + 1, np.where(fin, r, 0))
            prev = np.where(sk, sv[:, k], prev)
        run_[act] = r; run_s1[act] = r1; big_s1[act] = B1; big_s2[act] = B2; big_n[act] = BN
        s_cur[act] = sv[:, -1] * q
        over = s_cur[act] > s_out[act]
        oe = over & ~fin & (r >= MINRUN)
        if oe.any():
            a = act[oe]; big_s1[a] = run_s1[a]; big_s2[a] = np.minimum(s_cur[a] / q, s_out[a]); big_n[a] = run_[a]
        done[act] = fin | over
    has_big = big_n >= MINRUN; hit = dep > 0; miss = ~hit
    def ball(a):
        sv = big_s1[a] * q ** np.arange(int(big_n[a]))
        return bool((recipe.verdict(ro + rd[a] * sv[:, None], top, rho, grid, 300) == 1).any())
    holes = np.nonzero(miss & has_big)[0]; thru = np.nonzero(hit & has_big & (dep > big_s2 * (1 + 2 * pix)))[0]
    hole_ball = [int(a) for a in holes if ball(a)]; thru_ball = [int(a) for a in thru if ball(a)]
    hidx = np.nonzero(hit)[0]; Pst = ro + rd[hidx] * dep[hidx, None]; one = pix * dep[hidx]
    dirs = np.array([[a, bq, c] for a in (-1, 0, 1) for bq in (-1, 0, 1) for c in (-1, 0, 1) if a or bq or c], dtype=np.float64); dirs /= np.linalg.norm(dirs, axis=1)[:, None]
    nearb = sol(Pst).copy() if hidx.size else np.zeros(0, dtype=bool)
    for kk in (0.8, 1.6, 2.5):
        left = np.nonzero(~nearb)[0]
        if left.size == 0:
            break
        Q = Pst[left][:, None, :] + kk * one[left][:, None, None] * dirs[None, :, :]
        nearb[left] = sol(Q.reshape(-1, 3)).reshape(left.size, -1).any(axis=1)
    left = np.nonzero(~nearb)[0]; rng = np.random.default_rng(28); opened = []
    for a in left:
        v = rng.normal(size=(3000, 3)); v /= np.linalg.norm(v, axis=1)[:, None]; v *= (rng.random(3000) ** (1 / 3))[:, None] * 3.0
        if not sol(Pst[a] + one[a] * v).any():
            opened.append(int(hidx[a]))
    return dict(view=m['name'], p=m['p'], rho=rho, grid=grid, depth=rounds, cam=m['cam'], eye=[round(float(x), 4) for x in ro], nearest=near, rays=int(n), stops=int(hit.sum()),
                through2px=int(has_big.sum()), HOLES=int(holes.size), HOLES_IN_A_BALL=len(hole_ball), longestHolePx=float((big_n[holes] * 0.5).max()) if holes.size else 0.0,
                SEEN_THROUGH=int(thru.size), SEEN_THROUGH_A_BALL=len(thru_ball), IN_THE_OPEN=len(opened), openWorstPagePx=float(met[opened].max()) if opened else 0.0,
                pageMetOver2px=int((met[hit] > 2).sum()), pageMetWorstPx=float(met[hit].max()) if hit.any() else 0.0,
                where=[[float(px[a]), float(py[a])] for a in (hole_ball + thru_ball + opened)[:8]], status=m['status'], sig=m['sig'])


def walk(seed):
    ds = json.load(open(os.path.join(run.EYES, 'fuzz', '%d.json' % seed), encoding='utf-8'))
    lines = []; tot = dict(views=0, rays=0, stops=0, H=0, HB=0, T=0, TB=0, O=0)
    for d in ds:
        r = walk_one(d)
        if r.get('failed'):
            lines.append('%s: %s' % (r['view'], r['failed'])); continue
        tot['views'] += 1; tot['rays'] += r['rays']; tot['stops'] += r['stops']; tot['H'] += r['HOLES']; tot['HB'] += r['HOLES_IN_A_BALL']; tot['T'] += r['SEEN_THROUGH']; tot['TB'] += r['SEEN_THROUGH_A_BALL']; tot['O'] += r['IN_THE_OPEN']
        lines.append('%-9s size %-6s second sphere %6.2f %% grid %d depth %-3d | eye %s, %.3g from the nearest solid point, yaw %.3f pitch %.3f dist %.4f target %s | rays %d: stop %d, through solid for 2 px or more %d | '
                     'HOLES %d (in a ball: %d, longest %.1f px), SEEN THROUGH %d (a ball: %d), IN THE OPEN %d (page %.1f px) | page\'s own measure over 2 px: %d, worst %.1f px%s | %s'
                     % (r['view'], r['p'], 100 * r['rho'], r['grid'], r['depth'], r['eye'], r['nearest'] or -1, r['cam'][0], r['cam'][1], r['cam'][2], [round(x, 3) for x in r['cam'][3]], r['rays'], r['stops'], r['through2px'],
                        r['HOLES'], r['HOLES_IN_A_BALL'], r['longestHolePx'], r['SEEN_THROUGH'], r['SEEN_THROUGH_A_BALL'], r['IN_THE_OPEN'], r['openWorstPagePx'], r['pageMetOver2px'], r['pageMetWorstPx'],
                        ' | at pixels %s' % r['where'] if r['where'] else '', r['status']))
        print(lines[-1]); sys.stdout.flush()
    lines.append('seed %d: views %d, rays %d, stops %d: HOLES %d (in a ball %d), SEEN THROUGH %d (through a ball %d), IN THE OPEN %d' % (seed, tot['views'], tot['rays'], tot['stops'], tot['H'], tot['HB'], tot['T'], tot['TB'], tot['O']))
    print(lines[-1])
    open(os.path.join(run.EYES, 'logs', 'fuzz-%d.txt' % seed), 'w', encoding='utf-8', newline='\n').write('\n'.join(lines) + '\n')


if __name__ == '__main__':
    if sys.argv[1] == 'browser':
        browser(int(sys.argv[2]), int(sys.argv[3]))
    else:
        walk(int(sys.argv[2]))

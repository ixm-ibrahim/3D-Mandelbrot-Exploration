"""Round 28, Track A, builder, test 3: one recipe, three voices.

  python out/r28/dials/mk/voices.py            -> out/r28/dials/logs/voices.txt
  python out/r28/dials/mk/voices.py extreme    -> out/r28/dials/logs/voices-extreme.txt (the ends of the dials)

For each setting (rho, p, grid):
  the twin, ballsInside, at 20000 random points of a box round the object (the page's depth 16, and 60 rounds),
  the shader, through sampleSlice from the program the picture is drawn with: the flat view on a 142 x 142 grid
    (20164 points) and in space on twenty 32 x 32 grids at random heights (20480 points), at the page's depth,
  my own plain numpy writing of the recipe of ROUND28.md section 1.1 (kit28.recipe), asked for the same points.
The random points are made by the same small generator on both sides (mulberry32), so only verdicts travel.
Also, in the page: the shader's distance against the twin's ballsEstimate at the same grid points.
"""
import json, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import run28 as run
import kit28 as K

# (name, rho, p, grid)
SETS = [('rho 0.5, p 150, square', 0.5, 150.0, 0), ('rho 0.25, p 300, square', 0.25, 300.0, 0),
        ('rho 1/3, p 150, honeycomb', 1 / 3.0, 150.0, 1), ('rho 1/6, p 300, line', 1 / 6.0, 300.0, 2),
        ('rho 0.5, p 200 (the spheres touch), square', 0.5, 200.0, 0), ('rho 0.05, p 1000, honeycomb', 0.05, 1000.0, 1),
        ('rho 0.4, p 60, square', 0.4, 60.0, 0), ('rho 1, p 55.56 (as the page opens), square', 1.0, 100 / 1.8, 0)]
# the ends of the dials (python voices.py extreme): the largest and smallest sizes that can be typed, the smallest second sphere
EXTREME = [('rho 0.025, p 2000, square', 0.025, 2000.0, 0), ('rho 0.5, p 1, square', 0.5, 1.0, 0), ('rho 0.02, p 55.56, honeycomb', 0.02, 100 / 1.8, 1),
           ('rho 0.02, p 400, line', 0.02, 400.0, 2), ('rho 0.5, p 199.9 (all but touching), square', 0.5, 199.9, 0), ('rho 1, p 2 (the old lower end), square', 1.0, 2.0, 0)]
N = 20000

PRE = run.HEAD + """
window.__V = {};
const V = window.__V;
V.rng = seed => { let a = seed | 0; return () => { a |= 0; a = (a + 0x6D2B79F5) | 0; let t = Math.imul(a ^ (a >>> 15), 1 | a); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; };
$('ap-balls').click(); await settle();
return 'Balls on balls on show: ' + $('status').textContent;
"""
ONE = run.HEAD + """
const V = window.__V, rho = %r, t = %r, g = %d, bx = %r, by = %r, seed = %d, N = %d;
S.k.brho = rho; S.k.bt = t; S.k.bgrid = g; S.k.bit = 16; S.flat = false; S.cutOn = false; go(); await settle();
const rnd = V.rng(seed), o16 = { t, grid: g, rounds: 16, rho }, o60 = { t, grid: g, rounds: 60, rho };
let a16 = '', a60 = '', aPage = '';
for (let i = 0; i < N; i++) { const x = (2 * rnd() - 1) * bx, y = (2 * rnd() - 1) * by, z = (2 * rnd() - 1) * by; a16 += L.ballsInside(x, y, z, o16) ? '1' : '0'; a60 += L.ballsInside(x, y, z, o60) ? '1' : '0'; aPage += L.ballsInside(x, y, z) ? '1' : '0'; }
// the shader
const out = { sig: L.R.sig.replace(/\\n/g, '/'), rhoPage: S.k.brho, tPage: S.k.bt, a16, a60, samePage: aPage === a16, slices: [], est: { n: 0, worst: 0, over: 0, signs: 0 } };
const side = 2 * Math.max(bx, by);
const slice = async (n, z) => {
  const cx = 0.02 * (rnd() - 0.5), cy = 0.02 * (rnd() - 0.5);
  const snap = L.takeSnapshot(), arr = await L.sampleSlice(snap, cx, cy, side, z, n); L.releaseSnapshot(snap);
  if (!arr) fail('sampleSlice gave nothing');
  let s = '';
  for (let j = 0; j < n; j++) for (let i = 0; i < n; i++) {
    const d = arr[4 * (j * n + i) + 3]; s += !(d > 0) ? '1' : '0';
    // the distance: the shader's against the twin's, where both say outside
    const x = cx + side * ((i + 0.5) / n - 0.5), y = cy + side * ((j + 0.5) / n - 0.5), e = L.ballsEstimate(x, y, z, o16);
    if ((d > 0) !== (e > 0)) out.est.signs++;
    else if (d > 0) { out.est.n++; const r = Math.abs(d - e) / Math.max(e, 1e-4); if (r > out.est.worst) out.est.worst = r; if (r > 0.01) out.est.over++; }
  }
  out.slices.push({ n, z, cx, cy, side, bits: s });
};
await slice(142, 0);
for (let k = 0; k < 20; k++) { await slice(32, (2 * rnd() - 1) * by); await sleep(5); }
return JSON.stringify(out);
"""


def mulberry(seed):
    a = seed & 0xFFFFFFFF

    def imul(x, y):
        return (x * y) & 0xFFFFFFFF

    def nxt():
        nonlocal a
        a = (a + 0x6D2B79F5) & 0xFFFFFFFF
        t = imul(a ^ (a >> 15), 1 | a)
        t = ((t + imul(t ^ (t >> 7), 61 | t)) & 0xFFFFFFFF) ^ t
        return ((t ^ (t >> 14)) & 0xFFFFFFFF) / 4294967296.0
    return nxt


if __name__ == '__main__':
    extreme = len(sys.argv) > 1 and sys.argv[1] == 'extreme'
    if extreme:
        SETS = EXTREME
    tagname = 'voices-extreme' if extreme else 'voices'
    page = run.PAGE
    steps = [run.UP, {'js': PRE, 'wait': 'done', 'timeout': 900}]
    meta = []
    for k, (name, rho, p, g) in enumerate(SETS):
        top = 1 + 100.0 / p; t = top / 2
        rc = K.reach(top, rho); bx = float(round(min(rc if np.isfinite(rc) else 6.0, 6.0) + 0.3, 3))
        by = float(round(max(K.K2 * p / 200, K.K2 / 2 + K.K2 / (2 * top - 1)) + 0.3, 3)); by = min(by, 4.0); rho = float(rho); t = float(t)
        seed = 20261120 + 977 * k
        meta.append((name, rho, t, g, bx, by, seed))
        steps.append({'js': ONE % (rho, t, g, bx, by, seed, N), 'wait': 'done', 'timeout': 900})
    code, text, vals = run.shot(page, steps, tagname, '1400x950', 'dark')
    run.write(tagname + '.log', text + 'exit %d\n' % code)
    lines = ['page %s, exit %d, %s' % (page, code, 'no console errors' if run.clean(text) else 'SEE logs/%s.log' % tagname)]
    tot = [0, 0, 0, 0]
    for (name, rho, t, g, bx, by, seed), v in zip(meta, vals[2:]):
        d = json.loads(v)
        rnd = mulberry(seed)
        P = np.array([[(2 * rnd() - 1) * bx, (2 * rnd() - 1) * by, (2 * rnd() - 1) * by] for _ in range(N)])
        m16 = K.recipe(P[:, 0], P[:, 1], P[:, 2], t, rho, g, 16) != 0; m60 = K.recipe(P[:, 0], P[:, 1], P[:, 2], t, rho, g, 60) != 0
        t16 = np.array([c == '1' for c in d['a16']]); t60 = np.array([c == '1' for c in d['a60']])
        lines.append('=== %s (t = %.6f; box +-%.3f by +-%.3f; program %s; the page holds rho %s, t %s)' % (name, t, bx, by, d['sig'], d['rhoPage'], d['tPage']))
        lines.append('  twin against my writing, %d points in space: 16 rounds: inside by the twin %d, by me %d, verdicts that differ %d; 60 rounds: inside %d / %d, differ %d; the twin with nothing passed (read from the page) gives the same as with the numbers passed: %s'
                     % (N, int(t16.sum()), int(m16.sum()), int((t16 != m16).sum()), int(t60.sum()), int(m60.sum()), int((t60 != m60).sum()), d['samePage']))
        tot[0] += int((t16 != m16).sum()) + int((t60 != m60).sum())
        fl = [0, 0]; sp = [0, 0]; hair = []
        for s in d['slices']:
            for _ in range(2):
                rnd()                                                    # (the two numbers the page drew for the offset of this grid; not needed: it sent them)
            n = s['n']; idx = (np.arange(n) + 0.5) / n - 0.5
            X = (s['cx'] + s['side'] * idx[None, :] + np.zeros((n, 1))).ravel(); Y = (s['cy'] + s['side'] * idx[:, None] + np.zeros((1, n))).ravel(); Z = np.full(n * n, s['z'])
            mine = K.recipe(X, Y, Z, t, rho, g, 16) != 0; sh = np.array([c == '1' for c in s['bits']])
            bad = sh != mine
            tgt = fl if s['z'] == 0 else sp
            tgt[0] += n * n; tgt[1] += int(bad.sum())
            if bad.any():
                # how close to a skin are the points that differ? (my estimate of the distance there)
                best, free, st = K.estimate(X[bad], Y[bad], Z[bad], t, rho, g, 16)
                hair += list(np.abs(best))
            if s['n'] == 32:
                rnd()                                                    # the height of the next grid was drawn before its offset
        lines.append('  shader (sampleSlice, 16 rounds) against my writing: flat view %d points, verdicts that differ %d; in space %d points, differ %d%s'
                     % (fl[0], fl[1], sp[0], sp[1], '; the points that differ lie within %.2e of a skin (largest)' % max(hair) if hair else ''))
        e = d['est']
        lines.append('  shader distance against the twin\'s ballsEstimate where both say outside: %d points, worst relative difference %.2e, more than 1 %% apart at %d; one says inside and the other outside at %d'
                     % (e['n'], e['worst'], e['over'], e['signs']))
        tot[1] += fl[1]; tot[2] += sp[1]; tot[3] += e['over']
    lines.append('TOTAL: twin against my writing %d verdicts differ; shader against my writing: flat %d, in space %d; distances more than 1 %% apart %d' % tuple(tot))
    out = '\n'.join(lines) + '\n'
    run.write(tagname + '.txt', out); print(out)
    if code != 0:
        print(text[-3000:])

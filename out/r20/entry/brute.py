"""Round 20, entry: plain point-by-point cuts through Julia sets of "Wind, then square", worked with the page's own
MATH in JavaScript's 64-bit numbers (no distance estimate, no shader). A point is in the set when its orbit is still
within 64 after `its` steps, the page's own test. JULIA SETS ONLY.
  python out/r20/entry/brute.py <list>     -> brute-<tag>.png, brute-<list>.txt
Each cut: tag, id (MATH name), n, c, o (centre), u and w (the two directions of the picture), W (width), its."""
import base64, json, math, os, sys
import numpy as np
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import run

JS = r"""
const L = window.squaringLab, M = L.MATH;
const CUTS = __CUTS__;
const out = [];
for (const q of CUTS) {
  const N = q.N;
  const F = q.id === 'complex' ? (v => { let a = 1, b = 0; for (let i = 0; i < q.n; i++) [a, b] = [a * v[0] - b * v[1], a * v[1] + b * v[0]]; return [a, b, 0]; }) : (v => M[q.id](v, q.n, {}));
  const g = new Uint8Array(N * N);
  let ins = 0;
  for (let j = 0; j < N; j++) for (let i = 0; i < N; i++) {
    const a = q.W * ((i + 0.5) / N - 0.5), b = -q.W * ((j + 0.5) / N - 0.5);
    const p = [q.o[0] + a * q.u[0] + b * q.w[0], q.o[1] + a * q.u[1] + b * q.w[1], q.o[2] + a * q.u[2] + b * q.w[2]];
    const c = q.c;
    let z = p, e = 0;
    for (let s = 0; s <= q.its; s++) {
      if (!(Math.hypot(z[0], z[1], z[2]) <= 64)) { e = s + 1; break; }
      if (s === q.its) break;
      const f = F(z); z = [f[0] + c[0], f[1] + c[1], f[2] + c[2]];
    }
    g[j * N + i] = Math.min(e, 255); if (!e) ins++;
  }
  let bin = ''; for (let k = 0; k < g.length; k += 8192) bin += String.fromCharCode(...g.subarray(k, k + 8192));
  out.push({ tag: q.tag, inside: ins / (N * N), rows: btoa(bin) });
}
return JSON.stringify(out);
"""
X, Y, Z = [1, 0, 0], [0, 1, 0], [0, 0, 1]
def P(deg):
    a = math.radians(deg); return [0, math.cos(a), math.sin(a)]
BAS, RAB, SIE, DEN = [-1, 0, 0], [-0.122561, 0.744862, 0], [-0.390541, -0.586788, 0], [0, 1, 0]
W = 'windsq'


def cut(tag, c, o, u, w, Wd, its=40, n=2, N=360, id_=W):
    return dict(tag=tag, id=id_, n=n, c=c, o=o, u=u, w=w, W=Wd, its=its, N=N)


def basilica():
    return [
        cut('bas-x0', BAS, [0, 0, 0], Y, Z, 2.4),
        cut('bas-neck', BAS, [-0.618034, 0, 0], Y, Z, 0.2),
        cut('bas-xm03', BAS, [-0.3, 0, 0], Y, Z, 2.4, its=80, N=480),
        cut('bas-p30', BAS, [0, 0, 0], X, P(30), 3.6),
        cut('bas-p60', BAS, [0, 0, 0], X, P(60), 3.6),
        cut('bas-p90', BAS, [0, 0, 0], X, P(90), 3.6),
        cut('bas-skin-a', BAS, [0, 0.45, 0.26], Y, Z, 0.5, its=80, N=480),
        cut('bas-skin-b', BAS, [0, 0.45, 0.26], Y, Z, 0.12, its=80, N=480),
        cut('bas-bud60-a', BAS, [0, 0.3, 0.52], Y, Z, 0.5, its=80, N=480),
        cut('bas-bud-side', BAS, [0, 0.3, 0.52], X, [0, -math.sin(math.radians(60)), math.cos(math.radians(60))], 0.5, its=80, N=480),
    ]


def others():
    return [
        cut('rab-flat', RAB, [0, 0, 0], X, Y, 3.2),
        cut('rab-p60', RAB, [0, 0, 0], X, P(60), 3.2),
        cut('rab-p120', RAB, [0, 0, 0], X, P(120), 3.2),
        cut('rab-p30', RAB, [0, 0, 0], X, P(30), 3.2),
        cut('rab-x0', RAB, [0, 0, 0], Y, Z, 3.0, N=480),
        cut('rab-p10', RAB, [0, 0, 0], X, P(10), 3.2),
        cut('sie-x0', SIE, [0, 0, 0], Y, Z, 3.0, N=480),
        cut('sie-p30', SIE, [0, 0, 0], X, P(30), 3.2),
        cut('sie-p60', SIE, [0, 0, 0], X, P(60), 3.2),
        cut('den-x0', DEN, [0, 0, 0], Y, Z, 3.0, its=20),
        cut('den-p60', DEN, [0, 0, 0], X, P(60), 3.2, its=20),
    ]


# whole powers 2 to 5: the cut across the x-axis (the count round the axis), and the flat cut against plain complex arithmetic
POW = ((2, BAS, 'c = -1'), (3, [0.3, 0, 0], 'c = 0.3'), (4, BAS, 'c = -1'), (5, [0.3, 0, 0], 'c = 0.3'), (3, [0, 1, 0], 'c = i'), (4, [0.3, 0.3, 0], 'c = 0.3 + 0.3i'))


def powers():
    out = []
    for n, c, nm in POW:
        t = 'n%d-%s' % (n, nm.replace('c = ', 'c').replace(' ', '').replace('+', 'p').replace('.', '').replace('-', 'm'))
        out.append(cut(t + '-x0', c, [0, 0, 0], Y, Z, 2.6, its=30, n=n))
        out.append(cut(t + '-flat', c, [0, 0, 0], X, Y, 3.0, its=30, n=n, N=400))
        out.append(cut(t + '-flatref', c, [0, 0, 0], X, Y, 3.0, its=30, n=n, N=400, id_='complex'))
    return out


def ribs():
    CAU, SM = [0.25, 0, 0], [-0.75, 0, 0]
    return [
        cut('cau-x0', CAU, [0, 0, 0], Y, Z, 2.0, N=480),
        cut('cau-skin', CAU, [0, 0.52, 0.3], Y, Z, 0.3, its=80, N=480),
        cut('cau-p30', CAU, [0, 0, 0], X, P(30), 2.4),
        cut('sm-x0', SM, [0, 0, 0], Y, Z, 2.4, N=480),
        cut('sm-xm03', SM, [-0.3, 0, 0], Y, Z, 2.4, its=80, N=480),
        cut('sm-skin', SM, [0, 0.55, 0.32], Y, Z, 0.3, its=80, N=480),
        cut('bas-x02', BAS, [0.2, 0, 0], Y, Z, 2.4, its=80, N=480),
        cut('bas-x02-skin', BAS, [0.2, 0.42, 0.24], Y, Z, 0.3, its=80, N=480),
    ]


LISTS = {'basilica': basilica, 'others': others, 'powers': powers, 'ribs': ribs}


def lobes(g):
    """how many lobes the inside has round the middle of the picture: the outline's radius by direction, peaks counted"""
    N = g.shape[0]; ins = g == 0
    yy, xx = np.mgrid[0:N, 0:N]; dx = xx - (N - 1) / 2; dy = (N - 1) / 2 - yy
    r = np.hypot(dx, dy); th = (np.degrees(np.arctan2(dy, dx)) % 360)
    prof = np.zeros(360)
    b = np.floor(th[ins]).astype(int) % 360
    np.maximum.at(prof, b, r[ins])
    k = np.ones(5) / 5; sm = np.convolve(np.concatenate([prof[-5:], prof, prof[:5]]), k, 'same')[5:-5]
    if sm.max() <= 0:
        return 0, []
    peaks = []
    for i in range(360):
        w = [sm[(i + d) % 360] for d in range(-8, 9)]
        if sm[i] == max(w) and sm[i] > 1.04 * min(sm[(i + d) % 360] for d in range(-18, 19)) and (not peaks or (i - peaks[-1]) > 8):
            peaks.append(i)
    return len(peaks), peaks


def go(name):
    cuts = LISTS[name]()
    js = JS.replace('__CUTS__', json.dumps(cuts))
    steps = [run.UP, {'js': js, 'timeout': 1800}]
    code, text, vals = run.shot(run.PAGE, steps, 'brute-%s-steps' % name)
    res = json.loads(vals[-1]); lines = []; grids = {}
    for q, r in zip(cuts, res):
        N = q['N']
        g = np.frombuffer(base64.b64decode(r['rows']), np.uint8).reshape(N, N).astype(float)
        grids[q['tag']] = g
        im = np.zeros((N, N, 3), np.uint8); ins = g == 0
        v = np.clip((g - 1) / max(q['its'] - 1, 1), 0, 1)
        im[..., 0] = 14 + 60 * v; im[..., 1] = 18 + 90 * v; im[..., 2] = 30 + 150 * v
        im[ins] = (236, 226, 200)
        Image.fromarray(im).resize((2 * N, 2 * N), Image.NEAREST).save(os.path.join(HERE, 'brute-%s.png' % q['tag']))
        extra = ''
        if q['tag'].endswith('-x0'):
            k, pk = lobes(g); extra = '; lobes round the middle: %d (at %s degrees)' % (k, ', '.join(str(p) for p in pk))
        if q['tag'].endswith('-flat'):
            pass
        lines.append('brute-%s.png: %s, n %s, c = %s, centre %s, across %s, up %s, %.3g wide, %d steps, %d x %d points, in the set: %.2f %%%s' % (
            q['tag'], q['id'], q['n'], q['c'], q['o'], [round(x, 3) for x in q['u']], [round(x, 3) for x in q['w']], q['W'], q['its'], N, N, 100 * r['inside'], extra))
    for t in list(grids):
        if t.endswith('-flat') and t + 'ref' in grids:
            a, b = grids[t] == 0, grids[t + 'ref'] == 0
            lines.append('flat cut %s against plain complex arithmetic: %d of %d points differ (in the set: %d and %d)' % (t, int((a != b).sum()), a.size, int(a.sum()), int(b.sum())))
    run.write('brute-%s.txt' % name, '\n'.join(l for l in text.splitlines() if 'result: [' not in l) + '\n' + '\n'.join(lines) + '\n')
    print('\n'.join(lines))
    return code


if __name__ == '__main__':
    sys.exit(go(sys.argv[1]))

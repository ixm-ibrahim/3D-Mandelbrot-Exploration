"""Round 16, entry: plain point-by-point cuts through a solid, worked with the page's own MATH in JavaScript's 64-bit
numbers (no distance estimate, no shader). A point is in the solid when its orbit is still within 64 after `its` steps,
the page's own test.   python out/r16/entry/brute.py <list>     -> brute-<tag>.png, brute-<list>.txt
Each cut: tag, id (MATH name), n, mode ('j' with c, or 'm'), o (centre), u and w (the two directions of the picture), W (width), its."""
import base64, json, os, sys
import numpy as np
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import run

JS = r"""
const L = window.squaringLab, M = L.MATH;
const CUTS = __CUTS__;
const N = __N__, out = [];
for (const q of CUTS) {
  const F = q.id === 'fold' ? (v => M.fold(v, q.n, { planes: 2 })) : (v => M[q.id](v, q.n, {}));
  const g = new Uint8Array(N * N);
  let ins = 0;
  for (let j = 0; j < N; j++) for (let i = 0; i < N; i++) {
    const a = q.W * ((i + 0.5) / N - 0.5), b = -q.W * ((j + 0.5) / N - 0.5);
    const p = [q.o[0] + a * q.u[0] + b * q.w[0], q.o[1] + a * q.u[1] + b * q.w[1], q.o[2] + a * q.u[2] + b * q.w[2]];
    const c = q.mode === 'm' ? p : q.c;
    let z = q.mode === 'm' ? [0, 0, 0] : p, e = 0;
    for (let s = 0; s <= q.its; s++) {
      if (!(Math.hypot(z[0], z[1], z[2]) <= 64)) { e = s; break; }
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
S2 = 0.7071067811865476
X, Y, Z, D1 = [1, 0, 0], [0, 1, 0], [0, 0, 1], [0, S2, S2]
BAS = [-1, 0, 0]
RULES = (('ta', 'turnaway'), ('tl', 'turnalong'), ('f2', 'fold'))


def first():
    out = []
    for t, i in RULES:
        for its in (14, 40):
            out.append(dict(tag='%s-bas-x0-%d' % (t, its), id=i, n=2, mode='j', c=BAS, o=[0, 0, 0], u=Y, w=Z, W=2.4, its=its))
        out.append(dict(tag='%s-bas-diag-14' % t, id=i, n=2, mode='j', c=BAS, o=[0, 0, 0], u=X, w=D1, W=3.6, its=14))
        out.append(dict(tag='%s-bas-x618-14' % t, id=i, n=2, mode='j', c=BAS, o=[-0.618034, 0, 0], u=Y, w=Z, W=1.0, its=14))
        out.append(dict(tag='%s-bas-xm03-14' % t, id=i, n=2, mode='j', c=BAS, o=[-0.3, 0, 0], u=Y, w=Z, W=2.4, its=14))
    return out


LISTS = {'first': first}


def second():
    out = []
    for t, i in RULES:
        out.append(dict(tag='%s-bud-x0' % t, id=i, n=2, mode='j', c=BAS, o=[0, 0, 0.6], u=Y, w=Z, W=0.5, its=14))
        out.append(dict(tag='%s-bud-x0-zoom' % t, id=i, n=2, mode='j', c=BAS, o=[0, 0.08, 0.6], u=Y, w=Z, W=0.12, its=20))
        out.append(dict(tag='%s-bud-z06' % t, id=i, n=2, mode='j', c=BAS, o=[0, 0, 0.6], u=X, w=Y, W=0.5, its=14))
        out.append(dict(tag='%s-meet-x-40' % t, id=i, n=2, mode='j', c=BAS, o=[-0.618034, 0, 0], u=Y, w=Z, W=0.1, its=40))
        out.append(dict(tag='%s-meet-diag-30' % t, id=i, n=2, mode='j', c=BAS, o=[-0.618034, 0, 0], u=X, w=D1, W=0.3, its=30))
        out.append(dict(tag='%s-neck-x58-20' % t, id=i, n=2, mode='j', c=BAS, o=[-0.58, 0, 0], u=Y, w=Z, W=0.3, its=20))
    return out


LISTS['second'] = second


def third():
    out = []
    for t, i in RULES[:2]:
        out.append(dict(tag='%s-m-x02-14' % t, id=i, n=2, mode='m', c=None, o=[-0.2, 0, 0], u=Y, w=Z, W=2.4, its=14))
        out.append(dict(tag='%s-m-x02-40' % t, id=i, n=2, mode='m', c=None, o=[-0.2, 0, 0], u=Y, w=Z, W=2.4, its=40))
        out.append(dict(tag='%s-m-x1-14' % t, id=i, n=2, mode='m', c=None, o=[-1, 0, 0], u=Y, w=Z, W=1.2, its=14))
        out.append(dict(tag='%s-m-diag-14' % t, id=i, n=2, mode='m', c=None, o=[-0.6, 0, 0], u=X, w=D1, W=3.2, its=14))
        out.append(dict(tag='%s-m-y0-14' % t, id=i, n=2, mode='m', c=None, o=[-0.6, 0, 0], u=X, w=Z, W=3.2, its=14))
        out.append(dict(tag='%s-rabbit-x0-14' % t, id=i, n=2, mode='j', c=[-0.12, 0.74, 0], o=[0, 0, 0], u=Y, w=Z, W=3.0, its=14))
        out.append(dict(tag='%s-rabbit-y0-14' % t, id=i, n=2, mode='j', c=[-0.12, 0.74, 0], o=[0, 0, 0], u=X, w=Z, W=3.0, its=14))
        out.append(dict(tag='%s-n3-j03-x0' % t, id=i, n=3, mode='j', c=[0.3, 0, 0], o=[0, 0, 0], u=Y, w=Z, W=2.6, its=14))
        out.append(dict(tag='%s-n4-bas-x0' % t, id=i, n=4, mode='j', c=BAS, o=[0, 0, 0], u=Y, w=Z, W=2.6, its=14))
    return out


LISTS['third'] = third


def go(name, N=300):
    cuts = LISTS[name]()
    js = JS.replace('__CUTS__', json.dumps(cuts)).replace('__N__', str(N))
    path = os.path.join(HERE, 'brute-%s.js' % name)
    open(path, 'w', encoding='utf-8', newline='\n').write(js)
    steps = [run.UP, {'js': js, 'timeout': 1800}]
    code, text, vals = run.shot(run.PAGE, steps, 'brute-%s-steps' % name)
    res = json.loads(vals[-1]); lines = []
    for q, r in zip(cuts, res):
        g = np.frombuffer(base64.b64decode(r['rows']), np.uint8).reshape(N, N).astype(float)
        im = np.zeros((N, N, 3), np.uint8); ins = g == 0
        v = np.clip((g - 1) / max(q['its'] - 1, 1), 0, 1)
        im[..., 0] = 14 + 60 * v; im[..., 1] = 18 + 90 * v; im[..., 2] = 30 + 150 * v
        im[ins] = (236, 226, 200)
        Image.fromarray(im).resize((2 * N, 2 * N), Image.NEAREST).save(os.path.join(HERE, 'brute-%s.png' % q['tag']))
        lines.append('brute-%s.png: %s, n %s, %s, centre %s, across %s, up %s, %.3g wide, %d steps, in the solid: %.2f %%' % (
            q['tag'], q['id'], q['n'], 'Mandelbrot' if q['mode'] == 'm' else 'c = %s' % q['c'], q['o'], [round(x, 3) for x in q['u']], [round(x, 3) for x in q['w']], q['W'], q['its'], 100 * r['inside']))
    run.write('brute-%s.txt' % name, text.split('step 2 result')[0] + '\n'.join(lines) + '\n')
    print('\n'.join(lines))
    return code


if __name__ == '__main__':
    sys.exit(go(sys.argv[1]))

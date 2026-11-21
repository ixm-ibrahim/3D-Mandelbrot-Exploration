"""Round 29, Track A, builder, section 4 points 1 and 3: one recipe, three voices, and the distance.

  python -B out/r29/free/mk/voices29.py [new|old] [names...]   -> out/r29/free/logs/voices-<panel>.txt

For each state of the panel, in the page (dist/r29-free.html):
  the shader, through sampleSlice from the program the picture is drawn with: the flat cut on a 160 x 160 grid of
    the start view and fourteen 48 x 48 grids at other heights (the distance it hands out, and its sign);
  the twin: ballsInside and ballsEstimate at the same points (read from the page, nothing passed).
Here: my own numpy writing of the recipe (kit29.recipe) and the prototype of the distance (kit29.estimate) at the
same points. Reported: verdicts that differ (shader / twin / mine), the shader's distance against the twin's, the
twin's against the prototype's.
"""
import base64, json, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import run29 as run
import kit29 as K

PRE = run.HEAD + """
window.__V = {};
const V = window.__V;
V.b64 = f => { const u = new Uint8Array(f.buffer, f.byteOffset, f.byteLength); let s = ''; for (let i = 0; i < u.length; i += 8192) s += String.fromCharCode.apply(null, u.subarray(i, i + 8192)); return btoa(s); };
$('ap-balls').click(); await settle();
return 'Balls on balls on show: ' + $('status').textContent;
"""
ONE = run.HEAD + """
const V = window.__V, rho = %r, t = %r, g = %d, depth = %d, side = %r, zs = %s;
S.k.brho = rho; S.k.bt = t; S.k.bgrid = g; S.k.bit = depth; S.flat = false; S.cutOn = false; go(); await settle();
const out = { sig: String(L.R.sig).split('\\n')[0], rhoPage: S.k.brho, tPage: S.k.bt, warn: warn(), slices: [] };
for (let k = 0; k < zs.length; k++) {
  const n = k === 0 ? 160 : 48, z = zs[k];
  const snap = L.takeSnapshot(), arr = await L.sampleSlice(snap, 0, 0, side, z, n); L.releaseSnapshot(snap);
  if (!arr) fail('sampleSlice gave nothing');
  const sh = new Float32Array(n * n), tw = new Float32Array(n * n); let bits = '';
  for (let j = 0; j < n; j++) for (let i = 0; i < n; i++) {
    const x = side * ((i + 0.5) / n - 0.5), y = side * ((j + 0.5) / n - 0.5);
    sh[j * n + i] = arr[4 * (j * n + i) + 3]; tw[j * n + i] = L.ballsEstimate(x, y, z); bits += L.ballsInside(x, y, z) ? '1' : '0';
  }
  out.slices.push({ n, z, sh: V.b64(sh), tw: V.b64(tw), bits });
  await sleep(5);
}
return JSON.stringify(out);
"""


def f32(s):
    return np.frombuffer(base64.b64decode(s), dtype=np.float32).astype(float)


if __name__ == '__main__':
    args = sys.argv[1:]
    which = args[0] if args and args[0] in ('new', 'old') else 'new'
    names = args[1:] if args and args[0] in ('new', 'old') else args
    panel = K.PANEL_NEW if which == 'new' else K.PANEL_OLD
    panel = [s for s in panel if not names or s[0] in names]
    steps = [run.UP, {'js': PRE, 'wait': 'done', 'timeout': 900}]
    meta = []
    rng = np.random.RandomState(2029)
    for (name, p, rs, grid, depth) in panel:
        t = float(K.t_of(p)); rho = float(rs / 100.0)
        if which == 'old' and abs(rs - 33.33) < 0.01:
            rho = 0.3333
        if which == 'old' and abs(rs - 16.67) < 0.01:
            rho = 0.1667
        side = float(round(min(2 * (K.K2 * (0.5 + 1.2 * p / 100) + 0.4), 9.0), 3))
        zs = [0.0] + [float(round(v, 4)) for v in rng.uniform(-0.45, 0.45, 14) * side]
        meta.append((name, p, rs, grid, depth, t, rho, side, zs))
        steps.append({'js': ONE % (rho, t, grid, depth, side, json.dumps(zs)), 'wait': 'done', 'timeout': 1800})
    tag = 'voices-%s' % which + ('-' + '-'.join(names) if names else '')
    code, text, vals = run.shot(run.PAGE, steps, tag, '1400x950', 'dark')
    run.write(tag + '.log', text + 'exit %d\n' % code)
    lines = ['page %s, exit %d, %s' % (run.PAGE, code, 'no console errors' if run.clean(text) else 'SEE logs/%s.log' % tag)]
    tot = np.zeros(6, int)
    for (name, p, rs, grid, depth, t, rho, side, zs), v in zip(meta, vals[2:]):
        d = json.loads(v)
        pts = 0; d_sh = 0; d_tw = 0; n_out = 0; far = 0; worst = 0.0; pfar = 0; pworst = 0.0; signs = 0; hair = []; deep = []
        for s in d['slices']:
            n = s['n']; idx = side * ((np.arange(n) + 0.5) / n - 0.5)
            X, Y = np.meshgrid(idx, idx)
            P = np.stack([X.ravel(), Y.ravel(), np.full(n * n, s['z'])], 1)
            mine = K.recipe(P, t, rho, grid, depth)
            sh = f32(s['sh']); tw = f32(s['tw']); bits = np.array([c == '1' for c in s['bits']])
            pts += n * n; d_sh += int(((sh <= 0) != mine).sum()); d_tw += int((bits != mine).sum())
            bad = (sh <= 0) != mine
            if bad.any():
                # how near is a point where my own writing gives the other verdict? (the smallest of four steps at
                # which one of six neighbours differs), and how far out the point lies in the object's own space
                Q = P[bad]; base = mine[bad]; near = np.full(len(Q), 9.0)
                for h in (1e-2, 1e-3, 1e-4, 1e-5):
                    flip = np.zeros(len(Q), bool)
                    for ax in range(3):
                        for sg in (-1, 1):
                            R = Q.copy(); R[:, ax] += sg * h
                            flip |= K.recipe(R, t, rho, grid, depth) != base
                    near = np.where(flip, h, near)
                m0, _ = K.to_m(Q)
                hair += list(near); deep += list(np.sqrt((m0 * m0).sum(1)))
            signs += int(((tw <= 0) != bits).sum())
            o = (sh > 0) & (tw > 0)
            rel = np.abs(sh[o] - tw[o]) / np.maximum(tw[o], 1e-4)
            n_out += int(o.sum()); far += int((rel > 0.01).sum()); worst = max(worst, float(rel.max()) if o.any() else 0)
            pe, pb, pf, pst = K.estimate(P, t, rho, grid, depth)
            o2 = (tw > 0) & (pe > 0)
            rel2 = np.abs(tw[o2] - pe[o2]) / np.maximum(pe[o2], 1e-6)
            pfar += int((rel2 > 1e-3).sum()); pworst = max(pworst, float(rel2.max()) if o2.any() else 0)
        lines.append('%-4s size %7.2f second %6.2f grid %d depth %3d | program %s, t %.6f, rho %.4f' % (name, p, rs, grid, depth, d['sig'], d['tPage'], d['rhoPage']))
        lines.append('     %d points: verdicts that differ from my writing: shader %d, twin %d; twin\'s distance and twin\'s verdict disagree in sign at %d' % (pts, d_sh, d_tw, signs))
        if hair:
            hair = np.array(hair); deep = np.array(deep)
            lines.append('     the %d shader points: my own writing gives the other verdict within 1e-5 at %d, within 1e-4 at %d, within 1e-3 at %d, within 1e-2 at %d, not within 1e-2 at %d; how far out they lie in the space the recipe works in (|m| at the start): median %.1f, least %.1f'
                         % (len(hair), int((hair <= 1e-5).sum()), int((hair <= 1e-4).sum()), int((hair <= 1e-3).sum()), int((hair <= 1e-2).sum()), int((hair > 1e-2).sum()), np.median(deep), deep.min()))
        lines.append('     shader distance against the twin where both say outside: %d points, more than 1 %% apart %d, worst %.2e | twin against the numpy prototype: more than 0.1 %% apart %d, worst %.2e'
                     % (n_out, far, worst, pfar, pworst))
        tot += np.array([pts, d_sh, d_tw, far, pfar, signs])
    lines.append('TOTAL %d points: shader verdicts that differ %d, twin verdicts %d; shader distance more than 1 %% from the twin %d; twin more than 0.1 %% from the prototype %d; sign of the twin\'s distance against its verdict %d' % tuple(tot))
    out = '\n'.join(lines) + '\n'
    run.write(tag + '.txt', out); print(out)
    if code != 0:
        print(text[-3000:])

"""Round 29, the orchestrator's own check before Version 22 is published (free dials: states where the spheres cut, and a second sphere between 50 and 100).
The recipe with a smaller second sphere, written out by me from docs/ROUND28.md 1.1 / 1.2 (numpy), against the two
voices of the merged page dist/preview.html: the JavaScript twin (ballsInside) and the shader (sampleSlice, from the
program the picture is drawn with). Six settings, four of them past 100.

  python -B out/r29/me/own29.py [page]      -> out/r29/me/own29.txt
"""
import json, os, re, subprocess, sys
import numpy as np
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
PAGE = sys.argv[1] if len(sys.argv) > 1 else 'dist/preview.html'
K2 = 1.05
S3 = np.sqrt(3.0)
# size of the neighbours p, second sphere rho, grid (0 square, 1 honeycomb, 2 line), rounds
SETS = [(55.56, 1.0, 0, 16), (150.0, 1 / 3, 0, 16), (120.0, 1.0, 0, 16), (130.0, 1.0, 0, 16), (150.0, 1.0, 2, 16), (150.0, 1.0, 1, 16),
        (150.0, 0.75, 0, 16), (300.0, 0.5, 0, 16), (400.0, 1.0, 0, 16), (105.0, 1.0, 0, 40), (80.0, 0.75, 0, 16), (60.0, 0.6, 1, 16),
        (100.0, 0.9, 0, 16), (55.56, 0.99, 0, 16), (133.33, 0.75, 0, 16), (120.0, 0.51, 2, 16), (30.0, 0.75, 0, 16), (62.5, 0.625, 0, 24)]


def t_of(p):
    return 1.4 if abs(p - 100 / 1.8) < 0.06 else 0.5 * (100.0 / p + 1)


def nearest(grid, x, y):
    if grid == 2:
        return np.round(x), np.zeros_like(y)
    if grid == 0:
        return np.round(x), np.round(y)
    # honeycomb: whole-number sums of (1, 0) and (1/2, sqrt 3 / 2); the nearest of nine candidates
    b0 = np.round(y / (S3 / 2)); a0 = np.round(x - b0 / 2)
    best = None; bd = None
    for db in (-1, 0, 1):
        for da in (-1, 0, 1):
            b = b0 + db; a = a0 + da
            px = a + b / 2; py = b * S3 / 2
            d = (x - px) ** 2 + (y - py) ** 2
            if bd is None:
                bd = d; best = (px, py)
            else:
                m = d < bd
                best = (np.where(m, px, best[0]), np.where(m, py, best[1])); bd = np.where(m, d, bd)
    return best


def mine(x, y, z, p, rho, grid, rounds):
    """True = inside (or still undecided when the rounds run out)."""
    x = np.asarray(x, float); y = np.asarray(y, float); z = np.asarray(z, float)
    top = 2 * t_of(p)
    ux, uy, uz = y, z, x - K2 / 2
    d = ux * ux + uy * uy + uz * uz; d = np.where(d > 0, d, 1e-300)
    mx, my, mz = K2 * ux / d, K2 * uy / d, 1 + K2 * uz / d
    state = np.zeros(x.shape, int)                      # 0 undecided, 1 inside, 2 outside
    for _ in range(rounds):
        live = state == 0
        state = np.where(live & ((mz < 0) | (mz > top)), 1, state); live = state == 0
        nx, ny = nearest(grid, mx, my)
        mx = mx - nx; my = my - ny
        rb = mx * mx + my * my + mz * mz
        rt = mx * mx + my * my + (mz - top) ** 2
        inb = live & (rb < 1); itp = live & ~inb & (rt < rho * rho)
        state = np.where(live & ~inb & ~itp, 2, state)
        sb = 1 / np.where(rb > 0, rb, 1.0); st = rho * rho / np.where(rt > 0, rt, 1.0)
        mx, my, mz = (np.where(inb, mx * sb, np.where(itp, mx * st, mx)), np.where(inb, my * sb, np.where(itp, my * st, my)),
                      np.where(inb, mz * sb, np.where(itp, top + (mz - top) * st, mz)))
    return state != 2


JS = r"""
const L = window.squaringLab, S = L.S, $ = id => document.getElementById(id);
const sleep = ms => new Promise(r => setTimeout(r, ms));
const settle = async () => { await sleep(300); for (let i = 0; i < 20000 && !L.idle(); i++) await sleep(20); if (!L.idle()) throw new Error('never finished'); if (L.R.failed) throw new Error('a program failed'); };
let a = 0x51ed270b ^ 2026112017;
const rnd = () => { a |= 0; a = (a + 0x6D2B79F5) | 0; let t = Math.imul(a ^ (a >>> 15), 1 | a); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };
const r12 = x => +x.toFixed(12);
const SETS = __SETS__;
const out = [];
$('ap-balls').click(); await settle();
for (const [p, rho, grid, rounds] of SETS) {
  const t = Math.abs(p - 100 / 1.8) < 0.06 ? 1.4 : 0.5 * (100 / p + 1);
  const wide = Math.min(8, 1.2 + p / 60), o = { p, rho, grid, rounds, t, P: [], twin: '', twinFlat: '', sh: [] };
  for (let i = 0; i < 12000; i++) o.P.push([r12(wide * (2 * rnd() - 1)), r12(0.6 * wide * (2 * rnd() - 1)), r12(0.6 * wide * (2 * rnd() - 1))]);
  for (const q of o.P) { o.twin += L.ballsInside(q[0], q[1], q[2], { t, rho, grid, rounds }) ? '1' : '0'; o.twinFlat += L.ballsInside(q[0], q[1], 0, { t, rho, grid, rounds }) ? '1' : '0'; }
  // the shader: the state is written as the dials would leave it, then read back from the program on show
  S.mode = 'k'; S.k.group = 1; S.k.bt = t; S.k.brho = rho; S.k.bgrid = grid; S.k.bit = rounds; S.flat = false; S.cutOn = false;
  L.syncControls(); L.refresh(false); L.touch(); if (L.viewChanged) L.viewChanged(); await settle();
  o.program = String(L.R.sig || '').split('\n')[0]; o.shown = { size: $('ballsSizeNum').value, second: $('ballsRhoNum').value, depth: $('ballsDepthNum').value };
  const side = 2 * wide;
  for (const [n, z] of [[120, 0], [48, r12(0.5 * wide * (2 * rnd() - 1))], [48, r12(0.5 * wide * (2 * rnd() - 1))], [48, r12(0.25 * (2 * rnd() - 1))]]) {
    const snap = L.takeSnapshot(), arr = await L.sampleSlice(snap, 0, 0, side, z, n); L.releaseSnapshot(snap);
    if (!arr) throw new Error('sampleSlice gave nothing');
    let s = ''; for (let j = 0; j < n; j++) for (let i = 0; i < n; i++) s += !(arr[4 * (j * n + i) + 3] > 0) ? '1' : '0';
    o.sh.push({ n, z, side, bits: s });
  }
  out.push(o);
}
return JSON.stringify(out);
"""

if __name__ == '__main__':
    steps = [{'js': "const L = window.squaringLab; return 'page up, ' + L.APPROACHES.length + ' entries';", 'wait': 'done', 'timeout': 600},
             {'js': JS.replace('__SETS__', json.dumps(SETS)), 'timeout': 900}]
    sj = os.path.join(HERE, 'own29-steps.json'); json.dump(steps, open(sj, 'w', encoding='utf-8'))
    p = subprocess.run([sys.executable, os.path.join(ROOT, 'tools', 'shot.py'), '--url', PAGE, '--actions', sj, '--size', '1400x950', '--theme', 'dark'],
                       capture_output=True, cwd=ROOT, env=dict(os.environ, PYTHONIOENCODING='utf-8'))
    text = p.stdout.decode('utf-8', 'replace') + p.stderr.decode('utf-8', 'replace')
    val = None; rest = []
    for line in text.splitlines():
        m = re.match(r'step \d+ result: (".*")$', line)
        if m and len(m.group(1)) > 5000:
            val = json.loads(json.loads(m.group(1))); continue
        rest.append(line[:400])
    lines = ['page %s, exit %d' % (PAGE, p.returncode)] + ['   | ' + r for r in rest]
    tot = bad = 0
    for o in (val or []):
        P = np.array(o['P']); p_, rho, grid, rounds = o['p'], o['rho'], o['grid'], o['rounds']
        tw = np.array([c == '1' for c in o['twin']]); tf = np.array([c == '1' for c in o['twinFlat']])
        me = mine(P[:, 0], P[:, 1], P[:, 2], p_, rho, grid, rounds); mf = mine(P[:, 0], P[:, 1], 0 * P[:, 2], p_, rho, grid, rounds)
        b1 = int((tw != me).sum()) + int((tf != mf).sum())
        sb = sn = 0
        for s in o['sh']:
            n = s['n']; idx = (np.arange(n) + 0.5) / n - 0.5
            X = (s['side'] * idx[None, :] + np.zeros((n, 1))).ravel(); Y = (s['side'] * idx[:, None] + np.zeros((1, n))).ravel()
            got = np.array([c == '1' for c in s['bits']]); ref = mine(X, Y, np.full(n * n, s['z']), p_, rho, grid, rounds)
            sb += int((got != ref).sum()); sn += n * n
        tot += 2 * len(P) + sn; bad += b1 + sb
        lines.append('size %7.2f, second sphere %6.2f %%, grid %d, depth %2d (boxes show %s / %s / %s; program %s): inside in space %5d of %d; twin against my recipe %d of %d differ; shader against my recipe %d of %d differ'
                     % (p_, 100 * rho, grid, rounds, o['shown']['size'], o['shown']['second'], o['shown']['depth'], o['program'][:40], int(me.sum()), len(P), b1, 2 * len(P), sb, sn))
    lines.append('ALL: %d of %d verdicts differ' % (bad, tot) if val else 'NO VALUE CAME BACK')
    out = '\n'.join(lines) + '\n'
    open(os.path.join(HERE, 'own29.txt'), 'w', encoding='utf-8', newline='\n').write(out); print(out)

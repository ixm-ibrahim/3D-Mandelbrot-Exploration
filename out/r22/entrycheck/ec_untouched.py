"""Round 22, entrycheck: five entries that carry nothing, dist/r22-entry.html against dist/r22-entrycheck-base.html
(base17a built by me, byte-identical to the builder's dist/r22-base17a.html and to dist/v17check.html).
Other scenes than the builder's, the page's default quality (three neighbouring orbits where the entry allows them).
Also: every fragment shader the page hands to the GPU while the scenes are drawn, with comments out and the
#ifdef APR_CARRY blocks resolved for "not defined", as a hash, to compare between the two pages.
  python out/r22/entrycheck/ec_untouched.py shots new|base     (one page per run)
  python out/r22/entrycheck/ec_untouched.py compare            -> untouched.txt
"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import drive

IDS = ['mercator', 'lathe', 'turnalong', 'windsq', 'bulb']
SCENES = [('rabbit', "S.mode = 'j'; S.c = [-0.122561, 0.744862, 0]; S.iter = 36; S.flat = false; L.resetCam();"),
          ('mandel', "S.mode = 'm'; S.iter = 26; S.flat = false; L.resetCam(); L.cam.yaw = 0.6; L.cam.pitch = 0.2; L.cam.dist = 4.8;"),
          ('flat', "S.mode = 'j'; S.c = [-1, 0, 0]; S.iter = 40; S.flat = true; S.cut = 0.15; S.v2.x = 0; S.v2.y = 0; S.v2.h = 3.4;"),
          ('pow3', "S.mode = 'j'; S.n = 3; S.c = [0.3, 0, 0]; S.iter = 30; S.flat = false; L.resetCam();")]
PAGES = {'new': 'dist/r22-entry.html', 'base': 'dist/r22-entrycheck-base.html'}
PATCH = """
window.__src = [];
const old = WebGL2RenderingContext.prototype.shaderSource;
WebGL2RenderingContext.prototype.shaderSource = function (sh, src) { window.__src.push(String(src)); return old.call(this, sh, src); };
window.__norm = src => { const out = [], st = []; for (const line of src.split('\\n')) { const t = line.trim(), top = st[st.length - 1];
  if (t === '#ifdef APR_CARRY') { st.push('skip'); continue; }
  if (t === '#else' && (top === 'skip' || top === 'keep')) { st[st.length - 1] = top === 'skip' ? 'keep' : 'skip'; continue; }
  if (t === '#endif' && (top === 'skip' || top === 'keep')) { st.pop(); continue; }
  if (t.startsWith('#if')) st.push('other'); else if (t === '#endif' && top === 'other') st.pop();
  if (st.includes('skip')) continue;
  const l = line.replace(/\\/\\/.*$/, '').trimEnd(); if (l.trim()) out.push(l); } return out.join('\\n'); };
window.__hash = s => { let x = 2166136261; for (let i = 0; i < s.length; i++) { x ^= s.charCodeAt(i); x = Math.imul(x, 16777619); } return (x >>> 0).toString(16); };
return 'shaderSource patched';
"""


def shots(tag):
    steps = [drive.UP, {'js': PATCH}]
    for id_ in IDS:
        for sc, set_ in SCENES:
            js = drive.HEAD + "$('ap-%s').click(); await sleep(250); if (apId() !== '%s') fail('could not choose'); S.eq = 'z^n + c'; S.z0 = '0'; S.n = 2; S.cutOn = false; S.cut = 0; S.mosaic = false; S.q.de = 3; %s" % (id_, id_, set_) + """
document.querySelectorAll('#stage *').forEach(e => { if (e.tagName !== 'CANVAS' && !e.querySelector('canvas')) e.style.visibility = 'hidden'; });
window.__src.length = 0;
go(); const t0 = performance.now(); await settle(); const t1 = performance.now(); go(); await settle(); const t2 = performance.now();
const progs = window.__src.filter(s => s.length > 5000).map(s => { const n = window.__norm(s); return { raw: s.length, carry: /#define APR_CARRY/.test(s), hash: window.__hash(n), len: n.length, lines: n.split('\\n').length }; });
return JSON.stringify({ first: Math.round(t1 - t0), again: Math.round(t2 - t1 - 250), hits: grid()[0], progs, failed: L.R.failed || null });"""
            steps.append({'js': js, 'wait': 'done', 'timeout': 900, 'shot': 'out/r22/entrycheck/untouched/%s-%s-%s.png' % (tag, id_, sc), 'clip': '#stage canvas'})
    os.makedirs(os.path.join(HERE, 'untouched'), exist_ok=True)
    code, text, vals = drive.shot(PAGES[tag], steps, 'untouched-%s-steps' % tag, '1400x950')
    drive.write('untouched-%s.log' % tag, text + 'exit %d\n' % code)
    json.dump(vals, open(os.path.join(HERE, 'untouched-%s.json' % tag), 'w', encoding='utf-8'))
    print(tag, 'exit', code, text[-400:])
    return code


def compare():
    import numpy as np
    from PIL import Image
    V = {tag: [v if isinstance(v, dict) else json.loads(v) for v in json.load(open(os.path.join(HERE, 'untouched-%s.json' % tag), encoding='utf-8'))[2:]] for tag in PAGES}
    rep = ['Five entries that carry nothing: this build against base17a. Window 1400x950, the stage canvas, default quality.', '']
    i = 0; tot = [0, 0]; worst = 0
    for id_ in IDS:
        for sc, _ in SCENES:
            a = np.asarray(Image.open(os.path.join(HERE, 'untouched', 'new-%s-%s.png' % (id_, sc))).convert('RGB'), np.int16)
            b = np.asarray(Image.open(os.path.join(HERE, 'untouched', 'base-%s-%s.png' % (id_, sc))).convert('RGB'), np.int16)
            tn, tb = V['new'][i], V['base'][i]; i += 1
            if a.shape != b.shape:
                rep.append('  %-10s %-6s sizes differ: %s %s' % (id_, sc, a.shape, b.shape)); continue
            d = np.abs(a - b).max(-1); worst = max(worst, int((d > 0).sum()))
            hn = [(p['hash'], p['len']) for p in tn['progs']]; hb = [(p['hash'], p['len']) for p in tb['progs']]
            tot[0] += tn['again']; tot[1] += tb['again']
            rep.append('  %-10s %-6s %d x %d: %d pixels differ (largest %d of 255); not background %d; probes hit %d / %d | programs handed to the GPU: %d / %d, after stripping %s%s | drawn again in %d / %d ms' % (
                id_, sc, a.shape[1], a.shape[0], (d > 0).sum(), d.max(), (np.abs(a - a[2, 2]).max(-1) > 6).sum(), tn['hits'], tb['hits'], len(hn), len(hb),
                'the same text' if hn == hb else 'DIFFERENT: %s against %s' % (hn, hb), '; APR_CARRY DEFINED' if any(p['carry'] for p in tn['progs']) else '', tn['again'], tb['again']))
    rep.append('')
    rep.append('most pixels that differ in one picture: %d. Time to draw all %d pictures again: this build %d ms, base17a %d ms.' % (worst, i, tot[0], tot[1]))
    out = '\n'.join(rep) + '\n'
    drive.write('untouched.txt', out); print(out)


if __name__ == '__main__':
    if sys.argv[1] == 'shots':
        sys.exit(shots(sys.argv[2]))
    compare()

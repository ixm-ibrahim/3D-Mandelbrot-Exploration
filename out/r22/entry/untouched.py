"""Round 22, entry: do the entries that carry nothing draw exactly as they did?

  python out/r22/entry/untouched.py text      the orbit code with APR_CARRY not defined against base17a's, as text (no browser)
  python out/r22/entry/untouched.py shots     the same 15 pictures from dist/r22-entry.html and from dist/r22-base17a.html
  python out/r22/entry/untouched.py compare   the pictures pixel by pixel, the GLSL of every old entry, the drawing times
-> untouched.txt
"""
import hashlib, io, json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import run
IDS = ['mercator', 'lathe', 'turnalong', 'windsq', 'bulb']
SCENES = [('julia', "S.mode = 'j'; S.c = [-1, 0, 0]; S.iter = 40; S.flat = false; L.resetCam(); L.cam.yaw = -1.9; L.cam.pitch = 0.3; L.cam.dist = 4.6;"),
          ('mandel', "S.mode = 'm'; S.iter = 30; S.flat = false; L.resetCam();"),
          ('flat', "S.mode = 'j'; S.c = [-0.122561, 0.744862, 0]; S.iter = 40; S.flat = true; S.cut = 0; S.v2.x = 0; S.v2.y = 0; S.v2.h = 3.6;")]
PAGES = [('new', 'dist/r22-entry.html'), ('base', 'dist/r22-base17a.html')]


def strip(glsl):
    """GLSL with comments taken out and the blocks #ifdef APR_CARRY ... [#else ...] #endif resolved for APR_CARRY not defined."""
    out, state = [], []
    for line in glsl.split('\n'):
        t = line.strip()
        if t == '#ifdef APR_CARRY':
            state.append('skip'); continue
        if state and t == '#else' and state[-1] in ('skip', 'keep'):
            state[-1] = 'keep' if state[-1] == 'skip' else 'skip'; continue
        if state and t == '#endif' and state[-1] in ('skip', 'keep'):
            state.pop(); continue
        if t.startswith('#if'):
            state.append('other')
        elif t == '#endif' and state and state[-1] == 'other':
            state.pop()
        if 'skip' in state:
            continue
        line = re.sub(r'//.*$', '', line).rstrip()
        if line.strip():
            out.append(line)
    return '\n'.join(out)


def text():
    rep = []
    a = io.open(os.path.join(run.ROOT, 'base17a', 'js', '30-shaders.js'), encoding='utf-8').read()
    b = io.open(os.path.join(run.ROOT, 'src', 'js', '30-shaders.js'), encoding='utf-8').read()
    for name in ('GL_HEAD', 'GL_ORBIT', 'GL_KLEIN', 'GL_TAIL', 'VERT', 'BLIT'):
        ga = re.search(r'const %s = `(.*?)`;' % name, a, re.S).group(1); gb = re.search(r'const %s = `(.*?)`;' % name, b, re.S).group(1)
        rep.append('%-8s as written: %s; with comments out and APR_CARRY not defined: %s (%d lines)' % (
            name, 'identical' if ga == gb else 'DIFFERS', 'identical' if strip(ga) == strip(gb) else 'DIFFERS', len(strip(gb).split('\n'))))
    return rep


def shots():
    for tag, page in PAGES:
        steps = [run.UP]
        steps.append({'js': run.HEAD + """
const h = s => { let x = 2166136261; for (let i = 0; i < s.length; i++) { x ^= s.charCodeAt(i); x = Math.imul(x, 16777619); } return (x >>> 0).toString(16) + ':' + s.length; };
return JSON.stringify(Object.fromEntries(L.APPROACHES.map(a => [a.id, h(a.glsl)])));""", 'timeout': 300})
        for id_ in IDS:
            for sc, set_ in SCENES:
                js = run.HEAD + "$('ap-%s').click(); await sleep(250); S.eq = 'z^n + c'; S.z0 = '0'; S.n = 2; S.cutOn = false; S.mosaic = false; %s document.querySelectorAll('#stage *').forEach(e => { if (e.tagName !== 'CANVAS' && !e.querySelector('canvas')) e.style.visibility = 'hidden'; }); go(); const t0 = performance.now(); await settle(); const t1 = performance.now(); go(); await settle(); const t2 = performance.now(); return JSON.stringify({ id: apId(), scene: '%s', first: Math.round(t1 - t0), again: Math.round(performance.now() - t1) });" % (id_, set_, sc)
                steps.append({'js': js, 'wait': 'done', 'timeout': 900, 'shot': 'out/r22/entry/untouched/%s-%s-%s.png' % (tag, id_, sc), 'clip': '#stage canvas'})
        os.makedirs(os.path.join(HERE, 'untouched'), exist_ok=True)
        code, textout, vals = run.shot(page, steps, 'untouched-%s-steps' % tag, '1400x950')
        run.write('untouched-%s.log' % tag, textout + 'exit %d\n' % code)
        json.dump(vals, open(os.path.join(HERE, 'untouched-%s.json' % tag), 'w', encoding='utf-8'))
        print(tag, 'exit', code, textout[-300:])


def compare():
    import numpy as np
    from PIL import Image
    rep = text()
    V = {tag: json.load(open(os.path.join(HERE, 'untouched-%s.json' % tag), encoding='utf-8')) for tag, _ in PAGES}
    ga, gb = json.loads(V['new'][1]), json.loads(V['base'][1])
    same = [k for k in gb if ga.get(k) == gb[k]]; diff = [k for k in gb if ga.get(k) != gb[k]]
    rep.append('GLSL of the %d old entries (hash and length of approach.glsl in the two pages): %d identical%s; new in this build: %s' % (
        len(gb), len(same), '' if not diff else '; DIFFER: ' + ' '.join(diff), ' '.join(k for k in ga if k not in gb)))
    rep.append('')
    rep.append('Pictures of five untouched entries, this build against base17a (1400x950 window, the canvas of the stage):')
    T = {tag: [json.loads(v) for v in V[tag][2:]] for tag in V}
    i = 0
    for id_ in IDS:
        for sc, _ in SCENES:
            a = np.asarray(Image.open(os.path.join(HERE, 'untouched', 'new-%s-%s.png' % (id_, sc))).convert('RGB'), np.int16)
            b = np.asarray(Image.open(os.path.join(HERE, 'untouched', 'base-%s-%s.png' % (id_, sc))).convert('RGB'), np.int16)
            if a.shape != b.shape:
                rep.append('  %-10s %-6s sizes differ: %s %s' % (id_, sc, a.shape, b.shape)); i += 1; continue
            d = np.abs(a - b).max(-1)
            tn, tb = T['new'][i], T['base'][i]; i += 1
            rep.append('  %-10s %-6s %d x %d pixels: %d differ (largest difference %d of 255; by more than 2: %d); not background: %d | time to draw, first / again: this build %d / %d ms, base17a %d / %d ms' % (
                id_, sc, a.shape[1], a.shape[0], (d > 0).sum(), d.max(), (d > 2).sum(), (np.abs(a - a[2, 2]).max(-1) > 6).sum(), tn['first'], tn['again'], tb['first'], tb['again']))
    # the clock: every run there is of the two pages (each run: this build first, then base17a)
    rep.append('')
    rep.append('Time to draw again (ms, the second drawing of the same settings), this build / base17a, per run:')
    runs = []
    for suffix in ('.run1.json', '.json'):
        try:
            runs.append({tag: [json.loads(v) for v in json.load(open(os.path.join(HERE, 'untouched-%s%s' % (tag, suffix)), encoding='utf-8'))[2:]] for tag, _ in PAGES})
        except OSError:
            pass
    i = 0; tot = [[0, 0] for _ in runs]
    for id_ in IDS:
        for sc, _ in SCENES:
            rep.append('  %-10s %-6s %s' % (id_, sc, '   '.join('%5d / %5d' % (r['new'][i]['again'], r['base'][i]['again']) for r in runs)))
            for k, r in enumerate(runs):
                tot[k][0] += r['new'][i]['again']; tot[k][1] += r['base'][i]['again']
            i += 1
    rep.append('  %-17s %s' % ('all 15 together', '   '.join('%5d / %5d' % (a, b) for a, b in tot)))
    out = '\n'.join(rep) + '\n'
    run.write('untouched.txt', out); print(out)


if __name__ == '__main__':
    what = sys.argv[1]
    if what == 'text':
        print('\n'.join(text()))
    elif what == 'shots':
        shots()
    else:
        compare()

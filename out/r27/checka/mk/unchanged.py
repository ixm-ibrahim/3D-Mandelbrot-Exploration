"""Round 27, checker A, bullet 4: the same states on my page (dist/r27-checka.html) and on the frozen page
(dist/r27-base.html), compared pixel by pixel. Each state is set through the page's own controls and handles, with the
same script on both pages. Two pictures per state: the whole window, and the picture alone (canvas #view with
everything that lies over the stage hidden). The frozen page is also run a second time, to see what differs between
two runs of the same page.
  python unchanged.py [run|compare]   -> ../same/<new|old|old2>/*.png, ../logs/unchanged.txt
"""
import json, os, sys
import numpy as np
from PIL import Image
import drive as D

SAME = os.path.join(D.CHK, 'same')
RESET = "for (const e of $('stage').children) e.style.visibility = ''; $('resetAll').click(); await sleep(300);\n"
STATES = [
    ('s01-mandelbrot-start', ""),
    ('s02-mandelbrot-2d', "S.flat = true; go();"),
    ('s03-mandelbrot-bulb', "$('ap-bulb').click(); await sleep(200);"),
    ('s04-mandelbrot-quat4-power3', "$('ap-quat4').click(); await sleep(200); S.n = 3; go();"),
    ('s05-julia-start', "$('mode-j').click(); await sleep(200);"),
    ('s06-julia-rabbit-lathe', "$('mode-j').click(); await sleep(200); $('ap-lathe').click(); await sleep(200); S.c = [-0.122561, 0.744862, 0]; go();"),
    ('s07-julia-2d', "$('mode-j').click(); await sleep(200); S.flat = true; go();"),
    ('s08-julia-cut', "$('mode-j').click(); await sleep(200); S.cutOn = true; S.cut = 0.1; go();"),
    ('s09-klein-start', "$('mode-k').click(); await sleep(200);"),
    ('s10-klein-entry2-spirals', "$('mode-k').click(); await sleep(200); L.applyKleinPreset(L.KLEIN_PRESETS[2]); L.frameKleinPreset(L.KLEIN_PRESETS[2]); go();"),
    ('s11-klein-entry4-third', "$('mode-k').click(); await sleep(200); L.applyKleinPreset(L.KLEIN_PRESETS[4]); L.frameKleinPreset(L.KLEIN_PRESETS[4]); go();"),
    ('s12-klein-entry13-leaning', "$('mode-k').click(); await sleep(200); L.applyKleinPreset(L.KLEIN_PRESETS[13]); L.frameKleinPreset(L.KLEIN_PRESETS[13]); go();"),
    ('s13-klein-entry3-2d', "$('mode-k').click(); await sleep(200); L.applyKleinPreset(L.KLEIN_PRESETS[3]); L.frameKleinPreset(L.KLEIN_PRESETS[3]); S.flat = true; go();"),
    ('s14-klein-example-pearls-and-balls', "L.applyExample(L.EXAMPLES[6]); await sleep(200);"),
    ('s15-klein-2d-height', "$('mode-k').click(); await sleep(200); S.flat = true; S.cut = 0.3; go();"),
    ('s16-mandelbrot-example-spiky-coral', "L.applyExample(L.EXAMPLES[0]); await sleep(200);"),
    ('s17-learn-on', "$('mode-l').click(); await sleep(600);"),
    ('s18-learn-on-lathe-julia', "$('mode-j').click(); await sleep(200); $('ap-lathe').click(); await sleep(200); $('mode-l').click(); await sleep(600);"),
]
STATE = "return JSON.stringify({ mode: S.mode, learn: !!S.learn, flat: S.flat, ap: L.APPROACHES[S.approach].id, n: S.n, group: S.k.group === undefined ? null : S.k.group, kiter: S.k.iter, status: $('status') ? $('status').textContent : '' });"


def steps(which, learn):
    st = [D.UP]
    for name, js in STATES:
        if ('learn' in name) != learn:
            continue
        st.append({'js': D.HEAD + RESET + js + "\nawait sleep(300);", 'wait': 'done', 'timeout': 300})
        st.append({'js': D.HEAD + "await settle(); await sleep(500);\n" + STATE, 'shot': 'out/r27/checka/same/%s/%s-full.png' % (which, name)})
        if learn:   # under Learn the picture is Learn's own drawing on the stage; the canvas #view is not on show
            st.append({'js': D.HEAD + "await sleep(300);", 'shot': 'out/r27/checka/same/%s/%s-view.png' % (which, name), 'clip': '#stage'})
        else:
            st.append({'js': D.HEAD + "for (const e of $('stage').children) if (e.id !== 'view') e.style.visibility = 'hidden'; await sleep(300);",
                       'shot': 'out/r27/checka/same/%s/%s-view.png' % (which, name), 'clip': '#view'})
    return st


def diff(a, b):
    A = np.asarray(Image.open(a).convert('RGB')).astype(int); Bm = np.asarray(Image.open(b).convert('RGB')).astype(int)
    if A.shape != Bm.shape:
        return -1, 'sizes differ: %s against %s' % (A.shape, Bm.shape)
    d = np.abs(A - Bm).max(2)
    n = int((d > 0).sum())
    if not n:
        return 0, ''
    ys, xs = np.nonzero(d)
    return n, 'largest step %d, in the box x %d..%d, y %d..%d' % (d.max(), xs.min(), xs.max(), ys.min(), ys.max())


if __name__ == '__main__':
    what = sys.argv[1] if len(sys.argv) > 1 else 'run'
    if what in ('run', 'learn'):
        for which, page in (('new', D.PAGE), ('old', D.BASE), ('old2', D.BASE)):
            for learn in ((False, True) if what == 'run' else (True,)):
                tag = 'unchanged-%s%s' % (which, '-learn' if learn else '')
                code, vals, text = D.run(page, steps(which, learn), tag)
                print(tag, 'exit', code, 'values', len(vals)); sys.stdout.flush()
                with open(os.path.join(D.LOGS, tag + '-states.json'), 'w', encoding='utf-8') as f:
                    json.dump(vals, f, indent=1)
    lines = []
    sts = {}
    for w in ('new', 'old', 'old2'):
        a = json.load(open(os.path.join(D.LOGS, 'unchanged-%s-states.json' % w), encoding='utf-8'))
        b = json.load(open(os.path.join(D.LOGS, 'unchanged-%s-learn-states.json' % w), encoding='utf-8'))
        n_plain = sum(1 for nm, _ in STATES if 'learn' not in nm)
        sts[w] = a[:1 + n_plain] + b[1:]
    for i, (name, js) in enumerate(STATES):
        row = '%-36s' % name
        for kind in ('view', 'full'):
            for a, b in (('new', 'old'), ('old', 'old2')):
                n, where = diff(os.path.join(SAME, a, '%s-%s.png' % (name, kind)), os.path.join(SAME, b, '%s-%s.png' % (name, kind)))
                row += ' | %s %s/%s: %d%s' % ('picture alone' if kind == 'view' else 'whole window', a, b, n, (' (' + where + ')') if where else '')
        sn = sts['new'][i + 1] if len(sts['new']) > i + 1 else None; so = sts['old'][i + 1] if len(sts['old']) > i + 1 else None
        if sn is not None and so is not None:
            sn2 = {k: v for k, v in sn.items() if k != 'group'}; so2 = {k: v for k, v in so.items() if k != 'group'}
            row += ' | state %s (%s)' % ('same' if sn2 == so2 else 'DIFFERS: %s against %s' % (sn2, so2), json.dumps(sn2))
        lines.append(row)
    with open(os.path.join(D.LOGS, 'unchanged.txt'), 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(lines) + '\n')
    print('\n'.join(lines))

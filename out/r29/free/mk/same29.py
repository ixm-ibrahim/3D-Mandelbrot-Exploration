"""Round 29, Track A, builder, section 4 point 2: old pictures unchanged. The picture of dist/r29-free.html (the
overlay) against dist/r29-free-base.html (base21a alone, Version 21), pixel by pixel, for states set by the same
script on both pages, and the text of the program each state is drawn with.

  python -B out/r29/free/mk/same29.py [size] [theme]   -> out/r29/free/same/{new,old}-*.png, logs/same-<size>-<theme>.txt

The old panel of docs/ROUND29.md: (55.56, 100), (100, 100), (20, 100), (150, 33.33), (300, 16.67), (200, 50),
(400, 12.5, honeycomb), (1000, 5), (60, 40, honeycomb), (80, 50, line), each in the 3D and in the 2D view, as Frame it
shows it; one close view; and three states that are not Balls on balls.
The numbers are written into the state (S.k.bt, S.k.brho), because Version 21's dials cannot be set to a pair one
by one. The picture alone is compared (the canvas #view, the controls over it hidden).
The program text: every text the page hands the graphics card is caught (shaderSource) and its length and a sum of
its characters are returned, so the two pages can be compared state by state.
"""
import os, sys
import numpy as np
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import run29 as run

H = run.HEAD
HOOK = ("const P = WebGL2RenderingContext.prototype; if (!window.__src) { window.__src = []; const orig = P.shaderSource; "
        "P.shaderSource = function (s, t) { window.__src.push(t); return orig.call(this, s, t); }; }\n"
        "const sum = t => { let h = 0; for (let i = 0; i < t.length; i++) h = (h * 31 + t.charCodeAt(i)) >>> 0; return t.length + ':' + h; };\n")
OLD = [('55.56-100', 1.4, 1, 0), ('100-100', 1.0, 1, 0), ('20-100', 3.0, 1, 0), ('150-33.33', 0.5 * (100 / 150 + 1), 0.3333, 0),
       ('300-16.67', 0.5 * (100 / 300 + 1), 0.1667, 0), ('200-50', 0.75, 0.5, 0), ('400-12.5-honeycomb', 0.625, 0.125, 1),
       ('1000-5', 0.55, 0.05, 0), ('60-40-honeycomb', 0.5 * (100 / 60 + 1), 0.4, 1), ('80-50-line', 1.125, 0.5, 2)]
STATES = [('m-as-the-page-opens', "")]
first = True
for name, t, rho, grid in OLD:
    for flat in (False, True):
        js = ("$('ap-balls').click(); await sleep(250); " if first else "") + \
            "S.k.bt = %r; S.k.brho = %r; S.k.bgrid = %d; S.k.bit = 16; S.flat = %s; go(); await sleep(60); $('ballsFrame').click();" % (t, rho, grid, 'true' if flat else 'false')
        first = False
        STATES.append(('balls-%s-%s' % (name, '2d' if flat else '3d'), js))
STATES += [
    ('balls-150-33.33-close', "S.k.bt = %r; S.k.brho = 0.3333; S.k.bgrid = 0; S.flat = false; go(); L.cam.yaw = -1.25; L.cam.pitch = 0.5; L.cam.dist = 0.5; L.cam.target = [0.525, 0, 0]; go();" % (0.5 * (100 / 150 + 1))),
    ('k-first-group', "S.k.bt = 1.4; S.k.brho = 1; $('kleinGroup0').click(); await sleep(250);"),
    ('j-rabbit-bulb-cut', "$('mode-j').click(); await sleep(200); $('ap-bulb').click(); await sleep(200); S.c = [-0.122561, 0.744862, 0]; S.cutOn = true; S.cut = 0.05; go();"),
]
TAIL = (" await settle(); const st = $('status').textContent, info = ' | mode ' + S.mode + ', group ' + (S.k.group || 0) + ', t ' + S.k.bt + ', rho ' + S.k.brho + ', grid ' + S.k.bgrid + ', flat ' + S.flat + "
        "', cam ' + [L.cam.yaw, L.cam.pitch, L.cam.dist].map(x => +x.toFixed(4)).join(' ') + ', h ' + (+S.v2.h.toFixed(4)) + ', bound ' + S.view.bound + ', program ' + String(L.R.sig).split('\\n')[0] + "
        "', warn [' + warn() + '], texts handed over so far ' + window.__src.map(sum).join(' ');"
        " return '%s: ' + st + info;")
HIDE = "document.querySelectorAll('#stage > :not(canvas)').forEach(e => { e.style.visibility = 'hidden'; }); await new Promise(r => setTimeout(r, 150)); return 'controls over the picture hidden';"
SHOW = "document.querySelectorAll('#stage > :not(canvas)').forEach(e => { e.style.visibility = ''; }); return 'shown again';"


def steps(tag, pre):
    st = [run.UP]
    for name, js in STATES:
        st.append(dict(js=H + HOOK + "S.q.aa = 4; " + js + TAIL % name, wait='done', timeout=900))
        st.append(dict(js=HIDE, shot='%s/same/%s-%s-%s.png' % (run.OUT, tag, pre, name), clip='#view'))
        st.append(dict(js=SHOW))
    return st


def diff(a, b):
    a = np.asarray(Image.open(a).convert('RGB')).astype(int); b = np.asarray(Image.open(b).convert('RGB')).astype(int)
    if a.shape != b.shape:
        return None, a.shape, b.shape
    d = np.abs(a - b).max(axis=2)
    return int((d > 0).sum()), a.shape, int((np.abs(a - a[0, 0]).max(axis=2) > 8).sum())


if __name__ == '__main__':
    size = sys.argv[1] if len(sys.argv) > 1 else '1400x950'
    theme = sys.argv[2] if len(sys.argv) > 2 else 'dark'
    pre = '%s-%s' % (size, theme)
    SD = os.path.join(run.FREE, 'same'); os.makedirs(SD, exist_ok=True)
    lines = []; told = {}
    for tag, page in (('new', run.PAGE), ('old', run.BASE)):
        code, text, vals = run.shot(page, steps(tag, pre), 'same-%s-%s' % (pre, tag), size, theme)
        run.write('same-%s-%s.log' % (pre, tag), text + 'exit %d\n' % code)
        lines.append('%s page %s: exit %d, %s' % (tag, page, code, 'no console errors' if run.clean(text) else 'SEE same-%s-%s.log' % (pre, tag)))
        told[tag] = dict((v.split(': ')[0], v) for v in vals if ': ' in v and '|' in v)
    total = 0; texts = 0; words = 0
    for name, _ in STATES:
        n, shape, fg = diff(os.path.join(SD, 'new-%s-%s.png' % (pre, name)), os.path.join(SD, 'old-%s-%s.png' % (pre, name)))
        a = told['new'].get(name, ''); b = told['old'].get(name, '')
        prog = a.split(', program ')[1].split(',')[0] if ', program ' in a else '?'
        ta = a.split('texts handed over so far ')[-1]; tb = b.split('texts handed over so far ')[-1]
        same_text = ta == tb          # (the first state is drawn before the texts are caught: its list is empty on both pages)
        wa = a.split(', warn [')[1].split('], texts')[0] if ', warn [' in a else '?'; wb = b.split(', warn [')[1].split('], texts')[0] if ', warn [' in b else '?'
        cam_a = a.split(', cam ')[1].split(', program')[0] if ', cam ' in a else '?'; cam_b = b.split(', cam ')[1].split(', program')[0] if ', cam ' in b else '?'
        if n is None:
            lines.append('%-34s SIZES DIFFER %s %s' % (name, shape, fg)); total += 1; continue
        total += n; texts += 0 if same_text else 1; words += 0 if wa == wb else 1
        lines.append('%-34s %d x %d: pixels that differ %d (not background: %d) | program %s, every text handed to the card the same: %s | camera the same: %s | sentence the same: %s'
                     % (name, shape[1], shape[0], n, fg, prog, same_text, cam_a == cam_b, wa == wb))
        if wa != wb:
            lines.append('      new: %s' % wa); lines.append('      old: %s' % wb)
    lines.append('TOTAL over %d states: %d pixels differ; states whose program texts differ: %d; states whose sentence differs: %d' % (len(STATES), total, texts, words))
    text = '\n'.join(lines) + '\n'
    run.write('same-%s.txt' % pre, text); print(text)

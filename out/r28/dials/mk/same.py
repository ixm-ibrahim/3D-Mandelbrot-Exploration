"""Round 28, Track A, builder, test 2: old pictures. The picture of dist/r28-dials.html against the frozen
dist/r28-base.html (Version 20), pixel by pixel, for states set by the same script on both pages.

  python out/r28/dials/mk/same.py      -> out/r28/dials/same/{new,old}-*.png, logs/same.txt

Six states of Balls on balls with two equal spheres (the default as the row in the Approach list gives it; a typed
size; 100 with the honeycomb grid; a line only in the 2D view; a close-up of the place where two balls kiss at 100,
which is where the spindle works; small neighbours at a low depth) and three states that are not Balls on balls.
The picture alone is compared (the canvas #view; the controls that lie over it are hidden for the screenshot, as
round 27's same6.py does, because the zoom slider's handle differs between two runs of the frozen page itself).
"""
import os, sys
import numpy as np
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import run28 as run

H = run.HEAD
TYPE = "const type = async (id, text) => { const n = $(id + 'Num'); n.focus(); n.value = text; n.dispatchEvent(new Event('input', { bubbles: true })); n.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', bubbles: true })); n.blur(); await sleep(60); };\n"
KISS = "[0.525, 0, 0]"
STATES = [
    ('m-as-the-page-opens', ""),
    ('balls-as-the-row-gives-it', "$('ap-balls').click(); await sleep(200);"),
    ('balls-size-80-typed', "await type('ballsSize', '80'); $('ballsFrame').click();"),
    ('balls-100-honeycomb', "await type('ballsSize', '100'); S.k.bgrid = 1; go(); $('ballsFrame').click();"),
    ('balls-100-kiss-close-up', "S.k.bgrid = 0; L.cam.yaw = -1.25; L.cam.pitch = 0.5; L.cam.dist = 0.3; L.cam.target = " + KISS + "; go();"),
    ('balls-90-line-2d', "S.k.bt = 0.5 * (100 / 90 + 1); S.k.bgrid = 2; S.flat = true; go(); $('ballsFrame').click();"),
    ('balls-30-depth-8', "S.flat = false; S.k.bt = 0.5 * (100 / 30 + 1); S.k.bgrid = 0; S.k.bit = 8; go(); $('ballsFrame').click();"),
    ('k-first-group', "S.k.bit = 16; S.k.bt = 1.4; $('kleinGroup0').click(); await sleep(200);"),
    ('j-rabbit-bulb-cut', "$('mode-j').click(); await sleep(150); $('ap-bulb').click(); await sleep(150); S.c = [-0.122561, 0.744862, 0]; S.cutOn = true; S.cut = 0.05; go();"),
]
TAIL = (" await settle(); const st = $('status').textContent, info = ' | mode ' + S.mode + ', group ' + (S.k.group || 0) + ', t ' + S.k.bt + ', rho ' + S.k.brho + ', grid ' + S.k.bgrid + ', depth ' + S.k.bit + ', flat ' + S.flat + ', cam ' + [L.cam.yaw, L.cam.pitch, L.cam.dist].map(x => +x.toFixed(4)).join(' ') + ', canvas ' + $('view').width + 'x' + $('view').height + ', program ' + String(L.R.sig).replace(/\\n/g, '/').slice(0, 40);"
        " return '%s: ' + st + info;")
HIDE = "document.querySelectorAll('#stage > :not(canvas)').forEach(e => { e.style.visibility = 'hidden'; }); await new Promise(r => setTimeout(r, 150)); return 'controls over the picture hidden';"
SHOW = "document.querySelectorAll('#stage > :not(canvas)').forEach(e => { e.style.visibility = ''; }); return 'shown again';"


def steps(tag):
    st = [run.UP]
    for name, js in STATES:
        st.append(dict(js=H + TYPE + "S.q.aa = 4; " + js + TAIL % name, wait='done', timeout=900))
        st.append(dict(js=HIDE, shot=run.OUT + '/same/%s-%s.png' % (tag, name), clip='#view'))
        st.append(dict(js=SHOW))
    return st


def diff(a, b):
    a = np.asarray(Image.open(a).convert('RGB')).astype(int); b = np.asarray(Image.open(b).convert('RGB')).astype(int)
    if a.shape != b.shape:
        return None, a.shape, b.shape
    d = np.abs(a - b).max(axis=2)
    return int((d > 0).sum()), a.shape, int((np.abs(a - a[0, 0]).max(axis=2) > 8).sum())


if __name__ == '__main__':
    SD = os.path.join(run.DIALS, 'same'); os.makedirs(SD, exist_ok=True)
    lines = []
    for tag, page in (('new', run.PAGE), ('old', run.BASE)):
        code, text, vals = run.shot(page, steps(tag), 'same-' + tag, '1400x950', 'dark')
        run.write('same-%s.log' % tag, text + 'exit %d\n' % code)
        lines.append('%s page %s: exit %d, %s' % (tag, page, code, 'no console errors' if run.clean(text) else 'SEE same-%s.log' % tag))
        lines += ['   ' + v for v in vals if ': ' in v and '|' in v]
    total = 0
    for name, _ in STATES:
        n, shape, fg = diff(os.path.join(SD, 'new-%s.png' % name), os.path.join(SD, 'old-%s.png' % name))
        if n is None:
            lines.append('%-28s SIZES DIFFER %s %s' % (name, shape, fg)); total += 1; continue
        total += n
        lines.append('%-28s picture %d x %d: pixels that differ %d (pixels that are not background: %d)' % (name, shape[1], shape[0], n, fg))
    lines.append('TOTAL over %d states: %d pixels differ' % (len(STATES), total))
    text = '\n'.join(lines) + '\n'
    run.write('same.txt', text); print(text)

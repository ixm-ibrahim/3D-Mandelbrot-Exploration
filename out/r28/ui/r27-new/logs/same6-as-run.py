# copy of out/r27/final/mk/same6.py as run by out/r28/ui/mk/old27.py: 0 fixed picture path(s) changed, nothing else
"""Round 27, final, number 2: six old states, the picture of dist/r27-final.html against the frozen dist/r27-base.html,
pixel by pixel. My own six states (not the fixer's fourteen), set by the same script on both pages.
  python out/r27/final/mk/same6.py      -> out/r27/final/same/{new,old}-*.png, logs/same6.txt
The picture alone is compared (the canvas #view; the controls that lie over it are hidden for the screenshot, because
the checkers found the zoom slider's handle differs between two runs of the frozen page itself). As a second look the
whole #stage with its controls is saved too and compared, and counted apart."""
import os, sys
import numpy as np
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import run

H = run.HEAD
STATES = [
    ('m-as-the-page-opens', ""),
    ('m-lathe-power3-2d', "$('ap-lathe').click(); await sleep(150); S.n = 3; S.flat = true; go();"),
    ('j-rabbit-bulb-cut', "S.n = 2; S.flat = false; $('mode-j').click(); await sleep(150); $('ap-bulb').click(); await sleep(150); S.c = [-0.122561, 0.744862, 0]; S.cutOn = true; S.cut = 0.05; go();"),
    ('j-alongonce-escape-count', "S.cutOn = false; $('ap-alongonce').click(); await sleep(150); S.c = [-0.75, 0.1, 0.05]; S.colour.mode = 2; go();"),
    ('k-first-group-as-it-opens', "S.colour.mode = 0; $('mode-k').click(); await sleep(150);"),
    ('k-first-group-preset3-2d-inside-trap', "L.applyKleinPreset(L.KLEIN_PRESETS[3]); L.frameKleinPreset(L.KLEIN_PRESETS[3]); S.flat = true; S.colour.inMode = 1; go();"),
]
TAIL = (" await settle(); const st = $('status').textContent, info = ' | mode ' + S.mode + ', group ' + (S.k.group || 0) + ', approach ' + L.APPROACHES[S.approach].id + ', flat ' + S.flat + ', canvas ' + $('view').width + 'x' + $('view').height;"
        " return '%s: ' + st + info;")
HIDE = "document.querySelectorAll('#stage > :not(canvas)').forEach(e => { e.style.visibility = 'hidden'; }); await new Promise(r => setTimeout(r, 150)); return 'controls over the picture hidden';"
SHOW = "document.querySelectorAll('#stage > :not(canvas)').forEach(e => { e.style.visibility = ''; }); return 'shown again';"


def steps(tag):
    st = [run.UP]
    for name, js in STATES:
        st.append(dict(js=H + "S.q.aa = 4; " + js + TAIL % name, wait='done', timeout=900, shot=run.OUT + '/same/%s-%s-stage.png' % (tag, name), clip='#stage'))
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
    os.makedirs(os.path.join(run.ENTRY, 'same'), exist_ok=True)
    lines = []
    for tag, page in (('new', run.PAGE), ('old', run.BASE)):
        code, text, vals = run.shot(page, steps(tag), 'same6-' + tag, '1400x950', 'dark')
        run.write('same6-%s.log' % tag, text + 'exit %d\n' % code)
        lines.append('%s page %s: exit %d, %s' % (tag, page, code, 'no console errors' if run.clean(text) else 'SEE same6-%s.log' % tag))
        lines += ['   ' + v for v in vals if ': ' in v and '|' in v]
    total = 0; total_stage = 0
    for name, _ in STATES:
        S_ = os.path.join(run.ENTRY, 'same')
        n, shape, fg = diff(os.path.join(S_, 'new-%s.png' % name), os.path.join(S_, 'old-%s.png' % name))
        m, shape2, _ = diff(os.path.join(S_, 'new-%s-stage.png' % name), os.path.join(S_, 'old-%s-stage.png' % name))
        if n is None:
            lines.append('%-40s SIZES DIFFER %s %s' % (name, shape, fg)); total += 1; continue
        total += n; total_stage += (m or 0)
        lines.append('%-40s picture %d x %d: pixels that differ %d (pixels that are not background: %d); the stage with its controls: %s' % (name, shape[1], shape[0], n, fg, 'sizes differ' if m is None else '%d differ' % m))
    lines.append('TOTAL over %d states: picture alone %d pixels differ; stage with its controls %d' % (len(STATES), total, total_stage))
    text = '\n'.join(lines) + '\n'
    run.write('same6.txt', text); print(text)

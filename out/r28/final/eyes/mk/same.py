"""The eyes, section 1.4 d: old pictures. The picture of dist/r28-eyes.html (the overlay) against the frozen
dist/r28-base-eyes.html (Version 20), pixel by pixel, for states set by the same script on both pages (the way
out/r27/final/mk/same6.py does it; the states are my own).

  python out/r28/final/eyes/mk/same.py [size] [theme]    -> same/{new,old}-<size>-<theme>-*.png, logs/same-<size>-<theme>.txt

Balls on balls with the second sphere at 100: as the row of the Approach list gives it, and seven more (100 with
the square grid; 100 with the honeycomb grid, a close view of the place where two balls kiss; 70, a line only,
depth 40; 10, depth 5, the 2D view; 100 in the 2D view; 35 honeycomb from another side; 25 with depth 200).
Two that only the new page can walk, compared with the plain state on the frozen page:
  the default after a trip past 100 (size typed 300, then Reset this section), against the default;
  size 150, second sphere 50, second sphere back to 100 (which must give 50), against a typed 50.
Seven states that are not Balls on balls: Mandelbrot as the page opens; Mandelbrot, another approach, power 4;
Julia, a third approach, with a cut; Julia in the 2D view, a fourth approach; the first Kleinian group as it
opens; one of its presets in the 2D view; the Learn tab.
The picture alone is compared (the canvas #view, controls over it hidden). For the Learn tab the whole window.
As a second look the whole window is compared for every state that is not Balls on balls.
"""
import os, sys
import numpy as np
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import eyerun as run

H = run.HEAD
KISS = "[0.525, 0, 0]"
NEW = "!!$('ballsRhoNum')"
SEL = "const sel = async v => { const s = $('ballsGrid'); s.value = String(v); s.dispatchEvent(new Event('change', { bubbles: true })); await sleep(60); };\n"
STATES = [
    ('m-as-the-page-opens', ""),
    ('balls-as-the-row-gives-it', "$('ap-balls').click(); await sleep(250);"),
    ('balls-100-square', "await type('ballsSize', '100'); $('ballsFrame').click();"),
    ('balls-100-honeycomb-kiss', "await sel(1); L.cam.yaw = 1.9; L.cam.pitch = 0.9; L.cam.dist = 0.3; L.cam.target = " + KISS + "; go();"),
    ('balls-70-line-depth40', "await type('ballsSize', '70'); await sel(2); await type('ballsDepth', '40'); $('ballsFrame').click();"),
    ('balls-10-depth5-2d', "await type('ballsSize', '10'); await sel(0); await type('ballsDepth', '5'); $('flat').click(); await sleep(100); $('ballsFrame').click();"),
    ('balls-100-2d', "await type('ballsSize', '100'); await type('ballsDepth', '16'); $('ballsFrame').click();"),
    ('balls-35-honeycomb-other-side', "$('flat').click(); await sleep(100); await type('ballsSize', '35'); await sel(1); $('ballsFrame').click(); await sleep(100); L.cam.yaw = 2.2; L.cam.pitch = -0.35; go();"),
    ('balls-25-depth200', "await type('ballsSize', '25'); await sel(0); await type('ballsDepth', '200'); $('ballsFrame').click();"),
    ('balls-default-after-a-trip-past-100', "document.querySelector('#ballsReset button').click(); await sleep(150); if (" + NEW + ") { await type('ballsSize', '300'); await settle(); document.querySelector('#ballsReset button').click(); await sleep(150); } $('ballsFrame').click();"),
    ('balls-50-second-sphere-there-and-back', "if (" + NEW + ") { await type('ballsSize', '150'); await type('ballsRho', '50'); await settle(); await type('ballsRho', '100'); } else { await type('ballsSize', '50'); } $('ballsFrame').click();"),
    ('k-first-group-as-it-opens', "document.querySelector('#ballsReset button').click(); await sleep(150); $('kleinGroup0').click(); await sleep(250);"),
    ('k-first-group-preset5-2d', "L.applyKleinPreset(L.KLEIN_PRESETS[5]); L.frameKleinPreset(L.KLEIN_PRESETS[5]); S.flat = true; go();"),
    ('m-quat4-power4', "S.flat = false; $('mode-m').click(); await sleep(200); $('ap-quat4').click(); await sleep(200); S.n = 4; go();"),
    ('j-turnalong-cut', "S.n = 2; $('mode-j').click(); await sleep(200); $('ap-turnalong').click(); await sleep(200); S.c = [-0.8, 0.156, 0.0]; S.cutOn = true; S.cut = -0.1; go();"),
    ('j-pulledplane-2d', "S.cutOn = false; $('ap-pulledplane').click(); await sleep(200); S.c = [0.285, 0.01, 0.1]; S.flat = true; go();"),
    ('learn-tab', "S.flat = false; go(); await sleep(100); $('mode-l').click(); await sleep(1500);"),
]
WHOLE = {'m-as-the-page-opens', 'k-first-group-as-it-opens', 'k-first-group-preset5-2d', 'm-quat4-power4', 'j-turnalong-cut', 'j-pulledplane-2d', 'learn-tab'}
TAIL = (" await settle(); const st = $('status').textContent, info = ' | mode ' + S.mode + ', group ' + (S.k.group || 0) + ', t ' + S.k.bt + ', rho ' + S.k.brho + ', grid ' + S.k.bgrid + ', depth ' + S.k.bit + ', approach ' + L.APPROACHES[S.approach].id + ', n ' + S.n + ', flat ' + S.flat + ', cam ' + [L.cam.yaw, L.cam.pitch, L.cam.dist].map(x => +x.toFixed(4)).join(' ') + ', canvas ' + $('view').width + 'x' + $('view').height + ', program ' + String(L.R.sig).replace(/\\n/g, '/').slice(0, 60) + ', size box ' + ($('ballsSizeNum') ? $('ballsSizeNum').value : '-');"
        " return '%s: ' + st + info;")
HIDE = "document.querySelectorAll('#stage > :not(canvas)').forEach(e => { e.style.visibility = 'hidden'; }); await new Promise(r => setTimeout(r, 150)); return 'controls over the picture hidden';"
SHOW = "document.querySelectorAll('#stage > :not(canvas)').forEach(e => { e.style.visibility = ''; }); return 'shown again';"


def steps(tag, pre):
    st = [run.UP]
    for name, js in STATES:
        one = dict(js=H + SEL + "S.q.aa = 4; " + js + TAIL % name, wait='done', timeout=900)
        if name in WHOLE:
            one['shot'] = '%s/same/%s-%s-%s-window.png' % (run.OUT, tag, pre, name)
        st.append(one)
        if name != 'learn-tab':
            st.append(dict(js=HIDE, shot='%s/same/%s-%s-%s.png' % (run.OUT, tag, pre, name), clip='#view'))
            st.append(dict(js=SHOW))
    return st


def diff(a, b):
    a = np.asarray(Image.open(a).convert('RGB')).astype(int); b = np.asarray(Image.open(b).convert('RGB')).astype(int)
    if a.shape != b.shape:
        return None, a.shape, b.shape, None
    d = np.abs(a - b).max(axis=2)
    box = None
    if (d > 0).any():
        ys, xs = np.nonzero(d > 0); box = (int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max()))
    return int((d > 0).sum()), a.shape, int((np.abs(a - a[0, 0]).max(axis=2) > 8).sum()), box


if __name__ == '__main__':
    size = sys.argv[1] if len(sys.argv) > 1 else '1400x950'
    theme = sys.argv[2] if len(sys.argv) > 2 else 'dark'
    pre = '%s-%s' % (size, theme)
    SD = os.path.join(run.EYES, 'same'); os.makedirs(SD, exist_ok=True)
    lines = []
    for tag, page in (('new', run.PAGE), ('old', run.BASE)):
        code, text, vals = run.shot(page, steps(tag, pre), 'same-%s-%s' % (pre, tag), size, theme)
        run.write('same-%s-%s.log' % (pre, tag), text + 'exit %d\n' % code)
        lines.append('%s page %s: exit %d, %s' % (tag, page, code, 'no console errors' if run.clean(text) else 'SEE same-%s-%s.log' % (pre, tag)))
        lines += ['   ' + v for v in vals if ': ' in v and '|' in v]
    total = 0; nb = 0; nk = 0
    for name, _ in STATES:
        if name == 'learn-tab':
            continue
        n, shape, fg, box = diff(os.path.join(SD, 'new-%s-%s.png' % (pre, name)), os.path.join(SD, 'old-%s-%s.png' % (pre, name)))
        if n is None:
            lines.append('%-40s SIZES DIFFER %s %s' % (name, shape, fg)); total += 1; continue
        total += n
        lines.append('%-40s picture %d x %d: pixels that differ %d (pixels that are not background: %d)%s' % (name, shape[1], shape[0], n, fg, ' in the box %s' % (box,) if box else ''))
    lines.append('TOTAL, the picture alone, %d states: %d pixels differ' % (len(STATES) - 1, total))
    wt = 0
    for name, _ in STATES:
        if name not in WHOLE:
            continue
        n, shape, fg, box = diff(os.path.join(SD, 'new-%s-%s-window.png' % (pre, name)), os.path.join(SD, 'old-%s-%s-window.png' % (pre, name)))
        if n is None:
            lines.append('%-40s whole window: SIZES DIFFER %s %s' % (name, shape, fg)); wt += 1; continue
        wt += n
        lines.append('%-40s whole window %d x %d: pixels that differ %d%s' % (name, shape[1], shape[0], n, ' in the box %s' % (box,) if box else ''))
    lines.append('TOTAL, the whole window, %d states that are not Balls on balls: %d pixels differ' % (len(WHOLE), wt))
    text = '\n'.join(lines) + '\n'
    run.write('same-%s.txt' % pre, text); print(text)

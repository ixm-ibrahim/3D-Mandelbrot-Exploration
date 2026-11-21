"""Round 27, entry: with the first Kleinian group, and in the Mandelbrot and Julia views, the new page draws what the
frozen page draws. Fourteen states, each a screenshot of the stage (#view, the picture alone) on both pages, compared
pixel by pixel.
  python out/r27/entry/mk/same.py [new page] [frozen page]  -> out/r27/entry/same/*.png, logs/same.txt
A state is set from the handle (the same script on both pages), so nothing of the new controls is touched."""
import json, os, sys
import numpy as np
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import run

NEW = sys.argv[1] if len(sys.argv) > 1 else 'dist/r27-entry.html'
OLD = sys.argv[2] if len(sys.argv) > 2 else 'dist/r27-entry-base.html'
H = run.HEAD
# The controls that lie over the picture (the zoom slider, the buttons) are hidden for the screenshot: with them on, 14
# pixels of the zoom slider's handle differ between two runs of the FROZEN page itself (logs/same-frozen-against-itself.txt).
HIDE = True
STATES = [
    ('k-start', "$('mode-k').click(); await sleep(150);"),
    ('k-flat', "S.flat = true; go();"),
    ('k-flat-inside-trap', "S.colour.inMode = 1; go();"),
    ('k-preset-5', "S.colour.inMode = 0; S.flat = false; L.applyKleinPreset(L.KLEIN_PRESETS[5]); L.frameKleinPreset(L.KLEIN_PRESETS[5]); go();"),
    ('k-own-values-escape-count', "S.k.mx = 0.3; S.k.my = 1.9; S.k.three = false; S.k.iter = 60; S.colour.mode = 2; go();"),
    ('k-example-pearls-and-balls', "S.colour.mode = 0; L.applyExample(L.EXAMPLES[6]);"),
    ('k-example-rings-cut', "L.applyExample(L.EXAMPLES[7]); S.cutOn = true; S.cut = 0.1; go();"),
    ('m-start', "S.cutOn = false; $('resetAll').click(); await sleep(300);"),
    ('m-fold-power3-flat', "$('ap-fold').click(); await sleep(150); S.n = 3; S.flat = true; go();"),
    ('m-mosaic', "S.n = 2; S.flat = false; $('ap-mercator').click(); await sleep(100); S.mosaic = true; S.cutOn = true; S.cut = 0; go();"),
    ('j-basilica', "S.mosaic = false; S.cutOn = false; $('mode-j').click(); await sleep(150); S.c = [-1, 0, 0]; S.iter = 24; go();"),
    ('j-rabbit-turnalong-trapsolid', "$('ap-turnalong').click(); await sleep(150); S.c = [-0.122561, 0.744862, 0]; S.colour.solid = 2; S.colour.trap = 6; go();"),
    ('j-example-chain-of-bubbles', "L.applyExample(L.EXAMPLES[3]);"),
    ('j-flat-inside-deep', "S.colour.solid = 0; S.flat = true; S.colour.inMode = 3; go();"),
]


def steps(tag):
    st = [run.UP]
    for name, js in STATES:
        st.append(dict(js=H + "S.q.aa = 4; " + js + " await settle(); if (%s) { document.querySelectorAll('#stage > :not(canvas)').forEach(e => { e.style.visibility = 'hidden'; }); await sleep(150); }" % ('true' if HIDE else 'false') + " return '%s: ' + $('status').textContent + ' | mode ' + S.mode + ', group ' + (S.k.group || 0) + ', compiles ' + L.R.compiles;" % name,
                       wait='done', timeout=900, shot='out/r27/entry/same/%s-%s.png' % (tag, name), clip='#view'))
    return st


if __name__ == '__main__':
    lines = []
    for tag, page in (('new', NEW), ('old', OLD)):
        code, text, vals = run.shot(page, steps(tag), 'same-' + tag)
        run.write('same-%s.log' % tag, text + 'exit %d\n' % code)
        lines.append('%s page %s: exit %d, %s' % (tag, page, code, 'no console errors' if 'no console errors' in text else 'SEE same-%s.log' % tag))
    total = 0
    for name, _ in STATES:
        a = np.asarray(Image.open(os.path.join(run.ENTRY, 'same', 'new-%s.png' % name)).convert('RGB')).astype(int)
        b = np.asarray(Image.open(os.path.join(run.ENTRY, 'same', 'old-%s.png' % name)).convert('RGB')).astype(int)
        if a.shape != b.shape:
            lines.append('%-32s SIZES DIFFER %s %s' % (name, a.shape, b.shape)); total += 1; continue
        d = np.abs(a - b).max(axis=2); n = int((d > 0).sum()); total += n
        lines.append('%-32s %d x %d: pixels that differ %d (largest step %d of 255); not background: %d' % (name, a.shape[1], a.shape[0], n, int(d.max()), int((np.abs(a - a[0, 0]).max(axis=2) > 8).sum())))
    lines.append('TOTAL pixels that differ over %d states: %d' % (len(STATES), total))
    text = '\n'.join(lines) + '\n'
    run.write('same.txt', text); print(text)

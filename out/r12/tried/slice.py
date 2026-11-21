"""Round 12, tried rules: the slice at z = 0 as the page draws it (2D view), against the one-plane rule's slice.

  python out/r12/tried/slice.py   -> s-<m|j>-<name>.png, slice.txt

The 2D view with the colour mode "Depth from the camera" paints the solid in one flat colour. A pixel counts as
solid when it is within 8 levels of the colour found at a point known to be inside. The pictures share one view,
so the page's own overlays cancel in the comparison.
"""
import os, sys
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run as R

PRE = "const L = window.squaringLab, S = L.S, $ = id => document.getElementById(id); const sleep = ms => new Promise(r => setTimeout(r, ms)); "
END = " S.colour.mode = 4; L.syncControls(); L.refresh(false); L.touch(); if (L.viewChanged) L.viewChanged(); await sleep(200); return '%s: approach ' + L.APPROACHES[S.approach].id + ', mode ' + S.mode + ', flat ' + S.flat + ', cut ' + S.cut + ', failed ' + L.R.failed;"
SETS = [('mercator', 'mercator', ''), ('softfold', 'softfold', ''), ('softfold-pinch', 'softfold', 'S.param.softfold.mix = 2;'),
        ('axisbulb', 'axisbulb', ''), ('axisbulb-k5', 'axisbulb', 'S.param.axisbulb.k = 5; S.param.axisbulb.wob = 0;'),
        ('pillow', 'pillow', 'S.param.pillow.layout = 0;'), ('pillow-smooth', 'pillow', 'S.param.pillow.layout = 1;')]
steps = [{'js': "const L = window.squaringLab; L.R.warmOn = false; return 'page up';", 'wait': 'done', 'timeout': 300}]
names = []
for name, ap, extra in SETS:
    for mode, view in (('m', 'S.v2.x = -0.6; S.v2.y = 0; S.v2.h = 3.2;'), ('j', 'S.c[0] = -1; S.c[1] = 0; S.c[2] = 0; S.v2.x = 0; S.v2.y = 0; S.v2.h = 3.0;')):
        n = 's-%s-%s' % (mode, name)
        js = PRE + "$('ap-%s').click(); await sleep(300); $('mode-%s').click(); await sleep(200); %s S.cutOn = false; S.flat = true; S.cut = 0; %s" % (ap, mode, extra, view) + END % n
        steps.append({'js': js, 'wait': 'done', 'timeout': 600, 'shot': 'out/r12/tried/%s.png' % n, 'clip': '#stage canvas'})
        names.append(n)
code, text = R.shot(R.PAGE, steps, 'slice-steps')
out = [text]


def mask(n, ref, view):
    im = np.asarray(Image.open(os.path.join(HERE, n + '.png')).convert('RGB')).astype(int)
    H, W = im.shape[:2]
    cx, cy, vh = view
    px, py = int(W / 2 + (ref[0] - cx) * H / vh), int(H / 2 - (ref[1] - cy) * H / vh)
    col = np.median(im[py - 3:py + 4, px - 3:px + 4].reshape(-1, 3), axis=0)
    return np.abs(im - col).max(axis=2) <= 8, col


for mode, ref, view in (('m', (-0.1, 0.0), (-0.6, 0.0, 3.2)), ('j', (0.0, 0.0), (0.0, 0.0, 3.0))):
    base, col0 = mask('s-%s-mercator' % mode, ref, view)
    out.append('%s: one-plane slice: %d solid pixels, colour %s' % ('Mandelbrot' if mode == 'm' else 'Julia c = -1', base.sum(), col0.tolist()))
    for name, _, _ in SETS[1:]:
        m, col = mask('s-%s-%s' % (mode, name), ref, view)
        extra, missing = int((m & ~base).sum()), int((base & ~m).sum())
        out.append('   %-16s solid %7d  extra %6d (%.2f %%)  missing %6d (%.2f %%)  colour %s' % (name, m.sum(), extra, 100.0 * extra / base.sum(), missing, 100.0 * missing / base.sum(), col.tolist()))
R.write('slice.txt', '\n'.join(out) + '\n')
print('\n'.join(out))
sys.exit(code)

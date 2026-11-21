"""Round 27, checker A, bullet 1, second way: the flat view as it is on the screen, pixel by pixel.

The lab's 2D view of Balls on balls is saved (canvas alone), and every pixel centre is given its place in the plane
by the lab's own rule (pick() in the 2D view: x = v2.x + (px - w / 2) * v2.h / h, y = v2.y + (h / 2 - py) * v2.h / h,
z = the height of the slice). There my recipe (= the twin = tree.py at all 769500 points of verdicts.py) says inside
or outside. The picture's colours are then read against that: is there a ball's worth of pixels that the picture
paints as inside where the recipe says outside, or the other way round?
  python flat2d.py -> ../logs/flat2d.txt, ../shots/flat2d-*.png
"""
import json, os, sys
import numpy as np
from PIL import Image
from scipy import ndimage
import drive as D
import ballslib as B

CASES = [('g0-t1.4-r16', 0, 1.4, 16, 0.0), ('g1-t1.4-r16', 1, 1.4, 16, 0.0), ('g2-t2.5-r16', 2, 2.5, 16, 0.0), ('g0-t1-r16', 0, 1.0, 16, 0.0), ('g0-t1-r40', 0, 1.0, 40, 0.0),
         ('g0-t1.4-r16-z0.2', 0, 1.4, 16, 0.2), ('g1-t2.5-r40-z-0.15', 1, 2.5, 40, -0.15)]
SET = D.HEAD + """
for (const e of $('stage').children) e.style.visibility = '';
if (!(S.mode === 'k' && S.k.group === 1)) { L.ballsShow(); await settle(); }
S.k.bt = %r; S.k.bgrid = %d; S.k.bit = %d; L.ballsFrame(); S.flat = true; S.cut = %r; S.colour.inside = 0; go(); await sleep(300);
"""
INFO = D.HEAD + """
await settle();
for (const e of $('stage').children) if (e.id !== 'view') e.style.visibility = 'hidden';
await sleep(300);
const w = $('stage').clientWidth, h = $('stage').clientHeight;
return JSON.stringify({ v2: S.v2, cut: S.cut, flat: S.flat, stage: [w, h], k: S.k, p00: L.pick(0.5, 0.5), p11: L.pick(w - 0.5, h - 0.5), colour: S.colour, status: $('status').textContent });
"""
steps = [D.UP]
for name, g, t, R, z in CASES:
    steps.append({'js': SET % (t, g, R, z), 'wait': 'done', 'timeout': 300})
    steps.append({'js': INFO, 'shot': 'out/r27/checka/shots/flat2d-%s.png' % name, 'clip': '#view'})
if len(sys.argv) < 2:
    code, vals, text = D.run(D.PAGE, steps, 'flat2d')
    json.dump(vals, open(os.path.join(D.LOGS, 'flat2d-info.json'), 'w', encoding='utf-8'))
    print('exit', code)
vals = json.load(open(os.path.join(D.LOGS, 'flat2d-info.json'), encoding='utf-8'))
lines = []
for (name, g, t, R, z), info in zip(CASES, vals[1:]):
    img = np.asarray(Image.open(os.path.join(D.CHK, 'shots', 'flat2d-%s.png' % name)).convert('RGB')).astype(int)
    h, w = img.shape[:2]
    v2 = info['v2']; s = v2['h'] / h
    X, Y = np.meshgrid(v2['x'] + (np.arange(w) + 0.5 - w / 2) * s, v2['y'] + (h / 2 - (np.arange(h) + 0.5)) * s)
    # the lab's own answer for the two corner pixels, as a check of the rule
    c0 = info['p00']; c1 = info['p11']
    okmap = abs(c0[0] - X[0, 0]) < 1e-9 and abs(c0[1] - Y[0, 0]) < 1e-9 and abs(c1[0] - X[-1, -1]) < 1e-9 and abs(c1[1] - Y[-1, -1]) < 1e-9 and abs(c0[2] - z) < 1e-12
    ins = B.recipe_inside(X, Y, np.full(X.shape, z), t, g, R)
    ins80 = B.recipe_inside(X, Y, np.full(X.shape, z), t, g, 80)
    # pixels well inside (3 px from any outside pixel) and well outside: what colours does the picture give them?
    deep_in = ndimage.binary_erosion(ins, iterations=3); deep_out = ndimage.binary_erosion(~ins, iterations=3)
    ci = img[deep_in]; co = img[deep_out]
    # a classifier from the picture alone: nearest of the two mean colours is not good enough for a coloured outside,
    # so use what separates them best: the picture's inside colour is one flat colour
    vals_, counts = np.unique(ci.reshape(-1, 3), axis=0, return_counts=True)
    flatcol = vals_[counts.argmax()]; share = counts.max() / max(1, len(ci))
    pic_in = np.abs(img - flatcol).max(2) <= 6
    d = dict(name=name, stage=[w, h], map_ok=bool(okmap), inside=int(ins.sum()), inside_colour=[int(c) for c in flatcol], inside_colour_share=float(share),
             outside_pixels_with_inside_colour=int((pic_in & deep_out).sum()), inside_pixels_without_inside_colour=int((~pic_in & deep_in).sum()),
             differ=int((pic_in != ins).sum()), depth_vs_80=int((ins != ins80).sum()))
    wrong = pic_in != ins
    e = ndimage.distance_transform_edt(np.pad(wrong, 1))[1:-1, 1:-1]
    d['differ_widest_px'] = float(2 * e.max() - 1) if wrong.any() else 0.0
    j = np.unravel_index(e.argmax(), e.shape); d['differ_widest_at'] = [int(j[1]), int(j[0])]
    # the same against 80 rounds: how wide are the false solids of this depth?
    w80 = ins & ~ins80
    e2 = ndimage.distance_transform_edt(np.pad(w80, 1))[1:-1, 1:-1]
    d['depth_false_inside_pixels'] = int(w80.sum()); d['depth_false_inside_widest_px'] = float(2 * e2.max() - 1) if w80.any() else 0.0
    j2 = np.unravel_index(e2.argmax(), e2.shape); d['depth_false_inside_at'] = [int(j2[1]), int(j2[0])]
    lab_, k = ndimage.label(w80, structure=np.ones((3, 3))); d['depth_false_inside_blobs'] = int(k)
    d['depth_false_inside_largest_blob'] = int(np.bincount(lab_.ravel())[1:].max()) if k else 0
    d['span'] = v2['h']
    lines.append(json.dumps(d)); print(lines[-1])
    dimg = np.zeros((h, w, 3), np.uint8); dimg[...] = (16, 18, 24); dimg[ins] = (70, 74, 84); dimg[wrong] = (255, 60, 60); dimg[w80] = (60, 220, 255)
    Image.fromarray(dimg).save(os.path.join(D.CHK, 'shots', 'flat2d-%s-diff.png' % name))
with open(os.path.join(D.LOGS, 'flat2d.txt'), 'w', encoding='utf-8', newline='\n') as f:
    f.write('\n'.join(lines) + '\n')

"""Sheets of the cut solids: picture, model of v8, model of round 9, cropped to the solid. python out/r9/mesh/pairs.py"""
from PIL import Image, ImageDraw
import numpy as np, os
BASE = os.path.dirname(os.path.abspath(__file__))
def panels(tag, job):
    im = Image.open(os.path.join(BASE, tag, 'pics', 'cmp-%s.png' % job)).convert('RGB')
    W, H = im.size; w = W // 3
    return im.crop((0, 0, w, H)), im.crop((w, 0, 2 * w, H))
def box(model):
    a = np.asarray(model).astype(int); m = (np.abs(a - np.array([8, 11, 16])).sum(2) > 30)
    ys, xs = np.where(m); return max(0, xs.min() - 12), max(0, ys.min() - 12), min(model.width, xs.max() + 12), min(model.height, ys.max() + 12)
rows = []
for job in ['cutm-128', 'cutm-256', 'cutm-128-off0', 'cutm-128-off2', 'cutj-128', 'cutr-128', 'cutp-128']:
    pic, old = panels('v8', job); _, new = panels('r9-mesh', job)
    b = box(old)
    t = [x.crop(b) for x in (pic, old, new)]
    for x, lab in zip(t, ('picture', 'model, v8', 'model, round 9')): ImageDraw.Draw(x).text((4, 2), job + ': ' + lab, fill=(255, 255, 255))
    row = Image.new('RGB', (sum(x.width for x in t) + 8, t[0].height), (60, 60, 60)); x0 = 0
    for x in t: row.paste(x, (x0, 0)); x0 += x.width + 4
    rows.append(row)
for name, sel in (('sheet-cut-a.png', rows[:4]), ('sheet-cut-b.png', rows[4:])):
    Wm = max(r.width for r in sel); sheet = Image.new('RGB', (Wm, sum(r.height + 6 for r in sel)), (20, 22, 28)); y = 0
    for r in sel: sheet.paste(r, (0, y)); y += r.height + 6
    sheet.save(os.path.join(BASE, name)); print(name, sheet.size)
# a close look at the rim: the needle end of the default model and of the model at offset 0, three times enlarged
close = []
for job in ('cutm-128', 'cutm-128-off0'):
    pic, old = panels('v8', job); _, new = panels('r9-mesh', job); b = box(old); c = (b[0], b[1], b[0] + 230, b[1] + 150)
    for x, lab in zip((pic, old, new), ('picture', 'v8', 'round 9')):
        t = x.crop(c).resize((690, 450), Image.NEAREST); ImageDraw.Draw(t).text((4, 2), job + ': ' + lab, fill=(255, 255, 255)); close.append(t)
sheet = Image.new('RGB', (3 * 694, 2 * 454), (20, 22, 28))
for k, t in enumerate(close): sheet.paste(t, ((k % 3) * 694, (k // 3) * 454))
sheet.save(os.path.join(BASE, 'sheet-cut-close.png')); print('sheet-cut-close.png', sheet.size)

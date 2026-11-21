"""The sheet for the user. python out/r15/study/make_sheet.py"""
import os, sys, json, textwrap, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import vox
from PIL import Image, ImageDraw, ImageFont
D = os.path.join(HERE, 'data'); T = os.path.join(HERE, 'tiles')
S = 340; PAD = 8; CAP = 58; HEAD = 34
BG = (10, 11, 15)


def font(size, bold=False):
    for n in (('segoeuib.ttf', 'arialbd.ttf') if bold else ('segoeui.ttf', 'arial.ttf')):
        try: return ImageFont.truetype(n, size)
        except OSError: pass
    return ImageFont.load_default()


def fit(im, crop=None):
    if isinstance(im, np.ndarray): im = Image.fromarray(im)
    im = im.convert('RGB')
    if crop:
        w, h = im.size; cw, ch = int(w * crop), int(h * crop)
        im = im.crop(((w - cw) // 2, (h - ch) // 2, (w + cw) // 2, (h + ch) // 2))
    w, h = im.size; k = S / max(w, h)
    im = im.resize((max(1, round(w * k)), max(1, round(h * k))), Image.LANCZOS)
    out = Image.new('RGB', (S, S), (18, 20, 26)); out.paste(im, ((S - im.width) // 2, (S - im.height) // 2))
    return out


def tile(src, crop=None):
    if isinstance(src, np.ndarray): return fit(src, crop)
    for base in (T, HERE):
        p = os.path.join(base, src)
        if os.path.exists(p): return fit(Image.open(p), crop)
    print('missing', src); return Image.new('RGB', (S, S), (40, 20, 20))


def cut_from(npy, scale=14.0):
    return vox.cut_img(np.squeeze(np.load(os.path.join(D, npy))), scale)


def build(rows, notes, path, title):
    ncol = max(len(r[1]) for r in rows)
    W = PAD + ncol * (S + PAD)
    f, fb, ft, fn = font(15), font(18, True), font(24, True), font(17)
    wrap = lambda s, n: [l for para in s.split('\n') for l in (textwrap.wrap(para, n) or [''])]
    note_lines = [l for n in notes for l in wrap(n, int((W - 2 * PAD) / 8.6))]
    H = 50 + len(rows) * (HEAD + CAP + S + PAD) + 20 + 25 * len(note_lines) + 16
    im = Image.new('RGB', (W, H), BG); d = ImageDraw.Draw(im)
    d.text((PAD, 10), title, fill=(245, 245, 245), font=ft)
    y = 50
    for head, tiles in rows:
        d.text((PAD, y + 6), head, fill=(255, 214, 140), font=fb); y += HEAD
        for k, (src, cap, crop) in enumerate(tiles):
            x = PAD + k * (S + PAD)
            for j, line in enumerate(wrap(cap, 47)[:3]):
                d.text((x + 2, y + j * 18), line, fill=(222, 222, 222), font=f)
            im.paste(tile(src, crop), (x, y + CAP))
        y += CAP + S + PAD
    y += 12
    for line in note_lines:
        d.text((PAD, y), line, fill=(225, 225, 225), font=fn); y += 25
    im.save(path); print('wrote', path, im.size)


if __name__ == '__main__':
    q1 = json.load(open(os.path.join(HERE, 'q1.json')))
    rab = np.load(os.path.join(D, 'rab-box-321.npy'))
    rab_z0 = vox.cut_img(rab[:, :, 160])
    rows = [
        ('1. Bodies or one lump?  Julia set for c = -1, first layout', [
            ('cm1-front.png', 'The solid from the front: a ribbed spindle with spikes, not a row of bodies.', None),
            ('cm1-above.png', 'From above.', None),
            ('q1-cut-z0.png', 'Cut at z = 0 (the flat plane): exactly the flat set, bodies touching at points.', None),
            ('q1-cut-y0.png', 'Upright cut along the real axis (y = 0): one band with spikes. The bodies are joined here.', None),
            ('q1-cut-x-touch.png', 'Cut across a touching point (x = -0.618): a figure of eight. There is matter above and below the point.', 0.6),
            ('q1-zoom-x-0.05.png', 'The same cut 24 times closer: the two lobes meet at the point, with the same opening at every size.', None)]),
        ('1. The rabbit (c = -0.12 + 0.74 i), first layout: here the bodies do stand apart and touch at points', [
            ('rab-front.png', 'From the front: faceted bodies with smaller bodies round them.', None),
            ('rab-above.png', 'From above.', None),
            ('rab-below.png', 'From below (the rule is lopsided above and below the plane).', None),
            ('rab-side.png', 'From the side.', None),
            (rab_z0, 'Cut at z = 0: the flat rabbit.', None),
            (cut_from('meetcut-rab-up90-0.2.npy', 30.0), 'Upright cut through the point where three bodies meet (width 0.4): the light wedges are two of the bodies, meeting at that one point.', None)]),
        ('2. Detail at smaller sizes, first layout: a piece of the surface seen closer and closer (flat dark patches are gaps, or the walls of the box)', [
            ('zoom-cm1-0.32.png', 'c = -1, box 0.64 wide.', None), ('zoom-cm1-0.08.png', 'c = -1, box 0.16 wide.', None), ('zoom-cm1-0.02.png', 'c = -1, box 0.04 wide: ridges and grooves running one way.', None),
            ('zoom-rab-0.32.png', 'Rabbit, box 0.64 wide.', None), ('zoom-rab-0.02.png', 'Rabbit, box 0.04 wide: ridges and thin flakes.', None), ('deep-E-zoom-rab-0.005.png', 'Rabbit, box 0.01 wide: only streaks are left. Detail goes on, but it is smeared one way.', None)]),
        ('4. The same rule with a second layout (the Joukowski layout): the rabbit keeps knobs on knobs at every size, but c = -1 turns smooth', [
            ('J10-rab-front.png', 'Rabbit, second layout, from the front: rounder bodies with small bodies round them.', None),
            ('J10-zoom-rab-0.32.png', 'Its surface, box 0.64 wide.', None), ('J10-zoom-rab-0.02.png', 'Box 0.04 wide.', None), ('deep-J10-zoom-rab-0.005.png', 'Box 0.01 wide: still knobs and small bodies, not streaks.', None),
            ('J10-cm1-front.png', 'c = -1, second layout: one smooth lump with horns.', None),
            ('J10-mandel-front.png', 'Mandelbrot solid, second layout: a smooth rock with fins.', None)]),
        ('5. The Mandelbrot solid, first layout: a lopsided rock with fins and folds, no bulbs', [
            ('mandel2-front.png', 'From the front.', None), ('mandel2-above.png', 'From above.', None), ('mandel2-below.png', 'From below.', None), ('mandel2-side.png', 'From the side.', None),
            ('q5-mandel-z0.png', 'Cut at z = 0: the flat Mandelbrot set, point for point.', None),
            ('q5-mandel-y0.png', 'Upright cut along the real axis (y = 0): a filled blob with fins, three times more above the plane than below.', None)]),
        ('6. Power 3 (the same above and below the plane), first layout: the Julia set is the best solid of the study, the Mandelbrot solid is a cushion', [
            ('p3-julia-front.png', 'Julia set for c = i, power 3: a ball with bodies round it on every side.', None),
            ('E3-zoom-0.32.png', 'Its surface, box 0.64 wide: round knobs.', None),
            ('E3-zoom-0.08.png', 'Box 0.16 wide: knobs again.', None),
            ('E3-zoom-0.02.png', 'Box 0.04 wide: and again. Smaller bodies on bodies, not streaks.', None),
            ('p3-mandel-front.png', 'Mandelbrot solid, power 3: a cushion with four horned corners.', None),
            ('q6-p3-mandel-y0.png', 'Its upright cut at y = 0: a plain rounded square.', None)]),
    ]
    notes = json.load(open(os.path.join(HERE, 'sheet-notes.json'), encoding='utf-8'))
    build(rows, notes, os.path.join(HERE, 'sheet-for-user.png'), 'Square pillow rule: what it really looks like (voxel study, round 15)')

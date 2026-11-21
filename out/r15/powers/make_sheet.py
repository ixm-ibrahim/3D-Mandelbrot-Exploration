"""The sheet for the user: parts A (Julia sets by power), B (Mandelbrot solids by power), C (closer looks, power 2),
D (this layout next to the other one), then the notes.  python make_sheet.py [A,B,C,D] ; always restacks."""
import os, sys, numpy as np
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import viz
from viz import turns
D = os.path.join(HERE, 'data')
parts = sys.argv[1].split(',') if len(sys.argv) > 1 else ['A', 'B', 'C', 'D']
CELL = 250
COLS = ['Seen from the front', 'From above (looking down)', 'From below (looking up)', 'Along the x-axis', 'Along the y-axis',
        'Cut at z = 0 (the flat plane)', 'Cut at y = 0 (upright)', 'Cut at x = 0 (upright)']


def solid_row(volfile, cutfile):
    V = np.load(os.path.join(D, volfile)); v = V['inside']
    r = [viz.view(v, k) for k in ('front', 'above', 'below', 'alongx', 'alongy')]
    C = np.load(os.path.join(D, cutfile))
    r += [viz.cut2d(C['iz'], C['dz']), viz.cut2d(C['iy'], C['dy']), viz.cut2d(C['ix'], C['dx'])]
    return r


if 'A' in parts:
    rows = [solid_row('q1-j2-225.npz', 'cuts-j2.npz'), solid_row('q1-j3-225.npz', 'cuts-j3.npz'), solid_row('q1-j4-225.npz', 'cuts-j4.npz'),
            solid_row('q1-j4b-193.npz', 'cuts-j4b.npz'), solid_row('q1-j5-225.npz', 'cuts-j5.npz')]
    rt = ['Power 2, c = -1\n(basilica in the plane)\nbodies round the\nmain one: 2 in the\nplane, 4 in all\n(2 wings, 2 legs)',
          'Power 3, c = i\n3 in the plane,\n9 in all.\nThe cut at x = 0 is\nthe flat set again',
          'Power 4, c = -1\n4 in the plane;\noff the plane they\nhave run together\ninto one ridged lump',
          'Power 4,\nc = (0.5, 0.866, 0)\n4 in the plane,\n16 in all\n(four rows of four)',
          'Power 5,\nc = (0.707, 0.707, 0)\n5 in the plane,\n25 in all\n(five rows of five)']
    viz.sheet(rows, COLS, rt, os.path.join(HERE, 'part-A.png'), cell=CELL,
              title='1. Julia sets, powers 2 to 5: c at the centre of a period-2 body of that power (voxels, 225 per side; power 4 second row 193)')
if 'B' in parts:
    rows = [solid_row('q1-m%d-225.npz' % n, 'cuts-m%d.npz' % n) for n in (2, 3, 4, 5)]
    rt = ['Power 2\nin the plane: the\nMandelbrot set\n(1 lobe on the\nmain body)', 'Power 3\nin the plane:\n2 lobes.\nThe cut at x = 0 is\nthe flat set again', 'Power 4\nin the plane:\n3 lobes', 'Power 5\nin the plane:\n4 lobes']
    viz.sheet(rows, COLS, rt, os.path.join(HERE, 'part-B.png'), cell=CELL,
              title='2. Mandelbrot solids, powers 2 to 5 (voxels, 225 per side)')
if 'C' in parts:
    rows, rt = [], []
    lab = {'bas-meet': 'Power 2, c = -1:\nwhere two bodies\nmeet in the plane\n(-0.618, 0, 0)', 'bas-skin': 'Power 2, c = -1:\na point of the skin\noff the plane, above\nthe middle body',
           'rab-meet': 'Power 2, the rabbit:\nwhere the bodies\nmeet in the plane\n(-0.274, 0.478, 0)', 'rab-skin': 'Power 2, the rabbit:\na point of the skin\noff the plane, above\nthe middle body'}
    for key in ('bas-meet', 'bas-skin', 'rab-meet', 'rab-skin'):
        r = []
        for h in (0.3, 0.075, 0.02):
            f = os.path.join(D, 'q2-zoom-%s-%g.npz' % (key, h))
            r.append(viz.view(np.load(f)['inside'], 'front') if os.path.exists(f) else None)
        for pl, hs in (('xz', (0.3, 0.075, 0.02)), ('yz', (0.3, 0.02))):
            for h in hs:
                f = os.path.join(D, 'q2-cut-%s-%s-%g.npz' % (key, pl, h))
                if os.path.exists(f):
                    C = np.load(f); r.append(viz.cut2d(C['inside'], C['death']))
                else: r.append(None)
        rows.append(r); rt.append(lab[key])
    cols = ['A cube cut out, 0.6 wide', 'Cube 0.15 wide', 'Cube 0.04 wide', 'Upright cut along x, 0.6 wide', 'The same, 0.15 wide', 'The same, 0.04 wide',
            'Upright cut along y, 0.6 wide', 'The same, 0.04 wide']
    viz.sheet(rows, cols, rt, os.path.join(HERE, 'part-C.png'), cell=CELL,
              title='3. Closer and closer, power 2: does detail go on at smaller sizes? (cubes: 129 per side, flat faces are where the cube cuts the solid; cuts: 501 x 501)')
if 'D' in parts:
    def half(volfile):
        V = np.load(os.path.join(D, volfile)); v = V['inside']; N = v.shape[0]
        return [viz.view(v, 'front'), viz.view(v, 'above'), viz.view(v, 'alongy'), viz.cut2d(v[:, N // 2, :], V['death'][:, N // 2, :])]
    rows = [half('q1-j2-225.npz') + half('q4s-pillow-bas-193.npz'),
            half('q2-rabbit-193.npz') + half('q4s-pillow-rab-193.npz'),
            half('q1-m2-225.npz') + half('q4-pillow-m2-193.npz')]
    rt = ['Power 2, c = -1\n(same box, same\nscale, both layouts)', 'Power 2, the rabbit\n(same box, same scale)', 'Power 2,\nMandelbrot solid\n(same scale)']
    cols = ['THIS layout: front', 'THIS: from above', 'THIS: along the y-axis', 'THIS: cut at y = 0',
            'OTHER layout: front', 'OTHER: from above', 'OTHER: along the y-axis', 'OTHER: cut at y = 0']
    viz.sheet(rows, cols, rt, os.path.join(HERE, 'part-D.png'), cell=CELL,
              title='4. This layout (closed form, "from 4D") next to the other layout of the same pillow rule (round 15, pillow_ref)')

# ---------------------------------------------------------------- stack with the notes
ims = [Image.open(os.path.join(HERE, 'part-%s.png' % p)) for p in 'ABCD' if os.path.exists(os.path.join(HERE, 'part-%s.png' % p))]
notes = open(os.path.join(HERE, 'sheet-notes.txt'), encoding='utf-8').read().split('\n') if os.path.exists(os.path.join(HERE, 'sheet-notes.txt')) else []
W = max(i.size[0] for i in ims)
f, fb = turns.font(19), turns.font(27)
head = 64
NH = 30 * len(notes) + 30
H = head + sum(i.size[1] for i in ims) + NH
S = Image.new('RGB', (W, H), (10, 11, 15)); d = ImageDraw.Draw(S)
d.text((12, 14), 'Pillow rule in closed form ("from 4D"): what the power does in 3D. Voxel study, round 15B, powers.', fill=(245, 245, 245), font=fb)
y = head
# notes first after the title? No: pictures first, the notes at the foot
for i in ims:
    S.paste(i, (0, y)); y += i.size[1]
y += 12
for line in notes:
    col = (245, 225, 150) if line.startswith('#') else (215, 215, 215)
    d.text((14, y), line.lstrip('#').strip() if line.startswith('#') else line, fill=col, font=f); y += 30
S.save(os.path.join(HERE, 'sheet-for-user.png'))
print('wrote sheet-for-user.png', S.size)

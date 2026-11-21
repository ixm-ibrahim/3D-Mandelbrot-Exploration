"""Round 25, section klein: the sheets of rough solids. Each solid is rendered once and kept (depth-*.npy).

    python out/r25/klein/sheet.py render <object> <eye>      object: see OBJ below; eye: a (front) or top
    python out/r25/klein/sheet.py compose                    sheet.png (front eye) and sheet-top.png (from above)
"""
import os, sys, time
import numpy as np
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, 'out', 'r21', 'lib')); sys.path.insert(0, HERE)
import mem as M
import tree as T
import repair as R

CAMS = {'a': (0.45, 0.5, 1.0), 'top': (0.2, 1.0, 0.35)}
W, H, ND = 440, 330, 200
B, RAB = (-1.0, 0.0, 0.0), M.RABBIT
# key -> (rule maker, c, steps, caption)
OBJ = {
    'tree-line':  (lambda: T.tree('line'), T.ZERO, 14, 'pearl tree, one plane (the flat tree blown up)'),
    'tree-gauss': (lambda: T.tree('gauss'), T.ZERO, 14, 'pearl tree, Gaussian integers'),
    'tree-eisen': (lambda: T.tree('eisen'), T.ZERO, 14, 'pearl tree, Eisenstein integers'),
    'tree-gauss-big': (lambda: T.tree('gauss', t=1.118, k2=0.8), T.ZERO, 14, 'pearl tree, Gaussian, the size dial turned up'),
    'paper-b':    (R.RULES['paper'], B, 28, 'the paper\'s rule (one plane), c = -1'),
    'paper-r':    (R.RULES['paper'], RAB, 28, 'the paper\'s rule (one plane), rabbit'),
    'kfix-b':     (R.RULES['kfix'], B, 28, 'the paper\'s rule re-spaced (flat cut exact), c = -1'),
    'kfix-r':     (R.RULES['kfix'], RAB, 28, 'the paper\'s rule re-spaced (flat cut exact), rabbit'),
    'two-b':      (lambda: M.bench('twoplane'), B, 28, 'for comparison: two planes, c = -1'),
    'one-b':      (lambda: M.bench('oneplane'), B, 28, 'for comparison: one plane, c = -1'),
    'one-r':      (lambda: M.bench('oneplane'), RAB, 28, 'for comparison: one plane, rabbit'),
}
ROWS = [['tree-line', 'tree-gauss', 'tree-eisen', 'tree-gauss-big'], ['paper-b', 'kfix-b', 'paper-r', 'kfix-r']]
CAMS['end'] = (1.0, 0.3, 0.35)                 # nearly along the x-axis: shows the pattern round the axis


def big(lat=None):
    """tree-big.png: the Gaussian and the Eisenstein tree, finer, from the front and nearly end-on.
    big('gauss') / big('eisen') render and keep; big() composes what is there."""
    w, h, nd, pad = 560, 420, 320, 10; t0 = time.time()
    if lat:
        for eye in ('a', 'end'):
            dep, px = M.solid(T.tree(lat), T.ZERO, w, h, nd, 14, half_w=1.45, cam=CAMS[eye]); np.savez(path('big-' + lat, eye), dep=dep, px=px)
            print('big', lat, eye, '%.0f s' % (time.time() - t0)); sys.stdout.flush()
        return
    im = Image.new('RGB', (pad + 2 * (w + pad), 40 + 2 * (h + pad)), (12, 14, 20)); d = ImageDraw.Draw(im)
    d.text((pad, 8), 'The pearl tree: Gaussian integers (left), Eisenstein integers (right); from the front (top), nearly end-on (bottom)', fill=(240, 240, 245), font=M.font(18))
    for j, la in enumerate(('gauss', 'eisen')):
        for i, eye in enumerate(('a', 'end')):
            if os.path.exists(path('big-' + la, eye)):
                f = np.load(path('big-' + la, eye)); im.paste(Image.fromarray(M.shade_solid(f['dep'], float(f['px']))), (pad + j * (w + pad), 40 + i * (h + pad)))
    im.save(os.path.join(HERE, 'tree-big.png')); print('wrote tree-big.png')


def path(key, eye):
    return os.path.join(HERE, 'depth-%s-%s.npz' % (key, eye))


def render(key, eye):
    mk, c, steps, cap = OBJ[key]; t0 = time.time(); tr = key.startswith('tree')
    if key == 'kfix-r':                        # the slow one (many points stay): coarser blocks, 24 steps; the tile is enlarged when pasted
        dep, px = M.solid(mk(), c, 352, 264, 140, 24, cam=CAMS[eye])
    else:
        dep, px = M.solid(mk(), c, W, H, 280 if tr else ND, steps, half_w=1.5 if tr else 1.75, cam=CAMS[eye])
    np.savez(path(key, eye), dep=dep, px=px)
    print('rendered', key, eye, '%.0f s' % (time.time() - t0), 'pixels hit: %d' % int(np.isfinite(dep).sum()))


def compose():
    pad = 10
    for eye, out in (('a', 'sheet.png'), ('top', 'sheet-top.png')):
        im = Image.new('RGB', (pad + 4 * (W + pad), 44 + len(ROWS) * (H + pad)), (12, 14, 20)); d = ImageDraw.Draw(im)
        d.text((pad, 10), 'Section klein, rough solids, eye %s. Top: the group picture (no c, and no rabbit: three balls cannot touch at one point). Below: rules "square, add c".'
               % ('in front' if eye == 'a' else 'above'), fill=(240, 240, 245), font=M.font(17))
        for i, row in enumerate(ROWS):
            for j, key in enumerate(row):
                x, y = pad + j * (W + pad), 44 + i * (H + pad)
                if key is None:
                    d.text((x + 16, y + 120), 'No pearl tree can be a rabbit:', fill=(200, 200, 205), font=M.font(17))
                    d.text((x + 16, y + 146), 'three balls cannot touch at one point.', fill=(200, 200, 205), font=M.font(17)); continue
                if not os.path.exists(path(key, eye)):
                    d.text((x + 16, y + 140), '(not rendered: %s)' % key, fill=(160, 90, 90), font=M.font(15)); continue
                f = np.load(path(key, eye))
                im.paste(Image.fromarray(M.shade_solid(f['dep'], float(f['px']))).resize((W, H), Image.LANCZOS), (x, y)); d.text((x + 6, y + 4), OBJ[key][3], fill=(150, 160, 175), font=M.font(13))
        im.save(os.path.join(HERE, out)); print('wrote', out, im.size)


if __name__ == '__main__':
    if sys.argv[1] == 'render':
        render(sys.argv[2], sys.argv[3])
    elif sys.argv[1] == 'big':
        big(sys.argv[2] if len(sys.argv) > 2 else None)
    else:
        compose()

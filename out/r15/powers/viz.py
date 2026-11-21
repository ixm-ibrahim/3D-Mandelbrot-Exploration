"""Pictures: views of a voxel solid (turns.render), cuts, labelled sheets."""
import os, sys, numpy as np
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, 'out', 'r14', 'turns'))
import turns

VIEWS = {'front': (-60, 22), 'above': (-90, 89.9), 'below': (-90, -89.9), 'alongx': (0, 0), 'alongy': (-90, 0), 'back': (120, 22)}


def view(vol, name, out=None):
    az, el = VIEWS[name]
    return turns.render(vol, az=az, el=el, out=out)


def cut2d(a, d=None, bg=(18, 20, 26), edge=None):
    """a bool [i, j] (i to the right, j up), d death steps or None. Returns RGB rows top to bottom."""
    img = np.zeros(a.shape + (3,), np.float32); img[:] = bg
    if d is not None:
        t = np.clip(d.astype(np.float32) / 14.0, 0, 1); t[d == 0] = 0
        for ch, col in enumerate((70, 110, 170)): img[:, :, ch] = bg[ch] + (col - bg[ch]) * t
    img[a] = (235, 225, 200)
    if edge is not None:
        from scipy import ndimage
        e = edge & ~ndimage.binary_erosion(edge)
        img[e] = (255, 60, 60)
    return np.transpose(np.clip(img, 0, 255).astype(np.uint8), (1, 0, 2))[::-1]


def cut(vol, death, axis, index=None):
    N = vol.shape['xyz'.index(axis)]
    m = N // 2 if index is None else index
    sl = [slice(None)] * 3; sl['xyz'.index(axis)] = m
    return cut2d(vol[tuple(sl)], None if death is None else death[tuple(sl)])


def sheet(rows, col_titles, row_titles, path, title=None, cell=300, note=None, fs=16, left=210):
    f, fb = turns.font(fs), turns.font(fs + 6)
    ncol = max(len(r) for r in rows)
    top, pad = 40 + (46 if title else 0), 6
    foot = (fs + 9) * (len(note) if note else 0) + (14 if note else 0)
    W = left + ncol * (cell + pad) + pad
    H = top + len(rows) * (cell + pad) + pad + foot
    im = Image.new('RGB', (W, H), (10, 11, 15)); d = ImageDraw.Draw(im)
    if title: d.text((12, 8), title, fill=(240, 240, 240), font=fb)
    for j, t in enumerate(col_titles):
        for k, line in enumerate(t.split('\n')):
            d.text((left + j * (cell + pad) + 4, top - 32 + k * (fs + 2) - (fs + 2) * (t.count('\n'))), line, fill=(215, 215, 215), font=f)
    for i, r in enumerate(rows):
        y = top + i * (cell + pad)
        for k, line in enumerate(row_titles[i].split('\n')):
            d.text((10, y + 8 + k * (fs + 6)), line, fill=(215, 215, 215), font=f)
        for j, a in enumerate(r):
            if a is None: continue
            p = Image.fromarray(a) if isinstance(a, np.ndarray) else a
            if p.size != (cell, cell): p = p.resize((cell, cell), Image.LANCZOS)
            im.paste(p, (left + j * (cell + pad), y))
    if note:
        y = H - foot + 4
        for line in note:
            d.text((12, y), line, fill=(205, 205, 205), font=f); y += fs + 9
    im.save(path)
    return path

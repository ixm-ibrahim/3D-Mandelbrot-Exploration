"""Working sheet (internal names) for the hinged rule: cuts along pages through the HINGE (the line from 0 to the
meeting point), cuts across it, solids from two eye positions; one plane and along beside it.
python out/r22/design/sheet2.py rabbit|siegel|t02|sanmarco"""
import sys, os, time
import numpy as np
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dlib as L
M, D = L.M, L.D
R = L.refs()
SETS = {'rabbit': M.RABBIT, 'siegel': M.SIEGEL, 't02': (-1.0, 0.2, 0.0), 'sanmarco': (-0.75, 0.0, 0.0), 'basilica': (-1.0, 0.0, 0.0),
        't01': (-1.0, 0.1, 0.0), 'rabbit2': (-0.122561, -0.744862, 0.0), 'p4': (0.282271, 0.530060, 0.0), 'p5': (-0.504340, 0.562766, 0.0)}


def hinge_cut(rule, c, a, tilt, w, h, steps, box=(-1.8, 1.8, -1.3, 1.3)):
    """A page through the hinge line (turn a in the flat page), tilted `tilt` degrees out of the flat page."""
    u, s = np.meshgrid(np.linspace(box[0], box[1], w), np.linspace(box[3], box[2], h)); t = np.radians(tilt)
    hx, hy = np.cos(a), np.sin(a); nx, ny = -np.sin(a), np.cos(a)
    return M.stay(rule, u * hx + s * np.cos(t) * nx, u * hy + s * np.cos(t) * ny, s * np.sin(t), c[0], c[1], c[2], steps)


def hinge_across(rule, c, a, u0, w, steps, Lh=1.3):
    p, q = np.meshgrid(np.linspace(-Lh, Lh, w), np.linspace(Lh, -Lh, w))
    hx, hy = np.cos(a), np.sin(a); nx, ny = -np.sin(a), np.cos(a)
    return M.stay(rule, u0 * hx + p * nx, u0 * hy + p * ny, q, c[0], c[1], c[2], steps)


if __name__ == '__main__':
    which = sys.argv[1]; c = SETS[which]
    names = sys.argv[2:] or ['oneplane', 'along', 'alonghinge']
    rules = [R[n] if n in R else D.get(n) for n in names]
    a = float(D.meeting_turn(c[0], c[1])); al = (1 - np.sqrt(1 - 4 * complex(c[0], c[1]))) / 2
    um = al.real * np.cos(a) + al.imag * np.sin(a)                      # where the meeting point sits on the hinge
    tilts = (0.0, 11.25, 22.5, 45.0, 90.0); acr = (0.0, um, um / 2); cams = ((0.45, 0.5, 1.0), (1.0, 0.45, 0.25), (-0.3, 1.0, 0.35))
    cw, ch, sw, sh, steps = 250, 180, 280, 210, 60; pad = 8; t0 = time.time()
    heads = ['page through the hinge, tilted %g' % t for t in tilts] + ['across the hinge at %.2f' % u for u in acr] + ['solid, eye %s' % (cm,) for cm in cams]
    tw = [cw] * len(tilts) + [ch] * len(acr) + [sw] * len(cams)
    W = pad + sum(t + pad for t in tw); H = 50 + len(rules) * (sh + 46)
    im = Image.new('RGB', (W, H), (12, 14, 20)); d = ImageDraw.Draw(im)
    d.text((pad, 8), '%s, c = (%.4f, %.4f): hinge turned %.1f degrees, meeting point at %.3f on it (cuts %d steps, solids 40)' % (which, c[0], c[1], np.degrees(a), um, steps), fill=(240, 240, 245), font=M.font(18))
    for i, r in enumerate(rules):
        y = 50 + i * (sh + 46); d.text((pad, y), '%s: %s' % (r.name, r.label), fill=(235, 220, 170), font=M.font(15))
        pics = [M.shade(hinge_cut(r, c, a, t, cw, ch, steps), steps) for t in tilts] + [M.shade(hinge_across(r, c, a, u, ch, steps), steps) for u in acr]
        for cm in cams:
            dep, px = M.solid(r, c, sw, sh, 200, 40, cam=cm); pics.append(M.shade_solid(dep, px))
        x = pad
        for hd, pic in zip(heads, pics):
            d.text((x, y + 20), hd, fill=(150, 160, 175), font=M.font(11)); im.paste(Image.fromarray(pic), (x, y + 38)); x += pic.shape[1] + pad
        print('sheet2', which, r.name, '%.0f s' % (time.time() - t0)); sys.stdout.flush()
    im.save(os.path.join(L.HERE, 'w2-%s.png' % which))

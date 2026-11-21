"""Cuts coloured by what ONE step does to a tiny ball at each point, with the solid's outline on top.

    import zones as Z
    img = Z.tile('along', ('across', 0.0), c, w, L, steps)        # cut across the x-axis at x = 0, y to the right, z up, half-width L
    img = Z.tile('along', ('page', 30.0), c, w, box, steps)       # cut along the page turned 30 degrees from the flat page
"""
import numpy as np
import stab as T
M = T.M

COL = np.array([(52, 150, 138), (222, 190, 84), (224, 120, 48), (150, 78, 190)], float)   # keeps / squeezes / squeezes hard / inside out
NAMES = ['keeps shapes', 'squeezes', 'squeezes hard', 'turns inside out']


def grid(kind, w, ext):
    if kind[0] == 'across':
        L = ext; p, q = np.meshgrid(np.linspace(-L, L, w), np.linspace(L, -L, w)); return np.full_like(p, kind[1]), p, q
    box = ext; h = int(round(w * (box[3] - box[2]) / (box[1] - box[0])))
    u, s = np.meshgrid(np.linspace(box[0], box[1], w), np.linspace(box[3], box[2], h)); a = np.radians(kind[1])
    return u, s * np.cos(a), s * np.sin(a)


def cats(name, P):
    s, det = T.stretch(T.jac(T.rule(name), *P)); return T.category(s, det), T.ratio(s), det


def tile(name, kind, c, w, ext, steps=60, outline=True, dim=0.42):
    P = grid(kind, w, ext); cat, q, det = cats(name, P)
    ins = M.stay(M.bench(name), *P, c[0], c[1], c[2], steps) >= steps
    img = COL[cat] * np.where(ins, 1.0, dim)[..., None]
    if outline:
        e = np.zeros_like(ins)
        e[:-1] |= ins[:-1] != ins[1:]; e[1:] |= ins[:-1] != ins[1:]; e[:, :-1] |= ins[:, :-1] != ins[:, 1:]; e[:, 1:] |= ins[:, :-1] != ins[:, 1:]
        img[e & ins] = (255, 255, 255)
    return img.astype(np.uint8), cat, ins

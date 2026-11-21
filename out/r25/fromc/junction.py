"""Round 25, fromc: can the "two planes" / "along" look exist where q bodies meet at one point?

At a meeting point q bodies stand in a flat ring, 360/q degrees apart. The look of "two planes" (N = 4) or "along"
(N = 8) says: the bodies fastened to a body are the same after a turn of 360/N degrees about that body's own line
(the line from the meeting point into the body). So the set of bodies at the meeting point must be kept by a turn of
360/N about each of the q lines. Count how many different directions that forces (words up to a given length).

    python out/r25/fromc/junction.py
"""
import numpy as np


def rot(axis, ang):
    a = np.asarray(axis, float); a = a / np.linalg.norm(a); K = np.array([[0, -a[2], a[1]], [a[2], 0, -a[0]], [-a[1], a[0], 0]])
    return np.eye(3) + np.sin(ang) * K + (1 - np.cos(ang)) * K @ K


def orbit(q, N, depth=7, tol=1e-6):
    axes = [np.array([np.cos(2 * np.pi * k / q), np.sin(2 * np.pi * k / q), 0.0]) for k in range(q)]
    gens = [rot(a, 2 * np.pi / N) for a in axes]
    pts = list(axes); counts = [len(pts)]; frontier = list(axes)
    for _ in range(depth):
        new = []
        for p in frontier:
            for g in gens:
                v = g @ p
                if min(np.linalg.norm(v - w) for w in pts + new) > tol:
                    new.append(v)
        pts += new; frontier = new; counts.append(len(pts))
        if not new or len(pts) > 1500:
            break
    P = np.array(pts); d = np.clip(P @ P.T, -1, 1); np.fill_diagonal(d, -1)
    return counts, float(np.degrees(np.arccos(d.max())))


if __name__ == '__main__':
    print('q bodies in a ring, turn of 360/N about each body\'s own line: number of directions forced after 0, 1, 2, ... rounds; closest pair')
    for q in (2, 3, 4, 5):
        for N in (2, 3, 4, 8):
            c, sep = orbit(q, N)
            closed = len(c) >= 2 and c[-1] == c[-2]
            print('  q = %d, N = %d: %s %s; closest two directions %.1f degrees apart'
                  % (q, N, c, 'CLOSES (a finite set)' if closed else 'keeps growing', sep))

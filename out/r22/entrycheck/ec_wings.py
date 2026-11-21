"""Round 22, entrycheck: are the 'wings' of Along once in the Mandelbrot view films without thickness, as the builder says?
My own rule (ec_rules.py), the lab-only stops of my own cameras (lab-only.json from ec_parity.py).
  python out/r22/entrycheck/ec_wings.py -> wings.txt
"""
import json, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import ec_rules as E

rep = []
def say(*a):
    t = ' '.join(str(x) for x in a); rep.append(t); print(t); sys.stdout.flush()

# 1. the body: random c, Along once against one plane
rng = np.random.default_rng(11); N = 200000
cx = rng.uniform(-2.1, 0.6, N); cy = rng.uniform(-1.3, 1.3, N); cz = rng.uniform(-1.3, 1.3, N)
for steps in (27, 80):
    a = E.stay('alongonce', cx, cy, cz, cx, cy, cz, steps) >= steps
    b = E.stay('oneplane', cx, cy, cz, cx, cy, cz, steps) >= steps
    say('random c in the box, %d steps: inside Along once %d, one plane %d, verdicts that differ %d of %d' % (steps, a.sum(), b.sum(), (a != b).sum(), N))

# 2. the lab-only stops
L = json.load(open(os.path.join(HERE, 'lab-only.json')))
for key in ('alongonce man', 'alongonce man2'):
    d = L.get(key)
    if not d or not d['pts']:
        say(key, ': no lab-only stops'); continue
    P = np.array(d['pts']); RD = np.array(d['rd']); steps_lab = d['iter'] - 1
    say('')
    say('%s: %d lab-only stops; the lab asks for %d squarings' % (key, len(P), steps_lab))
    own = E.stay('alongonce', P[:, 0], P[:, 1], P[:, 2], P[:, 0], P[:, 1], P[:, 2], 300)
    say('  steps the stop point itself stays (of 300): median %d, least %d, most %d' % (np.median(own), own.min(), own.max()))
    pick = np.linspace(0, len(P) - 1, min(12, len(P))).astype(int)
    grew = 0; thick = []
    for i in pick:
        p, rd = P[i], RD[i]; lo, hi = -0.05, 0.05; seq = []; seq1 = []
        for it in range(9):
            t = np.linspace(lo, hi, 4001); q = p + t[:, None] * rd
            n = E.stay('alongonce', q[:, 0], q[:, 1], q[:, 2], q[:, 0], q[:, 1], q[:, 2], 400)
            n1 = E.stay('oneplane', q[:, 0], q[:, 1], q[:, 2], q[:, 0], q[:, 1], q[:, 2], 400)
            j = int(np.argmax(n)); seq.append(int(n[j])); seq1.append(int(n1.max()))
            if it == 0:
                w = (n >= steps_lab).sum() * (hi - lo) / 4000; first_w = w
            c0 = t[j]; half = (hi - lo) / 40; lo, hi = c0 - half, c0 + half
        # the width of the stretch that stays the lab's count, found by narrowing on it
        thick.append(first_w)
        if seq[-1] >= seq[0] + 12: grew += 1
        say('  stop %3d at (%.3f, %.3f, %.3f): longest stay as the stretch along the line of sight narrows from 0.1 by 20 each time: %s | one plane at the same places: %s | width that stays %d steps in the first pass: %.2g'
            % (i, p[0], p[1], p[2], ' '.join(map(str, seq)), ' '.join(map(str, seq1)), steps_lab, first_w))
    say('  on %d of %d lines the longest stay grew by 12 steps or more while narrowing' % (grew, len(pick)))
open(os.path.join(HERE, 'wings.txt'), 'w', encoding='utf-8', newline='\n').write('\n'.join(rep) + '\n')

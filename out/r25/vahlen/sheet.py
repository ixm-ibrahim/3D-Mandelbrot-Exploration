"""Rough solids for the section "vahlen". python out/r25/vahlen/sheet.py a|top [part]
part 1: one plane, holo, lathe 90        part 2: spin-V, spin-up        (two parts so that each run stays short)"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import vrules as V
M = V.M

if __name__ == '__main__':
    tag = sys.argv[1] if len(sys.argv) > 1 else 'a'; part = sys.argv[2] if len(sys.argv) > 2 else '1'
    cam = {'a': (0.45, 0.5, 1.0), 'top': (0.2, 1.0, 0.35)}[tag]
    rules = {'1': [V.R_one(), V.R_holo(), V.R_lathe_b(90)], '2': [V.spin('V'), V.spin('up')]}[part]
    out = os.path.join(HERE, 'part-%s-%s.png' % (tag, part))
    M.julia_sheet(rules, out, sets=[V.SETS[0], V.SETS[1]], w=400, h=300, nd=200, steps=30, cam=cam, title='Rough solids, eye at %s' % (cam,))
    print('wrote', out)

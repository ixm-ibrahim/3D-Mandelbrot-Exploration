"""Working sheets (internal names): the new rules beside one plane and along, basilica and rabbit.
python out/r22/design/sheet1.py basilica|rabbit [names...]"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dlib as L
M, D = L.M, L.D
which = sys.argv[1]
R = L.refs()
names = sys.argv[2:] or ['oneplane', 'along'] + [r.name for r in D.RULES]
rules = [R[n] if n in R else D.get(n) for n in names]
labels = ['%s: %s' % (r.name, r.label) for r in rules]
tag = '' if len(sys.argv) <= 2 else '-' + '-'.join(names)
if which == 'basilica':
    L.sheet(rules, labels, L.BAS, os.path.join(L.HERE, 'w-basilica%s.png' % tag), 'basilica c = -1 (cuts 60 steps, solids 40 steps)', across=(0.0, -1.0))
else:
    L.sheet(rules, labels, L.RAB, os.path.join(L.HERE, 'w-rabbit%s.png' % tag), 'rabbit (cuts 60 steps, solids 40 steps)', across=(-0.28, 0.04))

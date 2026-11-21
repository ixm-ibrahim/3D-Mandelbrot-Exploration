"""The eyes: what each view really showed (the numbers the page held), against what its name asks for.
My first runs pressed the wrong element for "Reset this section" (the box round the button, which does nothing),
so a view began from the dials of the view before it. This lists every kept view of a tag.
  python out/r28/eyes/mk/slip.py <tag>    -> logs/reset-slip-<tag>.txt"""
import glob, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import views
tag = sys.argv[1]
E = os.path.dirname(HERE)
out = []
for f in sorted(glob.glob(os.path.join(E, 'rays', tag + '-*.json')), key=os.path.getmtime):
    m = json.load(open(f, encoding='utf-8'))['meta']
    v = views.V[m['name']]
    ep, er = views.expected_rho(v['p'], v['rho'])
    et = 1.4 if abs(ep - 55.56) < 0.06 else 0.5 * (100 / ep + 1)
    ok = abs(m['k']['bt'] - et) < 1e-9 and abs(m['k']['brho'] - er) < 1e-9 and m['k']['bit'] == v['depth'] and m['k']['bgrid'] == v['grid']
    a = m['afterReset']; fresh = abs(a['bt'] - 1.4) < 1e-12 and a['brho'] == 1 and a['bgrid'] == 0 and a['bit'] == 16
    out.append('%-26s asked: size %-6s second sphere %-5s grid %d depth %-3d | after the reset press: %s | the page held: size %.2f, second sphere %.2f %%, grid %d, depth %d | %s'
               % (m['name'], v['p'], v['rho'], v['grid'], v['depth'], 'the defaults' if fresh else 'NOT reset (size %.2f, second sphere %.2f %%)' % (100 / (2 * a['bt'] - 1), 100 * a['brho']),
                  100 / (2 * m['k']['bt'] - 1), 100 * m['k']['brho'], m['k']['bgrid'], m['k']['bit'], 'as the name says' if ok else 'NOT what the name says'))
text = '\n'.join(out) + '\n'
open(os.path.join(E, 'logs', 'reset-slip-%s.txt' % tag), 'w', encoding='utf-8', newline='\n').write(text)
print(text)

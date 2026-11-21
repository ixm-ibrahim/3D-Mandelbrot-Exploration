"""The opening look: python out/r6/colour/look.py <page> <label> [zoom]

Draws the opening Mandelbrot view, the Julia set for c = -1 and the Douady rabbit at Balanced (4 passes) for a grid of
"Orbit steps the trap reads", glow width and trap radius, into out/r6/colour/<label>/ and one sheet per subject.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import scenes as s

page, label = sys.argv[1], sys.argv[2]
zoom = float(sys.argv[3]) if len(sys.argv) > 3 else 1
SUBJ = [('m', ""), ('jb', s.JB), ('jr', s.JR)]
GRID = [(reach, glow, radius) for radius in (1, 0.7) for glow in (1, 2, 3) for reach in (4, 6, 12)]
todo = []
for sn, sj in SUBJ:
    for reach, glow, radius in GRID:
        name = 'l-%s-r%s-g%d-k%02d' % (sn, str(radius).replace('.', ''), glow, reach)
        todo.append((name, s.B4 + 'S.q.aa = 2;' + sj + "C.reach = %d; C.glow = %d; C.radius = %s; S.view.fov /= %s;" % (reach, glow, radius, zoom)))
if '--sheet-only' not in sys.argv:
    s.shoot(page, label, (), extra=todo)
for sn, _ in SUBJ:
    s.grid([s.tile(label, n, 264, n[2:]) for n, _ in todo if n.startswith('l-%s-' % sn)], 6, 'look-%s-%s.png' % (label, sn))

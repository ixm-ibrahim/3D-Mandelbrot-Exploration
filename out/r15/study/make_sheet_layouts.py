"""Second sheet: the layouts side by side, and the Julia sets with c off the kept planes. python out/r15/study/make_sheet_layouts.py"""
import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import make_sheet as M
rows = [
    ('Rabbit, power 2, six layouts (first layout = the one in the brief)', [
        ('rab-front.png', 'First layout (ellipses, square pillow, seam factor 1/2).', None),
        ('E08-rab-front.png', 'Ellipses, pillow height 0.8.', None),
        ('Ea35-rab-front.png', 'Ellipses, seam factor 0.35.', None),
        ('J08-rab-front.png', 'Joukowski layout, pillow height 0.8.', None),
        ('J10-rab-front.png', 'Joukowski layout, square pillow.', None),
        ('J13-rab-front.png', 'Joukowski layout, pillow height 1.3.', None)]),
    ('c = -1, power 2, the same six layouts: fused in every one', [
        ('cm1-front.png', 'First layout: ribbed spindle.', None), ('E08-cm1-front.png', 'Ellipses, height 0.8.', None), ('Ea35-cm1-front.png', 'Ellipses, seam factor 0.35.', None),
        ('J08-cm1-front.png', 'Joukowski, height 0.8.', None), ('J10-cm1-front.png', 'Joukowski, square: smooth lump.', None), ('J13-cm1-front.png', 'Joukowski, height 1.3: smooth lump with horns.', None)]),
    ('Joukowski layout close up (rabbit), and Julia sets with c lifted off the flat plane', [
        ('J13-zoom-rab-0.08.png', 'Joukowski, height 1.3: rabbit surface, box 0.16 wide.', None),
        ('J13-zoom-rab-0.02.png', 'The same, box 0.04 wide.', None),
        ('off-rab-off-E-front.png', 'First layout, c = (-0.12, 0.74, 0.12): the rabbit lifted off the plane. The bodies have grown together (98 % in one piece).', None),
        ('off-rab-off-J13-front.png', 'Joukowski 1.3, the same c.', None),
        ('off-p3-off-front.png', 'Power 3, first layout, c = (0.1, 0.95, 0.15): empty, no point stays (this c is outside the power 3 solid).', None),
        ('E-c3-front.png', 'First layout, c = (-1, 0.15, 0.1).', None)]),
    ('Power 3 with the Joukowski layout', [
        ('J3-julia-front.png', 'Julia set c = i.', None), ('J3-zoom-0.32.png', 'Surface, box 0.64 wide: longer knobs than with the first layout.', None), ('J3-zoom-0.08.png', 'Box 0.16 wide.', None),
        ('J3-zoom-0.02.png', 'Box 0.04 wide.', None), ('J3-mandel-front.png', 'Mandelbrot solid: a cushion again.', None), ('q6-J3-mandel-y0.png', 'Its upright cut at y = 0.', None)]),
]
notes = ['Numbers for these layouts: out/r15/study/q4-numbers.log (shape stretch), q4-vols.log, q4b.log, q6b.log, q7.log.']
M.build(rows, notes, os.path.join(HERE, 'sheet-layouts.png'), 'Square pillow rule: layouts compared (study, round 15)')

"""The three sentences the shader engineer of round 11 asked for in the closing text (notes/_r11_engine_report.json).
python out/me/v13/closing_r11.py <body.html> [<body.html> ...]   (safe to run again)"""
import io, sys
PAIRS = [
    ("“Orbit steps the trap reads” starts at 4.</p>",
     "“Orbit steps the trap reads” starts at 4. At 4 a place keeps its colour while you zoom in. A higher number gives finer patterns but repaints whole areas as you zoom in.</p>"),
    ("a few balls still come out cut open, with a flat face, and a note beside the choice says so. That part is not cured.",
     "a few balls still come out cut open, with a flat face, and a note beside the choice says so. That part is not cured. With the trap centre off y = 0 some pieces grow so large that they fill the picture or close round the camera, and a note beside the choice says that too."),
    ("A Glow width of 2 or 3 brings more colour, and so does a Trap radius of 0.7 in the Mandelbrot picture.</p>",
     "A Glow width of 2 or 3 brings more colour, and so does a Trap radius of 0.7 in the Mandelbrot picture. A last trace of the slices, fine lines in shadowed folds with the distance estimate at Exact, came from the shadow and is gone as well.</p>"),
]
for p in sys.argv[1:]:
    t = io.open(p, encoding='utf-8', newline='').read()
    for old, new in PAIRS:
        if new in t: continue
        assert t.count(old) == 1, (p, old[:40], t.count(old))
        t = t.replace(old, new)
    io.open(p, 'w', encoding='utf-8', newline='').write(t)
    print('ok', p)

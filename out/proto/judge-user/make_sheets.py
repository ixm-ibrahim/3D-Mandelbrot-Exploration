"""Judge (user lens): contact sheets, one HTML page per picture kind, six pictures side by side.

  python out/proto/judge-user/make_sheets.py   -> sheets/<kind>.html and sheets/<kind>.png
"""
import os, subprocess, sys
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
SHEETS = os.path.join(HERE, "sheets")
os.makedirs(SHEETS, exist_ok=True)

COLS = [
    ("PILLOW radial (rays from the triangle's centre)", "../../radial/"),
    ("PILLOW sine (barycentric sines)", "../../sine/"),
    ("PILLOW twoplane (rays from the altitude's midpoint)", "../../twoplane/"),
    ("BASELINE inflated (Sphere inversions, planes = 1)", "../base-inflated/"),
    ("BASELINE folded (Sphere inversions, planes = 2, today's default)", "../base-folded/"),
    ("BASELINE bulb (power 2)", "../base-bulb/"),
]
KINDS = [
    ("m3d-default", "Mandelbrot solid, default camera"),
    ("m3d-top", "Mandelbrot solid, straight down the z axis"),
    ("m3d-x", "Mandelbrot solid, along the x axis"),
    ("m3d-y", "Mandelbrot solid, along the y axis (extra)"),
    ("m3d-cut0", "Mandelbrot solid, cut open at z = 0"),
    ("m3d-cut02", "Mandelbrot solid, cut open at z = 0.2"),
    ("m2d-z000", "Mandelbrot, flat slice at z = 0 (must be the ordinary Mandelbrot set)"),
    ("m2d-z010", "Mandelbrot, flat slice at z = 0.1"),
    ("m2d-z025", "Mandelbrot, flat slice at z = 0.25"),
    ("m2d-z050", "Mandelbrot, flat slice at z = 0.5"),
    ("j-bas-3d", "Julia c = -1 (basilica), default camera: compare with Kucera Figure 4"),
    ("j-bas-top", "Julia c = -1 (basilica), straight down the z axis"),
    ("j-bas-x", "Julia c = -1 (basilica), along the x axis (extra)"),
    ("j-bas-2d-z000", "Julia c = -1, flat slice at z = 0 (must be the ordinary basilica)"),
    ("j-bas-2d-z020", "Julia c = -1, flat slice at z = 0.2"),
    ("j-rab-3d", "Julia c = -0.1226 + 0.7449i (Douady rabbit), default camera"),
]
CSS = ("body{margin:0;background:#0b0e13;color:#e8e2d2;font:15px system-ui,sans-serif}"
       "#sheet{width:1980px;padding:10px 10px 14px;box-sizing:border-box}"
       "h1{font-size:19px;margin:0 0 8px;font-weight:600}"
       ".g{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}"
       ".c{background:#141922;border:1px solid #2a3240}"
       ".c b{display:block;padding:5px 8px;font-size:14px}"
       ".c.p b{color:#ffd27a}.c.b b{color:#8fd0ff}"
       ".c img{display:block;width:100%;height:auto}")

for kind, title in KINDS:
    cells = ""
    for label, rel in COLS:
        cls = "p" if label.startswith("PILLOW") else "b"
        cells += '<div class="c %s"><b>%s</b><img src="%s%s.png" alt=""></div>' % (cls, label, rel, kind)
    html = ('<!doctype html><html><head><meta charset="utf-8"><title>%s</title><style>%s</style></head><body>'
            '<div id="sheet"><h1>%s: %s</h1><div class="g">%s</div></div></body></html>') % (kind, CSS, kind, title, cells)
    with open(os.path.join(SHEETS, kind + ".html"), "w", encoding="utf-8") as f:
        f.write(html)


def shoot(kind):
    page = os.path.join(SHEETS, kind + ".html")
    out = "out/proto/judge-user/sheets/%s.png" % kind
    r = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "shot.py"), "--url", page, "--size", "2000x1200",
                        "--wait", "[...document.images].every(i => i.complete) && document.images.length === 6", "--timeout", "120",
                        "--js", "return [...document.images].map(i => i.naturalWidth + 'x' + i.naturalHeight).join(' ')",
                        "--shot", out, "--clip", "#sheet"], cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace")
    return kind + ": " + " / ".join(l for l in (r.stdout + r.stderr).strip().splitlines())


with ThreadPoolExecutor(4) as ex:
    for line in ex.map(shoot, [k for k, _ in KINDS]):
        print(line)

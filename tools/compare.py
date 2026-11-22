"""Check that a change to the code did not change the pictures.

  python tools/compare.py capture before      draw a fixed set of views into compare/before/
  (change the code, run build.py)
  python tools/compare.py capture after
  python tools/compare.py diff before after   list the views and numbers that differ

The page draws the same picture every time, so two captures of the same code are equal byte for byte. Any
difference is a real change. That includes a shader edit in code the view never runs: the graphics compiler may
round the rest differently. Captures are kept under compare/, which git ignores.
"""
import json, os, sys

from shot import ROOT, open_page, report, utf8_output

PAGE = os.path.join(ROOT, "squaring-lab.html")
HOME = os.path.join(ROOT, "compare")
# Only the picture is compared: the controls drawn over it move with the layout of the page.
BARE = ("const st = document.createElement('style'); "
        "st.textContent = '.cam-mode, .cam-zoom, .cam-note, .stage-bar, .draw-progress, #triad { display: none !important; }'; "
        "document.head.appendChild(st);")
SETUP = ("const L = window.squaringLab, S = L.S, $ = id => document.getElementById(id); "
         "const draw = () => { S.q.res = 0.5; S.q.aa = 2; L.syncControls(); L.refresh(); }; ")
BASILICA = "const P = L.JULIA_PRESETS.find(p => p.name === 'Basilica'); S.c = P.c.slice(0, 3); L.frameJuliaPreset(P); "
# Each rule's arithmetic at one point, for three powers.
NUMBERS = SETUP + """
  const out = {}, v = [0.31, -0.42, 0.53], c = [-0.12, 0.74, 0.1];
  for (const a of L.APPROACHES) out[a.id] = [2, 3, -2].map(n => L.MATH[a.id](v, n, S.param[a.id], c));
  return out;"""


def views(ids):
    for i, name in enumerate(ids):
        yield "julia-" + name, "$('mode-j').click(); S.approach = %d; S.n = 2; %s draw();" % (i, BASILICA)
    for i, name in enumerate(ids):
        yield "mandelbrot-" + name, "$('mode-m').click(); S.approach = %d; S.n = 2; draw();" % i
    yield "flat", "S.approach = 0; S.flat = true; draw();"
    yield "kleinian", "S.flat = false; $('mode-k').click(); S.k.group = 0; draw();"
    yield "balls-on-balls", "S.k.group = 1; draw();"


def capture(name):
    out = os.path.join(HOME, name)
    os.makedirs(out, exist_ok=True)
    with open_page(PAGE, (1100, 900)) as page:
        page.wait("done", 180)
        page.js(BARE)
        ids = page.js("return window.squaringLab.APPROACHES.map(a => a.id);")
        for view, js in views(ids):
            page.js(SETUP + js)
            if not page.wait("done", 300):
                sys.exit("never finished: " + view)
            page.shot(os.path.join(out, view + ".png"), "#view")
        with open(os.path.join(out, "numbers.json"), "w", encoding="utf-8") as f:
            json.dump(page.js(NUMBERS), f, indent=1)
        code = report(page)
    print("%d views in compare/%s" % (2 * len(ids) + 3, name))
    sys.exit(code)


def diff(a, b):
    A, B = os.path.join(HOME, a), os.path.join(HOME, b)
    changed = []
    for f in sorted(os.listdir(A)):
        if not os.path.exists(os.path.join(B, f)):
            changed.append(f + " (missing)")
            continue
        with open(os.path.join(A, f), "rb") as x, open(os.path.join(B, f), "rb") as y:
            if x.read() != y.read():
                changed.append(f)
    print("\n".join(changed) if changed else "no differences")
    sys.exit(1 if changed else 0)


def main():
    utf8_output()
    args = sys.argv[1:]
    if len(args) == 2 and args[0] == "capture":
        capture(args[1])
    elif len(args) == 3 and args[0] == "diff":
        diff(args[1], args[2])
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()

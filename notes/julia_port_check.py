"""Two checks on the numpy port in notes/julia_scan.py.

  python notes/julia_port_check.py

1. Parity with the lab: the text of foldk and MATH (base/js/10-approaches.js) is run in headless Chrome on
   random points, and MATH.mercator(v, 2, {planes}) is compared with the port's msq(foldk(v, planes)).
2. Symmetries of the constant with two planes, on a grid of start points:
   a constant with only a z part gives the same solid as the same number on -y; changing the sign of c.y
   or c.z mirrors the solid; swapping the y and z parts changes nothing.
"""
import json, os, random, subprocess, sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import julia_scan as js

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def parity():
    with open(os.path.join(ROOT, "base", "js", "10-approaches.js"), encoding="utf-8") as f:
        src = f.read()
    src = src[src.index("function foldk"):src.index("const GL_MERCATOR")]
    random.seed(11)
    pts = [[random.uniform(-2, 2) for _ in range(3)] for _ in range(400)]
    pts += [[1, 0, 0], [0, 1, 0], [0, 0, 1], [0.5, 0.3, 0.3], [0.5, -0.3, 0.3], [-1, 1e-9, 1], [0.2, 0, -0.7]]
    code = ("const PI = Math.PI, clamp = (x, a, b) => Math.max(a, Math.min(b, x));\n" + src +
            "\nconst pts = %s; return JSON.stringify([1, 2].map(k => pts.map(v => MATH.mercator(v, 2, { planes: k }))));" % json.dumps(pts))
    steps = os.path.join(ROOT, "out", "julia-presets", "port-steps.json")
    os.makedirs(os.path.dirname(steps), exist_ok=True)
    with open(steps, "w", encoding="utf-8") as f:
        json.dump([{"js": code}], f)
    r = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "shot.py"), "--url", "dist/julia-presets.html", "--actions", steps],
                       cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace")
    os.remove(steps)
    line = next(ln for ln in r.stdout.splitlines() if ln.startswith("step 1 result:"))
    lab = np.array(json.loads(json.loads(line.split(":", 1)[1])))          # [planes][point][xyz]
    v = tuple(np.array(pts).T)
    worst = 0.0
    for i, k in enumerate((1, 2)):
        mine = np.array(js.msq(js.foldk(v, k))).T
        worst = max(worst, float(np.abs(mine - lab[i]).max()))
        print("  planes %d: largest difference between the lab's MATH.mercator and the port on %d points: %.2e" % (k, len(pts), float(np.abs(mine - lab[i]).max())))
    return worst < 1e-5 and "no console errors" in r.stdout


def symmetry():
    F = lambda c: js.filled(c, 2, n=72)[0]
    a = F((-0.4, 0.13, 0.075))
    tests = [("only a z part equals the same number on -y", F((-0.8, 0, 0.156)), F((-0.8, -0.156, 0))),
             ("sign of c.y flipped is the mirror image in y", a, F((-0.4, -0.13, 0.075))[:, ::-1, :]),
             ("sign of c.z flipped is the mirror image in z", a, F((-0.4, 0.13, -0.075))[:, :, ::-1]),
             ("y and z parts swapped is the same solid", a, F((-0.4, 0.075, 0.13)))]
    ok = True
    for name, p, q in tests:
        d = int((p != q).sum())
        ok &= d == 0
        print("  %s: %d of %d cells differ" % (name, d, p.size))
    return ok


def main():
    print("parity with the lab's own code")
    a = parity()
    print("symmetries with two planes")
    b = symmetry()
    print("RESULT:", "pass" if a and b else "FAIL")
    sys.exit(0 if a and b else 1)


if __name__ == "__main__":
    main()

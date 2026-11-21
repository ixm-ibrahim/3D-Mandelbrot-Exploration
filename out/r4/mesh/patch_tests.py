"""One-off: make the private shader stand-in (base3's shaders plus the raw output of CONTRACT4) and teach
run_tests.py the 'real' run with stand-ins and mesh pictures. Kept for the record of how the stand-ins were made."""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))

s = open(os.path.join(ROOT, "base3/js/30-shaders.js"), encoding="utf-8").read()
a = "uniform float uBound, uMosaic, uFlat, uFlatH, uSliceZ;"
assert s.count(a) == 1
s = s.replace(a, a + "\nuniform float uRaw;")
b = "  if (phase == END_FLAT){\n"
assert s.count(b) == 1
s = s.replace(b, b + "    if (uRaw > 0.5){ colourCapture(); o = vec4(surfaceColour(slicePoint, dot(gGrad, gGrad) > 0.0 ? normalize(gGrad) : vec3(0.0, 0.0, 1.0), 0.0), d); return; }\n")
s = "// TEST STAND-IN (out/r4/mesh): base3's shaders plus the raw output of CONTRACT4, until the real one arrives.\n" + s
open(os.path.join(HERE, "30-shaders.js"), "w", encoding="utf-8", newline="\n").write(s)

p = os.path.join(HERE, "run_tests.py")
t = open(p, encoding="utf-8").read()
if "NAME =" not in t:
    t = t.replace('MINE = ["src/js/00-core.js", "src/js/46-mesh.js", "src/css/46-mesh.css"]',
                  'MINE = ["src/js/00-core.js", "src/js/46-mesh.js", "src/css/46-mesh.css"]\nNAME = "r4-mesh-real" if "real" in sys.argv[1:2] else "r4-mesh"')
    t = t.replace('    cmd = [sys.executable, "build.py", "--name", "r4-mesh", "--base", base, "--use"] + MINE + extra + ["--swap", "js/90-boot.js=out/r4/mesh/90-boot.js"]',
                  '    swaps = ["js/90-boot.js=out/r4/mesh/90-boot.js"] + [a for a in sys.argv if a.startswith("js/") and "=" in a]\n'
                  '    cmd = [sys.executable, "build.py", "--name", NAME, "--base", base, "--use"] + MINE + [e for e in extra if "=" not in e] + ["--swap"] + swaps')
    t = t.replace('"--url", "dist/r4-mesh.html"', '"--url", "dist/%s.html" % NAME')
    t = t.replace('        return {"js": f.read() + "\\nreturn \'helpers loaded\';"}',
                  '        code = f.read()\n    with open(os.path.join(HERE, "draw.js"), encoding="utf-8") as f:\n        return {"js": code + f.read() + "\\nreturn \'helpers loaded\';"}')
    save = '        {"js": "return await meshT.save();"},\n'
    draw = lambda name: '        {"js": "return meshT.draw(window.squaringLabMeshTest.mesh, 0.5, 0.45);", "shot": "out/r4/mesh/real-%s-mesh.png", "clip": "#meshView"},\n' % name
    head, tail = t.split("def real():", 1)
    parts = tail.split(save)
    assert len(parts) == 4, len(parts)
    tail = parts[0] + save + draw("julia") + parts[1] + save + draw("mandel") + parts[2] + save + draw("klein") + parts[3]
    tail = tail.replace('{"js": pre + "document.getElementById(\'mode-m\')', '{"js": "document.getElementById(\'meshView\').remove(); " + pre + "document.getElementById(\'mode-m\')')
    tail = tail.replace('{"js": pre + "document.getElementById(\'mode-k\')', '{"js": "document.getElementById(\'meshView\').remove(); " + pre + "document.getElementById(\'mode-k\')')
    tail = tail.replace('((3, "Julia set, c = -1, 128 cells", "julia"), (6, "Mandelbrot, default, 128 cells", "mandel"), (9, "Kleinian, default, 128 cells", "klein"))',
                        '((3, "Julia set, c = -1, 128 cells", "julia"), (7, "Mandelbrot, default, 128 cells", "mandel"), (11, "Kleinian, default, 128 cells", "klein"))')
    t = head + "def real():" + tail
    open(p, "w", encoding="utf-8", newline="\n").write(t)
print("patched")

"""Engineer "dial", fix pass 7: notes/dial_real.py with its two stale selectors corrected, without editing that file.

  python out/r7/dial/dial_real_r7.py --lab=dist/r7-dial.html

notes/dial_real.py was written for the baseline page, where Power n was the first dial in #eqDials. Since then the
page keeps Power n in its own host (#powHost), so "#eqDials .dial .dial-up" is the up button of Iterations and the
two lines that step Power n fail on every build, Version 6 included. Here the selector is "#powHost .dial .dial-up".
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
path = os.path.join(ROOT, "notes", "dial_real.py")
with open(path, encoding="utf-8") as f:
    src = f.read()
assert src.count('"#eqDials .dial .dial-up"') == 2
src = src.replace('"#eqDials .dial .dial-up"', '"#powHost .dial .dial-up"')
g = {"__name__": "__main__", "__file__": path}
exec(compile(src, path, "exec"), g)

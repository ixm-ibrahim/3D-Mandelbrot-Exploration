"""Make out/r4/maths/75-presets.js: the page's presets file (src/js/75-presets.js as it is now) with the Julia
block replaced by data/julia-presets.json, the way notes/ui_embed.py would write it. A private stand-in for
testing only; the real file belongs to the page engineer.

  python out/r4/maths/embed_private.py
  python build.py --name r4-maths-data --base base4 --use <my files> --swap js/75-presets.js=out/r4/maths/75-presets.js
"""
import json, os, re
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
with open(os.path.join(ROOT, "src", "js", "75-presets.js"), encoding="utf-8") as f:
    src = f.read()
with open(os.path.join(ROOT, "data", "julia-presets.json"), encoding="utf-8") as f:
    items = json.load(f)
rows = ",\n".join("  " + json.dumps(it, ensure_ascii=False) for it in items)
block = "// <julia-data>\nconst JULIA_PRESETS = [\n%s,\n];\n// </julia-data>" % rows
pat = re.compile(r"// <julia-data>.*?// </julia-data>", re.S)
assert pat.search(src), "marker not found"
with open(os.path.join(ROOT, "out", "r4", "maths", "75-presets.js"), "w", encoding="utf-8", newline="\n") as f:
    f.write(pat.sub(lambda m: block, src))
print("out/r4/maths/75-presets.js written with %d Julia entries" % len(items))

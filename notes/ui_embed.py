"""Copy data/julia-presets.json and data/klein-presets.json into src/js/75-presets.js, between its marker lines.

  python notes/ui_embed.py

The build does not load JSON, so the page carries the two lists as JavaScript constants. JSON is valid
JavaScript, so each entry is written as it stands, one per line.
"""
import json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TARGET = os.path.join(ROOT, "src", "js", "75-presets.js")


def block(tag, const, path):
    with open(os.path.join(ROOT, path), encoding="utf-8") as f:
        items = json.load(f)
    rows = ",\n".join("  " + json.dumps(it, ensure_ascii=False) for it in items)
    return "// <%s>\nconst %s = [\n%s,\n];\n// </%s>" % (tag, const, rows, tag), len(items)


def main():
    with open(TARGET, encoding="utf-8") as f:
        src = f.read()
    for tag, const, path in (("julia-data", "JULIA_PRESETS", "data/julia-presets.json"),
                             ("klein-data", "KLEIN_PRESETS", "data/klein-presets.json")):
        text, n = block(tag, const, path)
        pat = re.compile(r"// <%s>.*?// </%s>" % (tag, tag), re.S)
        if not pat.search(src):
            raise SystemExit("marker <%s> not found in 75-presets.js" % tag)
        src = pat.sub(lambda m: text, src)
        print("%s: %d entries" % (const, n))
    with open(TARGET, "w", encoding="utf-8", newline="\n") as f:
        f.write(src)


if __name__ == "__main__":
    main()

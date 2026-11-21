"""Assemble the lab from src/ into one page.

  python build.py                      -> squaring-lab.html (the published page) and dist/preview.html (same, wrapped for local viewing)
  python build.py --name mine --base base --use src/js/70-dial.js src/css/70-dial.css
                                       -> dist/mine.html only, built from the frozen copy in base/ with the listed live files swapped in.
                                          Use this to test one module against the known-good baseline while other modules are mid-edit.

Sources, in order: src/head.html, every src/css/*.css (sorted), src/body.html, every src/js/*.js (sorted).
All JavaScript files are concatenated inside ONE function scope, in file-name order, so a top-level name
declared in one file is visible in the others. Only 90-boot.js may run code at load time.
"""
import argparse, glob, os, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
WRAP_HEAD = ('<!doctype html><html><head><meta charset="utf-8">'
             '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">'
             '<style>body{margin:0;font:14px system-ui,sans-serif}img{max-width:100%}[hidden]{display:none!important}</style>'
             '</head><body>')


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read().replace("\r\n", "\n")


def assemble(base, live_root, use, swap=()):
    """base: directory holding head.html, css/, body.html, js/. Files named in `use` (paths relative to live_root's
    parent, e.g. src/js/70-dial.js) replace or add to the base copy. `swap` entries look like js/40-render.js=some/file.js
    and substitute any file at all for that slot (for throwaway test copies kept outside src/)."""
    over = {}
    for u in use:
        rel = os.path.relpath(os.path.join(ROOT, u), live_root).replace("\\", "/")
        over[rel] = os.path.join(ROOT, u)
    for s in swap:
        slot, path = s.split("=", 1)
        slot = slot.replace("\\", "/")
        over[slot[4:] if slot.startswith("src/") else slot] = os.path.join(ROOT, path)

    def listing(sub, ext):
        names = {os.path.basename(p) for p in glob.glob(os.path.join(base, sub, "*" + ext))}
        names |= {os.path.basename(rel) for rel in over if rel.startswith(sub + "/") and rel.endswith(ext)}
        return sorted(names)

    def get(rel):
        return read(over[rel]) if rel in over else read(os.path.join(base, rel))

    parts = [get("head.html").rstrip("\n"), "<style>"]
    for n in listing("css", ".css"):
        parts.append("/* ==== %s ==== */\n" % n + get("css/" + n).rstrip("\n"))
    parts += ["</style>", "", get("body.html").rstrip("\n"), "", "<script>", "(() => {", "'use strict';"]
    for n in listing("js", ".js"):
        parts.append("\n// ==================== %s ====================\n" % n + get("js/" + n).rstrip("\n"))
    parts += ["})();", "</script>", ""]
    return "\n".join(parts)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--name", help="write dist/<name>.html only (a wrapped test page), leaving the published page alone")
    ap.add_argument("--base", default="src", help="directory to build from (default src; use base for the frozen baseline)")
    ap.add_argument("--use", nargs="*", default=[], help="live files to swap into the base, e.g. src/js/70-dial.js")
    ap.add_argument("--swap", nargs="*", default=[], help="slot=file pairs, e.g. js/40-render.js=out/me/render-test.js: put any file in a slot (test copies)")
    ap.add_argument("--page", action="store_true", help="orchestrator only: write the published page from the chosen --base (a frozen copy), not from src")
    a = ap.parse_args()
    page = assemble(os.path.join(ROOT, a.base), os.path.join(ROOT, "src"), a.use, a.swap)
    os.makedirs(os.path.join(ROOT, "dist"), exist_ok=True)
    if a.name:
        out = os.path.join(ROOT, "dist", a.name + ".html")
        with open(out, "w", encoding="utf-8", newline="\n") as f:
            f.write(WRAP_HEAD + page + "</body></html>")
        print("wrote dist/%s.html (%d bytes)" % (a.name, len(page)))
        return
    if (a.base != "src" or a.use or a.swap) and not a.page:
        sys.exit("--base, --use and --swap need --name, so the published page is never built from a partial mix.")
    with open(os.path.join(ROOT, "squaring-lab.html"), "w", encoding="utf-8", newline="\n") as f:
        f.write(page)
    with open(os.path.join(ROOT, "dist", "preview.html"), "w", encoding="utf-8", newline="\n") as f:
        f.write(WRAP_HEAD + page + "</body></html>")
    print("wrote squaring-lab.html and dist/preview.html (%d bytes)" % len(page))


if __name__ == "__main__":
    main()

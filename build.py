"""Join src/ into one page.

  python build.py    writes squaring-lab.html (the published page) and dist/preview.html (the same page
                     inside a complete document, for opening from disk)

Order: src/head.html, src/css/*.css, src/body.html, src/js/*.js, each folder sorted by file name.
The JavaScript files share one function scope, so a top-level name in one file is visible in the
others. Only 90-boot.js runs code when the page loads.
"""
import glob, os

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, "src")
PREVIEW_HEAD = ('<!doctype html><html><head><meta charset="utf-8">'
                '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">'
                '<style>body{margin:0;font:14px system-ui,sans-serif}img{max-width:100%}[hidden]{display:none!important}</style>'
                '</head><body>')


def read(*parts):
    with open(os.path.join(SRC, *parts), encoding="utf-8") as f:
        return f.read().replace("\r\n", "\n").rstrip("\n")


def names(folder, ext):
    return sorted(os.path.basename(p) for p in glob.glob(os.path.join(SRC, folder, "*" + ext)))


def assemble():
    parts = [read("head.html"), "<style>"]
    parts += ["/* ==== %s ==== */\n%s" % (n, read("css", n)) for n in names("css", ".css")]
    parts += ["</style>", "", read("body.html"), "", "<script>", "(() => {", "'use strict';"]
    parts += ["\n// ==================== %s ====================\n%s" % (n, read("js", n)) for n in names("js", ".js")]
    parts += ["})();", "</script>", ""]
    return "\n".join(parts)


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def main():
    page = assemble()
    write(os.path.join(ROOT, "squaring-lab.html"), page)
    write(os.path.join(ROOT, "dist", "preview.html"), PREVIEW_HEAD + page + "</body></html>")
    print("wrote squaring-lab.html and dist/preview.html (%d bytes)" % len(page.encode("utf-8")))


if __name__ == "__main__":
    main()

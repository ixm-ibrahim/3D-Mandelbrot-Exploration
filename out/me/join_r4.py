"""Round 4 join, step 1: paste the Kleinian engineer's GL_KLEIN into src/js/30-shaders.js.

Run from the project root: python out/me/join_r4.py
"""
import io, os, shutil, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
live = os.path.join(ROOT, "src", "js", "30-shaders.js")
new = os.path.join(ROOT, "out", "r4", "kleinian", "GL_KLEIN.js")
keep = os.path.join(ROOT, "out", "me", "30-shaders.before-klein.js")

s = io.open(live, encoding="utf-8").read().replace("\r\n", "\n")
k = io.open(new, encoding="utf-8").read().replace("\r\n", "\n").strip()
assert k.startswith("const GL_KLEIN = `") and k.endswith("`;"), "the delivered constant has an unexpected shape"

a = s.index("const GL_KLEIN = `")
b = s.index("const GL_TAIL = `")
old = s[a:b]
end = old.rindex("`;") + 2          # the closing of the old statement; what follows is blank lines and comments
tail = old[end:]
if old[:end].strip() == k:
    print("already pasted; nothing to do")
    sys.exit(0)
if not os.path.exists(keep):
    shutil.copyfile(live, keep)
out = s[:a] + k + tail + s[b:]
io.open(live, "w", encoding="utf-8", newline="\n").write(out)
print("pasted GL_KLEIN: %d -> %d bytes of that statement; between it and GL_TAIL: %r" % (end, len(k), tail[:120]))

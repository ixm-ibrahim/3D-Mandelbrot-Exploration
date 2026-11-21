"""One-off edits to src/js/66-learn-view.js (the view engineer's own file): exact-text replacements, each must match once."""
import io, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
path = os.path.join(ROOT, "src", "js", "66-learn-view.js")
with io.open(path, encoding="utf-8") as f:
    text = f.read()
edits = [
 ("  cv.addEventListener('wheel', e => { if (!L.on) return; e.preventDefault(); zoomBy(Math.exp(-e.deltaY * 0.0015)); learnVNow(); }, { passive: false });",
  "  // The stage has a wheel listener of the camera's (50-camera.js), which would zoom the solid behind this picture.\n"
  "  // While Learn is on the wheel is taken here, on the stage and in the capture phase, before that one hears it.\n"
  "  stage.addEventListener('wheel', e => {\n"
  "    if (!L.on) return;\n"
  "    e.preventDefault(); e.stopImmediatePropagation();\n"
  "    zoomBy(Math.exp(-e.deltaY * (e.deltaMode === 1 ? 0.05 : 0.0015))); learnVNow();\n"
  "  }, { capture: true, passive: false });"),
]
bad = 0
for old, new in edits:
    n = text.count(old)
    if n != 1:
        print("MATCHES", n, ":", old[:90]); bad += 1; continue
    text = text.replace(old, new)
if bad:
    sys.exit("nothing written")
with io.open(path, "w", encoding="utf-8", newline="\n") as f:
    f.write(text)
print("ok", len(edits))

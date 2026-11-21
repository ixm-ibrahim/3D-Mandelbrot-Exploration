"""The three hooks the Learn tab and the pinned picture need in existing files.

python out/me/r13/hooks.py <dir>    patches <dir>/js/90-boot.js, <dir>/js/40-render.js and <dir>/js/80-ui.js
                                    in place. Safe to run again: a hook that is there already is left alone.
Everything else of round 13 lives in new files (65-learn-steps.js, 66-learn-view.js, 65-learn.css, 85-pin.js, 85-pin.css).
"""
import io, os, sys
d = sys.argv[1]

def patch(rel, old, new):
    p = os.path.join(d, rel)
    t = io.open(p, encoding='utf-8', newline='').read()
    if new in t:
        print('already in', rel); return
    assert t.count(old) == 1, (rel, old[:50], t.count(old))
    io.open(p, 'w', encoding='utf-8', newline='').write(t.replace(old, new))
    print('patched', rel)

patch('js/90-boot.js', "boot();",
      "boot();\n"
      "// Modules that start after the page is up, each only when it is part of the page.\n"
      "if (typeof learnInit === 'function') learnInit();\n"
      "if (typeof pinInit === 'function') pinInit();\n"
      "window.squaringLab.learn = typeof LEARN !== 'undefined' ? LEARN : null;\n"
      "window.squaringLab.learnPlan = typeof learnPlan === 'function' ? learnPlan : null;")
patch('js/40-render.js', "function touch() { R.wantPrev = true;",
      "function touch() {\n"
      "  // While the Learn tab is on show it draws its own picture on the stage: the solid is not drawn again until\n"
      "  // the tab is left (the Learn module then clears S.learn and calls touch()).\n"
      "  if (S.learn) { if (typeof learnTouch === 'function') learnTouch(); return; }\n"
      "  R.wantPrev = true;")
# asked for by the view engineer: a reset called from code also leaves the Learn tab
patch('js/80-ui.js', "function uiResetAll() {",
      "function uiResetAll() {\n  if (typeof learnReset === 'function') learnReset();")

import io, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
path = os.path.join(ROOT, 'src', 'js', '90-boot.js')
src = io.open(path, encoding='utf-8').read()
old1 = "showTwin: uiTwin, twinOff: uiTwinOff, juliaFoundDiff, applyJuliaFound,\n"
new1 = ("showTwin: uiTwin, twinOff: uiTwinOff, juliaFoundDiff, applyJuliaFound,\n"
        "  showQuaternionSquare: () => uiQuat('lathe'), showTwistedSquare: () => uiQuat('tilt'), juliaFoundWords,\n")
old2 = "// What this round's other modules add, each only when that module is part of the page.\n"
new2 = old2 + "if (typeof APPROACH_GROUPS !== 'undefined') window.squaringLab.APPROACH_GROUPS = APPROACH_GROUPS;\n"
for old, new in ((old1, new1), (old2, new2)):
    if src.count(old) != 1:
        sys.exit('no single match for: ' + old)
    src = src.replace(old, new)
io.open(path, 'w', encoding='utf-8', newline='\n').write(src)
print('90-boot.js edited')

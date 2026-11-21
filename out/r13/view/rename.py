"""One-off: give the view's private names their own prefix (learnV / LEARN_V_), so they cannot meet the names
of 65-learn-steps.js in the shared scope. Element ids inside strings are left alone."""
import re, io, os
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
path = os.path.join(ROOT, "src", "js", "66-learn-view.js")
names = {
    "LEARN_START": "LEARN_V_START", "LEARN_VIEWS": "LEARN_V_VIEWS", "LEARN_SECONDS": "LEARN_V_SECONDS",
    "LEARN_FITS": "LEARN_V_FITS", "LEARN_NOTICE": "LEARN_V_NOTICE", "LEARN_HIDDEN_TEXT": "LEARN_V_HIDDEN",
    "learnCopy": "learnVCopy", "learnFinite": "learnVFinite", "learnNum": "learnVNum", "learnDeg": "learnVDeg",
    "learnXyz": "learnVXyz", "learnViewKey": "learnVKey", "learnIsCam": "learnVIsCam", "learnBuild": "learnVBuild",
    "learnAt": "learnVAt", "learnPoint": "learnVPoint", "learnTheme": "learnVTheme", "learnProj": "learnVProj",
    "learnDraw": "learnVDraw", "learnPaint": "learnVPaint", "learnQueue": "learnVQueue", "learnFrame": "learnVFrame",
    "learnNow": "learnVNow", "learnChanged": "learnVChanged", "learnStop": "learnVStop", "learnPlay": "learnVPlay",
    "learnPlayMove": "learnVPlayMove", "learnGoto": "learnVGoto", "learnNextStep": "learnVNextStep",
    "learnAgain": "learnVAgain", "learnShowStage": "learnVShowStage", "learnDefaults": "learnVDefaults",
    "learnSetOn": "learnVSetOn", "learnRefresh": "learnVRefresh", "learnBindCanvas": "learnVBind",
}
with io.open(path, encoding="utf-8") as f:
    text = f.read()
total = 0
for old, new in names.items():
    text, n = re.subn(r"(?<!['\"#\w])" + old + r"(?![\w'\"])", new, text)
    print(old, "->", new, n)
    total += n
with io.open(path, "w", encoding="utf-8", newline="\n") as f:
    f.write(text)
print("replaced", total)

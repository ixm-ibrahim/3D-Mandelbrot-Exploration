"""Make out/r10/dial/kit-extra.json from kit-extra.js, for:
  python tools/shot.py --url tests/dial.html --actions out/r10/dial/kit-extra.json
"""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(HERE, "kit-extra.js"), encoding="utf-8") as f:
    code = f.read()
steps = [
    {"wait": "window.dialTests && window.dialTests.done", "timeout": 60},
    {"js": code},
    {"js": "return 'kit page: ' + window.dialTests.passed + ' passed, ' + window.dialTests.failed + ' failed (its own 71 checks)';"},
]
with open(os.path.join(HERE, "kit-extra.json"), "w", encoding="utf-8") as f:
    json.dump(steps, f, indent=1, ensure_ascii=False)
print("wrote kit-extra.json")

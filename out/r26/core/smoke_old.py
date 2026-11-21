"""Round 26, core: the old smoke list of Version 18 (out/r22/entry/smoke-all-steps.json, 90 steps: the 62 of
tools/smoke-v14.json, round 20's 5, round 22's 20 + 3) run on a round 26 page. Follow = One point is the page's
starting state, so every step must pass as it did.

  python out/r26/core/smoke_old.py learn [page]   only the steps that touch the Learn tab (10, 74, 84 and 88 of the 90,
                                                  counted from 1), each with the little setup it needs -> smoke-old-learn.log
  python out/r26/core/smoke_old.py all [page]     all 90 steps -> smoke-old-all.log
page: core (default) | three | fake | base. Pictures the steps take go to out/r26/core/smoke/ (not to out/r22/).
"""
import json, os, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
PAGE = {"core": "r26-core", "three": "r26-core-three", "fake": "r26-core-fake", "base": "r26-base"}
PICK = "const $ = id => document.getElementById(id), sleep = ms => new Promise(r => setTimeout(r, ms));\n" \
       "$('mode-j').click(); await sleep(200); $('ap-%s').click(); await sleep(300);\n" \
       "const S = window.squaringLab.S; S.eq = 'z^n + c'; S.z0 = '0'; S.n = 2; window.squaringLab.syncControls(); window.squaringLab.refresh(false);\n" \
       "return 'chose %s in Julia mode';"


def main():
    part = sys.argv[1] if len(sys.argv) > 1 else "learn"
    page = sys.argv[2] if len(sys.argv) > 2 else "core"
    with open(os.path.join(ROOT, "out", "r22", "entry", "smoke-all-steps.json"), encoding="utf-8") as f:
        steps = json.load(f)
    for s in steps:
        if "shot" in s:
            s["shot"] = "out/r26/core/smoke/" + os.path.basename(s["shot"])
    if part == "learn":
        learn = [i for i, s in enumerate(steps) if "learn" in json.dumps(s).lower() or "mode-l" in json.dumps(s)]
        print("steps that touch Learn (counted from 1):", [i + 1 for i in learn])
        acts = [{"wait": "done", "timeout": 110}]
        for i in learn:
            js = steps[i].get("js", "")
            for entry in ("alongonce", "pulledplane"):
                if "apId() !== '%s'" % entry in js and "for (const id of" not in js:
                    acts.append({"js": PICK % (entry, entry), "wait": "done", "timeout": 300})
            acts.append(steps[i])
    else:
        acts = steps
    fd, tmp = tempfile.mkstemp(suffix=".json", prefix="r26smoke-")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump(acts, f)
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    try:
        r = subprocess.run([sys.executable, "-W", "ignore", os.path.join("tools", "shot.py"), "--url", "dist/%s.html" % PAGE[page], "--actions", tmp, "--size", "1400x950"],
                           cwd=ROOT, env=env, capture_output=True, text=True, encoding="utf-8", errors="replace")
    finally:
        os.remove(tmp)
    text = "old smoke list, part %s, on dist/%s.html: %d actions\n" % (part, PAGE[page], len(acts)) + r.stdout + r.stderr + "exit code %d\n" % r.returncode
    with open(os.path.join(HERE, "smoke-old-%s%s.log" % (part, "" if page == "core" else "-" + page)), "w", encoding="utf-8") as f:
        f.write(text)
    lines = text.splitlines()
    print("\n".join(l[:400] for l in lines if "wrote out" not in l))
    sys.exit(r.returncode)


if __name__ == "__main__":
    main()

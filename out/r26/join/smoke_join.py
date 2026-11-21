"""Round 26, the joiner: the old smoke list of Version 18 run on the joined page.

The list is out/r22/entry/smoke-all-steps.json: 90 steps (the 62 of tools/smoke-v14.json, round 20's 5, round 22's
20 + 3). It is the list whose run is logged in out/r22/entry/smoke-all.log and out/r22/me/smoke-v18.out
("PUBLISHED: Version 18" in notes/_state.md). Follow = One point is the page's opening state, so every step must
pass as it did then.

  python out/r26/join/smoke_join.py [page] [log]     page: r26-join (default); log: smoke-join (default)
-> out/r26/join/<log>.log, and a comparison with the old log, step by step, at its end.
Pictures the steps take go to out/r26/join/smoke/ (never to out/r22/).
"""
import json, os, re, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
OLD_LOG = os.path.join(ROOT, "out", "r22", "entry", "smoke-all.log")


def results(text):
    """step number -> the text of its result line; and the set of steps that timed out"""
    res, late = {}, set()
    for line in text.splitlines():
        m = re.match(r"step (\d+) result: (.*)$", line)
        if m:
            txt = m.group(2).strip()
            try:      # today's tools/shot.py prints a result as JSON, the one of Version 18 printed a string as it was
                val = json.loads(txt)
                if isinstance(val, str):
                    txt = val
            except ValueError:
                pass
            res[int(m.group(1))] = txt
        m = re.match(r"step (\d+) TIMED OUT", line)
        if m:
            late.add(int(m.group(1)))
    return res, late


def main():
    page = sys.argv[1] if len(sys.argv) > 1 else "r26-join"
    log = sys.argv[2] if len(sys.argv) > 2 else "smoke-join"
    with open(os.path.join(ROOT, "out", "r22", "entry", "smoke-all-steps.json"), encoding="utf-8") as f:
        steps = json.load(f)
    for s in steps:
        if "shot" in s:
            s["shot"] = "out/r26/join/smoke/" + os.path.basename(s["shot"])
    fd, tmp = tempfile.mkstemp(suffix=".json", prefix="r26joinsmoke-")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump(steps, f)
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    try:
        r = subprocess.run([sys.executable, "-W", "ignore", os.path.join("tools", "shot.py"), "--url", "dist/%s.html" % page, "--actions", tmp, "--size", "1400x950"],
                           cwd=ROOT, env=env, capture_output=True, text=True, encoding="utf-8", errors="replace")
    finally:
        os.remove(tmp)
    text = "old smoke list (%d steps) on dist/%s.html, 1400x950\n" % (len(steps), page) + r.stdout + r.stderr + "exit code %d\n" % r.returncode
    new, late = results(text)
    with open(OLD_LOG, encoding="utf-8") as f:
        old, old_late = results(f.read())
    passed_then = [i for i in range(1, len(steps) + 1) if i in old and i not in old_late]
    passed_now = [i for i in passed_then if i in new and i not in late]
    same = [i for i in passed_now if new[i] == old[i]]
    tail = ["", "COMPARISON with out/r22/entry/smoke-all.log (the run of Version 18):",
            "steps in the list: %d; passed then: %d; of those, pass now: %d" % (len(steps), len(passed_then), len(passed_now)),
            "time-outs now: %s" % (sorted(late) or "none"),
            "missing now (the run stopped before them, or they gave no result): %s" % ([i for i in passed_then if i not in new] or "none"),
            "result text word for word as then: %d of %d" % (len(same), len(passed_now))]
    for i in passed_now:
        if new[i] != old[i]:
            tail.append("  step %d differs in its text:\n    then: %s\n    now:  %s" % (i, old[i][:500], new[i][:500]))
    tail.append("console: %s" % ("no console errors" if "no console errors" in text else "SEE ABOVE (PAGE PROBLEMS or a failed step)"))
    text += "\n".join(tail) + "\n"
    with open(os.path.join(HERE, log + ".log"), "w", encoding="utf-8") as f:
        f.write(text)
    lines = text.splitlines()
    print("\n".join(l[:600] for l in lines if "wrote out" not in l and not re.match(r"step \d+ (result|waited)", l)))
    sys.exit(r.returncode)


if __name__ == "__main__":
    main()

"""Round 26, the final look: the old smoke list of Version 18 on dist/r26-final.html.

The list: out/r22/entry/smoke-all-steps.json (90 steps: the 62 of tools/smoke-v14.json, round 20's 5, round 22's
20 + 3), the one whose run is logged in out/r22/entry/smoke-all.log ("PUBLISHED: Version 18" in notes/_state.md).

  python out/r26/final/smoke_final.py [page] [log]      page: r26-final, log: smoke-final
-> out/r26/final/<log>.log with a step-by-step comparison against the old log at its end.
Pictures go to out/r26/final/smoke/ (nothing is written to out/r22/).
"""
import json, os, re, subprocess, sys, tempfile, time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
OLD_LOG = os.path.join(ROOT, "out", "r22", "entry", "smoke-all.log")
LIST = os.path.join(ROOT, "out", "r22", "entry", "smoke-all-steps.json")


def results(text):
    res, late = {}, set()
    for line in text.splitlines():
        m = re.match(r"step (\d+) result: (.*)$", line)
        if m:
            txt = m.group(2).strip()
            try:
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
    page = sys.argv[1] if len(sys.argv) > 1 else "r26-final"
    log = sys.argv[2] if len(sys.argv) > 2 else "smoke-final"
    with open(LIST, encoding="utf-8") as f:
        steps = json.load(f)
    for s in steps:
        if "shot" in s:
            s["shot"] = "out/r26/final/smoke/" + os.path.basename(s["shot"])
    fd, tmp = tempfile.mkstemp(suffix=".json", prefix="r26finalsmoke-")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump(steps, f)
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    t0 = time.time()
    try:
        r = subprocess.run([sys.executable, "-W", "ignore", os.path.join("tools", "shot.py"), "--url", "dist/%s.html" % page,
                            "--actions", tmp, "--size", "1400x950"],
                           cwd=ROOT, env=env, capture_output=True, text=True, encoding="utf-8", errors="replace")
    finally:
        os.remove(tmp)
    text = ("old smoke list (%d steps) on dist/%s.html, 1400x950, started %s, took %.0f s\n"
            % (len(steps), page, time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(t0)), time.time() - t0))
    text += r.stdout + r.stderr + "exit code %d\n" % r.returncode
    new, late = results(text)
    with open(OLD_LOG, encoding="utf-8") as f:
        old, old_late = results(f.read())
    n = len(steps)
    passed_then = [i for i in range(1, n + 1) if i in old and i not in old_late]
    gave_now = [i for i in range(1, n + 1) if i in new and i not in late]
    passed_now = [i for i in passed_then if i in gave_now]
    same = [i for i in passed_now if new[i] == old[i]]
    tail = ["", "COMPARISON with out/r22/entry/smoke-all.log (the run of Version 18):",
            "steps in the list: %d; gave a result then: %d; give a result now: %d; of those that passed then, pass now: %d"
            % (n, len(passed_then), len(gave_now), len(passed_now)),
            "time-outs now: %s" % (sorted(late) or "none"),
            "missing now: %s" % ([i for i in range(1, n + 1) if i not in new] or "none"),
            "result text word for word as then: %d of %d" % (len(same), len(passed_now))]
    for i in passed_now:
        if new[i] != old[i]:
            tail.append("  step %d differs in its text:\n    then: %s\n    now:  %s" % (i, old[i][:700], new[i][:700]))
    tail.append("console: %s" % ("no console errors" if "no console errors" in text else "SEE ABOVE (PAGE PROBLEMS or a failed step)"))
    text += "\n".join(tail) + "\n"
    with open(os.path.join(HERE, log + ".log"), "w", encoding="utf-8") as f:
        f.write(text)
    print("\n".join(l[:700] for l in text.splitlines() if "wrote out" not in l and not re.match(r"step \d+ (result|waited)", l)))
    sys.exit(r.returncode)


if __name__ == "__main__":
    main()

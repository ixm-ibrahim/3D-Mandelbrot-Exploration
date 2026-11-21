"""Turn the logs of the checks into the tables NOTES.md quotes.

  python out/r26/three/t3_tables.py            (reads slice-required.log, slice-wide.log, all21.log, timing-run.log, robust-run.log)
"""
import json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))


def result(name, step):
    path = os.path.join(HERE, name)
    if not os.path.exists(path):
        return None, "(no %s)" % name
    t = open(path, encoding="utf-8").read()
    m = re.search(r"step %d result: (.*)" % step, t)
    tail = t.strip().splitlines()[-1] if t.strip() else ""
    return (json.loads(m.group(1)) if m else None), tail


def slices(name, step):
    rows, tail = result(name, step)
    print("\n## %s   (last line of the log: %s)" % (name, tail))
    if rows is None:
        return
    tot = pts = 0
    worst = {}
    print("| approach | power | kind | c | z | dials / modifiers | differ | of | nearest skin (how many) | where the worst one lies |")
    print("|---|---|---|---|---|---|---|---|---|---|")
    for r in rows:
        tot += r["differ"]; pts += r["points"]
        for k, v in r["hairs"].items():
            worst[k] = worst.get(k, 0) + v
        w = r.get("worst")
        where = "(%s) js %s, card %s" % (", ".join(str(x) for x in w["p"]), w["js"], w["gpu"]) if w else ""
        extra = (r.get("params", "") + " " + r.get("mods", "")).strip()
        hairs = ", ".join("%s: %d" % (k, v) for k, v in sorted(r["hairs"].items(), key=lambda kv: (kv[0] == "none", float(kv[0]) if kv[0] != "none" else 9)))
        print("| %s | %s | %s | %s | %s | %s | %d | %d | %s | %s |" % (r["id"], r["n"], r["kind"], r["c"], r["z"], extra, r["differ"], r["points"], hairs, where))
    print("\ncases %d, points %d, differ %d (%.4f%%)" % (len(rows), pts, tot, 100.0 * tot / max(pts, 1)))
    print("by distance to the nearest skin that explains the difference:", ", ".join("%s: %d" % (k, v) for k, v in sorted(worst.items(), key=lambda kv: (kv[0] == "none", float(kv[0]) if kv[0] != "none" else 9))))


def all21():
    rows, tail = result("all21.log", 3)
    print("\n## all21.log   (last line of the log: %s)" % tail)
    if rows is None:
        return
    print("| approach | id | builds (power 2 / other power) | build ms (2 / other) | first picture ms (2 / other) | drawn % m, j (power 2) | drawn % m, j (power 3) | ball at step 0 % | still frame ms, step 8 Julia (2 / 3) |")
    print("|---|---|---|---|---|---|---|---|---|")
    for r in rows:
        print("| %s | %s | %s / %s | %s / %s | %s / %s | %s, %s | %s, %s | %s | %s / %s |" % (
            r["name"], r["id"], "yes" if r["ok2"] else "NO", "yes" if r["ok3"] else "NO", r["build2"], r["build3"], r["first2"], r["first3"],
            r["m2"], r["j2"], r["m3"], r["j3"], r["ball2"], r["still2"], r["still3"]))
    b = [r["build2"] for r in rows] + [r["build3"] for r in rows]
    f = [r["first2"] for r in rows] + [r["first3"] for r in rows]
    print("\nbuild ms: least %s, greatest %s; first picture ms: least %s, greatest %s" % (min(b), max(b), min(f), max(f)))


def timing():
    rows, tail = result("timing-run.log", 4)
    print("\n## timing-run.log   (last line of the log: %s)" % tail)
    if rows is None:
        return
    print("| approach | kind | step | still: ms median (least), buffer, stops | move, finest | move, where it starts | move, half size |")
    print("|---|---|---|---|---|---|---|")
    for r in rows:
        if "id" in r:
            print("| %s | %s | %s | %s | %s | %s | %s |" % (r["id"], r["kind"], r["step"], r["still"], r["move0"], r["move1"], r["move2"]))
        else:
            print("\nbuilds in this run (ms):", {k: round(v) for k, v in r["builds"].items()})


def robust():
    d, tail = result("robust-run.log", 3)
    print("\n## robust-run.log   (last line of the log: %s)" % tail)
    if d is None:
        return
    print(json.dumps(d, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    for stream in (sys.stdout, sys.stderr):
        try: stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception: pass
    slices("slice-required.log", 3)
    slices("slice-wide.log", 4)
    all21()
    timing()
    robust()

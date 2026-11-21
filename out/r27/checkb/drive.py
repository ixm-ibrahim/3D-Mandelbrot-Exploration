"""Run one steps file of out/r27/checkb/steps/ through tools/shot.py for several window sizes and themes.

  python out/r27/checkb/drive.py NAME [combos]      combos like  wd,wl,pd,pl  (w = 1400x950, p = 390x800; d dark, l light)

In the steps file the text @T is replaced by the combo (for example wd), so each combo writes its own pictures.
The page is dist/r27-checkb.html unless the steps file's first action has a key "url".
"""
import json, os, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
SIZES = {"w": "1400x950", "p": "390x800"}
THEMES = {"d": "dark", "l": "light"}


def main():
    name = sys.argv[1]
    combos = (sys.argv[2] if len(sys.argv) > 2 else "wd,wl,pd,pl").split(",")
    with open(os.path.join(HERE, "steps", name + ".json"), encoding="utf-8") as f:
        raw = f.read()
    for c in combos:
        text = raw.replace("@T", c)
        acts = json.loads(text)
        url = "dist/r27-checkb.html"
        if acts and "url" in acts[0]:
            url = acts[0].pop("url")
        tmp = os.path.join(HERE, "steps", "_run-%s-%s.json" % (name, c))
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(acts, f)
        t0 = time.time()
        print("=== %s  %s %s" % (name, SIZES[c[0]], THEMES[c[1]]), flush=True)
        r = subprocess.run([sys.executable, "-W", "ignore", os.path.join(ROOT, "tools", "shot.py"), "--url", os.path.join(ROOT, url),
                            "--size", SIZES[c[0]], "--theme", THEMES[c[1]], "--actions", tmp], cwd=ROOT,
                           capture_output=True, text=True, encoding="utf-8", errors="replace")
        print(r.stdout.strip())
        if r.stderr.strip():
            print("STDERR:", r.stderr.strip()[-1500:])
        print("exit %d, %.1f s" % (r.returncode, time.time() - t0), flush=True)
        os.makedirs(os.path.join(HERE, "logs"), exist_ok=True)
        with open(os.path.join(HERE, "logs", "%s-%s.txt" % (name, c)), "w", encoding="utf-8") as f:
            f.write("%s  %s %s  page %s\n" % (name, SIZES[c[0]], THEMES[c[1]], url))
            f.write(r.stdout)
            if r.stderr.strip():
                f.write("\nSTDERR:\n" + r.stderr)
            f.write("\nexit %d, %.1f s\n" % (r.returncode, time.time() - t0))
        os.remove(tmp)


if __name__ == "__main__":
    main()

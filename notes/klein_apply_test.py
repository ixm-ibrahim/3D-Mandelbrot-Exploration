"""Check data/klein-presets.json as data, then apply every preset in the page the way the UI should.

    python notes/klein_apply_test.py [page]        default page: dist/klein-presets.html (the baseline build)

Part 1 (no browser): the shape of every entry, and that each value lies inside the hard limits of its dial.
Part 2 (browser, at 1400 x 950 and at 375 x 812): switch to the Kleinian view, apply each preset with the
function below, wait for the picture to finish, and read back the state (which must equal the JSON exactly), the typed
boxes (to the four decimals the baseline boxes show), the third-map checkbox and the camera. The function is the one suggested to the UI in notes/klein-presets.md, written
against window.squaringLab because a test cannot reach the page's private names.
"""
import json, os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "out", "klein-presets")
# hard limits of the Kleinian dials in the baseline UI (src/js/80-ui.js): a typed value is clamped to these
HARD = dict(mx=(-2, 2), my=(0.5, 4), mz=(-2, 2), L=(0.05, 8), iter=(5, 400), invR=(0.05, 10), cx=(-6, 6), cy=(-6, 6), cz=(-6, 6))
BOX = dict(mx="kmx", my="kmy", mz="kmz", L="kL", iter="kiter", invR="kinvr", cx="kcx", cy="kcy", cz="kcz")

APPLY = """
function applyKleinPreset(p) {
  const L = window.squaringLab;
  Object.assign(L.S.k, p.k);
  document.getElementById('k3').checked = L.S.k.three;
  L.cam.yaw = p.cam.yaw; L.cam.pitch = p.cam.pitch; L.cam.dist = p.cam.dist; L.cam.target = [0, 0, 0];
  L.syncControls();
  L.touch();
}
"""


def static_checks(ps):
    assert len(ps) >= 12, "at least twelve presets"
    names = set()
    for p in ps:
        assert set(p) == {"name", "note", "k", "cam", "source"}, p
        assert set(p["k"]) == {"mx", "my", "mz", "three", "L", "iter", "invR", "cx", "cy", "cz"}, p["name"]
        assert set(p["cam"]) == {"yaw", "pitch", "dist"}, p["name"]
        assert isinstance(p["k"]["three"], bool) and isinstance(p["k"]["iter"], int)
        assert p["source"] == "inside" or p["source"] == "explored" or p["source"].startswith("cusp "), p["source"]
        assert p["name"] not in names; names.add(p["name"])
        assert p["note"].endswith(".") and "!" not in p["note"]
        for key, (lo, hi) in HARD.items():
            assert lo <= p["k"][key] <= hi, (p["name"], key)
        assert 0 < p["k"]["cy"] < p["k"]["my"], "the turning-out centre must lie between the walls"
    kinds = [p["source"].split()[0] for p in ps]
    print("part 1 ok: %d presets (%d cusp, %d inside, %d explored), %d with a non-zero j part"
          % (len(ps), kinds.count("cusp"), kinds.count("inside"), kinds.count("explored"), sum(1 for p in ps if p["k"]["mz"] != 0)))


def page_checks(ps, page, size):
    acts = [{"js": "document.getElementById('mode-k').click();", "wait": "done"}]
    for p in ps:
        read = ("const L = window.squaringLab, k = L.S.k, want = %s, bad = [];"
                "for (const key in want.k) if (k[key] !== want.k[key]) bad.push('state ' + key + ' = ' + k[key]);"
                "const boxes = %s;"
                "for (const key in boxes) { const el = document.getElementById(boxes[key] + 'Num'); const v = el ? parseFloat(el.value) : NaN;"
                "  if (!(Math.abs(v - want.k[key]) < 6e-5)) bad.push('box ' + key + ' shows ' + (el ? el.value : 'nothing')); }"   # the baseline boxes show four decimals
                "if (document.getElementById('k3').checked !== want.k.three) bad.push('third-map box');"
                "if (L.cam.yaw !== want.cam.yaw || L.cam.pitch !== want.cam.pitch || L.cam.dist !== want.cam.dist || L.cam.target.join() !== '0,0,0') bad.push('camera');"
                "if (!L.idle()) bad.push('not finished');"
                "return bad.length ? want.name + ': ' + bad.join('; ') : null;") % (json.dumps(p), json.dumps(BOX))
        acts.append({"js": APPLY + "applyKleinPreset(%s); return null;" % json.dumps(p), "wait": "done", "timeout": 120})
        acts.append({"js": read})
    steps = os.path.join(OUT, "apply-steps.json")
    with open(steps, "w", encoding="utf-8") as f:
        json.dump(acts, f)
    r = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "shot.py"), "--url", os.path.join(ROOT, page), "--actions", steps, "--size", size],
                       capture_output=True, text=True, cwd=ROOT, encoding="utf-8", errors="replace")
    os.remove(steps)
    problems = [ln for ln in r.stdout.splitlines() if "result" in ln or "TIMED OUT" in ln or "PAGE PROBLEMS" in ln or ln.startswith("  ")]
    waits = [float(ln.split("waited")[1].split("s")[0]) for ln in r.stdout.splitlines() if "waited" in ln]
    ok = r.returncode == 0 and not problems
    print("part 2 at %s: %d presets applied, slowest picture %.1f s, exit code %d, %s"
          % (size, len(ps), max(waits[1:] or [0]), r.returncode, "all as expected" if ok else "PROBLEMS:"))
    for ln in problems:
        print("   ", ln)
    if r.returncode not in (0, 3) and not problems:
        print(r.stdout[-600:], r.stderr[-600:])
    return ok


if __name__ == "__main__":
    page = sys.argv[1] if len(sys.argv) > 1 else "dist/klein-presets.html"
    with open(os.path.join(ROOT, "data", "klein-presets.json"), encoding="utf-8") as f:
        presets = json.load(f)
    static_checks(presets)
    good = all([page_checks(presets, page, "1400x950"), page_checks(presets, page, "375x812")])
    sys.exit(0 if good else 1)

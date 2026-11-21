"""Check data/julia-presets.json as data, then apply every preset in the page the way the UI is asked to.

  python notes/julia_apply_test.py

Part 1 (no browser): shape of every entry, unique names, values inside the limits of the lab's dials and camera.
Part 2 (baseline build in headless Chrome, at a desktop and a phone window size): run the suggested "jump to
this point" code for every preset and check that the state, the typed boxes of the three c dials, the planes
dial, the iteration dial and the camera all follow, that the picture finishes drawing, and that moving a dial
afterwards does not write into the preset list.
Exit code 0 only if everything passes and the page logs no error.
"""
import json, os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "out", "julia-presets")

# The code suggested to the UI integrator (see notes/julia-presets.md), word for word except that the names it
# takes from the page's own scope (S, cam, stage, clampDist, syncControls, refresh) are rebuilt from the test handle.
APPLY = """
window.__applyJulia = p => {
  const L = window.squaringLab, S = L.S, cam = L.cam, stage = document.getElementById('stage');
  const clampDist = d => Math.max(S.view.zmin, Math.min(S.view.zmax, d)), syncControls = L.syncControls, refresh = L.refresh;
  S.c = p.c.slice();                                     // a copy: the c dials write into S.c in place
  if (p.planes && S.param.mercator) S.param.mercator.planes = p.planes;
  if (p.iter && S.iter < p.iter) S.iter = p.iter;        // a floor, never lowers what the user chose
  if (p.cam && !S.flat) {
    const narrow = Math.max(1, 1.2 * stage.clientHeight / stage.clientWidth);   // 1 on a desktop stage
    cam.target = [0, 0, 0]; cam.yaw = p.cam.yaw; cam.pitch = p.cam.pitch; cam.dist = clampDist(p.cam.dist * narrow);
  }
  syncControls(); refresh(false);
};
"""


def static_checks(P):
    bad = []
    names = [p.get("name") for p in P]
    if len(set(names)) != len(names):
        bad.append("names are not unique")
    for p in P:
        n = p.get("name", "?")
        if set(p) - {"name", "note", "c", "source", "planes", "iter", "cam"}:
            bad.append("%s: unknown keys %s" % (n, sorted(set(p) - {"name", "note", "c", "source", "planes", "iter", "cam"})))
        if not (isinstance(p.get("name"), str) and p["name"] and isinstance(p.get("note"), str) and p["note"]):
            bad.append("%s: name and note must be non-empty text" % n)
        if "!" in p.get("note", "") or len(p.get("note", "")) > 130:
            bad.append("%s: note has an exclamation mark or is over 130 characters" % n)
        c = p.get("c")
        if not (isinstance(c, list) and len(c) == 3 and all(isinstance(t, (int, float)) and abs(t) <= 8 for t in c)):
            bad.append("%s: c must be three numbers within the dials' hard limits of -8..8" % n)
        elif any(round(t, 6) != t for t in c):
            bad.append("%s: c has more than six decimals" % n)
        if p.get("source") not in ("classic", "computed", "explored"):
            bad.append("%s: source %r" % (n, p.get("source")))
        if p.get("source") == "explored" and c and c[2] == 0:
            bad.append("%s: an explored preset should have a z part" % n)
        if p.get("planes") not in (1, 2):
            bad.append("%s: planes %r" % (n, p.get("planes")))
        if "iter" in p and not (isinstance(p["iter"], int) and 14 < p["iter"] <= 60):
            bad.append("%s: iter %r" % (n, p["iter"]))
        cam = p.get("cam")
        if cam is not None and not (set(cam) == {"yaw", "pitch", "dist"} and abs(cam["pitch"]) <= 1.5 and 0.005 <= cam["dist"] <= 24):
            bad.append("%s: cam %r is outside what the baseline camera allows" % (n, cam))
    return bad


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    with open(os.path.join(ROOT, "data", "julia-presets.json"), encoding="utf-8") as f:
        P = json.load(f)
    counts = {s: sum(1 for p in P if p["source"] == s) for s in ("classic", "computed", "explored")}
    print("%d presets: %s; %d with a z part" % (len(P), counts, sum(1 for p in P if p["c"][2] != 0)))
    bad = static_checks(P)
    if counts["classic"] + counts["computed"] < 14:
        bad.append("fewer than fourteen well-known constants")
    if sum(1 for p in P if p["source"] == "explored" and p["c"][2] != 0 and p["planes"] == 2) < 6:
        bad.append("fewer than six explored constants with a z part for two planes")
    print("data checks: %s" % ("pass" if not bad else "FAIL\n  " + "\n  ".join(bad)))

    check = """
const P = %s, L = window.squaringLab, S = L.S, fails = [];
const num = id => parseFloat(document.getElementById(id).value), near = (a, b, e) => Math.abs(a - b) <= e;
const frozen = JSON.stringify(P), st = document.getElementById('stage'), narrow = Math.max(1, 1.2 * st.clientHeight / st.clientWidth);
S.iter = 14;
for (const p of P) {
  const before = S.iter;
  window.__applyJulia(p);
  if (S.c === p.c || S.c.some((v, i) => v !== p.c[i])) fails.push(p.name + ': S.c');
  ['cx', 'cy', 'cz'].forEach((id, i) => { if (!near(num(id + 'Num'), p.c[i], 6e-5)) fails.push(p.name + ': the box of dial ' + id + ' shows ' + num(id + 'Num')); });
  if (S.param.mercator.planes !== p.planes || num('par-mercator-planesNum') !== p.planes) fails.push(p.name + ': planes');
  if (S.iter !== Math.max(before, p.iter || 0) || num('iterNum') !== S.iter) fails.push(p.name + ': iterations');
  if (!near(L.cam.dist, p.cam.dist * narrow, 1e-9) || L.cam.yaw !== p.cam.yaw || L.cam.pitch !== p.cam.pitch || L.cam.target.some(v => v !== 0)) fails.push(p.name + ': camera');
  // moving a dial afterwards must not reach back into the list
  const r = document.getElementById('cz'); r.value = 0.5; r.dispatchEvent(new Event('input', { bubbles: true }));
  if (S.c[2] !== 0.5) fails.push(p.name + ': the z dial did not write to S.c');
}
if (JSON.stringify(P) !== frozen) fails.push('applying a preset and then moving a dial changed the preset list');
window.__applyJulia(P[0]);
return fails.length ? 'FAIL: ' + fails.join('; ') : 'all ' + P.length + ' presets apply cleanly (stage ' + st.clientWidth + ' x ' + st.clientHeight + ', distance factor ' + narrow.toFixed(3) + ')';
""" % json.dumps(P, ensure_ascii=False)
    steps = [{"js": "document.getElementById('mode-j').click(); const L = window.squaringLab; L.S.q.aa = 2; L.touch(); return null;", "wait": "done"},
             {"js": APPLY + check, "wait": "done", "timeout": 120}]
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, "apply-steps.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(steps, f, ensure_ascii=False)
    ok = not bad
    for size in ("1400x950", "375x812"):      # the desktop stage the cameras were chosen on, and a phone
        r = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "shot.py"), "--url", "dist/julia-presets.html", "--actions", path, "--size", size],
                           cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace")
        print("window %s:" % size)
        for ln in r.stdout.strip().splitlines():
            print("  " + ln)
        ok = ok and r.returncode == 0 and "FAIL" not in r.stdout and "apply cleanly" in r.stdout
    os.remove(path)
    print("RESULT:", "pass" if ok else "FAIL")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()

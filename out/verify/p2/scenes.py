"""p2: scenario checks with real input (edge-case typing, odd dial, approach switching, when rules, sweeps, screenshots)."""
import json, os, shutil, socket, subprocess, sys, tempfile, time, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from battery import T, ROOT, L, SHIFT, fmt  # noqa: E402
from shot import WS, Page, CHROMES  # noqa: E402

lines = []


def ok(name, cond, detail=""):
    s = ("pass  " if cond else "FAIL  ") + name + ("" if cond else "  :: " + str(detail))
    lines.append(s); print(s, flush=True)


def note(s):
    lines.append("note  " + s); print("note  " + s, flush=True)


def main():
    theme = sys.argv[1] if len(sys.argv) > 1 else "dark"
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    chrome = next((c for c in CHROMES if os.path.exists(c)), None)
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0)); port = probe.getsockname()[1]
    prof = tempfile.mkdtemp(prefix="p2s-")
    proc = subprocess.Popen([chrome, "--headless=new", "--remote-debugging-port=%d" % port, "--user-data-dir=" + prof,
                             "--no-first-run", "--no-default-browser-check", "--disable-extensions", "--hide-scrollbars",
                             "--window-size=1400,950", "--force-device-scale-factor=1", "about:blank"],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        target = None
        for _ in range(150):
            try:
                with urllib.request.urlopen("http://127.0.0.1:%d/json/list" % port, timeout=2) as r:
                    pages = [x for x in json.load(r) if x.get("type") == "page"]
                if pages:
                    target = pages[0]["webSocketDebuggerUrl"]; break
            except Exception:
                pass
            time.sleep(0.2)
        page = Page(WS(target))
        for m in ("Runtime.enable", "Log.enable", "Page.enable"):
            page.call(m)
        page.call("Emulation.setDeviceMetricsOverride", width=1400, height=950, deviceScaleFactor=1, mobile=False)
        page.call("Emulation.setEmulatedMedia", features=[{"name": "prefers-color-scheme", "value": theme}])
        page.call("Emulation.setFocusEmulationEnabled", enabled=True)
        page.call("Page.navigate", url="file:///" + os.path.join(ROOT, "dist", "preview.html").replace("\\", "/"))
        page.wait("document.readyState === 'complete'", 60)
        page.wait(L + " && " + L + ".S", 120)
        time.sleep(1.0)
        t = T(page)
        t.js("S.q.res=0.25; S.q.aa=1; S.q.steps=60; S.q.shadow=false; S.q.ao=false; L.syncControls(); L.touch();")
        box = lambda i: t.js("return document.getElementById(%s).value;" % json.dumps(i + "Num"))
        inv = lambda i: t.js("const n=document.getElementById(%s); return [n.getAttribute('aria-invalid'), n.parentElement.dataset.flag||''];" % json.dumps(i + "Num"))
        vis = lambda i: t.js("return document.getElementById(%s).closest('.dial').checkVisibility();" % json.dumps(i + "Num"))
        st = lambda e: t.js("return %s;" % e)
        shot = lambda name, clip=None: page.shot(os.path.join(HERE, name), clip)

        def enter(i, text, end="Enter"):
            t.retype("#" + i + "Num", text); t.key(end)

        if theme == "light":
            t.js("document.querySelectorAll('details.sec').forEach(s=>{s.open=true;});")
            enter("pow", "2.37")
            shot("light-eq-fine.png", "#eqDials")
            t.click("#powStep"); shot("light-eq-whole.png", "#eqDials")
            shot("light-quality.png", "#qDials")
            return

        # ---- A. more typing on Power n
        enter("pow", "2")
        cases = [(" 3 ", 3), ("+4", 4), (".5", 0.5), ("5.", 5), ("-0", 0), ("00012", 12), ("1e1", 10), ("1E1", 10), ("2.123456789", 2.123456789),
                 ("– 3", None), ("1,234.5", None), ("1.234,5", None), ("1e999", None), ("0x10", None), ("1.2.3", None), ("--5", None), ("1e", None),
                 ("Infinity", None), ("NaN", None), ("2/3", None), ("1 000", None), ("３", None), ("3%", None), ("2;", None), ("=2+1", None)]
        for text, exp in cases:
            before = st("S.n")
            enter("pow", text)
            s, b, fl = st("S.n"), box("pow"), inv("pow")
            if exp is None:
                ok("typing %r is refused, old value kept and flagged" % text, s == before and b == fmt(before) and fl[0] == "true", (s, b, fl))
            else:
                ok("typing %r gives %s" % (text, fmt(exp)), abs(s - exp) < 1e-12 and b == fmt(exp) and fl[0] is None, (s, b, fl))
        enter("pow", "2.123456789")
        t.click("#powNum ~ .dial-steps .dial-up")
        ok("a long decimal keeps its digits in the state and steps cleanly (2.223456789, box 2.223457)", st("S.n") == 2.223456789 and box("pow") == "2.223457", (st("S.n"), box("pow")))
        enter("pow", "1e-7")
        note("typed 1e-7 into Power n: state %r, box %r" % (st("S.n"), box("pow")))
        enter("pow", "0.00000004")
        note("typed 0.00000004 into Power n: state %r, box %r" % (st("S.n"), box("pow")))
        t.click("#powNum ~ .dial-steps .dial-up")
        note("  then one step up: state %r, box %r" % (st("S.n"), box("pow")))
        # type then step without committing
        enter("pow", "2")
        t.retype("#powNum", "5"); t.click("#powNum ~ .dial-steps .dial-up")
        ok("typed 5 (not committed) then the up button: steps from what is typed (5.1)", st("S.n") == 5.1 and box("pow") == "5.1", (st("S.n"), box("pow")))
        t.retype("#powNum", "abc"); t.key("ArrowUp")
        ok("typed abc then ArrowUp: steps from the current value (5.2), no junk left", st("S.n") == 5.2 and box("pow") == "5.2", (st("S.n"), box("pow")))
        # clamped flag picture
        enter("pow", "99"); shot("flag-clamped.png", "#eqDials")
        ok("typed 99: clamped to 24 with the clamp flag", st("S.n") == 24 and inv("pow")[1] == "clamped", (st("S.n"), inv("pow")))
        enter("pow", "abc"); shot("flag-invalid.png", "#eqDials")
        time.sleep(1.5)
        enter("pow", "2.37")
        shot("eq-fine.png", "#eqDials")
        t.click("#powStep"); time.sleep(0.1); shot("eq-whole.png", "#eqDials")
        tip = t.js("const m=document.getElementById('powStep'); return [m.textContent, m.title, m.getAttribute('aria-label'), m.getAttribute('aria-pressed'), document.querySelector('#powNum ~ .dial-steps .dial-up').title];")
        note("toggle in whole mode: %r" % (tip,))
        # does a reset leave the toggle in whole mode?
        t.click("#eqReset .dial-reset")
        time.sleep(0.4)
        tip2 = t.js("const m=document.getElementById('powStep'); return [m.textContent, m.getAttribute('aria-pressed'), L.S.n, document.getElementById('powNum').value];")
        note("after 'Reset this section' in Equation: toggle %r" % (tip2,))
        if tip2[1] == "true":
            t.click("#powStep")
        # reload check of toggle memory is by design (not remembered)

        # ---- B. iterations (whole-number-only)
        for text, exp in [("20.6", 21), ("20.5", 21), ("20.4", 20), ("2.5e1", 25), ("-3", 3), ("7,5", 8), ("400.4", 400), ("400.6", 400), ("2.4", 3)]:
            enter("iter", text)
            ok("Iterations: typing %r gives %d" % (text, exp), st("S.iter") == exp and box("iter") == str(exp), (st("S.iter"), box("iter")))
        t.retype("#iterNum", "20.6"); t.click("#iterNum ~ .dial-steps .dial-up")
        ok("Iterations: typed 20.6 (uncommitted) then up gives a whole number", st("S.iter") == round(st("S.iter")) and box("iter") == str(st("S.iter")), (st("S.iter"), box("iter")))
        note("Iterations: 20.6 typed then up button -> %r" % st("S.iter"))
        enter("iter", "14")

        # ---- C. the odd-only dial
        t.click("#ap-lathe + .mark"); time.sleep(0.4)
        sp = "S.param.lathe.spin"
        for text, exp in [("4", 5), ("2", 3), ("0", 1), ("-2", -1), ("2.9", 3), ("-6.5", -7), ("11", 9), ("-9", -7), ("3", 3), ("-3,2", -3), ("−5", -5), ("6.99", 7), ("8", 9)]:
            enter("par-lathe-spin", text)
            ok("Spin (odd): typing %r gives %d" % (text, exp), st(sp) == exp and box("par-lathe-spin") == str(exp), (st(sp), box("par-lathe-spin")))
        enter("par-lathe-spin", "1")
        seq = []
        for a in ("U", "U", "D", "D", "D", "u", "d", "d"):
            if a == "U": t.click("#par-lathe-spinNum ~ .dial-steps .dial-up")
            elif a == "D": t.click("#par-lathe-spinNum ~ .dial-steps .dial-down")
            elif a == "u": t.key("ArrowUp")
            else: t.key("ArrowDown")
            seq.append(st(sp))
        ok("Spin (odd): up up down down down, ArrowUp, ArrowDown ArrowDown from 1 = 3 5 3 1 -1 1 -1 -3", seq == [3, 5, 3, 1, -1, 1, -1, -3], seq)
        t.retype("#par-lathe-spinNum", "4"); t.key("ArrowUp"); a = st(sp)
        t.retype("#par-lathe-spinNum", "4"); t.key("ArrowDown"); b = st(sp)
        ok("Spin (odd): typed 4 then ArrowUp = 5, typed 4 then ArrowDown = 3", (a, b) == (5, 3), (a, b))
        # drag the slider across: only odd values
        x0, y0 = t.xy("#par-lathe-spin", 0.03); x1, _ = t.xy("#par-lathe-spin", 0.97)
        t.mouse("mouseMoved", x0, y0); t.mouse("mousePressed", x0, y0, button="left", clickCount=1)
        seen = set()
        for i in range(1, 41):
            t.mouse("mouseMoved", x0 + (x1 - x0) * i / 40, y0, button="left", buttons=1); seen.add(st(sp))
        t.mouse("mouseReleased", x1, y0, button="left", clickCount=1)
        ok("Spin (odd): dragging the slider end to end only ever stores odd numbers", all(v == round(v) and int(v) % 2 for v in seen) and len(seen) >= 6, sorted(seen))
        shot("spin.png", "#pd-lathe")

        # ---- D. values survive switching approach and mode
        t.click("#ap-mercator + .mark"); time.sleep(0.3)
        enter("par-mercator-lift", "0.37"); enter("par-mercator-planes", "3")
        t.click("#ap-lathe + .mark"); time.sleep(0.3); enter("par-lathe-spin", "5")
        t.click("#ap-bulb + .mark"); time.sleep(0.3); enter("par-bulb-lat", "12.5"); enter("par-bulb-lon", "-200")
        t.click("#ap-classic + .mark"); time.sleep(0.3); enter("par-classic-theta", "-33.25")
        enter("pow", "3.7")
        t.click("#ap-mercator + .mark"); time.sleep(0.4)
        a = [st("S.param.mercator.lift"), box("par-mercator-lift"), st("S.param.mercator.planes"), box("par-mercator-planes"), vis("par-mercator-lift")]
        ok("back on Sphere inversions: lift 0.37 and planes 3 are still there and shown", a == [0.37, "0.37", 3, "3", True], a)
        t.click("#ap-lathe + .mark"); time.sleep(0.3)
        a = [st(sp), box("par-lathe-spin"), vis("par-lathe-spin")]
        ok("back on the lathe: spin 5 still there", a == [5, "5", True], a)
        t.click("#ap-bulb + .mark"); time.sleep(0.3)
        a = [st("S.param.bulb.lat"), box("par-bulb-lat"), st("S.param.bulb.lon"), box("par-bulb-lon")]
        ok("back on the equator bulb: lat 12.5 and lon -200 still there", a == [12.5, "12.5", -200, "-200"], a)
        t.click("#ap-classic + .mark"); time.sleep(0.3)
        a = [st("S.param.classic.theta"), box("par-classic-theta"), st("S.n"), box("pow")]
        ok("back on the classic bulb: theta -33.25 still there, Power n still 3.7", a == [-33.25, "-33.25", 3.7, "3.7"], a)
        # step-1 dial without a toggle, from a fractional value
        t.click("#par-classic-thetaNum ~ .dial-steps .dial-up"); a = st("S.param.classic.theta")
        note("theta phase (step 1, no toggle): -33.25 then up -> %r" % a)
        t.click("#ap-mercator + .mark"); time.sleep(0.3)
        t.click("label:has(#mode-j)"); time.sleep(0.4)
        enter("cx", "0.123"); enter("cz", "-0.5")
        t.click("label:has(#mode-k)"); time.sleep(0.4)
        enter("kmy", "1.95")
        t.click("label:has(#mode-m)"); time.sleep(0.4)
        t.click("label:has(#mode-j)"); time.sleep(0.4)
        a = [st("S.c[0]"), box("cx"), st("S.c[2]"), box("cz")]
        ok("Julia point survives a trip through Kleinian and Mandelbrot", a == [0.123, "0.123", -0.5, "-0.5"], a)
        t.click("label:has(#mode-k)"); time.sleep(0.4)
        ok("Kleinian value survives too", [st("S.k.my"), box("kmy")] == [1.95, "1.95"], [st("S.k.my"), box("kmy")])
        t.click("label:has(#mode-m)"); time.sleep(0.4)

        # ---- E. when rules
        if not st("S.mosaic"): t.click("label:has(#m-mosaic)")
        time.sleep(0.3)
        enter("m-mosaicCell", "0.5")
        t.click("label:has(#m-mosaic)"); time.sleep(0.3); h = vis("m-mosaicCell")
        t.click("label:has(#m-mosaic)"); time.sleep(0.3)
        a = [h, vis("m-mosaicCell"), st("S.mosaicCell"), box("m-mosaicCell")]
        ok("mosaic cell size: hidden when the mosaic is off, back with 0.5 when on", a == [False, True, 0.5, "0.5"], a)
        t.click("label:has(#m-mosaic)"); time.sleep(0.2)
        enter("par-mercator-planes", "1"); time.sleep(0.2)
        v1 = vis("par-mercator-turn")
        enter("par-mercator-turn", "40.5")
        enter("par-mercator-planes", "2"); time.sleep(0.2); v2 = vis("par-mercator-turn")
        hidden_state = st("S.param.mercator.turn")
        enter("par-mercator-planes", "1"); time.sleep(0.2)
        a = [v1, v2, vis("par-mercator-turn"), st("S.param.mercator.turn"), box("par-mercator-turn")]
        ok("turn: shown with 1 plane, hidden with 2, back showing the state", a[:3] == [True, False, True] and box("par-mercator-turn") == fmt(a[3]), a)
        note("turn while hidden (planes 2): state stays %r" % hidden_state)
        # sweep, then hide: it must pause and show the state when it comes back
        t.click("#par-mercator-turnPlay"); time.sleep(1.2)
        playing = t.js("return document.getElementById('par-mercator-turnPlay').getAttribute('aria-pressed');")
        mid = [st("S.param.mercator.turn"), box("par-mercator-turn")]
        ok("turn: while it plays the box follows the state", playing == "true" and mid[1] == fmt(mid[0]) and mid[0] != 40.5, (playing, mid))
        t.click("#par-mercator-turnPlay"); time.sleep(0.3)
        a = st("S.param.mercator.turn"); b = box("par-mercator-turn")
        t.click("#par-mercator-turnNum ~ .dial-steps .dial-up")
        note("turn after a sweep was paused: %r (box %r); one step up -> %r" % (a, b, st("S.param.mercator.turn")))
        t.click("#par-mercator-turnPlay"); time.sleep(0.5)
        enter("par-mercator-planes", "2"); time.sleep(0.5)
        s1 = st("S.param.mercator.turn"); time.sleep(0.6); s2 = st("S.param.mercator.turn")
        pl = t.js("return document.getElementById('par-mercator-turnPlay').getAttribute('aria-pressed');")
        ok("turn: a sweep stops when the dial is hidden", s1 == s2 and pl == "false", (s1, s2, pl))
        enter("par-mercator-planes", "1"); time.sleep(0.3)
        ok("turn: shown again it shows the state", box("par-mercator-turn") == fmt(st("S.param.mercator.turn")), (box("par-mercator-turn"), st("S.param.mercator.turn")))
        enter("par-mercator-turn", "0"); enter("par-mercator-planes", "2")
        # colour: radius hidden and shown by the trap shape
        t.js("const s=document.getElementById('col-trap'); s.value=[...s.options].find(o=>/shell/i.test(o.text)).value; s.dispatchEvent(new Event('change',{bubbles:true}));")
        time.sleep(0.3); v1 = vis("col-radius")
        enter("col-radius", "1.37")
        t.js("const s=document.getElementById('col-trap'); s.value=[...s.options].find(o=>/^Point/.test(o.text)).value; s.dispatchEvent(new Event('change',{bubbles:true}));")
        time.sleep(0.3); v2 = vis("col-radius")
        t.js("const s=document.getElementById('col-trap'); s.value=[...s.options].find(o=>/Ring/.test(o.text)).value; s.dispatchEvent(new Event('change',{bubbles:true}));")
        time.sleep(0.3)
        a = [v1, v2, vis("col-radius"), st("S.colour.radius"), box("col-radius")]
        ok("trap radius: shown for shell, hidden for point, back with 1.37 for ring", a == [True, False, True, 1.37, "1.37"], a)
        shot("colour-dials.png", "#colDials")

        # ---- F. presets and resets keep boxes in step with the state
        t.js("document.getElementById('qUltra').click();"); time.sleep(0.3)
        allok = t.js("const bad=[]; const m={qres:S.q.res,qaa:S.q.aa,qsteps:S.q.steps,qdetail:S.q.detail,qstepk:S.q.stepk,qsmooth:S.q.smooth}; for (const k in m) { const b=document.getElementById(k+'Num').value; if (+b!==m[k]) bad.push([k,b,m[k]]); } return bad;")
        ok("Ultra fast: every quality box shows what the state holds", not allok, allok)
        shot("quality-dials.png", "#qDials")
        t.rect("#pd-mercator", True); shot("approach-dials.png", "#pd-mercator")
        problems = [p for p in page.problems]
        ok("no console errors or uncaught exceptions", not problems, problems[:8])
        try:
            page.call("Browser.close")
        except Exception:
            pass
    finally:
        try:
            proc.wait(timeout=5)
        except Exception:
            proc.kill()
        shutil.rmtree(prof, ignore_errors=True)
        with open(os.path.join(HERE, "scenes-%s.txt" % (sys.argv[1] if len(sys.argv) > 1 else "dark")), "w", encoding="utf-8") as fh:
            fh.write("\n".join(lines))


if __name__ == "__main__":
    main()

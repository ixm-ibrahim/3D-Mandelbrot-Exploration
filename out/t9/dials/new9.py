"""Tester "dials", second check: what the first check's driver does not cover on dist/v8.html.

  python out/t9/dials/new9.py <test> [<test> ...]     tests: new thick resets ex phone

new    = the dial "Orbit steps the trap reads" with real typing, keys, buttons, slider, Extreme ranges, where it shows
thick  = Trap thickness below 0.05: typed values, steps, the toggle, and pictures of a trap solid
resets = every reset against a snapshot of the whole page (state, camera, every input, every step toggle), with the new key and both save panels
ex     = the typed width and height of a picture (not reached by the first check)
phone  = the number boxes on a 375 x 812 touch phone, with finger taps
"""
import json, os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, "out", "t6", "controls"))
import drive  # noqa: E402

drive.URL = "dist/v8.html"
drive.HERE = HERE
ok, info, E, L = drive.ok, drive.info, drive.E, drive.L
SHIFT = drive.SHIFT


def setsel(d, id_, v):
    d.js("const e = %s; e.value = %s; e.dispatchEvent(new Event('change', { bubbles: true })); await new Promise(r => setTimeout(r, 150));" % (E(id_), json.dumps(str(v))))


def vis(d, id_):
    return d.js("const n = %s; return !!n && n.closest('.dial').checkVisibility();" % E(id_ + "Num"))


def t_new():
    page, proc, prof = drive.launch()
    d = drive.Drive(page)
    d.load()
    drive.open_all(d)
    d.click(E("qUltra"))
    S = lambda expr: d.js("return %s.S.%s;" % (L, expr))
    box = lambda: d.js("return %s.value;" % E("col-reachNum"))
    inv = lambda: d.js("return %s.getAttribute('aria-invalid');" % E("col-reachNum"))
    st = drive.dial_state(d, "col-reach")
    info("the dial at the start:", json.dumps(st, ensure_ascii=False))
    around = d.js("const e = document.getElementById('col-reachNum').closest('.dial'); const out = []; let n = e; for (let i = 0; i < 3 && n; i++) { out.push([n.className, n.id, n.textContent.trim().slice(0, 700), n.checkVisibility()]); n = n.nextElementSibling; } return out;")
    info("the dial and what follows it on the page:", json.dumps(around, ensure_ascii=False))
    ok("reads: starts at 4, slider 1 to 16 in whole steps, no step toggle", st["box"] == "4" and st["slider"][:3] == ["1", "16", "1"] and st["toggle"] is None and S("colour.reach") == 4, st)
    cases = [("8", 8), ("1", 1), ("0", 1), ("-3", 1), ("100", 100), ("101", 100), ("2.6", 3), ("2,4", 2), ("1e1", 10), (" 7 ", 7), ("abc", None), ("", None), ("3/2", None), ("NaN", None), ("4", 4)]
    for typed, want in cases:
        before = S("colour.reach")
        d.retype(E("col-reachNum"), typed)
        got, shown, flag = S("colour.reach"), box(), inv()
        if want is None:
            ok("reads: typed %r is refused (stays %s, box shows it again, flagged)" % (typed, before), got == before and flag == "true" and shown == str(before), (got, shown, flag))
        else:
            ok("reads: typed %r gives %s" % (typed, want), got == want and shown == str(want), (got, shown, flag))
    d.retype(E("col-reachNum"), "4")
    d.press("ArrowUp"); a = S("colour.reach")
    d.press("ArrowUp", modifiers=SHIFT); b = S("colour.reach")
    d.press("PageDown"); c = S("colour.reach")
    d.press("ArrowDown"); e = S("colour.reach")
    ok("reads: ArrowUp, Shift+ArrowUp, PageDown, ArrowDown from 4 give 5, 15, 5, 4", (a, b, c, e) == (5, 15, 5, 4), (a, b, c, e))
    up = "document.getElementById('col-reachNum').closest('.dial').querySelector('.dial-up')"
    down = "document.getElementById('col-reachNum').closest('.dial').querySelector('.dial-down')"
    d.click(up); a = S("colour.reach"); d.click(down); d.click(down); b = S("colour.reach")
    ok("reads: the up button gives 5, two presses of the down button give 3", (a, b) == (5, 3), (a, b))
    d.retype(E("col-reachNum"), "1"); d.click(down); a = S("colour.reach")
    d.retype(E("col-reachNum"), "100"); d.click(up); b = S("colour.reach")
    ok("reads: the buttons stop at 1 and at 100", (a, b) == (1, 100), (a, b))
    info("slider when the value is 100 (beyond its end 16):", d.js("const s = document.getElementById('col-reach'); return [s.min, s.max, s.value];"))
    # the slider with a real drag and with keys
    r = d.rect(E("col-reach"))
    y = r[1] + r[3] / 2
    d.drag(r[0] + r[2] * 0.5, y, r[0] + r[2] - 2, y, steps=10); time.sleep(0.2)
    a = S("colour.reach")
    d.drag(r[0] + r[2] - 4, y, r[0] + 2, y, steps=10); time.sleep(0.2)
    b = S("colour.reach")
    ok("reads: dragging the slider to its right end gives 16, to its left end 1", (a, b) == (16, 1), (a, b))
    d.js("document.getElementById('col-reach').focus();")
    d.press("ArrowRight"); d.press("ArrowRight"); c = S("colour.reach")
    ok("reads: two presses of ArrowRight on the slider give 3, and the box follows", c == 3 and box() == "3", (c, box()))
    # Extreme ranges
    d.retype(E("col-reachNum"), "4")
    d.click(E("extreme")); time.sleep(0.3)
    st1 = drive.dial_state(d, "col-reach")
    ok("reads, Extreme ranges on: slider to 60, the wide tag shows, the value is still 4", st1["slider"][1] == "60" and st1["wide"] is True and S("colour.reach") == 4, st1)
    d.retype(E("col-reachNum"), "500"); a = S("colour.reach")
    d.retype(E("col-reachNum"), "5000"); b = S("colour.reach")
    ok("reads, Extreme ranges on: typed 500 is taken, 5000 is held at 1000", (a, b) == (500, 1000), (a, b))
    d.retype(E("col-reachNum"), "500")
    snapA = d.js(drive.SNAP)
    d.click(E("extreme")); time.sleep(0.4)
    snapB = d.js(drive.SNAP)
    ch = drive.diff(snapA, snapB)
    ok("reads, Extreme ranges off again: 500 is pulled back to 100, the box shows 100, nothing else changes", S("colour.reach") == 100 and box() == "100" and set(ch) == {"S.extreme", "S.colour.reach"}, ch)
    d.retype(E("col-reachNum"), "4")
    # where the dial shows
    seen = {}
    seen["opening (Mandelbrot, 3D, orbit trap)"] = vis(d, "col-reach")
    for v in d.js("return [...document.getElementById('col-mode').options].map(o => [o.value, o.text]);"):
        setsel(d, "col-mode", v[0]); seen["Colour by: " + v[1]] = vis(d, "col-reach")
    setsel(d, "col-mode", 0)
    for v in d.js("return [...document.getElementById('col-solid').options].map(o => [o.value, o.text]);"):
        setsel(d, "col-solid", v[0]); seen["trap " + v[1]] = vis(d, "col-reach")
    setsel(d, "col-solid", 0)
    d.click(E("m-mosaic")); time.sleep(0.2); seen["Julia mosaic"] = vis(d, "col-reach"); d.click(E("m-mosaic"))
    d.click(E("flat")); time.sleep(0.2); seen["2D view"] = vis(d, "col-reach"); d.click(E("flat")); time.sleep(0.2)
    d.js("document.getElementById('mode-j').click(); await new Promise(r => setTimeout(r, 300));"); seen["Julia"] = vis(d, "col-reach")
    d.js("document.getElementById('mode-k').click(); await new Promise(r => setTimeout(r, 300));"); seen["Kleinian"] = vis(d, "col-reach")
    d.js("document.getElementById('mode-m').click(); await new Promise(r => setTimeout(r, 300));")
    info("where the dial is on show:", json.dumps(seen, ensure_ascii=False))
    # resets
    d.retype(E("col-reachNum"), "9")
    d.click("document.querySelector('#secColour .dial-reset')"); time.sleep(0.3)
    ok("reads: 'Reset this section' of Colour and light puts 9 back to 4 (state, box and slider)", S("colour.reach") == 4 and box() == "4" and d.js("return document.getElementById('col-reach').value;") == "4", (S("colour.reach"), box()))
    d.retype(E("col-reachNum"), "9")
    for sec in ("secEq", "secQuality", "secView", "secApproach", "secCut", "secMod", "mandelPanel"):
        d.click("document.querySelector('#%s .dial-reset')" % sec); time.sleep(0.15)
    ok("reads: the resets of the other sections leave 9 alone", S("colour.reach") == 9, S("colour.reach"))
    for q in ("qFast", "qFine", "qBal", "qUltra"):
        d.click(E(q)); time.sleep(0.15)
    ok("reads: the four quality buttons leave 9 alone", S("colour.reach") == 9, S("colour.reach"))
    d.click(E("resetAll")); time.sleep(0.5)
    ok("reads: 'Reset everything' puts 9 back to 4", S("colour.reach") == 4 and box() == "4", (S("colour.reach"), box()))
    # does the picture answer the dial? (Balanced, opening picture, three values)
    d.stage_top()
    sums = {}
    for v in ("1", "4", "16"):
        d.retype(E("col-reachNum"), v); d.stage_top()
        g, waited = d.idle(400)
        busy = d.js("const b = document.getElementById('busy'); return b && !b.hidden ? b.textContent : '';")
        d.shot("new-reach-%s.png" % v, "#stage")
        sums[v] = (g, round(waited, 1), busy)
    info("pictures at 1, 4, 16 steps (idle reached, seconds waited, busy label):", sums)
    d.retype(E("col-reachNum"), "4")
    d.idle(300)
    drive.finish(page, proc, prof, "new")


def t_thick():
    page, proc, prof = drive.launch()
    d = drive.Drive(page)
    d.load()
    drive.open_all(d)
    S = lambda expr: d.js("return %s.S.%s;" % (L, expr))
    box = lambda: d.js("return %s.value;" % E("col-thickNum"))
    inv = lambda: d.js("return %s.getAttribute('aria-invalid');" % E("col-thickNum"))
    info("Trap thickness on show at the opening settings:", vis(d, "col-thick"))
    d.js("document.getElementById('mode-j').click(); await new Promise(r => setTimeout(r, 400));")
    setsel(d, "col-solid", 1)
    d.retype(E("col-radiusNum"), "0.7")
    st = drive.dial_state(d, "col-thick")
    info("the dial with the trap as the solid:", json.dumps(st, ensure_ascii=False))
    around = d.js("const e = document.getElementById('col-thickNum').closest('.dial'); const out = []; let n = e.nextElementSibling; for (let i = 0; i < 2 && n; i++) { out.push([n.className, n.id, n.textContent.trim().slice(0, 600), n.checkVisibility()]); n = n.nextElementSibling; } return out;")
    info("what follows the dial on the page:", json.dumps(around, ensure_ascii=False))
    cases = [("0.02", 0.02), ("0.005", 0.005), ("0,03", 0.03), ("0.001", 0.001), ("0.0005", 0.0005), ("0.0001", 0.0005), ("0", 0.0005), ("-1", 0.0005), (".04", 0.04), ("5e-3", 0.005), ("0.0125", 0.0125), ("abc", None), ("", None), ("0.05", 0.05)]
    for typed, want in cases:
        before = S("colour.thick")
        d.retype(E("col-thickNum"), typed)
        got, shown, flag = S("colour.thick"), box(), inv()
        if want is None:
            ok("thickness: typed %r is refused (stays %s)" % (typed, before), got == before and flag == "true", (got, shown, flag))
        else:
            ok("thickness: typed %r gives %s (box %r)" % (typed, want, shown), abs(got - want) < 1e-12 and float(shown) == want, (got, shown, flag))
    up = "document.getElementById('col-thickNum').closest('.dial').querySelector('.dial-up')"
    down = "document.getElementById('col-thickNum').closest('.dial').querySelector('.dial-down')"
    seq = []
    for _ in range(12):
        d.click(down); seq.append(box())
    info("thickness: the down button twelve times from 0.05:", seq)
    ok("thickness: the down button walks 0.045, 0.04 ... 0.005 without floating-point noise", seq[:9] == ["0.045", "0.04", "0.035", "0.03", "0.025", "0.02", "0.015", "0.01", "0.005"], seq)
    seq2 = []
    for _ in range(3):
        d.click(up); seq2.append(box())
    info("thickness: then the up button three times:", seq2, "state", S("colour.thick"))
    d.retype(E("col-thickNum"), "0.05")
    d.click(E("col-thickStep")); t1 = d.js("return document.getElementById('col-thickStep').textContent;")
    d.click(down); a = box(); d.click(up); b = box(); d.click(up); c = box(); d.click(down); e = box(); d.click(down); f = box()
    info("thickness: toggle now %s; from 0.05: down %s, up %s, up %s, down %s, down %s" % (t1, a, b, c, e, f))
    d.click(E("col-thickStep"))
    d.retype(E("col-thickNum"), "0.05")
    # the slider's left end
    r = d.rect(E("col-thick")); y = r[1] + r[3] / 2
    d.drag(r[0] + r[2] * 0.3, y, r[0] + 1, y, steps=8); time.sleep(0.2)
    info("thickness: slider dragged to its left end gives", S("colour.thick"), "box", box())
    ok("thickness: the slider's left end is 0.005", S("colour.thick") == 0.005, S("colour.thick"))
    # pictures: the Julia set for c = -1, sphere shell of radius 0.7 as the solid, Balanced
    d.click(E("qBal"))
    d.js("%s.resetCam(); %s.touch();" % (L, L))
    stat = {}
    for v in ("0.05", "0.02", "0.005", "0.0005"):
        d.retype(E("col-thickNum"), v); d.stage_top()
        g, waited = d.idle(500)
        hits = d.js("const L = window.squaringLab, v = document.getElementById('view').getBoundingClientRect(); let n = 0, t = 0; for (let i = 1; i < 30; i++) for (let j = 1; j < 20; j++) { t++; if (L.pick(v.width * i / 30, v.height * j / 20)) n++; } return [n, t];")
        d.shot("thick-%s.png" % v.replace(".", "_"), "#stage")
        stat[v] = (g, round(waited, 1), hits)
    info("thickness pictures (idle, seconds, probes that hit the solid of 551):", stat)
    ok("thickness: the solid is still there at 0.02, 0.005 and 0.0005 (probes hit)", all(stat[v][2][0] > 0 for v in stat), stat)
    d.click(E("resetAll")); d.idle(300)
    drive.finish(page, proc, prof, "thick")


DOM = ("const L = window.squaringLab; const o = { S: JSON.parse(JSON.stringify(L.S)), cam: JSON.parse(JSON.stringify({ yaw: L.cam.yaw, pitch: L.cam.pitch, dist: L.cam.dist, target: L.cam.target })), inputs: {}, toggles: {}, open: {} };"
       " for (const e of document.querySelectorAll('input, select, textarea')) { if (!e.id) continue; o.inputs[e.id] = (e.type === 'checkbox' || e.type === 'radio') ? e.checked : e.value; }"
       " for (const b of document.querySelectorAll('.dial-mode')) o.toggles[b.id] = b.textContent + '|' + b.getAttribute('aria-pressed');"
       " for (const s of document.querySelectorAll('details')) if (s.id) o.open[s.id] = s.open;"
       " o.sel = {}; for (const e of document.querySelectorAll('select')) if (e.id) o.sel[e.id] = e.options[e.selectedIndex] ? e.options[e.selectedIndex].text.slice(0, 40) : null;"
       " o.wide = [...document.querySelectorAll('[id$=Wide]')].filter(w => !w.hidden).length; o.invalid = [...document.querySelectorAll('[aria-invalid=true]')].map(e => e.id); return o;")

PANEL_MOVE = ("for (const e of document.querySelectorAll('#%s input, #%s select')) { if (!e.checkVisibility()) continue; if (e.tagName === 'SELECT') { e.selectedIndex = (e.selectedIndex + 1) %% e.options.length; e.dispatchEvent(new Event('change', { bubbles: true })); }"
              " else if (e.type === 'checkbox') { e.click(); } }")


def t_resets():
    page, proc, prof = drive.launch()
    d = drive.Drive(page)
    d.load()
    drive.open_all(d)
    time.sleep(0.3)
    D0 = d.js(DOM)
    info("snapshot: %d state values, %d inputs with an id, %d step toggles, %d sections" % (len(drive.flat(D0["S"])), len(D0["inputs"]), len(D0["toggles"]), len(D0["open"])))
    info("the button and what the page says about it:", d.js("const b = document.getElementById('resetAll'); return [b.textContent, b.title, b.getAttribute('aria-label')];"))

    def perturb(mode):
        d.js("window.squaringLab.S.mode = %s; window.squaringLab.S.mosaic = false;" % json.dumps(mode))
        d.js(drive.PERTURB + " S.colour.reach = 9; Object.assign(S.v2, { x: 0.1, y: 0.2, h: 1, hmin: 0.001, hmax: 10 }); L.syncControls(); L.refresh(false);")
        time.sleep(0.25)

    # 1. the new key in each mode, by its own section's button
    for mode in ("m", "j"):
        perturb(mode)
        A = d.js(DOM)
        d.click("document.querySelector('#secColour .dial-reset')"); time.sleep(0.35)
        B = d.js(DOM)
        ch = drive.diff(A["S"], B["S"])
        foreign = {k: v for k, v in ch.items() if not (k.startswith("colour.") or k in ("lightAz", "lightEl"))}
        left = {k: (v, drive.flat(D0["S"]).get(k)) for k, v in drive.flat(B["S"]).items() if (k.startswith("colour.") or k in ("lightAz", "lightEl")) and v != drive.flat(D0["S"]).get(k)}
        ok("Colour and light reset (mode %s): reach 9 goes back to 4 with every other colour value, nothing foreign changes (%d changed)" % (mode, len(ch)), B["S"]["colour"]["reach"] == 4 and not foreign and not left, {"foreign": foreign, "left": left})
        info("   inputs of the section after its reset that differ from the opening page:", {k: (B["inputs"][k], D0["inputs"].get(k)) for k in B["inputs"] if k.startswith(("col-", "light", "trapEx")) and B["inputs"][k] != D0["inputs"].get(k)})
    # 2. everything away from the opening state, both save panels included, then Reset everything
    perturb("j")
    d.js("window.squaringLab.S.flat = true; window.squaringLab.syncControls(); window.squaringLab.refresh(false);")
    d.js("window.squaringLab.setExtreme(true);")
    d.js("for (const b of document.querySelectorAll('.dial-mode')) b.click();")
    d.js("document.getElementById('mode-m').click(); await new Promise(r => setTimeout(r, 300));")
    d.js(PANEL_MOVE % ("secExport", "secExport")); time.sleep(0.2)
    d.js("const s = document.getElementById('exportSize'); s.value = [...s.options].find(o => /typed/i.test(o.text)).value; s.dispatchEvent(new Event('change', { bubbles: true })); await new Promise(r => setTimeout(r, 200));")
    d.retype(E("exportWNum"), "3000"); d.retype(E("exportHNum"), "2000")
    d.js(PANEL_MOVE % ("secMesh", "secMesh")); time.sleep(0.2)
    d.retype(E("meshMmNum"), "150"); d.retype(E("meshOffsetNum"), "1.5")
    d.js("document.getElementById('mode-j').click(); await new Promise(r => setTimeout(r, 300));")
    d.click(E("camFly")) if d.js("return document.getElementById('camFly').checkVisibility();") else None
    A = d.js(DOM)
    moved_panels = {k: (D0["inputs"][k], A["inputs"][k]) for k in A["inputs"] if k.startswith(("export", "mesh")) and A["inputs"][k] != D0["inputs"].get(k)}
    info("save panels before Reset everything, settings away from the opening page (%d): %s" % (len(moved_panels), json.dumps(moved_panels, ensure_ascii=False)))
    info("state values away from the opening page before Reset everything: %d of %d; toggles flipped: %d of %d" % (
        len(drive.diff(D0["S"], A["S"])), len(drive.flat(D0["S"])), sum(1 for k in A["toggles"] if A["toggles"][k] != D0["toggles"][k]), len(A["toggles"])))
    d.click(E("resetAll")); time.sleep(0.8)
    B = d.js(DOM)
    left = {}
    for part in ("S", "cam", "inputs", "toggles", "sel"):
        dd = drive.diff(D0[part], B[part])
        if dd:
            left[part] = dd
    info("after Reset everything, what differs from the page as it opens: " + json.dumps(left, ensure_ascii=False))
    ok("Reset everything: the picture's state and camera are as the page opens", "S" not in left and "cam" not in left, {k: left.get(k) for k in ("S", "cam")})
    panel_left = {k: v for k, v in left.get("inputs", {}).items() if k.startswith(("export", "mesh"))}
    other_left = {k: v for k, v in left.get("inputs", {}).items() if not k.startswith(("export", "mesh"))}
    ok("Reset everything: every input outside the two save panels reads as the page opens", not other_left, other_left)
    ok("Reset everything: the two save panels are back at their opening settings too", not panel_left and not {k: v for k, v in left.get("toggles", {}).items()}, {"inputs": panel_left, "toggles": left.get("toggles")})
    info("wide tags on show after Reset everything: %s; boxes flagged invalid: %s; sections open state changed: %s" % (B["wide"], B["invalid"], drive.diff(D0["open"], B["open"])))
    # the panels' own buttons
    for sec in ("secExport", "secMesh"):
        d.click("document.querySelector('#%s .dial-reset')" % sec); time.sleep(0.3)
    C = d.js(DOM)
    left2 = {part: drive.diff(D0[part], C[part]) for part in ("S", "cam", "inputs", "toggles", "sel") if drive.diff(D0[part], C[part])}
    ok("after the two panels' own 'Reset this section' as well, nothing on the page differs from how it opens", not left2, left2)
    # 3. the Examples list, then Reset everything
    names = d.js("return [...document.getElementById('trapExamples').options].map(o => o.text);")
    info("Examples list:", names)
    bad = {}
    for i in range(1, len(names)):
        d.js("const s = document.getElementById('trapExamples'); s.selectedIndex = %d; s.dispatchEvent(new Event('change', { bubbles: true })); await new Promise(r => setTimeout(r, 350));" % i)
        M = d.js(DOM)
        d.click(E("resetAll")); time.sleep(0.6)
        R = d.js(DOM)
        dd = {part: drive.diff(D0[part], R[part]) for part in ("S", "cam", "inputs", "toggles", "sel") if drive.diff(D0[part], R[part])}
        info("   example %d '%s' set %d state values; after Reset everything %d parts differ" % (i, names[i], len(drive.diff(D0["S"], M["S"])), len(dd)))
        if dd:
            bad[names[i]] = dd
    ok("an example followed by Reset everything leaves the page as it opens (all %d examples)" % (len(names) - 1), not bad, bad)
    g, _ = d.idle(500)
    ok("the picture finishes drawing after all the resets", g, d.js("return document.getElementById('status').textContent;"))
    d.stage_top(); d.shot("resets-end.png")
    drive.finish(page, proc, prof, "resets")


def t_ex():
    page, proc, prof = drive.launch()
    d = drive.Drive(page)
    d.load()
    drive.open_all(d)
    d.js("const s = document.getElementById('exportSize'); s.value = [...s.options].find(o => /typed/i.test(o.text)).value; s.dispatchEvent(new Event('change', { bubbles: true })); await new Promise(r => setTimeout(r, 200));")
    v = [i for i in drive.visible_dials(d) if i in ("exportW", "exportH")]
    ok("the typed width and height boxes show when the typed size is chosen", v == ["exportW", "exportH"], v)
    drive.sweep(d, v, "typed picture size", set())
    d.retype(E("exportWNum"), "99999"); a = d.js("return document.getElementById('exportWNum').value;")
    d.retype(E("exportWNum"), "2.6"); b = d.js("return document.getElementById('exportWNum').value;")
    d.retype(E("exportWNum"), "1920,5"); c = d.js("return document.getElementById('exportWNum').value;")
    d.retype(E("exportWNum"), "1920")
    ok("Width, pixels: typed 99999 is held at 8192, 2.6 becomes 16 (the lowest)", (a, b) == ("8192", "16"), (a, b, c))
    d.click(E("extreme")); time.sleep(0.3)
    d.retype(E("exportWNum"), "12000"); a = d.js("return document.getElementById('exportWNum').value;")
    d.click(E("extreme")); time.sleep(0.3)
    b = d.js("return document.getElementById('exportWNum').value;")
    ok("Width with Extreme ranges: 12000 is taken, and pulled back to 8192 when the switch goes off", (a, b) == ("12000", "8192"), (a, b))
    d.click("document.querySelector('#secExport .dial-reset')"); time.sleep(0.3)
    drive.finish(page, proc, prof, "ex")


def t_phone():
    page, proc, prof = drive.launch(375, 812, mobile=True, touch=True, theme="light")
    d = drive.Drive(page)
    d.load()
    drive.open_all(d)
    info("pointer coarse:", d.js("return matchMedia('(pointer: coarse)').matches;"))

    def tap(expr):
        x, y = d.at(expr)
        d.touch("touchStart", [(x, y)]); d.touch("touchEnd", []); time.sleep(0.12)

    tap(E("qUltra"))
    ok("phone: a finger tap on Ultra fast is taken", d.js("return %s.S.q.res;" % L) == 0.5, d.js("return %s.S.q;" % L))
    seen, rows = set(), []

    def sweep(tag):
        for i in drive.visible_dials(d):
            if i in seen:
                continue
            seen.add(i)
            try:
                up = "document.getElementById(%s).closest('.dial').querySelector('.dial-up')" % json.dumps(i + "Num")
                down = "document.getElementById(%s).closest('.dial').querySelector('.dial-down')" % json.dumps(i + "Num")
                s0 = drive.dial_state(d, i); v0 = float(s0["box"])
                tap(up); a = float(drive.dial_state(d, i)["box"])
                tap(down); b = float(drive.dial_state(d, i)["box"])
                good, why = True, []
                if not (a > v0 and (abs(b - v0) < 1e-9 or not float(v0).is_integer())):
                    good = False; why.append("up %s down %s from %s" % (a, b, v0))
                t1 = None
                if s0["toggle"] is not None:
                    tap(E(i + "Step")); t1 = drive.dial_state(d, i)["toggle"]
                    if t1 == s0["toggle"]:
                        good = False; why.append("the toggle did not answer the tap")
                    tap(E(i + "Step"))
                # type with the finger on the box
                x, y = d.at(E(i + "Num"))
                d.touch("touchStart", [(x, y)]); d.touch("touchEnd", []); time.sleep(0.15)
                foc = d.js("return document.activeElement && document.activeElement.id;")
                d.js("const e = %s; e.focus(); e.select();" % E(i + "Num"))
                d.text(str(a)); d.press("Enter"); time.sleep(0.05)
                c = float(drive.dial_state(d, i)["box"])
                d.js("const e = %s; e.focus(); e.select();" % E(i + "Num")); d.text(s0["box"]); d.press("Enter"); time.sleep(0.05)
                e = drive.dial_state(d, i)
                if foc != i + "Num":
                    good = False; why.append("a tap on the box did not put the cursor in it (focus on %s)" % foc)
                if abs(c - a) > 1e-9 or e["box"] != s0["box"]:
                    good = False; why.append("typed %s gave %s, typed back gave %s" % (a, c, e["box"]))
                m = d.js("const n = %s, u = %s, w = %s, r = x => { const b = x.getBoundingClientRect(); return [Math.round(b.width), Math.round(b.height)]; }; return [r(n), r(u), r(w), n.scrollWidth <= n.clientWidth, getComputedStyle(n).fontSize];" % (E(i + "Num"), up, down))
                rows.append([i, tag, m])
                if not m[3]:
                    good = False; why.append("the number does not fit its box")
                ok("phone dial %s [%s] '%s': tap up %s, tap down %s, toggle %s -> %s, typed %s; box %s, arrows %s %s" % (i, tag, (s0["label"] or "").strip()[:36], a, b, s0["toggle"], t1, c, m[0], m[1], m[2]), good, "; ".join(why))
            except Exception as ex:
                ok("phone dial %s [%s] could be driven" % (i, tag), False, repr(ex)[:300])

    sweep("Mandelbrot")
    setsel(d, "col-solid", 1); sweep("trap solid"); setsel(d, "col-solid", 0)
    d.js("document.getElementById('mode-j').click(); await new Promise(r => setTimeout(r, 400));"); sweep("Julia")
    d.js("document.getElementById('mode-k').click(); await new Promise(r => setTimeout(r, 400));"); sweep("Kleinian")
    small = [r for r in rows if min(r[2][1]) < 40 or min(r[2][2]) < 40]
    info("phone: %d dials driven; arrow buttons smaller than 40 px in either direction: %s" % (len(rows), json.dumps(small[:6])))
    info("phone: sizes of the first dial's parts [box, up, down, fits, font]:", rows[0] if rows else None)
    d.js("document.getElementById('col-reachNum') && document.getElementById('mode-m').click(); await new Promise(r => setTimeout(r, 400)); document.getElementById('col-reachNum').closest('.dial').scrollIntoView({block: 'center'}); await new Promise(r => setTimeout(r, 200));")
    d.shot("phone-colour-dials.png")
    over = d.js("return document.documentElement.scrollWidth - document.documentElement.clientWidth;")
    ok("phone: the page does not scroll sideways", over <= 0, over)
    d.js("window.squaringLab.resetAll();"); d.idle(300)
    drive.finish(page, proc, prof, "phone")


TESTS = {"new": t_new, "thick": t_thick, "resets": t_resets, "ex": t_ex, "phone": t_phone}

if __name__ == "__main__":
    for stream in (sys.stdout, sys.stderr):
        try: stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception: pass
    print("page %s, started %s" % (drive.URL, time.strftime("%H:%M:%S")), flush=True)
    for name in sys.argv[1:]:
        print("===== " + name, flush=True)
        before = len(drive.results)
        try:
            TESTS[name]()
        except Exception as ex:
            import traceback
            traceback.print_exc()
            ok("%s ran to its end" % name, False, repr(ex)[:400])
        part = drive.results[before:]
        print("%s: %d passed, %d failed" % (name, part.count(True), part.count(False)), flush=True)
    print("%d passed, %d failed" % (drive.results.count(True), drive.results.count(False)), flush=True)
    print("ended", time.strftime("%H:%M:%S"), flush=True)

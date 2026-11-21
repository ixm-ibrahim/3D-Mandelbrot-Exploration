"""Engineer "dial", fix pass 7: the two defects reproduced with real input, on any build.

  python out/r7/dial/repro.py dist/v6.html before        # the faults as the testers found them
  python out/r7/dial/repro.py dist/r7-dial.html after    # the same steps on the fixed page

Parts: c1 (controls-1, desktop 1400x950, real clicks), l3 (layout-3, 375x812 touch phone and 1400x950 desktop).
A third argument limits the run to one part. Pictures: out/r7/dial/<tag>-*.png. Lines start with pass / FAIL / info.
"""
import json, os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, "out", "t6", "controls"))
import drive  # noqa: E402  the controls tester's driver: real mouse, keys and touch through the DevTools protocol

drive.URL = sys.argv[1] if len(sys.argv) > 1 else "dist/v6.html"
TAG = sys.argv[2] if len(sys.argv) > 2 else "run"
ONLY = sys.argv[3] if len(sys.argv) > 3 else ""
drive.HERE = HERE                      # pictures land here, not in the tester's folder
ok, info, E, L = drive.ok, drive.info, drive.E, drive.L


def toggles(d):
    return d.js("const o = {}; for (const b of document.querySelectorAll('.dial-mode')) o[b.id] = b.textContent + '|' + b.getAttribute('aria-pressed'); return o;")


def c1():
    page, proc, prof = drive.launch()
    d = drive.Drive(page)
    d.load()
    drive.open_all(d)
    d.click(E("qUltra"))
    open0 = toggles(d)
    info("step toggles on the page: %d" % len(open0))
    # --- the tester's reproduction, with real clicks
    t0 = d.js("return document.getElementById('powStep').textContent;")
    d.click(E("powStep"))
    t1 = d.js("return document.getElementById('powStep').textContent;")
    d.click("document.querySelector('#secEq .dial-reset')"); time.sleep(0.3)
    t2 = d.js("const b = document.getElementById('powStep'); return [b.textContent, b.getAttribute('aria-pressed'), b.title];")
    up = "document.getElementById('powNum').closest('.dial').querySelector('.dial-up')"
    d.click(up)
    n = d.js("return %s.S.n;" % L)
    tip = d.js("return %s.title;" % up)
    info("controls-1: toggle of Power n: opening %s, after a click %s, after Reset this section %s; then the up arrow gives %s (arrow tooltip: %s)" % (t0, t1, t2, n, tip))
    ok("controls-1: after Reset this section the toggle of Power n reads as it opened (%s) and is not pressed" % t0, t2[0] == t0 and t2[1] == "false", t2)
    ok("controls-1: the up arrow then takes the power from 2 to 2.1", n == 2.1, n)
    d.click("document.querySelector('#secEq .dial-reset')"); time.sleep(0.2)
    # --- a dial that opens on whole numbers (Field of view, step 1): its reset must bring +-1 back
    f0 = d.js("return document.getElementById('viewFovStep').textContent;")
    d.click(E("viewFovStep"))
    f1 = d.js("return document.getElementById('viewFovStep').textContent;")
    d.click("document.querySelector('#secView .dial-reset')"); time.sleep(0.3)
    f2 = d.js("const b = document.getElementById('viewFovStep'); return [b.textContent, b.getAttribute('aria-pressed')];")
    info("Field of view toggle: opening %s, after a click %s, after Reset this section %s" % (f0, f1, f2))
    ok("a dial that opens on whole steps (Field of view) is back on %s and pressed after its section's reset" % f0, f2 == [f0, "true"], f2)
    # --- every toggle, flipped by its own click handler, then Reset everything
    flipped = d.js("let k = 0; for (const b of document.querySelectorAll('.dial-mode')) { b.click(); k++; } return k;")
    mid = toggles(d)
    still = [k for k in open0 if mid.get(k) == open0[k]]
    d.retype(E("meshMmNum"), "150")      # a value of a file panel, to see what Reset everything does with that panel
    d.click(E("resetAll")); time.sleep(0.6)
    end = toggles(d)
    mm = d.js("return document.getElementById('meshMmNum').value;")
    d.click("document.querySelector('#secMesh .dial-reset')"); time.sleep(0.3)
    mm2 = d.js("return [document.getElementById('meshMmNum').value, document.getElementById('meshMmStep').textContent, document.getElementById('meshOffsetStep').textContent];")
    info("Save a 3D model, Longest side typed 150: after Reset everything it reads %s; after that panel's own Reset this section [value, its toggle, the offset's toggle] = %s" % (mm, mm2))
    panels = d.js("return [...document.querySelectorAll('#secExport .dial-mode, #secMesh .dial-mode')].map(b => b.id);")
    wrong = {k: (open0[k], end.get(k)) for k in open0 if end.get(k) != open0[k] and k not in panels}
    kept = [k for k in panels if end.get(k) != open0[k]]
    info("Reset everything: %d toggles flipped (%d did not change when clicked), %d of the picture's sections differ from the opening state afterwards: %s" % (flipped, len(still), len(wrong), sorted(wrong)))
    info("Reset everything leaves the two file panels as they are (their values too): toggles still flipped there: %s" % kept)
    ok("Reset everything puts back every step toggle of the sections it resets (%d of %d toggles)" % (len(open0) - len(panels), len(open0)), not wrong and not still, {"wrong": len(wrong), "unflipped": still})
    # --- each section's own button puts back its own toggles and no others
    secs = d.js("return [...document.querySelectorAll('#sections > details.sec')].filter(s => s.querySelector('.dial-reset')).map(s => s.id);")
    bad = {}
    # the sections on show in Mandelbrot mode first, then the Julia and the Kleinian panel in their own modes
    for sec in [x for x in secs if x not in ("juliaPanel", "kleinPanel")] + ["juliaPanel", "kleinPanel"]:
        if sec in ("juliaPanel", "kleinPanel") and not d.js("return document.querySelector('#%s .dial-reset').checkVisibility();" % sec):
            d.js("document.getElementById('mode-%s').click(); await new Promise(r => setTimeout(r, 400));" % sec[0])
        vis = d.js("const b = document.querySelector('#%s .dial-reset'); return !!b && b.checkVisibility();" % sec)
        if not vis:
            continue
        d.js("for (const b of document.querySelectorAll('.dial-mode')) b.click();")
        before = toggles(d)
        d.click("document.querySelector('#%s .dial-reset')" % sec); time.sleep(0.3)
        after = toggles(d)
        own = d.js("return [...document.querySelectorAll('#%s .dial-mode')].map(b => b.id);" % sec)
        back = [k for k in own if after.get(k) == open0.get(k)]
        notback = [k for k in own if after.get(k) != open0.get(k)]
        foreign = [k for k in after if k not in own and after[k] != before.get(k)]
        info("section %s: %d toggles of its own, %d back, %d not back, %d of other sections changed" % (sec, len(own), len(back), len(notback), len(foreign)))
        if notback or foreign:
            bad[sec] = {"notback": notback, "foreign": foreign}
        # put the rest back for the next round: flip the ones still away from their opening step
        d.js("const o = %s; for (const b of document.querySelectorAll('.dial-mode')) if (o[b.id] !== b.textContent + '|' + b.getAttribute('aria-pressed')) b.click();" % json.dumps(open0, ensure_ascii=False))
    ok("each section's reset puts back its own toggles and leaves the others alone (the sections of Mandelbrot mode, then the Julia and the Kleinian panel)", not bad, bad)
    d.js("document.getElementById('mode-m').click(); await new Promise(r => setTimeout(r, 400));")
    d.js("document.getElementById('secEq').scrollIntoView({block: 'center'});")
    d.click(E("powStep")); time.sleep(0.2)
    d.shot("%s-c1-power-toggled.png" % TAG, "#powHost")
    d.click("document.querySelector('#secEq .dial-reset')"); time.sleep(0.3)
    d.shot("%s-c1-power-after-reset.png" % TAG, "#powHost")
    d.idle(240)
    drive.finish(page, proc, prof, "c1")


BOXES = ("return [...document.querySelectorAll('.dial .num')].filter(n => n.closest('.dial').checkVisibility()).map(n => { const h = n.closest('.dial').parentElement.getBoundingClientRect(), b = n.closest('.dial-box').getBoundingClientRect();"
         " return [n.id, n.value, n.scrollWidth, n.clientWidth, Math.round(n.getBoundingClientRect().width * 10) / 10, b.left >= h.left - 0.5 && b.right <= h.right + 0.5]; });")
ONE = ("const e = document.getElementById('%sNum'), b = e.closest('.dial-box').getBoundingClientRect(), h = e.closest('.dial').getBoundingClientRect();"
       " return [e.value, e.scrollWidth, e.clientWidth, b.left >= h.left - 0.5 && b.right <= h.right + 0.5];")


def l3_one(w, h, phone, theme):
    tag = "%s-l3-%d%s" % (TAG, w, "t" if phone else "")
    page, proc, prof = drive.launch(w, h, mobile=phone, touch=phone, theme=theme)
    d = drive.Drive(page)
    d.load()
    coarse = d.js("return matchMedia('(pointer: coarse)').matches;")
    info("%dx%d, pointer coarse: %s, theme %s" % (w, h, coarse, theme))
    # --- the tester's reproduction
    d.js("document.getElementById('mode-k').click(); document.querySelectorAll('#sections > details.sec').forEach(s => { s.open = true; });"
         "const x = document.getElementById('extreme'); if (!x.checked) x.click();"
         "const s = document.getElementById('kleinPreset'); const o = [...s.options].find(o => o.text.startsWith('Leaning 30° with the third map, sphere moved across and in depth')) || [...s.options].sort((a, b) => b.text.length - a.text.length)[0];"
         "s.value = o.value; s.dispatchEvent(new Event('change', { bubbles: true })); await new Promise(r => setTimeout(r, 300));")
    r = d.js("const e = document.getElementById('kmyNum'), cs = getComputedStyle(e); return [e.value, e.scrollWidth, e.clientWidth, Math.round(e.getBoundingClientRect().width * 10) / 10, cs.fontSize, cs.fontFamily.slice(0, 30), document.fonts.check(cs.fontSize + ' ' + cs.fontFamily.split(',')[0])];")
    info("layout-3: kmyNum [value, scrollWidth, clientWidth, width, font size, font, first font loaded] = %s" % json.dumps(r, ensure_ascii=False))
    ok("layout-3 (%d wide): the whole number %s shows in its box" % (w, r[0]), r[1] <= r[2], r[:3])
    d.shot("%s-kmy.png" % tag, "#kmyNum")
    d.js("document.getElementById('kmyNum').closest('.dial').scrollIntoView({block: 'start'}); window.scrollBy(0, -140);"); time.sleep(0.25)
    d.shot("%s-klein-dials.png" % tag)
    # --- every Kleinian and Julia entry of the lists: is any number cut, does any dial stick out of its column?
    worst = {}
    count = 0
    for mode, sel in (("k", "kleinPreset"), ("j", "juliaPreset")):
        d.js("document.getElementById('mode-%s').click(); await new Promise(r => setTimeout(r, 250));" % mode)
        n = d.js("return document.getElementById('%s').options.length;" % sel)
        for i in range(n):
            d.js("const s = document.getElementById('%s'); s.selectedIndex = %d; s.dispatchEvent(new Event('change', { bubbles: true })); await new Promise(r => setTimeout(r, 60));" % (sel, i))
            count += 1
            for row in d.js(BOXES):
                if row[2] > row[3] or not row[5]:
                    worst.setdefault(row[0], []).append(row[1:] + [mode, i])
    info("%d wide: %d list entries tried; typed boxes too small or sticking out: %s" % (w, count, json.dumps({k: [len(v)] + v[:2] for k, v in worst.items()}, ensure_ascii=False)))
    ok("%d wide: in all %d list entries every typed number shows whole and no box cluster sticks out of its column" % (w, count), not worst, {k: len(v) for k, v in worst.items()})
    # --- longer numbers than any list entry holds: a minus sign and six decimals, two digits before the point, and the 1e-7 form
    d.js("document.getElementById('mode-k').click(); await new Promise(r => setTimeout(r, 250));")
    longs = {}
    for val in ("-1.732051", "-0.123456", "1.234567", "0.5"):
        d.js("const L = window.squaringLab; L.S.k.mx = %s; L.syncControls(); await new Promise(r => setTimeout(r, 60));" % val)
        longs[val] = d.js(ONE % "kmx")
        if val == "-1.732051":
            d.shot("%s-kmx-minus.png" % tag, "#kmxNum")
    d.js("const L = window.squaringLab; document.getElementById('mode-j').click(); L.S.c[0] = -12.345678; L.S.c[1] = 1.5e-7; L.syncControls(); await new Promise(r => setTimeout(r, 250));")
    for i in ("cx", "cy"):
        longs[i] = d.js(ONE % i)
    d.js("document.getElementById('cxNum').closest('.dial').scrollIntoView({block: 'start'}); window.scrollBy(0, -140);"); time.sleep(0.25)
    d.shot("%s-julia-long.png" % tag)
    info("%d wide, long numbers [value, scrollWidth, clientWidth, cluster inside its dial]: %s" % (w, json.dumps(longs, ensure_ascii=False)))
    cut = {k: v for k, v in longs.items() if v[1] > v[2] or not v[3]}
    ok("%d wide: numbers with a minus sign and six decimals, -12.345678 and 1.5e-7 show whole" % w, not cut, cut)
    d.js("document.getElementById('mode-m').click(); await new Promise(r => setTimeout(r, 300));")
    rows, tight = 0, {}
    for ap in ("lathe", "bulb", "classic", "split", "mercator"):
        d.js("document.getElementById('ap-%s').click(); await new Promise(r => setTimeout(r, 350));" % ap)
        for row in d.js(BOXES):
            rows += 1
            if row[2] > row[3] or not row[5]:
                tight[row[0]] = row[1:]
    info("%d wide, Mandelbrot with each of five approaches, extreme ranges on: %d typed boxes looked at; too small or sticking out: %s" % (w, rows, json.dumps(tight, ensure_ascii=False)))
    ok("%d wide: every typed box of the Mandelbrot controls holds its number, in each approach" % w, not tight, tight)
    d.js("const L = window.squaringLab; L.S.param.mercator.lift = -1.234567; L.syncControls(); await new Promise(r => setTimeout(r, 80));")
    lift = d.js(ONE % "par-mercator-lift")
    info("%d wide, the fullest cluster on the page (Lift: play, toggle, wide tag, box) with -1.234567: %s" % (w, json.dumps(lift)))
    ok("%d wide: Lift with -1.234567 shows whole and its cluster stays inside its card" % w, lift[1] <= lift[2] and lift[3], lift)
    d.js("document.getElementById('par-mercator-liftNum').closest('.dial').scrollIntoView({block: 'center'});"); time.sleep(0.25)
    d.shot("%s-lift-long.png" % tag, "#secApproach .dial:has(#par-mercator-liftNum)")
    over = d.js("return document.documentElement.scrollWidth - document.documentElement.clientWidth;")
    ok("%d wide: the page does not scroll sideways" % w, over <= 0, over)
    d.js("window.squaringLab.resetAll();")
    d.idle(240)
    drive.finish(page, proc, prof, "l3 %d" % w)


def l3():
    l3_one(375, 812, True, "light")
    l3_one(1400, 950, False, "dark")


def ex():
    """The two number boxes the controls tester did not reach (typed picture size), with the tester's own sweep."""
    page, proc, prof = drive.launch()
    d = drive.Drive(page)
    d.load()
    drive.open_all(d)
    d.js("const s = document.getElementById('exportSize'); s.value = [...s.options].find(o => o.text.startsWith('Typed')).value; s.dispatchEvent(new Event('change', { bubbles: true })); await new Promise(r => setTimeout(r, 200));")
    vis = [i for i in drive.visible_dials(d) if i in ("exportW", "exportH")]
    ok("the typed width and height boxes show when 'Typed width and height' is chosen", vis == ["exportW", "exportH"], vis)
    drive.sweep(d, vis, "typed picture size", set())
    d.retype(E("exportWNum"), "99999")
    a = d.js("return document.getElementById('exportWNum').value;")
    d.retype(E("exportWNum"), "2.6")
    b = d.js("return document.getElementById('exportWNum').value;")
    d.retype(E("exportWNum"), "1920")
    ok("Width, pixels: typed 99999 is held at 8192, typed 2.6 becomes 16 (the lowest), 1920 goes back in", (a, b) == ("8192", "16"), (a, b))
    d.js("document.getElementById('exportWNum').closest('.dial').scrollIntoView({block: 'center'});"); time.sleep(0.2)
    d.shot("%s-ex-typed-size.png" % TAG, "#secExport .export-typed")
    d.click("document.querySelector('#secExport .dial-reset')"); time.sleep(0.3)
    drive.finish(page, proc, prof, "ex")


if __name__ == "__main__":
    for stream in (sys.stdout, sys.stderr):
        try: stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception: pass
    print("page %s, started %s" % (drive.URL, time.strftime("%H:%M:%S")), flush=True)
    for name, f in (("c1", c1), ("l3", l3), ("ex", ex)):
        if ONLY and ONLY != name:
            continue
        print("===== " + name, flush=True)
        try:
            f()
        except Exception as ex:
            import traceback
            traceback.print_exc()
            ok("%s ran to its end" % name, False, repr(ex)[:400])
    print("%d passed, %d failed" % (drive.results.count(True), drive.results.count(False)), flush=True)
    print("ended", time.strftime("%H:%M:%S"), flush=True)

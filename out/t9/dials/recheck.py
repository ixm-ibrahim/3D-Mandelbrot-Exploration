"""Tester "dials", second check: the two defects of the first check, each with its own reproduction and real input.

  python out/t9/dials/recheck.py <page> <tag> [c1|l3]

c1 = controls-1 (desktop 1400x950, real clicks); l3 = layout-3 (375x812 touch phone, both themes; then 1400 and 1024).
Pictures: out/t9/dials/<tag>-*.png. Lines start with pass / FAIL / info.
"""
import json, os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, "out", "t6", "controls"))
import drive  # noqa: E402  the first tester's driver (real mouse, keys, touch through the DevTools protocol)

drive.URL = sys.argv[1] if len(sys.argv) > 1 else "dist/v8.html"
TAG = sys.argv[2] if len(sys.argv) > 2 else "v8"
ONLY = sys.argv[3] if len(sys.argv) > 3 else ""
drive.HERE = HERE
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
    # the first check's reproduction, with real clicks
    t0 = d.js("return document.getElementById('powStep').textContent;")
    d.click(E("powStep"))
    t1 = d.js("return document.getElementById('powStep').textContent;")
    d.shot("%s-c1-power-toggled.png" % TAG, "#powHost")
    d.click("document.querySelector('#secEq .dial-reset')"); time.sleep(0.3)
    t2 = d.js("const b = document.getElementById('powStep'); return [b.textContent, b.getAttribute('aria-pressed'), b.title];")
    d.shot("%s-c1-power-after-reset.png" % TAG, "#powHost")
    up = "document.getElementById('powNum').closest('.dial').querySelector('.dial-up')"
    d.click(up)
    n = d.js("return %s.S.n;" % L)
    info("controls-1: toggle of Power n: opening %s, after a click %s, after Reset this section %s; then the up arrow gives %s" % (t0, t1, t2, n))
    ok("controls-1: after Reset this section the toggle of Power n reads as it opened (%s), not pressed" % t0, t2[0] == t0 and t2[1] == "false", t2)
    ok("controls-1: the up arrow then takes the power from 2 to 2.1", n == 2.1, n)
    d.click("document.querySelector('#secEq .dial-reset')"); time.sleep(0.2)
    # every toggle flipped with a real click where it shows, then each section's own reset
    secs = d.js("return [...document.querySelectorAll('#sections > details.sec')].filter(s => s.querySelector('.dial-reset')).map(s => s.id);")
    info("sections with a reset button: %s" % secs)
    bad, rows = {}, []
    for sec in [x for x in secs if x not in ("juliaPanel", "kleinPanel")] + ["juliaPanel", "kleinPanel"]:
        if sec in ("juliaPanel", "kleinPanel"):
            d.js("document.getElementById('mode-%s').click(); await new Promise(r => setTimeout(r, 500));" % sec[0])
        vis = d.js("const b = document.querySelector('#%s .dial-reset'); return !!b && b.checkVisibility();" % sec)
        if not vis:
            info("section %s: reset button not on show" % sec); continue
        d.js("for (const b of document.querySelectorAll('.dial-mode')) b.click();")
        before = toggles(d)
        d.click("document.querySelector('#%s .dial-reset')" % sec); time.sleep(0.3)
        after = toggles(d)
        own = d.js("return [...document.querySelectorAll('#%s .dial-mode')].map(b => b.id);" % sec)
        notback = [k for k in own if after.get(k) != open0.get(k)]
        foreign = [k for k in after if k not in own and after[k] != before.get(k)]
        rows.append("%s %d own, %d not back, %d foreign" % (sec, len(own), len(notback), len(foreign)))
        if notback or foreign:
            bad[sec] = {"notback": notback, "foreign": foreign}
        d.js("const o = %s; for (const b of document.querySelectorAll('.dial-mode')) if (o[b.id] !== b.textContent + '|' + b.getAttribute('aria-pressed')) b.click();" % json.dumps(open0, ensure_ascii=False))
    info("per section: " + "; ".join(rows))
    ok("each section's reset puts back its own step toggles and no others", not bad, bad)
    # Reset everything with every toggle flipped
    d.js("document.getElementById('mode-m').click(); await new Promise(r => setTimeout(r, 400));")
    flipped = d.js("let k = 0; for (const b of document.querySelectorAll('.dial-mode')) { b.click(); k++; } return k;")
    d.click(E("resetAll")); time.sleep(0.6)
    end = toggles(d)
    wrong = {k: (open0[k], end.get(k)) for k in open0 if end.get(k) != open0[k]}
    info("Reset everything: %d toggles flipped; still away from the opening step afterwards: %s" % (flipped, json.dumps(wrong, ensure_ascii=False)))
    ok("Reset everything puts back every step toggle of the page (%d)" % len(open0), not wrong, wrong)
    d.idle(240)
    drive.finish(page, proc, prof, "c1")


BOXES = ("return [...document.querySelectorAll('.dial .num')].filter(n => n.closest('.dial').checkVisibility()).map(n => { const h = n.closest('.dial').parentElement.getBoundingClientRect(), b = n.closest('.dial-box').getBoundingClientRect();"
         " return [n.id, n.value, n.scrollWidth, n.clientWidth, Math.round(n.getBoundingClientRect().width * 10) / 10, b.left >= h.left - 0.5 && b.right <= h.right + 0.5]; });")


def l3_one(w, h, phone, theme):
    tag = "%s-l3-%d%s-%s" % (TAG, w, "t" if phone else "", theme)
    page, proc, prof = drive.launch(w, h, mobile=phone, touch=phone, theme=theme)
    d = drive.Drive(page)
    d.load()
    coarse = d.js("return matchMedia('(pointer: coarse)').matches;")
    info("%dx%d, pointer coarse: %s, theme %s" % (w, h, coarse, theme))
    d.js("document.getElementById('mode-k').click(); document.querySelectorAll('#sections > details.sec').forEach(s => { s.open = true; });"
         "const x = document.getElementById('extreme'); if (!x.checked) x.click(); await new Promise(r => setTimeout(r, 300));")
    names = d.js("return [...document.getElementById('kleinPreset').options].map(o => o.text);")
    lean = [i for i, n in enumerate(names) if n.startswith("Leaning 30")]
    info("Kleinian list: %d entries; the ones named 'Leaning 30...': %s" % (len(names), json.dumps([[i, names[i]] for i in lean], ensure_ascii=False)))
    hit = None
    for i in lean:
        d.js("const s = document.getElementById('kleinPreset'); s.selectedIndex = %d; s.dispatchEvent(new Event('change', { bubbles: true })); await new Promise(r => setTimeout(r, 250));" % i)
        r = d.js("const e = document.getElementById('kmyNum'), cs = getComputedStyle(e); return [e.value, e.scrollWidth, e.clientWidth, Math.round(e.getBoundingClientRect().width * 10) / 10, cs.fontSize];")
        info("layout-3: entry %d '%s': kmyNum [value, scrollWidth, clientWidth, width, font size] = %s" % (i, names[i], json.dumps(r)))
        if r[0] == "1.732051":
            ok("layout-3 (%d wide, %s): the whole number %s shows in its box (entry '%s')" % (w, theme, r[0], names[i]), r[1] <= r[2], r[:3])
            if hit is None:
                hit = i
                d.shot("%s-kmy.png" % tag, "#kmyNum")
                d.js("document.getElementById('kmyNum').closest('.dial').scrollIntoView({block: 'start'}); window.scrollBy(0, -140);"); time.sleep(0.25)
                d.shot("%s-klein-dials.png" % tag)
    ok("layout-3 (%d wide): an entry with the value 1.732051 was found to test" % w, hit is not None, lean)
    # every Kleinian and Julia entry of the lists: is any number cut, does any dial stick out of its column?
    worst, count = {}, 0
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
    ok("%d wide %s: in all %d list entries every typed number shows whole and no box cluster sticks out of its column" % (w, theme, count), not worst, {k: len(v) for k, v in worst.items()})
    # the Douady rabbit (the engineer found its minus sign clipped at 1400 too)
    d.js("document.getElementById('mode-j').click(); const e = document.getElementById('juliaPreset'); e.value = [...e.options].find(o => /rabbit/i.test(o.textContent)).value; e.dispatchEvent(new Event('change', { bubbles: true })); await new Promise(r => setTimeout(r, 300));")
    rb = d.js("return ['cx', 'cy', 'cz'].map(i => { const e = document.getElementById(i + 'Num'); return [e.value, e.scrollWidth, e.clientWidth]; });")
    info("%d wide: Douady rabbit c boxes [value, scrollWidth, clientWidth]: %s" % (w, json.dumps(rb)))
    ok("%d wide %s: the Douady rabbit's c values show whole" % (w, theme), all(r[1] <= r[2] for r in rb), rb)
    d.js("document.getElementById('cxNum').closest('.dial').scrollIntoView({block: 'start'}); window.scrollBy(0, -140);"); time.sleep(0.25)
    d.shot("%s-rabbit.png" % tag)
    over = d.js("return document.documentElement.scrollWidth - document.documentElement.clientWidth;")
    ok("%d wide: the page does not scroll sideways" % w, over <= 0, over)
    d.js("window.squaringLab.resetAll();")
    d.idle(240)
    drive.finish(page, proc, prof, "l3 %d %s" % (w, theme))


def l3():
    l3_one(375, 812, True, "light")
    l3_one(375, 812, True, "dark")
    l3_one(1400, 950, False, "dark")


if __name__ == "__main__":
    for stream in (sys.stdout, sys.stderr):
        try: stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception: pass
    print("page %s, started %s" % (drive.URL, time.strftime("%H:%M:%S")), flush=True)
    for name, f in (("c1", c1), ("l3", l3)):
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

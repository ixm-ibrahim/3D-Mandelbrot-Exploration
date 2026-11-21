"""Checker: follow-up questions left by the first runs."""
import sys, json, time
from drive import Session, show
URL = "dist/r13-check-page.html"
which = sys.argv[1:] or ["land", "phone", "desk", "base"]

RADIO = "return { checked: [...document.querySelectorAll('input[name=mode]')].filter(r => r.checked).map(r => r.id), learn: L.S.learn, mode: L.S.mode, cls: document.body.className };"

if "land" in which:
    with Session(URL, "667x375", "light", mobile=True, name="follow-667x375") as s:
        s.done()
        s.shot("follow-land-0-open.png")
        show("opening layout", s.js("return { main: rect(document.querySelector('.bench-main')), stage: rect($('stage')), toprow: [rect(document.querySelector('.toprow')), getComputedStyle(document.querySelector('.toprow')).position], cls: document.documentElement.className, sw: document.documentElement.scrollWidth };"))
        m = s.js("const e = document.querySelector('#mode-l + span'); e.scrollIntoView({ block: 'center', behavior: 'instant' }); await sleep(200); return mid(e);")
        s.tap(m[0], m[1]); time.sleep(0.3)
        show("after a tap on Learn", s.js(RADIO))
        s.js("go(0); await sleep(150);"); s.shot("follow-land-1-learn-top.png")
        show("Learn layout at the top of the page", s.js("return { y: scrollY, main: rect(document.querySelector('.bench-main')), stage: rect($('stage')), bar: rect($('learnBar')), ih: innerHeight };"))
        s.js("$('stage').scrollIntoView({ block: 'start', behavior: 'instant' }); await sleep(150);"); s.shot("follow-land-2-learn-stage.png")
        show("stage at the top of the window", s.js("return { y: Math.round(scrollY), stage: rect($('stage')), bar: rect($('learnBar')), toprow: rect(document.querySelector('.toprow')), ih: innerHeight };"))
        # touch on the picture, with the picture in view
        P = s.js("L.learn.goto(0, 0); const r = $('learnCanvas').getBoundingClientRect(), K = L.learn, q = K.proj.to(K.pts[2].z); return [r.left + q[0], r.top + q[1], K.proj.s, K.pts[2].z, Math.round(scrollY)];")
        s.tdrag(P[0], P[1], P[0] + 40, P[1] - 20, 6); time.sleep(0.2)
        show("ring dragged by touch (z before, z after, scrollY before, after)", s.js("return [%s, L.learn.pts[2].z, %d, Math.round(scrollY)];" % (json.dumps(P[3]), P[4])))
        # back to Mandelbrot by tap
        m = s.js("const e = document.querySelector('#mode-m + span'); e.scrollIntoView({ block: 'center', behavior: 'instant' }); await sleep(200); const p = mid(e), t = document.elementFromPoint(p[0], p[1]); return [p[0], p[1], t ? (t.id || t.className || t.tagName) + ':' + t.textContent.slice(0, 20) : null];")
        show("before the tap on Mandelbrot", [m, s.js(RADIO)])
        s.shot("follow-land-3-before-tap.png")
        s.tap(m[0], m[1]); time.sleep(0.4)
        show("after the tap on Mandelbrot", s.js(RADIO))
        s.done(); s.js("go(0); await sleep(100);"); s.shot("follow-land-4-after.png")

if "phone" in which:
    with Session(URL, "375x667", "light", mobile=True, name="follow-375x667") as s:
        s.done()
        m = s.js("const e = document.querySelector('#mode-l + span'); e.scrollIntoView({ block: 'center', behavior: 'instant' }); await sleep(200); return mid(e);")
        s.tap(m[0], m[1]); time.sleep(0.3)
        s.js("$('learnPanel').scrollIntoView({ block: 'start', behavior: 'instant' }); await sleep(200);")
        # the diamond, with fresh coordinates
        P = s.js("L.learn.goto(0, 0); const r = $('learnCanvas').getBoundingClientRect(), K = L.learn, c = K.proj.to(K.pts[2].c); return [r.left + c[0], r.top + c[1], K.proj.s, K.pts[2].c];")
        s.tdrag(P[0] + 8, P[1] - 6, P[0] - 22, P[1] + 4, 6); time.sleep(0.2)
        show("diamond dragged by touch 10 px off its centre (c before, c after, scale)", [P[3], s.js("return L.learn.pts[2].c;"), P[2]])
        # the three spaces as they open, mid-turn: does the Unpin button sit on a label?
        for sp, extra in ((1, ""), (2, ""), (2, "L.learn.set({ hidden: true });"), (3, "")):
            s.js("L.learn.set({ space: %d, z: null }); %s L.learn.goto(0, 0.5); await sleep(150);" % (sp, extra))
            s.shot("follow-phone-space%d%s.png" % (sp, "-tipped" if extra else ""))
        s.js("L.learn.set({ space: 1 }); L.learn.goto(0, 0.5); await sleep(100);")
        # every approach in 3D on the phone, mid second move
        for aid in ("mercator", "tilt", "bulb", "split", "pillow"):
            s.js("L.learn.set({ space: 3 }); $('ap-%s').click(); await sleep(120); L.learn.goto(1, 0.6); await sleep(100);" % aid)
            s.shot("follow-phone-3d-%s.png" % aid)
        # the radio of Show after settings change under Learn
        out = {}
        out["start"] = s.js(RADIO)
        s.js("type('pow', 3); await sleep(150);"); out["after the power dial"] = s.js(RADIO)
        fz = s.js("const lab = [...document.querySelectorAll('#secMod label')].find(l => l.textContent.trim() === 'flip z'); const inp = lab.querySelector('input') || $(lab.htmlFor); $('secMod').open = true; inp.click(); await sleep(150); return inp.id;")
        out["after flip z"] = s.js(RADIO)
        s.js("const b = $('secEq').querySelector('.dial-reset'); b.click(); await sleep(150);"); out["after Reset this section in Equation"] = s.js(RADIO)
        s.js("const b = $('extreme'); b.click(); await sleep(150);"); out["after Extreme ranges"] = s.js(RADIO)
        s.js("const b = $('collapseAll'); b.click(); await sleep(150); b.click(); await sleep(100);"); out["after Collapse all twice"] = s.js(RADIO)
        s.js("const b = [...document.querySelectorAll('#secMod button')]; for (const x of b) { x.click(); await sleep(80); }"); out["after every button in Modifiers (%s)" % s.js("return [...document.querySelectorAll('#secMod button')].map(b => b.textContent.trim()).join(' / ');")] = s.js(RADIO)
        s.js("const b = [...document.querySelectorAll('#secApproach .rule.is-on button')].filter(vis); for (const x of b) { x.click(); await sleep(80); } return b.map(x => x.textContent.trim());"); out["after the buttons of the chosen approach"] = s.js(RADIO)
        for k, v in out.items(): show(k, v)
        # the Show list, by its own options
        opts = s.js("return [...$('learn-show').options].map(o => [o.value, o.text]);"); show("options of Show", opts)
        for i in range(len(opts)):
            r = s.js("const e = $('learn-show'); e.selectedIndex = %d; e.dispatchEvent(new Event('change', { bubbles: true })); L.learn.set({ space: 3 }); L.learn.goto(0, 0.5); await sleep(120); return [L.learn.show, L.learn.cache.comp[0].length, L.learn.cache.follow];" % i)
            show("Show option %d" % i, r)
            s.shot("follow-phone-show-%d.png" % i)
        s.js("L.learn.set({ space: 2 }); L.learn.goto(0, 0.5); await sleep(120);"); s.shot("follow-phone-show-all-2d.png")
        s.js("L.learn.set({ space: 1 }); L.learn.goto(0, 0.5); await sleep(120);"); s.shot("follow-phone-show-all-1d.png")

if "desk" in which:
    with Session(URL, "1400x950", "dark", name="follow-desktop-dark") as s:
        s.done(); s.shot("follow-desk-dark-0-open.png")
        s.js("$('mode-l').click(); await sleep(200); L.learn.goto(0, 0.5); await sleep(100);"); s.shot("follow-desk-dark-1-2d.png")
        s.js("L.learn.set({ space: 3, show: 'all' }); $('ap-lathe').click(); await sleep(150); L.learn.goto(0, 0.6); await sleep(100);"); s.shot("follow-desk-dark-2-3d-lathe-all.png")
        s.js("L.learn.set({ space: 1 }); L.learn.goto(0, 0.5); await sleep(100);"); s.shot("follow-desk-dark-3-1d.png")
        s.js("$('learnNotice').scrollIntoView({ block: 'center', behavior: 'instant' }); await sleep(150);"); s.shot("follow-desk-dark-4-panel-end.png")

if "base" in which:
    for name, url in (("v13t", "dist/v13t.html"), ("check", URL)):
        with Session(url, "1400x950", "light", name="base-" + name) as s:
            s.js("L.R.warmOn = false;"); s.done()
            show("opening state", s.js("return { status: $('status').textContent.trim(), probes: probes(), main: rect(document.querySelector('.bench-main')), stage: rect($('stage')), dials: rect(document.querySelector('.dials')), mode: rect(document.querySelector('fieldset.mode')), modes: [...document.querySelectorAll('fieldset.mode .seg')].map(e => rect(e).concat([e.textContent.trim()])), sections: [...document.querySelectorAll('#sections > details.sec')].map(d => [d.id, rect(d), d.hidden]), doc: document.documentElement.scrollHeight, htmlCls: document.documentElement.className, mainPos: getComputedStyle(document.querySelector('.bench-main')).position, mainTop: getComputedStyle(document.querySelector('.bench-main')).top };"))
            s.shot("base-%s-top.png" % name)
            s.js("go(900); await sleep(200);"); s.shot("base-%s-y900.png" % name)

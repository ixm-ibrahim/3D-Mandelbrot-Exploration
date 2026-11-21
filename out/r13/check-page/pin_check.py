"""Checker: the pinned picture at one narrow size. Usage: python out/r13/check-page/pin_check.py SIZE THEME [mobile]"""
import sys, json, time
from drive import Session, show

size, theme = sys.argv[1], sys.argv[2]
mobile = len(sys.argv) > 3 and sys.argv[3] == "mobile"
tag = "pin-%s-%s%s" % (size, theme, "-m" if mobile else "")
URL = "dist/r13-check-page.html"

SNAP = r"""
const main = document.querySelector('.bench-main'), st = $('stage'), top = document.querySelector('.toprow');
return { y: Math.round(scrollY), ih: innerHeight, sw: document.documentElement.scrollWidth, iw: innerWidth,
  pin: L.pin ? L.pin.state() : null, cls: document.documentElement.className,
  main: rect(main), mainPos: getComputedStyle(main).position, stage: rect(st), status: $('status').textContent.trim(),
  lastTouch: Math.round(L.R.lastTouch), cv: [$('view').width, $('view').height], toprow: rect(top), toprowPos: getComputedStyle(top).position,
  pinBtn: $('pinToggle') ? [rect($('pinToggle')), getComputedStyle($('pinToggle')).display, $('pinToggle').textContent] : null,
  hintBelow: $('hintBelow') ? getComputedStyle($('hintBelow')).display : null, pinHint: $('pinHint') ? [getComputedStyle($('pinHint')).display, $('pinHint').textContent.slice(0, 60)] : null,
  idle: L.idle() };
"""
# what is on top at 9 x 5 points of the pinned block: must all belong to .bench-main (opaque, nothing over it)
COVER = r"""
const main = document.querySelector('.bench-main'), r = main.getBoundingClientRect(), bad = [];
for (let i = 0; i < 9; i++) for (let j = 0; j < 5; j++) {
  const x = 2 + (innerWidth - 4) * i / 8, y = Math.max(1, r.top + 1) + (Math.min(r.bottom, innerHeight) - Math.max(1, r.top + 1) - 2) * j / 4;
  const e = document.elementFromPoint(x, y);
  if (!e || !(main.contains(e))) bad.push([Math.round(x), Math.round(y), e ? (e.id || e.className || e.tagName) : 'none']);
}
return { bg: getComputedStyle(main, '::before').backgroundColor, paper: getComputedStyle(document.documentElement).getPropertyValue('--paper').trim(), notMain: bad };
"""
# is the picture in view whenever a control of the controls column is in view? walk the whole page in steps
WALK = r"""
const main = document.querySelector('.bench-main'), st = $('stage'), ctl = [...document.querySelectorAll('.dials input, .dials select, .dials button, .dials summary')].filter(vis);
const out = [], max = document.documentElement.scrollHeight - innerHeight; let lost = [];
const t0 = L.R.lastTouch, s0 = $('status').textContent, c0 = $('view').width + 'x' + $('view').height;
for (let y = 0; y <= max; y += 60) {
  go(y); await sleep(20);
  const m = main.getBoundingClientRect(), s = st.getBoundingClientRect();
  const low = Math.max(0, Math.min(m.bottom, innerHeight));
  const inView = ctl.filter(e => { const r = e.getBoundingClientRect(); return r.bottom > (s.bottom > 0 && s.top < innerHeight ? Math.max(0, m.bottom) : 0) + 4 && r.top < innerHeight - 4; }).length;
  const stageIn = s.top >= -1 && s.bottom <= innerHeight + 1;
  if (inView && !stageIn) lost.push([y, inView, Math.round(s.top), Math.round(s.bottom)]);
}
const firstLost = lost[0], n = lost.length; lost = lost.slice(0, 4);
go(0); await sleep(50);
return { max, steps: Math.floor(max / 60) + 1, positionsWithAControlInViewButNotThePicture: n, first: lost,
  sameTouch: L.R.lastTouch === t0, sameStatus: $('status').textContent === s0, sameCanvas: $('view').width + 'x' + $('view').height === c0, status: $('status').textContent.trim() };
"""
ACTIVE = r"""
const e = document.activeElement, main = document.querySelector('.bench-main'), m = main.getBoundingClientRect();
if (!e || e === document.body) return null;
const r = e.getBoundingClientRect(), inD = !!e.closest('.dials'), held = getComputedStyle(main).position === 'sticky' && m.top <= 1 && scrollY > 2;
let what = (e.id || e.name || e.tagName) + '';
return [what, Math.round(r.top), Math.round(r.bottom), Math.round(m.bottom), innerHeight, inD, held, Math.round(scrollY)];
"""

def tabwalk(s, n, shift):
    seen, bad = [], []
    for i in range(n):
        s.key("Tab", shift=shift)
        time.sleep(0.03)
        a = s.js(ACTIVE)
        if not a: continue
        seen.append(a[0])
        what, top, bottom, mb, ih, inD, held, y = a
        if inD and ((held and top < mb - 1) or bottom > ih + 1 or top < -1):
            bad.append(a)
    return seen, bad

with Session(URL, size, theme, mobile=mobile, name=tag) as s:
    ok, t = s.done()
    show("first picture done", [ok, round(t, 1)])
    a = s.js(SNAP); show("top", a)
    s.shot("%s-1-top.png" % tag)
    pinned = bool(a["pin"] and a["pin"]["on"])
    fp0 = s.js("return probes();")

    # the row with Collapse all, at the top
    show("toprow at top", s.js("const t = document.querySelector('.toprow'); return [rect(t), getComputedStyle(t).position, getComputedStyle(t).top, [...t.querySelectorAll('button,input')].map(b => (b.textContent || b.id).trim())];"))

    # scrolled to the Approach section
    s.js("$('secApproach').scrollIntoView({ block: 'start', behavior: 'instant' }); await sleep(250);")
    b = s.js(SNAP); show("at Approach", b); show("cover at Approach", s.js(COVER))
    show("Approach summary box", s.js("return rect($('secApproach').querySelector('summary'));"))
    s.shot("%s-2-approach.png" % tag)

    # the last control
    s.js("const c = [...document.querySelectorAll('.dials input, .dials select, .dials button, .dials summary')].filter(vis); const e = c[c.length - 1]; window.__last = e; e.scrollIntoView({ block: 'center', behavior: 'instant' }); await sleep(250);")
    c = s.js(SNAP); show("at last control", c); show("cover at last control", s.js(COVER))
    show("last control", s.js("return [(window.__last.id || window.__last.textContent || '').trim().slice(0, 40), rect(window.__last)];"))
    s.shot("%s-3-last.png" % tag)

    # past the controls, into the text below
    s.js("const f = document.querySelector('footer.why'); f.scrollIntoView({ block: 'start', behavior: 'instant' }); window.scrollBy({ top: 500, behavior: 'instant' }); await sleep(250);")
    d = s.js(SNAP); show("in the closing text", d)
    s.shot("%s-4-text.png" % tag)
    show("scrolling left the solid alone (snapshots)", [a["lastTouch"] == d["lastTouch"], a["status"] == d["status"], a["cv"] == d["cv"]])

    # the whole page in steps of 60 px
    show("walk", s.js(WALK))

    # a dial moved while scrolled far down
    s.js("const e = $('pow'); window.__powBox = e; e.scrollIntoView({ block: 'center', behavior: 'instant' }); await sleep(250);")
    info = s.js("const e = $('pow'); return { type: e.type, box: rect(e), y: Math.round(scrollY), stage: rect($('stage')), n: L.S.n, range: (() => { const r = e.closest('.dial') ? e.closest('.dial').querySelector('input[type=range]') : null; return r ? [r.id, rect(r), r.min, r.max] : null; })() };")
    show("power dial before", info)
    s.shot("%s-5a-dial-before.png" % tag)
    if info.get("range"):
        r = info["range"][1]
        # a tap on the slider track at three quarters of its width
        s.tap(r[0] + (r[2] - r[0]) * 0.75, (r[1] + r[3]) / 2)
    else:
        s.js("type('pow', 3);")
    time.sleep(0.3)
    show("power after the tap", s.js("return [L.S.n, Math.round(scrollY)];"))
    ok, t = s.done();
    e = s.js(SNAP); show("after the dial", e)
    fp1 = s.js("return probes();")
    show("picture changed (49 probes differ)", [fp0 != fp1, sum(1 for x, y in zip(fp0, fp1) if x != y)])
    s.shot("%s-5b-dial-after.png" % tag)
    s.js("L.S.n = 2; L.syncControls(); L.touch();"); s.done()

    # Tab, with real key presses
    s.js("go(0); await sleep(100); const f = document.querySelector('.bench-main button, .bench-main input'); if (f) f.focus();")
    seen, bad = tabwalk(s, 90, False)
    show("Tab forward: stops", len(seen)); show("Tab forward: first stops", seen[:14]); show("Tab forward: hidden under the block or outside the window", bad[:8])
    s.shot("%s-6a-tab-forward.png" % tag)
    seen2, bad2 = tabwalk(s, 90, True)
    show("Shift+Tab back: stops", len(seen2)); show("Shift+Tab back: hidden under the block or outside the window", bad2[:8])
    s.shot("%s-6b-tab-back.png" % tag)
    show("scroll-margin on a control", s.js("const e = $('pow'); return [getComputedStyle(e).scrollMarginTop, getComputedStyle(document.documentElement).getPropertyValue('--pin-h')];"))

    # Collapse all: the row scrolls with the page while pinned; bring it into view and tap it
    s.js("document.activeElement && document.activeElement.blur(); $('collapseAll').scrollIntoView({ block: 'center', behavior: 'instant' }); await sleep(250);")
    m = s.js("const b = $('collapseAll'), p = mid(b); return [p[0], p[1], document.elementFromPoint(p[0], p[1]) === b, Math.round(scrollY), rect(document.querySelector('.toprow')), rect(document.querySelector('.bench-main'))];")
    show("Collapse all before the tap (x, y, on top, scrollY, row, block)", m)
    s.shot("%s-7a-toprow.png" % tag)
    s.tap(m[0], m[1]); time.sleep(0.5)
    f = s.js(SNAP); show("after Collapse all", {k: f[k] for k in ("y", "main", "stage", "toprow", "status", "lastTouch")})
    show("open sections, label, page height", s.js("return [[...document.querySelectorAll('#sections > details.sec')].filter(d => d.open && vis(d)).length, $('collapseAll').textContent, document.documentElement.scrollHeight];"))
    s.shot("%s-7b-collapsed.png" % tag)
    m = s.js("$('collapseAll').scrollIntoView({ block: 'center', behavior: 'instant' }); await sleep(200); return mid($('collapseAll'));"); s.tap(m[0], m[1]); time.sleep(0.4)
    show("open sections after the second tap", s.js("return [[...document.querySelectorAll('#sections > details.sec')].filter(d => d.open && vis(d)).length, $('collapseAll').textContent];"))

    # unpin, pin again, reload
    KEYS = ("y", "cls", "pin", "main", "mainPos", "stage", "toprow", "toprowPos", "pinBtn", "status", "cv")
    def tapPin():
        m = s.js("const b = $('pinToggle'); b.scrollIntoView({ block: 'center', behavior: 'instant' }); await sleep(250); const p = mid(b); return [p[0], p[1], document.elementFromPoint(p[0], p[1]) === b, rect(b)];")
        show("pin button (x, y, on top at its centre, box)", m)
        s.tap(m[0], m[1]); time.sleep(0.6); s.done()
    stored = "try { return localStorage.getItem('squaringLab.pin.v1'); } catch (e) { return 'blocked: ' + e.message; }"
    if a["pinBtn"] and a["pinBtn"][1] != "none":
        tapPin()
        g = s.js(SNAP); show("after Unpin picture", {k: g[k] for k in KEYS}); show("stored", s.js(stored))
        s.js("go(0); await sleep(200);"); s.shot("%s-8a-unpinned-top.png" % tag)
        s.js("$('secApproach').scrollIntoView({ block: 'start', behavior: 'instant' }); await sleep(250);")
        show("unpinned, at Approach", {k: v for k, v in s.js(SNAP).items() if k in KEYS})
        s.shot("%s-8b-unpinned-approach.png" % tag)
        s.reload(); s.done()
        h = s.js(SNAP); show("after reload (stored unpinned)", {k: h[k] for k in KEYS}); show("stored", s.js(stored))
        tapPin()
        i = s.js(SNAP); show("after Pin picture", {k: i[k] for k in KEYS}); show("stored", s.js(stored))
        s.reload(); s.done()
        j = s.js(SNAP); show("after reload (stored pinned)", {k: j[k] for k in KEYS})
        s.js("$('secApproach').scrollIntoView({ block: 'start', behavior: 'instant' }); await sleep(250);")
        s.shot("%s-8c-pinned-again.png" % tag)
    else:
        show("pin button", "not shown at this size")
        s.js("$('secApproach').scrollIntoView({ block: 'start', behavior: 'instant' }); await sleep(250);")
        show("at Approach, no pin", {k: v for k, v in s.js(SNAP).items() if k in KEYS})
        s.shot("%s-8-approach-nopin.png" % tag)

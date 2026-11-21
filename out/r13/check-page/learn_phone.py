"""Checker: the Learn tab on a narrow window, with touch. Usage: python out/r13/check-page/learn_phone.py SIZE THEME [mobile] [dsf]"""
import sys, json, time
from drive import Session, show

size, theme = sys.argv[1], sys.argv[2]
mobile = len(sys.argv) > 3 and sys.argv[3] == "mobile"
dsf = float(sys.argv[4]) if len(sys.argv) > 4 else 1
tag = "learn-p-%s-%s%s%s" % (size, theme, "-m" if mobile else "", ("-x%g" % dsf) if dsf != 1 else "")
URL = "dist/r13-check-page.html"
fails = []
def check(name, ok, detail=""):
    print("  %s  %s%s" % ("PASS" if ok else "FAIL", name, ("  | " + (detail if isinstance(detail, str) else json.dumps(detail, ensure_ascii=False))) if detail != "" else ""))
    if not ok: fails.append(name)
def tapsel(s, sel):
    m = s.js("const e = document.querySelector(%s); e.scrollIntoView({ block: 'center', behavior: 'instant' }); await sleep(200); const p = mid(e), t = document.elementFromPoint(p[0], p[1]); return [p[0], p[1], !!t && (t === e || e.contains(t) || t.contains(e)), t ? (t.id || t.className || t.tagName) : null];" % json.dumps(sel))
    if not m[2]: print("  NOTE: %s is not on top at its centre: %s is" % (sel, m[3]))
    s.tap(m[0], m[1]); time.sleep(0.25)
    return m

LAY = r"""const main = document.querySelector('.bench-main'), m = main.getBoundingClientRect(), b = $('pinToggle');
return { y: Math.round(scrollY), ih: innerHeight, iw: innerWidth, sw: document.documentElement.scrollWidth, cls: document.documentElement.className, body: document.body.className,
  main: rect(main), share: +(m.height / innerHeight).toFixed(3), mainPos: getComputedStyle(main).position, stage: rect($('stage')), bar: rect($('learnBar')),
  pin: L.pin ? L.pin.state() : null, pinBtn: b ? [rect(b), getComputedStyle(b).display, getComputedStyle(b).position, b.textContent] : null,
  dpr: devicePixelRatio, canvas: [$('learnCanvas').width, $('learnCanvas').height], coarse: matchMedia('(pointer: coarse)').matches };"""
ACTIVE = r"""
const e = document.activeElement, main = document.querySelector('.bench-main'), m = main.getBoundingClientRect();
if (!e || e === document.body) return null;
const r = e.getBoundingClientRect(), inD = !!e.closest('.dials'), held = getComputedStyle(main).position === 'sticky' && m.top <= 1 && scrollY > 2;
return [(e.id || e.name || e.tagName) + '', Math.round(r.top), Math.round(r.bottom), Math.round(m.bottom), innerHeight, inD, held, Math.round(scrollY)];
"""

with Session(URL, size, theme, mobile=mobile, dsf=dsf, name=tag) as s:
    s.done()
    m = tapsel(s, "#mode-l + span")
    a = s.js(LAY); show("Learn on, just after the tap", a)
    check("a tap on Learn turns it on", "is-learn" in a["body"], a["body"])
    s.shot(tag + "-01-after-tap.png")
    s.js("$('learnPanel').scrollIntoView({ block: 'start', behavior: 'instant' }); await sleep(300);")
    b = s.js(LAY); show("scrolled to the Learn panel", b)
    pinned = b["pin"] and b["pin"]["on"] and not b["pin"]["free"]
    if pinned:
        check("picture and transport are held at the top", b["mainPos"] == "sticky" and b["main"][1] == 0, [b["main"], b["mainPos"]])
        check("the held block takes at most about 60%% of the window (%.1f%%)" % (b["share"] * 100), b["share"] <= 0.605, b["share"])
    else:
        show("not pinned at this size", [b["pin"], b["share"]])
    check("no sideways scroll", b["sw"] <= b["iw"], [b["sw"], b["iw"]])
    show("panel summary just under the block", s.js("return [rect($('learnPanel').querySelector('summary')), rect(document.querySelector('.bench-main'))];"))
    s.shot(tag + "-02-panel-top.png")

    # sizes of the things a thumb has to hit
    t = s.js(r"""const box = e => { const r = e.getBoundingClientRect(); return [Math.round(r.width), Math.round(r.height)]; };
      const out = {};
      for (const id of ['learnBack', 'learnPlay', 'learnFwd', 'learnNext', 'learnAgain', 'learnPos', 'learnSpeed', 'pinToggle', 'learnZero', 'learnJuliaC', 'learn-show', 'learn-hid', 'learnViewReset']) { const e = $(id); if (e && vis(e)) out[id] = box(e).concat([e.scrollWidth > e.clientWidth + 1 ? 'label cut' : '']); }
      out.ticks = [...$('learnTicks').children].map(e => box(e).concat([e.textContent, e.scrollWidth > e.clientWidth + 1 ? 'CUT' : '']));
      out.space = [...document.querySelectorAll('#learnSpace .seg')].map(e => box(e).concat([e.textContent]));
      out.modes = [...document.querySelectorAll('fieldset.mode .seg')].map(e => box(e).concat([e.textContent.trim(), e.querySelector('span').scrollWidth > e.querySelector('span').clientWidth + 1 ? 'CUT' : '']));
      out.moves = [...$('learnMoves').children].map(e => box(e));
      out.hidLabel = $('learn-hid') && vis($('learn-hid')) ? box($('learn-hid').closest('label') || $('learn-hid')) : null;
      out.say = [getComputedStyle($('learnSay')).fontSize, $('learnSay').clientHeight, $('learnSay').scrollHeight];
      out.where = [$('learnWhere').textContent, $('learnWhere').scrollWidth > $('learnWhere').clientWidth + 1];
      return out;""")
    show("target sizes (width, height)", t)
    small = [k for k in ("learnBack", "learnPlay", "learnFwd", "learnNext", "learnAgain", "pinToggle") if k in t and (t[k][0] < 40 or t[k][1] < 40)]
    check("transport buttons are at least 40 px each way", [k for k in small if k != "pinToggle"] == [], {k: t[k] for k in small})

    # does every sentence fit the box under the picture? all spaces, all approaches, powers 2, 3, -2
    over = s.js(r"""const K = L.learn, out = [], say = $('learnSay'); let n = 0, most = 0, longest = '';
      const one = (label) => { const st = K.state(); for (let j = 0; j <= st.moves.length; j++) { const q = j < st.moves.length ? K.goto(j, 0.5) : K.goto(st.moves.length - 1, 1); n++;
        if (q.sentence.length > most) { most = q.sentence.length; longest = q.sentence; }
        if (say.scrollHeight > say.clientHeight + 1) out.push([label, j < st.moves.length ? st.moves[j] : 'done', say.scrollHeight, say.clientHeight, q.sentence.length]); } };
      for (const p of [2, 3, -2]) { L.S.n = p; L.syncControls(); L.touch(); await sleep(60);
        for (const sp of [1, 2]) { K.set({ space: sp }); one('space ' + sp + ' n=' + p); }
        K.set({ space: 3 });
        for (const a of L.APPROACHES) { if (a.integerOnly && p % 1) continue; $('ap-' + a.id).click(); await sleep(60); one(a.id + ' n=' + p); } }
      L.S.n = 2; L.syncControls(); $('ap-' + L.APPROACHES[0].id).click(); await sleep(60); K.set({ space: 2 }); K.goto(0, 0);
      return { sentences: n, tooLong: out.length, list: out.slice(0, 12), most, longest, box: [say.clientWidth, say.clientHeight] };""")
    show("sentences that do not fit the box under the picture", over)

    # touch: drag the ring on the flat page
    P = s.js("L.learn.set({ space: 2, hidden: false }); L.learn.goto(0, 0); await sleep(100); const cv = $('learnCanvas'); const r = cv.getBoundingClientRect(), K = L.learn, q = K.proj.to(K.pts[2].z), c = K.proj.to(K.pts[2].c); return [r.left + q[0], r.top + q[1], r.left + c[0], r.top + c[1], K.proj.s, K.pts[2].z, K.pts[2].c, rect(cv), Math.round(scrollY)];")
    s.tdrag(P[0] + 10, P[1] + 8, P[0] + 50, P[1] - 22, 6); time.sleep(0.2)
    z = s.js("return [L.learn.pts[2].z, Math.round(scrollY)];")
    check("touch: dragging the ring (13 px off its centre) moves z and the page does not scroll", abs(z[0][0] - (P[5][0] + 40 / P[4])) < 0.04 and abs(z[0][1] - (P[5][1] + 30 / P[4])) < 0.04 and z[1] == P[8], [P[5], z, P[4]])
    s.tdrag(P[2], P[3], P[2] - 30, P[3] + 10, 6); time.sleep(0.2)
    c = s.js("return L.learn.pts[2].c;")
    check("touch: dragging the diamond moves c", abs(c[0] - (P[6][0] - 30 / P[4])) < 0.04, [P[6], c])
    show("distance between ring and diamond on the screen, px", round(((P[0] - P[2]) ** 2 + (P[1] - P[3]) ** 2) ** 0.5))
    s.js("L.learn.set({ z: [0.7, 0.4, 0], c: [-0.4, 0.3, 0] }); L.learn.goto(0, 0.6);"); time.sleep(0.2); s.shot(tag + "-03-2d-flat.png")
    # touch in 3D: one finger turns, two fingers zoom
    R = s.js("L.learn.set({ space: 3 }); L.learn.goto(0, 0.6); await sleep(100); const r = $('learnCanvas').getBoundingClientRect(); return [r.left + r.width / 2, r.top + r.height / 2, L.learn.view.s3.yaw, L.learn.view.s3.pitch, L.learn.view.s3.zoom, Math.round(scrollY)];")
    s.tdrag(R[0], R[1], R[0] + 60, R[1] + 20, 6); time.sleep(0.2)
    v = s.js("return [L.learn.view.s3.yaw, L.learn.view.s3.pitch, Math.round(scrollY), vis($('learnViewReset')), rect($('learnViewReset')), $('pinToggle') ? rect($('pinToggle')) : null];")
    check("touch: one finger turns the 3D view, the page stays", abs(v[0] - (R[2] - 0.6)) < 1e-6 and v[2] == R[5], [R[2:], v])
    if mobile:
        s.touch("touchStart", [[R[0] - 30, R[1]], [R[0] + 30, R[1]]])
        for k in range(1, 6): s.touch("touchMove", [[R[0] - 30 - 8 * k, R[1]], [R[0] + 30 + 8 * k, R[1]]])
        s.touch("touchEnd", []); time.sleep(0.2)
        z2 = s.js("return [L.learn.view.s3.zoom, L.learn.ptr.size, L.learn.view.s3.yaw];")
        check("touch: a pinch zooms the picture", z2[0] > R[4] * 1.5 and z2[1] == 0, [R[4], z2])
    s.shot(tag + "-04-3d-turned.png")
    rv = tapsel(s, "#learnViewReset"); v2 = s.js("return [L.learn.view.s3.zoom, vis($('learnViewReset'))];")
    check("Reset view by tap", v2[0] == 1 and not v2[1], [rv, v2])
    # the transport by tap
    s.js("$('learnSpeed').value = 'fast'; $('learnSpeed').dispatchEvent(new Event('change', { bubbles: true }));")
    tapsel(s, "#learnPlay"); ok, tt = s.wait("!window.squaringLab.learn.playing", 40); d = s.js("return L.learn.state();")
    check("Play by tap runs to the end of the step", ok and d["done"], [d["move"], d["t"], d["sentence"]])
    s.shot(tag + "-05-3d-done.png")
    tapsel(s, "#learnNext"); s.wait("!window.squaringLab.learn.playing", 40); d2 = s.js("return L.learn.state();")
    check("Next step by tap", d2["step"] == 1, d2["step"])
    r = s.js("return rect($('learnPos'));")
    s.tdrag(r[0] + 20, (r[1] + r[3]) / 2, r[0] + (r[2] - r[0]) * 0.5, (r[1] + r[3]) / 2, 8); time.sleep(0.2); d3 = s.js("return [L.learn.pos, L.learn.state().moves.length];")
    check("the slider scrubs under a finger", 0.2 * d3[1] < d3[0] < 0.8 * d3[1], d3)
    tapsel(s, "#learnAgain")

    # scrolled to Approach: choose another approach, the pinned picture follows
    s.js("L.learn.goto(0, 0.5); $('secApproach').open = true; $('ap-lathe').closest('.rule').scrollIntoView({ block: 'center', behavior: 'instant' }); await sleep(250);")
    before = s.js("return [L.learn.state().moves, rect($('stage')), rect($('learnBar')), Math.round(scrollY)];")
    tapsel(s, "#ap-lathe + *") if s.js("return !!document.querySelector('#ap-lathe + *');") else s.js("$('ap-lathe').click();")
    time.sleep(0.3)
    after = s.js("return [L.learn.state().moves, rect($('stage')), rect($('learnBar')), Math.round(scrollY), L.APPROACHES[L.S.approach].id];")
    check("choosing another approach far down changes the moves in the held picture", after[4] == "lathe" and after[0] != before[0] and (not pinned or after[1][1] == 0), [before, after])
    s.shot(tag + "-06-approach-lathe.png")
    # screens down the Learn panel
    for i, sel in enumerate(["#learnDials", "#learnMovesHead", "#learnNotice", "#secEq", "#secMod"]):
        s.js("const e = document.querySelector(%s); if (e.tagName === 'DETAILS') e.open = true; e.scrollIntoView({ block: 'start', behavior: 'instant' }); await sleep(250);" % json.dumps(sel))
        s.shot("%s-07-%d-%s.png" % (tag, i, sel.strip("#")))
    show("Equation section under Learn: what is on show", s.js("return [...$('secEq').querySelectorAll('.dial, .field, .note, button')].filter(vis).map(e => (e.id || e.className) + ': ' + e.textContent.trim().slice(0, 50));"))
    # Tab with real keys
    s.js("go(0); await sleep(100); $('learnCanvas').focus();")
    def walk(n, shift):
        seen, bad = [], []
        for i in range(n):
            s.key("Tab", shift=shift); time.sleep(0.03)
            a = s.js(ACTIVE)
            if not a: continue
            seen.append(a[0])
            if a[5] and ((a[6] and a[1] < a[3] - 1) or a[2] > a[4] + 1 or a[1] < -1): bad.append(a)
        return seen, bad
    seen, bad = walk(70, False); show("Tab forward under Learn: stops, first ones", [len(seen), seen[:16]]); check("Tab forward: every focused control is clear of the held block", bad == [], bad[:6])
    seen, bad = walk(70, True); check("Shift+Tab back: every focused control is clear of the held block", bad == [], bad[:6])
    # off again
    tapsel(s, "#mode-m + span"); ok, tt = s.done()
    e = s.js("return [L.S.learn, document.body.className, rect($('stage')), $('status').textContent.trim(), vis($('view'))];")
    check("back to Mandelbrot by tap: the solid is drawn", e[0] is False and e[4] and ok, e)
    s.js("go(0); await sleep(100);"); s.shot(tag + "-08-off.png")
    print("FAILS (%d): %s" % (len(fails), json.dumps(fails, ensure_ascii=False)))

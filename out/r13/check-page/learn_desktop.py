"""Checker: the Learn tab at 1400x950 with a real mouse and keyboard. Usage: python out/r13/check-page/learn_desktop.py [theme]"""
import sys, json, time, os
from drive import Session, show, HERE

theme = sys.argv[1] if len(sys.argv) > 1 else "light"
tag = "learn-d-" + theme
URL = "dist/r13-check-page.html"
fails = []
def check(name, ok, detail=""):
    print("  %s  %s%s" % ("PASS" if ok else "FAIL", name, ("  | " + (detail if isinstance(detail, str) else json.dumps(detail, ensure_ascii=False))) if detail != "" else ""))
    if not ok: fails.append(name)

ST = "return L.learn.state();"
HASH = r"""const cv = $('learnCanvas'), g = cv.getContext('2d'), d = g.getImageData(0, 0, cv.width, cv.height).data; let h = 0, ink = 0;
for (let i = 0; i < d.length; i += 4) { if (d[i + 3] > 20) ink++; h = (h * 31 + d[i] + d[i + 1] * 3 + d[i + 2] * 7 + d[i + 3] * 11) | 0; } return [h, ink];"""
def mid(s, sel, scroll=True):
    return s.js("const e = document.querySelector(%s); %s await sleep(120); const p = mid(e); return [p[0], p[1], document.elementFromPoint(p[0], p[1]) === e || e.contains(document.elementFromPoint(p[0], p[1])) || (document.elementFromPoint(p[0], p[1]) && document.elementFromPoint(p[0], p[1]).contains(e))];" % (json.dumps(sel), "e.scrollIntoView({ block: 'center', behavior: 'instant' });" if scroll else ""))
def click(s, sel, scroll=True):
    m = mid(s, sel, scroll)
    if not m[2]: print("  NOTE: %s is not on top at its centre" % sel)
    s.click(m[0], m[1]); time.sleep(0.15)
    return m
def waitstop(s, t=40):
    return s.wait("!window.squaringLab.learn.playing", t)

with Session(URL, "1400x950", theme, name=tag) as s:
    s.done()
    s.shot(tag + "-00-open.png")
    s.js("L.cam.yaw += 0.6; L.cam.pitch = 0.45; L.touch();"); s.done()
    before = s.js("return [$('status').textContent.trim(), probes(), [L.cam.yaw, L.cam.pitch, L.cam.dist].join()];")
    s.shot(tag + "-01-before.png")

    # ---------- on
    click(s, "#mode-l + span")
    a = s.js("""return { learn: L.S.learn, mode: L.S.mode, cls: document.body.className, radio: $('mode-l').checked, first: $('sections').firstElementChild.id,
      gone: ['view', 'mandelPanel', 'secCut', 'secColour', 'secView', 'secQuality', 'secExport', 'secMesh', 'status', 'hintBelow'].filter(id => vis($(id))),
      here: ['learnCanvas', 'learnBar', 'learnPanel', 'secApproach', 'secEq', 'secMod', 'pow'].filter(id => !vis($(id))), hiddenAttr: [$('mandelPanel').hidden, $('secCut').hidden],
      main: rect(document.querySelector('.bench-main')), stage: rect($('stage')), bar: rect($('learnBar')), ih: innerHeight, sw: document.documentElement.scrollWidth, st: L.learn.state() };""")
    check("Learn on by a click: S.learn, class, radio, S.mode kept", a["learn"] is True and "is-learn" in a["cls"] and a["radio"] and a["mode"] == "m", {k: a[k] for k in ("learn", "mode", "cls", "radio")})
    check("Learn panel is first among the sections", a["first"] == "learnPanel", a["first"])
    check("what should be put away is put away", a["gone"] == [], a["gone"])
    check("what should stay is on show", a["here"] == [], a["here"])
    check("picture and transport fit in the window", a["main"][3] <= a["ih"] and a["sw"] <= 1400, [a["main"], a["stage"], a["bar"], a["ih"], a["sw"]])
    check("opens on the 2D page with moves Turn, Stretch, Add c", a["st"]["space"] == 2 and a["st"]["moves"] == ["Turn", "Stretch", "Add c"], a["st"]["moves"])
    time.sleep(0.3); s.shot(tag + "-02-on.png")

    # ---------- transport
    click(s, "#learnPlay"); time.sleep(0.7)
    b = s.js("return [L.learn.playing, L.learn.pos, $('learnPlay').textContent];")
    check("Play starts the move and the button reads Pause", b[0] and b[1] > 0.05 and b[2] == "Pause", b)
    s.shot(tag + "-03-playing.png")
    click(s, "#learnPlay"); time.sleep(0.2); p1 = s.js("return L.learn.pos;"); time.sleep(0.5); p2 = s.js("return [L.learn.pos, L.learn.playing, $('learnPlay').textContent];")
    check("Pause holds the place", abs(p1 - p2[0]) < 1e-9 and not p2[1] and p2[2] == "Play", [p1, p2])
    s.js("$('learnSpeed').value = 'fast'; $('learnSpeed').dispatchEvent(new Event('change', { bubbles: true }));")
    click(s, "#learnPlay"); ok, t = waitstop(s)
    c = s.js(ST)
    check("Play runs through all moves and stops", ok and c["done"] and not c["playing"] and "Step 1 is done" in c["sentence"], [round(t, 1), c["move"], c["t"], c["sentence"]])
    s.shot(tag + "-04-done.png")
    end1 = c["end"]
    click(s, "#learnNext"); time.sleep(0.3)
    d = s.js(ST)
    check("Next step goes on from the new point", d["step"] == 1 and all(abs(x - y) < 1e-12 for x, y in zip(d["z"], end1)) and len(d["orbit"]) == 2, [d["step"], d["z"], end1])
    waitstop(s); s.shot(tag + "-05-step2-done.png")
    click(s, "#learnBack"); e = s.js(ST)
    check("Back one move from the end stands at the start of the last move", e["move"] == 2 and e["t"] == 0 and not e["done"], [e["move"], e["t"], e["done"]])
    click(s, "#learnBack"); e2 = s.js(ST)
    check("Back again goes one move further back", e2["move"] == 1 and e2["t"] == 0, [e2["move"], e2["t"]])
    click(s, "#learnFwd"); waitstop(s); f = s.js("return [L.learn.pos, L.learn.state().move, L.learn.state().t];")
    check("Forward plays one move and stops at its end", abs(f[0] - 2) < 1e-9, f)
    click(s, "#learnAgain"); g = s.js(ST)
    check("Start again goes back to the first point", g["step"] == 0 and g["move"] == 0 and g["t"] == 0 and len(g["orbit"]) == 1, [g["step"], g["move"], g["t"]])
    # the slider, dragged with the mouse
    r = s.js("$('learnPos').scrollIntoView({ block: 'center', behavior: 'instant' }); await sleep(100); return rect($('learnPos'));")
    h0 = s.js(HASH)
    s.drag(r[0] + 12, (r[1] + r[3]) / 2, r[0] + (r[2] - r[0]) * 0.5, (r[1] + r[3]) / 2, 10); time.sleep(0.2)
    h = s.js(ST); h1 = s.js(HASH)
    check("dragging the slider to the middle stands in the second move", h["move"] == 1 and 0.3 < h["t"] < 0.7 and h0 != h1, [h["move"], round(h["t"], 3), h0, h1])
    s.shot(tag + "-06-slider-mid.png")
    s.drag(r[0] + (r[2] - r[0]) * 0.5, (r[1] + r[3]) / 2, r[0] + (r[2] - r[0]) * 0.2, (r[1] + r[3]) / 2, 10); h2 = s.js(ST)
    check("dragging the slider back goes back", h2["move"] == 0 and 0.4 < h2["t"] < 0.8, [h2["move"], round(h2["t"], 3)])
    s.js("$('learnPos').focus();"); p0 = s.js("return L.learn.pos;"); s.key("ArrowRight"); s.key("ArrowRight"); p1 = s.js("return L.learn.pos;")
    check("arrow keys on the slider move it", p1 > p0, [p0, p1])
    m = click(s, "#learnTicks button:nth-child(3)"); waitstop(s); k = s.js(ST)
    check("pressing a move name under the slider plays that move", k["done"], [k["move"], k["t"]])

    # ---------- the panel: Space, hidden direction, dials, buttons, Show
    click(s, "#learnSpace1 + span"); time.sleep(0.2)
    q = s.js("const st = L.learn.state(); return { space: st.space, hidden: st.hidden, box: $('learn-hid') ? $('learn-hid').checked : null, dials: ['learn-zx', 'learn-zy', 'learn-zz', 'learn-cx', 'learn-cy', 'learn-cz'].filter(id => vis($(id))), moves: st.moves, note: st.note, hn: $('learnHiddenNote').textContent, notice: $('learnNotice').textContent };")
    check("1D: space 1, hidden direction ticked at first, only the x dials", q["space"] == 1 and q["hidden"] and q["box"] and q["dials"] == ["learn-zx", "learn-cx"], q)
    mt = s.js("return L.learn.goto(0, 0.5);")
    check("1D mid-turn: the negative number is off the line (hidden direction)", abs(mt["point"][1]) > 0.5, [mt["point"], mt["sentence"]])
    time.sleep(0.2); s.shot(tag + "-10-1d-hidden-midturn.png")
    click(s, "#learn-hid"); time.sleep(0.2)
    q2 = s.js("return [L.learn.state().hidden, $('learnHiddenNote').textContent];")
    check("unticking the box gives the flat line", q2[0] is False, q2)
    s.js("L.learn.goto(0, 0.5);"); time.sleep(0.2); s.shot(tag + "-11-1d-flat-midturn.png")
    # drag the ring on the flat line
    P = s.js("L.learn.goto(0, 0); const cv = $('learnCanvas'); cv.scrollIntoView({ block: 'center', behavior: 'instant' }); await sleep(100); const r = cv.getBoundingClientRect(), K = L.learn, q = K.proj.to(K.pts[K.space].z), c = K.proj.to(K.pts[K.space].c); return [r.left + q[0], r.top + q[1], r.left + c[0], r.top + c[1], K.proj.s, K.pts[K.space].z, K.pts[K.space].c];")
    s.drag(P[0], P[1], P[0] + 60, P[1], 6); z1 = s.js("return [L.learn.pts[1].z, $('learn-zx').value];")
    check("1D: dragging the ring moves z along the line, the dial follows", abs(z1[0][0] - (P[5][0] + 60 / P[4])) < 0.03 and abs(float(z1[1]) - z1[0][0]) < 1e-9, [P[5], z1, P[4]])
    click(s, "#learnSpace2 + span"); time.sleep(0.2)
    P = s.js("L.learn.goto(0, 0); const cv = $('learnCanvas'); cv.scrollIntoView({ block: 'center', behavior: 'instant' }); await sleep(100); const r = cv.getBoundingClientRect(), K = L.learn, q = K.proj.to(K.pts[K.space].z), c = K.proj.to(K.pts[K.space].c); return [r.left + q[0], r.top + q[1], r.left + c[0], r.top + c[1], K.proj.s, K.pts[K.space].z, K.pts[K.space].c];")
    s.drag(P[0], P[1], P[0] + 50, P[1] - 40, 6); time.sleep(0.1); z2 = s.js("return [L.learn.pts[2].z, $('learn-zx').value, $('learn-zy').value];")
    check("2D flat: dragging the ring moves z", abs(z2[0][0] - (P[5][0] + 50 / P[4])) < 0.03 and abs(z2[0][1] - (P[5][1] + 40 / P[4])) < 0.03, [P[5], z2, P[4]])
    P = s.js("const cv = $('learnCanvas'); const r = cv.getBoundingClientRect(), K = L.learn, c = K.proj.to(K.pts[K.space].c); return [r.left + c[0], r.top + c[1], K.proj.s, K.pts[K.space].c];")
    s.drag(P[0], P[1], P[0] - 30, P[1] + 20, 6); time.sleep(0.1); c2 = s.js("return [L.learn.pts[2].c, $('learn-cx').value, $('learn-cy').value];")
    check("2D flat: dragging the diamond moves c", abs(c2[0][0] - (P[3][0] - 30 / P[2])) < 0.03 and abs(c2[0][1] - (P[3][1] - 20 / P[2])) < 0.03, [P[3], c2])
    s.js("L.learn.goto(0, 0.6);"); time.sleep(0.2); s.shot(tag + "-12-2d-flat-midturn.png")
    # dials
    s.js("type('learn-zx', 0.5); type('learn-zy', -0.25); type('learn-cx', 0.1);"); time.sleep(0.1)
    dl = s.js("return [L.learn.pts[2].z, L.learn.pts[2].c];")
    check("the dials set z and c", dl[0][:2] == [0.5, -0.25] and dl[1][0] == 0.1, dl)
    click(s, "#learnZero"); z0 = s.js("const st = L.learn.state(); const says = st.moves.map((m, j) => L.learn.goto(j, 0.5).sentence); return [st.z0, says];")
    check("Start at 0 puts z at 0 and the sentences still read", z0[0] == [0, 0, 0] and not any(("NaN" in x or "undefined" in x or "Infinity" in x) for x in z0[1]), z0)
    click(s, "#learnJuliaC"); jc = s.js("return [L.learn.pts[2].c, L.S.c];")
    check("Use the c of the Julia tab copies it (flat part)", jc[0][:2] == jc[1][:2] and jc[0][2] == 0, jc)
    s.js("L.learn.set({ z: [0.7, 0.4, 0], c: [-0.4, 0.3, 0] }); const e = $('learn-show'); e.value = 'all'; e.dispatchEvent(new Event('change', { bubbles: true })); L.learn.goto(0, 0.6);"); time.sleep(0.2)
    sh = s.js("return [L.learn.show, L.learn.cache.comp[0].length];")
    check("Show: all directions gives dots on the unit circle", sh == ["all", 72], sh)
    s.shot(tag + "-13-2d-all.png")
    s.js("const e = $('learn-show'); e.value = 'point'; e.dispatchEvent(new Event('change', { bubbles: true }));"); sh = s.js("return [L.learn.show, L.learn.cache.comp[0].length];")
    check("Show: the point alone", sh == ["point", 0], sh)
    s.js("const e = $('learn-show'); e.value = 'circle'; e.dispatchEvent(new Event('change', { bubbles: true }));")
    click(s, "#learnMoves button:nth-child(2)"); time.sleep(0.3); mv = s.js("return [L.learn.playing, L.learn.state().move];"); waitstop(s); mv2 = s.js("return L.learn.pos;")
    check("a move button in the panel plays that move", mv[1] == 1 and abs(mv2 - 2) < 1e-9, [mv, mv2])
    # the hidden direction on the page; turning and zooming the tipped view
    click(s, "#learn-hid"); time.sleep(0.2)
    s.js("L.learn.goto(0, 0.6);"); time.sleep(0.2); s.shot(tag + "-14-2d-tipped.png")
    R = s.js("const cv = $('learnCanvas'); cv.scrollIntoView({ block: 'center', behavior: 'instant' }); await sleep(100); const r = cv.getBoundingClientRect(); return [r.left + r.width / 2, r.top + r.height / 2, L.learn.view.h2.yaw, L.learn.view.h2.pitch, L.learn.view.h2.zoom, vis($('learnViewReset'))];")
    s.drag(R[0], R[1], R[0] + 80, R[1] + 30, 8); v1 = s.js("return [L.learn.view.h2.yaw, L.learn.view.h2.pitch, L.learn.pts[2].z, vis($('learnViewReset'))];")
    check("tipped 2D: a drag turns the view and moves no point", abs(v1[0] - (R[2] - 0.8)) < 1e-6 and abs(v1[1] - (R[3] + 0.3)) < 1e-6 and v1[2] == [0.7, 0.4, 0] and v1[3] and not R[5], [R[2:], v1])
    lab0 = s.js("return [L.cam.dist, Math.round(scrollY)];")
    s.wheel(R[0], R[1], -240); time.sleep(0.3); v2 = s.js("return [L.learn.view.h2.zoom, L.cam.dist, Math.round(scrollY)];")
    check("the wheel zooms the Learn picture, not the solid behind it, and does not scroll", v2[0] > 1.2 and v2[1] == lab0[0] and v2[2] == lab0[1], [v2, lab0])
    s.shot(tag + "-15-2d-tipped-turned.png")
    click(s, "#learnViewReset", scroll=False); v3 = s.js("return [L.learn.view.h2.yaw, L.learn.view.h2.zoom, vis($('learnViewReset'))];")
    check("Reset view puts the view back and the button goes", abs(v3[0] + 0.5) < 1e-9 and v3[1] == 1 and not v3[2], v3)
    # keyboard on the picture
    s.js("$('learnCanvas').focus();"); s.key("ArrowLeft"); s.key("+"); s.key(" "); time.sleep(0.3)
    kb = s.js("return [L.learn.view.h2.yaw, L.learn.view.h2.zoom, L.learn.playing];"); s.key(" "); kb2 = s.js("return L.learn.playing;")
    check("keys on the picture: arrow turns, plus zooms, space plays and pauses", abs(kb[0] + 0.4) < 1e-9 and kb[1] > 1.1 and kb[2] and not kb2, [kb, kb2])
    # 3D, mouse
    click(s, "#learnSpace3 + span"); time.sleep(0.3)
    t3 = s.js("const st = L.learn.state(); return { space: st.space, box: vis($('learn-hid')), dials: ['learn-zx', 'learn-zy', 'learn-zz', 'learn-cx', 'learn-cy', 'learn-cz'].filter(id => vis($(id))).length, hn: $('learnHiddenNote').textContent.slice(0, 80), moves: st.moves };")
    check("3D: no hidden direction box, three dials per point", t3["space"] == 3 and not t3["box"] and t3["dials"] == 6, t3)
    R = s.js("const cv = $('learnCanvas'); cv.scrollIntoView({ block: 'center', behavior: 'instant' }); await sleep(100); const r = cv.getBoundingClientRect(); return [r.left + r.width / 2, r.top + r.height / 2, L.learn.view.s3.yaw, L.learn.view.s3.pitch];")
    s.drag(R[0], R[1], R[0] - 70, R[1] - 20, 8); v = s.js("return [L.learn.view.s3.yaw, L.learn.view.s3.pitch, L.learn.pts[3].z];")
    check("3D: a drag turns the view", abs(v[0] - (R[2] + 0.7)) < 1e-6 and abs(v[1] - (R[3] - 0.2)) < 1e-6, [R[2:], v])
    click(s, "#learnViewReset", scroll=False)
    # Reset this section
    click(s, "#learnReset button"); rs = s.js("const st = L.learn.state(); return [st.on, st.space, st.z0, st.c, st.show, L.learn.pos, L.learn.speed, L.learn.hidden];")
    check("Reset this section puts Learn's settings back and stays in Learn", rs[0] and rs[1] == 2 and rs[2] == [0.7, 0.4, 0] and rs[4] == "circle", rs)

    # ---------- off again: the solid as it was
    click(s, "#mode-m + span"); ok, t = s.done()
    after = s.js("return [$('status').textContent.trim(), probes(), [L.cam.yaw, L.cam.pitch, L.cam.dist].join(), L.S.learn, document.body.className, $('mode-m').checked, vis($('view')), vis($('learnBar'))];")
    check("Learn off: the solid, its camera and its status line are as before", after[:3] == before and after[3] is False and "is-learn" not in after[4] and after[5] and after[6] and not after[7], [before[0], after[0], before[2], after[2], after[3:]])
    s.js("go(0); await sleep(100);"); s.shot(tag + "-20-after.png")

    # ---------- on again: every approach in 3D, power, dial, modifier
    click(s, "#mode-l + span"); s.js("L.learn.set({ space: 3 });")
    words = []
    ids = s.js("return L.APPROACHES.map(a => [a.id, a.name, a.group || '']);")
    for i, (aid, name, grp) in enumerate(ids):
        r = s.js(r"""const id = %s; $('ap-' + id).click(); await sleep(120);
          const K = L.learn, st = K.state(), out = { id: L.APPROACHES[L.S.approach].id, moves: st.moves, note: st.note, says: [], bad: [], inks: [] };
          const plan = L.learnPlan({ space: 3, id, params: L.S.param[id], n: L.S.n, c: st.c, abs: L.S.abs, flip: L.S.flip });
          out.check = plan.check ? plan.check(st.z0) : null;
          let prev = null;
          for (let j = 0; j < st.moves.length; j++) for (const t of [0.25, 0.75]) {
            const q = K.goto(j, t); if (t === 0.25) out.says.push(q.sentence);
            if (!q.point.every(isFinite) || /NaN|undefined|Infinity|null/.test(q.sentence)) out.bad.push([j, t, q.point, q.sentence]);
            const cv = $('learnCanvas'), d = cv.getContext('2d').getImageData(0, 0, cv.width, cv.height).data; let h = 0, ink = 0;
            for (let k = 0; k < d.length; k += 4) { if (d[k + 3] > 20) ink++; h = (h * 31 + d[k] + d[k + 1] * 3 + d[k + 2] * 7) | 0; }
            out.inks.push(ink); if (h === prev) out.bad.push(['same picture', j, t]); prev = h;
          }
          out.end = st.end; out.done = K.goto(st.moves.length - 1, 1).sentence;
          K.goto(Math.min(1, st.moves.length - 1), 0.6); return out;""" % json.dumps(aid))
        check("3D %s (%s): moves %s" % (name, aid, ", ".join(r["moves"])), r["id"] == aid and len(r["moves"]) >= 2 and r["bad"] == [] and min(r["inks"]) > 2000 and r["check"] is not None and r["check"] < 1e-9, {"check": r["check"], "bad": r["bad"][:3], "inks": [min(r["inks"]), max(r["inks"])]})
        words.append({"space": 3, "id": aid, "name": name, "moves": r["moves"], "says": r["says"], "done": r["done"], "note": r["note"]})
        time.sleep(0.15); s.js("go(0); await sleep(60);"); s.shot("%s-3d-%02d-%s.png" % (tag, i, aid))
    # power, an approach dial, a modifier
    s.js("$('ap-bulb').click(); await sleep(100); L.learn.goto(0, 0.5);")
    b0 = s.js("const st = L.learn.state(); return [st.sentence, st.end, st.moves];")
    s.js("type('pow', 3); await sleep(150);"); b1 = s.js("const st = L.learn.goto(0, 0.5); return [st.sentence, st.end, st.moves, L.S.n, L.S.learn, L.idle()];")
    check("power 3 while Learn is on: the sentence and the result change", b1[3] == 3 and b1[0] != b0[0] and b1[1] != b0[1], [b0[0], b1[0]])
    s.js("type('par-bulb-lat', 30); await sleep(150);"); b2 = s.js("const st = L.learn.state(); return [st.end, st.moves, L.S.param.bulb.lat, st.note];")
    check("an approach dial (Latitude phase 30) changes the result", b2[2] == 30 and b2[0] != b1[1], [b1[1], b2[0], b2[1]])
    fz = s.js("const lab = [...document.querySelectorAll('#secMod label')].find(l => l.textContent.trim() === 'flip z'); const inp = lab ? (lab.querySelector('input') || $(lab.htmlFor)) : null; if (inp) { $('secMod').open = true; inp.id = inp.id || 'chk-flipz'; } return inp ? inp.id : null;")
    if fz:
        click(s, "#" + fz); time.sleep(0.2)
        b3 = s.js("const st = L.learn.state(); return [st.moves, L.S.flip, L.learn.goto(0, 0.5).sentence];")
        check("the modifier flip z adds a first move Mirror", b3[0][0] == "Mirror" and b3[1][1] == 1, b3)
        words.append({"space": 3, "id": "bulb+flip z, n=3, lat 30", "moves": b3[0], "says": s.js("const st = L.learn.state(); return st.moves.map((m, j) => L.learn.goto(j, 0.25).sentence);"), "note": s.js("return L.learn.state().note;")})
        time.sleep(0.2); s.js("go(0); await sleep(60);"); s.shot(tag + "-30-bulb-n3-lat30-flipz.png")
        click(s, "#" + fz)
    else:
        check("found the flip z tick box", False)
    # words in the flat spaces and other powers
    for sp in (1, 2):
        for n in (2, 3, -1, 2.5):
            w = s.js("L.S.n = %s; L.syncControls(); L.touch(); await sleep(120); L.learn.set({ space: %d }); const st = L.learn.state(); return { space: %d, id: 'n=' + L.S.n, moves: st.moves, says: st.moves.map((m, j) => L.learn.goto(j, 0.25).sentence), done: L.learn.goto(st.moves.length - 1, 1).sentence, note: st.note };" % (n, sp, sp))
            words.append(w)
    s.js("L.S.n = 2; L.S.param.bulb.lat = 0; L.syncControls(); L.touch(); await sleep(100); L.learn.set({ space: 3 });")
    # run away
    ra = s.js("L.learn.set({ space: 2, z: [2.5, 2, 0], c: [1, 1, 0] }); const st = L.learn.goto(2, 1); return [st.away, st.sentence, $('learnNext').disabled];")
    check("a point that runs away says so and Next step is off", ra[0] and "run away" in ra[1] and ra[2], ra)
    words.append({"space": 2, "id": "run away", "says": [ra[1]]})
    # the page's own words in the panel and transport
    words.append({"panel": s.js("return $('learnPanel').innerText;"), "bar": s.js("return $('learnBar').innerText;"), "titles": s.js("return [...document.querySelectorAll('#learnBar [title], #learnPanel [title], #learnBar [aria-label], #learnCanvas, #pinToggle')].map(e => [e.id, e.title, e.getAttribute('aria-label')]);")})
    for sp in (1, 3):
        words.append({"panel space %d" % sp: s.js("L.learn.set({ space: %d }); return [$('learnHiddenNote').textContent, $('learnNotice').textContent, $('learnNote').textContent];" % sp)})
    s.js("L.learn.set({ space: 1, hidden: false }); "); words.append({"1D flat note": s.js("return $('learnHiddenNote').textContent;")})
    s.js("L.learn.set({ space: 2, hidden: true }); "); words.append({"2D tipped note": s.js("return $('learnHiddenNote').textContent;")})
    with open(os.path.join(HERE, "learn-words-%s.json" % theme), "w", encoding="utf-8") as f:
        json.dump(words, f, ensure_ascii=False, indent=1)
    # the equation note
    eq = s.js("$('mode-m').click(); await sleep(100); const e = $('eq'); const old = e.value; type('eq', 'z^n + c + 0.1'); await sleep(200); const took = L.S.eq; $('mode-l').click(); await sleep(150); const shown = vis($('learnEqNote')), txt = $('learnEqNote').textContent; return [old, took, shown, txt];")
    check("with another equation the Learn panel says it shows the plain rule", eq[2] and eq[1] != "z^n + c", eq)
    time.sleep(0.2); s.js("$('learnPanel').scrollIntoView({ block: 'start', behavior: 'instant' }); await sleep(100);"); s.shot(tag + "-31-eq-note.png")

    # ---------- the choices under Show, by keyboard (real key presses)
    s.js("$('mode-l').focus();")
    s.key("ArrowLeft"); time.sleep(0.4); k1 = s.js("return [document.activeElement.id, L.S.mode, L.S.learn, document.body.className, vis($('view'))];")
    check("keyboard: arrow left from Learn chooses Kleinian and leaves Learn", k1[0] == "mode-k" and k1[1] == "k" and k1[2] is False and "is-learn" not in k1[3] and k1[4], k1)
    s.key("ArrowRight"); time.sleep(0.4); k2 = s.js("return [document.activeElement.id, L.S.mode, L.S.learn, $('secApproach').hidden, vis($('secApproach')), vis($('secEq')), vis($('secMod')), vis($('kleinPanel')), L.learn.state().moves];")
    check("keyboard: arrow right from Kleinian chooses Learn; Approach, Equation, Modifiers show although Kleinian hides them", k2[0] == "mode-l" and k2[1] == "k" and k2[2] is True and k2[4] and k2[5] and k2[6] and not k2[7], k2)
    s.js("go(0); await sleep(80);"); s.shot(tag + "-32-learn-from-kleinian.png")
    s.key("ArrowRight"); time.sleep(0.4); k3 = s.js("return [document.activeElement.id, L.S.mode, L.S.learn];")
    check("keyboard: arrow right from Learn wraps to Mandelbrot", k3 == ["mode-m", "m", False], k3)
    s.key("ArrowRight"); time.sleep(0.4); k4 = s.js("return [document.activeElement.id, L.S.mode, L.S.learn];")
    check("keyboard: Julia", k4 == ["mode-j", "j", False], k4)
    s.key("ArrowLeft"); s.key("ArrowLeft"); time.sleep(0.4); k5 = s.js("return [document.activeElement.id, L.S.mode, L.S.learn];")
    check("keyboard: back round to Learn", k5[0] == "mode-l" and k5[2] is True, k5)

    # ---------- Reset everything, from Learn in 3D mid-move
    s.js("L.learn.set({ space: 3, show: 'all' }); L.learn.goto(1, 0.4); $('ap-tilt').click(); type('pow', 5);")
    click(s, "#resetAll"); time.sleep(0.3); ok, t = s.done()
    re = s.js("const K = L.learn; return [L.S.learn, L.S.mode, document.body.className, K.space, K.show, K.pos, K.pts[2].z, L.S.n, L.S.eq, L.APPROACHES[L.S.approach].id, $('mode-m').checked, vis($('view')), $('status').textContent.trim()];")
    check("Reset everything leaves Learn, resets it and the lab, and draws the solid", re[0] is False and re[1] == "m" and "is-learn" not in re[2] and re[3] == 2 and re[4] == "circle" and re[5] == 0 and re[7] == 2 and re[10] and re[11] and ok, re)
    s.js("go(0); await sleep(80);"); s.shot(tag + "-33-after-reset.png")
    # the other three still work by click
    click(s, "#mode-j + span"); ok, t = s.done(); j = s.js("return [L.S.mode, L.S.learn, probes().includes('1')];")
    check("Julia by click still works", j == ["j", False, True] and ok, j)
    click(s, "#mode-k + span"); ok, t = s.done(); k = s.js("return [L.S.mode, L.S.learn, vis($('kleinPanel'))];")
    check("Kleinian by click still works", k == ["k", False, True] and ok, k)
    click(s, "#mode-m + span"); ok, t = s.done(); m = s.js("return [L.S.mode, L.S.learn, probes().includes('1')];")
    check("Mandelbrot by click still works", m == ["m", False, True] and ok, m)
    # resetAll() from code while Learn is on (the view engineer's stated gap)
    rc = s.js("$('mode-l').click(); await sleep(100); L.resetAll && L.resetAll(); await sleep(200); return [typeof L.resetAll, L.S.learn, document.body.className];")
    show("resetAll() from code while Learn is on (typeof, S.learn, class)", rc)
    print("FAILS (%d): %s" % (len(fails), json.dumps(fails, ensure_ascii=False)))

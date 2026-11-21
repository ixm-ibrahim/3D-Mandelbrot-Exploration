"""Writes steps/s8-extra.json: the loose ends (model description, low depth stops, zooming in, Frame it against a small
drawing radius, the arrows beside the Approach menu, leaving by an approach when the Kleinian button was the way in)."""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
SH = "out/r27/checkb/shots/s8-@T-"

HELPERS = r"""
window.L = window.squaringLab;
window.sleep = ms => new Promise(r => setTimeout(r, ms));
window.settle = async () => { const t0 = performance.now(); await sleep(100); while (!L.idle()) await sleep(25); await sleep(50); while (!L.idle()) await sleep(25); return Math.round(performance.now() - t0); };
window.slide = async (id, v) => { const r = document.getElementById(id); r.value = v; r.dispatchEvent(new Event('input', {bubbles: true})); r.dispatchEvent(new Event('change', {bubbles: true})); return await settle(); };
window.typed = async (id, v) => { const n = document.getElementById(id + 'Num'); n.focus(); n.value = String(v); n.dispatchEvent(new Event('input', {bubbles: true})); n.dispatchEvent(new KeyboardEvent('keydown', {key: 'Enter', bubbles: true, cancelable: true})); return await settle(); };
window.pick = async (id, i) => { const s = document.getElementById(id); s.value = String(i); s.dispatchEvent(new Event('change', {bubbles: true})); return await settle(); };
window.press = async id => { document.getElementById(id).click(); return await settle(); };
window.shown = e => { if (!e) return false; for (let x = e; x && x.nodeType === 1; x = x.parentElement) { if (x.hidden) return false; const cs = getComputedStyle(x); if (cs.display === 'none' || cs.visibility === 'hidden') return false; } const b = e.getBoundingClientRect(); return b.width > 0 && b.height > 0; };
window.st = () => ({ mode: L.S.mode, group: L.S.k.group, flat: L.S.flat, t: +L.S.k.bt.toFixed(4), grid: L.S.k.bgrid, rounds: L.S.k.bit, approach: L.S.approach, apName: document.getElementById('apMenuName').textContent, cam: [+L.cam.yaw.toFixed(3), +L.cam.pitch.toFixed(3), +L.cam.dist.toFixed(4)], target: L.cam.target.map(v => +v.toFixed(3)), bound: L.S.view.bound, zmin: L.S.view.zmin, zmax: L.S.view.zmax, h: +L.S.v2.h.toFixed(5), hmax: L.S.v2.hmax, warn: shown(document.getElementById('ballsWarn')) ? document.getElementById('ballsWarn').textContent : '', status: document.getElementById('status').textContent, sizeBox: document.getElementById('ballsSizeNum').value });
window.toBalls = async () => { document.getElementById('ap-balls').click(); await settle(); window.scrollTo(0, 0); };
window.flatAt = async (x, y, h) => { L.S.v2.x = x; L.S.v2.y = y; L.S.v2.h = h; L.touch(); return await settle(); };
window.camAt = async (target, yaw, pitch, dist) => { L.cam.target = target; L.cam.yaw = yaw; L.cam.pitch = pitch; L.cam.dist = dist; L.touch(); return await settle(); };
"""


def main():
    a = [{"wait": "done", "timeout": 100},
         {"js": HELPERS + "await toBalls(); ['secCut', 'secColour', 'secView', 'secQuality', 'secExport', 'secMesh'].forEach(id => { document.getElementById(id).open = true; }); window.squaringLabSaveHook = async (name, blob) => { window.__blob = blob; window.__name = name; }; return st();"}]

    def shot(name, clip="#stage"):
        d = {"shot": SH + name + ".png"}
        if clip:
            d["clip"] = clip
        a.append(d)

    # (a) what the saved model says about itself
    a.append({"js": "await pick('meshCells', 0); document.getElementById('meshStart').click(); await sleep(400);"})
    a.append({"wait": "!window.squaringLab.meshBusy()", "timeout": 110})
    a.append({"js": "document.getElementById('meshSave').click(); await sleep(1500); const b = window.__blob; if (!b) return 'no file'; const buf = new Uint8Array(await b.arrayBuffer()); let s = ''; const N = Math.min(buf.length, 4000000); const dec = new TextDecoder('utf-8', {fatal: false}); const txt = dec.decode(buf.subarray(0, N)); const out = []; let i = -1; while ((i = txt.indexOf('Balls on balls', i + 1)) >= 0 && out.length < 6) out.push(txt.slice(Math.max(0, i - 160), i + 260).replace(/[^\\x20-\\x7e\\n]/g, '?')); const names = [...txt.matchAll(/kleinian-96\\.[a-z]+|[A-Za-z-]+\\.txt/g)].map(m => m[0]); return {a: 'model file', name: window.__name, size: b.size, mentions: out, names: [...new Set(names)]};"})
    a.append({"js": "document.getElementById('meshDiscard').click(); window.scrollTo(0, 0); await settle();"})

    # (b) the low end of the depth slider
    for d in (2, 3, 4, 5, 6):
        a.append({"js": "const ms = await slide('ballsDepth', %d); return {b: 'depth %d', ms, rounds: L.S.k.bit};" % (d, d)})
        shot("b-depth-%d-3d" % d)
    a.append({"js": "await press('flat');"})
    for d in (2, 3, 4, 5, 6):
        a.append({"js": "const ms = await slide('ballsDepth', %d); return {b: 'depth %d flat', ms};" % (d, d)})
        shot("b-depth-%d-flat" % d)
    a.append({"js": "await slide('ballsDepth', 16); return st();"})

    # (c) zooming in, 2D view: at a kiss (between the middle ball and its right neighbour) and on a bud
    for label, x, y in (("kiss", 0.525, 0.0), ("bud", 0.0, 0.84)):
        for h in (0.4, 0.05, 0.005, 0.0006):
            for d in (16, 40, 200):
                if d != 16 and h > 0.05:
                    continue
                how = "slide('ballsDepth', %d)" % d if d <= 40 else "typed('ballsDepth', %d)" % d
                a.append({"js": "await %s; const ms = await flatAt(%s, %s, %s); return {c: '2D zoom %s, height of picture %s, depth %d', ms, h: L.S.v2.h, status: document.getElementById('status').textContent};" % (how, x, y, h, label, h, d)})
                shot("c-2d-%s-h%s-d%d" % (label, str(h).replace(".", "p"), d))
    a.append({"js": "await typed('ballsDepth', 16); await press('reset'); await press('flat'); return st();"})

    # (d) zooming in, 3D: towards the kiss between the middle ball and the bud on top of it, and onto the side of the middle ball
    for label, tgt, yaw, pitch in (("topkiss", [0, 0, 0.525], -1.25, 0.25), ("side", [0.0, -0.525, 0.0], -1.5708, 0.3), ("chainkiss", [0.525, 0, 0], -1.5708, 0.5)):
        for dist in (1.0, 0.25, 0.06, 0.015):
            for d in (16, 40):
                if d != 16 and dist > 0.06:
                    continue
                a.append({"js": "await slide('ballsDepth', %d); const ms = await camAt(%s, %s, %s, %s); return {d: '3D zoom %s, distance %s, depth %d', ms, dist: L.cam.dist, status: document.getElementById('status').textContent};" % (d, json.dumps(tgt), yaw, pitch, dist, label, dist, d)})
                shot("d-3d-%s-dist%s-d%d" % (label, str(dist).replace(".", "p"), d))
    a.append({"js": "await slide('ballsDepth', 16); await press('reset'); return st();"})

    # (e) Frame it against a small drawing radius and a near zoom limit: does 'Nothing else changes' hold?
    a.append({"js": "await slide('viewBound', 1); const b1 = st(); return {e: 'Drawing radius set to 1', ...b1};"})
    shot("e-bound1")
    a.append({"js": "document.getElementById('ballsWarn').scrollIntoView({block: 'center'}); await sleep(250);"})
    shot("e-bound1-panel", None)
    a.append({"js": "window.scrollTo(0, 0); const before = st(); const ms = await press('ballsFrame'); return {e: 'Frame it with Drawing radius 1', ms, before: {bound: before.bound, zmin: before.zmin, zmax: before.zmax, hmax: before.hmax, cam: before.cam}, after: st()};"})
    shot("e-bound1-after-frame")
    a.append({"js": "document.querySelector('#viewReset button').click(); await settle(); L.S.view.zmax = 2; L.cam.dist = 2; L.viewChanged(); L.touch(); await settle(); const before = st(); const ms = await press('ballsFrame'); return {e: 'Frame it with the farthest zoom set to 2', ms, before: {bound: before.bound, zmin: before.zmin, zmax: before.zmax, cam: before.cam}, after: st()};"})
    shot("e-zmax2-after-frame")
    a.append({"js": "await press('resetAll'); await toBalls(); return st();"})

    # (f) the two arrows beside the Approach menu, from Balls on balls
    a.append({"js": "const ms = await press('apNext'); window.scrollTo(0, 0); return {f: 'arrow down (next) from Balls on balls', ms, ...st()};"})
    shot("f-after-next", None)
    a.append({"js": "await toBalls(); const ms = await press('apPrev'); window.scrollTo(0, 0); return {f: 'arrow up (previous) from Balls on balls', ms, ...st()};"})
    shot("f-after-prev", None)
    # arrows the other way round: from the last approach, does 'next' reach Balls on balls?
    a.append({"js": "const ms = await press('apNext'); return {f: 'arrow down (next) from the last approach', ms, ...st()};"})
    a.append({"js": "await press('resetAll'); const ms = await press('apPrev'); return {f: 'arrow up (previous) from the first approach', ms, ...st()};"})

    # (g) in by the Kleinian button from Julia, out by an approach
    a.append({"js": "await press('resetAll'); await press('mode-j'); await press('mode-k'); await press('kleinGroup1'); const inn = st(); document.getElementById('ap-' + L.APPROACHES[3].id).click(); const ms = await settle(); window.scrollTo(0, 0); return {g: 'Julia, Kleinian button, Balls on balls, then approach 3', ms, inside: {mode: inn.mode, group: inn.group, apName: inn.apName}, after: st()};"})
    shot("g-after-approach", None)
    # (h) in by the row from Julia, out by Mandelbrot button, then Kleinian again
    a.append({"js": "await toBalls(); await press('mode-m'); const m = st(); await press('mode-k'); return {h: 'row, then Mandelbrot button, then Kleinian button', mandel: {mode: m.mode, apName: m.apName, approach: m.approach}, kleinian: st()};"})

    # (i) typed values outside the range of the size dial
    for v in (1, 0, 150, -5, "abc", 55.56):
        a.append({"js": "const ms = await typed('ballsSize', %s); const n = document.getElementById('ballsSizeNum'); return {i: 'typed %s into the size box', ms, box: n.value, t: L.S.k.bt, flag: n.closest('.dial').className, at: n.closest('.dial').dataset.at};" % (json.dumps(v), v)})
    with open(os.path.join(HERE, "steps", "s8-extra.json"), "w", encoding="utf-8") as f:
        json.dump(a, f, indent=1)
    print(len(a), "steps")


if __name__ == "__main__":
    main()

"""Writes out/r27/checkb/steps/s3-dials.json: every dial of Balls on balls through its stops, the way a user moves it."""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
SH = "out/r27/checkb/shots/s3-@T-"

HELPERS = r"""
window.L = window.squaringLab;
window.sleep = ms => new Promise(r => setTimeout(r, ms));
window.settle = async () => { const t0 = performance.now(); await sleep(80); while (!L.idle()) await sleep(25); return Math.round(performance.now() - t0); };
window.slide = async (id, v) => { const r = document.getElementById(id); r.value = v; r.dispatchEvent(new Event('input', {bubbles: true})); r.dispatchEvent(new Event('change', {bubbles: true})); return await settle(); };
window.typed = async (id, v) => { const n = document.getElementById(id + 'Num'); n.focus(); n.value = String(v); n.dispatchEvent(new Event('input', {bubbles: true})); n.dispatchEvent(new KeyboardEvent('keydown', {key: 'Enter', bubbles: true, cancelable: true})); return await settle(); };
window.pick = async (id, i) => { const s = document.getElementById(id); s.value = String(i); s.dispatchEvent(new Event('change', {bubbles: true})); return await settle(); };
window.press = async id => { document.getElementById(id).click(); return await settle(); };
window.cam3 = async (yaw, pitch, dist) => { const c = L.cam; c.yaw = yaw; c.pitch = pitch; if (dist) c.dist = dist; L.touch(); return await settle(); };
window.info = () => { const w = document.getElementById('ballsWarn'), k = L.S.k; return { t: +k.bt.toFixed(4), grid: k.bgrid, rounds: k.bit, sizeBox: document.getElementById('ballsSizeNum').value, depthBox: document.getElementById('ballsDepthNum').value, gridBox: document.getElementById('ballsGrid').selectedOptions[0].textContent, warn: w.hidden ? '' : w.textContent, status: document.getElementById('status').textContent, reach: +L.ballsReach().toFixed(3), dist: +L.cam.dist.toFixed(3), flat: L.S.flat, h: +L.S.v2.h.toFixed(3), bound: L.S.view.bound, zmax: L.S.view.zmax }; };
"""


def main():
    a = [{"wait": "done", "timeout": 100},
         {"js": HELPERS + "document.getElementById('apMenuBtn').click(); await sleep(200); const ms = await press('ap-balls'); window.scrollTo(0, 0); return {ms, ...info()};"}]

    def shot(name, clip="#stage"):
        a.append({"shot": SH + name + ".png", "clip": clip})

    # --- size of the neighbours
    for label, how in [("010", "slide('ballsSize', 10)"), ("030", "slide('ballsSize', 30)"), ("055", "slide('ballsSize', 55.6)"),
                       ("080", "slide('ballsSize', 80)"), ("100", "slide('ballsSize', 100)"), ("002typed", "typed('ballsSize', 2)"),
                       ("095typed", "typed('ballsSize', 95)")]:
        a.append({"js": "const ms = await %s; return {stop: 'size %s', ms, ...info()};" % (how, label)})
        shot("size-%s-a-asis" % label)
        a.append({"js": "const ms = await press('ballsFrame'); return {stop: 'size %s framed', ms, ...info()};" % label})
        shot("size-%s-b-framed" % label)
        a.append({"js": "const ms = await press('flat'); return {stop: 'size %s flat', ms, ...info()};" % label})
        shot("size-%s-c-flat" % label)
        a.append({"js": "await press('flat');"})
    # the panel as it stands at 100 (is there a warning line?)
    a.append({"js": "await slide('ballsSize', 100); document.getElementById('ballsPart').scrollIntoView({block: 'center'}); await sleep(300); return info();"})
    a.append({"shot": SH + "size-100-panel.png"})
    a.append({"js": "await press('ballsFrame'); document.getElementById('ballsPart').scrollIntoView({block: 'center'}); await sleep(300); return info();"})
    a.append({"shot": SH + "size-100-panel-after-frame.png"})
    a.append({"js": "window.scrollTo(0, 0); const ms = await typed('ballsSize', 55.56); await press('ballsFrame'); return {stop: 'size back to 55.56', ms, ...info()};"})

    # --- whole numbers
    for i, label in enumerate(["square", "honeycomb", "line"]):
        a.append({"js": "const ms = await pick('ballsGrid', %d); return {stop: 'grid %s', ms, ...info()};" % (i, label)})
        shot("grid-%s-a-start" % label)
        a.append({"js": "const ms = await cam3(0.0, 0.15); return {stop: 'grid %s end-on', ms};" % label})
        shot("grid-%s-b-endon" % label)
        a.append({"js": "const ms = await cam3(-1.5708, 1.5); return {stop: 'grid %s above', ms};" % label})
        shot("grid-%s-c-above" % label)
        a.append({"js": "await press('reset'); const ms = await press('flat'); return {stop: 'grid %s flat', ms, ...info()};" % label})
        shot("grid-%s-d-flat" % label)
        a.append({"js": "await press('flat');"})
    a.append({"js": "await pick('ballsGrid', 0); return info();"})

    # --- depth of the search
    for label, how in [("01typed", "typed('ballsDepth', 1)"), ("02", "slide('ballsDepth', 2)"), ("05", "slide('ballsDepth', 5)"), ("08", "slide('ballsDepth', 8)"),
                       ("16", "slide('ballsDepth', 16)"), ("28", "slide('ballsDepth', 28)"), ("40", "slide('ballsDepth', 40)"), ("200typed", "typed('ballsDepth', 200)")]:
        a.append({"js": "const ms = await %s; return {stop: 'depth %s', ms, ...info()};" % (how, label)})
        shot("depth-%s-a-3d" % label)
        a.append({"js": "const ms = await press('flat'); return {stop: 'depth %s flat', ms, ...info()};" % label})
        shot("depth-%s-b-flat" % label)
        a.append({"js": "await press('flat');"})
    a.append({"js": "await typed('ballsDepth', 16); return info();"})

    # --- the heavy corners: neighbours at 100, each grid, depth 16 / 40 / 200, 3D
    for g, gl in enumerate(["square", "honeycomb", "line"]):
        for d in (16, 40, 200):
            a.append({"js": "await typed('ballsSize', 100); await pick('ballsGrid', %d); await press('ballsFrame'); const ms = await typed('ballsDepth', %d); return {stop: 'corner size 100 %s depth %d', ms, ...info()};" % (g, d, gl, d), })
            shot("corner-100-%s-%03d" % (gl, d))
    a.append({"js": "const ms = await press('flat'); return {stop: 'corner size 100 line depth 200 flat', ms, ...info()};"})
    shot("corner-100-line-200-flat")
    # the panel's own reset puts every dial back
    a.append({"js": "await press('flat'); const b = document.querySelector('#ballsReset button'); b.click(); const ms = await settle(); return {stop: 'panel reset', label: b.textContent, ms, ...info()};"})
    shot("after-panel-reset")

    with open(os.path.join(HERE, "steps", "s3-dials.json"), "w", encoding="utf-8") as f:
        json.dump(a, f, indent=1)
    print(len(a), "steps")


if __name__ == "__main__":
    main()

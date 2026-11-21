"""Writes steps/s7-back.json (the new page: into Balls on balls, dials moved, then back out) and steps/s7-base.json
(the frozen page taken to the same places directly), so that the pictures can be compared pixel by pixel."""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))

HELPERS = r"""
window.L = window.squaringLab;
window.sleep = ms => new Promise(r => setTimeout(r, ms));
window.settle = async () => { const t0 = performance.now(); await sleep(120); while (!L.idle()) await sleep(25); await sleep(60); while (!L.idle()) await sleep(25); return Math.round(performance.now() - t0); };
window.slide = async (id, v) => { const r = document.getElementById(id); r.value = v; r.dispatchEvent(new Event('input', {bubbles: true})); r.dispatchEvent(new Event('change', {bubbles: true})); return await settle(); };
window.pick = async (id, i) => { const s = document.getElementById(id); s.value = String(i); s.dispatchEvent(new Event('change', {bubbles: true})); return await settle(); };
window.press = async id => { document.getElementById(id).click(); return await settle(); };
window.cam3 = async (yaw, pitch, dist) => { const c = L.cam; c.yaw = yaw; c.pitch = pitch; if (dist) c.dist = dist; L.touch(); return await settle(); };
window.shown = e => { if (!e) return false; for (let x = e; x && x.nodeType === 1; x = x.parentElement) { if (x.hidden) return false; const cs = getComputedStyle(x); if (cs.display === 'none' || cs.visibility === 'hidden') return false; } const b = e.getBoundingClientRect(); return b.width > 0 && b.height > 0; };
window.texts = sel => { const out = []; document.querySelectorAll(sel).forEach(root => { const w = document.createTreeWalker(root, NodeFilter.SHOW_TEXT); let n; while ((n = w.nextNode())) { const t = n.textContent.replace(/\s+/g, ' ').trim(); if (t && shown(n.parentElement)) out.push(t); } }); return out; };
window.st = () => ({ mode: L.S.mode, group: L.S.k.group, flat: L.S.flat, approach: L.S.approach, apName: document.getElementById('apMenuName').textContent, modeChecked: [...document.querySelectorAll('input[name=mode]')].filter(i => i.checked).map(i => i.id), cam: [+L.cam.yaw.toFixed(4), +L.cam.pitch.toFixed(4), +L.cam.dist.toFixed(4)], view: { bound: L.S.view.bound, zmin: L.S.view.zmin, zmax: L.S.view.zmax, fov: L.S.view.fov }, v2: { x: L.S.v2.x, y: L.S.v2.y, h: +L.S.v2.h.toFixed(4), hmax: L.S.v2.hmax }, k: JSON.stringify(L.S.k), colour: JSON.stringify(L.S.colour), q: JSON.stringify(L.S.q), status: document.getElementById('status').textContent, secs: ['juliaPanel', 'mandelPanel', 'kleinPanel', 'secApproach', 'secEq', 'secMod', 'secCut', 'secColour', 'secView', 'secQuality'].filter(id => document.getElementById(id) && shown(document.getElementById(id))), panelWords: texts('#sections').length });
window.ap = async i => { const id = 'ap-' + L.APPROACHES[i].id; document.getElementById(id).click(); return await settle(); };
window.top0 = () => window.scrollTo(0, 0);
"""


def seq(tag, new):
    SH = "out/r27/checkb/shots/s7-@T-%s-" % tag
    a = [{"wait": "done", "timeout": 100}]
    if not new:
        a[0]["url"] = "dist/r27-checkb-base.html"

    def both(name):
        a.append({"js": "top0(); await sleep(250);"})
        a.append({"shot": SH + name + "-window.png"})
        a.append({"shot": SH + name + "-stage.png", "clip": "#stage"})

    a.append({"js": HELPERS + "await settle(); return {at: '0 as it opens', ...st()};"})
    both("0-open")
    if new:
        a.append({"js": "document.getElementById('apMenuBtn').click(); await sleep(200); await press('ap-balls'); await slide('ballsSize', 80); await pick('ballsGrid', 1); await slide('ballsDepth', 30); await press('ballsFrame'); await cam3(0.7, 0.9); return {at: 'in Balls on balls, dials and camera moved', ...st()};"})
        both("x-in-balls")
        a.append({"js": "document.getElementById('apMenuBtn').scrollIntoView({block: 'start'}); await sleep(150); document.getElementById('apMenuBtn').click(); await sleep(250); return {menuOpen: !document.getElementById('apPop').hidden};"})
        a.append({"shot": SH + "x-menu-from-balls.png"})
    a.append({"js": "const ms = await ap(7); return {at: '1 approach 7 chosen', ms, name: L.APPROACHES[7].name, ...st()};"})
    both("1-approach7")
    a.append({"js": "const ms = await press('mode-j'); return {at: '2 Julia', ms, ...st()};"})
    both("2-julia")
    a.append({"js": "const ms = await press('mode-k'); return {at: '3 Kleinian button', ms, ...st()};"})
    if new:
        both("3-kleinian-button")
        a.append({"js": "const ms = await press('kleinGroup0'); return {at: '4 the old Kleinian group chosen', ms, kleinNote: document.getElementById('kleinNote').textContent, kleinWarn: shown(document.getElementById('kleinWarn')) ? document.getElementById('kleinWarn').textContent : '', preset: document.getElementById('kleinPreset').selectedOptions[0].textContent, ...st()};"})
    else:
        a.append({"js": "return {at: '4 the Kleinian view', kleinNote: document.getElementById('kleinNote').textContent, kleinWarn: shown(document.getElementById('kleinWarn')) ? document.getElementById('kleinWarn').textContent : '', preset: document.getElementById('kleinPreset').selectedOptions[0].textContent, ...st()};"})
    both("4-kleinian-old")
    a.append({"js": "document.getElementById('kleinDials').scrollIntoView({block: 'center'}); await sleep(250);"})
    a.append({"shot": SH + "4-kleinian-old-dials.png"})
    a.append({"js": "const ms = await press('flat'); return {at: '5 old group, 2D view', ms, ...st()};"})
    both("5-kleinian-old-flat")
    a.append({"js": "await press('flat'); const ms = await pick('col-mode', 4); return {at: '6 old group, colour by direction of the last step', ms};"})
    both("6-kleinian-old-laststep")
    a.append({"js": "await pick('col-mode', 0); document.getElementById('mode-l').click(); await sleep(1200); top0(); return {at: '7 Learn from the old Kleinian group', bodyLearn: document.body.classList.contains('is-learn'), apShown: shown(document.getElementById('secApproach')), kleinShown: shown(document.getElementById('kleinPanel')), eqShown: shown(document.getElementById('secEq')), first: texts('#sections').slice(0, 3)};"})
    a.append({"shot": SH + "7-learn-from-kleinian-window.png"})
    a.append({"js": "await press('mode-m'); const ms = await ap(0); return {at: '8 Mandelbrot, first approach again', ms, ...st()};"})
    both("8-mandelbrot-again")
    a.append({"js": "document.getElementById('apMenuBtn').scrollIntoView({block: 'start'}); await sleep(150); document.getElementById('apMenuBtn').click(); await sleep(300); const p = document.getElementById('apPop'), r = document.getElementById('rules'); const rows = [...document.querySelectorAll('#rules .rule')].filter(e => { const b = e.getBoundingClientRect(), q = r.getBoundingClientRect(); return b.top >= q.top - 1 && b.bottom <= q.bottom + 1 && b.bottom <= innerHeight; }); return {at: '9 the open Approach menu', pop: [Math.round(p.getBoundingClientRect().top), Math.round(p.getBoundingClientRect().bottom)], list: [Math.round(r.getBoundingClientRect().top), Math.round(r.getBoundingClientRect().bottom), r.scrollHeight, r.clientHeight, getComputedStyle(r).overflowY], rowsWhollyVisible: rows.length, win: [innerWidth, innerHeight]};"})
    a.append({"shot": SH + "9-menu.png"})
    name = "s7-back" if new else "s7-base"
    with open(os.path.join(HERE, "steps", name + ".json"), "w", encoding="utf-8") as f:
        json.dump(a, f, indent=1)
    print(name, len(a), "steps")


if __name__ == "__main__":
    seq("new", True)
    seq("base", False)

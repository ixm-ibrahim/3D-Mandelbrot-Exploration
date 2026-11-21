"""Writes steps/s5a-feat.json and steps/s5b-feat.json: everything decision 7 lists, tried in Balls on balls."""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))

HELPERS = r"""
window.L = window.squaringLab;
window.sleep = ms => new Promise(r => setTimeout(r, ms));
window.settle = async () => { const t0 = performance.now(); await sleep(80); while (!L.idle()) await sleep(25); return Math.round(performance.now() - t0); };
window.slide = async (id, v) => { const r = document.getElementById(id); r.value = v; r.dispatchEvent(new Event('input', {bubbles: true})); r.dispatchEvent(new Event('change', {bubbles: true})); return await settle(); };
window.typed = async (id, v) => { const n = document.getElementById(id + 'Num'); n.focus(); n.value = String(v); n.dispatchEvent(new Event('input', {bubbles: true})); n.dispatchEvent(new KeyboardEvent('keydown', {key: 'Enter', bubbles: true, cancelable: true})); return await settle(); };
window.pick = async (id, i) => { const s = document.getElementById(id); s.value = String(i); s.dispatchEvent(new Event('change', {bubbles: true})); return await settle(); };
window.press = async id => { document.getElementById(id).click(); return await settle(); };
window.cam3 = async (yaw, pitch, dist) => { const c = L.cam; c.yaw = yaw; c.pitch = pitch; if (dist) c.dist = dist; L.touch(); return await settle(); };
window.shown = e => { if (!e) return false; for (let x = e; x && x.nodeType === 1; x = x.parentElement) { if (x.hidden) return false; const cs = getComputedStyle(x); if (cs.display === 'none' || cs.visibility === 'hidden') return false; } const b = e.getBoundingClientRect(); return b.width > 0 && b.height > 0; };
window.texts = sel => { const out = []; document.querySelectorAll(sel).forEach(root => { const w = document.createTreeWalker(root, NodeFilter.SHOW_TEXT); let n; while ((n = w.nextNode())) { const t = n.textContent.replace(/\s+/g, ' ').trim(); if (t && shown(n.parentElement)) out.push(t); } }); return out; };
window.openSec = id => { const d = document.getElementById(id); if (d && d.tagName === 'DETAILS') d.open = true; };
window.notes = sel => [...document.querySelectorAll(sel + ' p.note')].filter(shown).map(p => p.textContent.trim());
window.labels = sel => [...document.querySelectorAll(sel + ' label.label, ' + sel + ' label.check')].filter(shown).map(p => p.textContent.replace(/\s+/g, ' ').trim());
window.st = () => ({ mode: L.S.mode, group: L.S.k.group, flat: L.S.flat, cutOn: L.S.cutOn, cut: L.S.cut, t: L.S.k.bt, grid: L.S.k.bgrid, rounds: L.S.k.bit, approach: L.S.approach, learn: !!L.S.learn, status: document.getElementById('status').textContent, kWarnOld: (() => { const w = document.getElementById('kleinWarn'); return w && shown(w) ? w.textContent : ''; })(), kWarnNew: (() => { const w = document.getElementById('ballsWarn'); return w && shown(w) ? w.textContent : ''; })() });
window.toBalls = async () => { document.getElementById('ap-balls').click(); await settle(); window.scrollTo(0, 0); };
"""


def write(name, a):
    with open(os.path.join(HERE, "steps", name + ".json"), "w", encoding="utf-8") as f:
        json.dump(a, f, indent=1)
    print(name, len(a), "steps")


def part_a():
    SH = "out/r27/checkb/shots/s5a-@T-"
    a = [{"wait": "done", "timeout": 100},
         {"js": HELPERS + "await toBalls(); ['secCut', 'secColour', 'secView', 'secQuality', 'secExport', 'secMesh'].forEach(openSec); await sleep(200); return st();"}]

    def shot(name, clip="#stage"):
        d = {"shot": SH + name + ".png"}
        if clip:
            d["clip"] = clip
        a.append(d)

    # ---- F1: the 2D view and the height of the slice
    a.append({"js": "const ms = await press('flat'); return {f: '2D view on', ms, flatZ: document.getElementById('flatZ').textContent, cutLabels: labels('#secCut'), cutNotes: notes('#secCut'), ...st()};"})
    shot("f1-flat-z0")
    for z in (0.15, 0.3, 0.5, 0.6, -0.3):
        a.append({"js": "const ms = await slide('cut', %s); return {f: 'slice height %s', ms, flatZ: document.getElementById('flatZ').textContent, cutBox: document.getElementById('cutNum').value, ...st()};" % (z, z)})
        shot("f1-flat-z%s" % str(z).replace("-", "m").replace(".", "p"))
    a.append({"js": "document.getElementById('secCut').scrollIntoView({block: 'center'}); await sleep(300);"})
    shot("f1-slice-section", None)
    a.append({"js": "await slide('cut', 0); const ms = await press('flat'); window.scrollTo(0, 0); return {f: '2D view off', ms, ...st()};"})

    # ---- F2: the 3D cut and its painted face
    a.append({"js": "const ms = await press('cutOn'); return {f: 'cut the solid open at z = 0', ms, colourLabels: labels('#secColour'), ...st()};"})
    shot("f2-cut-z0")
    a.append({"js": "const ms = await press('col-cutFace'); return {f: 'cut face coloured like the inside of the 2D view', ms, colourNotes: notes('#secColour'), ...st()};"})
    shot("f2-cut-z0-face")
    a.append({"js": "await pick('col-inMode', 3); const ms = await cam3(-1.5708, 1.2); return {f: 'cut face, inside by how deep, from above', ms};"})
    shot("f2-cut-z0-face-deep-above")
    a.append({"js": "const ms = await slide('cut', 0.25); return {f: 'cut at 0.25', ms, ...st()};"})
    shot("f2-cut-z025-face-above")
    a.append({"js": "await pick('col-inMode', 0); await press('col-cutFace'); await slide('cut', 0); await press('cutOn'); const ms = await press('reset'); return {f: 'cut off again', ms, ...st()};"})

    # ---- F3: colour by, in 3D and in the 2D view
    for i, nm in enumerate(["trap", "escape", "centre", "depth", "laststep", "surface", "clay"]):
        a.append({"js": "const ms = await pick('col-mode', %d); return {f: 'colour by %s (3D)', ms, option: document.getElementById('col-mode').selectedOptions[0].textContent, notes: notes('#secColour'), status: document.getElementById('status').textContent};" % (i, nm)})
        shot("f3-3d-%d-%s" % (i, nm))
    a.append({"js": "await pick('col-mode', 0); await press('flat');"})
    for i, nm in enumerate(["trap", "escape", "centre", "depth", "laststep", "surface", "clay"]):
        a.append({"js": "const ms = await pick('col-mode', %d); return {f: 'colour by %s (2D)', ms, notes: notes('#secColour'), status: document.getElementById('status').textContent};" % (i, nm)})
        shot("f3-2d-%d-%s" % (i, nm))
    a.append({"js": "await pick('col-mode', 0);"})

    # ---- F4: inside colours (2D view)
    for i, nm in enumerate(["plain", "trap", "ends", "deep", "settles"]):
        a.append({"js": "const ms = await pick('col-inMode', %d); return {f: 'inside by %s (2D)', ms, option: document.getElementById('col-inMode').selectedOptions[0].textContent, notes: notes('#secColour'), status: document.getElementById('status').textContent};" % (i, nm)})
        shot("f4-inside-%d-%s" % (i, nm))
    a.append({"js": "await pick('col-inMode', 0); await press('flat'); return st();"})

    # ---- F5: trap shapes and "trap colours by" (3D)
    for i, nm in enumerate(["point", "cross", "line", "ray", "planes", "shell", "ring", "tones"]):
        a.append({"js": "const ms = await pick('col-trap', %d); return {f: 'trap shape %s', ms, option: document.getElementById('col-trap').selectedOptions[0].textContent, labels: labels('#secColour'), notes: notes('#secColour')};" % (i, nm)})
        shot("f5-trap-%d-%s" % (i, nm))
    a.append({"js": "await pick('col-trap', 5);"})
    for i, nm in enumerate(["bands", "glow", "step", "blend", "side", "where"]):
        a.append({"js": "const ms = await pick('col-by', %d); return {f: 'trap colours by %s', ms, option: document.getElementById('col-by').selectedOptions[0].textContent, notes: notes('#secColour')};" % (i, nm)})
        shot("f5-by-%d-%s" % (i, nm))
    a.append({"js": "await pick('col-by', 1);"})

    # ---- F6: trap solids
    a.append({"js": "return {f: 'before the trap solid', solidShown: shown(document.getElementById('col-solid')), solidOptions: [...document.getElementById('col-solid').options].map(o => o.textContent + (o.disabled ? ' (disabled)' : '')), labels: labels('#secColour')};"})
    for i, nm in ((1, "is-the-solid"), (2, "is-added")):
        a.append({"js": "const ms = await pick('col-solid', %d); return {f: 'trap %s', ms, option: document.getElementById('col-solid').selectedOptions[0].textContent, solid: L.S.colour.solid, labels: labels('#secColour'), notes: notes('#secColour'), thickShown: shown(document.getElementById('col-thick')), skipShown: shown(document.getElementById('col-skip')), ...st()};" % (i, nm)})
        shot("f6-solid-%s" % nm)
        a.append({"js": "document.getElementById('col-solid').scrollIntoView({block: 'center'}); await sleep(300);"})
        shot("f6-solid-%s-section" % nm, None)
        a.append({"js": "window.scrollTo(0, 0);"})
    a.append({"js": "const ms = await pick('col-trap', 7); return {f: 'three tones while a solid is asked for', ms, notes: notes('#secColour'), labels: labels('#secColour')};"})
    shot("f6-solid-tones")
    # the same asked-for solid in the old group, for comparison of the picture, then back
    a.append({"js": "await pick('col-trap', 5); await press('kleinGroup0'); return {f: 'old group with the solid still asked for', notes: notes('#secColour'), ...st()};"})
    shot("f6-old-group-solid-kept")
    a.append({"js": "await press('kleinGroup1'); const r = {f: 'back in Balls on balls, solid still asked for', notes: notes('#secColour'), ...st()}; await pick('col-solid', 0); return r;"})
    shot("f6-back-colours-surface")

    # ---- F7: the Examples list
    a.append({"js": "const s = document.getElementById('trapExamples'); return {f: 'Examples list', shown: shown(s), value: s.value, chosen: s.selectedOptions[0] ? s.selectedOptions[0].textContent : null, options: [...s.querySelectorAll('option')].map(o => (o.parentElement.tagName === 'OPTGROUP' ? o.parentElement.label + ' / ' : '') + o.textContent + (o.disabled ? ' (disabled)' : '')), help: notes('#secColour').slice(0, 2)};"})
    a.append({"js": "document.getElementById('trapExamples').scrollIntoView({block: 'center'}); await sleep(300);"})
    shot("f7-examples-list", None)
    a.append({"js": "const s = document.getElementById('trapExamples'); const k = [...s.options].findIndex(o => /Kleinian/i.test(o.parentElement.label || '') ); return {firstKleinianOption: k, text: k >= 0 ? s.options[k].textContent : null, value: k >= 0 ? s.options[k].value : null};"})
    a.append({"js": "const s = document.getElementById('trapExamples'); const k = [...s.options].findIndex(o => /Kleinian/i.test(o.parentElement.label || '')); if (k < 0) return 'no Kleinian example'; const ms = await pick('trapExamples', s.options[k].value); window.scrollTo(0, 0); return {f: 'a Kleinian example chosen from Balls on balls', ms, group0: document.getElementById('kleinGroup0').checked, apName: document.getElementById('apMenuName').textContent, anyWordAboutIt: texts('#kleinPanel').slice(0, 8), ...st()};"})
    shot("f7-after-kleinian-example", None)
    a.append({"js": "await toBalls(); const s = document.getElementById('trapExamples'); const k = [...s.options].findIndex(o => o.value !== '0' && !/Kleinian/i.test(o.parentElement.label || '') && o.value !== '' && o.index > 0); const ms = await pick('trapExamples', s.options[k].value); window.scrollTo(0, 0); return {f: 'another example chosen from Balls on balls: ' + s.options[k].textContent, ms, ...st()};"})
    shot("f7-after-other-example", None)
    a.append({"js": "await toBalls(); return {f: 'back to Balls on balls by its row', colour: {mode: L.S.colour.mode, trap: L.S.colour.trap, solid: L.S.colour.solid, by: L.S.colour.by}, ...st()};"})
    shot("f7-back-in-balls")
    write("s5a-feat", a)


def part_b():
    SH = "out/r27/checkb/shots/s5b-@T-"
    a = [{"wait": "done", "timeout": 100},
         {"js": HELPERS + "await toBalls(); ['secCut', 'secColour', 'secView', 'secQuality', 'secExport', 'secMesh'].forEach(openSec); window.squaringLabSaveHook = async (name, blob) => { window.__saved = (window.__saved || []).concat([{ name, size: blob.size, type: blob.type }]); window.__blob = blob; }; await sleep(200); return st();"}]

    def shot(name, clip="#stage"):
        d = {"shot": SH + name + ".png"}
        if clip:
            d["clip"] = clip
        a.append(d)

    # ---- F8: picture export
    a.append({"js": "await pick('exportSize', 0); await pick('exportQuality', 0); document.getElementById('exportStart').click(); await sleep(300); return {f: 'picture export started', busy: L.exportBusy(), step: document.getElementById('exportStep').textContent, msg: document.getElementById('exportMsg').textContent};"})
    a.append({"wait": "!window.squaringLab.exportBusy()", "timeout": 110})
    a.append({"js": "document.getElementById('secExport').scrollIntoView({block: 'center'}); await sleep(300); return {f: 'picture export finished', facts: texts('#exportFacts'), msg: document.getElementById('exportMsg').textContent, saveShown: shown(document.getElementById('exportSave'))};"})
    shot("f8-export-section", None)
    a.append({"js": "document.getElementById('exportSave').click(); await sleep(600); const b = window.__blob; let dim = null; if (b) { const bm = await createImageBitmap(b); dim = [bm.width, bm.height]; const im = document.createElement('img'); im.id = 'chkImg'; im.src = URL.createObjectURL(b); im.style.cssText = 'position:fixed;left:0;top:0;max-width:100vw;max-height:100vh;z-index:99999;background:#000'; document.body.appendChild(im); await new Promise(r => { im.onload = r; }); await sleep(200); } return {f: 'picture saved', saved: window.__saved, dim, msg: document.getElementById('exportMsg').textContent};"})
    shot("f8-exported-picture", None)
    a.append({"js": "const im = document.getElementById('chkImg'); if (im) im.remove(); window.__blob = null; window.scrollTo(0, 0);"})

    # ---- F9: 3D model export
    a.append({"js": "document.getElementById('secMesh').scrollIntoView({block: 'center'}); await sleep(200); const before = {labels: labels('#secMesh'), notes: notes('#secMesh')}; await pick('meshCells', 0); document.getElementById('meshStart').click(); await sleep(400); return {f: 'model export started', before, busy: L.meshBusy(), step: document.getElementById('meshStep').textContent, msg: document.getElementById('meshMsg').textContent};"})
    a.append({"wait": "!window.squaringLab.meshBusy()", "timeout": 110})
    a.append({"js": "document.getElementById('secMesh').scrollIntoView({block: 'end'}); await sleep(300); return {f: 'model export finished', facts: texts('#meshFacts'), warn: document.getElementById('meshWarn').textContent, msg: document.getElementById('meshMsg').textContent, saveShown: shown(document.getElementById('meshSave')), all: texts('#secMesh').slice(-30)};"})
    shot("f9-model-section", None)
    a.append({"js": "document.getElementById('meshSave').click(); await sleep(1500); return {f: 'model saved', saved: window.__saved, msg: document.getElementById('meshMsg').textContent};"})
    a.append({"js": "document.getElementById('meshDiscard').click(); document.getElementById('exportDiscard').click(); window.scrollTo(0, 0);"})

    # ---- F10: the scorecard and the figures under the picture, in both groups
    a.append({"js": "const sc = document.querySelector('section.score'); const grab = () => ({ scoreShown: shown(sc), card: texts('#card').slice(0, 12), figs: [...document.querySelectorAll('figure.fig')].map(shown), below: texts('main section').slice(0, 6) }); const balls = grab(); await press('kleinGroup0'); const old = grab(); await press('kleinGroup1'); return {f: 'scorecard', balls, old, same: JSON.stringify(balls) === JSON.stringify(old)};"})
    a.append({"js": "const sc = document.querySelector('section.score') || document.getElementById('card'); sc.scrollIntoView({block: 'center'}); await sleep(300);"})
    shot("f10-scorecard-area", None)
    a.append({"js": "window.scrollTo(0, document.body.scrollHeight); await sleep(300);"})
    shot("f10-page-bottom", None)
    a.append({"js": "window.scrollTo(0, 0);"})

    # ---- F11: reset buttons
    a.append({"js": "await slide('ballsSize', 80); await pick('ballsGrid', 1); await slide('ballsDepth', 30); await cam3(0.4, 0.9, 9); const before = st(); before.cam = [L.cam.yaw, L.cam.pitch, +L.cam.dist.toFixed(2)]; const ms = await press('reset'); const after = st(); after.cam = [L.cam.yaw, L.cam.pitch, +L.cam.dist.toFixed(2)]; return {f: 'Reset view (dials moved, camera moved)', ms, before, after};"})
    shot("f11-after-reset-view")
    a.append({"js": "await press('flat'); L.S.v2.x = 1.2; L.S.v2.h = 0.4; L.touch(); await settle(); const b = {...L.S.v2}; const ms = await press('reset'); const r = {f: 'Reset view in the 2D view', ms, before: b, after: {...L.S.v2}}; return r;"})
    shot("f11-after-reset-view-2d")
    a.append({"js": "await press('flat'); const b = document.querySelector('#ballsReset button'); b.click(); const ms = await settle(); return {f: 'Reset this section (Kleinian panel)', ms, ...st(), cam: [L.cam.yaw, L.cam.pitch, +L.cam.dist.toFixed(2)]};"})
    shot("f11-after-panel-reset")
    a.append({"js": "await slide('ballsSize', 30); await pick('ballsGrid', 2); await pick('col-mode', 2); const before = st(); const ms = await press('resetAll'); window.scrollTo(0, 0); return {f: 'Reset everything from Balls on balls', ms, before, after: st(), apName: document.getElementById('apMenuName').textContent, modeChecked: [...document.querySelectorAll('input[name=mode]')].filter(i => i.checked).map(i => i.id), colourMode: L.S.colour.mode};"})
    shot("f11-after-reset-everything", None)
    a.append({"js": "await press('mode-k'); window.scrollTo(0, 0); return {f: 'Kleinian after Reset everything', group0: document.getElementById('kleinGroup0').checked, ...st()};"})
    shot("f11-kleinian-after-reset-everything", None)

    # ---- F12: the Learn tab, from the old group and from Balls on balls
    a.append({"js": "const grab = () => ({ bodyLearn: document.body.classList.contains('is-learn'), learnOn: !!(L.learn && L.learn.state && L.learn.state().on), modeChecked: [...document.querySelectorAll('input[name=mode]')].filter(i => i.checked).map(i => i.id), apShown: shown(document.getElementById('secApproach')), apName: document.getElementById('apMenuName').textContent, kleinPanelShown: shown(document.getElementById('kleinPanel')), firstWords: texts('#sections').slice(0, 14), ...st() }); window.grabLearn = grab; document.getElementById('mode-l').click(); await sleep(1200); const old = grab(); return {f: 'Learn from the old Kleinian group', old};"})
    shot("f12-learn-from-old-group", None)
    a.append({"js": "document.getElementById('mode-k').click(); await settle(); const backOld = st(); await press('kleinGroup1'); document.getElementById('mode-l').click(); await sleep(1200); window.scrollTo(0, 0); return {f: 'Learn from Balls on balls', backOld, balls: window.grabLearn()};"})
    shot("f12-learn-from-balls", None)
    a.append({"js": "document.getElementById('apMenuBtn').scrollIntoView({block: 'start'}); await sleep(200); document.getElementById('apMenuBtn').click(); await sleep(300); return {f: 'Approach menu under Learn with Balls on balls behind', popHidden: document.getElementById('apPop').hidden, rowShown: shown(document.getElementById('ap-balls')), rowOn: document.getElementById('apBallsRow').className, ticked: [...document.querySelectorAll('#rules input:checked')].map(i => i.id)};"})
    shot("f12-learn-menu", None)
    a.append({"js": "document.getElementById('apMenuBtn').click(); await sleep(200); document.getElementById('mode-k').click(); await settle(); window.scrollTo(0, 0); return {f: 'Kleinian button after Learn', ...st(), group1: document.getElementById('kleinGroup1').checked};"})
    shot("f12-kleinian-after-learn", None)
    write("s5b-feat", a)


if __name__ == "__main__":
    part_a()
    part_b()

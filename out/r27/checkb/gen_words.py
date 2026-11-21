"""Writes steps/s4-words.json: every new word on the screen, and the layout of the new controls (boxes measured)."""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
SH = "out/r27/checkb/shots/s4-@T-"

HELPERS = r"""
window.L = window.squaringLab;
window.sleep = ms => new Promise(r => setTimeout(r, ms));
window.settle = async () => { const t0 = performance.now(); await sleep(80); while (!L.idle()) await sleep(25); return Math.round(performance.now() - t0); };
window.press = async id => { document.getElementById(id).click(); return await settle(); };
window.shown = e => { if (!e) return false; for (let x = e; x && x.nodeType === 1; x = x.parentElement) { if (x.hidden) return false; const cs = getComputedStyle(x); if (cs.display === 'none' || cs.visibility === 'hidden') return false; if (x.tagName === 'DETAILS' && !x.open && e !== x && !(x.querySelector('summary') && x.querySelector('summary').contains(e))) return false; } const b = e.getBoundingClientRect(); return b.width > 0 && b.height > 0; };
window.texts = sel => { const out = []; document.querySelectorAll(sel).forEach(root => { const w = document.createTreeWalker(root, NodeFilter.SHOW_TEXT); let n; while ((n = w.nextNode())) { const t = n.textContent.replace(/\s+/g, ' ').trim(); if (t && shown(n.parentElement)) out.push(t); } }); return out; };
window.titles = sel => { const out = []; document.querySelectorAll(sel).forEach(root => { [root, ...root.querySelectorAll('[title], [aria-label]')].forEach(e => { if (!shown(e)) return; for (const a of ['title', 'aria-label']) { const t = e.getAttribute && e.getAttribute(a); if (t) out.push((e.id || e.tagName.toLowerCase()) + ' @' + a + ': ' + t); } }); }); return out; };
window.boxes = ids => { const W = innerWidth, res = {}; for (const id of ids) { const e = id.startsWith('#') || id.startsWith('.') ? document.querySelector(id) : document.getElementById(id); if (!e) { res[id] = 'MISSING'; continue; } const b = e.getBoundingClientRect(); res[id] = { x0: Math.round(b.left), x1: Math.round(b.right), w: Math.round(b.width), h: Math.round(b.height), shown: shown(e), outRight: b.right > W + 0.5, outLeft: b.left < -0.5, clipX: e.scrollWidth > e.clientWidth + 1, clipY: e.scrollHeight > e.clientHeight + 1 && getComputedStyle(e).overflowY !== 'visible' }; } return res; };
window.overlaps = sel => { const es = [...document.querySelectorAll(sel)].filter(shown), bad = []; for (let i = 0; i < es.length; i++) for (let j = i + 1; j < es.length; j++) { const a = es[i], b = es[j]; if (a.contains(b) || b.contains(a)) continue; const p = a.getBoundingClientRect(), q = b.getBoundingClientRect(); const ox = Math.min(p.right, q.right) - Math.max(p.left, q.left), oy = Math.min(p.bottom, q.bottom) - Math.max(p.top, q.top); if (ox > 1.5 && oy > 1.5) bad.push([(a.id || a.className || a.tagName) + ' | ' + (b.id || b.className || b.tagName), Math.round(ox), Math.round(oy)]); } return bad; };
"""

NEW = ["kleinGroup", "kleinGroup0", "kleinGroup1", ".kgroup-tag", "ballsNote", "ballsWarn", "ballsDials", "ballsSize", "ballsSizeNum", "ballsSizeHelp",
       "ballsGrid", "ballsGridHelp", "ballsDepth", "ballsDepthNum", "ballsDepthHelp", "ballsFrame", "#ballsReset button"]
LEAVES = "#ballsPart label, #ballsPart .dial-box, #ballsPart input[type=range], #ballsPart select, #ballsPart p, #ballsPart button.btn, #kleinGroup label, #kleinGroup legend"


def main():
    a = [{"wait": "done", "timeout": 100},
         {"js": HELPERS + "document.getElementById('apMenuBtn').click(); await sleep(250); return {menuBoxes: boxes(['apPop', 'apg-cousin', 'apgh-cousin', 'apBallsRow', 'ap-balls', '.cousin-tag']), menuTexts: texts('#apg-cousin'), menuTitles: titles('#apg-cousin'), pageWider: document.documentElement.scrollWidth - innerWidth};"},
         {"js": "document.getElementById('ap-balls').scrollIntoView({block: 'center'}); await sleep(300);"},
         {"shot": SH + "0-menu-row.png"},
         {"js": "await press('ap-balls'); window.scrollTo(0, 0); await sleep(200); return {mode: L.S.mode, group: L.S.k.group};"},
         {"shot": SH + "1-top.png"}]
    for i, anchor in enumerate(["kleinGroup", "ballsNote", "ballsSize", "ballsGrid", "ballsDepth", "ballsFrame", "secApproach"]):
        a.append({"js": "document.getElementById('%s').scrollIntoView({block: 'center'}); await sleep(300);" % anchor})
        a.append({"shot": SH + "2-panel-%d-%s.png" % (i, anchor)})
    a.append({"js": "return {panelTexts: texts('#kleinPanel'), panelTitles: titles('#kleinPanel')};"})
    a.append({"js": "return {approachTexts: texts('#secApproach'), approachTitles: titles('#apMenu')};"})
    a.append({"js": "return {flatLabel: texts('#flatHost'), status: document.getElementById('status').textContent, stageHint: texts('#stage'), stageTitles: titles('#stage'), canvasLabel: document.getElementById('view').getAttribute('aria-label')};"})
    a.append({"js": "return {boxes: boxes(%s), overlaps: overlaps(%s), pageWider: document.documentElement.scrollWidth - innerWidth, win: [innerWidth, innerHeight]};" % (json.dumps(NEW), json.dumps(LEAVES))})
    # the warning line on show (neighbours at 100), and its layout
    a.append({"js": "const r = document.getElementById('ballsSize'); r.value = 100; r.dispatchEvent(new Event('input', {bubbles: true})); await settle(); document.getElementById('ballsWarn').scrollIntoView({block: 'center'}); await sleep(300); return {warn: texts('#ballsWarn'), boxes: boxes(['ballsWarn', 'ballsNote', 'ballsSize']), overlaps: overlaps(%s)};" % json.dumps(LEAVES)})
    a.append({"shot": SH + "3-warning.png"})
    # the menu while Balls on balls is on show
    a.append({"js": "document.querySelector('#ballsReset button').click(); await settle(); document.getElementById('apMenuBtn').scrollIntoView({block: 'start'}); await sleep(200); document.getElementById('apMenuBtn').click(); await sleep(300); return {menuTexts: texts('#apPop').slice(-6), popHidden: document.getElementById('apPop').hidden, boxes: boxes(['apPop', 'ap-balls', 'apBallsRow', 'apMenuName']), ticked: [...document.querySelectorAll('#rules input:checked')].length, rowOn: document.getElementById('apBallsRow').className};"})
    a.append({"shot": SH + "4-menu-while-on.png"})
    a.append({"js": "document.getElementById('ap-balls').scrollIntoView({block: 'center'}); await sleep(300);"})
    a.append({"shot": SH + "4-menu-while-on-row.png"})
    with open(os.path.join(HERE, "steps", "s4-words.json"), "w", encoding="utf-8") as f:
        json.dump(a, f, indent=1)
    print(len(a), "steps")


if __name__ == "__main__":
    main()

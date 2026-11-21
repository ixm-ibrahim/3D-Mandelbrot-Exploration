"""Write the step files for out/r7/camera/drive.py. Usage: python out/r7/camera/gen.py <tag>
<tag> goes into the picture names, e.g. v6 or r7, so the before and after pictures sit side by side."""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
tag = sys.argv[1] if len(sys.argv) > 1 else "v6"
P = "out/r7/camera/"

HELP = r"""
window.T = {};
const L = window.squaringLab, $ = id => document.getElementById(id);
T.sel = (id, v) => { const e = $(id); if (!e) throw new Error('no control ' + id); e.value = String(v); e.dispatchEvent(new Event('change', { bubbles: true })); };
T.type = (id, v) => { const e = $(id); if (!e) throw new Error('no control ' + id); e.value = v; e.dispatchEvent(new Event('input', { bubbles: true })); e.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', bubbles: true })); };
// the boxes of the picture's own controls, relative to the stage: [id, left, right, top, bottom]
T.boxes = () => { const s = $('stage').getBoundingClientRect(); const out = { stage: [Math.round(s.width), Math.round(s.height)], coarse: matchMedia('(pointer: coarse)').matches };
  for (const id of ['camArc', 'camFly', 'camNear', 'camRail', 'camThumb', 'camVal', 'camFar', 'camEndA', 'camEndB', 'zoomOut', 'zoomIn', 'reset', 'triad', 'camZoom']) { const e = $(id); if (!e) { out[id] = null; continue; } const r = e.getBoundingClientRect(); out[id] = r.width ? [Math.round(r.left - s.left), Math.round(r.right - s.left), Math.round(r.top - s.top), Math.round(r.bottom - s.top)] : 'not shown'; }
  return out; };
// share of the picture covered by anything of its own that is on show (the layout tester's measure, 75 x 75 grid)
T.cover = () => { const st = $('stage'), sr = st.getBoundingClientRect();
  const visible = e => { if (!e.getClientRects().length) return false; const s = getComputedStyle(e); if (s.visibility === 'hidden') return false; const r = e.getBoundingClientRect(); return r.width > 0.5 && r.height > 0.5; };
  const lay = [...st.querySelectorAll('*')].filter(e => visible(e) && e.tagName !== 'CANVAS' && !e.closest('svg') || (e.tagName === 'svg' && visible(e)));
  const leaf = lay.filter(e => e.tagName === 'svg' || e.matches('button, input, p, span, output, label') || e.childElementCount === 0);
  const gw = 75, gh = 75, cell = new Uint8Array(gw * gh);
  for (const e of leaf) { const r = e.getBoundingClientRect(); const x0 = Math.max(0, Math.floor((r.left - sr.left) / sr.width * gw)), x1 = Math.min(gw, Math.ceil((r.right - sr.left) / sr.width * gw)), y0 = Math.max(0, Math.floor((r.top - sr.top) / sr.height * gh)), y1 = Math.min(gh, Math.ceil((r.bottom - sr.top) / sr.height * gh)); for (let y = y0; y < y1; y++) for (let x = x0; x < x1; x++) cell[y * gw + x] = 1; }
  return Math.round(cell.reduce((a, b) => a + b, 0) / (gw * gh) * 1000) / 10; };
// where the solid is in the picture: the box of the pick probes that hit, in stage pixels, on a 40 x 40 grid
T.extent = () => { const w = $('stage').clientWidth, h = $('stage').clientHeight, n = 40; let x0 = 1e9, x1 = -1, y0 = 1e9, y1 = -1, hits = 0;
  for (let i = 0; i <= n; i++) for (let j = 0; j <= n; j++) { const x = (w - 1) * i / n, y = (h - 1) * j / n; if (L.pick(x, y)) { hits++; x0 = Math.min(x0, x); x1 = Math.max(x1, x); y0 = Math.min(y0, y); y1 = Math.max(y1, y); } }
  return { w, h, hits, of: (n + 1) * (n + 1), x: [Math.round(x0), Math.round(x1)], y: [Math.round(y0), Math.round(y1)], dist: +L.cam.dist.toFixed(3), target: L.cam.target.map(v => +v.toFixed(3)) }; };
// which controls of the picture lie over a spot the solid is drawn at (pick probes under each control's box)
T.under = () => { const s = $('stage').getBoundingClientRect(), out = {};
  for (const id of ['camArc', 'camFly', 'camNear', 'camRail', 'camVal', 'camFar', 'zoomOut', 'zoomIn', 'reset', 'triad']) { const e = $(id); if (!e) continue; const r = e.getBoundingClientRect(); if (!r.width) continue;
    if (r.top - s.top >= s.height || r.left - s.left >= s.width) { out[id] = 'outside the picture'; continue; }
    let hit = 0, n = 0; for (let i = 0; i <= 6; i++) for (let j = 0; j <= 6; j++) { n++; if (L.pick(r.left - s.left + r.width * i / 6, r.top - s.top + r.height * j / 6)) hit++; } out[id] = hit + '/' + n; }
  return out; };
return 'helpers ready';
"""


def write(name, steps):
    for st in steps[1:]:
        if "js" in st:
            st["js"] = "const L = window.squaringLab; " + st["js"]
    with open(os.path.join(HERE, name), "w", encoding="utf-8") as f:
        json.dump(steps, f, ensure_ascii=False, indent=1)


first = [{"js": HELP, "wait": "done", "timeout": 180}]

# layout-1 and words-2: the phone picture, opening view and Figure 4, then Kleinian
write("phone.json", first + [
    {"js": "return { boxes: T.boxes(), cover: T.cover(), extent: T.extent(), under: T.under() };"},
    {"js": "scrollTo(0, 0);", "sleep": 0.3, "shot": P + tag + "-phone-open-window.png"},
    {"shot": P + tag + "-phone-open.png", "clip": "#stage"},
    {"js": "document.getElementById('fig4Show').click();", "sleep": 1.2, "wait": "done", "timeout": 180},
    {"js": "return { extent: T.extent(), under: T.under() };"},
    {"shot": P + tag + "-phone-fig4.png", "clip": "#stage"},
    {"js": "document.getElementById('mode-k').click();", "sleep": 0.5, "wait": "done", "timeout": 180},
    {"js": "return { boxes: T.boxes(), cover: T.cover(), extent: T.extent(), under: T.under() };"},
    {"shot": P + tag + "-phone-klein.png", "clip": "#stage"},
    {"js": "document.getElementById('mode-j').click();", "sleep": 0.5, "wait": "done", "timeout": 180},
    {"js": "return { extent: T.extent(), under: T.under() };"},
    {"shot": P + tag + "-phone-julia.png", "clip": "#stage"},
    {"js": "document.getElementById('mode-m').click(); document.getElementById('flat').click();", "sleep": 0.5, "wait": "done", "timeout": 180},
    {"js": "return { boxes: T.boxes(), cover: T.cover() };"},
    {"shot": P + tag + "-phone-2d.png", "clip": "#stage"},
])

# layout-5: the keyboard walk through the picture
write("tab.json", first + [
    {"js": "scrollTo(0, 0); document.getElementById('view').focus(); return document.activeElement.id;", "tab": 9},
])

# solids-7: trap solids at the sizes the tester found cut off
write("solids.json", first + [
    {"js": "document.getElementById('mode-j').click(); T.type('cxNum', '-1'); T.type('cyNum', '0'); T.type('czNum', '0'); T.sel('col-trap', 5); T.sel('col-solid', 1); T.type('col-radiusNum', '0.7'); return [L.cam.dist, L.S.colour.radius];", "sleep": 0.4, "wait": "done", "timeout": 240},
    {"js": "return T.extent();", "shot": P + tag + "-s-j-r0.7.png", "clip": "#stage"},
    {"js": "T.type('col-radiusNum', '1.5'); return L.cam.dist;", "sleep": 0.4, "wait": "done", "timeout": 240},
    {"js": "return T.extent();", "shot": P + tag + "-s-j-r1.5-dial.png", "clip": "#stage"},
    {"js": "document.getElementById('reset').click(); return L.cam.dist;", "sleep": 0.4, "wait": "done", "timeout": 240},
    {"js": "return T.extent();", "shot": P + tag + "-s-j-r1.5-reset.png", "clip": "#stage"},
    {"js": "T.type('col-radiusNum', '2'); document.getElementById('reset').click(); return L.cam.dist;", "sleep": 0.4, "wait": "done", "timeout": 240},
    {"js": "return T.extent();", "shot": P + tag + "-s-j-r2-reset.png", "clip": "#stage"},
    {"js": "T.type('col-radiusNum', '1'); document.getElementById('mode-k').click(); T.sel('col-trap', 6); T.sel('col-solid', 1); return [L.cam.dist, L.S.colour.radius, L.S.colour.thick];", "sleep": 0.4, "wait": "done", "timeout": 240},
    {"js": "return T.extent();", "shot": P + tag + "-s-k-base.png", "clip": "#stage"},
    {"js": "T.type('col-thickNum', '0.2'); document.getElementById('reset').click(); return L.cam.dist;", "sleep": 0.4, "wait": "done", "timeout": 240},
    {"js": "return T.extent();", "shot": P + tag + "-s-k-thick0.2.png", "clip": "#stage"},
    {"js": "T.type('col-thickNum', '0.05'); T.type('col-radiusNum', '1.6'); document.getElementById('reset').click(); return L.cam.dist;", "sleep": 0.4, "wait": "done", "timeout": 240},
    {"js": "return T.extent();", "shot": P + tag + "-s-k-r1.6.png", "clip": "#stage"},
    {"js": "T.type('col-radiusNum', '1'); T.type('col-txNum', '0.6'); document.getElementById('reset').click(); return L.cam.dist;", "sleep": 0.4, "wait": "done", "timeout": 240},
    {"js": "return T.extent();", "shot": P + tag + "-s-k-tx0.6.png", "clip": "#stage"},
])
print("wrote phone.json, tab.json, solids.json for tag", tag)

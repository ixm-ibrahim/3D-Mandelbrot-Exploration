"""Tester "layout", round 6: drive dist/v6.html at one size and theme, audit the layout by numbers, keep pictures.

  python out/t6/layout/lay.py 1400x950 dark          # states m3d j3d k3d m2d j2d k2d + specials, audits + band pictures
  python out/t6/layout/lay.py 375x812 light --phone  # the same as a touch phone (pointer: coarse)
  python out/t6/layout/lay.py 1400x950 dark --tab    # only the keyboard walk (real Tab presses)

Writes out/t6/layout/raw/<tag>-<state>-<nn>.png (what the window shows at successive scroll positions),
out/t6/layout/audit-<tag>.json (numbers) and prints a summary.
"""
import json, os, socket, subprocess, sys, tempfile, time, shutil, urllib.request, base64

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
from shot import WS, Page, CHROMES  # noqa: E402

URL = "file:///" + os.path.join(ROOT, "dist", "v6.html").replace("\\", "/")
RAW = os.path.join(HERE, "raw")
os.makedirs(RAW, exist_ok=True)

PRE = r"""
const L = window.squaringLab, S = L.S, $ = id => document.getElementById(id);
const sleep = ms => new Promise(r => setTimeout(r, ms));
const pick = (id, text) => { const e = $(id); if (!e) throw new Error('no control ' + id); const o = [...e.options].find(x => x.text.startsWith(text)); if (!o) throw new Error('no option ' + text + ' in ' + id); e.value = o.value; e.dispatchEvent(new Event('change', { bubbles: true })); };
const tick = (id, on) => { const e = $(id); if (!e) throw new Error('no control ' + id); if (e.checked !== on) e.click(); };
const openAll = () => document.querySelectorAll('#sections > details.sec').forEach(d => { d.open = true; });
const mode = m => { $('mode-' + m).click(); };
"""

AUDIT = r"""
const de = document.documentElement, vw = de.clientWidth, vh = innerHeight, sx = scrollX, sy = scrollY;
const res = { vw, vh, scrollW: de.scrollWidth, bodyScrollW: document.body.scrollWidth, pageH: de.scrollHeight,
  coarse: matchMedia('(pointer: coarse)').matches, dark: matchMedia('(prefers-color-scheme: dark)').matches };
const visible = e => { if (!e.getClientRects().length) return false; const s = getComputedStyle(e); if (s.visibility === 'hidden') return false; const r = e.getBoundingClientRect(); return r.width > 0.5 && r.height > 0.5; };
const RR = e => { const r = e.getBoundingClientRect(); return [Math.round(r.left + sx), Math.round(r.top + sy), Math.round(r.right + sx), Math.round(r.bottom + sy)]; };
const desc = e => e.id ? '#' + e.id : e.tagName.toLowerCase() + (typeof e.className === 'string' && e.className.trim() ? '.' + e.className.trim().split(/\s+/).join('.') : '');
const where = e => { let p = desc(e), a = e.parentElement, n = 0; if (e.id) return p; while (a && n < 4) { p = desc(a) + ' > ' + p; if (a.id) break; a = a.parentElement; n++; } return p; };
const txt = e => (e.textContent || '').replace(/\s+/g, ' ').trim().slice(0, 60);
const clipAnc = e => { for (let a = e.parentElement; a && a !== document.body; a = a.parentElement) { const s = getComputedStyle(a); if (/(hidden|clip|auto|scroll)/.test(s.overflowX)) return a; } return null; };
const all = [...document.body.querySelectorAll('*')].filter(e => !['SCRIPT', 'STYLE', 'OPTION', 'OPTGROUP', 'TITLE', 'META'].includes(e.tagName) && visible(e));

// 1. things that stick out of the window sideways, or are cut by a clipping parent
res.offside = []; res.cut = [];
for (const e of all) {
  const r = e.getBoundingClientRect(), l = r.left + sx, rt = r.right + sx;
  const ca = clipAnc(e);
  if (ca) {
    const c = ca.getBoundingClientRect();
    if ((r.right > c.right + 1.5 || r.left < c.left - 1.5 || r.bottom > c.bottom + 1.5 || r.top < c.top - 1.5) && (e.matches('button,input,select,textarea,a,label,p,span,summary,dt,dd,h2,h3,text') || e.childElementCount === 0))
      res.cut.push({ el: where(e), by: desc(ca), box: RR(e), clip: [Math.round(c.left + sx), Math.round(c.top + sy), Math.round(c.right + sx), Math.round(c.bottom + sy)], text: txt(e) });
    continue;
  }
  if (rt > vw + 1.5 || l < -1.5) res.offside.push({ el: where(e), box: RR(e), text: txt(e) });
}
// 2. text that does not fit its own box
res.squeezed = [];
for (const e of all) {
  const s = getComputedStyle(e);
  if (e.tagName === 'INPUT' && /^(text|number|search|)$/.test(e.type || '')) {
    if (e.scrollWidth > e.clientWidth + 1) res.squeezed.push({ el: where(e), kind: 'input value wider than box', value: e.value, sw: e.scrollWidth, cw: e.clientWidth });
  } else if (e.tagName === 'SELECT') {
    const c = document.createElement('canvas').getContext('2d'); c.font = s.fontWeight + ' ' + s.fontSize + ' ' + s.fontFamily;
    const up = s.textTransform === 'uppercase', ls = parseFloat(s.letterSpacing) || 0;
    const room = e.clientWidth - parseFloat(s.paddingLeft) - parseFloat(s.paddingRight) - (s.appearance === 'none' ? 0 : 18);
    const wide = [...e.options].map(o => { const t = up ? o.text.toUpperCase() : o.text; return [o.text, Math.ceil(c.measureText(t).width + ls * t.length)]; }).filter(x => x[1] > room + 0.5).sort((a, b) => b[1] - a[1]);
    if (wide.length) res.squeezed.push({ el: where(e), kind: 'select options wider than the closed box', room: Math.round(room), count: wide.length, of: e.options.length, worst: wide.slice(0, 4) });
  } else if (/(hidden|clip)/.test(s.overflowX + s.overflowY) && e.childElementCount === 0 && txt(e)) {
    if (e.scrollWidth > e.clientWidth + 1 || e.scrollHeight > e.clientHeight + 1) res.squeezed.push({ el: where(e), kind: 'text cut by its own box', text: txt(e), sw: e.scrollWidth, cw: e.clientWidth, sh: e.scrollHeight, ch: e.clientHeight });
  } else if (e.tagName === 'BUTTON' && (e.scrollWidth > e.clientWidth + 1)) {
    res.squeezed.push({ el: where(e), kind: 'button text wider than button', text: txt(e), sw: e.scrollWidth, cw: e.clientWidth });
  }
}
// 3. controls: inventory, names, labels, sizes
const ctrls = all.filter(e => e.matches('button, input:not([type=hidden]), select, textarea, summary, a[href], [role=slider], [role=button], canvas[tabindex], [contenteditable=true]'));
const accName = e => {
  const lb = e.getAttribute('aria-labelledby'); if (lb) return lb.split(/\s+/).map(i => ($(i) || {}).textContent || '').join(' ').replace(/\s+/g, ' ').trim();
  if (e.getAttribute('aria-label')) return e.getAttribute('aria-label').trim();
  if (e.id) { const l = document.querySelector('label[for="' + CSS.escape(e.id) + '"]'); if (l) return txt(l); }
  const wl = e.closest('label'); if (wl) return txt(wl);
  if (e.tagName === 'BUTTON' || e.tagName === 'SUMMARY' || e.tagName === 'A') return txt(e);
  if (e.title) return e.title.trim();
  if (e.placeholder) return '(placeholder only) ' + e.placeholder;
  return '';
};
const visLabel = e => {
  if (e.tagName === 'BUTTON' || e.tagName === 'SUMMARY' || e.tagName === 'A') return txt(e);
  if (e.id) { const l = document.querySelector('label[for="' + CSS.escape(e.id) + '"]'); if (l && visible(l)) return txt(l); }
  const wl = e.closest('label'); if (wl && visible(wl)) return txt(wl);
  const lb = e.getAttribute('aria-labelledby'); if (lb) { const t = lb.split(/\s+/).map(i => $(i)).filter(x => x && visible(x)).map(x => txt(x)).join(' '); if (t) return t; }
  return '';
};
res.controls = ctrls.map(e => { const b = RR(e); return { el: where(e), tag: e.tagName.toLowerCase(), type: e.type || '', name: accName(e), label: visLabel(e), box: b, w: b[2] - b[0], h: b[3] - b[1], dis: !!e.disabled, tab: e.tabIndex }; });
res.noName = res.controls.filter(c => !c.name).map(c => c.el);
res.noVisibleLabel = res.controls.filter(c => !c.label).map(c => c.el + ' [' + c.name + ']');
res.smallTargets = res.controls.filter(c => (c.w < 24 || c.h < 24) && c.tag !== 'summary').map(c => c.el + ' ' + c.w + 'x' + c.h + ' [' + (c.name || '').slice(0, 30) + ']');
// 4. overlaps between controls, and between controls and text blocks
const inTop = e => !!e.closest('#toprow');
const rel = (a, b) => a.contains(b) || b.contains(a);
const hit = (a, b) => { const p = a.getBoundingClientRect(), q = b.getBoundingClientRect(); const w = Math.min(p.right, q.right) - Math.max(p.left, q.left), h = Math.min(p.bottom, q.bottom) - Math.max(p.top, q.top); return w > 2 && h > 2 ? [Math.round(w), Math.round(h)] : null; };
res.overlap = [];
for (let i = 0; i < ctrls.length; i++) for (let j = i + 1; j < ctrls.length; j++) {
  const a = ctrls[i], b = ctrls[j]; if (rel(a, b) || inTop(a) !== inTop(b)) continue;
  if (a.tagName === 'CANVAS' || b.tagName === 'CANVAS') continue;
  const h = hit(a, b); if (h) res.overlap.push({ a: where(a), b: where(b), by: h });
}
const blocks = all.filter(e => e.matches('p, label, legend, dt, dd, figcaption, h1, h2, h3, li, span, code, output') && [...e.childNodes].some(n => n.nodeType === 3 && n.nodeValue.trim()));
res.textOverControl = [];
for (const t of blocks) for (const c of ctrls) {
  if (rel(t, c) || inTop(t) !== inTop(c) || c.tagName === 'CANVAS') continue;
  if (t.tagName === 'LABEL' && t.htmlFor && t.htmlFor === c.id) { const h = hit(t, c); if (h) res.textOverControl.push({ text: where(t) + ' "' + txt(t) + '"', ctrl: where(c), by: h, own: true }); continue; }
  const h = hit(t, c); if (h) res.textOverControl.push({ text: where(t) + ' "' + txt(t) + '"', ctrl: where(c), by: h });
}
res.textOverText = [];
for (let i = 0; i < blocks.length; i++) for (let j = i + 1; j < blocks.length; j++) {
  const a = blocks[i], b = blocks[j]; if (rel(a, b) || inTop(a) !== inTop(b)) continue;
  const h = hit(a, b); if (h && h[0] > 4 && h[1] > 4) res.textOverText.push({ a: where(a) + ' "' + txt(a) + '"', b: where(b) + ' "' + txt(b) + '"', by: h });
}
// 5. the picture's own controls
const st = $('stage'), sr = st.getBoundingClientRect();
res.stage = { box: RR(st), items: [] };
const lay = [...st.querySelectorAll('*')].filter(e => visible(e) && e.tagName !== 'CANVAS' && !e.closest('svg') || (e.tagName === 'svg' && visible(e)));
const leaf = lay.filter(e => e.tagName === 'svg' || e.matches('button, input, p, span, output, label') || e.childElementCount === 0);
res.stage.items = leaf.map(e => { const r = e.getBoundingClientRect(); const s = getComputedStyle(e); return { el: where(e), text: txt(e), box: [Math.round(r.left - sr.left), Math.round(r.top - sr.top), Math.round(r.right - sr.left), Math.round(r.bottom - sr.top)], bg: s.backgroundColor, fg: s.color, fs: s.fontSize }; });
res.stage.clash = [];
for (let i = 0; i < leaf.length; i++) for (let j = i + 1; j < leaf.length; j++) { const a = leaf[i], b = leaf[j]; if (rel(a, b)) continue; const h = hit(a, b); if (h) res.stage.clash.push({ a: where(a) + ' "' + txt(a).slice(0, 30) + '"', b: where(b) + ' "' + txt(b).slice(0, 30) + '"', by: h }); }
let cover = 0; { // share of the picture covered by its own controls (union by a coarse grid)
  const gw = 75, gh = 75, cell = new Uint8Array(gw * gh);
  for (const e of leaf) { const r = e.getBoundingClientRect(); const x0 = Math.max(0, Math.floor((r.left - sr.left) / sr.width * gw)), x1 = Math.min(gw, Math.ceil((r.right - sr.left) / sr.width * gw)), y0 = Math.max(0, Math.floor((r.top - sr.top) / sr.height * gh)), y1 = Math.min(gh, Math.ceil((r.bottom - sr.top) / sr.height * gh)); for (let y = y0; y < y1; y++) for (let x = x0; x < x1; x++) cell[y * gw + x] = 1; }
  cover = cell.reduce((a, b) => a + b, 0) / (gw * gh);
}
res.stage.covered = Math.round(cover * 1000) / 10;
// 6. contrast of every text against what is behind it
const parse = c => { const m = /rgba?\(([^)]+)\)/.exec(c); if (!m) return null; const p = m[1].split(/[,\s\/]+/).filter(Boolean).map(Number); return [p[0], p[1], p[2], p.length > 3 ? p[3] : 1]; };
const over = (f, b) => { const a = f[3]; return [f[0] * a + b[0] * (1 - a), f[1] * a + b[1] * (1 - a), f[2] * a + b[2] * (1 - a), 1]; };
const lum = c => { const f = v => { v /= 255; return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); }; return 0.2126 * f(c[0]) + 0.7152 * f(c[1]) + 0.0722 * f(c[2]); };
const ratio = (a, b) => { const x = lum(a), y = lum(b); return (Math.max(x, y) + 0.05) / (Math.min(x, y) + 0.05); };
const rootBg = (() => { for (const e of [document.body, de]) { const c = parse(getComputedStyle(e).backgroundColor); if (c && c[3] > 0.99) return c; } return res.dark ? [18, 18, 18, 1] : [255, 255, 255, 1]; })();
res.rootBg = rootBg; res.pageBg = getComputedStyle(document.querySelector('.page') || document.body).backgroundColor;
const bgOf = e => { const layers = []; let base = null, solid = true;
  for (let a = e; a; a = a.parentElement) {
    const c = parse(getComputedStyle(a).backgroundColor);
    if (a.id === 'stage' && a !== e) { solid = false; base = c && c[3] > 0.99 ? c : rootBg; break; }
    if (c && c[3] > 0) { if (c[3] > 0.99) { base = c; break; } layers.push(c); }
  }
  if (!base) base = rootBg;
  for (let i = layers.length - 1; i >= 0; i--) base = over(layers[i], base);
  return { c: base, solid }; };
const groups = {};
for (const e of all) {
  if (![...e.childNodes].some(n => n.nodeType === 3 && n.nodeValue.trim())) { if (!(e.tagName === 'INPUT' && e.value && /^(text|)$/.test(e.type || '')) && e.tagName !== 'SELECT') continue; }
  if (e.closest('svg') && e.tagName !== 'text') continue;
  const s = getComputedStyle(e); let fg = parse(e.tagName === 'text' ? s.fill : s.color); if (!fg) continue;
  let op = 1; for (let a = e; a; a = a.parentElement) op *= +getComputedStyle(a).opacity;
  const bg = bgOf(e); fg = [fg[0], fg[1], fg[2], fg[3] * op]; const f2 = over(fg, bg.c);
  const size = parseFloat(s.fontSize), bold = (+s.fontWeight || 400) >= 700, big = size >= 24 || (size >= 18.66 && bold);
  const r = ratio(f2, bg.c), need = big ? 3 : 4.5;
  const k = [desc(e.id && /\d|-/.test(e.id) ? { tagName: e.tagName, className: e.className, id: '' } : e), s.color, bg.c.map(Math.round).slice(0, 3).join(','), size, bold ? 'b' : '', e.disabled || e.closest('[aria-disabled=true]') ? 'disabled' : '', bg.solid ? '' : 'on-picture'].join('|');
  const g = groups[k] || (groups[k] = { el: where(e), n: 0, ratio: Math.round(r * 100) / 100, need, size, fg: s.color, op: Math.round(op * 100) / 100, bg: 'rgb(' + bg.c.map(Math.round).slice(0, 3).join(',') + ')', solid: bg.solid, dis: !!(e.disabled), text: txt(e) || e.value });
  g.n++;
}
res.lowContrast = Object.values(groups).filter(g => g.ratio < g.need).sort((a, b) => a.ratio - b.ratio);
res.onPicture = Object.values(groups).filter(g => !g.solid);
res.tinyText = Object.values(groups).filter(g => g.size < 11).map(g => ({ el: g.el, size: g.size, n: g.n, text: g.text }));
res.texts = Object.keys(groups).length;
return res;
"""


def launch(w, h, theme, phone=False):
    chrome = next((c for c in CHROMES if os.path.exists(c)), None)
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0)); port = probe.getsockname()[1]
    prof = tempfile.mkdtemp(prefix="laylab-")
    proc = subprocess.Popen([chrome, "--headless=new", "--remote-debugging-port=%d" % port, "--user-data-dir=" + prof,
                             "--no-first-run", "--no-default-browser-check", "--disable-extensions", "--hide-scrollbars",
                             "--window-size=%d,%d" % (w, h), "--force-device-scale-factor=1", "about:blank"],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    target = None
    for _ in range(100):
        try:
            with urllib.request.urlopen("http://127.0.0.1:%d/json/list" % port, timeout=2) as r:
                pages = [t for t in json.load(r) if t.get("type") == "page"]
            if pages:
                target = pages[0]["webSocketDebuggerUrl"]; break
        except Exception:
            pass
        time.sleep(0.2)
    page = Page(WS(target))
    page.call("Runtime.enable"); page.call("Log.enable"); page.call("Page.enable")
    page.call("Emulation.setDeviceMetricsOverride", width=w, height=h, deviceScaleFactor=1, mobile=bool(phone))
    if phone:
        page.call("Emulation.setTouchEmulationEnabled", enabled=True, maxTouchPoints=5)
    page.call("Emulation.setEmulatedMedia", features=[{"name": "prefers-color-scheme", "value": theme}])
    page.call("Emulation.setFocusEmulationEnabled", enabled=True)
    page.call("Page.navigate", url=URL)
    page.wait("document.readyState === 'complete'", 30)
    time.sleep(0.5)
    return page, proc, prof


def done(page, timeout=60):
    t0 = time.time()
    ok = page.wait("window.squaringLab && window.squaringLab.idle && window.squaringLab.idle()", timeout)
    return ok, time.time() - t0


def bands(page, tag, state, h, most=40):
    """What the window shows at successive scroll positions."""
    page.js("scrollTo(0, 0); await new Promise(r => setTimeout(r, 120));")
    H = page.js("return document.documentElement.scrollHeight;")
    step = h - 120
    y, k, out = 0, 0, []
    while k < most:
        page.js("scrollTo(0, %d); await new Promise(r => setTimeout(r, 140));" % y)
        real = page.js("return Math.round(scrollY);")
        path = os.path.join(RAW, "%s-%s-%02d.png" % (tag, state, k))
        data = page.call("Page.captureScreenshot", format="png")["data"]
        with open(path, "wb") as f:
            f.write(base64.b64decode(data))
        out.append([os.path.relpath(path, ROOT).replace("\\", "/"), real])
        k += 1
        if real + h >= H - 1:
            break
        y = real + step
    page.js("scrollTo(0, 0);")
    return out, H


STATES = [
    ("m3d", "mode('m'); tick('flat', false); openAll();"),
    ("j3d", "mode('j'); tick('flat', false); openAll();"),
    ("k3d", "mode('k'); tick('flat', false); openAll();"),
    ("m2d", "mode('m'); tick('flat', true); openAll();"),
    ("j2d", "mode('j'); tick('flat', true); openAll();"),
    ("k2d", "mode('k'); tick('flat', true); openAll();"),
]

SPECIAL = [
    # every new part showing as much as it can: extreme ranges on, a trap that is the solid, the cut open with the cut-face box,
    # a saved Julia point chosen (Delete shows), a long Kleinian name, and both file panels after a finished job
    ("jx3d", """mode('j'); tick('flat', false); openAll(); tick('extreme', true);
      pick('col-solid', 'Is the solid'); const cut = [...document.querySelectorAll('#cutDials input[type=checkbox]')][0]; if (cut && !cut.checked) cut.click();
      await sleep(300); const cf = $('col-cutFace'); if (cf && !cf.checked) cf.click();
      $('juliaName').value = 'A point with a fairly long name, to see'; $('juliaSave').click(); await sleep(300);
      return { del: !$('juliaDelete').hidden, found: !$('juliaFound').hidden, sel: $('juliaPreset').selectedOptions[0].text, note: $('extremeNote').textContent };"""),
    ("jfound", """tick('extreme', false); pick('col-solid', 'Colours the surface'); const o = [...$('juliaPreset').options].find(x => x.parentElement.label === 'Found with two planes'); $('juliaPreset').value = o.value; $('juliaPreset').dispatchEvent(new Event('change', { bubbles: true })); await sleep(300);
      return { found: !$('juliaFound').hidden, sel: o.text, note: $('juliaNote').textContent };"""),
    ("kx3d", """mode('k'); tick('flat', false); openAll(); tick('extreme', true); const os = [...$('kleinPreset').options]; const o = os.slice().sort((a, b) => b.text.length - a.text.length)[0]; $('kleinPreset').value = o.value; $('kleinPreset').dispatchEvent(new Event('change', { bubbles: true })); await sleep(300);
      const third = [...document.querySelectorAll('#kleinDials input[type=checkbox]')][0]; if (third && !third.checked) third.click();
      pick('col-solid', 'Is added to the solid');
      return { sel: o.text, n: os.length, note: $('kleinNote').textContent, warn: $('kleinWarn').hidden ? '' : $('kleinWarn').textContent };"""),
    ("m2dx", """mode('m'); tick('flat', true); openAll(); tick('extreme', true); pick('col-inMode', 'Orbit trap'); await sleep(300); const ip = $('col-inPal'); if (ip) { ip.selectedIndex = 3; ip.dispatchEvent(new Event('change', { bubbles: true })); } await sleep(300);
      return { inMode: !!$('col-inMode'), inPal: !!$('col-inPal'), inRev: !!$('col-inRev'), edge: !!$('col-edge'), glow: !!$('col-edgeGlow') };"""),
]

JOBS = """mode('m'); tick('flat', false); tick('extreme', false); openAll(); window.squaringLabSaveHook = (n, b) => { (window.__saved = window.__saved || []).push([n, b.size]); };
  window.squaringLabMeshTest = { cells: 48 };
  const sz = $('exportSize'); const opts = [...sz.options].map(o => o.text); const o = [...sz.options].find(x => /type|own|custom|choose/i.test(x.text)) || sz.options[sz.options.length - 1];
  sz.value = o.value; sz.dispatchEvent(new Event('change', { bubbles: true })); await sleep(200);
  const setNum = (id, v) => { const e = $(id + 'Num') || $(id); if (!e) return 'no ' + id; e.value = v; e.dispatchEvent(new Event('input', { bubbles: true })); e.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', bubbles: true })); e.dispatchEvent(new Event('change', { bubbles: true })); return e.id; };
  const a = setNum('exportW', 400), b = setNum('exportH', 300); pick('exportQuality', 'As on screen');
  await sleep(200); const note = $('exportSizeNote').textContent;
  $('exportStart').click(); await sleep(400); return { opts, chose: o.text, a, b, note, running: L.exportBusy && L.exportBusy() };"""


def main():
    size, theme = sys.argv[1], sys.argv[2]
    phone = "--phone" in sys.argv
    w, h = (int(x) for x in size.split("x"))
    tag = "%d%s%s" % (w, theme[0], "t" if phone else "")
    page, proc, prof = launch(w, h, theme, phone)
    report = {"tag": tag, "size": size, "theme": theme, "phone": phone, "states": {}}
    try:
        ok, t = done(page, 240)
        print("[%s] opened, idle=%s after %.0f s" % (tag, ok, t), flush=True)
        if "--tab" in sys.argv:
            tabwalk(page, tag, w, h, report)
        else:
            for name, js in STATES + SPECIAL:
                try:
                    val = page.js(PRE + js)
                except Exception as e:
                    val = "SCRIPT FAILED: %s" % e
                time.sleep(0.6)
                ok, t = done(page, 75)
                a = page.js(PRE + "openAll(); await sleep(150);" + AUDIT)
                shots, H = bands(page, tag, name, h)
                a["set"] = val; a["idle"] = ok; a["waited"] = round(t, 1); a["shots"] = shots
                report["states"][name] = a
                print("[%s] %s: idle=%s %.0fs  vw=%d scrollW=%d pageH=%d  offside=%d cut=%d squeezed=%d overlap=%d txt/ctrl=%d txt/txt=%d noName=%d lowContrast=%d stageClash=%d covered=%.1f%% bands=%d  set=%s" % (
                    tag, name, ok, t, a["vw"], a["scrollW"], a["pageH"], len(a["offside"]), len(a["cut"]), len(a["squeezed"]), len(a["overlap"]),
                    len(a["textOverControl"]), len(a["textOverText"]), len(a["noName"]), len(a["lowContrast"]), len(a["stage"]["clash"]), a["stage"]["covered"], len(shots), json.dumps(val, ensure_ascii=False)[:300]), flush=True)
            # the two file panels: while running, and when finished
            try:
                val = page.js(PRE + JOBS)
                a = page.js(PRE + AUDIT); a["set"] = val
                report["states"]["job-running"] = a
                page.js("document.getElementById('secExport').scrollIntoView({block: 'start'}); await new Promise(r => setTimeout(r, 200));")
                page.shot(os.path.join(RAW, "%s-job-running.png" % tag))
                page.wait("!window.squaringLab.exportBusy()", 240)
                page.js(PRE + "$('meshStart').click(); await sleep(300);")
                page.js("document.getElementById('secMesh').scrollIntoView({block: 'start'}); await new Promise(r => setTimeout(r, 200));")
                page.shot(os.path.join(RAW, "%s-mesh-running.png" % tag))
                page.wait("!window.squaringLab.meshBusy()", 240)
                time.sleep(0.5)
                a = page.js(PRE + "openAll(); await sleep(150);" + AUDIT)
                shots, H = bands(page, tag, "jobs-done", h)
                a["shots"] = shots
                a["set"] = page.js("return { exp: document.getElementById('exportPanel').innerText.slice(0, 900), mesh: document.getElementById('meshPanel').innerText.slice(0, 1500) };")
                report["states"]["jobs-done"] = a
                print("[%s] jobs-done: offside=%d cut=%d squeezed=%d overlap=%d lowContrast=%d bands=%d" % (tag, len(a["offside"]), len(a["cut"]), len(a["squeezed"]), len(a["overlap"]), len(a["lowContrast"]), len(shots)), flush=True)
            except Exception as e:
                print("[%s] jobs FAILED: %s" % (tag, e), flush=True)
        page.js("return 0;")
        report["problems"] = page.problems
        print("[%s] page problems: %d" % (tag, len(page.problems)))
        for p in page.problems[:20]:
            print("   " + p[:400])
    finally:
        with open(os.path.join(HERE, "audit-%s%s.json" % (tag, "-tab" if "--tab" in sys.argv else "")), "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=1)
        try:
            page.call("Browser.close")
        except Exception:
            pass
        try:
            proc.wait(timeout=5)
        except Exception:
            proc.kill()
        shutil.rmtree(prof, ignore_errors=True)


TABINFO = r"""
const a = document.activeElement; if (!a || a === document.body) return null;
const r = a.getBoundingClientRect(), s = getComputedStyle(a);
const top = document.getElementById('toprow').getBoundingClientRect();
const desc = e => e.id ? '#' + e.id : e.tagName.toLowerCase() + (typeof e.className === 'string' && e.className.trim() ? '.' + e.className.trim().split(/\s+/).join('.') : '');
let p = desc(a), q = a.parentElement, n = 0; while (!a.id && q && n < 3) { p = desc(q) + ' > ' + p; if (q.id) break; q = q.parentElement; n++; }
const lab = a.getAttribute('aria-label') || (a.id && document.querySelector('label[for="' + CSS.escape(a.id) + '"]') || {}).textContent || (a.closest('label') || {}).textContent || a.textContent || a.title || '';
const inView = r.bottom > 0 && r.top < innerHeight && r.right > 0 && r.left < innerWidth;
const sticky = getComputedStyle(document.getElementById('toprow')).position === 'sticky';
const under = sticky && !a.closest('#toprow') && r.top < top.bottom - 1 && r.bottom > top.top + 1 && r.left < top.right && r.right > top.left;
const ring = s.outlineStyle !== 'none' && parseFloat(s.outlineWidth) > 0 ? s.outlineWidth + ' ' + s.outlineStyle + ' ' + s.outlineColor : (s.boxShadow !== 'none' ? 'shadow ' + s.boxShadow.slice(0, 60) : '');
const sec = a.closest('details.sec, #toprow, fieldset.mode, #stage, footer, .lower');
return { el: p, label: String(lab).replace(/\s+/g, ' ').trim().slice(0, 50), x: Math.round(r.left + scrollX), y: Math.round(r.top + scrollY), w: Math.round(r.width), h: Math.round(r.height), inView, under, ring, sec: sec ? desc(sec) : '', vis: r.width > 0 && r.height > 0 && s.visibility !== 'hidden', hidOpacity: +s.opacity < 0.05 };
"""


def tabwalk(page, tag, w, h, report):
    key = dict(key="Tab", code="Tab", windowsVirtualKeyCode=9)
    walks = {}
    for name, js in [("m3d", STATES[0][1]), ("j3d", STATES[1][1]), ("k3d", STATES[2][1]), ("m2d", STATES[3][1])]:
        page.js(PRE + js + " scrollTo(0, 0); if (document.activeElement) document.activeElement.blur();")
        time.sleep(0.5)
        seq = []
        for i in range(420):
            page.call("Input.dispatchKeyEvent", type="rawKeyDown", **key)
            page.call("Input.dispatchKeyEvent", type="keyUp", **key)
            info = page.js(TABINFO)
            if info is None:
                seq.append(None); break
            if seq and seq[0] and info["el"] == seq[0]["el"] and i > 3:
                break
            seq.append(info)
            if name == "m3d" and i in (1, 6, 14, 40):
                page.shot(os.path.join(RAW, "%s-tab-%s-%03d.png" % (tag, name, i)))
        walks[name] = seq
        got = [s for s in seq if s]
        back = [(i, got[i - 1]["el"], got[i]["el"]) for i in range(1, len(got)) if got[i]["y"] < got[i - 1]["y"] - 40 and got[i]["sec"] == got[i - 1]["sec"]]
        print("[%s] tab walk %s: %d stops, not in view %d, under the sticky row %d, no focus ring %d, invisible %d, steps upward inside a section %d" % (
            tag, name, len(got), sum(not s["inView"] for s in got), sum(s["under"] for s in got), sum(not s["ring"] for s in got), sum((not s["vis"]) or s["hidOpacity"] for s in got), len(back)), flush=True)
    report["tab"] = walks


if __name__ == "__main__":
    main()

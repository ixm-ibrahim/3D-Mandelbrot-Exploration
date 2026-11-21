"""Real Tab presses through the whole page (every section open), then keyboard operation of the main control kinds."""
import json, os, sys, time
from lab import Lab, HERE, SHIFT

mode = sys.argv[1] if len(sys.argv) > 1 else "m"
lab = Lab(1400, 950, "dark", False, wait_idle=150)
lab.js("document.getElementById('mode-%s').click(); document.querySelectorAll('details.sec').forEach(s => { s.open = true; }); await new Promise(r => setTimeout(r, 400));" % mode)
lab.idle(100)
lab.js("window.scrollTo(0, 0); if (document.activeElement) document.activeElement.blur();")

DESC = r"""
const e = document.activeElement; if (!e || e === document.body) return null;
const cs = getComputedStyle(e);
const ring = s => s.outlineStyle !== 'none' && parseFloat(s.outlineWidth) > 0 ? s.outlineWidth + ' ' + s.outlineStyle + ' ' + s.outlineColor : '';
const near = [e.nextElementSibling, e.parentElement, e.previousElementSibling].filter(Boolean).map(x => ring(getComputedStyle(x)) ? x.tagName.toLowerCase() + '.' + (typeof x.className === 'string' ? x.className : '') + ':' + ring(getComputedStyle(x)) : '').filter(Boolean);
const r = e.getBoundingClientRect();
const lab = e.closest('label') || (e.id && document.querySelector('label[for="' + CSS.escape(e.id) + '"]'));
const txt = (e.getAttribute('aria-label') || (lab && lab.textContent) || e.textContent || e.placeholder || '').trim().replace(/\s+/g, ' ').slice(0, 40);
const cx = r.left + r.width / 2, cy = r.top + r.height / 2;
const top = document.elementFromPoint(Math.min(innerWidth - 1, Math.max(0, cx)), Math.min(innerHeight - 1, Math.max(0, cy)));
const covered = !(top && (top === e || e.contains(top) || top.contains(e) || (lab && lab.contains(top))));
return { tag: e.tagName.toLowerCase(), id: e.id, cls: typeof e.className === 'string' ? e.className : '', type: e.type || '', txt, fv: e.matches(':focus-visible'), ring: ring(cs), shadow: cs.boxShadow !== 'none' ? cs.boxShadow.slice(0, 60) : '', near,
  box: [Math.round(r.left), Math.round(r.top), Math.round(r.width), Math.round(r.height)], inView: r.bottom > 0 && r.top < innerHeight && r.right > 0 && r.left < innerWidth, fullyInView: r.top >= 0 && r.bottom <= innerHeight, covered, w0: r.width < 2 || r.height < 2,
  sec: (e.closest('details.sec') || {}).id || (e.closest('#stage') ? 'stage' : (e.closest('.toprow') ? 'toprow' : (e.closest('.mode') ? 'mode' : ''))), tabindex: e.getAttribute('tabindex') };
"""
order, kinds_shot = [], set()
first = None
for i in range(420):
    lab.key("Tab")
    time.sleep(0.03)
    d = lab.js(DESC)
    if d is None:
        print("focus left the page after %d stops" % len(order)); break
    key = (d["tag"], d["id"], d["txt"], d["sec"])
    if first is None: first = key
    elif key == first:
        print("wrapped to the first stop after %d stops" % len(order)); break
    order.append(d)
    kind = d["tag"] + "." + d["type"] + "." + d["cls"].split(" ")[0] + ("" if d["sec"] != "stage" else ".stage")
    if kind not in kinds_shot and len(kinds_shot) < 40:
        kinds_shot.add(kind)
        b = d["box"]; pad = 26
        x, y = max(0, b[0] - pad), max(0, b[1] - pad)
        w, h = min(1400 - x, b[2] + 2 * pad), min(950 - y, b[3] + 2 * pad)
        if w > 4 and h > 4:
            n = "focus-%02d-%s.png" % (len(kinds_shot), "".join(c if c.isalnum() else "_" for c in kind)[:40])
            lab.shot(os.path.join(HERE, n), [x, y, w, h]); d["shot"] = n
with open(os.path.join(HERE, "taborder-%s.json" % mode), "w", encoding="utf-8") as f:
    json.dump(order, f, indent=0, ensure_ascii=False)
print("stops:", len(order))
noring = [d for d in order if not d["ring"] and not d["near"]]
print("NO RING on self or neighbours (%d):" % len(noring))
for d in noring: print("   ", d["sec"], d["tag"], d["id"], d["type"], repr(d["txt"]), "fv=%s shadow=%s" % (d["fv"], d["shadow"]))
print("ring only on a neighbour:", sorted(set((d["tag"] + "." + d["type"], tuple(d["near"])) for d in order if not d["ring"] and d["near"]))[:12])
print("NOT IN VIEW after Tab:", [(d["sec"], d["id"] or d["txt"]) for d in order if not d["inView"]])
print("not fully in view:", [(d["sec"], d["id"] or d["txt"]) for d in order if d["inView"] and not d["fullyInView"]][:30])
print("COVERED by something else:", [(d["sec"], d["id"] or d["txt"]) for d in order if d["covered"] and d["inView"]][:30])
print("zero-size focus stops:", [(d["sec"], d["id"] or d["txt"], d["near"]) for d in order if d["w0"]][:30])
print("ORDER:")
last = None
for d in order:
    if d["sec"] != last:
        last = d["sec"]; print("  [%s]" % last)
    print("     %s%s %s %r" % (d["tag"], ("[" + d["type"] + "]") if d["type"] else "", d["id"], d["txt"][:32]))

# ---- operating controls from the keyboard (focus set by script, keys are real)
L = "window.squaringLab"
def focus(sel):
    return lab.js("const e = document.querySelector(%s); if (!e) return 'missing'; e.scrollIntoView({block: 'center'}); e.focus(); return document.activeElement === e;" % json.dumps(sel))
def state():
    return lab.js("const q = document.querySelector('input[name=mode]:checked'); return { mode: q && q.value, flat: %s.S.flat, cam: document.getElementById('stage').dataset.cam || '', eq: document.getElementById('eq').value, preset: document.getElementById('eqPreset').selectedIndex,"
                  " open: [...document.querySelectorAll('#sections > details.sec')].filter(d => !d.hidden).map(d => d.open ? 1 : 0).join(''), collapse: document.getElementById('collapseAll').textContent, pressed: [...document.querySelectorAll('.cam-mode button')].map(b => b.textContent.trim() + ':' + b.getAttribute('aria-pressed')).join(' ') };" % L)
print("OPERATE:")
s0 = state(); print("  start", s0)
print("  focus mode radio:", focus("#mode-%s" % mode)); lab.key("ArrowRight"); time.sleep(0.4); s = state(); print("  mode radio + ArrowRight ->", s["mode"]);
lab.key("ArrowLeft"); time.sleep(0.4); print("  + ArrowLeft ->", state()["mode"])
lab.js("document.getElementById('mode-m').click(); document.querySelectorAll('details.sec').forEach(s => { s.open = true; });"); time.sleep(0.4)
print("  focus 2D checkbox:", focus("#flat")); lab.key(" ", text=" "); time.sleep(0.4); print("  Space ->flat", state()["flat"]); lab.key(" ", text=" "); time.sleep(0.3); print("  Space again ->flat", state()["flat"])
print("  focus eqPreset:", focus("#eqPreset")); lab.key("ArrowDown"); time.sleep(0.5); s = state(); print("  select + ArrowDown -> index %s eq %r" % (s["preset"], s["eq"])); lab.key("ArrowUp"); time.sleep(0.5); s = state(); print("  + ArrowUp -> index %s eq %r" % (s["preset"], s["eq"]))
cams = lab.js("return [...document.querySelectorAll('.cam-mode button')].map((b, i) => b.textContent.trim());"); print("  cam buttons:", cams)
print("  focus Fly:", focus(".cam-mode button:nth-child(2)")); lab.key("Enter", text="\r"); time.sleep(0.4); s = state(); print("  Enter on 2nd cam button ->", s["cam"], s["pressed"])
print("  focus Arcball:", focus(".cam-mode button:nth-child(1)")); lab.key(" ", text=" "); time.sleep(0.4); s = state(); print("  Space on 1st cam button ->", s["cam"], s["pressed"])
print("  focus summary:", focus("#secEq > summary")); lab.key("Enter", text="\r"); time.sleep(0.3); print("  Enter on Equation summary -> open", state()["open"]); lab.key(" ", text=" "); time.sleep(0.3); print("  Space -> open", state()["open"])
print("  focus collapseAll:", focus("#collapseAll")); lab.key("Enter", text="\r"); time.sleep(0.3); s = state(); print("  Enter ->", s["open"], s["collapse"]); lab.key("Enter", text="\r"); time.sleep(0.3); s = state(); print("  Enter ->", s["open"], s["collapse"])
ap = lab.js("return [...document.querySelectorAll('#rules input[type=radio]')].map(r => r.id + (r.checked ? '*' : ''));"); print("  approach radios:", ap)
if ap:
    print("  focus approach radio:", focus("#rules input[type=radio]:checked")); lab.key("ArrowDown"); time.sleep(0.6)
    print("  ArrowDown ->", lab.js("return [...document.querySelectorAll('#rules input[type=radio]')].filter(r => r.checked).map(r => r.id);")); lab.key("ArrowUp"); time.sleep(0.6)
print("  focus canvas:", focus("#view")); c0 = lab.js("return [%s.cam.yaw, %s.cam.pitch, %s.cam.dist];" % (L, L, L)); lab.key("ArrowLeft"); time.sleep(0.5); c1 = lab.js("return [%s.cam.yaw, %s.cam.pitch, %s.cam.dist];" % (L, L, L)); print("  canvas ArrowLeft: cam", c0, "->", c1)
sy0 = lab.js("return scrollY;"); lab.key("ArrowDown"); time.sleep(0.5); print("  canvas ArrowDown: page scroll", sy0, "->", lab.js("return scrollY;"), "cam", lab.js("return [%s.cam.yaw, %s.cam.pitch, %s.cam.dist];" % (L, L, L)))
problems = lab.close()
print("PAGE PROBLEMS:", problems[:20])

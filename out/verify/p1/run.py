"""p1: sample the busy label, the progress bar and the status line every 50 ms around each action."""
import json, os, shutil, socket, subprocess, sys, tempfile, time, urllib.request
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, os.path.join(ROOT, "tools"))
from shot import WS, Page, CHROMES
OUT = os.path.dirname(os.path.abspath(__file__))
for s in (sys.stdout, sys.stderr):
    try: s.reconfigure(encoding="utf-8", errors="replace")
    except Exception: pass

HELP = r"""
window.__p1 = {
  rows: [], on: false, t0: 0, maxGap: 0,
  snap() {
    const L = window.squaringLab, b = document.getElementById('busy'), d = document.getElementById('drawProgress'), s = document.getElementById('status');
    const bvis = !!(b && !b.hidden && b.getClientRects().length), dvis = !!(d && !d.hidden && d.getClientRects().length);
    let frac = -1; if (dvis) { const m = /scaleX\(([\d.]+)\)/.exec(d.firstChild.style.transform); frac = m ? +m[1] : -2; }
    const gf = document.getElementById('glfail');
    this.rows.push([Math.round(performance.now() - this.t0), bvis ? b.textContent : '', frac, s.textContent, L.renderIdle() ? 1 : 0, L.cardIdle() ? 1 : 0, gf && !gf.hidden ? 1 : 0]);
  },
  start() {
    this.rows = []; this.t0 = performance.now(); this.on = true; this.maxGap = 0; let last = this.t0;
    const tick = () => { if (!this.on) return; this.snap(); setTimeout(tick, 50); }; tick();
    const raf = () => { if (!this.on) return; const n = performance.now(); this.maxGap = Math.max(this.maxGap, n - last); last = n; requestAnimationFrame(raf); }; requestAnimationFrame(raf);
  },
  stop() { this.snap(); this.on = false; return { rows: this.rows, maxGap: Math.round(this.maxGap) }; }
};
return 'ok';
"""


def launch(size="1400x950", theme="dark", mobile=False):
    w, h = (int(x) for x in size.split("x"))
    chrome = next(c for c in CHROMES if os.path.exists(c))
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0)); port = probe.getsockname()[1]
    prof = tempfile.mkdtemp(prefix="p1-")
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
    page.call("Emulation.setDeviceMetricsOverride", width=w, height=h, deviceScaleFactor=1, mobile=mobile)
    page.call("Emulation.setEmulatedMedia", features=[{"name": "prefers-color-scheme", "value": theme}])
    return proc, page, prof


def load(page):
    url = "file:///" + os.path.join(ROOT, "dist", "preview.html").replace("\\", "/")
    page.call("Page.navigate", url=url)
    page.wait("document.readyState === 'complete'", 60)
    time.sleep(0.3)
    page.js(HELP)


def close(proc, page, prof):
    try: page.call("Browser.close")
    except Exception: pass
    try: proc.wait(timeout=5)
    except Exception: proc.kill()
    shutil.rmtree(prof, ignore_errors=True)


def wait_idle(page, timeout=240, settle=0.6):
    end = time.time() + timeout; since = None
    while time.time() < end:
        if page.js("return !!window.squaringLab.idle();"):
            if since is None: since = time.time()
            if time.time() - since >= settle: return True
        else:
            since = None
        time.sleep(0.1)
    return False


def summarize(name, res, log):
    rows = res["rows"]; out = []
    out.append("== %s  (samples %d, longest frame gap %d ms)" % (name, len(rows), res["maxGap"]))
    runs = []
    for t, busy, frac, status, ri, ci, gf in rows:
        key = (busy, frac >= 0, status, ri, ci, gf)
        if runs and runs[-1]["key"] == key:
            r = runs[-1]; r["t1"] = t; r["f1"] = frac; r["n"] += 1
        else:
            runs.append({"key": key, "t0": t, "t1": t, "f0": frac, "f1": frac, "n": 1})
    for r in runs:
        busy, bar, status, ri, ci, gf = r["key"]
        out.append("  %6d-%6d ms  busy=%-26s bar=%-10s status=%-36s %s%s%s" % (
            r["t0"], r["t1"], repr(busy) if busy else "-", ("%.2f>%.2f" % (r["f0"], r["f1"])) if bar else "hidden", repr(status),
            "render-idle " if ri else "DRAWING     ", "card-idle" if ci else "MEASURING", " GLFAIL-shown" if gf else ""))
    gap = 0; longest = 0; cur = 0; prev_t = rows[0][0]; first = None; in_gap = set()
    for t, busy, frac, status, ri, ci, gf in rows:
        dt = t - prev_t; prev_t = t
        working = not (ri and ci); shown = bool(busy) or frac >= 0
        if shown and first is None: first = t
        if working and not shown:
            gap += dt; cur += dt; longest = max(longest, cur); in_gap.add(status)
        else:
            cur = 0
    last = rows[-1]
    work_end = max([r[0] for r in rows if not (r[4] and r[5])] or [0])
    out.append("  -> work ended at %d ms; first indicator at %s ms; working with NO indicator: %d ms total, longest stretch %d ms, status meanwhile %s" % (
        work_end, first, gap, longest, sorted(in_gap)))
    out.append("  -> at the end: busy=%r bar=%s status=%r glfail=%d" % (last[1], "shown" if last[2] >= 0 else "hidden", last[3], last[6]))
    bad = []
    for t, busy, frac, status, ri, ci, gf in rows:
        if frac >= 0 and status.startswith(("Done", "Preview", "Preparing", "Nothing")): bad.append((t, "bar shown but status=%r" % status))
        if frac < 0 and status.startswith(("Drawing", "Refining")): bad.append((t, "bar hidden but status=%r" % status))
        if ri and ci and (busy or frac >= 0): bad.append((t, "idle but indicator shown busy=%r bar=%s" % (busy, frac)))
        if busy.startswith("Preparing") and not status.startswith("Preparing"): bad.append((t, "busy says Preparing, status=%r" % status))
        if not ri and status.startswith("Done"): bad.append((t, "still drawing but status=%r" % status))
    if bad:
        out.append("  -> disagreements: %d samples, e.g. %s" % (len(bad), bad[:5]))
    drops = 0; pf = None
    for t, busy, frac, status, ri, ci, gf in rows:
        if frac >= 0 and pf is not None and pf >= 0 and frac < pf - 1e-6: drops += 1
        pf = frac
    out.append("  -> bar went backwards %d time(s); bar max %.2f" % (drops, max([r[2] for r in rows])))
    text = "\n".join(out); print(text); log.write(text + "\n"); log.flush()


def scenario(page, log, name, action, shots=(), timeout=240, during=None):
    if not wait_idle(page, timeout): print("!! not idle before", name)
    val = page.js("window.__p1.start();\n" + action)
    t0 = time.time()
    if during: during(page)
    for delay, path in shots:
        while time.time() - t0 < delay: time.sleep(0.01)
        page.shot(os.path.join(OUT, path), "#stage")
    ok = wait_idle(page, timeout)
    res = page.js("return window.__p1.stop();")
    if not ok: print("!! TIMED OUT waiting for idle:", name)
    summarize(name + ("" if val is None else "  [" + str(val) + "]"), res, log)
    return res


SEL = ("const $ = id => document.getElementById(id); const L = window.squaringLab; "
       "const pickSel = (id, f) => { const s = $(id); const o = [...s.options].find(f); s.value = o.value; "
       "s.dispatchEvent(new Event('change', { bubbles: true })); return o.textContent; };\n")
TYPE = "const b = $('%s'); if (!b) return 'no box'; b.focus(); b.value = '%s'; b.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', bubbles: true })); "


def main():
    which = sys.argv[1] if len(sys.argv) > 1 else "main"
    log = open(os.path.join(OUT, "timeline-%s.txt" % which), "w", encoding="utf-8")
    proc, page, prof = launch()
    try:
        load(page)
        sc = lambda *a, **k: scenario(page, log, *a, **k)
        if which == "main":
            sc("00 page load (already running)", "return 'load';")
            sc("01 equation preset: lambda", SEL + "return pickSel('eqPreset', o => /lambda/.test(o.textContent));", shots=[(0.12, "01-lambda-120ms.png"), (1.0, "01-lambda-1s.png")])
            sc("02 type equation z^3 + c*z", SEL + "$('eq').value = 'z^3 + c*z'; $('eq').dispatchEvent(new Event('change', { bubbles: true })); return 'err=' + $('eqErr').textContent + ' preset=' + $('eqPreset').value;")
            sc("03 typing error: z^n + c)", SEL + "$('eq').value = 'z^n + c)'; $('eq').dispatchEvent(new Event('change', { bubbles: true })); return 'err=' + $('eqErr').textContent;", shots=[(0.5, "03-typo-500ms.png")])
            sc("04 typing error: z^n + q*", SEL + "$('eq').value = 'z^n + q*'; $('eq').dispatchEvent(new Event('change', { bubbles: true })); return 'err=' + $('eqErr').textContent;")
            sc("05 equation preset back to first", SEL + "return pickSel('eqPreset', (o) => o.index === 0);")
            for ap in ["classic", "lathe", "bulb", "mercator"]:
                sc("06 approach -> " + ap, SEL + "const e = $('ap-%s'); if (!e) return 'NO SUCH'; e.click(); return L.S.ap || '';" % ap,
                   shots=([(0.15, "06-approach-classic-150ms.png"), (0.6, "06-approach-classic-600ms.png"), (2.0, "06-approach-classic-2s.png")] if ap == "classic" else ()))
            sc("07 mode -> Julia", SEL + "$('mode-j').click(); return L.S.mode;", shots=[(0.15, "07-julia-150ms.png")])
            sc("08 Julia preset", SEL + "const rows = [...document.querySelectorAll('#juliaList .plist-row')]; const r = rows[Math.min(8, rows.length - 1)]; const b = r.querySelector('button') || r; b.click(); return rows.length + ' rows; clicked ' + r.textContent.slice(0, 40) + ' c=' + JSON.stringify(L.S.c);")
            sc("09 mode -> Kleinian", SEL + "$('mode-k').click(); return L.S.mode;", shots=[(0.15, "09-klein-150ms.png"), (1.5, "09-klein-1500ms.png")])
            sc("10 Kleinian preset (4th)", SEL + "return pickSel('kleinPreset', (o) => o.index === 3);")
            sc("11 mode -> Mandelbrot", SEL + "$('mode-m').click(); return L.S.mode;")
            sc("12 power typed 3", SEL + TYPE % ("powNum", "3") + "return 'n=' + L.S.n;")
            sc("13 power typed -2", SEL + TYPE % ("powNum", "-2") + "return 'n=' + L.S.n;")
            sc("14 power typed 2", SEL + TYPE % ("powNum", "2") + "return 'n=' + L.S.n;")
            sc("15 2D view on", SEL + "$('flat').click(); return 'flat=' + L.S.flat;", shots=[(0.15, "15-flat-150ms.png")])
            sc("16 2D view off", SEL + "$('flat').click(); return 'flat=' + L.S.flat;")
            sc("17 mosaic on", SEL + "const c = document.querySelector('#mandelDials input[type=checkbox]'); c.click(); return c.id + ' mosaic=' + L.S.mosaic;", shots=[(0.15, "17-mosaic-150ms.png"), (2.0, "17-mosaic-2s.png")])
            sc("18 mosaic + 2D view", SEL + "$('flat').click(); return 'flat=' + L.S.flat;")
            sc("19 mosaic off, 2D off", SEL + "$('flat').click(); document.querySelector('#mandelDials input[type=checkbox]').click(); return 'flat=' + L.S.flat + ' mosaic=' + L.S.mosaic;")
            for q in ["qUltra", "qFast", "qFine", "qBal"]:
                sc("20 quality " + q, SEL + "$('%s').click(); return JSON.stringify(L.S.q);" % q, shots=([(1.5, "20-qFine-1500ms.png")] if q == "qFine" else ()))
            sc("21 approach parameter: planes 3 (scorecard)", SEL + TYPE % ("par-mercator-planesNum", "3") + "return JSON.stringify(L.S.param.mercator);")
        if which == "drag":
            for sid, key in (("pow", "n"), ("iter", "iter")):
                box = page.js("const e = document.getElementById('%s'); document.querySelectorAll('details.sec').forEach(d => { d.open = true; }); e.scrollIntoView({ block: 'center' }); await new Promise(r => setTimeout(r, 400)); const b = e.getBoundingClientRect(); return [b.left, b.top, b.width, b.height, e.min, e.max, e.value];" % sid)
                print(sid, "slider box", box)
                x0 = box[0] + box[2] * 0.56; y = box[1] + box[3] / 2

                def drag(page, x0=x0, y=y, box=box, sid=sid):
                    page.call("Input.dispatchMouseEvent", type="mouseMoved", x=x0, y=y)
                    page.call("Input.dispatchMouseEvent", type="mousePressed", x=x0, y=y, button="left", clickCount=1)
                    for i in range(40):
                        page.call("Input.dispatchMouseEvent", type="mouseMoved", x=x0 + (i + 1) * box[2] * 0.008, y=y, button="left", buttons=1)
                        time.sleep(0.05)
                        if i == 20: page.shot(os.path.join(OUT, "22-drag-%s-mid.png" % sid))
                    page.call("Input.dispatchMouseEvent", type="mouseReleased", x=x0 + 40 * box[2] * 0.008, y=y, button="left", clickCount=1)
                sc("22 real mouse drag of the %s slider for about 2 s, then release" % sid, "return '%s=' + window.squaringLab.S.%s;" % (key, key), during=drag)
                print("after drag", key, "=", page.js("return window.squaringLab.S.%s;" % key))
        page.js("return 0;")
        if page.problems:
            print("PAGE PROBLEMS (%d):" % len(page.problems))
            for p in page.problems[:40]: print("  " + p[:500])
            log.write("PAGE PROBLEMS: " + json.dumps(page.problems[:40]) + "\n")
        else:
            print("no console errors"); log.write("no console errors\n")
    finally:
        close(proc, page, prof); log.close()


if __name__ == "__main__":
    main()

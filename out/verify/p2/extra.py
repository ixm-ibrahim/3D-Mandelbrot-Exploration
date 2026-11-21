import json, os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)

from battery import T, ROOT, L, fmt
# reuse scenes' launcher by monkeypatching: simplest is to copy its start-up
import socket, subprocess, tempfile, shutil, urllib.request
from shot import WS, Page, CHROMES
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
chrome = next(c for c in CHROMES if os.path.exists(c))
with socket.socket() as probe:
    probe.bind(("127.0.0.1", 0)); port = probe.getsockname()[1]
prof = tempfile.mkdtemp(prefix="p2x-")
proc = subprocess.Popen([chrome, "--headless=new", "--remote-debugging-port=%d" % port, "--user-data-dir=" + prof, "--no-first-run", "--no-default-browser-check", "--disable-extensions", "--hide-scrollbars", "--window-size=1400,950", "--force-device-scale-factor=1", "about:blank"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
try:
    target = None
    for _ in range(150):
        try:
            with urllib.request.urlopen("http://127.0.0.1:%d/json/list" % port, timeout=2) as r:
                pages = [x for x in json.load(r) if x.get("type") == "page"]
            if pages: target = pages[0]["webSocketDebuggerUrl"]; break
        except Exception: pass
        time.sleep(0.2)
    page = Page(WS(target))
    for m in ("Runtime.enable", "Log.enable", "Page.enable"): page.call(m)
    page.call("Emulation.setDeviceMetricsOverride", width=1400, height=950, deviceScaleFactor=1, mobile=False)
    page.call("Emulation.setFocusEmulationEnabled", enabled=True)
    page.call("Page.navigate", url="file:///" + os.path.join(ROOT, "dist", "preview.html").replace("\\", "/"))
    page.wait("document.readyState === 'complete'", 60); page.wait(L + " && " + L + ".S", 120); time.sleep(1)
    t = T(page)
    t.js("S.q.res=0.25; S.q.aa=1; S.q.steps=60; S.q.shadow=false; S.q.ao=false; L.syncControls(); L.touch(); document.querySelectorAll('details.sec').forEach(s=>{s.open=true;});")
    box = lambda i: t.js("return document.getElementById(%s).value;" % json.dumps(i + "Num"))
    # field of view: fresh page, arrows
    seq = [box("viewFov")]
    for _ in range(3):
        t.click("#viewFovNum ~ .dial-steps .dial-up"); seq.append(box("viewFov"))
    print("FOV fresh page, three up-clicks:", seq)
    page.shot(os.path.join(HERE, "fov-steps.png"), "#viewDials")
    # drawing radius slider
    t.retype("#viewBoundNum", "8"); t.key("Enter")
    x, y = t.xy("#viewBound", 0.5)
    t.mouse("mouseMoved", x, y); t.mouse("mousePressed", x, y, button="left", clickCount=1); t.mouse("mouseReleased", x, y, button="left", clickCount=1)
    a = t.js("return S.view.bound;"); t.key("ArrowRight"); b = t.js("return S.view.bound;")
    print("Drawing radius: click mid of slider from 8 ->", a, "ArrowRight ->", b, "box", box("viewBound"))
    # sweep leftovers on the classic theta phase
    t.js("document.getElementById('ap-classic').click();"); time.sleep(0.4)
    left = []
    for i in range(4):
        t.click("#par-classic-thetaPlay"); time.sleep(0.55 + 0.13 * i); t.click("#par-classic-thetaPlay"); time.sleep(0.2)
        v = box("par-classic-theta"); t.click("#par-classic-thetaNum ~ .dial-steps .dial-up"); left.append((v, box("par-classic-theta")))
    print("theta after pausing a sweep, then one up-click:", left)
    page.shot(os.path.join(HERE, "sweep-left.png"), "#pd-classic")
    # light direction: typed fraction then arrows
    t.retype("#lightAzNum", "180.37"); t.key("Enter"); t.key("ArrowUp"); u = box("lightAz"); t.key("ArrowDown"); t.key("ArrowDown")
    print("lightAz 180.37, ArrowUp ->", u, ", two ArrowDown ->", box("lightAz"))
    print("problems:", page.problems[:6])
    page.call("Browser.close")
finally:
    try: proc.wait(timeout=5)
    except Exception: proc.kill()
    shutil.rmtree(prof, ignore_errors=True)

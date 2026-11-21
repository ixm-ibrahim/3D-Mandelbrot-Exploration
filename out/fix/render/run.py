"""Run a page script against a build of the lab in headless Chrome and print what it returns.

  python out/fix/render/run.py dist/fix-render.html out/fix/render/some.js [--size 1400x950] [--theme light] [--no-idle] [--arg JSON]

The page is loaded, the first finished picture is waited for (unless --no-idle), out/fix/render/trace.js is
evaluated (it installs window.__t, the tracing hooks), then the script file is evaluated as the body of an async
function; the value it returns is printed as JSON. `ARG` in the script is the --arg value.
Console errors and uncaught exceptions are printed at the end (exit code 3).
"""
import json, os, shutil, socket, subprocess, sys, tempfile, time, urllib.request, argparse
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
from shot import WS, Page, CHROMES  # noqa: E402
L = "window.squaringLab"


def launch(w, h, theme):
    chrome = next((c for c in CHROMES if os.path.exists(c)), None)
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0)); port = probe.getsockname()[1]
    prof = tempfile.mkdtemp(prefix="fixrender-")
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
    for m in ("Runtime.enable", "Log.enable", "Page.enable"):
        page.call(m)
    page.call("Emulation.setDeviceMetricsOverride", width=w, height=h, deviceScaleFactor=1, mobile=False)
    page.call("Emulation.setEmulatedMedia", features=[{"name": "prefers-color-scheme", "value": theme}])
    page.call("Emulation.setFocusEmulationEnabled", enabled=True)
    return page, proc, prof


def main():
    for stream in (sys.stdout, sys.stderr):
        try: stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception: pass
    ap = argparse.ArgumentParser()
    ap.add_argument("page"); ap.add_argument("script")
    ap.add_argument("--size", default="1400x950"); ap.add_argument("--theme", default="dark")
    ap.add_argument("--no-idle", action="store_true"); ap.add_argument("--arg", default="null")
    ap.add_argument("--argfile")
    ap.add_argument("--shot"); ap.add_argument("--clip", default="#stage"); ap.add_argument("--timeout", type=float, default=600)
    a = ap.parse_args()
    w, h = (int(x) for x in a.size.lower().split("x"))
    url = "file:///" + os.path.abspath(os.path.join(ROOT, a.page)).replace("\\", "/")
    arg = a.arg
    if a.argfile:
        with open(os.path.join(ROOT, a.argfile), encoding="utf-8") as f:
            arg = f.read()
    page, proc, prof = launch(w, h, a.theme)
    code = 0
    try:
        page.call("Page.navigate", url=url)
        page.wait("document.readyState === 'complete'", 30)
        page.wait(L + " && " + L + ".R", 30)
        if not a.no_idle and not page.wait(L + ".idle()", 240):
            print("WARNING: the page never finished its first picture")
        with open(os.path.join(HERE, "trace.js"), encoding="utf-8") as f:
            page.js(f.read())
        with open(os.path.join(ROOT, a.script), encoding="utf-8") as f:
            src = f.read()
        page.ws.s.settimeout(a.timeout)
        val = page.js("const ARG = %s;\n%s" % (arg, src))
        print(val if isinstance(val, str) else json.dumps(val, ensure_ascii=False))
        if a.shot:
            page.shot(os.path.join(ROOT, a.shot), a.clip)
            print("wrote " + a.shot)
        page.js("return 0;")
        if page.problems:
            print("PAGE PROBLEMS (%d):" % len(page.problems))
            for p in page.problems[:30]:
                print("  " + p[:500])
            code = 3
        try:
            page.call("Browser.close")
        except Exception:
            pass
    finally:
        try:
            proc.wait(timeout=5)
        except Exception:
            proc.kill()
        shutil.rmtree(prof, ignore_errors=True)
    sys.exit(code)


if __name__ == "__main__":
    main()

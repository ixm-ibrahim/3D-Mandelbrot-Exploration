"""Second probe: do animation frames still fire in the stalled pages, and is drawing progressing?"""
import json, os, subprocess, sys, time, urllib.request, re
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
from shot import WS
out = subprocess.run(["powershell", "-NoProfile", "-Command", "Get-CimInstance Win32_Process -Filter \"name='chrome.exe'\" | Where-Object { $_.CommandLine -match 'user-data-dir=.*monkey-' -and $_.CommandLine -notmatch '--type=' } | ForEach-Object { $_.ProcessId.ToString() + ' ' + $_.CommandLine }"], capture_output=True, text=True).stdout
def ask(ws, mid, expr, timeout, awaitp=False):
    ws.s.settimeout(timeout)
    ws.send(json.dumps({"id": mid, "method": "Runtime.evaluate", "params": {"expression": expr, "returnByValue": True, "awaitPromise": awaitp}}))
    t0 = time.time()
    try:
        while True:
            msg = json.loads(ws.recv())
            if msg.get("id") == mid:
                return "%.1fs %s" % (time.time() - t0, json.dumps(msg.get("result", msg), ensure_ascii=False)[:900])
    except Exception as err:
        return "NO ANSWER in %.0f s (%s)" % (time.time() - t0, type(err).__name__)
SNAP = "JSON.stringify({t: Math.round(performance.now()), vis: document.visibilityState, focus: document.hasFocus(), status: document.getElementById('status').textContent, busy: (document.getElementById('busy')||{}).textContent, busyHidden: (document.getElementById('busy')||{}).hidden, R: (() => { const R = window.squaringLab.R, o = {}; for (const k of Object.keys(R)) { const v = R[k]; if (v === null || ['number','string','boolean'].includes(typeof v)) o[k] = v; } return o; })(), active: document.activeElement && (document.activeElement.id || document.activeElement.tagName)})"
for line in out.splitlines():
    m = re.search(r"remote-debugging-port=(\d+)", line)
    if not m: continue
    port = int(m.group(1)); print("chrome pid", line.split()[0], "port", port, flush=True)
    with urllib.request.urlopen("http://127.0.0.1:%d/json/list" % port, timeout=5) as r:
        pages = [t for t in json.load(r) if t.get("type") == "page"]
    ws = WS(pages[0]["webSocketDebuggerUrl"])
    print("  snap1:", ask(ws, 1, SNAP, 10))
    print("  one animation frame:", ask(ws, 2, "new Promise(r => { const t = performance.now(); requestAnimationFrame(() => r('rAF fired after ' + Math.round(performance.now() - t) + ' ms')); })", 20, True))
    print("  one timer tick:", ask(ws, 3, "new Promise(r => { const t = performance.now(); setTimeout(() => r('timer fired after ' + Math.round(performance.now() - t) + ' ms'), 50); })", 20, True))
    time.sleep(3)
    print("  snap2:", ask(ws, 4, SNAP, 10))

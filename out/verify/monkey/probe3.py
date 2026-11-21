"""Third probe: what keeps changing in the stalled pages, and does a fresh real mouse event get answered?"""
import json, os, subprocess, sys, time, urllib.request, re
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
from shot import WS
out = subprocess.run(["powershell", "-NoProfile", "-Command", "Get-CimInstance Win32_Process -Filter \"name='chrome.exe'\" | Where-Object { $_.CommandLine -match 'user-data-dir=.*monkey-' -and $_.CommandLine -notmatch '--type=' } | ForEach-Object { $_.ProcessId.ToString() + ' ' + $_.CommandLine }"], capture_output=True, text=True).stdout
def ask(ws, mid, method, params, timeout):
    ws.s.settimeout(timeout)
    ws.send(json.dumps({"id": mid, "method": method, "params": params}))
    t0 = time.time()
    try:
        while True:
            msg = json.loads(ws.recv())
            if msg.get("id") == mid:
                return "%.1fs %s" % (time.time() - t0, json.dumps(msg.get("result", msg), ensure_ascii=False)[:1100])
    except Exception as err:
        return "NO ANSWER in %.0f s (%s)" % (time.time() - t0, type(err).__name__)
SNAP = ("JSON.stringify({t: Math.round(performance.now()), status: document.getElementById('status').textContent, lastTouch: Math.round(window.squaringLab.R.lastTouch), colour: window.squaringLab.S.colour, pos: window.squaringLab.basis().pos, cam: window.squaringLab.cam, "
        "active: (a => a && (a.id || a.tagName + '.' + a.className + ' in ' + (a.closest('.dial') ? a.closest('.dial').querySelector('input').id : '?')))(document.activeElement), "
        "pressed: [...document.querySelectorAll(':active')].map(e => e.id || e.tagName + '.' + (e.getAttribute('class') || '')).slice(-4), playing: [...document.querySelectorAll('.is-playing input[type=range]')].map(e => e.id), "
        "hover: [...document.querySelectorAll(':hover')].map(e => e.id || e.tagName).slice(-3), scrollY: Math.round(scrollY)})")
for line in out.splitlines():
    m = re.search(r"remote-debugging-port=(\d+)", line)
    if not m: continue
    port = int(m.group(1)); print("chrome pid", line.split()[0], "port", port, flush=True)
    with urllib.request.urlopen("http://127.0.0.1:%d/json/list" % port, timeout=5) as r:
        pages = [t for t in json.load(r) if t.get("type") == "page"]
    ws = WS(pages[0]["webSocketDebuggerUrl"])
    print("  snap1:", ask(ws, 1, "Runtime.evaluate", {"expression": SNAP, "returnByValue": True}, 10))
    time.sleep(2)
    print("  snap2:", ask(ws, 2, "Runtime.evaluate", {"expression": SNAP, "returnByValue": True}, 10))
    print("  fresh mouseMoved over the page title:", ask(ws, 3, "Input.dispatchMouseEvent", {"type": "mouseMoved", "x": 5, "y": 5}, 15))

"""Attach a second DevTools client to the monkey's stalled Chrome instances and see whether the page thread answers."""
import json, os, subprocess, sys, time, urllib.request, re, socket
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
from shot import WS
out = subprocess.run(["powershell", "-NoProfile", "-Command", "Get-CimInstance Win32_Process -Filter \"name='chrome.exe'\" | Where-Object { $_.CommandLine -match 'user-data-dir=.*monkey-' -and $_.CommandLine -notmatch '--type=' } | ForEach-Object { $_.ProcessId.ToString() + ' ' + $_.CommandLine }"], capture_output=True, text=True).stdout
for line in out.splitlines():
    m = re.search(r"remote-debugging-port=(\d+)", line)
    if not m: continue
    port = int(m.group(1)); print("chrome pid", line.split()[0], "port", port, flush=True)
    try:
        with urllib.request.urlopen("http://127.0.0.1:%d/json/list" % port, timeout=5) as r:
            pages = [t for t in json.load(r) if t.get("type") == "page"]
    except Exception as err:
        print("  /json/list failed:", err); continue
    ws = WS(pages[0]["webSocketDebuggerUrl"]); ws.s.settimeout(12)
    ws.send(json.dumps({"id": 1, "method": "Runtime.evaluate", "params": {"expression": "JSON.stringify({t: performance.now(), status: document.getElementById('status').textContent, idle: window.squaringLab.idle(), failed: window.squaringLab.R.failed, busy: (document.getElementById('busy')||{}).textContent, S: {mode: window.squaringLab.S.mode, ap: window.squaringLab.S.approach, n: window.squaringLab.S.n, eq: window.squaringLab.S.eq, fly: window.squaringLab.S.view.fly, q: window.squaringLab.S.q, colour: window.squaringLab.S.colour}, cam: window.squaringLab.cam})", "returnByValue": True}}))
    t0 = time.time(); got = False; events = 0
    try:
        while time.time() - t0 < 12:
            msg = json.loads(ws.recv())
            if msg.get("id") == 1:
                print("  page thread ANSWERED in %.1f s: %s" % (time.time() - t0, json.dumps(msg.get("result", msg))[:1500])); got = True; break
            events += 1
    except Exception as err:
        print("  no answer from the page thread in %.0f s (%s), %d events meanwhile" % (time.time() - t0, type(err).__name__, events))

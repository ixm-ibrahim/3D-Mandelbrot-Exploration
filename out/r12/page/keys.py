"""Round 12, page: the Approach list by keyboard, with real key presses (tools/shot.py can only run page scripts,
and a scripted key event does not move a radio button).

  python out/r12/page/keys.py dist/r12-page.html

Focuses the first entry of the list, presses Arrow Down once for every entry, then Arrow Up once, and prints which
entry had the focus and which approach was in use after each press. Arrow Down from the last entry goes back to
the first, as in any set of radio buttons. Exit code 1 if the walk is not the order the list is shown in.
"""
import json, os, socket, subprocess, sys, tempfile, time, shutil, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, os.path.join(ROOT, 'tools'))
import shot  # noqa: E402  (the WebSocket client and the page wrapper of the screenshot tool)


def main():
    for stream in (sys.stdout, sys.stderr):
        try: stream.reconfigure(encoding='utf-8', errors='replace')
        except Exception: pass
    url = 'file:///' + os.path.abspath(os.path.join(ROOT, sys.argv[1])).replace('\\', '/')
    chrome = next((c for c in shot.CHROMES if os.path.exists(c)), None)
    if not chrome:
        sys.exit('No Chrome or Edge found.')
    with socket.socket() as probe:
        probe.bind(('127.0.0.1', 0)); port = probe.getsockname()[1]
    prof = tempfile.mkdtemp(prefix='labkeys-')
    proc = subprocess.Popen([chrome, '--headless=new', '--remote-debugging-port=%d' % port, '--user-data-dir=' + prof,
                             '--no-first-run', '--no-default-browser-check', '--disable-extensions', '--hide-scrollbars',
                             '--window-size=1400,950', '--force-device-scale-factor=1', 'about:blank'],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    code = 0
    try:
        target = None
        for _ in range(100):
            try:
                with urllib.request.urlopen('http://127.0.0.1:%d/json/list' % port, timeout=2) as r:
                    pages = [t for t in json.load(r) if t.get('type') == 'page']
                if pages:
                    target = pages[0]['webSocketDebuggerUrl']; break
            except Exception:
                pass
            time.sleep(0.2)
        if not target:
            sys.exit('Chrome did not start its debugging port.')
        page = shot.Page(shot.WS(target))
        page.call('Runtime.enable'); page.call('Log.enable'); page.call('Page.enable')
        page.call('Emulation.setDeviceMetricsOverride', width=1400, height=950, deviceScaleFactor=1, mobile=False)
        page.call('Page.navigate', url=url)
        page.wait("document.readyState === 'complete'", 30)
        page.wait(shot.DONE, 120)
        shown = page.js("return [...document.querySelectorAll('#rules .rule')].map(e => e.dataset.ap);")
        state = "const L = window.squaringLab, a = document.activeElement, r = a && a.closest ? a.closest('.rule') : null; return [a ? a.id : '', L.APPROACHES[L.S.approach].id, r ? r.classList.contains('is-focus') : false];"
        page.js("document.getElementById('ap-' + %s).focus();" % json.dumps(shown[0]))

        def press(key, code_, vk):
            for kind in ('keyDown', 'keyUp'):
                page.call('Input.dispatchKeyEvent', type=kind, key=key, code=code_, windowsVirtualKeyCode=vk, nativeVirtualKeyCode=vk)
            time.sleep(0.35)
            return page.js(state)

        print('the list as shown: ' + ', '.join(shown))
        walked = []
        for i in range(len(shown)):
            focus, chosen, ring = press('ArrowDown', 'ArrowDown', 40)
            walked.append(chosen)
            want = shown[(i + 1) % len(shown)]
            ok = focus == 'ap-' + want and chosen == want
            print('Arrow Down %d: focus on %s, approach in use %s, focus ring %s%s' % (i + 1, focus, chosen, 'shown' if ring else 'NOT shown', '' if ok else '   <-- expected ' + want))
            if not ok or not ring:
                code = 1
        focus, chosen, ring = press('ArrowUp', 'ArrowUp', 38)
        want = shown[-1]
        print('Arrow Up: focus on %s, approach in use %s%s' % (focus, chosen, '' if chosen == want else '   <-- expected ' + want))
        if chosen != want:
            code = 1
        page.wait(shot.DONE, 120)
        page.js('return 0;')
        if page.problems:
            print('PAGE PROBLEMS: ' + ' | '.join(p[:300] for p in page.problems[:10]))
            code = code or 3
        print('keyboard walk ' + ('as the list is shown' if code == 0 else 'NOT as expected'))
        try: page.call('Browser.close')
        except Exception: pass
    finally:
        try: proc.wait(timeout=5)
        except Exception: proc.kill()
        shutil.rmtree(prof, ignore_errors=True)
    sys.exit(code)


if __name__ == '__main__':
    main()

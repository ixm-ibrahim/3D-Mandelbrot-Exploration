"""Round 12, checker of the page: the Approach list with a real mouse and real keys (through Chrome's input channel).

  python out/r12/check-page/real.py dist/r12-check-page.html 1400 950
  python out/r12/check-page/real.py dist/r12-check-page.html 375 800

For every entry: scroll its name into view, click the middle of the name with the mouse, and read which approach is
in use. Then focus the first entry and walk the list with Arrow Down (once per entry) and Arrow Up, then use the
keys inside a drop-down of a tried entry. Exit code 1 if a click or a key did not do what the list shows.
"""
import json, os, socket, subprocess, sys, tempfile, time, shutil, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, os.path.join(ROOT, 'tools'))
import shot  # noqa: E402


def main():
    for stream in (sys.stdout, sys.stderr):
        try: stream.reconfigure(encoding='utf-8', errors='replace')
        except Exception: pass
    W, H = int(sys.argv[2]), int(sys.argv[3])
    url = 'file:///' + os.path.abspath(os.path.join(ROOT, sys.argv[1])).replace('\\', '/')
    chrome = next((c for c in shot.CHROMES if os.path.exists(c)), None)
    if not chrome:
        sys.exit('No Chrome or Edge found.')
    with socket.socket() as probe:
        probe.bind(('127.0.0.1', 0)); port = probe.getsockname()[1]
    prof = tempfile.mkdtemp(prefix='labreal-')
    proc = subprocess.Popen([chrome, '--headless=new', '--remote-debugging-port=%d' % port, '--user-data-dir=' + prof,
                             '--no-first-run', '--no-default-browser-check', '--disable-extensions', '--hide-scrollbars',
                             '--window-size=%d,%d' % (W, H), '--force-device-scale-factor=1', 'about:blank'],
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
        page.call('Emulation.setDeviceMetricsOverride', width=W, height=H, deviceScaleFactor=1, mobile=False)
        page.call('Page.navigate', url=url)
        page.wait("document.readyState === 'complete'", 30)
        page.wait(shot.DONE, 120)
        print('window %d x %d' % (W, H))
        shown = page.js("return [...document.querySelectorAll('#rules .rule')].map(e => e.dataset.ap);")
        print('the list as shown: ' + ', '.join(shown))

        def mouse(x, y):
            page.call('Input.dispatchMouseEvent', type='mouseMoved', x=x, y=y)
            page.call('Input.dispatchMouseEvent', type='mousePressed', x=x, y=y, button='left', clickCount=1)
            page.call('Input.dispatchMouseEvent', type='mouseReleased', x=x, y=y, button='left', clickCount=1)
            time.sleep(0.4)

        # the mouse, last entry first so that every click changes the approach
        for ap in reversed(shown):
            x, y, top = page.js("const e = document.querySelector('.rule[data-ap=%s] .name'); e.scrollIntoView({ block: 'center' }); const r = e.getBoundingClientRect(); const el = document.elementFromPoint(r.left + r.width / 2, r.top + r.height / 2); return [r.left + r.width / 2, r.top + r.height / 2, el ? (el.className || el.tagName) : 'nothing'];" % json.dumps(ap))
            mouse(x, y)
            got, body = page.js("const L = window.squaringLab; const b = document.querySelector('.rule.is-on .rule-body'); return [L.APPROACHES[L.S.approach].id, b ? Math.round(b.getBoundingClientRect().height) : 0];")
            ok = got == ap and body > 0
            print('mouse click on the name of %s (at %d, %d, on top there: %s): approach in use %s, its body %d px tall%s' % (ap, x, y, top, got, body, '' if ok else '   <-- WRONG'))
            if not ok: code = 1
        page.wait(shot.DONE, 120)

        # the keys
        state = "const L = window.squaringLab, a = document.activeElement, r = a && a.closest ? a.closest('.rule') : null; return [a ? a.id : '', L.APPROACHES[L.S.approach].id, r ? r.classList.contains('is-focus') : false];"
        page.js("document.getElementById('ap-' + %s).focus();" % json.dumps(shown[0]))

        def press(key, code_, vk):
            for kind in ('keyDown', 'keyUp'):
                page.call('Input.dispatchKeyEvent', type=kind, key=key, code=code_, windowsVirtualKeyCode=vk, nativeVirtualKeyCode=vk)
            time.sleep(0.35)
            return page.js(state)

        for i in range(len(shown)):
            focus, chosen, ring = press('ArrowDown', 'ArrowDown', 40)
            want = shown[(i + 1) % len(shown)]
            ok = focus == 'ap-' + want and chosen == want
            print('Arrow Down %d: focus on %s, approach in use %s, focus ring %s%s' % (i + 1, focus, chosen, 'shown' if ring else 'NOT shown', '' if ok else '   <-- expected ' + want))
            if not ok or not ring: code = 1
        focus, chosen, ring = press('ArrowUp', 'ArrowUp', 38)
        print('Arrow Up: focus on %s, approach in use %s%s' % (focus, chosen, '' if chosen == shown[-1] else '   <-- expected ' + shown[-1]))
        if chosen != shown[-1]: code = 1
        # Tab from the chosen entry must reach a control of that entry (its first dial or drop-down), not jump out of the list
        last = shown[-1]
        seq = []
        for _ in range(4):
            for kind in ('keyDown', 'keyUp'):
                page.call('Input.dispatchKeyEvent', type=kind, key='Tab', code='Tab', windowsVirtualKeyCode=9, nativeVirtualKeyCode=9)
            time.sleep(0.2)
            seq.append(page.js("const a = document.activeElement; return (a.id || a.tagName) + (a.closest && a.closest('.rule') ? ' (in ' + a.closest('.rule').dataset.ap + ')' : ' (outside the list)');"))
        print('Tab four times from %s: %s' % (last, ' -> '.join(seq)))
        # a drop-down of a tried entry by keys: focus it, Arrow Down changes its choice and not the approach
        sel = page.js("const s = document.querySelector('.rule.is-on select'); if (!s) return null; s.focus(); return [s.id, s.selectedIndex, s.options.length];")
        if sel:
            f2, chosen2, _ = press('ArrowDown', 'ArrowDown', 40)
            idx = page.js("const s = document.getElementById(%s); return [s.selectedIndex, s.options[s.selectedIndex].text];" % json.dumps(sel[0]))
            ok = chosen2 == last and idx[0] != sel[1]
            print('drop-down %s by Arrow Down: choice %d -> %d ("%s"), approach in use %s%s' % (sel[0], sel[1], idx[0], idx[1], chosen2, '' if ok else '   <-- WRONG'))
            if not ok: code = 1
        else:
            print('the entry %s has no drop-down to try' % last)
        page.wait(shot.DONE, 120)
        page.js('return 0;')
        if page.problems:
            print('PAGE PROBLEMS: ' + ' | '.join(p[:300] for p in page.problems[:10]))
            code = code or 3
        else:
            print('no console errors')
        print('mouse and keys ' + ('as the list is shown' if code == 0 else 'NOT as expected'))
        try: page.call('Browser.close')
        except Exception: pass
    finally:
        try: proc.wait(timeout=5)
        except Exception: proc.kill()
        shutil.rmtree(prof, ignore_errors=True)
    sys.exit(code)


if __name__ == '__main__':
    main()

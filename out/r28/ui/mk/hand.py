"""Round 28, dial checker (ui): a page of the lab driven the way a hand drives it.

Chrome is started and spoken to with the classes of tools/shot.py (imported: WS, Page, CHROMES, DONE). On top of
that this file sends REAL input through Chrome's debugging port: mouse presses, moves and releases, key presses, and
typed characters. They reach the page as trusted events, exactly like a user's. Nothing here calls a setter of the
lab; reading the state (what the boxes show, what S holds) is done with JavaScript.

    with Hand('dist/r28-ui.html', '1400x950', 'dark') as h:
        h.click('#ap-balls')                 real click in the middle of the element (scrolled into view first)
        h.type('#ballsSizeNum', '150')       click into the box, Ctrl+A, the characters one by one, Enter
        h.key('ArrowUp')                     a key to whatever has the focus
        h.drag('#ballsSize', 250)            press the thumb, move, aim by the number the slider itself reports, let go
        h.drag('#ballsSize', 'right')        ... to 60 pixels past that end
        h.js('return S.k.bt;')               read something (L, S, $, sleep, vis are there)
"""
import json, os, shutil, socket, subprocess, sys, tempfile, time, urllib.request
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__)); UI = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(UI)))
sys.path.insert(0, os.path.join(ROOT, 'tools'))
import shot as SH

HEAD = """
const L = window.squaringLab, S = L.S, $ = id => document.getElementById(id);
const sleep = ms => new Promise(r => setTimeout(r, ms));
const vis = e => !!e && e.getClientRects().length > 0 && getComputedStyle(e).visibility !== 'hidden';
"""
VK = {'ArrowUp': 38, 'ArrowDown': 40, 'ArrowLeft': 37, 'ArrowRight': 39, 'PageUp': 33, 'PageDown': 34, 'Enter': 13, 'Escape': 27,
      'Tab': 9, 'Home': 36, 'End': 35, ' ': 32, 'Backspace': 8, 'Delete': 46}


class Hand:
    def __init__(self, url, size='1400x950', theme='dark', warm=True):
        self.url, self.size, self.theme, self.warm = url, size, theme, warm

    def __enter__(self):
        url = self.url
        if not url.startswith(('file:', 'http:', 'https:')):
            url = 'file:///' + os.path.abspath(os.path.join(ROOT, url)).replace('\\', '/')
        self.full_url = url
        w, h = (int(x) for x in self.size.lower().split('x'))
        chrome = next((c for c in SH.CHROMES if os.path.exists(c)), None)
        if not chrome:
            raise RuntimeError('No Chrome or Edge found.')
        with socket.socket() as probe:
            probe.bind(('127.0.0.1', 0)); port = probe.getsockname()[1]
        self.prof = tempfile.mkdtemp(prefix='labhand-')
        self.proc = subprocess.Popen([chrome, '--headless=new', '--remote-debugging-port=%d' % port, '--user-data-dir=' + self.prof,
                                      '--no-first-run', '--no-default-browser-check', '--disable-extensions', '--hide-scrollbars',
                                      '--window-size=%d,%d' % (w, h), '--force-device-scale-factor=1', 'about:blank'],
                                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        target = None
        for _ in range(300):
            try:
                with urllib.request.urlopen('http://127.0.0.1:%d/json/list' % port, timeout=2) as r:
                    pages = [t for t in json.load(r) if t.get('type') == 'page']
                if pages:
                    target = pages[0]['webSocketDebuggerUrl']; break
            except Exception:
                pass
            time.sleep(0.2)
        if not target:
            raise RuntimeError('Chrome did not start its debugging port.')
        self.page = SH.Page(SH.WS(target)); p = self.page
        p.call('Runtime.enable'); p.call('Log.enable'); p.call('Page.enable')
        p.call('Emulation.setDeviceMetricsOverride', width=w, height=h, deviceScaleFactor=1, mobile=False)
        p.call('Emulation.setEmulatedMedia', features=[{'name': 'prefers-color-scheme', 'value': self.theme}])
        p.call('Page.navigate', url=url)
        if not p.wait("document.readyState === 'complete'", 120):
            print('WARNING: the page did not finish loading in 120 s')
        time.sleep(0.5)
        if not self.warm:
            self.js("L.R.warmOn = false; return 1;")
        self.done()
        return self

    def __exit__(self, *a):
        try:
            self.page.call('Browser.close')
        except Exception:
            pass
        try:
            self.proc.wait(timeout=8)
        except Exception:
            self.proc.kill()
        shutil.rmtree(self.prof, ignore_errors=True)

    # ---- the page
    def js(self, code):
        return self.page.js(HEAD + code)

    def done(self, timeout=600):
        time.sleep(0.15)
        if not self.page.wait(SH.DONE, timeout):
            raise RuntimeError('the picture never finished: ' + str(self.js("return $('status').textContent;")))

    def reload(self):
        self.page.call('Page.reload')
        time.sleep(0.5)
        if not self.page.wait("document.readyState === 'complete' && !!window.squaringLab", 120):
            print('WARNING: the page did not finish loading after the reload')
        time.sleep(0.5)
        self.done()

    def problems(self):
        self.page.js('return 0;')
        return list(self.page.problems)

    def shot(self, path, clip=None):
        self.page.shot(os.path.join(ROOT, path), clip)

    def window_shot(self, path):
        """The window as it is, without scrolling anything."""
        data = self.page.call('Page.captureScreenshot', format='png')['data']
        import base64
        full = os.path.join(ROOT, path); os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, 'wb') as f:
            f.write(base64.b64decode(data))

    def box(self, sel, block='center'):
        b = self.js("const e = document.querySelector(%s); if (!e) return null; e.scrollIntoView({ block: %s }); await sleep(150); const b = e.getBoundingClientRect(); return [b.left, b.top, b.width, b.height];" % (json.dumps(sel), json.dumps(block)))
        if not b:
            raise RuntimeError('nothing matches ' + sel)
        return b

    # ---- real input
    def mouse(self, kind, x, y, buttons=0, count=1):
        self.page.call('Input.dispatchMouseEvent', type=kind, x=x, y=y, button='left' if (kind != 'mouseMoved' or buttons) else 'none',
                       buttons=buttons, clickCount=count if kind != 'mouseMoved' else 0, pointerType='mouse')

    def click_at(self, x, y):
        self.mouse('mouseMoved', x, y); self.mouse('mousePressed', x, y, 1); time.sleep(0.04); self.mouse('mouseReleased', x, y, 0); time.sleep(0.1)

    def on_top(self, sel, x, y):
        """Is the element (or a part of it, or the label it sits in) what a finger meets at that point of the window?"""
        return self.js("const e = document.querySelector(%s), t = document.elementFromPoint(%f, %f); if (!e || !t) return [false, t ? t.tagName + '#' + t.id + '.' + t.className : 'nothing'];"
                       " const lab = e.closest('label'); return [e === t || e.contains(t) || t.contains(e) || (!!lab && lab.contains(t)), t.tagName + '#' + t.id + '.' + (typeof t.className === 'string' ? t.className : '')];" % (json.dumps(sel), x, y))

    def click(self, sel):
        """A real click in the middle of the element. A hand does not click what it cannot see: when something else
        lies over that point (on a phone the pinned picture covers the top of the window), the element is brought to
        the lower edge of the window instead, and if it is still covered the click is not made and the log says so."""
        self.last_click = None
        for block in ('center', 'end', 'nearest'):
            b = self.box(sel, block); x, y = b[0] + b[2] / 2, b[1] + b[3] / 2
            ok, what = self.on_top(sel, x, y)
            if ok:
                self.click_at(x, y); self.last_click = (sel, block); return True
        print('   (NOT CLICKED: %s is covered by %s or out of the window; box %s)' % (sel, what, [round(v) for v in b]))
        self.not_clicked = getattr(self, 'not_clicked', []) + [sel]
        return False

    def hover(self, sel):
        b = self.box(sel); self.mouse('mouseMoved', b[0] + b[2] / 2, b[1] + b[3] / 2); time.sleep(0.15)

    def key(self, name, shift=False, ctrl=False):
        vk = VK.get(name, ord(name.upper()) if len(name) == 1 else 0); mod = (8 if shift else 0) | (2 if ctrl else 0)
        extra = {}
        if name == 'Enter':
            extra['text'] = '\r'
        if ctrl and name.lower() == 'a':
            extra['commands'] = ['selectAll']
        code = name if len(name) > 1 else 'Key' + name.upper()
        self.page.call('Input.dispatchKeyEvent', type='keyDown' if (extra.get('text') or len(name) > 1 or ctrl) else 'rawKeyDown', key=name, code=code,
                       windowsVirtualKeyCode=vk, nativeVirtualKeyCode=vk, modifiers=mod, **extra)
        self.page.call('Input.dispatchKeyEvent', type='keyUp', key=name, code=code, windowsVirtualKeyCode=vk, nativeVirtualKeyCode=vk, modifiers=mod)
        time.sleep(0.08)

    def chars(self, text):
        for ch in text:
            self.page.call('Input.dispatchKeyEvent', type='char', text=ch)
            time.sleep(0.015)

    def type(self, sel, text, enter=True, leave=None):
        """Click into the box, select what is there (Ctrl+A), type, then Enter (or, with leave='tab', the Tab key)."""
        self.click(sel)
        self.key('a', ctrl=True)
        if text == '':
            self.key('Backspace')          # an emptied box
        self.chars(text)
        if leave == 'tab':
            self.key('Tab')
        elif enter:
            self.key('Enter')
        time.sleep(0.12)

    def slider(self, sel):
        return self.js("const e = document.querySelector(%s); return [+e.min, +e.max, +e.value, +e.step];" % json.dumps(sel))

    def thumb(self, sel, value=None, tw=16.0):
        b = self.box(sel); r = self.slider(sel)
        v = r[2] if value is None else value
        f = min(1.0, max(0.0, (v - r[0]) / (r[1] - r[0])))
        return b[0] + tw / 2 + f * (b[2] - tw), b[1] + b[3] / 2, b

    def drag(self, sel, to, moves=6, aim=True, hold=False, read=None):
        """Press the slider's thumb and move it. to: a value, or 'left' / 'right' (60 pixels past that end).
        With aim=True the hand then creeps a pixel at a time until the slider reports the value nearest to the one
        wanted (as a user does who watches the number). read(self) is called after every move; its answers are returned."""
        x0, y, b = self.thumb(sel)
        if to in ('left', 'right'):
            x1 = b[0] - 60 if to == 'left' else b[0] + b[2] + 60
        else:
            x1 = self.thumb(sel, to)[0]
        self.mouse('mouseMoved', x0, y); self.mouse('mousePressed', x0, y, 1); time.sleep(0.06)
        seen = []; x = x0
        for k in range(1, moves + 1):
            x = x0 + (x1 - x0) * k / moves
            self.mouse('mouseMoved', x, y, 1); time.sleep(0.07)
            if read:
                seen.append(read(self))
        if aim and to not in ('left', 'right'):
            best = None
            for _ in range(40):
                v = self.slider(sel)[2]
                if best is None or abs(v - to) < abs(best[0] - to):
                    best = (v, x)
                if abs(v - to) < 1e-9:
                    break
                x += 1 if v < to else -1
                self.mouse('mouseMoved', x, y, 1); time.sleep(0.04)
                if read:
                    seen.append(read(self))
            v = self.slider(sel)[2]
            if best and abs(best[0] - to) < abs(v - to):
                x = best[1]; self.mouse('mouseMoved', x, y, 1); time.sleep(0.05)
        self._held = (x, y)
        if not hold:
            self.release()
        return seen

    def release(self):
        x, y = self._held; self.mouse('mouseReleased', x, y, 0); time.sleep(0.15)

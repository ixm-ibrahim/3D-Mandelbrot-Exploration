"""Round 28, Track A, builder: a page of the lab driven with REAL input (mouse and keys sent through Chrome's
debugging port, not events made up in the page), for the test of the dials. The start of Chrome and the socket are
those of tools/shot.py (imported, not copied).

    with Lab('dist/r28-dials.html', '1400x950', 'dark') as lab:
        lab.js("return 1 + 1;")            # JavaScript in the page; L, S, $ and sleep / settle are there
        lab.done()                         # wait for the picture
        lab.click('#ballsFrame')           # a real click at the middle of the element
        lab.type('#ballsSizeNum', '150')   # click into the box, select what is there, type, press Enter
        lab.key('ArrowUp')                 # a real key, to whatever has the focus
        lab.drag('#ballsSize', 250, 8)     # press the slider's thumb, move it to about that value in 8 moves, let go
        lab.drag('#ballsSize', 'right', 5) # the same, to 40 pixels past the right end
"""
import json, os, shutil, socket, subprocess, sys, tempfile, time, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE))))
sys.path.insert(0, os.path.join(ROOT, 'tools'))
import shot as SH

HEAD = """
const L = window.squaringLab, S = L.S, $ = id => document.getElementById(id);
const sleep = ms => new Promise(r => setTimeout(r, ms));
const settle = async (most = 30000) => { await sleep(200); for (let i = 0; i < most && !L.idle(); i++) await sleep(20); };
const vis = e => !!e && e.getClientRects().length > 0 && getComputedStyle(e).visibility !== 'hidden';
"""
KEYS = {'ArrowUp': 38, 'ArrowDown': 40, 'ArrowLeft': 37, 'ArrowRight': 39, 'PageUp': 33, 'PageDown': 34, 'Enter': 13, 'Escape': 27, 'Tab': 9, 'Home': 36, 'End': 35}


class Lab:
    def __init__(self, url, size='1400x950', theme='dark'):
        self.url, self.size, self.theme = url, size, theme

    def __enter__(self):
        url = self.url
        if not url.startswith(('file:', 'http:', 'https:')):
            url = 'file:///' + os.path.abspath(os.path.join(ROOT, url)).replace('\\', '/')
        w, h = (int(x) for x in self.size.lower().split('x'))
        chrome = next((c for c in SH.CHROMES if os.path.exists(c)), None)
        if not chrome:
            raise RuntimeError('No Chrome or Edge found.')
        with socket.socket() as probe:
            probe.bind(('127.0.0.1', 0)); port = probe.getsockname()[1]
        self.prof = tempfile.mkdtemp(prefix='labdrive-')
        self.proc = subprocess.Popen([chrome, '--headless=new', '--remote-debugging-port=%d' % port, '--user-data-dir=' + self.prof,
                                      '--no-first-run', '--no-default-browser-check', '--disable-extensions', '--hide-scrollbars',
                                      '--window-size=%d,%d' % (w, h), '--force-device-scale-factor=1', 'about:blank'],
                                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        target = None
        for _ in range(150):
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
        if not p.wait("document.readyState === 'complete'", 60):
            print('WARNING: the page did not finish loading in 60 s')
        time.sleep(0.4)
        self.js("L.R.warmOn = false; return 1;")
        self.done()
        return self

    def __exit__(self, *a):
        try:
            self.page.call('Browser.close')
        except Exception:
            pass
        try:
            self.proc.wait(timeout=5)
        except Exception:
            self.proc.kill()
        shutil.rmtree(self.prof, ignore_errors=True)

    # ---- the page
    def js(self, code):
        return self.page.js(HEAD + code)

    def done(self, timeout=900):
        if not self.page.wait(SH.DONE, timeout):
            raise RuntimeError('the picture never finished: ' + str(self.js("return $('status').textContent;")))

    def problems(self):
        self.page.js('return 0;')
        return list(self.page.problems)

    def shot(self, path, clip=None):
        self.page.shot(os.path.join(ROOT, path), clip)

    def box(self, sel):
        """The element's box in the window, after it has been scrolled into view: [left, top, width, height]."""
        b = self.js("const e = document.querySelector(%s); if (!e) return null; e.scrollIntoView({ block: 'center' }); await sleep(120); const b = e.getBoundingClientRect(); return [b.left, b.top, b.width, b.height];" % json.dumps(sel))
        if not b:
            raise RuntimeError('nothing matches ' + sel)
        return b

    # ---- real input
    def mouse(self, kind, x, y, buttons=0):
        self.page.call('Input.dispatchMouseEvent', type=kind, x=x, y=y, button='left' if (kind != 'mouseMoved' or buttons) else 'none', buttons=buttons, clickCount=1 if kind != 'mouseMoved' else 0)

    def click_at(self, x, y):
        self.mouse('mouseMoved', x, y); self.mouse('mousePressed', x, y, 1); time.sleep(0.03); self.mouse('mouseReleased', x, y, 0); time.sleep(0.08)

    def click(self, sel):
        b = self.box(sel); self.click_at(b[0] + b[2] / 2, b[1] + b[3] / 2)

    def key(self, name, shift=False):
        vk = KEYS[name]; mod = 8 if shift else 0
        extra = {'text': '\r'} if name == 'Enter' else {}
        self.page.call('Input.dispatchKeyEvent', type='keyDown', key=name, code=name, windowsVirtualKeyCode=vk, nativeVirtualKeyCode=vk, modifiers=mod, **extra)
        self.page.call('Input.dispatchKeyEvent', type='keyUp', key=name, code=name, windowsVirtualKeyCode=vk, nativeVirtualKeyCode=vk, modifiers=mod)
        time.sleep(0.08)

    def type(self, sel, text, enter=True):
        self.click(sel)
        self.js("const e = document.querySelector(%s); e.focus(); e.select(); return 1;" % json.dumps(sel))
        self.page.call('Input.insertText', text=text)
        if enter:
            self.key('Enter')
        time.sleep(0.1)

    def thumb_x(self, sel, value=None):
        """Where the slider's thumb is (or would be for a value), in window pixels: (x, y)."""
        b = self.box(sel)
        r = self.js("const e = document.querySelector(%s); return [+e.min, +e.max, +e.value];" % json.dumps(sel))
        v = r[2] if value is None else value
        tw = 14.0                                                    # about the width of the thumb
        f = min(1.0, max(0.0, (v - r[0]) / (r[1] - r[0])))
        return b[0] + tw / 2 + f * (b[2] - tw), b[1] + b[3] / 2

    def drag(self, sel, to_value, moves=8, read=None, hold=False):
        """Press the thumb, move it to about to_value in `moves` moves; after each move read(lab) is called and its
        answers are returned. With hold=True the button is not let go (call release())."""
        x0, y = self.thumb_x(sel)
        if to_value in ('left', 'right'):                           # past that end of the slider, as a hand does that wants the end
            b = self.box(sel); x1 = b[0] - 40 if to_value == 'left' else b[0] + b[2] + 40
        else:
            x1, _ = self.thumb_x(sel, to_value)
        self.mouse('mouseMoved', x0, y); self.mouse('mousePressed', x0, y, 1); time.sleep(0.05)
        seen = []
        for k in range(1, moves + 1):
            x = x0 + (x1 - x0) * k / moves
            self.mouse('mouseMoved', x, y, 1); time.sleep(0.06)
            if read:
                seen.append(read(self))
        self._held = (x1, y)
        if not hold:
            self.release()
        return seen

    def release(self):
        x, y = self._held; self.mouse('mouseReleased', x, y, 0); time.sleep(0.12)

"""Driver for the export tester: one headless Chrome on dist/v6.html, helpers to run picture jobs through the
panel, fetch the saved files into Python and compare them with the stage."""
import base64, io, json, os, shutil, socket, subprocess, sys, tempfile, time, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, 'tools'))
from shot import WS, Page, CHROMES  # noqa: E402
import numpy as np  # noqa: E402
from PIL import Image  # noqa: E402

Image.MAX_IMAGE_PIXELS = None
for stream in (sys.stdout, sys.stderr):
    try: stream.reconfigure(encoding='utf-8', errors='replace')
    except Exception: pass

PRE = r"""const L = window.squaringLab, $ = id => document.getElementById(id);
const sleep = ms => new Promise(r => setTimeout(r, ms));
const fail = m => { throw new Error(m); };
const type = (id, v) => { const e = $(id); if (!e) fail('no control ' + id); e.value = v; e.dispatchEvent(new Event('input', { bubbles: true })); e.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', bubbles: true })); };
const pick = (id, text) => { const e = $(id); if (!e) fail('no control ' + id); const o = [...e.options].find(x => x.text.startsWith(text)); if (!o) fail('no option ' + text + ' in ' + id); e.value = o.value; e.dispatchEvent(new Event('change', { bubbles: true })); };
const shown = id => { const e = $(id); return !!e && e.getBoundingClientRect().width > 0; };
const chosen = id => { const e = $(id); return e.selectedIndex >= 0 ? e.options[e.selectedIndex].text : ''; };
if (!window.files) { window.files = []; }
"""
HOOK = "window.squaringLabSaveHook = (name, blob) => { window.files.push({ name, blob }); };"


def log(*a):
    print(time.strftime('%H:%M:%S'), *a, flush=True)


class Lab:
    def __init__(self, size=(1400, 950), theme='dark', url='dist/v6.html', before=None, hook=True):
        chrome = next(c for c in CHROMES if os.path.exists(c))
        with socket.socket() as probe:
            probe.bind(('127.0.0.1', 0)); port = probe.getsockname()[1]
        self.prof = tempfile.mkdtemp(prefix='labexp-')
        self.proc = subprocess.Popen([chrome, '--headless=new', '--remote-debugging-port=%d' % port, '--user-data-dir=' + self.prof,
                                      '--no-first-run', '--no-default-browser-check', '--disable-extensions', '--hide-scrollbars',
                                      '--window-size=%d,%d' % size, '--force-device-scale-factor=1', 'about:blank'],
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
            raise RuntimeError('Chrome did not start')
        self.page = p = Page(WS(target))
        self.size = size
        p.call('Runtime.enable'); p.call('Log.enable'); p.call('Page.enable')
        p.call('Emulation.setDeviceMetricsOverride', width=size[0], height=size[1], deviceScaleFactor=1, mobile=False)
        p.call('Emulation.setEmulatedMedia', features=[{'name': 'prefers-color-scheme', 'value': theme}])
        if before:
            p.call('Page.addScriptToEvaluateOnNewDocument', source=before)
        p.call('Page.navigate', url='file:///' + os.path.join(ROOT, url).replace('\\', '/'))
        p.wait("document.readyState === 'complete'", 30)
        time.sleep(0.4)
        if hook:
            self.js(HOOK)

    def js(self, code):
        return self.page.js(PRE + code)

    def idle(self, timeout=300):
        ok = self.page.wait("window.squaringLab && window.squaringLab.idle && window.squaringLab.idle()", timeout)
        if not ok:
            log('  !! idle() not reached in', timeout, 's; status:', self.js("return $('status') ? $('status').textContent : null;"))
        return ok

    def job_wait(self, timeout=1500):
        end = time.time() + timeout
        while time.time() < end:
            if not self.js("return L.exportBusy();"):
                return True
            time.sleep(0.4)
        return False

    def shot(self, path, clip=None):
        self.page.shot(os.path.join(HERE, path), clip)

    def stage_shot(self, path):
        """The live picture alone: everything that lies over the canvas is hidden for the screenshot."""
        self.js("let s = $('__hide'); if (!s) { s = document.createElement('style'); s.id = '__hide'; document.head.appendChild(s); } "
                "s.textContent = '#stage > *:not(#view) { visibility: hidden !important; }'; await sleep(150);")
        self.page.shot(os.path.join(HERE, path), '#view')
        self.js("$('__hide').textContent = '';")

    def blob(self, expr, path):
        n = self.js("window.__buf = new Uint8Array(await (%s).arrayBuffer()); return window.__buf.length;" % expr)
        data = bytearray()
        CH = 3 * 1024 * 1024
        for off in range(0, n, CH):
            s = self.js("const a = window.__buf.subarray(%d, %d); let s = ''; for (let i = 0; i < a.length; i += 32768) s += String.fromCharCode.apply(null, a.subarray(i, i + 32768)); return btoa(s);" % (off, min(n, off + CH)))
            data += base64.b64decode(s)
        self.js("window.__buf = null;")
        with open(os.path.join(HERE, path), 'wb') as f:
            f.write(data)
        return len(data)

    def start_job(self, size, quality, kind, w=None, h=None, watch=True):
        typed = ("type('exportWNum', '%d'); type('exportHNum', '%d');" % (w, h)) if w else ''
        return self.js("""
$('secExport').open = true;
if (shown('exportDiscard')) { $('exportDiscard').click(); await sleep(60); }
pick('exportSize', %s); %s
pick('exportQuality', %s); pick('exportKind', %s);
await sleep(60);
const note = $('exportSizeNote').textContent;
window.__tl = []; window.__gaps = []; window.__raf = %s;
let last = performance.now();
const tick = () => { const now = performance.now(); window.__gaps.push(now - last); last = now; if (window.__raf) requestAnimationFrame(tick); };
if (window.__raf) requestAnimationFrame(tick);
window.__t0 = performance.now();
clearInterval(window.__tlTimer);
window.__tlTimer = setInterval(() => { if (L.exportBusy()) window.__tl.push([Math.round(performance.now() - window.__t0), $('exportStep').textContent]); }, 250);
$('exportStart').click();
await sleep(80);
return { busy: L.exportBusy(), step: $('exportStep').textContent, msg: $('exportMsg').textContent, note, startShown: shown('exportStart'), cancelShown: shown('exportCancel') };
""" % (json.dumps(size), typed, json.dumps(quality), json.dumps(kind), 'true' if watch else 'false'))

    def end_job(self):
        return self.js("""
clearInterval(window.__tlTimer); window.__raf = false;
const took = Math.round(performance.now() - window.__t0), g = window.__gaps.slice(2).sort((a, b) => a - b), n = g.length;
const gaps = n ? { n, mean: +(g.reduce((a, b) => a + b, 0) / n).toFixed(1), p95: +g[Math.floor(n * 0.95)].toFixed(1), worst: +g[n - 1].toFixed(1), over50: g.filter(x => x > 50).length, over100: g.filter(x => x > 100).length } : null;
const pv = $('exportPreview');
return { took, gaps, tl: window.__tl, msg: $('exportMsg').textContent, facts: [...$('exportFacts').children].map(e => e.textContent), saveShown: shown('exportSave'), discardShown: shown('exportDiscard'), startShown: shown('exportStart'), preview: [pv.width, pv.height], focus: document.activeElement && document.activeElement.id };
""")

    def save(self, path_stem):
        """Click Save the file and fetch what the hook received. Returns (path, name, mime, bytes)."""
        r = self.js("""
const n = window.files.length; $('exportSave').click(); await sleep(400);
const f = window.files[n]; if (!f) return { none: true, msg: $('exportMsg').textContent };
window.__last = f; return { name: f.name, type: f.blob.type, size: f.blob.size, msg: $('exportMsg').textContent };
""")
        if r.get('none'):
            return None, r
        ext = r['name'].rsplit('.', 1)[-1]
        path = path_stem + '.' + ext
        n = self.blob('window.__last.blob', path)
        r['fetched'] = n
        return path, r

    def problems(self):
        self.page.js("return 0;")
        return list(self.page.problems)

    def close(self):
        try: self.page.call('Browser.close')
        except Exception: pass
        try: self.proc.wait(timeout=5)
        except Exception: self.proc.kill()
        shutil.rmtree(self.prof, ignore_errors=True)


# ---------- looking at the files in Python
def open_rgb(path):
    im = Image.open(os.path.join(HERE, path))
    fmt = im.format
    im = im.convert('RGB')
    return im, fmt


def blank(im):
    """Standard deviation over a small copy, and the share of the most common colour."""
    t = np.asarray(im.resize((256, max(1, round(256 * im.size[1] / im.size[0]))), Image.BOX), dtype=np.float32)
    flat = t.reshape(-1, 3)
    q = (flat // 8).astype(np.int32)
    keys = q[:, 0] * 1024 + q[:, 1] * 32 + q[:, 2]
    vals, counts = np.unique(keys, return_counts=True)
    return {'std': round(float(flat.std()), 2), 'top_colour_share': round(float(counts.max() / len(keys)), 3), 'colours': int(len(vals))}


def compare(im, stage_path, save_pair=None):
    """The saved picture brought to the stage's scale (same height), the middle part both have compared."""
    st = Image.open(os.path.join(HERE, stage_path)).convert('RGB')
    sw, sh = st.size
    W, H = im.size
    k = sh / H
    small = im.resize((max(1, round(W * k)), sh), Image.LANCZOS if k < 1 else Image.BICUBIC)
    w = min(small.size[0], sw)
    a = small.crop(((small.size[0] - w) // 2, 0, (small.size[0] - w) // 2 + w, sh))
    b = st.crop(((sw - w) // 2, 0, (sw - w) // 2 + w, sh))
    A, B = np.asarray(a, dtype=np.int16), np.asarray(b, dtype=np.int16)
    d = np.abs(A - B).max(axis=2)
    out = {'mean': round(float(d.mean()), 2), 'over24_pct': round(float((d > 24).mean() * 100), 2), 'over64_pct': round(float((d > 64).mean() * 100), 2), 'worst': int(d.max()), 'compared': [w, sh]}
    # how far the solid's outline moved: both pictures against their own background (the corner colour)
    if save_pair:
        pair = Image.new('RGB', (2 * w + 6, sh), (128, 128, 128))
        pair.paste(b, (0, 0)); pair.paste(a, (w + 6, 0))
        pair.save(os.path.join(HERE, save_pair))
    return out


def seams(im, T=512):
    """Steps across the borders of the 512-pixel tiles against the steps one pixel to either side."""
    W, H = im.size
    A = np.asarray(im, dtype=np.int16)
    worst = {'ratio': 0}
    res = []
    for x in range(T, W, T):
        db = np.abs(A[:, x] - A[:, x - 1]).mean()
        dn = 0.5 * (np.abs(A[:, x - 1] - A[:, x - 2]).mean() + np.abs(A[:, x + 1] - A[:, x]).mean()) if x + 1 < W else np.abs(A[:, x - 1] - A[:, x - 2]).mean()
        res.append(('x', x, float(db), float(dn)))
    for k in range(1, (H + T - 1) // T):
        y = H - T * k   # GL rows run upward: tile borders are counted from the bottom of the picture
        if y <= 1 or y + 1 >= H: continue
        db = np.abs(A[y] - A[y - 1]).mean()
        dn = 0.5 * (np.abs(A[y - 1] - A[y - 2]).mean() + np.abs(A[y + 1] - A[y]).mean())
        res.append(('y', y, float(db), float(dn)))
    for axis, pos, db, dn in res:
        r = db / max(dn, 0.05)
        if r > worst['ratio']:
            worst = {'ratio': round(r, 2), 'axis': axis, 'at': pos, 'step_on_border': round(db, 2), 'step_beside': round(dn, 2)}
    worst['borders'] = len(res)
    return worst


def tl_report(tl, took):
    """How good the time-left estimate was: for each reading that named a time, (said, true)."""
    import re
    rows = []
    for t, text in tl:
        m = re.search(r'About ([\d.]+) (seconds|minutes|hours) left', text)
        pc = re.search(r'(\d+)%', text)
        if m:
            said = float(m.group(1)) * {'seconds': 1, 'minutes': 60, 'hours': 3600}[m.group(2)]
            rows.append((round(t / 1000, 1), int(pc.group(1)) if pc else None, said, round((took - t) / 1000, 1)))
    return rows

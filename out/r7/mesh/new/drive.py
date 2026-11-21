"""Tester "mesh": run real "Save a 3D model" jobs on dist/v6.html through the panel and keep the zips.

  python out/t6/mesh/drive.py <tag> <subject>:<cells>[,<cells>...] [<subject>:<cells> ...]
  python out/t6/mesh/drive.py <tag> special:cancel | special:perturb | special:edge

Each subject is loaded on a fresh page. For each job: the picture of the stage (pics/<subject>.png), the camera,
the progress line sampled every quarter second, the facts the panel shows, the zip caught through
window.squaringLabSaveHook (zips/<subject>-<cells>.zip), a json with everything (runs/<subject>-<cells>.json).
"""
import base64, json, os, socket, subprocess, sys, tempfile, threading, time, shutil, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'tools'))
import shot  # noqa: E402

URL = 'file:///' + os.path.join(ROOT, 'dist', 'r7-mesh.html').replace('\\', '/')
HELP = r"""
const L = window.squaringLab, $ = id => document.getElementById(id);
const sleep = ms => new Promise(r => setTimeout(r, ms));
const fail = m => { throw new Error(m); };
const type = (id, v) => { const e = $(id); if (!e) fail('no control ' + id); e.value = v; e.dispatchEvent(new Event('input', { bubbles: true })); e.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', bubbles: true })); };
const pick = (id, text) => { const e = $(id); if (!e) fail('no control ' + id); const o = [...e.options].find(x => x.text.startsWith(text)); if (!o) fail('no option ' + text + ' in ' + id + ': ' + [...e.options].map(x => x.text).join(' | ')); e.value = o.value; e.dispatchEvent(new Event('change', { bubbles: true })); };
"""
SUBJECTS = {
    'mandel': "return 'the opening picture';",
    'julia1': "$('mode-j').click(); await sleep(300); pick('juliaPreset', 'Basilica'); await sleep(200); $('juliaFrame').click(); await sleep(200); return 'c = ' + JSON.stringify(L.S.c);",
    'rabbit': "$('mode-j').click(); await sleep(300); pick('juliaPreset', 'Douady rabbit'); await sleep(200); $('juliaFrame').click(); await sleep(200); return 'c = ' + JSON.stringify(L.S.c);",
    'klein': "$('mode-k').click(); await sleep(300); return 'opening Kleinian view, depth ' + L.S.k.iter;",
    'trapsolid': "$('mode-j').click(); await sleep(300); pick('juliaPreset', 'Basilica'); await sleep(200); $('juliaFrame').click(); await sleep(200); pick('col-solid', 'Is the solid'); await sleep(200); return 'solid = ' + L.S.colour.solid + ', c = ' + JSON.stringify(L.S.c);",
    'trapadd': "pick('col-solid', 'Is added to the solid'); await sleep(200); return 'solid = ' + L.S.colour.solid;",
    'negpow': "type('pow', '-2'); await sleep(300); return 'power ' + L.S.n;",
    'cut': "$('cutOn').click(); await sleep(300); return 'cutOn ' + L.S.cutOn + ' at z = ' + L.S.cut;",
}
STATE = r"""
const b = L.basis(), cv = $('view'), r = cv.getBoundingClientRect(), st = $('stage').getBoundingClientRect();
return { pos: b.pos, right: b.right, up: b.up, f: b.f, fov: L.S.view.fov, bound: L.S.view.bound, cw: r.width, ch: r.height,
  cx: r.left - st.left, cy: r.top - st.top, sw: st.width, sh: st.height, mode: L.S.mode, c: L.S.c, n: L.S.n, iter: L.S.iter,
  kiter: L.S.k.iter, cutOn: L.S.cutOn, cut: L.S.cut, solid: L.S.colour.solid, flat: L.S.flat, eq: L.S.eq,
  cells: $('meshCells').value, cellsOptions: [...$('meshCells').options].map(o => o.text), offset: $('meshOffset') ? $('meshOffset').value : null };
"""


class FastWS(shot.WS):
    def __init__(self, url):
        super().__init__(url)
        self.buf = bytearray(self.rest); self.rest = b''

    def _read(self, n):
        while len(self.buf) < n:
            chunk = self.s.recv(1 << 20)
            if not chunk:
                raise RuntimeError('connection closed')
            self.buf += chunk
        out = bytes(self.buf[:n]); del self.buf[:n]
        return out


def launch(w=1400, h=950):
    chrome = next(c for c in shot.CHROMES if os.path.exists(c))
    with socket.socket() as probe:
        probe.bind(('127.0.0.1', 0)); port = probe.getsockname()[1]
    prof = tempfile.mkdtemp(prefix='labmesh-')
    proc = subprocess.Popen([chrome, '--headless=new', '--remote-debugging-port=%d' % port, '--user-data-dir=' + prof,
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
        sys.exit('Chrome did not start its debugging port.')
    page = shot.Page(FastWS(target))
    page.call('Runtime.enable'); page.call('Log.enable'); page.call('Page.enable')
    page.call('Emulation.setDeviceMetricsOverride', width=w, height=h, deviceScaleFactor=1, mobile=False)
    page.call('Emulation.setEmulatedMedia', features=[{'name': 'prefers-color-scheme', 'value': 'dark'}])
    return proc, prof, page


def js(page, code):
    return page.js(HELP + code)


def load(page):
    page.call('Page.navigate', url=URL)
    page.wait("document.readyState === 'complete'", 60)
    time.sleep(0.5)
    if not page.wait(shot.DONE, 400):
        print('  WARNING: the page did not come to rest within 400 s after loading', flush=True)


def mem_of(profname):
    ps = ("$p = Get-CimInstance Win32_Process -Filter \"Name='chrome.exe'\" | Where-Object { $_.CommandLine -like '*%s*' }; "
          "($p | Measure-Object -Property WorkingSetSize -Sum).Sum; ($p | Measure-Object -Property PrivatePageCount -Sum).Sum; $p.Count") % profname
    try:
        out = subprocess.run(['powershell', '-NoProfile', '-Command', ps], capture_output=True, text=True, timeout=40).stdout.split()
        return [int(float(x)) for x in out[:3]]
    except Exception as e:
        return [0, 0, 0]


class MemWatch(threading.Thread):
    def __init__(self, profname):
        super().__init__(daemon=True)
        self.profname, self.samples, self.stop = profname, [], False

    def run(self):
        t0 = time.time()
        while not self.stop:
            m = mem_of(self.profname)
            self.samples.append([round(time.time() - t0, 1)] + m)
            time.sleep(1.5)


def pull(page, index, path):
    info = js(page, "const f = window.__files[%d]; return f ? { name: f.name, size: f.blob.size, type: f.blob.type } : null;" % index)
    if not info:
        return None
    step, t0 = 6 << 20, time.time()
    with open(path, 'wb') as out:
        for o in range(0, info['size'], step):
            s = js(page, "const b = window.__files[%d].blob.slice(%d, %d); const u = new Uint8Array(await b.arrayBuffer()); let s = ''; "
                         "for (let i = 0; i < u.length; i += 32768) s += String.fromCharCode.apply(null, u.subarray(i, i + 32768)); return btoa(s);" % (index, o, o + step))
            out.write(base64.b64decode(s))
    info['pulled_s'] = round(time.time() - t0, 1)
    return info


def run_job(page, prof, subject, cells, extra_during=None, name=None, timeout=1500, keep_zip=True):
    name = name or '%s-%s' % (subject, cells)
    rec = {'job': name, 'subject': subject, 'cells': cells}
    rec['state'] = js(page, STATE)
    js(page, "window.__files = []; window.squaringLabSaveHook = (name, blob) => { window.__files.push({ name, blob }); };"
             "window.squaringLabMeshTest = {}; $('secMesh').open = true; pick('meshCells', '%s');"
             "window.__gap = { max: 0, n: 0, last: performance.now(), over50: 0, over100: 0 };"
             "window.__gapTimer = setInterval(() => { const t = performance.now(), g = window.__gap, d = t - g.last; g.last = t; if (d > g.max) g.max = d; if (d > 50) g.over50++; if (d > 100) g.over100++; g.n++; }, 8);"
             "return $('meshCells').value;" % cells)
    watch = None
    if int(cells) >= 384:
        watch = MemWatch(os.path.basename(prof)); watch.start()
        time.sleep(3.5)
    t0 = time.time()
    started = js(page, "const heap = performance.memory ? performance.memory.usedJSHeapSize : 0; $('meshStart').click(); await sleep(30); return [L.meshBusy(), heap, $('meshStart').closest('[hidden]') !== null, $('meshMsg').textContent];")
    rec['started'] = started
    line, last, did_extra = [], None, False
    while True:
        st = js(page, "return [L.meshBusy(), $('meshStep').textContent, performance.memory ? performance.memory.usedJSHeapSize : 0, L.idle()];")
        t = time.time() - t0
        if st[1] != last:
            line.append([round(t, 2), st[1], st[2]]); last = st[1]
        if not st[0]:
            break
        if extra_during and not did_extra and t > extra_during[0]:
            rec['extra'] = js(page, extra_during[1]); did_extra = True
        if t > timeout:
            rec['timeout'] = True
            js(page, "$('meshCancel').click(); return 1;")
            break
        time.sleep(0.25)
    rec['seconds'] = round(time.time() - t0, 2)
    rec['line'] = line
    if watch:
        time.sleep(2.0); watch.stop = True; watch.join(60)
        rec['mem'] = watch.samples
        rec['mem_peak_ws_MB'] = round(max(s[1] for s in watch.samples) / 1048576) if watch.samples else None
        rec['mem_peak_private_MB'] = round(max(s[2] for s in watch.samples) / 1048576) if watch.samples else None
        rec['mem_before_ws_MB'] = round(watch.samples[0][1] / 1048576) if watch.samples else None
    rec['after'] = js(page, r"""
clearInterval(window.__gapTimer);
const facts = [...$('meshFacts').children].map(e => e.textContent);
const T = window.squaringLabMeshTest, m = T && T.mesh; let lab = null;
if (m) {
  const lo = [1e30, 1e30, 1e30], hi = [-1e30, -1e30, -1e30], P = m.pos;
  for (let p = 0; p < P.length; p += 3) for (let k = 0; k < 3; k++) { const v = P[p + k]; if (v < lo[k]) lo[k] = v; if (v > hi[k]) hi[k] = v; }
  lab = { org: m.org, h: m.h, lo, hi, box: m.box, n: m.n, nz: m.nz, unit: m.unit, tris: m.tris, points: m.points, pieces: m.pieces, volume: m.volume, size: m.size };
}
delete window.squaringLabMeshTest;
const vis = id => { const e = $(id); return !!e && e.getBoundingClientRect().width > 0; };
return { facts, warn: $('meshWarn').hidden ? '' : $('meshWarn').textContent, msg: $('meshMsg').textContent, saveShown: vis('meshSave'), startShown: vis('meshStart'),
  cancelShown: vis('meshCancel'), lab, gap: window.__gap, focus: document.activeElement ? document.activeElement.id : null, idle: L.idle() };
""")
    try:
        page.shot(os.path.join(HERE, 'pics', 'panel-%s.png' % name), '#secMesh')
    except Exception as e:
        rec['panel_shot_error'] = str(e)
    if rec['after']['saveShown']:
        rec['saved'] = js(page, "$('meshSave').click(); await sleep(400); return { n: window.__files.length, msg: $('meshMsg').textContent };")
        for _ in range(60):
            if js(page, "return window.__files.length;"):
                break
            time.sleep(0.5)
        rec['saved']['msg'] = js(page, "return $('meshMsg').textContent;")
        if keep_zip:
            rec['file'] = pull(page, 0, os.path.join(HERE, 'zips', name + '.zip'))
        else:
            rec['file'] = js(page, "const f = window.__files[0]; return f ? { name: f.name, size: f.blob.size, type: f.blob.type } : null;")
        rec['discard'] = js(page, "$('meshDiscard').click(); await sleep(100); const vis = id => { const e = $(id); return !!e && e.getBoundingClientRect().width > 0; }; window.__files = []; return { startShown: vis('meshStart'), msg: $('meshMsg').textContent };")
    rec['problems'] = list(page.problems)
    os.makedirs(os.path.join(HERE, 'runs'), exist_ok=True)
    with open(os.path.join(HERE, 'runs', name + '.json'), 'w', encoding='utf-8') as f:
        json.dump(rec, f, indent=1, ensure_ascii=False)
    a = rec['after']
    print('  %s: %.1f s, facts %s | warn %r | msg %r | file %s | gap max %.0f ms (%d turns, %d over 50 ms, %d over 100 ms)%s' % (
        name, rec['seconds'], a['facts'], a['warn'][:80], a['msg'], rec.get('file'), a['gap']['max'], a['gap']['n'], a['gap']['over50'], a['gap']['over100'],
        ' | peak memory %s MB working set, %s MB private (before: %s MB)' % (rec.get('mem_peak_ws_MB'), rec.get('mem_peak_private_MB'), rec.get('mem_before_ws_MB')) if watch else ''), flush=True)
    return rec


def subject_page(page, subject):
    load(page)
    print('subject %s: %s' % (subject, js(page, SUBJECTS[subject])), flush=True)
    t0 = time.time()
    ok = page.wait(shot.DONE, 600)
    time.sleep(0.6)
    print('  picture at rest after %.1f s (%s)' % (time.time() - t0, 'ok' if ok else 'TIMED OUT'), flush=True)
    page.shot(os.path.join(HERE, 'pics', subject + '.png'), '#stage')


def main():
    for stream in (sys.stdout, sys.stderr):
        try: stream.reconfigure(encoding='utf-8', errors='replace')
        except Exception: pass
    tag, jobs = sys.argv[1], sys.argv[2:]
    for d in ('pics', 'zips', 'runs'):
        os.makedirs(os.path.join(HERE, d), exist_ok=True)
    proc, prof, page = launch()
    try:
        for spec in jobs:
            subject, _, what = spec.partition(':')
            if subject == 'special':
                import special
                sys.path.insert(0, os.path.dirname(HERE)); import mine
                getattr(mine, what, None) and getattr(mine, what)(page, prof, sys.modules[__name__]) or (not hasattr(mine, what) and getattr(special, what)(page, prof, sys.modules[__name__]))
                continue
            subject_page(page, subject)
            for cells in what.split(','):
                run_job(page, prof, subject, cells)
        page.js('return 0;')
        if page.problems:
            print('PAGE PROBLEMS (%d):' % len(page.problems))
            for p in page.problems[:40]:
                print('  ' + p[:600])
        else:
            print('no console errors')
        try: page.call('Browser.close')
        except Exception: pass
    finally:
        try: proc.wait(timeout=8)
        except Exception: proc.kill()
        shutil.rmtree(prof, ignore_errors=True)


if __name__ == '__main__':
    main()
